"""Two Slurm workers claim only missing TIMEOUT tasks after the original array ends."""
import fcntl,subprocess,os,datetime
from common import *

def claim():
    with (ROOT/'retry_claims.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);path=ROOT/'retry_claims.json';claims=read(path) if path.exists() else {}
        specs=read(ROOT/'retry_wave_tasks.json')
        for t in specs:
            name=f"{t['model']}_{t['domain']}_s{t['seed']}";key=str(t['index'])
            if (ROOT/'runs/formal'/name/'complete.json').exists() or key in claims:continue
            claims[key]=dict(task=t,status='running',job_id=os.environ['SLURM_JOB_ID'],step_id=os.environ['SLURM_STEP_ID'],at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(path,claims);return t
        return None

def main():
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID')
    parent=read(ROOT/'retry_wave_parent.json')['job_id']
    raw=subprocess.check_output(['sacct','-j',parent,'--parsable2','--noheader','--format=JobID,State'],text=True);state={r.split('|')[0]:r.split('|')[1] for r in raw.splitlines() if '.' not in r.split('|')[0]}
    while True:
        t=claim()
        if t is None:break
        key=str(t['index']);original=parent+'_'+key
        rc=subprocess.run([str(PYTHON),str(ROOT/'run.py'),'--phase','formal','--index',key]).returncode if state.get(original) in ('TIMEOUT','NODE_FAIL') else -1
        with (ROOT/'retry_claims.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);claims=read(ROOT/'retry_claims.json');claims[key].update(status='completed' if rc==0 else 'technical_failure_or_not_recoverable',returncode=rc,original_state=state.get(original));dump(ROOT/'retry_claims.json',claims)
        print(json.dumps(dict(task=t,returncode=rc)),flush=True)

if __name__=='__main__':main()
