"""One smoke then one seed array; measured walltime and cumulative request barrier."""
import argparse,getpass,math,subprocess
from common_g14 import *
def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['smoke','main']);a=p.parse_args();verify_lock()
    assert json.loads((ROOT/'cpu_tests.json').read_text())['passed']
    q=subprocess.check_output(['squeue','-h','-u',getpass.getuser(),'-o','%i %j'],text=True);assert not any('g14-' in x for x in q.splitlines()),'Active G14 work; no overlapping submissions'
    path=ROOT/'submissions.json';records=json.loads(path.read_text()) if path.exists() else []
    assert not any(r['phase']==a.phase for r in records),'No blind duplicate submissions'
    if a.phase=='smoke':seconds=CFG['smoke_seconds'];count=1
    else:
        sm=json.loads((ROOT/'smoke_test.json').read_text());assert sm['passed'] and sm['new_worlds']==0
        state=subprocess.check_output(['sacct','-X','-n','-P','-j',records[0]['job_id'],'-o','JobID,State'],text=True);assert 'COMPLETED' in state and 'RUNNING' not in state
        measured=sm['timing']['cache_seconds']+sm['timing']['receiver_evaluation_seconds'];estimate=measured*10+180
        seconds=max(900,math.ceil(1.75*estimate/60)*60);count=3
        dump(ROOT/'resource_plan.json',dict(smoke_job=records[0]['job_id'],smoke_32_world_pipeline_seconds=measured,estimated_320_world_seed_seconds=estimate,main_wall_seconds=seconds,safety_factor=1.75,max_request_hours=4,scientific_scale_unchanged=True))
    requested=sum(r['requested_gpu_seconds'] for r in records)+seconds*count;assert requested<=14400,'Budget insufficient; stop without shrinking science'
    script='smoke.sbatch' if a.phase=='smoke' else 'main.sbatch'
    cmd=['sbatch','--parsable',f'--time={seconds//3600:02d}:{seconds%3600//60:02d}:00',f'--export=ALL,G14_WALL_SECONDS={seconds-60}',str(ROOT.relative_to(REPO)/'scripts'/script)]
    job=subprocess.check_output(cmd,cwd=REPO,text=True).strip().split(';')[0]
    records.append(dict(phase=a.phase,job_id=job,command=cmd,count=count,wall_seconds=seconds,requested_gpu_seconds=seconds*count));dump(path,records)
    with (ROOT/'commands.log').open('a') as f:f.write(' '.join(cmd)+' # JobID '+job+'\n')
    print(job,flush=True)
if __name__=='__main__':main()
