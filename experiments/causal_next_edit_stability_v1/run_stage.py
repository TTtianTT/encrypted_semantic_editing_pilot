import argparse
import os
import time
import traceback
from pathlib import Path
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True,type=Path);p.add_argument('--manifest',required=True,type=Path);p.add_argument('--task-index',required=True,type=int);p.add_argument('--resume',action='store_true');a=p.parse_args()
    c=read(a.config);m=read(a.manifest);assert m['config_hash']==sha(a.config) and m['code_hash']==code_hash()
    for path,digest in c.get('input_hashes',{}).items():assert sha(ROOT/path)==digest
    t=m['tasks'][a.task_index];assert t['data_hash']==sha(ROOT/'configs/worlds.jsonl')
    folder=ROOT/t['output_path'];folder.mkdir(parents=True,exist_ok=True)
    marker=folder/'complete.json'
    if a.resume and marker.exists():assert read(marker)['task_hash']==t['task_hash'];return
    if c['gpus']==0:
        assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID')
        from .aggregate import aggregate
        result=aggregate();dump(marker,dict(task_hash=t['task_hash'],task=t,result=result));return
    from .resource_guard import runtime_check
    runtime_check(c)
    from .adapter import Engine
    start=time.monotonic()
    try:
        eng=Engine(t);ws=rows(ROOT/'configs/worlds.jsonl')
        if c['stage'].startswith('smoke'):
            from .audit import smoke
            result=smoke(eng,[w for w in ws if w['mechanism_split']=='discovery'])
        elif c['stage'].startswith('scan'):
            from .pairs import scan
            result=scan(eng,ws[:c.get('world_cap',256)],folder,a.resume)
        elif c.get('mode')=='decoder':
            from .decoder_patching import run
            result=run(eng,c,folder)
        else:
            from .rollout_eval import run
            result=run(eng,c,folder)
        dump(marker,dict(task_hash=t['task_hash'],task=t,result=result,wall_seconds=time.monotonic()-start))
        print(json.dumps(result),flush=True)
    except BaseException as error:
        dump(folder/'failure.json',dict(task=t,error=repr(error),traceback=traceback.format_exc(),wall_seconds=time.monotonic()-start,job_id=os.environ['SLURM_JOB_ID']))
        raise
if __name__=='__main__':main()
