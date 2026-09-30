"""Stage barrier and global reservation checks before sbatch."""
import argparse,subprocess,getpass
from common_g12 import *
def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['preflight','train','current','finish']);a=p.parse_args();lock();b=json.loads((ROOT/'budget.json').read_text());assert b['gpu_seconds']+b.get('reserved_seconds',0)+(5400 if a.phase=='train' else 1800)<=14400
 out=subprocess.check_output(['squeue','-h','-u',getpass.getuser(),'-o','%i %j'],text=True)
 assert not any('g12-' in row for row in out.splitlines()),'Previous G12 stage still active: '+out
 if a.phase=='train':assert json.loads((ROOT/'smoke_test.json').read_text())['passed']
 if a.phase in ['current','finish']:
  for s in CFG['seeds']:
   for arm in ['A','B']:assert json.loads((ROOT/f'training/{arm}_seed{s}.json').read_text())['updates']==200
 if a.phase=='finish':assert (ROOT/'data/cohort_lock.json').exists()
 cmd=['sbatch','--parsable','--partition=B300q','--exclude=node01']
 if a.phase=='train':cmd += [str(ROOT.relative_to(REPO)/'train.slurm')]
 else:cmd += ['--export=ALL,G12_PHASE='+a.phase,str(ROOT.relative_to(REPO)/'job.slurm')]
 job=subprocess.check_output(cmd,text=True).strip().split(';')[0]
 subprocess.check_call([sys.executable,str(ROOT/'account.py'),'--reserve-job',job,'--phase',a.phase,'--count','3' if a.phase=='train' else '1'])
 with (ROOT/'commands.log').open('a') as f:f.write(' '.join(cmd)+' # job '+job+'\n')
 print('submitted',a.phase,job,flush=True)
if __name__=='__main__':main()
