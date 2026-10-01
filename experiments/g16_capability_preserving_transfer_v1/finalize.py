"""Post-run CPU delivery checks; never loads a GPU model or chooses a checkpoint.

This delivery-only helper is added after the pre-inference scientific lock. It
does not change its files, inference, data, schedule, selection or statistics.
"""
import argparse
import statistics
from datetime import datetime, timezone, timedelta
from common_g16 import *
from selection import check_selection_lock, qualify, decision

stats=load_module('g16_delivery_readonly_statistics',G15/'analyze.py')

def export_metadata():
    """Normalize the inherited final-only step sentinel, keeping its provenance.

    Scientific inference already records actual_updates and checkpoint_sha256.
    The G15 final interface also supplies step=200 for every model, including P.
    G16 has guard snapshots: in the delivered archive step must reflect their
    actual update count. This changes neither output text nor any score/cohort.
    """
    checks=[]
    for seed in CFG['seeds']:
        path=ROOT/f'per_example_s{seed}.jsonl.gz';rows=read(path)
        changed=0
        for r in rows:
            original=r.get('legacy_final_interface_step',r['step'])
            if r['step']!=r['actual_updates']:changed+=1
            r['legacy_final_interface_step']=original;r['step']=r['actual_updates']
        write(path,rows)
        checks.append(dict(seed=seed,records=len(rows),normalized_step_fields=changed,actual_updates_already_in_original_inference=True,only_export_metadata_changed=True))
    dump(ROOT/'export_metadata_audit.json',dict(checks=checks,text_scores_cohorts_checkpoint_hashes_unchanged=True,legacy_sentinel_retained=True,scientific_lock_unchanged=True))

def cohorts():
    rows=[];old=[]
    for seed in CFG['seeds']:
        for split in ['iid','template_ood']:
            meta=json.loads((ROOT/f'data/confirm_{split}_s{seed}.json').read_text())
            states=read(ROOT/meta['state_metadata']);gates=meta['gates'];n=sum(g['fixed_gate']['matched'] for g in gates)
            oldn=sum(g['old_gate']['matched'] for g in gates)
            old.append(dict(seed=seed,split=split,n=oldn,N=160,wilson_lo=stats.wilson(oldn,160)[0],wilson_hi=stats.wilson(oldn,160)[1],failures=json.dumps(dict(collections.Counter(f for g in gates for f in g['old_gate']['failures']))),cohort_independent_of_today_C=True,exploratory=oldn<40))
            for source in ['E','P','G','U']:
                sample=[r for r in states if r['source']==source]
                exact=sum(r['current']['exact'] for r in sample)
                joint=sum(r['current']['joint'] for r in sample)
                k=sum(r['current']['exact'] and r['current']['joint'] and r['current']['normal_end'] for r in sample)
                assert len(sample)==160
                lo,hi=stats.wilson(k,160)
                rows.append(dict(seed=seed,split=split,source=source,current_correct_k=k,current_exact_k=exact,current_joint_k=joint,N=160,current_wilson_lo=lo,current_wilson_hi=hi,C=n,C_wilson_lo=stats.wilson(n,160)[0],C_wilson_hi=stats.wilson(n,160)[1],gate_failures=json.dumps(dict(collections.Counter(f for g in gates for f in g['fixed_gate']['failures']))),current_error_types=json.dumps(dict(collections.Counter(r['current']['error_type'] for r in sample))),natural_mask_equal_k=sum(g['natural_mask_equal'] for g in gates),producer_masks_equal=all(g['producer_masks_equal'] for g in gates),exploratory=n<40))
    csvwrite(ROOT/'cohort_results.csv',rows)
    csvwrite(ROOT/'maintenance_cohort_results.csv',old)

def summaries():
    core=list(csv.DictReader((ROOT/'core_results.csv').open()))
    extra={
        'atomic_min_cell':lambda r:float(r['atomic_min_cell']),
        'self_first':lambda r:int(r['first_k'])/160,
        'self_endpoint2':lambda r:int(r['endpoint2_k'])/160,
        'natural_today':lambda r:int(r['natural_today_k'])/int(r['n']) if int(r['n']) else None,
        'all_fixed4':lambda r:int(r['all_fixed4_k'])/int(r['n']) if int(r['n']) else None,
        'today_C_coverage':lambda r:int(r['n'])/160,
        'old_C_coverage':lambda r:int(r['old_n'])/160,
    }
    path=ROOT/'seed_mean_SD.csv';rows=[r for r in csv.DictReader(path.open()) if r['metric'] not in extra]
    for method,split in sorted({(r['method'],r['split']) for r in core}):
        rs=[r for r in core if (r['method'],r['split'])==(method,split)]
        for metric,f in extra.items():
            vals={r['seed']:f(r) for r in rs};vs=[v for v in vals.values() if v is not None]
            rows.append(dict(method=method,split=split,metric=metric,contributing_seeds=len(vs),original_seed_denominator=3,mean=statistics.mean(vs) if vs else None,sample_SD=statistics.stdev(vs) if len(vs)>1 else None,per_seed=json.dumps(vals)))
    csvwrite(path,rows)

