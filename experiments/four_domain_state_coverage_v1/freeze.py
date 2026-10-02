"""Lock the complete protocol after dev engineering, before formal/test outputs."""
from common import *

def main():
    path=ROOT/'formal_lock.json'
    if path.exists():raise RuntimeError('Formal lock immutable')
    assert read(ROOT/'independent_parser_checks.json')['passed']
    measured=[];interface=[]
    for model in MODELS:
        for d in DOMAINS:
            p=ROOT/f'runs/engineering/{model}_{d}_s42/complete.json'
            assert p.exists(),p
            measured.append(read(p))
    for d in DOMAINS:
        p=ROOT/f'runs/interface/t5gemma_{d}_s42/complete.json';assert p.exists(),p;interface.append(read(p))
    cfg=read(ROOT/'config.json');cfg['copy_instruction']='Copy the following text exactly. Output only the copied text.\n\n'
    cfg['pre_formal_amendment_sha']=digest(ROOT/'AMENDMENTS.md');cfg['data_manifest_sha']=digest(ROOT/'data/manifest.json');dump(ROOT/'config.json',cfg)
    # Conservatively scale trial's complete training+three dev interfaces24x
    # per formal seed, plus symbolic4x, with20% extra reserve.
    trial_seconds=sum(v['resources']['wall_seconds'] for v in measured)
    estimate=(trial_seconds*24*3+trial_seconds*4)/3600
    dump(ROOT/'resource_plan.json',dict(trial_total_gpu_seconds=trial_seconds,formal_plus_symbol_estimated_gpu_hours=estimate,with_20_percent_reserve=estimate*1.2,gpu_hour_consumption_cap=48,estimate_is_conservative_scaling_not_guarantee=True,resources=dict(partition='B300q',gpus_per_task=1,array_limit=2,cpus=4,ram='64G',walltime='02:00:00'),interface_rates={x['task']['domain']:x['reconstruction']['rate'] for x in interface}))
    assert estimate*1.2<48,'Measured plan exceeds cap; do not submit; report estimate'
    lineage=read(ROOT/'SOURCE_LINEAGE.json');lineage.update(config_sha=digest(ROOT/'config.json'),data_manifest_sha=digest(ROOT/'data/manifest.json'));dump(ROOT/'SOURCE_LINEAGE.json',lineage)
    ps=sorted(ROOT.glob('*.py'))+[ROOT/p for p in ['config.json','tasks.json','EXPERIMENT_PLAN.md','DATA_SPEC.md','AMENDMENTS.md','model_manifest.json','SOURCE_LINEAGE.json','data/manifest.json','job.slurm']]
    dump(path,dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p)) for p in ps],stage='all formal science locked before any formal training/test generation',copy_wrapper='previously admitted Copy-exact B; one common wrapper across all four T5 domains',interface={x['task']['domain']:x['reconstruction']['rate'] for x in interface},engineering_only=True))
    print('Formal protocol locked; estimatedGPUh=',estimate)

if __name__=='__main__':main()
