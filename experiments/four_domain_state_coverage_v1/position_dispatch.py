import argparse,subprocess,os
from common import *
p=argparse.ArgumentParser();p.add_argument('--index',type=int,required=True);args=p.parse_args();t=read(ROOT/'position_tasks.json')[args.index]
assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'Must execute inside srun'
subprocess.run([str(PYTHON),str(ROOT/'position_worker.py'),'--study',t['study'],'--domain',t['domain'],'--model',t['model']],check=True)
