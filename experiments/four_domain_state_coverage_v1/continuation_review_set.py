"""Fixed readable continuation review set, selected without next-output scores."""
from common import *

def main():
    result=[]
    for domain in ('time','person'):
        first_world=min(w['world_id'] for w in rows(ROOT/f'data/{domain}/worlds.jsonl') if w['split']=='test')
        for seed in (42,43,44):
            p=ROOT/f'runs/formal/bart_{domain}_s{seed}/outputs/P/trajectory_t0.jsonl'
            if not p.exists():continue
            rr=rows(p)
            for trajectory in ('forward','reverse','inverse'):
                current=next(r for r in rr if r['world_id']==first_world and r['trajectory']==trajectory and r['mode']=='latent' and r['step']==1)
                continuation=next(r for r in rr if r['world_id']==first_world and r['trajectory']==trajectory and r['mode']=='latent' and r['step']==2)
                control=next(r for r in rr if r['world_id']==first_world and r['trajectory']==trajectory and r['mode']=='gold_reencode' and r['step']==2)
                result.append(dict(model='bart',domain=domain,seed=seed,world_id=first_world,trajectory=trajectory,current=current,next=continuation,gold_reencode_next=control,selection='first test world, all three seeds, all three predefined core trajectories, steps1/2; no next-score filter',review_status='pending_agent_review; no independent human label'))
    jsonl(ROOT/'continuation_review_set.jsonl',result)
    for r in result:print(json.dumps(dict(domain=r['domain'],seed=r['seed'],trajectory=r['trajectory'],current=r['current']['prediction'],next=r['next']['prediction'],control=r['gold_reencode_next']['prediction'],gold=r['next']['gold']),ensure_ascii=False))

if __name__=='__main__':main()
