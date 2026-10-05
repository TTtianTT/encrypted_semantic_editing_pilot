"""Only GPU submission entry. Snapshot committed code before sbatch."""
import argparse
import io
import subprocess
import tarfile
from .common import *
from .resource import *

def submit(round_,walltime,resume=False):
    parts=[int(x) for x in walltime.split(':')];hours=parts[0]+parts[1]/60+parts[2]/3600
    with lock('global-GPU'):
        ledger=refresh();q=queue();other=[s for s in q if 'gpu' in s]
        registry=read(ROOT/'task_registry.json');candidates=[r for r in registry['runs'] if r['round']==round_]
        if not candidates:raise ValueError('prepare first')
        previous={'R01':['R00'],'R02':['R00','R01'],'R03':['R00','R01','R02']}.get(round_,[])
        for r in registry['runs']:
            if r['round'] in previous:
                receipt=ROOT/f'runs/{r["run_id"]}/receipt.json'
                assert receipt.exists() and read(receipt)['state']=='PUSH_VERIFIED',('Previous run not published',r['run_id'])
                conclusion=read(ROOT/f'runs/{r["run_id"]}/conclusion.json')
                assert conclusion['scientific_status']=='EXECUTED',('Previous compute/acceptance gate not passed',r['run_id'])
        tasks=[]
        for r in candidates:
            task=read(ROOT/r['manifest']);done=Path(task['output'])/'complete.json'
            if done.exists():
                assert read(done)['scientific_hash']==task['scientific_hash'];continue
            if any(r['run_id'] in s['run_ids'] for s in ledger['submissions']) and not resume:raise RuntimeError('Already attempted; --resume only for missing same-hash batches')
            tasks.append(task)
        eligible(ledger,len(tasks),hours,other)
        execution=cmd(['git','rev-parse','HEAD'],WT)
        # Every execution-relevant file must match its committed blob.
        for path in [ROOT/'protocol.yaml',ROOT/'world_manifest.jsonl',ROOT/'CHECKPOINTS.json']+list(ROOT.glob('*.py'))+list((ROOT/'manifests').glob('*.json'))+list((ROOT/'slurm').glob('*')):
            committed=subprocess.check_output(['git','show',execution+':'+str(path.relative_to(WT))],cwd=WT)
            assert hashlib.sha256(committed).hexdigest()==sha(path),('Commit code/config before running',path)
        snapshot=LOCAL/'snapshots'/execution
        if not (snapshot/'EXECUTION_COMMIT').exists():
            snapshot.mkdir(parents=True,exist_ok=True)
            archive=subprocess.check_output(['git','archive',execution],cwd=WT)
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(snapshot,filter='data')
            text(snapshot/'EXECUTION_COMMIT',execution+'\n')
            for p in snapshot.rglob('*'):
                if p.is_file():p.chmod(0o444)
        for t in tasks:t['execution_commit']=execution
        serial=len(ledger['submissions']);manifest=LOCAL/f'submissions/{round_}_attempt{serial}.json'
        package=dict(round=round_,tasks=tasks,execution_commit=execution,snapshot=str(snapshot),walltime=walltime,created_at=now());dump(manifest,package)
        logs=LOCAL/'logs';logs.mkdir(parents=True,exist_ok=True)
        args=['sbatch','--parsable','--partition=B300q','--gres=gpu:1','--qos=normal','--nodes=1','--ntasks=1','--cpus-per-task=4',f'--array=0-{len(tasks)-1}%2','--time='+walltime,'--job-name=handoff-'+round_,'--output='+str(logs/'%A_%a.out'),'--error='+str(logs/'%A_%a.err'),str(snapshot/'experiments/state_handoff_diagnosis_v1/slurm/worker.sbatch'),str(snapshot),str(PYTHON),str(manifest)]
        intent=dict(round=round_,run_ids=[t['run_id'] for t in tasks],manifest=str(manifest),manifest_hash=sha(manifest),execution_commit=execution,walltime=walltime,reserved_gpu_hours=len(tasks)*hours,command=args,created_at=now(),terminal=False)
        dump(LOCAL/f'submissions/intent{serial}.json',intent)
        jid=cmd(args).split(';')[0];assert jid.isdigit(),jid
        ledger['submissions'].append(dict(**intent,job_id=jid));dump(LEDGER,ledger)
        for r in registry['runs']:
            if r['run_id'] in intent['run_ids']:r['state']='SUBMITTED';r.setdefault('attempts',[]).append(dict(job_id=jid,execution_commit=execution,manifest=str(manifest)))
        dump(ROOT/'task_registry.json',registry);print(jid,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',required=True);p.add_argument('--walltime',default='00:15:00');p.add_argument('--resume',action='store_true');a=p.parse_args();submit(a.round,a.walltime,a.resume)
