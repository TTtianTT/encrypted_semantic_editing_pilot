"""The sole neural entry; imports science only after Slurm/registration guards."""
import argparse
import os
import time
import traceback
from datetime import datetime, timezone
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--task-index',required=True,type=int);p.add_argument('--resume',action='store_true');a=p.parse_args()
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'), 'Neural work requires sbatch+srun'
    assert os.environ.get('SLURM_ARRAY_TASK_ID')==str(a.task_index)
    m=read(a.manifest);t=m['tasks'][a.task_index]
    assert Path(m['snapshot']).resolve()==WT.resolve(),'Wrong immutable snapshot'
    parent=os.environ.get('SLURM_ARRAY_JOB_ID',os.environ['SLURM_JOB_ID'])
    registered=False
    for _ in range(60):
        if (CONTROL/'jobs.json').exists():
            registered=any(r['job_id']==parent and r['manifest_hash']==sha(a.manifest) for r in read(CONTROL/'jobs.json'))
        if registered:break
        time.sleep(1)
    assert registered,'Unregistered allocation'
    for rel,digest in m['files'].items():assert sha(WT/rel)==digest,rel
    assert sha(t['checkpoint'])==t['checkpoint_hash']
    folder=Path(m['output_root'])/f"{t['model']}_s{t['seed']}";folder.mkdir(parents=True,exist_ok=True)
    status_path=folder/'RUN_STATUS.json'
    if status_path.exists() and read(status_path)['status']=='COMPLETED':return
    status=dict(status='RUNNING',stage=t['stage'],model=t['model'],seed=t['seed'],job_id=os.environ['SLURM_JOB_ID'],array_job_id=parent,task_index=a.task_index,step_id=os.environ['SLURM_STEP_ID'],started=datetime.now(timezone.utc).isoformat(),manifest_hash=sha(a.manifest),code_hash=objsha(m['files']),split_hash=m['split_hash'],checkpoint_hash=t['checkpoint_hash'],completed_samples=0,remaining_samples=8 if t['stage']=='S0' else 1 if t['stage']=='PARITY_DIAG' else 72,exit_code=None)
    dump(status_path,status)
    engine=None
    try:
        import torch
        assert torch.cuda.device_count()==1,'Exactly one allocated visible GPU required'
        from .engine import Engine
        engine=Engine(t)
        if t['stage']=='S0':
            from .acceptance import run
            result=run(engine,folder)
        elif t['stage']=='S1':
            from .readout import run
            result=run(engine,folder)
        elif t['stage']=='PARITY_DIAG':
            from .parity_diagnostic import run
            result=run(engine,folder)
        else:raise RuntimeError('Unimplemented stage; no fabricated completion')
        dump(folder/'SUMMARY.json',result)
        status.update(status=result.get('status','COMPLETED' if result['passed'] else 'FAILED_TECHNICAL'),exit_code=0 if result['passed'] else 1,completed_samples=result.get('worlds',0),remaining_samples=0)
    except BaseException as e:
        status.update(status='FAILED_TECHNICAL',exit_code=1,error=repr(e),traceback=traceback.format_exc())
        text(folder/'FAILURE.txt',status['traceback']);raise
    finally:
        status['ended']=datetime.now(timezone.utc).isoformat()
        if engine:status['GPU_config']=engine.resources()
        status['artifacts']=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in folder.rglob('*') if p.is_file() and p!=status_path]
        dump(status_path,status)
    if status['exit_code']:raise SystemExit(status['exit_code'])

if __name__=='__main__':main()
