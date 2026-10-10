"""Lock methods and data before evaluation. No independent-confirmation claim."""
from shared import *

def main():
    assert not (ROOT/'protocol.json').exists(), 'Protocol already locked'
    train=rows(V2/'train_worlds.jsonl');test=rows(V2/'eval_worlds.jsonl')
    ids=[w['world_id'] for w in train];rng=np.random.default_rng(3101);ix=rng.permutation(len(ids))
    dev=[ids[i] for i in ix[:16]];fit=[ids[i] for i in ix[16:]]
    key=lambda w:tuple(w[k] for k in ('object','color','quantity','status'))
    assert not(set(map(key,train))&set(map(key,test)))
    inputs=dict(read(V2/'protocol.json')['inputs'])
    for p in [V2/'REPORT.md',V2/'results/audit.json',V2/'results/artifact_manifest.json',V2/'results/projection.jsonl',V2/'results/attribution.jsonl']:
        inputs[str(p)]=sha(p)
    for seed in SEEDS:
        p=V2/f'local/fit_s{seed}.pt';inputs[str(p)]=sha(p)
    sources={p.name:sha(p) for p in ROOT.iterdir() if p.suffix in ('.py','.slurm')}
    dump('protocol.json',dict(version=1,neural_training=False,seeds=list(SEEDS),ranks=[16,64,256,768],
       fitting_worlds=ids,fit_partition=fit,dev_partition=dev,eval_worlds=[w['world_id'] for w in test],
       exposure='Same 80 historical analysis-held-out worlds; not a fresh confirmation set',
       fit_conditions={'iid_only':[0],'aligned_templates':[0,3]},eval_templates=[0,3],states=list(range(-3,4)),
       operators=['plus','minus'],sequences=read(V2/'protocol.json')['sequences'],
       ridge_relative_grid=[1e-6,1e-4,1e-2],ridge_scaling='lambda=relative*trace(Xc.T Xc/N)/768',
       ridge_selection='Per condition/operator/rank: minimum dev token MSE; refit all 96 training worlds',
       objective='mean_token ||Yc-Xc B||^2 + lambda ||B||_F^2; affine intercept unpenalized',
       rank_solution='SVD of G^(-1/2) Xc.T Yc/N, G=Xc.T Xc/N+lambda I; augmented-design fitted-value truncation',
       alignment='Fit only world/state transitions with identical attention masks; residual metrics NA otherwise',
       token_weighting='Equal valid-token weight; no position-specific parameters',
       probe_ridge_relative=.001,probe_fit_templates=[0],probe_states=list(range(-3,4)),
       probe='Seven-way canonical-state ridge classifier: full, separately fitted S and S-complement; shared full-probe margins also decomposed',
       random_seeds=[31011,31012,31013,31014],norm_control='Per-world, masked-token Frobenius norm equals actual edited-state ridge displacement',
       control_contexts=['edited','canonical'],control_conditions=['none','ridge_delta','random_full','random4'],
       control_source_state=1,control_current_state=0,control_next_operation='plus',
       failure_priority=['unparseable_or_invalid_grammar','non_target_corruption','edit_not_executed','wrong_state'],
       maximum_gpus=1,total_allocation_cap_seconds=5400,inputs=inputs,sources=sources))
    print('Locked 96 train / 80 historical evaluation worlds; 80/16 train/dev split.')

if __name__=='__main__':main()
