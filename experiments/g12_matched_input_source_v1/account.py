"""Global budget and reservation ledger; array task allocations counted once."""
import argparse,subprocess,re
from common_g12 import *
def main():
 p=argparse.ArgumentParser();p.add_argument('--reserve-job');p.add_argument('--phase');p.add_argument('--count',type=int,default=1);a=p.parse_args();b=json.loads((ROOT/'budget.json').read_text())
 if a.reserve_job:b['reservations'].append(dict(job_id=a.reserve_job,phase=a.phase,count=a.count,seconds=1800*a.count))
 jobs=[];reservations=[]
 for r in b['reservations']:
  out=subprocess.check_output(['sacct','-X','-n','-P','-j',r['job_id'],'--format=JobID,State,ElapsedRaw,Start,End,AllocTRES'],text=True);rows=[x.split('|') for x in out.splitlines() if x.strip()];parents=[x for x in rows if re.fullmatch(r'\d+(?:_\d+)?',x[0]) and (r['count']==1 or '_' in x[0])];allocated=[]
  for x in parents:
   if x[1] in ['RUNNING','PENDING','COMPLETING','CONFIGURING']:continue
   if not x[2]:continue
   g=re.search(r'(?:^|,)gres/gpu=(\d+)',x[5]);ng=int(g[1]) if g else 0;allocated.append(dict(job_id=x[0],phase=r['phase'],state=x[1],gpu_count=ng,gpu_seconds=int(x[2])*ng,start=x[3],end=x[4],alloc_tres=x[5]))
  jobs+=allocated
  reservations.append(dict(r,pending_reserved_seconds=(r['count']-len(allocated))*1800))
 b['jobs']=jobs;b['reservations']=reservations;b['gpu_seconds']=sum(x['gpu_seconds'] for x in jobs);b['reserved_seconds']=sum(x['pending_reserved_seconds'] for x in reservations);assert b['gpu_seconds']+b['reserved_seconds']<=14400
 dump('budget.json',b);print(b['gpu_seconds'],'used',b['reserved_seconds'],'reserved /14400')
if __name__=='__main__':main()