def audit():
    original=verify_lock();selection_lock=check_selection_lock()
    assert json.loads((ROOT/'cpu_tests.json').read_text())['passed']
    assert json.loads((ROOT/'smoke_test.json').read_text())['passed']
    assert json.loads((ROOT/'g15_audit.json').read_text())['passed']
    assert not json.loads((ROOT/'g15_audit.json').read_text())['definite_invalidating_engineering_error']
    for relative,sha in json.loads((ROOT/'g15_audit.json').read_text())['source_sha256'].items():
        assert digest(REPO/relative)==sha,('G15 read-only dependency changed',relative)
    budget=json.loads((ROOT/'budget.json').read_text());assert budget['within_limits']
    jobs=list(csv.DictReader((ROOT/'slurm_jobs.csv').open()))
    assert len(jobs)==7 and all(r['state']=='COMPLETED' and r['exit_code']=='0:0' and int(r['gpus'])==1 for r in jobs)
    request=json.loads((ROOT/'submissions.json').read_text())
    assert [r['phase'] for r in request]==['smoke','train','confirm']
    assert sum(r['requested_gpu_seconds'] for r in request)/3600==budget['requested_gpu_hours']
    def span(phase):
        job=next(r['job_id'] for r in request if r['phase']==phase)
        return [r for r in jobs if r['job_id']==job or r['job_id'].startswith(job+'_')]
    assert max(r['end'] for r in span('smoke'))<=min(r['start'] for r in span('train'))
    assert max(r['end'] for r in span('train'))<=min(r['start'] for r in span('confirm'))
    # Execution-local mtime evidence is saved once; future clones must use this
    # saved timeline, not reinterpret checkout mtimes as historical run times.
    timeline=ROOT/'execution_timeline.json'
    if not timeline.exists():
        zone=timezone(timedelta(hours=8))
        mtime=lambda p:datetime.fromtimestamp(p.stat().st_mtime,zone).isoformat()
        selected_times={str(s):mtime(ROOT/f'selection_s{s}.json') for s in CFG['seeds']}
        locked_time=mtime(ROOT/'selection_lock.json')
        assert datetime.fromisoformat(locked_time).replace(tzinfo=None)>=datetime.fromisoformat(max(r['end'] for r in span('train')))
        assert datetime.fromisoformat(locked_time).replace(tzinfo=None)<=datetime.fromisoformat(min(r['start'] for r in span('confirm')))
        dump(timeline,dict(timezone='Asia/Singapore UTC+08:00',selection_record_creation_times=selected_times,global_selection_lock_time=locked_time,all_training_allocation_end=max(r['end'] for r in span('train')),first_confirmation_allocation_start=min(r['start'] for r in span('confirm')),observed_execution_local_mtimes=True,not_reconstructed_from_clone=True,selection_lock_sha256=digest(ROOT/'selection_lock.json')))
    proofs=[];weights=[];local=[]
    for seed in CFG['seeds']:
        tr=json.loads((ROOT/f'seed_s{seed}_train_complete.json').read_text())
        co=json.loads((ROOT/f'seed_s{seed}_confirm_complete.json').read_text())
        for proof in [tr,co]:
            assert proof['passed'] and proof['frozen_before']==proof['frozen_after'] and proof['caches_unchanged']
        assert tr['U_never_loaded'] and co['U_loaded_after_global_lock']
        assert co['selection_lock_sha256']==digest(ROOT/'selection_lock.json')
        proofs.append(dict(seed=seed,train_gpu=tr['gpu'],confirm_gpu=co['gpu'],train_peak_bytes=tr['peak_cuda_bytes'],confirm_peak_bytes=co['peak_cuda_bytes'],same_SHA_reused=co['same_SHA_reused']))
        candidates=json.loads((ROOT/f'training/F_s{seed}_candidates.json').read_text())
        selected=json.loads((ROOT/f'selection_s{seed}.json').read_text());best=decision(candidates)
        assert selected['selected_step']==(best['step'] if best else None)
        assert not selected['U_used'] and not selected['confirm_used']
        metas={m:json.loads((ROOT/f'training/{m}_s{seed}.json').read_text()) for m in ['N','F']}
        assert metas['N']['initial_hash']==metas['F']['initial_hash']
        logs={m:read(ROOT/f'training/{m}_s{seed}_steps.jsonl.gz') for m in metas}
        assert [r['tokens'] for r in logs['N']]==[r['tokens'] for r in logs['F']]
        for m,z in metas.items():
            assert z['updates']==200 and z['counts']['instances']==6400 and z['fresh_optimizer']
            assert len(logs[m])==200 and [r['step'] for r in logs[m]]==list(range(1,201))
            assert z['counts']['block_instances']=={k:1600 for k in 'ABCD'}
            assert z['counts']['tokens']=={k:sum(r['tokens'][k] for r in logs[m]) for k in 'ABCD'}
            assert z['no_U_or_G_today_receiver_in_train_dev'] and z['RNG_preserved_around_all_diagnostics']
            path=ROOT/z['final_path'];assert digest(path)==z['final_sha256']
            weights.append(dict(seed=seed,version=m+'-final',actual_updates=200,path=str(path),repo_path=str(path.relative_to(REPO)),sha256=digest(path),bytes=path.stat().st_size,uploaded=True))
        if best:
            path=ROOT/selected['checkpoint_path'];assert digest(path)==selected['checkpoint_sha256']
            weights.append(dict(seed=seed,version='F-guard',actual_updates=selected['selected_step'],path=str(path),repo_path=str(path.relative_to(REPO)),sha256=digest(path),bytes=path.stat().st_size,uploaded=True,same_as_final=digest(path)==metas['F']['final_sha256']))
        for sp in ['repair_train','repair_dev','confirm_iid','confirm_template_ood']:
            meta=json.loads((ROOT/f'data/{sp}_s{seed}.json').read_text());path=Path(meta['cache_path'])
            assert path.exists() and digest(path)==meta['cache_sha256']
            local.append(dict(kind='full_FP32_latent_cache',path=str(path),sha256=digest(path),bytes=path.stat().st_size,uploaded=False))
    mapping=json.loads((ROOT/'checkpoints_manifest.json').read_text())
    references=[dict(seed=seed,role=role,**z,uploaded=False,reason='existing checkpoint, read-only reference') for seed,m in mapping['models'].items() for role,z in m.items()]
    for path in sorted((ROOT/'local').glob('*.pt')):
        if not any(r['path']==str(path) for r in local):
            local.append(dict(kind='candidate_optimizer_or_smoke_local_only',path=str(path),sha256=digest(path),bytes=path.stat().st_size,uploaded=False))
    archives=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in sorted(ROOT.glob('*jsonl.gz'))]
    dump(ROOT/'artifact_manifest.json',dict(editor_checkpoints=weights,existing_model_references=references,local_only_artifacts=local,complete_text_archives=archives,base_model_manifest='checkpoints_manifest.json',no_base_model_or_large_latent_uploaded=True))
    csvwrite(ROOT/'gpu_engineering_results.csv',proofs)
    expected_rows=sum(len(json.loads((ROOT/f'seed_s{s}_confirm_complete.json').read_text())['versions'])*2*8480 for s in CFG['seeds'])
    result=json.loads((ROOT/'result_audit.json').read_text());assert result['complete_seeds']==CFG['seeds'] and result['confirmation_rows']==expected_rows and result['learning_rows']==335040
    dump(ROOT/'delivery_audit.json',dict(passed=True,scientific_lock_sha256=digest(ROOT/'data/lock.json'),scientific_lock_unchanged=True,all6_training_runs200=True,all3_earliest_selections_rechecked=True,all_confirmation_and_learning_scores_recomputed=True,shared_schedule_tokens_equal=True,instances_per_group=6400,frozen_hashes_equal=True,all_large_caches_hash_verified=True,U_only_after_all_seed_lock=True,stages_nonoverlapping=True,all7_single_GPU_allocations_completed=True,actual_gpu_hours=budget['actual_gpu_hours'],requested_gpu_hours=budget['requested_gpu_hours'],peak_concurrent_gpus=budget['max_concurrent_gpus'],post_lock_delivery_helper_only=True))
    print('G16 final CPU delivery audit passed',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohorts-only',action='store_true');args=parser.parse_args()
    cohorts()
    if not args.cohorts_only:summaries();export_metadata();audit()
