"""Additional structure controls/final CPU report under the global project lock."""
import argparse,fcntl,subprocess,os
from common import *

def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['linguistic_controls','finalize']);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);ledger=read(ROOT/'submissions.json');prior=[r for r in ledger if r['phase']==args.phase]
        if prior and not args.resume:print(json.dumps(dict(already_submitted=prior)));return
        if prior:
            active=subprocess.check_output(['squeue','-h','-j',','.join(r['job_id'] for r in prior),'-o','%i'],text=True).strip();assert not active,'Existing phase still active'
        if args.phase=='linguistic_controls':
            tasks=[dict(index=i,model=m,domain=d,study='space_relation_confirmation_v1' if d=='space' else 'four_domain_state_coverage_v1') for i,(m,d) in enumerate((m,d) for m in MODELS for d in DOMAINS)]
            if (ROOT/'linguistic_tasks.json').exists():assert tasks==read(ROOT/'linguistic_tasks.json')
            else:dump(ROOT/'linguistic_tasks.json',tasks)
            if not (ROOT/'linguistic_lock.json').exists():dump(ROOT/'linguistic_lock.json',dict(files=[dict(path=p,sha256=digest(ROOT/p)) for p in ['LINGUISTIC_CONTROLS_PLAN.md','linguistic_controls.py','linguistic_worker.py','linguistic_controls.slurm','linguistic_tasks.json']]))
            indices=[t['index'] for t in tasks if not (ROOT.parent/t['study']/'language_controls'/f"{t['model']}_{t['domain']}"/'complete.json').exists()];script='linguistic_controls.slurm';gpu=True
            if not indices:print('All structure controls complete');return
        else:indices=[0];script='finalize.slurm';gpu=False
        raw=subprocess.check_output(['squeue','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%b|%Z'],text=True);deps=[]
        for line in raw.splitlines():
            jid,name,gres,cwd=line.split('|',3)
            if cwd.startswith(str(ORIGINAL)) or name.startswith(('g1','fdsc','reference-frame','encrypted')):deps.append(jid.split('_')[0])
        name='fdsc-'+args.phase+'-v1';assert not any('|'+name+'|' in l for l in raw.splitlines()),'Orphan allocation'
        cmd=['sbatch','--parsable','--partition=B300q','--job-name='+name]
        if gpu:cmd+=['--array='+','.join(map(str,indices))+'%2']
        if deps:cmd+=['--dependency=afterany:'+':'.join(sorted(set(deps)))]
        cmd+=['experiments/four_domain_state_coverage_v1/'+script];intent=dict(phase=args.phase,indices=indices,command=cmd,pre_squeue=raw,one_gpu_per_task=gpu,max_array_tasks=2 if gpu else 1)
        dump(ROOT/f'submission_intent_{args.phase}.json',intent);jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0];ledger.append(dict(**intent,job_id=jid));dump(ROOT/'submissions.json',ledger);print(json.dumps(dict(job_id=jid,phase=args.phase,one_gpu_per_task=gpu,indices=indices)))

if __name__=='__main__':main()
