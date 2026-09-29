import subprocess,sys
from datetime import datetime
from common import *
b=json.loads((ROOT/'budget.json').read_text());known={str(j['job_id']):j for j in b['jobs']}
for arg in sys.argv[1:]:
 jid,phase,model=arg.split(':');known[jid]={'job_id':int(jid),'phase':phase,'model':model}
s=subprocess.check_output(['sacct','-j',','.join(known),'--format=JobIDRaw,State,ElapsedRaw,AllocTRES,Submit,Start,End','-n','-P'],text=True);(ROOT/'logs/sacct.txt').write_text(s)
for jid,meta in known.items():
 rows=[l.split('|') for l in s.splitlines() if l.split('|')[0].split('.')[0]==jid]
 if not rows:continue
 p=next(r for r in rows if r[0]==jid);meta.update(state=p[1],gpu_seconds=max(int(r[2]) for r in rows),allocation=p[3],submit=p[4],start=p[5],end=p[6])
 try:meta['queue_seconds']=(datetime.fromisoformat(p[5])-datetime.fromisoformat(p[4])).total_seconds()
 except ValueError:meta['queue_seconds']=None
b['jobs']=list(known.values());b['total_gpu_seconds']=sum(r.get('gpu_seconds',0) for r in b['jobs']);b['preflight_gpu_seconds']=sum(r.get('gpu_seconds',0) for r in b['jobs'] if r['phase']=='preflight');b['remaining_gpu_seconds']=14400-b['total_gpu_seconds'];b['remaining_preflight_seconds']=3600-b['preflight_gpu_seconds'];assert b['remaining_gpu_seconds']>=0 and b['remaining_preflight_seconds']>=0;dump('budget.json',b);print(json.dumps(b))
