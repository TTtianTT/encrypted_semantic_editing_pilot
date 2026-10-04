"""Account-wide dependencies, one global phase array, persistent intent and lock."""
import argparse,fcntl,subprocess,os,re
from study import *
def complete(phase,i):return (ROOT/'SMOKE_AUDIT.json').exists() if phase=='smoke' else (ROOT/f'runs/{phase}/s{(42,43,44)[i]}/complete.json').exists()
def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['smoke','preflight','formal']);p.add_argument('--resume',action='store_true');a=p.parse_args();verify_lock();(ROOT/'logs').mkdir(exist_ok=True)
    with (ROOT/'submission.lock').open('a+') as lock:
      fcntl.flock(lock,fcntl.LOCK_EX);file=ROOT/'submissions.json';ledger=read(file) if file.exists() else []
      previous=[r for r in ledger if r['phase']==a.phase]
      if previous and not a.resume:print('Already submitted:',previous[-1]['job_id']);return
      if a.phase!='smoke':assert read(ROOT/'SMOKE_AUDIT.json')['passed']
      if a.phase=='formal':
       for seed in (42,43,44):assert read(ROOT/f'runs/preflight/s{seed}/complete.json')['passed']
      missing=[i for i in range(1 if a.phase=='smoke' else 3) if not complete(a.phase,i)]
      if not missing:print('All tasks complete');return
      raw=subprocess.check_output(['squeue','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%b|%Z'],text=True)
      # Every account GPU allocation/pending allocation is included, regardless of project.
      dependencies=sorted({line.split('|')[0].split('_')[0] for line in raw.splitlines() if re.search(r'gpu',line.split('|')[2])})
      assert not any('|csc-v1-'+a.phase+'|' in line for line in raw.splitlines()),'Existing matching job active; no duplicate'
      intent_path=ROOT/f'intent_{a.phase}.json'
      if intent_path.exists() and not previous:raise RuntimeError('Unrecorded submission intent exists: inspect scheduler and recover its ID; never resubmit blindly')
      cmd=['sbatch','--parsable','--partition=B300q','--job-name=csc-v1-'+a.phase,'--array='+','.join(map(str,missing))+('%1' if a.phase=='smoke' else '%2'),'--time='+('01:00:00' if a.phase=='smoke' else '12:00:00')]
      if dependencies:cmd+=['--dependency=afterany:'+':'.join(dependencies)]
      cmd+=['experiments/current_source_compatibility_v1/job.slurm',a.phase]
      intent=dict(phase=a.phase,indices=missing,pre_account_squeue=raw,all_account_GPU_dependencies=dependencies,command=cmd,created_utc=now());dump(intent_path,intent)
      jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0];ledger.append(dict(**intent,job_id=jid));dump(file,ledger);print(json.dumps(dict(job_id=jid,phase=a.phase,tasks=len(missing),max_gpus=1 if a.phase=='smoke' else 2)))
if __name__=='__main__':main()
