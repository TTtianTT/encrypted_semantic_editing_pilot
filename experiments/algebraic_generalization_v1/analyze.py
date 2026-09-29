"""Aggregate fixed G4 trajectories without fitting on test outcomes."""
import csv, json, statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return [json.loads(x) for x in (HERE / name).read_text().splitlines()]


def write_csv(name, records):
    with (HERE / name).open('w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n'); wr.writeheader(); wr.writerows(records)


def mean(xs): return sum(xs)/len(xs) if xs else None


def pct(xs): return round(100*mean(xs), 2) if xs else None


def main():
    probes = json.loads((HERE/'probe_accuracy.json').read_text())
    pidx = {(p['layer'],p['position'],p['attribute']):p for p in probes}
    records = read('G3_trajectories.jsonl')+read('repair_trajectories.jsonl')
    reliable_content=[a for a in ['author','recipient','action','object','quantity','record_status','polarity']
                      if pidx[6,'mean',a]['dev_accuracy']>=0.95]
    for r in records:
        r['reliable_content_probe_ok']=all(r['probe'][a]==r['gold_semantic_state']['content'][a] for a in reliable_content)
    keyed = defaultdict(list)
    for r in records: keyed[r['group'],r['split'],r['path'],r['world_id']].append(r)
    trajectories = []
    for (g,s,p,w), steps in keyed.items():
        steps.sort(key=lambda x:x['step'])
        trajectories.append(dict(group=g,split=s,path=p,world_id=w,length=len(steps),
                                 endpoint_success=steps[-1]['endpoint_success'],
                                 trajectory_success=all(x['endpoint_success'] for x in steps),
                                 fact_preservation=all(x['fact_preservation'] for x in steps),
                                 endpoint_fact_preservation=steps[-1]['fact_preservation'],
                                 unresolved=any(x['parse_unresolved'] for x in steps)))
    write_csv('per_trajectory.csv',trajectories)
    length=[]
    for (g,s), rs in sorted(groupby(trajectories, lambda x:(x['group'],x['split'])).items()):
        for k in range(1,6):
            chain = [keyed[g,s,'plus_chain',r['world_id']][:k] for r in rs if r['path']=='plus_chain']
            assert len(chain)==53
            length.append(dict(group=g,split=s,length=k,n=len(chain),endpoint_success=pct([x[-1]['endpoint_success'] for x in chain]),
                               trajectory_success=pct([all(y['endpoint_success'] for y in x) for x in chain]),
                               fact_preservation=pct([all(y['fact_preservation'] for y in x) for x in chain]),
                               endpoint_fact_preservation=pct([x[-1]['fact_preservation'] for x in chain])))
    write_csv('length_generalization.csv',length)
    svg_curve('length_curve.svg', length, 'length', 'trajectory_success', 'Trajectory success (%)', 0, 100)
    algebra=[]
    for (g,s,p), rs in sorted(groupby(trajectories, lambda x:(x['group'],x['split'],x['path'])).items()):
        if p=='plus_chain': continue
        last=[keyed[g,s,p,r['world_id']][-1] for r in rs]
        algebra.append(dict(group=g,split=s,path=p,n=len(rs),latent_cosine_distance=round(mean([x['cosine_distance'] for x in last]),5),
                            latent_normalized_l2=round(mean([x['normalized_l2'] for x in last]),5),
                            decoded_endpoint_success=pct([x['endpoint_success'] for x in last]),
                            decoded_trajectory_success=pct([r['trajectory_success'] for r in rs]),
                            fact_preservation=pct([r['fact_preservation'] for r in rs])))
    # Commutator compares two actual edited memories for each paired world.
    import torch
    for g in ['G3','repair']:
        latents=torch.load(HERE/f'{g}_latents.pt',map_location='cpu',weights_only=False)
        for s in ['test_iid','test_template_ood']:
            diffs=[]; semantic=[]
            for w in {r['world_id'] for r in trajectories if r['group']==g and r['split']==s}:
                a=latents[f'{s}/{w}/plus_person/2']; b=latents[f'{s}/{w}/person_plus/2']
                m=a['mask'].bool(); assert torch.equal(a['mask'],b['mask'])
                av=a['latent'][m].float();bv=b['latent'][m].float()
                diffs.append(float((av-bv).norm()/bv.norm()))
                ap=keyed[g,s,'plus_person',w][-1];bp=keyed[g,s,'person_plus',w][-1]
                semantic.append(ap['decoded_semantic_state']==bp['decoded_semantic_state'] and ap['decoded_semantic_state'] is not None)
            algebra.append(dict(group=g,split=s,path='commutator_P_T',n=len(diffs),latent_cosine_distance='',
                                latent_normalized_l2=round(mean(diffs),5),decoded_endpoint_success=pct(semantic),
                                decoded_trajectory_success='',fact_preservation=''))
    write_csv('algebraic_consistency.csv',algebra)
    geo=[]
    for (g,s,k), rs in sorted(groupby([x for x in records if x['path']=='plus_chain'],lambda x:(x['group'],x['split'],x['step'])).items()):
        geo.append(dict(group=g,split=s,step=k,n=len(rs),cosine_distance=round(mean([r['cosine_distance'] for r in rs]),6),
                        normalized_l2=round(mean([r['normalized_l2'] for r in rs]),6),
                        time_projection_distance=round(mean([r['projection_distance'] for r in rs]),6),
                        nearest_gold_correct=pct([r['nearest_gold_offset']==r['gold_semantic_state']['offset'] for r in rs]),
                        residual_norm=round(mean([r['residual_norm'] for r in rs]),6),
                        residual_direction_cosine=round(mean([r['residual_direction_cosine'] for r in rs if r['residual_direction_cosine'] is not None]),6) if k>1 else '',
                        probe_time_accuracy=pct([r['probe']['offset']==r['gold_semantic_state']['offset'] for r in rs]),
                        probe_content_all_correct=pct([r['content_probe_ok'] for r in rs]),
                        reliable_content_probe_correct=pct([r['reliable_content_probe_ok'] for r in rs])))
    write_csv('representation_distance.csv',geo)
    svg_curve('representation_curve.svg', geo, 'step', 'normalized_l2', 'Normalized L2 to gold', 0, None)
    taxonomy=[]
    for (g,s,w), steps in sorted(groupby([x for x in records if x['path']=='plus_chain'],lambda x:(x['group'],x['split'],x['world_id'])).items()):
        steps.sort(key=lambda x:x['step'])
        for i, r in enumerate(steps):
            gold=r['gold_semantic_state']['offset']; probe=r['probe']['offset']; prev=steps[i-1]['probe']['offset'] if i else r['source_offset']
            if not r['fact_preservation'] and not r['parse_unresolved']: cat='decoded_content_error'
            elif r['parse_unresolved']: cat='unresolved_decode'
            elif probe==gold and not r['endpoint_success']: cat='decoder_semantic_error'
            elif probe>gold and probe==prev: cat='operator_saturation'
            elif probe>gold: cat='operator_understep'
            elif probe<gold: cat='operator_overshoot'
            elif r['endpoint_success'] and not r['reliable_content_probe_ok']: cat='content_probe_mismatch'
            else: cat='correct'
            taxonomy.append(dict(group=g,split=s,world_id=w,step=r['step'],gold_offset=gold,probe_offset=probe,
                                 decoded_offset=r['observed_offset'],category=cat,cosine_distance=r['cosine_distance'],
                                 content_probe_ok=r['reliable_content_probe_ok'],decoded_success=r['endpoint_success']))
    write_csv('failure_taxonomy.csv',taxonomy)
    counts=[]
    for (g,s,k,c), rs in sorted(groupby(taxonomy,lambda x:(x['group'],x['split'],x['step'],x['category'])).items()):
        counts.append(dict(group=g,split=s,step=k,category=c,n=len(rs),denominator=53,percent=round(100*len(rs)/53,2)))
    write_csv('failure_taxonomy_counts.csv',counts)
    sample=[]
    for g,s,w in [('G3','test_iid',next(r['world_id'] for r in trajectories if r['group']=='G3' and r['split']=='test_iid' and r['path']=='plus_chain' and not r['endpoint_success'])),
                  ('repair','test_iid',next(r['world_id'] for r in trajectories if r['group']=='repair' and r['split']=='test_iid' and r['path']=='plus_chain'))]:
        sample += keyed[g,s,'plus_chain',w]
    with (HERE/'typical_trajectories.jsonl').open('w') as f:
        for x in sample: f.write(json.dumps(x,ensure_ascii=False)+'\n')
    write_json('summary.json',dict(length=length,geometry=geo,algebra=algebra,taxonomy_counts=counts,
                                   final_mean_probe_time_accuracy=pidx[6,'mean','offset']['test_accuracy'],
                                   reliable_content_attributes=reliable_content,
                                   test_stages=len(records),trajectories=len(trajectories)))


