"""Matched-world summaries for G5 with a fixed paired bootstrap."""
import csv,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/'config.json').read_text())

def read(name):return [json.loads(s) for s in (HERE/name).read_text().splitlines()]
def save_csv(name,records):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
def save_json(name,x):(HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def pct(x):return round(100*sum(x)/len(x),2)
def avg(x):return round(sum(x)/len(x),6)

def curve(name,rows,ykey,title,top=None):
    width,height=700,390;left,right,up,down=60,610,40,330
    values=[float(r[ykey]) for r in rows]
    ymax=top or max(values)*1.12 or 1
    def X(k):return left+(k-1)*(right-left)/4
    def Y(v):return down-float(v)/ymax*(down-up)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="700" height="390" fill="white"/>',
         f'<text x="60" y="24" font-family="sans-serif" font-size="16">{title}</text>',
         f'<path d="M {left} {up} V {down} H {right}" fill="none" stroke="#333"/>']
    for k in range(1,6):out.append(f'<text x="{X(k)-4:.1f}" y="350" font-family="sans-serif" font-size="12">{k}</text>')
    for path,color in [('pure_latent','#1261a0'),('decode_reencode','#d55e00')]:
        for split,dash in [('test_iid',''),('test_template_ood','6 4')]:
            rr=sorted([r for r in rows if r['path']==path and r['split']==split],key=lambda x:x['step'])
            pts=' '.join(f'{X(r["step"]):.1f},{Y(r[ykey]):.1f}' for r in rr)
            out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
            out.append(f'<text x="{right+8}" y="{Y(rr[-1][ykey])+4:.1f}" font-family="sans-serif" font-size="10" fill="{color}">{"pure" if path=="pure_latent" else "reencode"} {"IID" if split=="test_iid" else "OOD"}</text>')
    out.append('</svg>')
    (HERE/name).write_text('\n'.join(out)+'\n')

