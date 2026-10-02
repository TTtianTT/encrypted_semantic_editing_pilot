import fcntl,subprocess,os
from common import *

def main():
    phase='identity_probe'
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);ledger=read(ROOT/'submissions.json');prior=[r for r in ledger if r['phase']==phase]
        if prior:print(json.dumps(dict(already_submitted=prior)));return
        tasks=[]
        for study,domains in [('four_domain_state_coverage_v1',DOMAINS),('space_relation_confirmation_v1',['space'])]:
            for m in MODELS:
                for d in domains:
                    for s in (42,43,44):tasks.append(dict(index=len(tasks),study=study,model=m,domain=d,seed=s))
        dump(ROOT/'identity_probe_tasks.json',tasks)
        dump(ROOT/'identity_probe_lock.json',dict(files=[dict(path=p,sha256=digest(ROOT/p)) for p in ['MECHANISM_EXTENSION_PLAN.md','identity_probe.py','identity_probe.slurm','identity_probe_tasks.json']]))
        raw=subprocess.check_output(['squeue','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%b|%Z'],text=True);deps=[]
        for line in raw.splitlines():
            jid,name,gres,cwd=line.split('|',3)
            if cwd.startswith(str(ORIGINAL)) or name.startswith(('g1','fdsc','reference-frame','encrypted')):deps.append(jid.split('_')[0])
        assert not any('|fdsc-identity-probe-v1|' in l for l in raw.splitlines()),'Orphan identity probe array'
        cmd=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-identity-probe-v1','--array=0-'+str(len(tasks)-1)+'%2']
        if deps:cmd+=['--dependency=afterany:'+':'.join(sorted(set(deps)))]
        cmd+=['experiments/four_domain_state_coverage_v1/identity_probe.slurm'];intent=dict(phase=phase,indices=list(range(len(tasks))),command=cmd,pre_squeue=raw,one_gpu_per_task=True,max_array_tasks=2,protocol_sha=digest(ROOT/'identity_probe_lock.json'))
        dump(ROOT/'submission_intent_identity_probe.json',intent);jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0];ledger.append(dict(**intent,job_id=jid));dump(ROOT/'submissions.json',ledger);print(json.dumps(dict(job_id=jid,phase=phase,tasks=len(tasks),concurrency=2)))

if __name__=='__main__':main()
