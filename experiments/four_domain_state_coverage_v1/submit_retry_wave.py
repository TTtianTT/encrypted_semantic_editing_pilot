"""Insert timeout-only recovery before all downstream pending project phases."""
import fcntl,subprocess
from common import *

def main():
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);ledger=read(ROOT/'submissions.json');previous=[r for r in ledger if r['phase']=='formal_retry']
        if previous:print(json.dumps(dict(already_submitted=previous)));return
        original=next(r for r in ledger if r['phase']=='formal');parent=original['job_id']
        raw=subprocess.check_output(['squeue','--array','-h','-u','zailong','-o','%i|%T|%b|%Z'],text=True);entries=[r.split('|',3) for r in raw.splitlines()]
        assert any(r[0].split('_')[0]==parent for r in entries),'Use normal fresh missing-task submission when original parent is terminal'
        downstream=[r for r in ledger if r['phase'] in ('symbol','space_confirmation','identity_probe','linguistic_controls','finalize') and any(v[0].split('_')[0]==r['job_id'] for v in entries)]
        assert all(v[1]=='PENDING' for v in entries if v[0].split('_')[0] in {r['job_id'] for r in downstream})
        dump(ROOT/'retry_wave_parent.json',dict(job_id=parent));dump(ROOT/'retry_wave_tasks.json',[t for t in read(ROOT/'tasks.json') if t['phase']=='formal'])
        intent=dict(parent=parent,pending_downstream=[r['job_id'] for r in downstream],queue=raw,reason='One original child timed out and was purged by controller; resume only missing tasks after parent termination, before later phases.',resource_amendment='Evaluation recovery workers6h within verified unlimited B300q partition; no training budget/config/checkpoint change; initial48GPUh cap remains.')
        dump(ROOT/'retry_wave_intent.json',intent)
        for r in downstream:subprocess.run(['scontrol','hold',r['job_id']],check=True)
        cmd=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-formal-retry-v1','--array=0-1%2','--dependency=afterany:'+parent,'experiments/four_domain_state_coverage_v1/retry_wave.slurm'];jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0]
        ledger.append(dict(phase='formal_retry',job_id=jid,indices=[0,1],command=cmd,pre_squeue=raw,one_gpu_per_task=True,max_array_tasks=2,worker_claims_only_missing_tasks=True));dump(ROOT/'submissions.json',ledger)
        for r in downstream:
            original_dep=next((s.split('=',1)[1] for s in r['command'] if s.startswith('--dependency=')),None)
            deps=set(original_dep.split(':')[1:] if original_dep else []);deps.add(jid)
            dependency='afterany:'+':'.join(sorted(deps));subprocess.run(['scontrol','update','JobId='+r['job_id'],'Dependency='+dependency],check=True);r['recovery_dependency']=dependency;dump(ROOT/'submissions.json',ledger)
            subprocess.run(['scontrol','release',r['job_id']],check=True)
        dump(ROOT/'retry_wave_submitted.json',dict(**intent,job_id=jid,downstream_updated=True));print(json.dumps(dict(job_id=jid,concurrency=2,downstream=[r['job_id'] for r in downstream])))

if __name__=='__main__':main()
