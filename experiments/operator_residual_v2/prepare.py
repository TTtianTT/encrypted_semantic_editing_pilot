"""Lock data and scientific choices before new held-out interventions."""
from core import *

def main():
    if (ROOT/'protocol.json').exists():raise RuntimeError('Protocol already locked')
    train=[r for r in rows(SOURCE/'data/time/worlds.jsonl') if r['split']=='train']
    ids=read(V1/'protocol.json')['world_ids']
    pool={r['world_id']:r for r in rows(CES/'configs/worlds.jsonl')}
    test=[pool[w] for w in ids]
    def key(w):return tuple(w[k] for k in ('object','color','quantity','status'))
    assert not(set(map(key,train))&set(map(key,test)))
    write('train_worlds.jsonl',train);write('eval_worlds.jsonl',test)
    inputs={}
    for seed in SEEDS:
        ck=task(seed);assert sha(ck['checkpoint'])==ck['checkpoint_hash'];inputs[ck['checkpoint']]=ck['checkpoint_hash']
        p=CES/f'local/pca/bart_s{seed}.pt';inputs[str(p)]=sha(p)
        z=load(p);assert not(set(z['worlds'])&set(ids))
        pp=CES/f'local/scan_bart/bart_s{seed}/pairs.jsonl';inputs[str(pp)]=sha(pp)
        for r in rows(pp):
            if r['world_id'] in ids and r['donor_source']=='N→E' and r['operation']=='plus':inputs[r['state_path']]=sha(r['state_path'])
    for p in [ROOT/'train_worlds.jsonl',ROOT/'eval_worlds.jsonl',SOURCE/'data/time/worlds.jsonl',
              REPO/'models/bart-base/model.safetensors',REPO/'experiments/reference_frame_pilot_v3/data/train_worlds.jsonl',
              REPO/'experiments/algebraic_generalization_v1/G3_trajectories.jsonl',REPO/'experiments/projection_hypothesis_v1/pooled_representations.pt']:
        inputs[str(p)]=sha(p)
    for p in list(ROOT.glob('*.py'))+list(SOURCE.glob('*.py')):
        inputs[str(p)]=sha(p)
    dump('protocol.json',dict(version=2,neural_training=False,seeds=list(SEEDS),eval_world_ids=ids,train_world_ids=[w['world_id'] for w in train],
                             core_disjoint=True,old_pca_disjoint=True,alphas=[.25,.5,.75,1.],random_seeds=[91001,91002,91003,91004],
                             residual_sign='e=bad-good; repair bad-alpha*e_component; inject good+alpha*e_component',
                             attribution_basis='frozen old discovery PCA4; test worlds excluded',
                             new_basis='PCA4 fitted only on current-exact, canonical-next-correct, edited-next-failed training-world differences',
                             canonical_fit_templates=[0,1],canonical_fit_states=list(range(-3,4)),eval_templates=[0,2,3],
                             sequences=dict(primary=['plus','minus','plus','minus','plus'],reordered=['plus','plus','minus','minus','plus']),
                             regression_ridge=.001,mahal_ridge=.0001,projection_methods=['none','mean','ridge','random_ridge','reencode'],
                             decoder_worlds=40,decoder_layers=list(range(6)),decoder_conditions=['K','V','KV'],decoder_groups=['all','edited','entity_quantity','other'],
                             maximum_gpus=1,total_allocation_cap_seconds=5400,exposure='Historical analysis-held-out worlds, previously evaluated; no fresh independent-confirmation claim',
                             KL='KL(reference||perturbed), same teacher forcing labels, pad excluded',inputs=inputs))
    print('Locked 96 training and 80 analysis-held-out worlds; core and old-PCA world disjointness passed.')

if __name__=='__main__':main()
