"""Post-lock operational helper: resume a diagnosed final-evaluation timeout only."""
import subprocess
from common_g15 import *

def main():
    verify_lock()
    seed=43
    submissions=json.loads((ROOT/'submissions.json').read_text())
    assert not any(s['phase']=='engineering-final-eval-resume' for s in submissions)
    state=subprocess.check_output(['sacct','-X','-n','-j','2507_1','--format=State%30'],text=True).strip()
    assert state=='FAILED',state
    error=(ROOT/'logs/2507_1.err').read_text()
    assert "TimeoutError: Allocation budget stop" in error
    active=subprocess.check_output(['squeue','-h','-o','%i|%j|%T'],text=True)
    own=[r for r in active.splitlines() if 'g15' in r.lower()]
    assert len(own)<=1,own
    protected=[]
    for method in ['N','F','O']:
        meta=ROOT/f'training/{method}_s{seed}.json'
        z=json.loads(meta.read_text());checkpoint=ROOT/z['final_path']
        assert z['updates']==200 and digest(checkpoint)==z['final_sha256']
        protected += [meta,checkpoint,ROOT/f'training/{method}_s{seed}_steps.jsonl.gz',ROOT/f'training/{method}_s{seed}_curves.json']
    missing=[]
    for method in ['P','N','F','O']:
        for split in ['iid','template_ood']:
            p=ROOT/f'outputs/{method}_s{seed}_{split}.jsonl'
            if p.exists():protected.append(p)
            else:missing.append(str(p.relative_to(ROOT)))
    assert missing==['outputs/O_s43_template_ood.jsonl'],missing
    for tag in ['repair_train','repair_dev','confirm_iid','confirm_template_ood']:
        p=ROOT/f'data/{tag}_s43.json';z=json.loads(p.read_text())
        cache=Path(z['cache_path']);assert digest(cache)==z['cache_sha256']
        protected += [cache,p,ROOT/f'data/{tag}_s43_states.jsonl.gz']
    protected += [ROOT/'data/schedule_s43.jsonl',ROOT/'data/confirm_cohort_s43.json',ROOT/'logs/2507_1.out',ROOT/'logs/2507_1.err']
    before={str(p.relative_to(ROOT)):digest(p) for p in protected}
    seconds=900
    assert sum(s['requested_gpu_seconds'] for s in submissions)+seconds<=14400
    deviation=dict(phase='engineering-final-evaluation resume',seed=43,failed_job_id='2507_1',failed_raw_allocation_id='2509',reason='Internal Engine.check time protection interrupted final O/template_OOD atomic evaluation; all three training runs completed200 and seven confirmation shards saved.',scientific_config_data_schedule_code_changed=False,retraining=False,missing_shards=missing,requested_seconds=seconds,walltime_basis='Only one8480-record evaluation shard remains. Measured completed shards take about1–2minutes;900seconds includes model/cache loading and IO reserve.',protected_before_sha256=before,helper_added_after_scientific_lock=True)
    dump(ROOT/'resume_evaluation_audit.json',deviation)
    deviations=json.loads((ROOT/'engineering_deviations.json').read_text());deviations.append(deviation);dump(ROOT/'engineering_deviations.json',deviations)
    cmd=['sbatch','--parsable','--time=00:15:00','--export=ALL,G15_WALL_SECONDS=840,G15_RETRY_INDEX=1','experiments/g15_self_state_transfer_v1/scripts/resume_evaluation.sbatch']
    job=subprocess.check_output(cmd,cwd=REPO,text=True).strip().split(';')[0]
    submissions.append(dict(phase='engineering-final-eval-resume',job_id=job,command=cmd,count=1,seed=43,wall_seconds=seconds,requested_gpu_seconds=seconds))
    dump(ROOT/'submissions.json',submissions)
    with (ROOT/'commands.log').open('a') as f:f.write(' '.join(cmd)+' -> '+job+'\n')
    print(job,flush=True)

if __name__=='__main__':main()
