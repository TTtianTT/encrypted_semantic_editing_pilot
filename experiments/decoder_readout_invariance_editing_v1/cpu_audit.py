"""Final CPU-only source, artifact, queue and headline audit."""
from datetime import datetime,timezone
import csv
import gzip
import io
import unittest
from .common import *
from .resources import accounting


def run():
    ledger=accounting([r['job_id'] for r in read(CONTROL/'jobs.json')])
    assert ledger['all_terminal'] and ledger['peak_concurrent_GPUs']<=2
    dump(ROOT/'results/resource_ledger.json',ledger)
    queue=command('squeue','-u',command('id','-un'),'-h','-o','%i|%T|%j|%b')
    registered={r['job_id'] for r in read(CONTROL/'jobs.json')}
    queue_rows=[dict(job_id=parts[0],state=parts[1],name=parts[2],resources=parts[3]) for parts in (line.split('|') for line in queue.splitlines())]
    controlled_active=[r for r in queue_rows if r['job_id'].split('_')[0] in registered]
    assert not controlled_active,'Registered jobs remain active'
    external=[r for r in queue_rows if r not in controlled_active]
    dump(ROOT/'results/FINAL_QUEUE_AUDIT.json',dict(time_UTC=datetime.now(timezone.utc).isoformat(),
        command='squeue -u zailong -h -o %i|%T|%j|%b',stdout=queue,
        registered_allocations=len(ledger['allocations']),all_terminal=True,
        GPU_hours=ledger['GPU_hours'],peak_concurrent_GPUs=ledger['peak_concurrent_GPUs'],remaining_controlled_jobs=[],external_jobs=external,external_jobs_not_cancelled=True))
    inputs=read(ROOT/'manifests/INPUTS.json');checked=[]
    for r in inputs['checked_files']:
        actual=sha(r['path']);assert actual==r['sha256']
        checked.append(dict(path=r['path'],before_sha256=r['sha256'],after_sha256=actual,unchanged=True))
    branch_names=['causal-next-edit-stability-v1','state-handoff-diagnosis-v1',
        'four-domain-state-coverage-v1','current-source-compatibility-v1']
    remote=command('git','ls-remote','origin',*['refs/heads/experiment/'+n for n in branch_names])
    refs={ref.removeprefix('refs/heads/experiment/'):head for head,ref in (r.split() for r in remote.splitlines())}
    assert all(refs[n]==inputs['baseline_remote_heads'][n] for n in branch_names)
    original_diff=command('git','diff','--name-only',cwd=PROJECT)
    assert original_diff==inputs['original_tracked_diff']
    assert command('git','branch','--show-current',cwd=PROJECT)==inputs['original_branch']
    reports=list((ROOT/'reports').glob('*/RUN_STATUS.json'))
    GPU_reports=[p for p in reports if read(p).get('allocation') and isinstance(read(p)['allocation'],dict)]
    allocation_ids={read(p)['allocation']['job_id'] for p in GPU_reports}
    assert allocation_ids=={r['job_id'] for r in ledger['allocations']}
    published=read(CONTROL/'publications.json')
    assert all(any(r['run']==str(p.parent) and r['status']=='VERIFIED' for r in published) for p in GPU_reports)
    for p in GPU_reports:
        folder=p.parent
        assert all((folder/f).exists() for f in ('REPORT.md','INTERPRETATION.md','ARTIFACTS.json'))
        # Big local caches, complete predictions, and small checkpoints are all indexed.
        for r in read(folder/'ARTIFACTS.json'):
            assert Path(r['path']).exists() and sha(r['path'])==r['sha256']
    audit=read(ROOT/'results/VALIDATION_NUMERICAL_AUDIT.json')
    path=ROOT/'results/validation_atomic_recomputed.jsonl.gz'
    atomic_rows=[json.loads(r) for r in gzip.decompress(path.read_bytes()).decode().splitlines()]
    for record in audit['atomic']:
        rs=[r for r in atomic_rows if r['seed']==record['seed'] and r['method']==record['method']]
        group=record['grouping'];value=record['stratum']
        if group=='source':
            if value!='all_50_50':rs=[r for r in rs if r['source']==value]
        else:rs=[r for r in rs if r[group]==value]
        assert len(rs)==record['records']
        for field in ('joint','target','content','parseable','EOS','exact_match'):
            assert sum(r[field] for r in rs)==record[field+'_numerator']
    selected_checked=False;trajectory_checked=False
    if (ROOT/'results/SELECTED_VALIDATION_NUMERICAL_AUDIT.json').exists():
        selected=read(ROOT/'results/SELECTED_VALIDATION_NUMERICAL_AUDIT.json')
        full=[json.loads(r) for r in gzip.decompress((ROOT/'results/selected_validation_atomic.jsonl.gz').read_bytes()).decode().splitlines()]
        assert len(full)==selected['records']==23040 and len({r['world_id'] for r in full})==64
        for record in selected['atomic']:
            rs=[r for r in full if r['seed']==record['seed'] and r['method']==record['method']]
            group=record['grouping'];val=record['stratum']
            if group=='source':
                if val!='all_50_50':rs=[r for r in rs if r['source']==val]
            elif group=='update_norm':
                low,high=map(float,val[1:-1].split(','));rs=[r for r in rs if low<=r['update_norm']<high]
            else:rs=[r for r in rs if r[group]==val]
            assert len(rs)==record['records']
            for field in ('joint','target','content','parseable','EOS','exact_match'):
                assert sum(r[field] for r in rs)==record[field+'_numerator']
                assert record[field+'_rate']==(sum(r[field] for r in rs)/len(rs) if rs else None)
        selected_checked=True
    if (ROOT/'results/SELECTED_TRAJECTORY_NUMERICAL_AUDIT.json').exists():
        selected=read(ROOT/'results/SELECTED_TRAJECTORY_NUMERICAL_AUDIT.json')
        full=[json.loads(r) for r in gzip.decompress((ROOT/'results/selected_validation_trajectories.jsonl.gz').read_bytes()).decode().splitlines()]
        assert len(full)==selected['records']==15360
        for record in selected['trajectories']:
            rs=[r for r in full if (r['seed'],r['method'],r['length'])==(record['seed'],record['method'],record['length'])]
            assert len(rs)==record['trajectory_denominator']==256
            assert sum(r['success'] for r in rs)==record['complete_numerator']
            assert sum(all(r['success'] for r in rs if r['world_id']==world) for world in {r['world_id'] for r in rs})==record['all_four_trajectories_world_numerator']
        trajectory_checked=True
    magnitude_checked=False
    if (ROOT/'results/TRAJECTORY_MAGNITUDE_NUMERICAL_AUDIT.json').exists():
        magnitude=read(ROOT/'results/TRAJECTORY_MAGNITUDE_NUMERICAL_AUDIT.json')
        full=[json.loads(r) for r in gzip.decompress((ROOT/'results/selected_trajectory_magnitudes.jsonl.gz').read_bytes()).decode().splitlines()]
        assert len(full)==magnitude['records']==19200 and magnitude['stored_prediction_checks']==300 and magnitude['mismatches']==0
        for record in magnitude['table']:
            rs=[r for r in full if (r['seed'],r['method'],r['step'])==(record['seed'],record['method'],record['step'])]
            assert len(rs)==256 and sum(r['complete_to_step'] for r in rs)==record['complete_numerator']
            assert sum(r['update_norm'] for r in rs)/256==record['mean_update_norm']
        magnitude_checked=True
    suite=unittest.defaultTestLoader.loadTestsFromName('experiments.decoder_readout_invariance_editing_v1.tests.test_cpu')
    out=io.StringIO();test=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
    assert test.wasSuccessful()
    dump(ROOT/'results/CPU_ACCEPTANCE_FINAL.json',dict(passed=True,tests=test.testsRun,
        failures=0,errors=0,stdout=out.getvalue(),neural_model_loaded=False,temporary_root=str(TASK_TMP)))
    dump(ROOT/'results/FINAL_DELIVERY_AUDIT.json',dict(time_UTC=datetime.now(timezone.utc).isoformat(),
        neural_model_loaded=False,checked_input_files=checked,remote_source_heads=refs,
        original_workspace_tracked_diff=original_diff,original_branch=inputs['original_branch'],
        GPU_terminal_report_count=len(GPU_reports),all_GPU_reports_published_verified=True,
        artifacts_hashes_verified=True,atomic_headlines_recomputed=True,
        selected_method_headlines_recomputed=selected_checked,
        selected_trajectory_headlines_recomputed=trajectory_checked,CPU_tests=test.testsRun,
        selected_trajectory_magnitudes_recomputed=magnitude_checked,
        independent_test_status='BLOCKED_TEST_INTEGRITY',overall_status='BLOCKED',
        location_prefix='/dataset1/zailong/'))
    print(dict(passed=True,CPU_tests=test.testsRun,GPU_reports=len(GPU_reports),
        input_files=len(checked),GPU_hours=ledger['GPU_hours'],controlled_queue=[],external_jobs=external))


