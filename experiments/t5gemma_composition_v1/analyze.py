"""Matched BART/T5Gemma length and geometry summaries on the locked G5 worlds."""
import csv,json,math
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;G5=HERE.parent/'projection_hypothesis_v1'
CFG=json.loads((HERE/'config.json').read_text())
def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def save(name,rows):
 with (HERE/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def mean(x):return round(float(np.mean(x)),6)
def pct(x):return round(100*sum(x)/len(x),2)
def cat(s):
 if s['success']:return 'success'
 if s['parse_unresolved'] or s['decoded_semantic_state'] is None:return 'unresolved_decode'
 if not s['fact_preservation']:return 'parsed_content_error'
 return 'parsed_semantic_error'
def chart(name,rows,key,title,split,top=None):
 W,H=810,390;L,R,U,D=65,620,43,320;maxy=top or max(r[key] for r in rows if r['split']==split)*1.12 or 1
 X=lambda k:L+(k-1)*(R-L)/4
 Y=lambda v:D-v/maxy*(D-U)
 lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="65" y="25" font-size="17" font-family="sans-serif">{title}</text>',f'<path d="M {L} {U} V {D} H {R}" fill="none" stroke="#333"/>']
 for fraction in (0,.25,.5,.75,1):
  value=maxy*fraction;y=Y(value)
  lines.append(f'<line x1="{L}" x2="{R}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e8e8e8"/>')
  lines.append(f'<text x="{L-9}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#555" font-family="sans-serif">{value:.1f}</text>')
 for k in range(1,6):lines.append(f'<text x="{X(k)-4:.1f}" y="340" font-size="13" font-family="sans-serif">{k}</text>')
 for backbone,color in [('BART','#1c6ea4'),('T5Gemma','#d35400')]:
  for path,dash in [('pure_latent',''),('decode_reencode','7 4')]:
   rr=sorted([r for r in rows if r['backbone']==backbone and r['path']==path and r['split']==split],key=lambda r:r['step']);assert len(rr)==5
   points=' '.join(f'{X(r["step"]):.1f},{Y(r[key]):.1f}' for r in rr)
   lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
   legend_y=80+24*(2*(backbone=='T5Gemma')+(path=='decode_reencode'))
   lines.append(f'<line x1="632" x2="657" y1="{legend_y}" y2="{legend_y}" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
   lines.append(f'<text x="664" y="{legend_y+4}" font-size="11" fill="{color}" font-family="sans-serif">{backbone} {"pure" if path=="pure_latent" else "reencode"}</text>')
 lines.append('</svg>');(HERE/name).write_text('\n'.join(lines)+'\n')

def main():
 bart=read(G5/'pure_reset_controls.jsonl')+read(G5/'decode_reencode_trajectories.jsonl')
 t5=read(HERE/'trajectories.jsonl');assert len(bart)==len(t5)==1060
 allrows=[dict(r,backbone=b) for b,rs in [('BART',bart),('T5Gemma',t5)] for r in rs]
 idx={(r['backbone'],r['path'],r['split'],r['world_id'],r['step']):r for r in allrows};assert len(idx)==2120
 ids={s:sorted({r['world_id'] for r in t5 if r['split']==s}) for s in ('test_iid','test_template_ood')};assert all(len(x)==53 for x in ids.values())
 length=[];geometry=[];taxonomy=[];paired=[];rng=np.random.default_rng(CFG['bootstrap_seed'])
 for split,ws in ids.items():
  for backbone in ('BART','T5Gemma'):
   for path in ('pure_latent','decode_reencode'):
    for k in range(1,6):
     rr=[idx[backbone,path,split,w,k] for w in ws];end=[r['edited']['success'] for r in rr]
     trajectory=[all(idx[backbone,path,split,w,j]['edited']['success'] for j in range(1,k+1)) for w in ws]
     early=[w for w in ws if all(idx[backbone,path,split,w,j]['edited']['success'] for j in (1,2))]
     conditional=sum(all(idx[backbone,path,split,w,j]['edited']['success'] for j in range(1,k+1)) for w in early)
     length.append(dict(backbone=backbone,path=path,split=split,step=k,n=53,endpoint_count=sum(end),endpoint_pct=pct(end),trajectory_count=sum(trajectory),trajectory_pct=pct(trajectory),fact_count=sum(r['edited']['fact_preservation'] for r in rr),fact_pct=pct([r['edited']['fact_preservation'] for r in rr]),first_two_success_n=len(early),conditional_trajectory_count=conditional))
     geometry.append(dict(backbone=backbone,path=path,split=split,step=k,n=53,edited_cosine=mean([r['edited_distance']['cosine'] for r in rr]),post_reencode_cosine=mean([r['reset_distance']['cosine'] for r in rr]),edited_normalized_l2=mean([r['edited_distance']['normalized_l2'] for r in rr]),post_reencode_normalized_l2=mean([r['reset_distance']['normalized_l2'] for r in rr]),post_reencode_l2_better=sum(r['reset_distance']['normalized_l2']<r['edited_distance']['normalized_l2'] for r in rr),residual_norm=mean([r['residual_norm'] for r in rr])))
     for r in rr:
      parsed=r['edited']['decoded_semantic_state'];gold_date=date.fromisoformat(r['gold_frame']['view_date'])+timedelta(days=r['gold_semantic_state']['offset'])
      time_error=(date.fromisoformat(parsed['event_date'])-gold_date).days if parsed else None
      taxonomy.append(dict(backbone=backbone,path=path,split=split,world_id=r['world_id'],step=k,category=cat(r['edited']),fact_preservation=r['edited']['fact_preservation'],time_date_error_days=time_error,edited_l2=r['edited_distance']['normalized_l2']))
   for k in range(1,6):
    x=np.array([idx[backbone,'pure_latent',split,w,k]['edited']['success'] for w in ws],dtype=int)
    y=np.array([idx[backbone,'decode_reencode',split,w,k]['edited']['success'] for w in ws],dtype=int)
    d=y-x;sample=rng.integers(0,53,size=(CFG['bootstrap_replicates'],53));boot=d[sample].mean(1)
    plus=int(((x==0)&(y==1)).sum());minus=int(((x==1)&(y==0)).sum());n=plus+minus
    p=min(1.,2*sum(math.comb(n,j) for j in range(min(plus,minus)+1))/2**n) if n else 1.
    paired.append(dict(backbone=backbone,split=split,step=k,n=53,pure_count=int(x.sum()),reencode_count=int(y.sum()),reencode_minus_pure_pp=round(float(100*d.mean()),2),ci_low_pp=round(float(100*np.quantile(boot,.025)),2),ci_high_pp=round(float(100*np.quantile(boot,.975)),2),improved_worlds=plus,worsened_worlds=minus,mcnemar_exact_p=p))
 save('backbone_comparison.csv',length);save('representation_distance.csv',geometry);save('failure_taxonomy.csv',taxonomy);save('paired_effects.csv',paired)
 drift=[]
 for split in ids:
  for backbone in ('BART','T5Gemma'):
   for path in ('pure_latent','decode_reencode'):
    gg={r['step']:r for r in geometry if r['backbone']==backbone and r['path']==path and r['split']==split}
    ll={r['step']:r for r in length if r['backbone']==backbone and r['path']==path and r['split']==split}
    drift.append(dict(backbone=backbone,path=path,split=split,edited_l2_step1=gg[1]['edited_normalized_l2'],edited_l2_step2=gg[2]['edited_normalized_l2'],edited_l2_step3=gg[3]['edited_normalized_l2'],edited_l2_step4=gg[4]['edited_normalized_l2'],edited_l2_step5=gg[5]['edited_normalized_l2'],l2_increase_step2_to5=round(gg[5]['edited_normalized_l2']-gg[2]['edited_normalized_l2'],6),first_endpoint_below_50pct=next((k for k in range(1,6) if ll[k]['endpoint_pct']<50),None)))
 save('drift_summary.csv',drift)
 counts=[]
 for backbone in ('BART','T5Gemma'):
  for path in ('pure_latent','decode_reencode'):
   for split in ids:
    for k in range(1,6):
     c=Counter(r['category'] for r in taxonomy if r['backbone']==backbone and r['path']==path and r['split']==split and r['step']==k)
     for label,n in c.items():counts.append(dict(backbone=backbone,path=path,split=split,step=k,category=label,count=n,denominator=53))
 save('failure_counts.csv',counts)
 time_errors=[]
 for backbone in ('BART','T5Gemma'):
  for path in ('pure_latent','decode_reencode'):
   for split in ids:
    for k in range(1,6):
     c=Counter(r['time_date_error_days'] for r in taxonomy if r['backbone']==backbone and r['path']==path and r['split']==split and r['step']==k and r['category']=='parsed_semantic_error' and r['time_date_error_days'] is not None)
     for delta,n in sorted(c.items()):time_errors.append(dict(backbone=backbone,path=path,split=split,step=k,parsed_event_date_minus_gold_days=delta,count=n))
 if time_errors:save('parsed_time_error_counts.csv',time_errors)
 for split,label in [('test_iid','iid'),('test_template_ood','ood')]:
  chart(f'length_curve_{label}.svg',length,'trajectory_pct',f'{label.upper()} trajectory success (%)',split,100)
  chart(f'distance_curve_{label}.svg',geometry,'edited_normalized_l2',f'{label.upper()} edited latent distance to gold',split)
 cases=[]
 for split,ws in ids.items():
  patterns={
   't5_pure_fails_dre_recovers':[w for w in ws if all(idx['T5Gemma','pure_latent',split,w,j]['edited']['success'] for j in (1,2)) and not idx['T5Gemma','pure_latent',split,w,5]['edited']['success'] and all(idx['T5Gemma','decode_reencode',split,w,j]['edited']['success'] for j in range(1,6))],
   't5_both_success':[w for w in ws if all(idx['T5Gemma',p,split,w,j]['edited']['success'] for p in ('pure_latent','decode_reencode') for j in range(1,6))],
   't5_both_fail':[w for w in ws if not idx['T5Gemma','pure_latent',split,w,5]['edited']['success'] and not idx['T5Gemma','decode_reencode',split,w,5]['edited']['success']],
   't5_dre_worse':[w for w in ws if idx['T5Gemma','pure_latent',split,w,5]['edited']['success'] and not idx['T5Gemma','decode_reencode',split,w,5]['edited']['success']]}
  for name,candidates in patterns.items():
   if not candidates:continue
   w=candidates[0];stages=[]
   for k in range(1,6):
    stage=dict(step=k,gold_text=idx['T5Gemma','pure_latent',split,w,k]['gold_text'])
    for backbone in ('BART','T5Gemma'):
     for path in ('pure_latent','decode_reencode'):
      r=idx[backbone,path,split,w,k];stage[f'{backbone}/{path}']=dict(text=r['decoded_text'],success=r['edited']['success'],fact_preservation=r['edited']['fact_preservation'],edited_l2=r['edited_distance']['normalized_l2'],residual_norm=r['residual_norm'])
    stages.append(stage)
   cases.append(dict(category=name,split=split,world_id=w,stages=stages))
 js('typical_trajectories.json',cases)
 ident=read(HERE/'identity_controls.jsonl');gold=read(HERE/'gold_autoencode_controls.jsonl')
 controls=[dict(type='source_identity',split=s,step=0,n=53,success=sum(r['score']['success'] for r in ident if r['split']==s)) for s in ids]
 controls +=[dict(type='gold_autoencode',split=s,step=k,n=53,success=sum(r['score']['success'] for r in gold if r['split']==s and r['step']==k)) for s in ids for k in range(1,6)]
 save('autoencoding_controls.csv',controls)
 exact=[]
 for backbone in ('BART','T5Gemma'):
  for path in ('pure_latent','decode_reencode'):
   for split,ws in ids.items():
    for k in range(1,6):
     rs=[idx[backbone,path,split,w,k] for w in ws]
     exact.append(dict(backbone=backbone,path=path,split=split,step=k,n=53,decoded_text_strip_equals_gold=sum(r['decoded_text'].strip()==r['gold_text'] for r in rs)))
 save('exact_text_match.csv',exact)
 js('summary.json',dict(length=length,geometry=geometry,paired=paired,failure_counts=counts,autoencoding_controls=controls,examples=[dict(category=x['category'],split=x['split'],world_id=x['world_id']) for x in cases]))
if __name__=='__main__':main()
