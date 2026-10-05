"""Worker: GPU only under registered sbatch array and srun; atomic batch resume."""
import argparse
import time
from .common import *

def run(manifest,index,resume):
    from .resource import runtime_check
    package=read(manifest);task=package['tasks'][index];runtime_check(package,task)
    assert task['execution_commit']==cmd(['cat',WT/'EXECUTION_COMMIT'])
    assert sha(task['world_file'])==task['world_hash']
    for p,h in task['source_files'].items():assert sha(p)==h,p
    assert sha(ROOT/'protocol.yaml')==task['protocol_hash']
    from .engine import Engine,atomic_table,bart_second,cross_matrix,depth_diagnosis,smoke_acceptance
    import torch
    folder=Path(task['output']);folder.mkdir(parents=True,exist_ok=True)
    if (folder/'complete.json').exists():
        assert read(folder/'complete.json')['scientific_hash']==task['scientific_hash'];return
    dump(folder/f'attempt_{os.environ["SLURM_JOB_ID"]}.json',dict(task=task,started_at=now(),job_id=os.environ['SLURM_JOB_ID'],attempt_state='RUNNING'))
    start=time.monotonic();eng=Engine(task)
    worlds=rows(task['world_file'])
    if task['round']!='R00':worlds=[w for w in worlds if w['split']==task['split']]
    expected=[];checks=[]
    try:
        with torch.inference_mode():
            for i in range(0,len(worlds),task['batch_size']):
                batch=worlds[i:i+task['batch_size']];p=folder/f'batch_{i:04d}.jsonl';meta=p.with_suffix('.meta.json');expected.append(str(p))
                if p.exists() and meta.exists():
                    m=read(meta);assert m['scientific_hash']==task['scientific_hash'] and m['sha256']==sha(p)
                    if m.get('acceptance'):checks.append(m['acceptance'])
                    continue
                if task['round']=='R03':records=depth_diagnosis(eng,batch)
                else:
                    records,natural,obs=atomic_table(eng,batch)
                    records += bart_second(eng,batch,natural,obs) if task['model']=='bart' else cross_matrix(eng,batch,natural,obs)
                acceptance=smoke_acceptance(eng,batch,records) if task['round']=='R00' else None
                eng.frozen_check();jsonl(p,records)
                dump(meta,dict(scientific_hash=task['scientific_hash'],execution_commit=task['execution_commit'],sha256=sha(p),rows=len(records),worlds=[w['world_id'] for w in batch],job_id=os.environ['SLURM_JOB_ID'],acceptance=acceptance))
                if acceptance:checks.append(acceptance)
                print(f'{task["run_id"]}: {i+len(batch)}/{len(worlds)} worlds saved; decode calls={eng.decode_calls}',flush=True)
        eng.frozen_check();dump(folder/'artifacts.json',list(eng.artifacts.values()))
        dump(folder/'complete.json',dict(scientific_hash=task['scientific_hash'],execution_commit=task['execution_commit'],expected_worlds=len(worlds),expected_batches=len(expected),shards=[dict(path=p,sha256=sha(p)) for p in expected],acceptance=checks,resources=eng.resources(),encode_calls=eng.encode_calls,encoder_forward_calls=eng.encoder_forward_calls,decode_calls=eng.decode_calls,reused_cache_count=eng.reuse_count,new_cache_count=eng.new_count,wall_seconds=time.monotonic()-start,finished_at=now()))
    finally:eng.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--task-index',type=int,required=True);p.add_argument('--resume',action='store_true');a=p.parse_args();run(a.manifest,a.task_index,a.resume)
