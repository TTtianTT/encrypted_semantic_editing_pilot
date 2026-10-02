"""Allocation-only GPU ledger; Slurm child steps are not counted twice."""
import csv,subprocess,datetime,re
from common import *

def main():
    ledger=read(ROOT/'submissions.json');jobs=','.join(r['job_id'] for r in ledger)
    raw=subprocess.check_output(['sacct','--duplicates','--starttime=2026-10-02T00:00:00','-j',jobs,'--parsable2','--noheader','--format=JobIDRaw,JobID,State,ElapsedRaw,AllocTRES,ExitCode,Start,End,NodeList,ReqTRES,MaxRSS'],text=True)
    (ROOT/'slurm_accounting.psv').write_text(raw);allocations=[];events=[];hours=0
    for line in raw.splitlines():
        rr=line.split('|')
        if len(rr)<11 or '.' in rr[0] or '[' in rr[1]:continue
        gpu=re.search(r'(?:^|,)gres/gpu=(\d+)',rr[4]);count=int(gpu[1]) if gpu else 0
        row=dict(raw_id=rr[0],job_id=rr[1],state=rr[2],elapsed_seconds=int(rr[3]),alloc_tres=rr[4],exit_code=rr[5],start=rr[6],end=rr[7],nodes=rr[8],requested_tres=rr[9],max_rss=rr[10],gpu_count=count)
        hours+=count*row['elapsed_seconds']/3600;allocations.append(row)
        if count and rr[6] not in ('Unknown','None'):
            start=datetime.datetime.fromisoformat(rr[6]);end=datetime.datetime.fromisoformat(rr[7]) if rr[7] not in ('Unknown','None') else datetime.datetime.now() if rr[2] in ('RUNNING','COMPLETING','SUSPENDED') else start+datetime.timedelta(seconds=row['elapsed_seconds'])
            events.extend([(start,count),(end,-count)])
    total=peak=0
    for t,change in sorted(events,key=lambda x:(x[0],x[1])):total+=change;peak=max(peak,total)
    assert peak<=2,('Global project concurrency exceeded',peak)
    config=read(ROOT/'config.json');dump(ROOT/'budget.json',dict(actual_gpu_hours=hours,consumption_cap_gpu_hours=config['gpu_hour_cap'],max_concurrent_gpus=peak,allocations=allocations,allocation_only=True,within_gpu_hours=hours<=config['gpu_hour_cap'],job_ids=[r['job_id'] for r in ledger]))
    print(json.dumps(dict(gpu_hours=hours,max_concurrent_gpus=peak,states={r['job_id']:r['state'] for r in allocations})))

if __name__=='__main__':main()
