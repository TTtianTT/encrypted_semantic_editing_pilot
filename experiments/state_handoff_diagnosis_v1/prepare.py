"""CPU audit and immutable manifest construction. No CUDA imports at module level."""
import argparse
import itertools
import platform
import random
import sys
from datetime import date,timedelta
from .common import *

def initialize():
    if (ROOT/'world_manifest.jsonl').exists(): return
    sys.path.insert(0,str(SOURCE))
    from semantics import render,states,NAMES,OBJECTS,COLORS
    import torch,transformers
    sources=[SOURCE/'data/time/worlds.jsonl',CURRENT/'data/worlds.jsonl',CAUSAL/'configs/worlds.jsonl']
    for n,exp in [(13,'g13_source_overfit_audit_v1'),(14,'g14_matched_state_handoff_v1'),(15,'g15_self_state_transfer_v1'),(16,'g16_capability_preserving_transfer_v1'),(17,'g17_state_source_transfer_v1')]:
        sources += sorted((ORIGINAL/f'.g{n}-worktree/experiments'/exp/'data').glob('*worlds.jsonl'))
    excluded=set();inventory=[];schema_missing=0
    for p in sources:
        data=rows(p); comparable=[]
        for w in data:
            if w.get('domain')=='time' and all(k in w for k in ['object','quantity','status','color','people','event_date']):
                comparable.append(w);excluded.add(render(w,0,0))
            else: schema_missing+=1
        inventory.append(dict(path=str(p),sha256=sha(p),rows=len(data),comparable_time_worlds=len(comparable)))
    # Exact original generator draw order; parameterized seed/count and exclusion.
    rng=random.Random(2026100501);selected=[];seen=set(excluded)
    attempts=0
    while len(selected)<104 and attempts<100000:
        attempts+=1;people=rng.sample(NAMES,3);obj,other=rng.sample(OBJECTS,2);col=rng.choice(COLORS);quantity=rng.randrange(1,10);status=rng.choice(['planned','completed','cancelled'])
        key=(obj,col,quantity,status)
        # In original generator duplicate-key check occurs before auxiliary draws.
        surface=f'The {obj} event is dated today. Its status is {status}. The {obj} is {col}. '+('There is 1 copy.' if quantity==1 else f'There are {quantity} copies.')
        if surface in seen: continue
        event=(date(2026,11,1)+timedelta(days=rng.randrange(60))).isoformat()
        dx,dy=rng.choice([(0,1),(1,0),(0,-1),(-1,0)]);distance=rng.choice([1,2,3]);ox,oy=rng.randrange(-3,4),rng.randrange(-3,4)
        w=dict(domain='time',people=people,object=obj,other_object=other,color=col,quantity=quantity,event_date=event,quote_date=(date.fromisoformat(event)-timedelta(days=2)).isoformat(),status=status,object_xy=[ox+dx*distance,oy+dy*distance],observer_xy=[ox,oy],fixed_heading=rng.randrange(4),focus=rng.choice(people[:2]),other_level=rng.randrange(5),original_split='new',template=0)
        assert render(w,0,0)==surface
        seen.add(surface);w['core_hash']=objsha(surface);w['world_id']='handoff_time_'+w['core_hash'][:16];w['order_hash']=objsha('handoff-v1-split:'+surface);selected.append(w)
    selected.sort(key=lambda w:w['order_hash'])
    for i,w in enumerate(selected): w['split']='development' if i<24 else 'confirmation'
    assert len(selected)==104 and not ({render(w,0,0) for w in selected}&excluded)
    jsonl(ROOT/'world_manifest.jsonl',selected)
    old=rows(SOURCE/'data/time/worlds.jsonl'); smoke=[w for w in old if w['split']=='test'][:8]
    jsonl(ROOT/'configs/smoke_worlds.jsonl',smoke)
    dump(ROOT/'configs/data_exclusion.json',dict(sources=inventory,excluded_unique_core_content=len(excluded),noncomparable_schema_rows=schema_missing,generation_attempts=attempts,new_worlds=len(selected),development=24,confirmation=80,core_overlap=0,generator_source_sha=sha(SOURCE/'prepare.py')))
    models=read(SOURCE/'model_manifest.json');checkpoints=[];backbone=[]
    for model in ('bart','t5gemma'):
        for name,meta in models[model]['files'].items():
            p=Path(models[model]['directory'])/name; assert sha(p)==meta['sha256'],p
            backbone.append(dict(model=model,path=str(p),bytes=p.stat().st_size,sha256=meta['sha256']))
    ci=read(CURRENT/'CHECKPOINT_INDEX.json')
    for seed in (42,43,44):
        pmeta=read(SOURCE/f'runs/formal/bart_time_s{seed}/checkpoint_index.json')['P'];p=Path(pmeta['path']);assert sha(p)==pmeta['sha256']
        ck=torch.load(p,map_location='cpu',weights_only=False)
        checkpoints.append(dict(model='bart',seed=seed,condition='P',path=str(p),sha256=sha(p),step=ck.get('step'),rank=16,dtype='float32',metadata=pmeta,source_commit='0b73738cf552e1ec29aa7a5db1eb1ee703804b66'))
        for condition in ('F','R'):
            item=next(x for x in ci if x['seed']==seed and x['condition']==condition and x['update']==200)
            p=CURRENT/item['path'];raw=Path(item['raw_checkpoint']);assert sha(p)==item['sha256'] and sha(raw)==item['raw_sha256']
            export=torch.load(p,map_location='cpu',weights_only=True);original=torch.load(raw,map_location='cpu',weights_only=True)
            assert original['update']==200 and all(torch.equal(v,original['editor'][k]) for k,v in export['editor'].items())
            checkpoints.append(dict(model='t5gemma',seed=seed,condition=condition,path=str(p),sha256=sha(p),update=200,raw_path=str(raw),raw_sha256=sha(raw),export_exact_tensor_match=True,rank=16,dtype='float32',source_commit=CURRENT_SHA))
    sourcefiles=[SOURCE/f for f in ['backend.py','semantics.py','evaluator.py','common.py','config.json','model_manifest.json']]
    dump(ROOT/'CHECKPOINTS.json',dict(models={m:{k:v for k,v in models[m].items() if k!='historical_admission'} for m in ('bart','t5gemma')},editors=checkpoints,verified_backbone_files=backbone,source_files={str(p):sha(p) for p in sourcefiles}))
    dump(ROOT/'ENVIRONMENT.json',dict(python=sys.version,python_executable=str(PYTHON),torch=torch.__version__,transformers=transformers.__version__,cuda_build=torch.version.cuda,platform=platform.platform(),dependencies=cmd([PYTHON,'-m','pip','freeze']).splitlines(),GPU_runtime='only inspected in Slurm',slurm=dict(partition='B300q',gres='gpu:1',account=None,qos='normal',cpus=4,source_script=str(CAUSAL/'slurm/worker.sbatch'))))
    reads=[CAUSAL/f for f in ['CAUSAL_NEXT_EDIT_STABILITY_V1_REPORT.md','preregistered_protocol.yaml','ARTIFACT_AUDIT.md','pairs.py','adapter.py','rollout_eval.py','resource_guard.py']]+[CURRENT/f for f in ['RESEARCH_ANSWERS.md','RESULTS.md','EXPERIMENT_PLAN.md','CHECKPOINT_INDEX.json','SOURCE_LINEAGE.json','SOURCE_LINEAGE_RESOLVED.json','evaluation.py','engine.py']]
    for n,exp in [(13,'g13_source_overfit_audit_v1'),(14,'g14_matched_state_handoff_v1'),(15,'g15_self_state_transfer_v1'),(16,'g16_capability_preserving_transfer_v1'),(17,'g17_state_source_transfer_v1')]:
        d=ORIGINAL/f'.g{n}-worktree/experiments'/exp
        reads += [p for name in ['RESULTS.md','README.md','SOURCE_LINEAGE.json'] if (p:=d/name).exists()]
    for p in reads:p.read_text()
    dump(ROOT/'SOURCE_LINEAGE.json',dict(base_commit=BASE_SHA,current_source_commit=CURRENT_SHA,fetched_refs=cmd(['git','for-each-ref','--format=%(refname:short) %(objectname)','refs/remotes/origin'],WT).splitlines(),original_worktree_status=cmd(['git','status','--short'],ORIGINAL),read_files=[dict(path=str(p),sha256=sha(p)) for p in reads],reuse_policy='Exact model/checkpoint/world/initial state/history/mask/wrapper/generation match only. Old32/80 worlds exposed, no independent claim.',new_questions=['exact old P state1 second-operation failure partition','F200-to-R200 and R200-to-F200 same-memory handoff','fixed history-depth diagnostics']))
    text(ROOT/'AUDIT.md', '# Audit and deduplication\n\nFetched reference branches are unchanged at their specified SHAs; no existing state-handoff branch. Base is causal2f4713f; current-source aea8310 is read-only, no branch merge. Original worktrees and untracked files retained.\n\nOld BART P donor/Good second-step failures and T5Gemma F/F, R/R self two-step, natural ability, actual/gold reencoding are known. These are controls or exposed smoke comparisons, not new findings. Cross F→R/R→F with fixed update200 and exact old P natural atomic cells on new content are new. New confirmation worlds are IID template0, no template OOD claim. Core-content exclusion and all data-source hashes are configs/data_exclusion.json. G13–G17 use differing objectives/source/checkpoints; no near-equivalent result is substituted.\n\nBackbones and parser/wrapper are original four-domain implementations; all source hashes are CHECKPOINTS.json. Editors are affine rank16 residuals, FP32 computation and original output cast (BART FP32 / T5 BF16). Export F/R tensors exactly match update200 raw checkpoints, no best-dev selection. Natural reconstruction, bridge reconstruction and joint target/preservation/grammar/EOS are separate. Reencoding changes representation and mask/layout, not a localized patch.\n\nNo new training, SAE, PCA, layer scan or model conversion. 16 allocated GPU-hours, one active1GPU array%2, account queue checked conservatively. Every terminal run publishes separately from immutable execution snapshots.\n')
    dump(ROOT/'results/job_ledger.json',dict(cap_gpu_hours=16,submissions=[],gpu_hours=0,maximum_concurrent_gpus=0))
    dump(ROOT/'task_registry.json',dict(semantic_version=SEMANTIC_VERSION,runs=[]))
    text(ROOT/'STATUS.md','# Status\n\nR00 CPU audit prepared. No neural outputs on confirmation data. GPU-hours0.\n')
    text(ROOT/'README.md','# State handoff diagnosis v1\n\nFrozen BART P second-step attribution and original T5Gemma F200/R200 cross handoff. No training. Read protocol.yaml, AUDIT.md and STATUS.md.\n\nCPU CLI: `python -m experiments.state_handoff_diagnosis_v1.prepare --round R00`, then submit/collect/publish with the same `--round`. Submit only via this interface; run only in sbatch+srun. Immutable execution snapshot and actual manifest are recorded for every run. Outputs under ignored local/runs; small compressed observations and reports published per terminal run.\n')
    text(ROOT/'CHANGELOG.md','# Changes\n\nInitial implementation: data/checkpoint audit, fixed protocol, immutable execution snapshots and per-run publication.\n')

