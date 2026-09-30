"""Single-array concurrency and cumulative requested budget barrier."""
import argparse, getpass, math, subprocess
from common_g13 import *
def main():
    p=argparse.ArgumentParser(); p.add_argument('phase',choices=['smoke','main','main_retry1']); a=p.parse_args(); verify_lock()
    q=subprocess.check_output(['squeue','-h','-u',getpass.getuser(),'-o','%i %j'],text=True)
    assert not any('g13-' in x for x in q.splitlines()), 'Existing G13 work must finish first: '+q
    path=ROOT/'submissions.json'; records=json.loads(path.read_text()) if path.exists() else []
    assert not any(x['phase']==a.phase for x in records),'No blind duplicate submissions; diagnose before retry'
    if a.phase=='smoke': seconds=1200; n=1
    else:
        sm=json.loads((ROOT/'smoke_test.json').read_text()); assert sm['passed']
        status=subprocess.check_output(['sacct','-X','-n','-P','-j',records[0]['job_id'],'-o','JobID,State'],text=True); assert 'COMPLETED' in status and 'RUNNING' not in status
        # Conservative measured estimate: ~12,000 16-world decoder batches/seed,
        # ~800 training updates, IO/base-load margin, factor 2 for diagnostics.
        raw=12000*max(sm['decode_16_seconds'])+800*max(sm['update_seconds'])+300
        seconds=min(6000 if a.phase=='main_retry1' else 7200,max(1800,math.ceil(2*raw/60)*60)); n=3
        dump(ROOT/'resource_plan.json',dict(smoke_job=records[0]['job_id'],measured_decode_seconds=max(sm['decode_16_seconds']),measured_update_seconds=max(sm['update_seconds']),estimated_seed_seconds=raw,main_seconds_per_seed=seconds,array_gpu_count=1,array_concurrency=2,requested_total_seconds=sum(x['requested_gpu_seconds'] for x in records)+seconds*n,limit_seconds=43200,account='cluster default (AccountingStorageEnforce=none; no user association returned)',qos='cluster default',partition='B300q',exclude='node01 follows successful G12 environment',no_CUDA_VISIBLE_DEVICES_override=True))
    requested=sum(x['requested_gpu_seconds'] for x in records)+seconds*n; assert requested<=43200
    cmd=['sbatch','--parsable','--partition=B300q','--exclude=node01',f'--time={seconds//3600:02d}:{seconds%3600//60:02d}:00',f'--export=ALL,G13_PHASE={a.phase},G13_WALL_SECONDS={seconds-90}']
    if a.phase!='smoke': cmd+=['--array=0-2%2']
    cmd+=['experiments/g13_source_overfit_audit_v1/scripts/run_seed.sbatch']
    job=subprocess.check_output(cmd,cwd=REPO,text=True).strip().split(';')[0]
    records.append(dict(phase=a.phase,job_id=job,command=cmd,requested_gpu_seconds=seconds*n,count=n,seconds_per_allocation=seconds)); dump(path,records)
    with (ROOT/'commands.log').open('a') as f: f.write(' '.join(cmd)+' # JobID '+job+'\n')
    print(job,flush=True)
if __name__=='__main__': main()
