"""Allocation-level GPU accounting; array parent/batch/extern/srun never double-counted."""
import re, subprocess
from common_g13 import *
def main():
    submissions=json.loads((ROOT/'submissions.json').read_text()); jobs=','.join(r['job_id'] for r in submissions)
    fields='JobIDRaw,JobID,State,ExitCode,Partition,NodeList,Submit,Start,End,ElapsedRaw,AllocTRES,MaxRSS'
    raw=subprocess.check_output(['sacct','-X','-P','-j',jobs,'--format='+fields],text=True); (ROOT/'allocation_details.psv').write_text(raw)
    allocations=list(csv.DictReader(raw.splitlines(),delimiter='|')); rows=[]
    for r in allocations:
        if '.' in r['JobID'] or not r['Start'] or r['Start']=='Unknown': continue
        m=re.search(r'(?:^|,)gres/gpu=(\d+)(?:,|$)',r['AllocTRES']); n=int(m[1]) if m else 0
        if n==0: continue
        rows.append(dict(job_id=r['JobID'],state=r['State'],exit_code=r['ExitCode'],partition=r['Partition'],node=r['NodeList'],submit=r['Submit'],start=r['Start'],end=r['End'],gpu_count=n,elapsed_seconds=int(r['ElapsedRaw']),gpu_hours=int(r['ElapsedRaw'])*n/3600,allocation_TRES=r['AllocTRES']))
    csvwrite(ROOT/'slurm_jobs.csv',rows)
    total=sum(r['gpu_hours'] for r in rows)
    dump(ROOT/'budget.json',dict(limit_gpu_hours=12,actual_gpu_hours=total,requested_gpu_hours=sum(r['requested_gpu_seconds'] for r in submissions)/3600,allocation_rows=len(rows),no_step_double_count=True,within_limit=total<=12,max_concurrency=2))
    print('allocation GPU hours',total,flush=True)
if __name__=='__main__': main()
