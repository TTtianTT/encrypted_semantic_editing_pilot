import csv,json
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
def read(name):return [json.loads(s) for s in (HERE/name).read_text().splitlines()]
def save(name,rs):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)

def main():
    pred={r['key']:r['predicted_offset'] for r in read('mlp_probe_predictions.jsonl')}
    base=read('G3_trajectories.jsonl')
    val=json.loads((HERE/'mlp_probe_validation.json').read_text())
    selected=next(r for r in val['history'] if r['epoch']==val['selected_epoch'])
    out=[];tax=[];cases=defaultdict(list)
    for split in ['test_iid','test_template_ood']:
        for step in range(1,6):
            rr=[r for r in base if r['split']==split and r['path']=='plus_chain' and r['step']==step]
            for r in rr:
                key=f"{split}/{r['world_id']}/plus_chain/{step}"
                p=pred[key];gold=r['gold_semantic_state']['offset']
                prev=pred[f"{split}/{r['world_id']}/plus_chain/{step-1}"] if step>1 else r['source_offset']
                if r['endpoint_success'] and p!=gold:cat='probe_disagrees_with_correct_decode'
                elif not r['fact_preservation'] and not r['parse_unresolved']:cat='decoded_content_error'
                elif step==5 and p==-4:cat='probe_floor_unidentifiable'
                elif p>gold and p==prev:cat='saturation_candidate'
                elif p>gold:cat='understep_candidate'
                elif p<gold:cat='overshoot_candidate'
                elif r['parse_unresolved']:cat='decoder_unresolved_with_correct_probe'
                elif not r['endpoint_success']:cat='decoder_semantic_error_with_correct_probe'
                else:cat='correct'
                tax.append(dict(split=split,world_id=r['world_id'],step=step,gold_offset=gold,probe_offset=p,
                                decoded_offset=r['observed_offset'],category=cat,decoded_success=r['endpoint_success'],
                                parse_unresolved=r['parse_unresolved'],cosine_distance=r['cosine_distance'],normalized_l2=r['normalized_l2']))
                cases[split,r['world_id']].append(dict(step=step,gold_offset=gold,probe_offset=p,decoded_offset=r['observed_offset'],
                                                       output=r['decoded_text'],gold=r['gold_text'],category=cat))
            out.append(dict(split=split,step=step,n=len(rr),probe_accuracy=round(100*sum(pred[f"{split}/{r['world_id']}/plus_chain/{step}"]==r['gold_semantic_state']['offset'] for r in rr)/len(rr),2),
                            decoded_success=round(100*sum(r['endpoint_success'] for r in rr)/len(rr),2),
                            parse_unresolved=round(100*sum(r['parse_unresolved'] for r in rr)/len(rr),2),
                            dev_probe_accuracy_at_trained_step=round(100*selected['dev_accuracy_by_step'][step],2) if step<=2 else 'untrained_length'))
    save('mlp_probe_trajectory.csv',out);save('mlp_failure_taxonomy.csv',tax)
    counts=[]
    for split in ['test_iid','test_template_ood']:
        for step in range(1,6):
            c=Counter(r['category'] for r in tax if r['split']==split and r['step']==step)
            for category,n in c.items():counts.append(dict(split=split,step=step,category=category,n=n,denominator=53,percent=round(100*n/53,2)))
    save('mlp_failure_counts.csv',counts)
    exemplar=[]
    for split in ['test_iid','test_template_ood']:
        selection=[w for (s,w),st in cases.items() if s==split and st[2]['category']=='decoder_unresolved_with_correct_probe'][:1]
        selection += [w for (s,w),st in cases.items() if s==split and st[2]['category']=='overshoot_candidate'][:1]
        for w in selection:exemplar.append(dict(split=split,world_id=w,trajectory=cases[split,w]))
    (HERE/'typical_trajectories_mlp.json').write_text(json.dumps(exemplar,ensure_ascii=False,indent=2)+'\n')
    (HERE/'mlp_summary.json').write_text(json.dumps(dict(probe_trajectory=out,failure_counts=counts,dev_selected_epoch=selected),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
