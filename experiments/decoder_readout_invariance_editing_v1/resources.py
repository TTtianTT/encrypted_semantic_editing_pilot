"""Allocation-only accounting; no torch dependency."""
import re
from datetime import datetime
from .common import *

ACTIVE={'PENDING','RUNNING','COMPLETING','CONFIGURING','SUSPENDED','RESIZING','REQUEUED'}

def gpu_count(tres):
    match=re.search(r'(?:^|,)gres/gpu=(\d+)(?:,|$)',tres)
    return int(match[1]) if match else 0

def accounting(jobs):
    if not jobs:return dict(GPU_hours=0.,peak_concurrent_GPUs=0,allocations=[],all_terminal=True)
    raw=command('sacct','-j',','.join(jobs),'-X','-n','-P','-o','JobID%50,State,ElapsedRaw,AllocTRES%200,Start,End,ExitCode')
    allocations=[];events=[]
    for line in raw.splitlines():
        cols=line.split('|');jid,state,elapsed,tres,start,end,exitcode=cols[:7]
        # Parent summary without resources is not an allocation; never count steps.
        n=gpu_count(tres)
        if '.' in jid or n==0:continue
        seconds=int(elapsed or 0)
        a=dict(job_id=jid,state=state.split()[0],elapsed_seconds=seconds,GPUs=n,GPU_hours=n*seconds/3600,start=start,end=end,exit_code=exitcode)
        allocations.append(a)
        if start not in ('Unknown','None',''):
            events.append((start,n))
            if end not in ('Unknown','None',''):events.append((end,-n))
    current=peak=0
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):current+=delta;peak=max(peak,current)
    return dict(GPU_hours=sum(a['GPU_hours'] for a in allocations),peak_concurrent_GPUs=peak,allocations=allocations,all_terminal=bool(allocations) and all(a['state'] not in ACTIVE for a in allocations),sacct_raw=raw)
