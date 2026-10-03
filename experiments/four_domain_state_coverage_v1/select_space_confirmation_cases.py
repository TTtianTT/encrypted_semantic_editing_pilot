"""CPU-only descriptive audit; fixed worlds/paths, no next-outcome selection."""
from common import *

def main():
    base=ROOT.parent/'space_relation_confirmation_v1'
    first=min(w['world_id'] for w in rows(base/'data/space/worlds.jsonl') if w['split']=='test')
    cases=[];counts=[];successes=[];missing=[]
    for seed in (42,43,44):
        path=base/f'runs/formal/t5gemma_space_s{seed}/outputs/P/trajectory_t0.jsonl'
        if not path.exists():missing.append(seed);continue
        rr=rows(path);lookup={(r['world_id'],r['trajectory'],r['mode'],r['step']):r for r in rr}
        eligible=[r for r in rr if r['mode']=='latent' and r['step']==2 and r['previous_correct'] and lookup[(r['world_id'],r['trajectory'],'gold_reencode',2)]['score']['success']]
        counts.append(dict(seed=seed,eligible=len(eligible),worlds=len({r['world_id'] for r in eligible}),strict_success=sum(r['score']['success'] for r in eligible),strict_failed=sum(not r['score']['success'] for r in eligible),parsed_slot_mismatch=sum(r['score']['parseable'] and r['score']['grammar'] and r['score']['ended'] and not (r['score']['target'] and r['score']['preserved']) for r in eligible)))
        successes.extend(dict(seed=seed,artifact=str(path.relative_to(base)),row=r) for r in eligible if r['score']['success'])
        for trajectory in ('forward','reverse','inverse'):
            cur=lookup[(first,trajectory,'latent',1)];nxt=lookup[(first,trajectory,'latent',2)];control=lookup[(first,trajectory,'gold_reencode',2)]
            cases.append(dict(case_id=f'space_relation_confirmation_v1/t5gemma/s{seed}/{first}/{trajectory}',seed=seed,world_id=first,trajectory=trajectory,current=cur,next=nxt,gold_reencode_control=control,artifact=str(path.relative_to(base)),artifact_sha256=digest(path),checkpoint_sha256=digest(base/f'local/formal/t5gemma_space_s{seed}/P/best.pt'),selection='First test world, all three formal seeds and all three predefined core trajectories, steps1/2; no next-outcome filter',review_status='not automatically labeled; see separate assistant review'))
    jsonl(base/'continuation_review_set.jsonl',cases);jsonl(base/'continuation_success_counterexamples.jsonl',successes)
    dump(base/'CONTINUATION_CASE_SELECTION.json',dict(counts=counts,unavailable_seed_shards=missing,case_set_sha256=digest(base/'continuation_review_set.jsonl'),complete_three_seed_P_core_review_set=not missing,does_not_establish_formal_NSM_completion=True,independent_human_labels=False))
    print(json.dumps(dict(counts=counts,selected_cases=len(cases),success_counterexamples=len(successes),unavailable_seed_shards=missing)))

if __name__=='__main__':main()
