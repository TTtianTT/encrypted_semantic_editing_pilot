"""Single-allocation ledger, not Slurm parent+step double-counting."""
import argparse,subprocess
from g11 import *
def seconds(s):
 day=0
 if '-' in s:ds,s=s.split('-');day=int(ds)
 vals=list(map(int,s.split(':')));return day*86400+sum(v*m for v,m in zip(vals,[3600,60,1][-len(vals):]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',required=True);p.add_argument('--phase',required=True);a=p.parse_args();out=subprocess.check_output(['sacct','-X','-n','-P','-j',a.job,'--format=JobID,State,Elapsed,Start,End,AllocTRES'],text=True);lines=[s.split('|') for s in out.splitlines() if s.strip()];r=next(x for x in lines if x[0]==a.job);state=r[1];assert state not in ['RUNNING','PENDING','COMPLETING'],state
 b=json.loads((ROOT/'budget.json').read_text());b['jobs']=[x for x in b['jobs'] if x['job_id']!=a.job];b['jobs'].append(dict(job_id=a.job,phase=a.phase,state=state,allocated_gpu_seconds=seconds(r[2]),start=r[3],end=r[4],alloc_tres=r[5],gpu_count=1));b['gpu_seconds']=sum(x['allocated_gpu_seconds'] for x in b['jobs']);assert b['gpu_seconds']<=7200;dump('budget.json',b);print('allocation ledger',b['gpu_seconds'],'/7200',state)
if __name__=='__main__':main()
