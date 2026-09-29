"""Matched 106-world G6 curves, geometry, paired effects, and failure categories."""
import csv,json,math
from collections import Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;G5=HERE.parent/'projection_hypothesis_v1'
CFG=json.loads((HERE/'config.json').read_text())
def read(p):return [json.loads(x) for x in p.read_text().splitlines()]
def save(name,rows):
 with (HERE/name).open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');wr.writeheader();wr.writerows(rows)
def jsonsave(name,x):(HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def avg(xs):return round(float(np.mean(xs)),6)
def pct(xs):return round(100*sum(xs)/len(xs),2)

def chart(name,rows,key,title,ymax=None):
 w,h=780,430;L,R,U,D=62,620,45,350;top=ymax or max(r[key] for r in rows)*1.13
 X=lambda k:L+(k-1)*(R-L)/4
 Y=lambda v:D-v/top*(D-U)
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="62" y="26" font-size="17" font-family="sans-serif">{title}</text>',f'<path d="M {L} {U} V {D} H {R}" fill="none" stroke="#333"/>']
 for k in range(1,6):out.append(f'<text x="{X(k)-4:.1f}" y="371" font-size="13" font-family="sans-serif">{k}</text>')
 for path,color in [('pure_latent','#21618c'),('decode_reencode','#d35400'),('learned_reset','#239b56')]:
  for split,dash in [('test_iid',''),('test_template_ood','6 4')]:
   rr=sorted([r for r in rows if r['path']==path and r['split']==split],key=lambda x:x['step']);assert len(rr)==5
   pts=' '.join(f'{X(r["step"]):.1f},{Y(r[key]):.1f}' for r in rr)
   out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
   out.append(f'<text x="{R+8}" y="{Y(rr[-1][key])+5:.1f}" fill="{color}" font-size="11" font-family="sans-serif">{path.replace("_", " ")} {"IID" if split=="test_iid" else "OOD"}</text>')
 out.append('</svg>');(HERE/name).write_text('\n'.join(out)+'\n')

def category(r,path):
 s=r['reset'] if path=='learned_reset' else r['edited']
 if s['success']:return 'success'
 if s['parse_unresolved'] or s['decoded_semantic_state'] is None:return 'unresolved_decode'
 if not s['fact_preservation']:return 'parsed_content_error'
 return 'parsed_semantic_error'

def main():
 rows=read(G5/'pure_reset_controls.jsonl')+read(G5/'decode_reencode_trajectories.jsonl')+read(HERE/'learned_trajectories.jsonl')
 idx={(r['path'],r['split'],r['world_id'],r['step']):r for r in rows};assert len(rows)==len(idx)==1590
 splits=['test_iid','test_template_ood'];paths=['pure_latent','decode_reencode','learned_reset']
 ids={s:sorted({r['world_id'] for r in rows if r['split']==s}) for s in splits};assert all(len(v)==53 for v in ids.values())
 length=[];geo=[];taxonomy=[];mask=[];paired=[];rng=np.random.default_rng(CFG['bootstrap_seed'])
 for split in splits:
  for path in paths:
   for k in range(1,6):
    rs=[idx[path,split,w,k] for w in ids[split]]
    out=lambda r:r['reset'] if path=='learned_reset' else r['edited']
    endpoint=[out(r)['success'] for r in rs]
    trajectory=[all(out(idx[path,split,w,j])['success'] for j in range(1,k+1)) for w in ids[split]]
    fact=[out(r)['fact_preservation'] for r in rs]
    length.append(dict(path=path,split=split,step=k,n=53,endpoint_count=sum(endpoint),endpoint_pct=pct(endpoint),trajectory_count=sum(trajectory),trajectory_pct=pct(trajectory),fact_count=sum(fact),fact_pct=pct(fact)))
    pre=[r['edited_distance'] for r in rs];post=[r['reset_distance'] for r in rs]
    geo.append(dict(path=path,split=split,step=k,n=53,edited_cosine=avg([r['cosine'] for r in pre]),post_cosine=avg([r['cosine'] for r in post]),edited_normalized_l2=avg([r['normalized_l2'] for r in pre]),post_normalized_l2=avg([r['normalized_l2'] for r in post]),post_l2_improved_count=sum(y['normalized_l2']<x['normalized_l2'] for x,y in zip(pre,post)),mean_editor_residual=avg([r['residual_norm'] for r in rs])))
    for r in rs:
     taxonomy.append(dict(path=path,split=split,world_id=r['world_id'],step=k,category=category(r,path),fact_preservation=out(r)['fact_preservation'],edited_l2=r['edited_distance']['normalized_l2'],post_l2=r['reset_distance']['normalized_l2']))
     if path=='learned_reset':
      mask.append(dict(split=split,world_id=r['world_id'],step=k,learned_success=r['reset']['success'],pre_reset_success=r['edited']['success'],oracle_mask_success=r['oracle_mask']['success'],mask_equal=r['source_target_mask_equal'],token_ids_equal=r['source_target_token_ids_equal'],input_mask_length=r['input_mask_length'],oracle_mask_length=r['oracle_mask_length'],edited_l2=r['edited_distance']['normalized_l2'],learned_l2=r['reset_distance']['normalized_l2'],oracle_l2=r['oracle_distance']['normalized_l2'],learned_to_oracle_l2=r['reset_to_oracle_distance']['normalized_l2']))
  for k in range(1,6):
   for baseline in ['pure_latent','decode_reencode']:
    x=np.array([idx[baseline,split,w,k]['edited']['success'] for w in ids[split]],dtype=int)
    y=np.array([idx['learned_reset',split,w,k]['reset']['success'] for w in ids[split]],dtype=int)
    d=y-x;samples=rng.integers(0,53,size=(CFG['bootstrap_replicates'],53));boots=d[samples].mean(1)
    better=int(((x==0)&(y==1)).sum());worse=int(((x==1)&(y==0)).sum());n=better+worse
    p=min(1.,2*sum(math.comb(n,j) for j in range(min(better,worse)+1))/2**n) if n else 1.
    paired.append(dict(split=split,step=k,baseline=baseline,n=53,baseline_success=int(x.sum()),learned_success=int(y.sum()),learned_minus_baseline_pp=round(float(100*d.mean()),2),ci_low_pp=round(float(100*np.quantile(boots,.025)),2),ci_high_pp=round(float(100*np.quantile(boots,.975)),2),improved_worlds=better,worsened_worlds=worse,mcnemar_exact_p=p))
 save('length_generalization.csv',length);save('representation_distance.csv',geo);save('failure_taxonomy.csv',taxonomy);save('mask_token_diagnostic.csv',mask);save('paired_effects.csv',paired)
 counts=[];diagnostic=[]
 for split in splits:
  for path in paths:
   for k in range(1,6):
    c=Counter(r['category'] for r in taxonomy if r['path']==path and r['split']==split and r['step']==k)
    for cat,n in c.items():counts.append(dict(path=path,split=split,step=k,category=cat,count=n,denominator=53))
  for k in range(1,6):
   rr=[r for r in mask if r['split']==split and r['step']==k];fail=[r for r in rr if not r['learned_success']]
   diagnostic.append(dict(split=split,step=k,n=53,learned_failures=len(fail),mask_mismatch=sum(not r['mask_equal'] for r in rr),token_ids_changed=sum(not r['token_ids_equal'] for r in rr),fail_mask_mismatch=sum(not r['mask_equal'] for r in fail),fail_mask_equal=sum(r['mask_equal'] for r in fail),fail_oracle_mask_rescued=sum(r['oracle_mask_success'] for r in fail),fail_pre_reset_semantic_correct=sum(r['pre_reset_success'] for r in fail),mean_learned_to_oracle_l2=avg([r['learned_to_oracle_l2'] for r in rr])))
 save('failure_counts.csv',counts);save('mask_token_summary.csv',diagnostic)
 chart('length_curve.svg',length,'trajectory_pct','Trajectory success by chain length (%)',100)
 chart('distance_curve.svg',geo,'post_normalized_l2','Active chain representation distance to gold')
 cases=[]
 for split in splits:
  candidates={
   'learned_recovered':[w for w in ids[split] if not idx['pure_latent',split,w,5]['edited']['success'] and all(idx['learned_reset',split,w,k]['reset']['success'] for k in range(1,6))],
   'learned_fails_dre_succeeds':[w for w in ids[split] if not idx['learned_reset',split,w,5]['reset']['success'] and all(idx['decode_reencode',split,w,k]['edited']['success'] for k in range(1,6))],
   'both_resets_fail':[w for w in ids[split] if not idx['learned_reset',split,w,5]['reset']['success'] and not idx['decode_reencode',split,w,5]['edited']['success']]}
  for label,opts in candidates.items():
   if not opts:continue
   w=opts[0];stages=[]
   for k in range(1,6):
    d={'step':k,'gold_text':idx['pure_latent',split,w,k]['gold_text']}
    for path in paths:
     r=idx[path,split,w,k];d[path]=dict(text=r['decoded_text'],success=(r['reset'] if path=='learned_reset' else r['edited'])['success'],pre_reset_text=r.get('edited_text'),post_l2=r['reset_distance']['normalized_l2'],input_mask_length=r.get('input_mask_length',r.get('edited_mask_length')),oracle_mask_length=r.get('oracle_mask_length'))
    stages.append(d)
   cases.append(dict(label=label,split=split,world_id=w,stages=stages))
 jsonsave('typical_trajectories.json',cases)
 jsonsave('summary.json',dict(length=length,geometry=geo,paired=paired,failure_counts=counts,mask_token_summary=diagnostic,examples=[dict(label=r['label'],split=r['split'],world_id=r['world_id']) for r in cases]))

if __name__=='__main__':main()