def closeout():
    prior=ROOT/'results/FINAL_DELIVERY_AUDIT.json';prior_sha=sha(prior)
    lock=read(ROOT/'configs/FINAL_EXPOSURE_LOCK.json')
    assert not lock['new_endpoint_authorized'] and lock['test_model_evaluations']==0
    for name,digest in lock['evidence_sha256'].items():assert sha(ROOT/'results'/name)==digest
    assert sha(ROOT/'configs/worlds.jsonl')==lock['original_worlds_sha256']==read(ROOT/'configs/SPLIT_LOCK.json')['sha256']
    for item in read(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')['checkpoints']:assert sha(item['path'])==item['sha256']
    out=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromName('experiments.decoder_readout_invariance_editing_v1.tests.test_cpu')
    test=unittest.TextTestRunner(stream=out,verbosity=2).run(suite);assert test.wasSuccessful()
    dump(ROOT/'results/CPU_ACCEPTANCE_FINAL.json',dict(passed=True,tests=test.testsRun,failures=0,errors=0,stdout=out.getvalue(),neural_model_loaded=False,temporary_root=str(TASK_TMP)))
    acct=accounting([r['job_id'] for r in read(CONTROL/'jobs.json')]);assert acct['all_terminal'] and acct['peak_concurrent_GPUs']<=2
    queue=command('squeue','-u',command('id','-un'),'-h','-o','%i|%T|%j|%b')
    registered={r['job_id'] for r in read(CONTROL/'jobs.json')}
    external=[dict(job_id=p[0],state=p[1],name=p[2],resources=p[3]) for p in (line.split('|') for line in queue.splitlines())]
    assert not any(r['job_id'].split('_')[0] in registered for r in external)
    dump(ROOT/'results/FINAL_QUEUE_AUDIT.json',dict(time_UTC=datetime.now(timezone.utc).isoformat(),command='squeue -u zailong -h -o %i|%T|%j|%b',stdout=queue,registered_allocations=len(acct['allocations']),all_terminal=True,GPU_hours=acct['GPU_hours'],peak_concurrent_GPUs=acct['peak_concurrent_GPUs'],remaining_controlled_jobs=[],external_jobs=external,external_jobs_not_cancelled=True))
    dump(ROOT/'results/FINAL_CLOSEOUT_AUDIT.json',dict(passed=True,prior_full_source_artifact_headline_audit_sha256=prior_sha,CPU_tests=test.testsRun,exposure_union_count=lock['known_exposed_count'],original_test_denominator=128,test_model_evaluations=0,worlds_and_all12_checkpoints_unchanged=True,exposure_evidence_hashes_verified=True,withdrawn_endpoint_guard_passed=True,neural_model_loaded=False,registered_GPU_allocations=len(acct['allocations']),GPU_hours=acct['GPU_hours'],peak_concurrent_GPUs=acct['peak_concurrent_GPUs'],remaining_controlled_jobs=[],external_jobs=external))
    print(dict(passed=True,CPU_tests=test.testsRun,known_exposed=lock['known_exposed_count'],GPU_hours=acct['GPU_hours'],external_jobs=external))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--closeout',action='store_true');args=parser.parse_args()
    closeout() if args.closeout else run()
