import csv,json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
def read(name):return [json.loads(s) for s in (HERE/name).read_text().splitlines()]
def save(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    pred={r['key']:r for r in read('gold_probe_predictions.jsonl')}
    rows=read('pure_reset_controls.jsonl')+read('decode_reencode_trajectories.jsonl')
    out=[];detail=[]
    for path in ['pure_latent','decode_reencode']:
        for split in ['test_iid','test_template_ood']:
            for step in range(1,6):
                rr=[r for r in rows if r['path']==path and r['split']==split and r['step']==step]
                assert len(rr)==53
                pp=[pred[f'{"pure" if path=="pure_latent" else "decode_reencode"}/{split}/{r["world_id"]}/{step}'] for r in rr]
                reset_correct=[];edited_correct=[];gold_correct=[];same_success=[];same_fail=[]
                for r,p in zip(rr,pp):
                    gold=r['gold_semantic_state']['offset']
                    z=p['reset_offset']==gold;reset_correct.append(z);edited_correct.append(p['edited_offset']==gold);gold_correct.append(p['gold_offset']==gold)
                    (same_success if r['edited']['success'] else same_fail).append(z)
                    detail.append(dict(path=path,split=split,world_id=r['world_id'],step=step,gold_offset=gold,
                                       edited_gold_probe_offset=p['edited_offset'],reset_gold_probe_offset=p['reset_offset'],
                                       gold_encoder_probe_offset=p['gold_offset'],decoded_success=r['edited']['success'],
                                       reset_decoded_success=r['reset']['success']))
                out.append(dict(path=path,split=split,step=step,n=53,
                                gold_encoder_probe_accuracy=round(100*sum(gold_correct)/53,2),
                                edited_gold_probe_accuracy=round(100*sum(edited_correct)/53,2),
                                reset_gold_probe_accuracy=round(100*sum(reset_correct)/53,2),
                                reset_probe_accuracy_given_decoded_success=round(100*sum(same_success)/len(same_success),2) if same_success else '',
                                reset_probe_accuracy_given_decoded_failure=round(100*sum(same_fail)/len(same_fail),2) if same_fail else ''))
    save('gold_probe_trajectory.csv',out);save('gold_probe_per_record.csv',detail)

if __name__=='__main__':main()
