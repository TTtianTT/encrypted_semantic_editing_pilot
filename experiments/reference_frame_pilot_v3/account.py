import subprocess,sys
from datetime import datetime
from common import *
jobs=[int(x) for x in sys.argv[1:]]
s=subprocess.check_output(['sacct','-j',','.join(map(str,jobs)),'--format=JobIDRaw,State,ElapsedRaw,AllocTRES,Submit,Start,End','-n','-P'],text=True)
(ROOT/'logs/sacct.txt').write_text(s);records=[]
for jid in jobs:
 lines=[l.split('|') for l in s.splitlines() if l.split('|')[0].split('.')[0]==str(jid)];parent=next(x for x in lines if x[0]==str(jid));elapsed=max(int(x[2]) for x in lines)
 wait=None
 try:wait=(datetime.fromisoformat(parent[5])-datetime.fromisoformat(parent[4])).total_seconds()
 except ValueError:pass
 records.append(dict(job_id=jid,state=parent[1],gpu_allocation_seconds=elapsed,queue_seconds=wait,allocation=parent[3],submit=parent[4],start=parent[5],end=parent[6]))
total=sum(r['gpu_allocation_seconds'] for r in records);assert total<=3600
dump('budget.json',dict(limit_gpu_allocation_seconds=3600,max_concurrent_gpus=1,jobs=records,total_gpu_allocation_seconds=total,gpu_hours=total/3600,remaining_seconds=3600-total,accounting='maximum parent/step elapsed, no double counting; queue separate'))
print(total,records)
