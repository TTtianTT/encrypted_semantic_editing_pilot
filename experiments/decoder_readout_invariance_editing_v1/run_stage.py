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
    expected=8 if t['stage']=='S0' else 1 if t['stage']=='PARITY_DIAG' else 64 if t['stage'].startswith('S2') else 256 if t['stage'].startswith('S3') else 32 if t['stage']=='T5_QUALIFICATION' else 72
    expected={'S3_REGULARIZER_SMOKE':8,'S3_SELECTED_VALIDATION_TRAJECTORIES':64,'S3_VALIDATION_TRAJECTORIES':64,'S2_QUERY_BRIDGE':32,'S1_GENERATION_AUDIT':8}.get(t['stage'],expected)
    status=dict(status='RUNNING',stage=t['stage'],model=t['model'],seed=t['seed'],job_id=os.environ['SLURM_JOB_ID'],array_job_id=parent,task_index=a.task_index,step_id=os.environ['SLURM_STEP_ID'],started=datetime.now(timezone.utc).isoformat(),manifest_hash=sha(a.manifest),code_hash=objsha(m['files']),split_hash=m['split_hash'],checkpoint_hash=t['checkpoint_hash'],completed_samples=0,remaining_samples=expected,exit_code=None)
    dump(status_path,status)
    engine=None
    try:
        import torch
        assert torch.cuda.device_count()==1,'Exactly one allocated visible GPU required'
        from .engine import Engine
        engine=Engine(t)
        from .acceptance import parameter_sha
        if t['stage'].startswith('S3'):
            frozen_sha=parameter_sha(engine.model);history_sha=parameter_sha(engine.ed)
        if t['stage']=='S0':
            from .acceptance import run
            result=run(engine,folder)
        elif t['stage'] in ('S1','S1_NATIVE'):
            from .readout import run
            result=run(engine,folder)
        elif t['stage']=='S1_GENERATION_AUDIT':
            from .generation_audit import run
            result=run(engine,folder)
        elif t['stage']=='PARITY_DIAG':
            from .parity_diagnostic import run
            result=run(engine,folder)
        elif t['stage'] in ('S2','S2_NATIVE'):
            from .causal import run
            result=run(engine,folder)
        elif t['stage']=='S2_QUERY_BRIDGE':
            from .query_bridge import run
            result=run(engine,folder)
        elif t['stage'] in ('S3_SELECT','S3_MAIN'):
            from .training import run
            result=run(engine,folder)
        elif t['stage']=='S3_REGULARIZER_SMOKE':
            from .regularizer_smoke import run
            result=run(engine,folder)
        elif t['stage']=='S3_PLAIN':
            from .training import run_plain
            result=run_plain(engine,folder)
        elif t['stage']=='S3_VALIDATION_TRAJECTORIES':
            from .validation_trajectories import run
            result=run(engine,folder)
        elif t['stage']=='S3_SELECTED_VALIDATION_TRAJECTORIES':
            from .selected_trajectories import run
            result=run(engine,folder)
        elif t['stage']=='T5_QUALIFICATION':
            from .t5_qualification import run
            result=run(engine,folder)
        else:raise RuntimeError('Unimplemented stage; no fabricated completion')
        if t['stage'].startswith('S3'):
            result['frozen_backbone_sha_before']=frozen_sha
            result['frozen_backbone_sha_after']=parameter_sha(engine.model)
            result['frozen_history_sha_before']=history_sha
            result['frozen_history_sha_after']=parameter_sha(engine.ed)
            assert frozen_sha==result['frozen_backbone_sha_after'] and history_sha==result['frozen_history_sha_after']
            assert all(p.grad is None for p in engine.model.parameters())
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