def prepare_round(round_):
    initialize()
    registry=read(ROOT/'task_registry.json')
    if any(r['round']==round_ for r in registry['runs']):
        print('Already prepared:',round_);return
    models=('bart','t5gemma') if round_ in ('R00','R03') else ('bart',) if round_=='R01' else ('t5gemma',)
    data=ROOT/('configs/smoke_worlds.jsonl' if round_=='R00' else 'world_manifest.jsonl')
    cp=read(ROOT/'CHECKPOINTS.json')
    for model in models:
        for seed in (42,43,44):
            run_id=f'{round_}_{model}_s{seed}_'+('smoke' if round_=='R00' else 'confirm')
            t=dict(run_id=run_id,round=round_,model=model,seed=seed,split='exposed_smoke' if round_=='R00' else 'confirmation',scope='IID_time_template0',world_file=str(data),world_hash=sha(data),protocol_hash=sha(ROOT/'protocol.yaml'),semantic_version=SEMANTIC_VERSION,checkpoint_records=[c for c in cp['editors'] if c['model']==model and c['seed']==seed],source_files=cp['source_files'],output=str(LOCAL/'runs'/run_id),batch_size=8)
            t['scientific_hash']=objsha(t)
            dump(ROOT/f'manifests/{run_id}.json',t)
            registry['runs'].append(dict(run_id=run_id,round=round_,model=model,seed=seed,state='LOCKED',manifest=f'manifests/{run_id}.json',scientific_hash=t['scientific_hash']))
    dump(ROOT/'task_registry.json',registry)
    print('Prepared',round_,[r['run_id'] for r in registry['runs'] if r['round']==round_])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',required=True,choices=['R00','R01','R02','R03']);a=p.parse_args();prepare_round(a.round)
