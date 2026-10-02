"""Correct remaining admission ordering without creating duplicate P updates."""
import fcntl,subprocess
from common import *

def main():
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);ledger=read(ROOT/'submissions.json')
        if any(r['phase']=='atomic_preflight_remaining' for r in ledger):print('Already submitted; inspect atomic_preflight_submission.json');return
        parent=next(r['job_id'] for r in ledger if r['phase']=='formal');tasks=[t for t in read(ROOT/'tasks.json') if t['phase']=='formal' and t['index'] in range(16,24)];assert len(tasks)==8
        raw=subprocess.check_output(['squeue','--array','-h','-u','zailong','-o','%i|%T|%j|%b|%Z'],text=True);entries=[r.split('|',4) for r in raw.splitlines()];held=[parent+'_'+str(t['index']) for t in tasks];assert all(any(r[0]==jid and r[1]=='PENDING' for r in entries) for jid in held),'Remaining tasks have already started'
        active=[r[0] for r in entries if r[1] in ('RUNNING','COMPLETING') and (r[4].startswith(str(ORIGINAL)) or r[2].startswith('fdsc'))];assert set(active)<= {parent+'_14',parent+'_15'} and active
        dump(ROOT/'atomic_preflight_tasks.json',tasks);files=['REMAINING_ATOMIC_PREFLIGHT.md','atomic_preflight_worker.py','atomic_preflight.slurm','atomic_preflight_tasks.json'];dump(ROOT/'atomic_preflight_lock.json',dict(files=[dict(path=p,sha256=digest(ROOT/p)) for p in files]))
        for jid in held:subprocess.run(['scontrol','hold',jid],check=True)
        cmd=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-atomic-preflight-v1','--array=0-7%2','--dependency=afterany:'+':'.join(sorted(active)),'experiments/four_domain_state_coverage_v1/atomic_preflight.slurm'];jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0];ledger.append(dict(phase='atomic_preflight_remaining',job_id=jid,indices=list(range(8)),command=cmd,pre_squeue=raw,one_gpu_per_task=True,max_array_tasks=2,no_extra_P_updates=True));dump(ROOT/'submissions.json',ledger)
        record=dict(held_children=held,atomic_job_id=jid,running_dependencies=active,global_max_gpus=2,original_formal_parent=parent);dump(ROOT/'atomic_preflight_submission.json',record)
        release=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-atomic-release-v1','--dependency=afterany:'+jid,'experiments/four_domain_state_coverage_v1/release_after_atomic.slurm'];rid=subprocess.check_output(release,cwd=WORKTREE,text=True).strip().split(';')[0];ledger.append(dict(phase='atomic_preflight_release',job_id=rid,indices=[0],command=release,one_gpu_per_task=False,max_array_tasks=1));dump(ROOT/'submissions.json',ledger);dump(ROOT/'atomic_preflight_submission.json',dict(**record,release_cpu_job_id=rid));print(json.dumps(dict(atomic_preflight=jid,cpu_release=rid,held_children=held,gpu_limit=2)))

if __name__=='__main__':main()
