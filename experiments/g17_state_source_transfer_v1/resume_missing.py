"""CPU-only diagnosed engineering recovery; original scientific entry unchanged."""
import fcntl,subprocess
from common_g17 import *
def main():
    verify_lock()
    with (ROOT/'submission.lock').open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        rs=json.loads((ROOT/'submissions.json').read_text());assert not any(r['phase']=='resume_seed43' for r in rs)
        main=next(r for r in rs if r['phase']=='main');failed=main['job_id']+'_1'
        state=subprocess.check_output(['sacct','-X','-n','-P','-j',failed,'--format=State,ExitCode'],text=True).strip();assert state=='FAILED|1:0'
        log=ROOT/f'logs/g17-main_{main["job_id"]}_1.err';assert 'TimeoutError: Allocation budget stop' in log.read_text()
        expected={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'outputs').glob('s43_*.jsonl.gz')};assert len(expected)==7
        cache={str(p.relative_to(ROOT)):json.loads(p.read_text())['cache_sha256'] for p in (ROOT/'cache_manifests').glob('confirm_s43_*.json')};assert len(cache)==8
        requested=sum(r['requested_gpu_seconds'] for r in rs)+600;assert requested<=7200
        cmd=['sbatch','--partition=B300q','--time=10:00',f'--dependency=afterany:{main["job_id"]}','--array=1-1%1','--job-name=g17-resume43','--export=ALL,RF_WALL_SECONDS=570',str((ROOT/'scripts/main.sbatch').relative_to(REPO))]
        output=subprocess.check_output(cmd,cwd=REPO,text=True).strip();job=output.split()[-1];assert job.isdigit()
        rs.append(dict(phase='resume_seed43',job_id=job,command=cmd,wall_seconds=600,allocations=1,gpus_per_allocation=1,requested_gpu_seconds=600,dependency_all_main_ended=True,seed_index=1,seed=43,scientific_lock_sha256=digest(ROOT/'scientific_lock.json')));dump(ROOT/'submissions.json',rs)
        dump(ROOT/'recovery_lock.json',dict(only_missing_output='s43_template_ood_a-2.jsonl.gz',preserved_output_sha256=expected,preserved_cache_sha256=cache,scientific_lock_sha256=digest(ROOT/'scientific_lock.json'),original_failure=failed,new_job_id=job,reason='smoke underestimated slow allocation; safe time stop; no scientific score-based retry'))
        events=json.loads((ROOT/'engineering_events.json').read_text());events.append(dict(phase='main seed43',job_id=failed,engineering_failure='safe time budget stop in final OOD -2 shard',fix='reuse8immutable caches/7existing output SHAs; complete missing last shard using same code/config/models',science_unchanged=True,requested_gpu_seconds=600,reserve_consumed=True,dependency=main['job_id']));dump(ROOT/'engineering_events.json',events)
        with (ROOT/'commands.log').open('a') as c:c.write(' '.join(cmd)+'\n'+output+'\n')
        print(output)
if __name__=='__main__':main()
