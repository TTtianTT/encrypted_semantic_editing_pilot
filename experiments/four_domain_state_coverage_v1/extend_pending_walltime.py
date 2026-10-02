"""Resource-only amendment to pending tasks after an evaluation timeout."""
import subprocess,fcntl,datetime
from common import *

def main():
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);dest=ROOT/'pending_walltime_amendment.json'
        if dest.exists():print(json.dumps(dict(already_applied=read(dest))));return
        ledger=read(ROOT/'submissions.json');eligible={r['job_id'] for r in ledger if r['phase'] in ('formal','symbol','space_confirmation','linguistic_controls')}
        raw=subprocess.check_output(['squeue','--array','-h','-u','zailong','-o','%i|%T|%j|%b|%Z'],text=True);changes=[]
        for line in raw.splitlines():
            jid,state,name,gres,cwd=line.split('|',4)
            if jid.split('_')[0] not in eligible or state!='PENDING':continue
            assert name.startswith('fdsc') and cwd.startswith(str(ORIGINAL)) and 'gpu:1' in gres
            before=subprocess.check_output(['scontrol','show','job',jid,'--oneliner'],text=True)
            result=subprocess.run(['scontrol','update','JobId='+jid,'TimeLimit=360'],text=True,capture_output=True)
            after=subprocess.check_output(['scontrol','show','job',jid,'--oneliner'],text=True)
            changes.append(dict(job_id=jid,before=before,after=after,returncode=result.returncode,stderr=result.stderr))
        record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Original time42 completed all training but exceeded2h during evaluation. Give not-yet-started jobs sufficient evaluation allocation; scientific updates/selection/data unchanged.',new_walltime_minutes=360,running_jobs_unchanged=True,queue_before=raw,changes=changes,official_command_reference='https://slurm.schedmd.com/scontrol.html',global_gpu_limit=2,gpu_hour_cap=48)
        dump(dest,record)
        for r in ledger:
            if r['job_id'] in eligible:r['pending_walltime_resource_amendment']=str(dest)
        dump(ROOT/'submissions.json',ledger);print(json.dumps(dict(updated=sum(r['returncode']==0 for r in changes),failed=sum(r['returncode']!=0 for r in changes),running_jobs_changed=0)))

if __name__=='__main__':main()
