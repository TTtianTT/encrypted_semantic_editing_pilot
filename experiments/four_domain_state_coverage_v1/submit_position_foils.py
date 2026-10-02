"""Insert one globally capped diagnostic array before pending CPU finalization."""
import fcntl,subprocess,os
from common import *

def main():
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);ledger=read(ROOT/'submissions.json');previous=[r for r in ledger if r['phase']=='position_foils']
        if previous:print(json.dumps(dict(already_submitted=previous)));return
        tasks=[dict(index=i,model=m,domain=d,study='space_relation_confirmation_v1' if d=='space' else 'four_domain_state_coverage_v1') for i,(m,d) in enumerate((m,d) for m in MODELS for d in DOMAINS)]
        dump(ROOT/'position_tasks.json',tasks)
        files=[ROOT/p for p in ('POSITION_FOILS_PLAN.md','position_spec.py','prepare_position_foils.py','position_worker.py','position_dispatch.py','position_foils.slurm','position_tasks.json')]
        for d in DOMAINS:
            base=ROOT.parent/'space_relation_confirmation_v1' if d=='space' else ROOT
            folder=base/'position_foils/data'/d;assert (folder/'manifest.json').exists(),'CPU fixture audit required'
            files+=list(sorted(folder.glob('*.jsonl')))+[folder/'manifest.json']
        dump(ROOT/'position_lock.json',dict(files=[dict(path=str(p),sha256=digest(p)) for p in files],no_training=True,registered_after_initial_formal=True))
        raw=subprocess.check_output(['squeue','--array','-h','-u',os.environ.get('USER','zailong'),'-o','%i|%j|%T|%b|%Z'],text=True);entries=[s.split('|',4) for s in raw.splitlines()];final=next(r for r in reversed(ledger) if r['phase']=='finalize');fj=final['job_id']
        assert any(r[0]==fj and r[2]=='PENDING' for r in entries),'CPU finalization must still be pending'
        deps=set()
        for jid,name,state,gres,cwd in entries:
            if jid==fj:continue
            if cwd.startswith(str(ORIGINAL)) or name.startswith(('g1','fdsc','reference-frame','encrypted')):deps.add(jid.split('_')[0])
        subprocess.run(['scontrol','hold',fj],check=True)
        cmd=['sbatch','--parsable','--partition=B300q','--job-name=fdsc-position-foils-v1','--array=0-7%2']
        if deps:cmd+=['--dependency=afterany:'+':'.join(sorted(deps))]
        cmd+=['experiments/four_domain_state_coverage_v1/position_foils.slurm'];dump(ROOT/'submission_intent_position_foils.json',dict(command=cmd,pre_squeue=raw))
        jid=subprocess.check_output(cmd,cwd=WORKTREE,text=True).strip().split(';')[0];ledger.append(dict(phase='position_foils',job_id=jid,indices=list(range(8)),command=cmd,pre_squeue=raw,one_gpu_per_task=True,max_array_tasks=2,protocol_sha=digest(ROOT/'position_lock.json')));dump(ROOT/'submissions.json',ledger)
        old=final.get('recovery_dependency') or next(c.split('=',1)[1] for c in final['command'] if c.startswith('--dependency='));fd=set(old.split(':')[1:]);fd.add(jid);dependency='afterany:'+':'.join(sorted(fd))
        subprocess.run(['scontrol','update','JobId='+fj,'Dependency='+dependency],check=True);final['position_dependency']=dependency;dump(ROOT/'submissions.json',ledger);subprocess.run(['scontrol','release',fj],check=True)
        print(json.dumps(dict(job_id=jid,max_concurrent_gpus=2,final_cpu_dependency_updated=fj)))

if __name__=='__main__':main()
