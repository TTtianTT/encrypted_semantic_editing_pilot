"""Unique CPU submitter. Global lock and conservative queue/budget gates."""
import argparse
import fcntl
import getpass
import shlex
from datetime import datetime, timezone
from .common import *
from .resources import accounting

def submit(stage):
    CONTROL.mkdir(exist_ok=True)
    with (CONTROL/'global.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        ledger_path=CONTROL/'jobs.json';ledger=read(ledger_path) if ledger_path.exists() else []
        previous=[r for r in ledger if r['stage']==stage]
        if previous:
            print('Already registered; no duplicate submission:',previous[-1]['job_id']);return
        manifest_path=ROOT/f'manifests/{stage}.json';m=read(manifest_path)
        active=command('squeue','-u',getpass.getuser(),'-h','-o','%i|%T|%b|%j|%P')
        # Any account GPU/unknown-resource job blocks: older submitters do not honor our lock.
        gpu_jobs=[line for line in active.splitlines() if 'gpu' in line.lower() or line.split('|')[-1] in ('B300q','RTXq')]
        acct=accounting([r['job_id'] for r in ledger]);dump(ROOT/'results/resource_ledger.json',acct)
        reason='BLOCKED_CONCURRENCY' if gpu_jobs else 'NOT_RUN_BUDGET' if acct['GPU_hours']+m['reservation_GPU_hours']>40 else None
        if ledger and not acct['all_terminal']:reason='BLOCKED_CONCURRENCY'
        if reason:
            dump(ROOT/f'results/{stage}_SUBMISSION_STATUS.json',dict(status=reason,active_queue=active,accounting=acct));raise RuntimeError(reason)
        # Verify immutable scientific files and input hashes before any submission.
        for rel,digest in m['files'].items():assert sha(Path(m['snapshot'])/rel)==digest
        for path,digest in m['checkpoint_hashes'].items():assert sha(path)==digest
        logs=ROOT/'local/slurm_logs';logs.mkdir(parents=True,exist_ok=True)
        cmd=['sbatch','--parsable','--partition='+m['partition'],'--gres=gpu:1','--time='+m['walltime'],'--job-name=drie-v1-'+stage,'--array=0-'+str(len(m['tasks'])-1)+'%2','--output='+str(logs/'%x-%A_%a.out'),'--error='+str(logs/'%x-%A_%a.err'),'--export=ALL,RUN_SNAPSHOT='+m['snapshot']+',MANIFEST='+str(manifest_path)+',PYTHON_BIN='+m['python'],str(ROOT/'slurm/worker.sbatch')]
        printable=shlex.join(cmd);text(ROOT/f'manifests/{stage}_submit_command.txt',printable+'\n')
        job=command(*cmd).split(';')[0];assert job.isdigit()
        entry=dict(stage=stage,job_id=job,manifest=str(manifest_path),manifest_hash=sha(manifest_path),snapshot=m['snapshot'],GPUs_per_task=1,array_concurrency=2,reservation_GPU_hours=m['reservation_GPU_hours'],submitted=datetime.now(timezone.utc).isoformat(),queue_before=active,command=printable)
        ledger.append(entry);dump(ledger_path,ledger);dump(ROOT/f'manifests/{stage}_registration.json',entry)
        print(printable);print('Registered job',job)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True);a=p.parse_args();submit(a.stage)
