"""Single locked submission entry and allocation-only resource accounting."""
import argparse
import contextlib
import fcntl
import os
import re
import subprocess
from datetime import datetime
from .common import ROOT, WT, ORIGINAL, read, dump, sha, code_hash

LEDGER = ROOT / 'results/job_ledger.json'
LOCK = ORIGINAL / '.causal-next-edit-stability-v1.lock'
TERMINAL = {'COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT', 'OUT_OF_MEMORY', 'NODE_FAIL', 'PREEMPTED', 'BOOT_FAIL', 'DEADLINE', 'REVOKED'}

@contextlib.contextmanager
def locked():
    with LOCK.open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX); yield

def command(args): return subprocess.check_output(args, text=True).strip()
def gpu_count(tres):
    m = re.search(r'(?:^|,)gres/gpu=(\d+)', tres)
    return int(m[1]) if m else 0

def allocation_rows(raw):
    out=[]
    for line in raw.splitlines():
        fields=line.split('|')
        if len(fields) < 9 or '.' in fields[0]: continue
        jid, aid, state, ec, elapsed, tres, start, end, limit=fields[:9]
        out.append(dict(job_id=jid, array_id=aid, state=state.split()[0].split('+')[0], exit_code=ec,
                        elapsed_seconds=int(elapsed or 0), gpus=gpu_count(tres), start=start, end=end, limit_minutes=int(limit or 0)))
    return out

def summarize(allocs):
    hours=sum(r['gpus'] * r['elapsed_seconds'] / 3600 for r in allocs)
    events=[]
    for r in allocs:
        if r['gpus'] and r['start'] not in ('Unknown', 'None', '') and r['end'] not in ('Unknown', 'None', ''):
            events.extend([(r['start'], r['gpus']), (r['end'], -r['gpus'])])
    current=peak=0
    for _, delta in sorted(events, key=lambda x:(x[0], x[1])):
        current+=delta; peak=max(peak,current)
    return hours,peak

def refresh(ledger):
    allocations=[]
    for s in ledger['submissions']:
        raw=command(['sacct','--duplicates','-j',s['job_id'],'-n','-P','--format=JobIDRaw,JobID,State,ExitCode,ElapsedRaw,AllocTRES,Start,End,TimelimitRaw'])
        rs=allocation_rows(raw); s['allocations']=rs; allocations.extend(rs)
        s['terminal']=len(rs)==len(s['indices']) and all(r['state'] in TERMINAL for r in rs)
    ledger['gpu_hours'], ledger['maximum_concurrent_gpus']=summarize(allocations)
    ledger['updated_at']=datetime.now().isoformat()
    dump(LEDGER,ledger); return ledger

def eligible(ledger, n, hours):
    if n < 1: raise ValueError('Empty manifest')
    if any(not s.get('terminal') for s in ledger['submissions']): raise RuntimeError('Another experiment GPU phase remains active or unconfirmed')
    if ledger['gpu_hours'] + n*hours > 40: raise RuntimeError('40 allocated GPU-hour cap: conservative walltime reserve insufficient')

def runtime_check(config):
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID') and os.environ.get('SLURM_ARRAY_TASK_ID'), 'Must use sbatch array and srun'
    import torch
    assert torch.cuda.device_count()==config['gpus']==1
    with locked():
        ledger=read(LEDGER)
        parent=os.environ['SLURM_ARRAY_JOB_ID']
        assert any(s['job_id']==parent for s in ledger['submissions']), 'Unregistered GPU allocation'
        ledger.setdefault('runtime_events',[]).append(dict(event='worker_started', job_id=os.environ['SLURM_JOB_ID'],parent=parent,task=os.environ['SLURM_ARRAY_TASK_ID'],time=datetime.now().isoformat(),visible=os.environ.get('CUDA_VISIBLE_DEVICES')))
        dump(LEDGER,ledger)

def submit(config_path, manifest_path, resume=False):
    c=read(config_path); m=read(manifest_path)
    assert c['gpus']==1 and c['partition']=='B300q'
    assert m['code_hash']==code_hash() and m['config_hash']==sha(config_path)
    for gate in c.get('prerequisites',[]):
        marker=read(ROOT/gate['path'])
        if gate.get('passed_required'): assert marker['result']['passed'], 'Scientific prerequisite failed'
    for path,digest in c.get('input_hashes',{}).items(): assert sha(ROOT/path)==digest,'Locked stage input changed'
    with locked():
        ledger=refresh(read(LEDGER)) if LEDGER.exists() else dict(cap_gpu_hours=40, submissions=[],gpu_hours=0)
        indices=[]
        for i,t in enumerate(m['tasks']):
            p=ROOT/t['output_path']/'complete.json'
            if p.exists():
                marker=read(p); assert marker['task_hash']==t['task_hash']
                continue
            indices.append(i)
        eligible(ledger,len(indices),c['walltime_hours'])
        if not resume and any(s['stage']==c['stage'] for s in ledger['submissions']): raise RuntimeError('Use --resume for missing failed shards')
        user=os.environ.get('USER','zailong')
        q=command(['squeue','-r','-h','-u',user,'-o','%i|%j|%b|%T'])
        if any('cesv1-' in line for line in q.splitlines()): raise RuntimeError('Unclosed/unregistered experiment job detected')
        others=[line for line in q.splitlines() if 'gpu' in line]
        concurrency=1 if others else 2
        logs=ROOT/'local/logs'; logs.mkdir(parents=True,exist_ok=True)
        args=['sbatch','--parsable','--partition='+c['partition'],'--gres=gpu:1','--job-name=cesv1-'+c['stage'],
              '--array='+','.join(map(str,indices))+'%'+str(concurrency),'--time='+c['walltime'],
              '--output='+str(logs/'%A_%a.out'),'--error='+str(logs/'%A_%a.err'),
              str(ROOT/'slurm/worker.sbatch'),str(WT),str(ROOT/'slurm/slurm_env.sh'),str(config_path.resolve()),str(manifest_path.resolve())]
        intent=dict(stage=c['stage'],indices=indices,manifest=str(manifest_path),config=str(config_path),command=args,other_user_gpu_jobs=others,reserved_gpu_hours=len(indices)*c['walltime_hours'],time=datetime.now().isoformat())
        dump(ROOT/'results/submission_intent.json',intent)
        jid=command(args).split(';')[0]
        assert jid.isdigit(),jid
        ledger['submissions'].append(dict(**intent,job_id=jid,gpus_per_task=1,concurrency=concurrency,terminal=False))
        dump(LEDGER,ledger); print(jid,flush=True)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',type=lambda s:__import__('pathlib').Path(s));p.add_argument('--manifest',type=lambda s:__import__('pathlib').Path(s));p.add_argument('--resume',action='store_true');p.add_argument('--account',action='store_true');a=p.parse_args()
    if a.account:
        with locked(): print(refresh(read(LEDGER)))
    else: submit(a.config,a.manifest,a.resume)
if __name__=='__main__':main()
