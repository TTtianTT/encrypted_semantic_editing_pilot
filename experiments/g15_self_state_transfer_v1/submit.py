"""Submission barriers, measured resource sizing and cumulative request cap."""
import argparse, math, subprocess
from common_g15 import *

def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['smoke','main']);phase=parser.parse_args().phase
    verify_lock();assert json.loads((ROOT/'cpu_tests.json').read_text())['passed']
    submitted=json.loads((ROOT/'submissions.json').read_text()) if (ROOT/'submissions.json').exists() else []
    assert not any(r['phase']==phase for r in submitted),'Do not submit duplicates'
    active=subprocess.check_output(['squeue','-u',os.environ['USER'],'-h','-o','%i|%j|%T'],text=True)
    assert not any('g15' in line.lower() for line in active.splitlines()),'Existing G15 GPU allocation must finish'
    if phase=='smoke':seconds=CFG['smoke_wall_seconds'];count=1
    else:
        smoke=json.loads((ROOT/'smoke_test.json').read_text());assert smoke['passed'] and smoke['new_confirmation_never_accessed'] and smoke['U_never_loaded']
        smokeid=next(r['job_id'] for r in submitted if r['phase']=='smoke')
        status=subprocess.check_output(['sacct','-X','-n','-j',smokeid,'--format=State%30'],text=True).strip();assert status=='COMPLETED',status
        # Smoke atomic640 has40 complete16-instance batches, including encoder,
        # frozen-decoder CE/free decode, CPU state hashes and score serialization.
        per_batch=smoke['atomic_640_seconds']/40
        components=dict(final_atomic=smoke['atomic_640_seconds']*80,diagnostic_atomic=smoke['atomic_640_seconds']*30,other_final_and_diagnostic=(16640+4800)/16*per_batch,updates600=max(smoke['update_seconds'])*600,main_cache=smoke['cache16_seconds']*60,extra_heldout_cache=40*per_batch,engine_hash_IO_reserve=180)
        estimate=sum(components.values());seconds=max(900,int(math.ceil(estimate*1.2/60)*60));count=3
        dump(ROOT/'resource_plan.json',dict(smoke_job=smokeid,measured_atomic_batch_seconds=per_batch,measured_max_update_seconds=max(smoke['update_seconds']),components_seconds=components,seed_estimate_seconds=estimate,safety_multiplier=1.2,wall_seconds_per_seed=seconds,scientific_scale_unchanged=True))
    request=count*seconds;previous=sum(r['requested_gpu_seconds'] for r in submitted)
    assert previous+request<=14400,f'Measured workload cannot fit4 requested GPU hours: {previous+request}/14400; do not resize science or enlarge budget'
    hours,rem=divmod(seconds,3600);minutes,secs=divmod(rem,60)
    cmd=['sbatch','--parsable',f'--time={hours:02d}:{minutes:02d}:{secs:02d}',f'--export=ALL,G15_WALL_SECONDS={seconds-60}',f'experiments/g15_self_state_transfer_v1/scripts/{phase}.sbatch']
    job=subprocess.check_output(cmd,cwd=REPO,text=True).strip().split(';')[0]
    submitted.append(dict(phase=phase,job_id=job,command=cmd,count=count,wall_seconds=seconds,requested_gpu_seconds=request))
    dump(ROOT/'submissions.json',submitted)
    with (ROOT/'commands.log').open('a') as f:f.write(' '.join(cmd)+' -> '+job+'\n')
    print(job,flush=True)

if __name__=='__main__':main()
