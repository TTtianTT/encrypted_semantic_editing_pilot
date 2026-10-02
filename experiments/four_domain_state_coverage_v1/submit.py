"""One global Slurm submission lock, arrays%2, dependency on ALL project allocations."""
import argparse,fcntl,subprocess,os
from common import *

def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['engineering','interface','formal','symbol']);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    (ROOT/'logs').mkdir(exist_ok=True)
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path=ROOT/'submissions.json';ledger=read(path) if path.exists() else []
        prior=[v for v in ledger if v['phase']==args.phase]
        if prior and not args.resume:print(json.dumps(dict(already_submitted=prior)));return
        if args.phase in ('formal','symbol'):
            assert (ROOT/'formal_lock.json').exists(),'Formal config/code must be locked before formal/symbol'
        if prior:
            active=subprocess.check_output(['squeue','-h','-j',','.join(v['job_id'] for v in prior),'-o','%i'],text=True).strip()
            assert not active,'Existing phase allocations active; do not duplicate'
        tasks=[t for t in read(ROOT/'tasks.json') if t['phase']==args.phase];missing=[]
        for t in tasks:
            p=ROOT/'runs'/args.phase/f"{t['model']}_{t['domain']}_s{t['seed']}"/'complete.json'
            if not p.exists():missing.append(t['index'])
        if not missing:print('All phase tasks complete');return
        raw=subprocess.check_output(['squeue','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%b|%Z'],text=True)
        dependencies=[];existing=[]
        for line in raw.splitlines():
            job,name,gres,cwd=line.split('|',3)
            if cwd.startswith(str(ORIGINAL)) or name.startswith(('g1','fdsc','reference-frame','encrypted')):
                # Array parent dependency includes every sibling and any queued retry.
                parent=job.split('_')[0];dependencies.append(parent);existing.append(line)
        # Fresh arrays wait for ALL project jobs, so existing allocations cannot
        # overlap these two tasks even when other project scripts lack our lock.
        orphan=[line for line in raw.splitlines() if '|fdsc-v1-'+args.phase+'|' in line]
        assert not orphan,'Active matching phase without submission record; inspect/recover its ID instead of resubmitting'
        args_sbatch=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-v1-'+args.phase,'--array='+','.join(map(str,missing))+'%2']
        if dependencies:args_sbatch+=['--dependency=afterany:'+':'.join(sorted(set(dependencies)))]
        args_sbatch+=['experiments/four_domain_state_coverage_v1/job.slurm',args.phase]
        intent=dict(phase=args.phase,indices=missing,command=args_sbatch,pre_squeue=raw,project_dependencies=existing,one_gpu_per_task=True,max_array_tasks=2)
        dump(ROOT/f'submission_intent_{args.phase}.json',intent)
        jid=subprocess.check_output(args_sbatch,cwd=WORKTREE,text=True).strip().split(';')[0]
        ledger.append(dict(**intent,job_id=jid));dump(path,ledger);print(json.dumps(dict(job_id=jid,phase=args.phase,tasks=len(missing),concurrency=2)))

if __name__=='__main__':main()