def groupby(rows, func):
    out=defaultdict(list)
    for r in rows: out[func(r)].append(r)
    return out


def write_json(name, obj): (HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def svg_curve(name, rows, xkey, ykey, title, ymin, ymax):
    colors={'G3':'#1261a0','repair':'#d55e00'}
    values=[float(r[ykey]) for r in rows]
    top=max(values)*1.12 if ymax is None else ymax
    top=max(top, 0.01)
    left,right,up,down=65,620,40,330
    def px(x): return left+(x-1)*(right-left)/4
    def py(y): return down-(float(y)-ymin)/(top-ymin)*(down-up)
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="700" height="390" viewBox="0 0 700 390">',
         '<rect width="700" height="390" fill="white"/>',
         f'<text x="65" y="24" font-family="sans-serif" font-size="16">{title}</text>',
         f'<path d="M {left} {up} V {down} H {right}" fill="none" stroke="#333"/>']
    for tick in range(1,6):out.append(f'<text x="{px(tick)-4:.1f}" y="350" font-family="sans-serif" font-size="12">{tick}</text>')
    for g in ['G3','repair']:
        for split, dash in [('test_iid',''),('test_template_ood','6 4')]:
            rr=sorted([r for r in rows if r['group']==g and r['split']==split],key=lambda x:x[xkey])
            pts=' '.join(f'{px(int(r[xkey])):.1f},{py(r[ykey]):.1f}' for r in rr)
            out.append(f'<polyline points="{pts}" fill="none" stroke="{colors[g]}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
            out.append(f'<text x="{right+10}" y="{py(rr[-1][ykey])+4:.1f}" font-family="sans-serif" font-size="11" fill="{colors[g]}">{g} {"IID" if split=="test_iid" else "OOD"}</text>')
    out.append('</svg>')
    (HERE/name).write_text('\n'.join(out)+'\n')


if __name__=='__main__': main()
