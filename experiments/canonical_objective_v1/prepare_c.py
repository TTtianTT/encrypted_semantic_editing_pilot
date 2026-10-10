"""Lock design, source code and frozen inputs before new inference/training."""
from cutil import *

def main():
    assert not (ROOT/'protocol.json').exists(),'Do not overwrite an executed protocol'
    items=transition_items('train');scale={}
    for op,rs in items.items():
        vals=[]
        for i,s,_ in rs:
            y=old.semantics()[2]('time',s,op);a,b=canonical('train',0,s),canonical('train',0,y)
            n=max(a['h'].shape[1],b['h'].shape[1]);h,m=old.pad(a['h'][i:i+1],a['m'][i:i+1],n);g,gm=old.pad(b['h'][i:i+1],b['m'][i:i+1],n)
            vals.append(float(((h-g).square()*m[...,None]).sum()/(m.sum()*768)))
        scale[op]=float(np.mean(vals))
    paths={
      'original_alternating':dict(initial_state=0,operations=['plus','minus','plus','minus','plus']),
      'original_reordered':dict(initial_state=0,operations=['plus','plus','minus','minus','plus']),
      'aligned_from_plus_one':dict(initial_state=1,operations=['plus','plus','minus','minus','plus']),
      'aligned_from_minus_one':dict(initial_state=-1,operations=['minus','minus','plus','plus','minus'])}
    inputs=[V2/'train_worlds.jsonl',V2/'eval_worlds.jsonl',V2/'core.py',PRIOR/'shared.py',PRIOR/'protocol.json',PRIOR/'alignment_followup_protocol.json',PRIOR/'local/rrr.pt']
    inputs+=list((PRIOR/'local').glob('*_t*_s*.pt'))
    inputs += [V2/f'local/fit_s{s}.pt' for s in SEEDS]
    inputs += [Path(old.previous.task(s)['checkpoint']) for s in SEEDS]
    source=old.previous.SOURCE
    inputs += [source/n for n in ('backend.py','train.py','semantics.py','evaluator.py','common.py','config.json','model_manifest.json')]
    # The old protocol already fingerprints the complete frozen backbone; inherit it explicitly.
    prior=read(PRIOR/'protocol.json')
    backbone={k:v for k,v in prior['inputs'].items() if '/models/bart-base/' in k}
    sources={p.name:sha(p) for p in ROOT.glob('*.py')};sources['job.slurm']=sha(ROOT/'job.slurm')
    p=dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),rank=16,seeds=list(SEEDS),templates_train=[0],templates_eval=[0,3],
      worlds_train=[w['world_id'] for w in worlds('train')],worlds_eval=[w['world_id'] for w in worlds('eval')],
      exposure='Exploratory historical 80 worlds. Aligned paths were chosen post hoc in the previous round and are prospectively fixed here. No independent confirmation.',
      paths=paths,closure=dict(steps=50,horizons=[10,20,50],paths=['original_alternating','aligned_from_plus_one','aligned_from_minus_one'],cycles='Repeat first two ops of alternating, first four ops of aligned paths; each returns to the initial state'),
      dose=dict(lambdas=[0,.1,.25,.5,.75,.9,1],paths=list(paths),effective_rank_up_to=32),
      training=dict(updates=600,batch=8,microbatch=2,lr=.001,optimizer='AdamW',weight_decay=0,clip=1,
        l2_scale=scale,l2_weight=1,kl_weight=1,checkpoints=[0,10,25,50,100,200,300,400,600],
        evaluation_C4_checkpoints=[0,10,25,50,100,200,400,600],no_eval_selection=True,
        C1='aligned mask-identical transitions, CE, random',C2='aligned, token L2 / train mean ideal-write energy, random',
        C3='aligned, CE + normalized L2 (weight 1), random',C4='aligned, CE, balanced exact RRR-16 initialization',
        C5='all legal transitions, CE + canonical-next teacher-to-student KL (weight 1), random; canonical teacher branch fully detached; one-step foresight only',
        all_data_refit='All 96 train worlds, matching final RRR refit. No new hyperparameter or checkpoint selection on these historical evaluation worlds.'),
      mechanism=dict(S='Frozen train-world PCA4 from operator_residual_v2; own final residual PCA4 fitted on train worlds only',
        injection='For each seed use its historical CE residual projected onto frozen S, source 0 -> target -1. Add same delta to each new current edited state, then apply minus. Report current preservation and conditional next success; alpha=1.',
        eigengap='lambda4-lambda5, relative gap, absolute residual energy and centered top4 fraction; angles unstable when low energy or small gap'),
      inference=dict(batch=16,greedy=True,max_new_tokens=160),inputs={**{str(x.resolve()):sha(x) for x in inputs},**backbone},sources=sources,
      confirmation='Not run: final locked selected method requires five seeds and new worlds.',
      limits=['Finite 50-step evidence is not arbitrary-length proof.','Dose curve is a change in editor maps, not an isolated residual intervention.','Template3 is structural OOD; length-changing original reordered paths are not supported by aligned-only C1-C4 training.'])
    dump('protocol.json',p);print('locked',sha(ROOT/'protocol.json'),'L2 scales',scale,'backbone files',len(backbone))

if __name__=='__main__':main()
