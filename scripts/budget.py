"""Read-only conservative Slurm accounting for this pilot. No submission."""
import subprocess,json,csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ids=[1611,1612,1613,1614,1615,1616,1617,1618]
cmd=['sacct','-j',','.join(map(str,ids)),'--format=JobID,State,ElapsedRaw,AllocTRES%100,NodeList','-P']
s=subprocess.check_output(cmd,text=True);(ROOT/'logs/slurm_accounting.tsv').write_text(s);rows=list(csv.DictReader(s.splitlines(),delimiter='|'));jobs=[]
for jid in ids:
 rr=[r for r in rows if r['JobID'].split('.')[0]==str(jid)];base=next((r for r in rr if r['JobID']==str(jid)),{})
 if not base:continue
 n=1 if any('gres/gpu=1' in r['AllocTRES'] for r in rr) else 0
 seconds=max(int(r['ElapsedRaw']) for r in rr)
 jobs.append({'job_id':jid,'state':base['State'],'seconds_conservative':seconds,'n_gpu':n,'GPU_hours':seconds*n/3600,'node':base['NodeList'],'note':'max parent/step elapsed, no double counting of steps'})
gpu=sum(j['GPU_hours'] for j in jobs);cpu=sum(j['seconds_conservative'] for j in jobs if j['job_id']==1614)
x={'jobs':jobs,'GPU_hours_conservative':gpu,'GPU_hours_remaining':max(0,12-gpu),'CPU_HE_job_wall_hours':cpu/3600,'CPU_HE_smoke_wall_seconds_allowance':5,'limits':{'GPU_hours':12,'HE_CPU_wall_hours':4,'concurrent_GPUs':2},'all_terminal':all(not any(k in j['state'] for k in ['RUNNING','PENDING','COMPLETING']) for j in jobs)}
(ROOT/'budget.json').write_text(json.dumps(x,indent=2));print(json.dumps(x,indent=2))
assert gpu<=12,'GPU budget exceeded'
assert cpu+5<=4*3600,'CPU HE budget exceeded'
