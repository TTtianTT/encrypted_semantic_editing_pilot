"""Offline accounting of an independently captured sacct snapshot."""
import sys
from datetime import datetime
from task import *
b=json.loads((ROOT/'budget.json').read_text());known={str(j['job_id']):j for j in b['jobs']}
for arg in sys.argv[1:]:
 jid,phase,label=arg.split(':');known.setdefault(jid,dict(job_id=int(jid),phase=phase,label=label))
s=(ROOT/'logs/sacct.txt').read_text()
for jid,j in known.items():
 rows=[l.split('|') for l in s.splitlines() if l.split('|')[0].split('.')[0]==jid]
 if not rows:continue
 p=next(r for r in rows if r[0]==jid);j.update(state=p[1],gpu_seconds=max(int(r[2]) for r in rows),allocation=p[3],submit=p[4],start=p[5],end=p[6])
 try:j['queue_seconds']=(datetime.fromisoformat(p[5])-datetime.fromisoformat(p[4])).total_seconds()
 except ValueError:j['queue_seconds']=None
b['jobs']=list(known.values());b['total_gpu_seconds']=sum(j.get('gpu_seconds',0) for j in b['jobs']);b['remaining_gpu_seconds']=7200-b['total_gpu_seconds'];assert b['remaining_gpu_seconds']>=0;dump('budget.json',b);print('GPU seconds',b['total_gpu_seconds'],'remaining',b['remaining_gpu_seconds'])
