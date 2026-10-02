"""CPU submit coordinator: one active phase, allocation GPU budget ≤2 hours."""
import argparse,fcntl,subprocess,math
from common_g17 import *
def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['smoke','main']);ap.add_argument('--engineering-retry',action='store_true');args=ap.parse_args();verify_lock()
    ROOT.mkdir(exist_ok=True)
    with (ROOT/'submission.lock').open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        records=json.loads((ROOT/'submissions.json').read_text()) if (ROOT/'submissions.json').exists() else []
        previous=[r for r in records if r['phase']==args.phase]
        if previous:
            assert args.engineering_retry and args.phase=='smoke','No duplicate phase submission'
            last=subprocess.check_output(['sacct','-X','-n','-P','-j',previous[-1]['job_id'],'--format=State,ExitCode'],text=True).strip()
            assert last.startswith('FAILED|') and (ROOT/'engineering_events.json').exists(),'Retry requires diagnosed failure'
        else:assert not args.engineering_retry
        active=subprocess.check_output(['squeue','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%T|%b'],text=True)
        assert not any('g17-' in line for line in active.splitlines()),'An active G17 allocation/array exists'
        (ROOT/'pre_submit_squeue.txt').write_text(active)
        if args.phase=='smoke':seconds=600;count=1
        else:
            smoke=json.loads((ROOT/'smoke_test.json').read_text());assert smoke['passed'] and json.loads((ROOT/'frozen_smoke.json').read_text())['passed']
            prior=[r for r in records if r['phase']=='smoke'];assert len(prior)>=1
            result=subprocess.check_output(['sacct','-X','-n','-P','-j',prior[-1]['job_id'],'--format=State,ExitCode'],text=True).strip();assert result=='COMPLETED|0:0'
            # 32 historyworlds × 1anchor measured; fixed320worlds ×4anchors extrapolated.
            timings=smoke['throughput'];measured=sum(z['cache_seconds']+z['total_seconds'] for z in timings)
            full=measured*(320*4)/(32*1);load=max(0,smoke['elapsed_seconds']-measured)
            seconds=int(math.ceil((full*CFG['runtime_safety_factor']+load+60)/60)*60);count=3
            requested=sum(r['requested_gpu_seconds'] for r in records)+seconds*3+CFG['reserve_gpu_seconds']
            plan=dict(smoke_measured_seconds=measured,model_load_hash_and_smoke_check_overhead_seconds=load,full_fixed_scale_extrapolated_seconds=full,safety_factor=CFG['runtime_safety_factor'],wall_seconds_per_seed=seconds,main_array_mapping=[dict(index=i,seed=s) for i,s in enumerate(CFG['seeds'])],engineering_reserve_seconds=600,planned_requested_gpu_seconds_including_reserve=requested,budget_seconds=7200,within_budget=requested<=7200)
            dump(ROOT/'resource_plan.json',plan);assert requested<=7200,'Fixed scientific scope cannot fit2GPUhour requested budget; no main submission'
        script=ROOT/f'scripts/{args.phase}.sbatch';cmd=['sbatch','--partition=B300q',f'--time={seconds//60:02d}:00',f'--export=ALL,RF_WALL_SECONDS={seconds-30}',str(script.relative_to(REPO))]
        assert sum(r['requested_gpu_seconds'] for r in records)+count*seconds<=7200
        result=subprocess.check_output(cmd,cwd=REPO,text=True).strip();job=result.split()[-1];assert job.isdigit();records.append(dict(phase=args.phase,job_id=job,command=cmd,wall_seconds=seconds,allocations=count,gpus_per_allocation=1,requested_gpu_seconds=count*seconds))
        dump(ROOT/'submissions.json',records)
        with (ROOT/'commands.log').open('a') as f:f.write(' '.join(cmd)+'\n'+result+'\n')
        print(result)
if __name__=='__main__':main()
