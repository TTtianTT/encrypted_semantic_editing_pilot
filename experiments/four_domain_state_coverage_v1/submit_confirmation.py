"""Share the original global lock/ledger for the separate spatial correction."""
import fcntl,subprocess,os,argparse
from common import *

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    phase='space_confirmation';target=ROOT.parent/'space_relation_confirmation_v1';assert (target/'formal_lock.json').exists()
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);path=ROOT/'submissions.json';ledger=read(path)
        prior=[r for r in ledger if r['phase']==phase]
        if prior and not args.resume:print(json.dumps(dict(already_submitted=prior)));return
        if prior:
            active=subprocess.check_output(['squeue','-h','-j',','.join(r['job_id'] for r in prior),'-o','%i'],text=True).strip()
            assert not active,'Existing confirmation allocations active; do not duplicate'
        missing=[t['index'] for t in read(target/'tasks.json') if not (target/'runs/formal'/f"{t['model']}_space_s{t['seed']}"/'complete.json').exists()]
        if not missing:print('All confirmation tasks complete');return
        raw=subprocess.check_output(['squeue','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%b|%Z'],text=True)
        dependencies=[]
        for line in raw.splitlines():
            job,name,gres,cwd=line.split('|',3)
            if cwd.startswith(str(ORIGINAL)) or name.startswith(('g1','fdsc','reference-frame','encrypted')):dependencies.append(job.split('_')[0])
        assert not any('|fdsc-space-confirm-v1|' in l for l in raw.splitlines()),'Orphan confirmation allocation; inspect existing ID'
        cmd=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-space-confirm-v1','--array='+','.join(map(str,missing))+'%2']
        if dependencies:cmd+=['--dependency=afterany:'+':'.join(sorted(set(dependencies)))]
        cmd+=['experiments/space_relation_confirmation_v1/job.slurm','formal']
        intent=dict(phase=phase,indices=missing,command=cmd,pre_squeue=raw,one_gpu_per_task=True,max_array_tasks=2,protocol_sha=digest(target/'formal_lock.json'))
        dump(ROOT/'submission_intent_space_confirmation.json',intent)
        jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0]
        ledger.append(dict(**intent,job_id=jid));dump(path,ledger);dump(target/'submissions.json',[r for r in ledger if r['phase']==phase])
        print(json.dumps(dict(job_id=jid,phase=phase,dependency=dependencies,concurrency=2)))

if __name__=='__main__':main()
