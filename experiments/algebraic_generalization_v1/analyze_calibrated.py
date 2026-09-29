import csv,json
from collections import Counter,defaultdict
from pathlib import Path
import torch

HERE=Path(__file__).resolve().parent

def read(name):return [json.loads(s) for s in (HERE/name).read_text().splitlines()]
def csvout(name,records):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)

def main():
    val=json.loads((HERE/'calibrated_probe_validation.json').read_text())
    valid={(r['group'],r['step'],r['attribute']):r['dev_accuracy'] for r in val['accuracy']}
    reliable={g:[a for a in ['author','recipient','action','object','quantity','record_status','polarity']
                 if min(valid[g,1,a],valid[g,2,a])>=.95] for g in ['G3','repair']}
    preds={r['key']:r['prediction'] for r in read('calibrated_probe_predictions.jsonl')}
    stages=read('G3_trajectories.jsonl')+read('repair_trajectories.jsonl')
    for r in stages:
        key=f"{r['split']}/{r['world_id']}/{r['path']}/{r['step']}"
        r['calibrated_probe']=preds[key]
    stats=[]
    for g in ['G3','repair']:
        for split in ['test_iid','test_template_ood']:
            for k in range(1,6):
                ss=[r for r in stages if r['group']==g and r['split']==split and r['path']=='plus_chain' and r['step']==k]
                stats.append(dict(group=g,split=split,step=k,n=len(ss),time_probe_accuracy=round(100*sum(r['calibrated_probe']['offset']==r['gold_semantic_state']['offset'] for r in ss)/len(ss),2),
                                  person_probe_accuracy=round(100*sum(r['calibrated_probe']['person']==r['gold_semantic_state']['person'] for r in ss)/len(ss),2),
                                  reliable_content_probe_accuracy=round(100*sum(all(r['calibrated_probe'][a]==r['gold_semantic_state']['content'][a] for a in reliable[g]) for r in ss)/len(ss),2),
                                  dev_probe_step1=round(100*valid[g,1,'offset'],2),dev_probe_step2=round(100*valid[g,2,'offset'],2)))
    csvout('calibrated_probe_trajectory.csv',stats)
    taxonomy=[]
    for g in ['G3','repair']:
        for split in ['test_iid','test_template_ood']:
            byworld=defaultdict(list)
            for r in stages:
                if r['group']==g and r['split']==split and r['path']=='plus_chain':byworld[r['world_id']].append(r)
            for w,rr in byworld.items():
                rr.sort(key=lambda z:z['step'])
                for i,r in enumerate(rr):
                    gold=r['gold_semantic_state']['offset'];probe=r['calibrated_probe']['offset']
                    previous=rr[i-1]['calibrated_probe']['offset'] if i else r['source_offset']
                    decoded=r['decoded_semantic_state']
                    if r['endpoint_success'] and probe!=gold:typ='probe_disagrees_with_correct_decode'
                    elif not r['fact_preservation'] and not r['parse_unresolved']:typ='decoded_content_error'
                    elif probe>gold and probe==previous:typ='operator_saturation_candidate'
                    elif probe>gold:typ='operator_understep_candidate'
                    elif probe<gold:typ='operator_overshoot_candidate'
                    elif r['parse_unresolved']:typ='unresolved_decode_with_correct_probe'
                    elif not r['endpoint_success']:typ='decoder_semantic_error_with_correct_probe'
                    elif any(r['calibrated_probe'][a]!=r['gold_semantic_state']['content'][a] for a in reliable[g]):typ='content_probe_mismatch'
                    else:typ='correct'
                    taxonomy.append(dict(group=g,split=split,world_id=w,step=r['step'],category=typ,
                                         gold_offset=gold,probe_offset=probe,decoded_offset=r['observed_offset'],
                                         decoded_success=r['endpoint_success'],fact_preservation=r['fact_preservation'],
                                         normalized_l2=r['normalized_l2']))
    csvout('calibrated_failure_taxonomy.csv',taxonomy)
    counts=[]
    for g in ['G3','repair']:
        for split in ['test_iid','test_template_ood']:
            for k in range(1,6):
                c=Counter(r['category'] for r in taxonomy if r['group']==g and r['split']==split and r['step']==k)
                for cat,n in c.items():counts.append(dict(group=g,split=split,step=k,category=cat,n=n,denominator=53,percent=round(100*n/53,2)))
    csvout('calibrated_failure_counts.csv',counts)
    source=torch.load(HERE/'source_latents.pt',map_location='cpu',weights_only=False)
    inv=[]
    for g in ['G3','repair']:
        latent=torch.load(HERE/f'{g}_latents.pt',map_location='cpu',weights_only=False)
        for split in ['test_iid','test_template_ood']:
            for path in ['plus_minus','minus_plus']:
                vals=[]
                for w in {r['world_id'] for r in stages if r['group']==g and r['split']==split}:
                    h0=source[f'{split}/{w}'];h2=latent[f'{split}/{w}/{path}/2'];m=h0['mask'].bool()
                    a=h0['latent'][m].float();b=h2['latent'][m].float()
                    vals.append(float((a-b).norm()/a.norm()))
                inv.append(dict(group=g,split=split,path=path,n=len(vals),mean_full_latent_relative_l2=round(sum(vals)/len(vals),6)))
    csvout('inverse_full_latent.csv',inv)
    (HERE/'calibrated_summary.json').write_text(json.dumps(dict(reliable_content_attributes=reliable,probe_trajectory=stats,taxonomy_counts=counts,inverse_full_latent=inv),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
