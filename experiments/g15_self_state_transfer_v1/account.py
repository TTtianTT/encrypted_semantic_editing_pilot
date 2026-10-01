"""Allocation-only Slurm GPU hours and measured concurrent resources."""
import re, subprocess
from datetime import datetime
from common_g15 import *

def main():
    submissions=json.loads((ROOT/'submissions.json').read_text());ids=','.join(r['job_id'] for r in submissions)
    fields='JobIDRaw,JobID,State,ExitCode,Partition,Account,QOS,Timelimit,ReqTRES,NodeList,Submit,Start,End,ElapsedRaw,AllocTRES'
    raw=subprocess.check_output(['sacct','-X','-P','-j',ids,'--format='+fields],text=True);(ROOT/'allocation_details.psv').write_text(raw);rows=[];events=[]
    for r in csv.DictReader(raw.splitlines(),delimiter='|'):
        if '.' in r['JobID'] or r['Start'] in ('','Unknown'):continue
        match=re.search(r'(?:^|,)gres/gpu=(\d+)(?:,|$)',r['AllocTRES']);gpus=int(match[1]) if match else 0
        if not gpus:continue
        rows.append(dict(job_id=r['JobID'],raw_job_id=r['JobIDRaw'],state=r['State'],exit_code=r['ExitCode'],partition=r['Partition'],account=r['Account'],qos=r['QOS'],node=r['NodeList'],time_limit=r['Timelimit'],submit=r['Submit'],start=r['Start'],end=r['End'],gpus=gpus,elapsed_seconds=int(r['ElapsedRaw']),gpu_hours=int(r['ElapsedRaw'])*gpus/3600,requested_TRES=r['ReqTRES'],allocation_TRES=r['AllocTRES']))
        events.append((datetime.fromisoformat(r['Start']),gpus));events.append((datetime.fromisoformat(r['End']) if r['End'] not in ('','Unknown') else datetime.now(),-gpus))
    current=peak=0
    for _,change in sorted(events):current+=change;peak=max(peak,current)
    actual=sum(r['gpu_hours'] for r in rows);requested=sum(r['requested_gpu_seconds'] for r in submissions)/3600
    csvwrite(ROOT/'slurm_jobs.csv',rows);dump(ROOT/'budget.json',dict(limit_gpu_hours=4,actual_gpu_hours=actual,requested_gpu_hours=requested,max_concurrent_gpus=peak,allocation_only=True,steps_not_double_counted=True,within_limits=actual<=4 and requested<=4 and peak<=2))
    print('actual/requested GPU hours',actual,requested,'peak',peak)

if __name__=='__main__':main()
