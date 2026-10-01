"""Post-lock CPU delivery checks; does not change scientific data or estimates."""
from common_g15 import *

def main():
    verify_lock()
    result=json.loads((ROOT/'result_audit.json').read_text())
    assert result['complete_seeds']==[42,43,44] and not result['missing_seeds']
    assert result['confirmation_rows']==203520 and result['all_scores_recomputed']
    budget=json.loads((ROOT/'budget.json').read_text());assert budget['within_limits']
    assert json.loads((ROOT/'cpu_tests.json').read_text())['passed']
    assert json.loads((ROOT/'aggregation_test.json').read_text())['passed']
    assert json.loads((ROOT/'smoke_test.json').read_text())['passed']
    final=[];caches=[]
    for seed in CFG['seeds']:
        proof=json.loads((ROOT/f'seed_s{seed}_complete.json').read_text())
        assert proof['passed'] and proof['frozen_before']==proof['frozen_after']
        assert proof['U_frozen_before']==proof['U_frozen_after'] and proof['U_loaded_only_after_three_trainings']
        for method in CFG['methods']:
            z=json.loads((ROOT/f'training/{method}_s{seed}.json').read_text());p=ROOT/z['final_path']
            assert z['updates']==200 and z['counts']['instances']==6400
            assert digest(p)==z['final_sha256'] and p.stat().st_size<1024*1024
            final.append(dict(seed=seed,method=method,path=str(p),repo_path=str(p.relative_to(REPO)),sha256=digest(p),bytes=p.stat().st_size,updates=200,instances=6400))
        for tag in ['repair_train','repair_dev','confirm_iid','confirm_template_ood']:
            z=json.loads((ROOT/f'data/{tag}_s{seed}.json').read_text());p=Path(z['cache_path'])
            assert p.exists() and digest(p)==z['cache_sha256']
            caches.append(dict(seed=seed,tag=tag,path=str(p),sha256=z['cache_sha256'],bytes=p.stat().st_size,uploaded=False,full_FP32_states=True))
    retry=json.loads((ROOT/'resume_evaluation_audit.json').read_text())
    after={p:digest(ROOT/p) for p in retry['protected_before_sha256']}
    assert after==retry['protected_before_sha256'],'Engineering resume changed a protected artifact'
    for path in retry['missing_shards']:assert len(read(ROOT/path))==8480
    retry.update(protected_after_sha256=after,all_prior_artifacts_unchanged=True,missing_shard_added=True,seed_completed=True,no_training_repeated=True)
    dump(ROOT/'resume_evaluation_audit.json',retry)
    jobs=list(csv.DictReader((ROOT/'slurm_jobs.csv').open()))
    assert len(jobs)==5 and len({r['raw_job_id'] for r in jobs})==5
    assert len([r for r in jobs if r['state']=='FAILED'])==1
    assert all(r['state'] in ['COMPLETED','FAILED'] and int(r['gpus'])==1 for r in jobs)
    gpu=[]
    for r in jobs:
        s=42 if r['job_id']=='2507_0' else 43 if r['job_id'] in ['2507_1','2510'] else 44 if r['job_id']=='2507_2' else None
        proof=json.loads((ROOT/f'seed_s{s}_complete.json').read_text()) if s else json.loads((ROOT/'smoke_test.json').read_text())
        peak=max(json.loads((ROOT/f'training/{m}_s{s}.json').read_text())['peak_cuda_bytes'] for m in CFG['methods']) if s and r['state']=='FAILED' else proof['peak_cuda_bytes']
        gpu.append(dict(**r,seed=s,gpu_model=proof['gpu'],gpu_model_measurement='successful seed43 resume CUDA name on same node02; failed allocation model inferred from same B300 node' if r['state']=='FAILED' else 'completed allocation CUDA device name',peak_cuda_bytes=peak,peak_measurement='training peak before failed evaluation; whole failed allocation peak unavailable' if r['state']=='FAILED' else 'completed run cuda allocator peak'))
    csvwrite(ROOT/'gpu_resources.csv',gpu)
    dump(ROOT/'final_checkpoints.json',final)
    dump(ROOT/'local_cache_inventory.json',caches)
    dump(ROOT/'delivery_audit.json',dict(passed=True,complete_models=9,completed_steps=1800,total_supervised_instances=57600,primary_final_step=200,all_locked_science_hashes_unchanged=True,frozen_ED_P_G_U_verified=True,confirmation_rows=203520,learning_rows=72000,training_current_rows=14400,all_prior_retry_artifacts_unchanged=True,allocation_count=5,budget=budget,post_lock_operational_files=['tests_aggregation.py','resume_evaluation.py','scripts/resume_evaluation.sbatch','annotate_report.py','finalize.py'],post_result_interpretation='INTERPRETATION.md',old_experiments_modified=False))
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or any(s in ['local','outputs','learning','__pycache__'] for s in p.relative_to(ROOT).parts) or p.name in ['artifact_manifest.json'] or p.name.endswith('.tmp'):continue
        assert not p.is_symlink() and p.stat().st_size<100*1024*1024,str(p)
        files.append(dict(repo_path=str(p.relative_to(REPO)),sha256=digest(p),bytes=p.stat().st_size))
    dump(ROOT/'artifact_manifest.json',dict(files=files,total_bytes=sum(r['bytes'] for r in files),includes_only_G15=True,large_latent_caches_uploaded=False,old_or_base_weights_uploaded=False,self_manifest_excluded=True))
    print('G15 final delivery verified',len(files),'files',sum(r['bytes'] for r in files),'bytes',flush=True)

if __name__=='__main__':main()
