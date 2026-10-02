import subprocess,json
from common import *

def command(args,cwd=ORIGINAL):
    return subprocess.check_output(args,cwd=cwd,text=True)

def main():
    manifests={}
    for name,key in [('t5gemma','t5gemma-2b-2b-ul2-it'),('failed_270m','t5gemma-2-270m-270m')]:
        p=f'experiments/reference_frame_cross_backbone_v1/models/{key}.json'
        m=json.loads(command(['git','show',f'origin/experiment/reference-frame-cross-backbone-v1:{p}']))
        for file,info in m['files'].items():assert digest(Path(m['directory'])/file)==info['sha256'],file
        m['local_files_verified']=True;m['license']='gemma';m['historical_admission']=json.loads(command(['git','show',f'origin/experiment/reference-frame-cross-backbone-v1:experiments/reference_frame_cross_backbone_v1/calibration/{key}/admission.json']))
        manifests[name]=m
    directory=ORIGINAL/'models/bart-base';files={}
    for p in directory.iterdir():
        if p.is_file():files[p.name]=dict(sha256=digest(p),bytes=p.stat().st_size)
    manifests['bart']=dict(model_id='facebook/bart-base',revision='aadd2ab0ae0c8268c7c9693540e9904811f36177',tokenizer_revision='aadd2ab0ae0c8268c7c9693540e9904811f36177',directory=str(directory),license='apache-2.0',files=files,local_files_verified=True)
    dump(ROOT/'model_manifest.json',manifests)
    report_paths=[]
    for d in ['g14_matched_state_handoff_v1','g15_self_state_transfer_v1','g16_capability_preserving_transfer_v1','g17_state_source_transfer_v1']:
        parent=ORIGINAL/'.g17-worktree'/'experiments'/d
        for name in ['REPORT.md','INTERPRETATION.md','checkpoints_manifest.json','runs_manifest.json','budget.json','delivery_audit.json']:
            p=parent/name
            if p.exists():report_paths.append(dict(path=str(p),sha256=digest(p)))
    dump(ROOT/'AUDIT.json',dict(base_commit=command(['git','rev-parse','HEAD'],WORKTREE).strip(),original_status=command(['git','status','--short','--branch']),branches=command(['git','for-each-ref','--sort=-committerdate','--format=%(refname:short) %(objectname) %(committerdate:iso8601)','refs/remotes/origin']),instructions_found=[],sinfo=command(['sinfo','-o','%P %a %l %D %G']),squeue=command(['squeue','-u','zailong','-o','%i %j %T %P %b %Z']),partition=command(['scontrol','show','partition','B300q']),historical_files=report_paths,limitations=['Historical reports read and hashed; no new inference replicating every G14–G17 result','No admitted 270M IT artifact found; pretrained270M is not IT','Existing old worktrees and untracked files preserved']))
    cfg=dict(rank=16,seeds=[42,43,44],engineering_steps=160,atomic_steps=600,repair_steps=200,source_seed_offset=10000,batch=8,microbatch=2,lr=.001,clip=1.,source_cap=dict(bart=192,t5gemma=256),max_new_tokens=160,gpu_hour_cap=48.,repair_train_world_cap=32,gate=dict(reconstruction=.95,atomic=.85,min_cell=.75),holdouts=dict(time=[2,-2],space=[1,3],emotion=[1,3],person=[1,2]),selection='minimum full-core-dev per-example token mean NLL every100 atomic updates; supplement final200',scientific_plan_sha=digest(ROOT/'EXPERIMENT_PLAN.md'),data_spec_sha=digest(ROOT/'DATA_SPEC.md'))
    if (ROOT/'config.json').exists():assert read(ROOT/'config.json')==cfg
    else:dump(ROOT/'config.json',cfg)
    tasks=[]
    for phase in ('engineering','formal','symbol'):
        cohort=[]
        for model in MODELS:
            for domain in DOMAINS:
                for seed in ([42,43,44] if phase=='formal' else [42]):cohort.append(dict(phase=phase,model=model,domain=domain,seed=seed))
        for i,t in enumerate(cohort):t['index']=i;tasks.append(t)
    dump(ROOT/'tasks.json',tasks)
    dump(ROOT/'SOURCE_LINEAGE.json',dict(base_model_manifest_sha=digest(ROOT/'model_manifest.json'),config_sha=digest(ROOT/'config.json'),historical_editor_weights_used=False,P='new domain-specific atomic editor from identity initialization; natural atomic training only',Q='same P optimization trajectory frozen at step300',U='independent atomic optimization seed+10000, same train/dev data, no supplement',N_S_M='identical selected P initialization, independent200updates per holdout split; exact lineage in each run/checkpoint_index.json',data_manifest_sha=digest(ROOT/'data/manifest.json')))
    dump(ROOT/'pre_engineering_lock.json',dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p)) for p in sorted(ROOT.glob('*.py'))]+[dict(path=p,sha256=digest(ROOT/p)) for p in ['config.json','tasks.json','EXPERIMENT_PLAN.md','DATA_SPEC.md','model_manifest.json','data/manifest.json']],stage='before any new neural outputs'))

if __name__=='__main__':main()
