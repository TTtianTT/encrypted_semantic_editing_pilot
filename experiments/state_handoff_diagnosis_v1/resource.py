"""Allocation-level accounting and a single guarded submitter; CPU safe."""
import re
from .common import *
TERMINAL={'COMPLETED','FAILED','CANCELLED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL','DEADLINE','REVOKED'}
LEDGER=PUBLIC/'results/job_ledger.json'
def gpu_count(tres):
    m=re.search(r'(?:^|,)gres/gpu=(\d+)',tres)
    return int(m[1]) if m else 0
def allocation_rows(raw):
    out=[]
    for line in raw.splitlines():
        f=line.split('|')
        if len(f)<9 or '.' in f[0]:continue
        jid,aid,state,ec,elapsed,tres,start,end,limit=f[:9]
        out.append(dict(job_id=jid,array_task_id=aid,state=state.split()[0].split('+')[0],exit_code=ec,elapsed_seconds=int(elapsed or 0),gpus=gpu_count(tres),start=start,end=end,limit_minutes=int(limit or 0)))
    return out
def summarize(allocations):
    hours=sum(r['gpus']*r['elapsed_seconds']/3600 for r in allocations);events=[]
    for r in allocations:
        if r['gpus'] and r['start'] not in ('Unknown','None',''):
            events.append((r['start'],r['gpus']))
            if r['end'] not in ('Unknown','None',''):events.append((r['end'],-r['gpus']))
    current=peak=0
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):current+=delta;peak=max(current,peak)
    return hours,peak
def queue():return cmd(['squeue','-r','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%b|%T']).splitlines()
def refresh():
    ledger=read(LEDGER);alloc=[]
    for sub in ledger['submissions']:
        raw=cmd(['sacct','--duplicates','-j',sub['job_id'],'-n','-P','--format=JobIDRaw,JobID,State,ExitCode,ElapsedRaw,AllocTRES,Start,End,TimelimitRaw'])
        a=allocation_rows(raw);sub['allocations']=a;sub['terminal']=len(a)==len(sub['run_ids']) and all(r['state'] in TERMINAL for r in a);alloc+=a
    ledger['gpu_hours'],ledger['maximum_concurrent_gpus']=summarize(alloc)
    ledger['updated_at']=now();ledger.setdefault('queue_samples',[]).append(dict(time=now(),rows=queue()))
    dump(LEDGER,ledger);return ledger
def eligible(ledger,n,hours,other):
    if n<1:raise ValueError('Empty manifest')
    if any(not s['terminal'] for s in ledger['submissions']):raise RuntimeError('Active or unconfirmed array remains')
    if other:raise RuntimeError('Existing GPU jobs: conservatively wait, no cancellation: '+str(other))
    if ledger['gpu_hours']+n*hours>16:raise RuntimeError('16 GPU-hour conservative reservation exceeded')
def runtime_check(package,task):
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID') and os.environ.get('SLURM_ARRAY_TASK_ID') is not None
    import torch
    assert torch.cuda.device_count()==1
    with lock('global-GPU'):
        ledger=read(LEDGER);parent=os.environ['SLURM_ARRAY_JOB_ID']
        assert any(s['job_id']==parent and task['run_id'] in s['run_ids'] for s in ledger['submissions']),'Unregistered allocation'
        q=queue();count=sum(int(n) for line in q if line.endswith('|RUNNING') for n in re.findall(r'gpu(?::[^,:()]+)*:(\d+)',line))
        assert count<=2,('Account GPU concurrency exceeds2',q)
        ledger.setdefault('runtime_events',[]).append(dict(time=now(),job_id=os.environ['SLURM_JOB_ID'],run_id=task['run_id'],gpu_count=1,visible=os.environ.get('CUDA_VISIBLE_DEVICES'),account_GPU_count=count))
        dump(LEDGER,ledger)
