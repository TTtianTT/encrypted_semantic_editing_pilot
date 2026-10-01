"""CPU phased submission with no overlapping arrays, cumulative cap and measured sizing."""
import argparse,math,subprocess
from common_g16 import *
from selection import check_selection_lock

def complete(job):
    rows=subprocess.check_output(['sacct','-X','-n','-P','-j',job,'--format=State'],text=True).splitlines()
    assert rows and all(r.split('|')[0].strip()=='COMPLETED' for r in rows),rows

def resource_plan():
    smoke=json.loads((ROOT/'smoke_test.json').read_text());assert smoke['passed'] and smoke['U_never_loaded'] and smoke['new_confirmation_never_accessed']
    dev=smoke['full_dev_seconds'];flow=smoke['final_flow_848_seconds'];cache=smoke['cache128_seconds'];update=max(smoke['update_seconds']);factor=CFG['runtime_safety_factor']
    train=dict(full_dev18=18*dev,small_train10=10*dev*800/5760,updates400=400*update,cache640=5*cache,model_hash_IO_startup=120)
    confirm=dict(final4versions2splits=80*flow,cache320_plus2_producers=cache*2.5*8/6,model_hash_IO_startup=120)
    tr=math.ceil(sum(train.values())*factor/60)*60;co=math.ceil(sum(confirm.values())*factor/60)*60
    plan=dict(smoke_sha256=digest(ROOT/'smoke_test.json'),train_components_seconds=train,confirm_components_seconds=confirm,safety_factor=factor,train_wall_seconds=tr,confirm_wall_seconds=co,smoke_request_seconds=900,engineering_reserve_seconds=CFG['reserved_engineering_gpu_seconds'],planned_requested_seconds=900+3*tr+3*co,planned_plus_reserved_seconds=900+3*tr+3*co+CFG['reserved_engineering_gpu_seconds'],scientific_scale_unchanged=True,within_budget=900+3*tr+3*co+CFG['reserved_engineering_gpu_seconds']<=14400)
    if (ROOT/'resource_plan.json').exists():assert json.loads((ROOT/'resource_plan.json').read_text())==plan
    else:dump(ROOT/'resource_plan.json',plan)
    return plan

def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['smoke','train','confirm']);phase=parser.parse_args().phase
    verify_lock();assert json.loads((ROOT/'cpu_tests.json').read_text())['passed'] and json.loads((ROOT/'g15_audit.json').read_text())['passed']
    gate=ROOT/'submission.lock';fd=os.open(gate,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
    try:
        submitted=json.loads((ROOT/'submissions.json').read_text()) if (ROOT/'submissions.json').exists() else []
        assert not any(r['phase']==phase for r in submitted),'Duplicate phase refused'
        active=subprocess.check_output(['squeue','-h','-o','%i|%j|%T'],text=True)
        assert not any('g16-' in r for r in active.splitlines()),'Any active G16 allocation blocks another stage/array'
        if phase=='smoke':seconds=900;count=1
        else:
            complete(next(r['job_id'] for r in submitted if r['phase']=='smoke'));plan=resource_plan()
            assert plan['within_budget'],f'Full locked scale cannot fit requested4 GPU hours with reserve: {plan}; no resize or budget increase'
            seconds=plan['train_wall_seconds' if phase=='train' else 'confirm_wall_seconds'];count=3
        dependency=[]
        if phase=='confirm':
            check_selection_lock();trainjob=next(r['job_id'] for r in submitted if r['phase']=='train');complete(trainjob);dependency=['--dependency=afterok:'+trainjob]
        assert sum(r['requested_gpu_seconds'] for r in submitted)+count*seconds<=14400
        hours,rem=divmod(seconds,3600);minutes,secs=divmod(rem,60)
        cmd=['sbatch','--parsable',f'--time={hours:02d}:{minutes:02d}:{secs:02d}',f'--export=ALL,G16_WALL_SECONDS={seconds-60}']+dependency+[f'experiments/g16_capability_preserving_transfer_v1/scripts/{phase}.sbatch']
        job=subprocess.check_output(cmd,cwd=REPO,text=True).strip().split(';')[0]
        submitted.append(dict(phase=phase,job_id=job,command=cmd,count=count,wall_seconds=seconds,requested_gpu_seconds=count*seconds));dump(ROOT/'submissions.json',submitted)
        with (ROOT/'commands.log').open('a') as f:f.write(' '.join(cmd)+' -> '+job+'\n')
        print(job,flush=True)
    finally:gate.unlink()

if __name__=='__main__':main()
