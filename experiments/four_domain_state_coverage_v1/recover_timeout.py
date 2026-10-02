"""Requeue only a timed-out own array child while its parent still gates later phases."""
import argparse,fcntl,subprocess,datetime,shutil
from common import *

def main():
    parser=argparse.ArgumentParser();parser.add_argument('job_id');args=parser.parse_args();parent=args.job_id.split('_')[0];assert '_' in args.job_id
    with (ROOT/'submit.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);ledger=read(ROOT/'submissions.json');submission=next(r for r in ledger if r['job_id']==parent);assert submission['one_gpu_per_task']
        direct_dependents=[r['job_id'] for r in ledger if r.get('one_gpu_per_task') and any(args.job_id in c.split('=',1)[1].split(':')[1:] for c in r.get('command',[]) if c.startswith('--dependency='))]
        assert not direct_dependents,('A GPU phase depends on this specific child; requeue could invalidate the phase barrier. Use registered dependent recovery.',direct_dependents)
        queue=subprocess.check_output(['squeue','--array','-h','-u','zailong','-o','%i|%j|%T|%b|%Z'],text=True)
        active=[];other_running=[]
        for line in queue.splitlines():
            jid,name,state,gres,cwd=line.split('|',4)
            if jid==args.job_id:raise RuntimeError('This array child is already pending/running; no duplicate recovery')
            if jid.split('_')[0]==parent:active.append(line)
            if state=='RUNNING' and ('gpu' in gres) and (cwd.startswith(str(ORIGINAL)) or name.startswith(('g1','fdsc','reference-frame','encrypted'))) and jid.split('_')[0]!=parent:other_running.append(line)
        assert active and not other_running,'Parent already terminal or another project GPU phase active; use fresh dependent submission after phase termination'
        raw=subprocess.check_output(['sacct','--duplicates','-j',args.job_id,'--noheader','--parsable2','--format=JobID,State,Start,End,ElapsedRaw,AllocTRES,ExitCode'],text=True)
        records=[line.split('|') for line in raw.splitlines() if line.split('|')[0]==args.job_id];latest=max(records,key=lambda r:r[2]);assert latest[1]=='TIMEOUT',latest
        events=read(ROOT/'requeue_events.json') if (ROOT/'requeue_events.json').exists() else []
        attempt=(args.job_id,latest[2],latest[3]);assert not any(tuple(e['attempt'])==attempt for e in events),'This timeout already recovered';assert sum(e['job_id']==args.job_id for e in events)<3,'Three timeout recoveries exhausted; inspect stalled shard rather than retry forever'
        base=ROOT.parent/'space_relation_confirmation_v1' if submission['phase']=='space_confirmation' else ROOT
        archive=base/'logs'/'requeue_history'/f"{args.job_id}_{len(events)}";archive.mkdir(parents=True,exist_ok=True)
        for p in (base/'logs').glob('*'+args.job_id+'.*'):shutil.copyfile(p,archive/p.name)
        # Some job templates separate array parent/task with the same underscore;
        # the archive above retains previous stdout/stderr before requeue opens it.
        dump(archive/'accounting_before_requeue.json',dict(raw=raw,queue=queue,attempt=attempt))
        subprocess.run(['scontrol','requeue',args.job_id],check=True)
        events.append(dict(job_id=args.job_id,attempt=attempt,phase=submission['phase'],accounting_before=raw,logs_archive=str(archive),at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='actual TIMEOUT; same array%2 and immutable sources/checkpoints; only missing shards/remaining updates',new_submission=False,gpu_request_per_attempt=1));dump(ROOT/'requeue_events.json',events)
        print(json.dumps(dict(requeued=args.job_id,parent=parent,preserves_array_limit=2,previous_elapsed_seconds=int(latest[4]))))

if __name__=='__main__':main()