def main():
    records=read('pure_reset_controls.jsonl')+read('decode_reencode_trajectories.jsonl')
    idx={(r['path'],r['split'],r['world_id'],r['step']):r for r in records}
    assert len(records)==len(idx)==1060
    worldids={split:sorted({r['world_id'] for r in records if r['split']==split}) for split in ['test_iid','test_template_ood']}
    length=[];geo=[];tax=[];pair=[];reset=[]
    rng=np.random.default_rng(CFG['bootstrap_seed'])
    for split,ids in worldids.items():
        assert len(ids)==53
        for path in ['pure_latent','decode_reencode']:
            for k in range(1,6):
                rr=[idx[path,split,w,k] for w in ids]
                endpoint=[r['edited']['success'] for r in rr]
                trajectory=[all(idx[path,split,w,j]['edited']['success'] for j in range(1,k+1)) for w in ids]
                fact=[r['edited']['fact_preservation'] for r in rr]
                facttraj=[all(idx[path,split,w,j]['edited']['fact_preservation'] for j in range(1,k+1)) for w in ids]
                length.append(dict(path=path,split=split,step=k,n=53,endpoint_count=sum(endpoint),endpoint_pct=pct(endpoint),
                                   trajectory_count=sum(trajectory),trajectory_pct=pct(trajectory),
                                   endpoint_fact_count=sum(fact),endpoint_fact_pct=pct(fact),
                                   trajectory_fact_count=sum(facttraj),trajectory_fact_pct=pct(facttraj)))
                geo.append(dict(path=path,split=split,step=k,n=53,
                                edited_cosine=avg([r['edited_distance']['cosine'] for r in rr]),
                                reset_cosine=avg([r['reset_distance']['cosine'] for r in rr]),
                                cosine_change_post_minus_pre=avg([r['reset_distance']['cosine']-r['edited_distance']['cosine'] for r in rr]),
                                edited_normalized_l2=avg([r['edited_distance']['normalized_l2'] for r in rr]),
                                reset_normalized_l2=avg([r['reset_distance']['normalized_l2'] for r in rr]),
                                l2_change_post_minus_pre=avg([r['reset_distance']['normalized_l2']-r['edited_distance']['normalized_l2'] for r in rr]),
                                reset_l2_improved_pct=pct([r['reset_distance']['normalized_l2']<r['edited_distance']['normalized_l2'] for r in rr]),
                                edited_probe_correct_pct=pct([r['edited_probe_offset']==r['gold_semantic_state']['offset'] for r in rr]),
                                reset_probe_correct_pct=pct([r['reset_probe_offset']==r['gold_semantic_state']['offset'] for r in rr]),
                                mean_residual_norm=avg([r['residual_norm'] for r in rr]),
                                reset_same_stage_success_pct=pct([r['reset']['success'] for r in rr])))
                for r in rr:
                    sc=r['edited'];gold=r['gold_semantic_state']['offset']
                    parsed=sc['decoded_semantic_state']
                    if sc['success']:cat='success'
                    elif sc['parse_unresolved']:cat='unresolved_decode'
                    elif not sc['fact_preservation']:cat='parsed_content_error'
                    elif parsed['event_date']!=r['gold_frame']['view_date'] and not sc['success']:cat='parsed_semantic_error'
                    else:cat='parsed_semantic_error'
                    tax.append(dict(path=path,split=split,world_id=r['world_id'],step=k,category=cat,
                                    gold_offset=gold,edited_probe_offset=r['edited_probe_offset'],reset_probe_offset=r['reset_probe_offset'],
                                    probe_correct_decoder_failed=(r['edited_probe_offset']==gold and not sc['success']),
                                    edited_success=sc['success'],reset_same_stage_success=r['reset']['success'],
                                    fact_preservation=sc['fact_preservation'],edited_l2=r['edited_distance']['normalized_l2'],
                                    reset_l2=r['reset_distance']['normalized_l2']))
        for k in range(1,6):
            a=[idx['pure_latent',split,w,k] for w in ids];b=[idx['decode_reencode',split,w,k] for w in ids]
            ea=np.array([r['edited']['success'] for r in a],dtype=float);eb=np.array([r['edited']['success'] for r in b],dtype=float)
            ta=np.array([all(idx['pure_latent',split,w,j]['edited']['success'] for j in range(1,k+1)) for w in ids],dtype=float)
            tb=np.array([all(idx['decode_reencode',split,w,j]['edited']['success'] for j in range(1,k+1)) for w in ids],dtype=float)
            sample=rng.integers(0,len(ids),size=(CFG['bootstrap_replicates'],len(ids)))
            for metric,x,y in [('endpoint',ea,eb),('trajectory',ta,tb)]:
                diff=y-x; boot=diff[sample].mean(1)
                better=int(((x==0)&(y==1)).sum());worse=int(((x==1)&(y==0)).sum());discordant=better+worse
                exact_p=min(1.,2*sum(math.comb(discordant,j) for j in range(min(better,worse)+1))/2**discordant) if discordant else 1.
                pair.append(dict(split=split,step=k,metric=metric,n=53,pure_count=int(x.sum()),reencode_count=int(y.sum()),
                                 reencode_minus_pure_pp=round(float(100*diff.mean()),2),
                                 ci_low_pp=round(float(100*np.quantile(boot,.025)),2),ci_high_pp=round(float(100*np.quantile(boot,.975)),2),
                                 improved_worlds=better,worsened_worlds=worse,mcnemar_exact_p=exact_p))
            subset=[i for i,r in enumerate(a) if r['edited_probe_offset']==r['gold_semantic_state']['offset'] and not r['edited']['success']]
            reset.append(dict(split=split,step=k,pure_probe_correct_decoder_failed=len(subset),
                              same_stage_reset_success=sum(a[i]['reset']['success'] for i in subset),
                              reencode_path_success=sum(b[i]['edited']['success'] for i in subset),
                              reencode_path_trajectory_success=sum(all(idx['decode_reencode',split,ids[i],j]['edited']['success'] for j in range(1,k+1)) for i in subset),
                              pure_post_l2_better=sum(a[i]['reset_distance']['normalized_l2']<a[i]['edited_distance']['normalized_l2'] for i in subset)))
    save_csv('length_generalization.csv',length)
    save_csv('representation_reset.csv',geo)
    save_csv('paired_effects.csv',pair)
    save_csv('probe_decoder_recovery.csv',reset)
    save_csv('failure_taxonomy.csv',tax)
    counts=[]
    for path in ['pure_latent','decode_reencode']:
        for split in worldids:
            for k in range(1,6):
                c=Counter(r['category'] for r in tax if r['path']==path and r['split']==split and r['step']==k)
                for cat,n in c.items():counts.append(dict(path=path,split=split,step=k,category=cat,n=n,denominator=53,pct=round(100*n/53,2)))
    save_csv('failure_counts.csv',counts)
    curve('length_curve.svg',length,'trajectory_pct','Trajectory success (%)',100)
    curve('distance_curve.svg',geo,'edited_normalized_l2','Edited latent distance to gold')
    # Matched trajectory examples selected by predeclared outcome patterns.
    examples=[]
    for split,ids in worldids.items():
        recovered=[w for w in ids if not idx['pure_latent',split,w,4]['edited']['success'] and all(idx['decode_reencode',split,w,j]['edited']['success'] for j in range(1,6))]
        failed=[w for w in ids if not idx['decode_reencode',split,w,5]['edited']['success']]
        for label,choices in [('recovered',recovered),('reencode_failed',failed)]:
            if not choices:continue
            w=choices[0]
            examples.append(dict(label=label,split=split,world_id=w,
                                 pure=[idx['pure_latent',split,w,j] for j in range(1,6)],
                                 decode_reencode=[idx['decode_reencode',split,w,j] for j in range(1,6)]))
    save_json('typical_trajectories.json',examples)
    save_json('summary.json',dict(length=length,geometry=geo,paired_effects=pair,probe_decoder_recovery=reset,failure_counts=counts,
                                  examples=[dict(label=x['label'],split=x['split'],world_id=x['world_id']) for x in examples]))

if __name__=='__main__':main()
