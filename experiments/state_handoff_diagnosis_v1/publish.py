"""Single CPU publisher. Ordinary push, SHA verification, failures preserved."""
import argparse
import subprocess
from .common import *

def push_verify(commit,runner=cmd):
    runner(['git','push','origin','HEAD:refs/heads/'+BRANCH],WT)
    remote=runner(['git','ls-remote','--heads','origin','refs/heads/'+BRANCH],WT).split()
    assert remote and remote[0]==commit,('Remote SHA mismatch',remote,commit)

def index_status():
    registry=read(ROOT/'task_registry.json');entries=[]
    for r in registry['runs']:
        p=ROOT/f'runs/{r["run_id"]}/receipt.json';receipt=read(p) if p.exists() else dict(state=r['state'])
        c=ROOT/f'runs/{r["run_id"]}/conclusion.json';conclusion=read(c) if c.exists() else None
        r['state']=receipt['state'];entries.append(dict(**r,receipt=receipt,scientific_status=conclusion['scientific_status'] if conclusion else 'PLANNED'))
    dump(ROOT/'task_registry.json',registry);jsonl(ROOT/'results/run_index.jsonl',entries)
    ledger=read(ROOT/'results/job_ledger.json')
    lines=['# Status','',f'累计allocationGPU-hours：{ledger["gpu_hours"]:.6f}/16；allocation事件重建峰值{ledger["maximum_concurrent_gpus"]}GPU。','','| Run | Publication | Scientific |','| --- | --- | --- |']
    lines += [f'| {e["run_id"]} | {e["state"]} | {e["scientific_status"]} |' for e in entries]
    text(ROOT/'STATUS.md','\n'.join(lines)+'\n')
    return entries

def stage_small():
    # Explicit experiment-only whitelist; never git add . or -A.
    files=[ROOT/'task_registry.json',ROOT/'STATUS.md']
    for d in ['runs','reports','results']:
        files += [p for p in (ROOT/d).rglob('*') if p.is_file() and (p.suffix in ('.json','.jsonl','.csv','.md','.gz'))]
    assert all(p.stat().st_size<20_000_000 for p in files),'Large artifact must stay external'
    relative=[str(p.relative_to(WT)) for p in files]
    cmd(['git','add','--',*relative],WT)
    staged=cmd(['git','diff','--cached','--name-only'],WT).splitlines()
    assert all(p.startswith('experiments/state_handoff_diagnosis_v1/') for p in staged),'Unexpected staged file'
    assert all(not p.endswith(('.pt','.key','.pem','.env')) for p in staged),'Forbidden artifact'
    return staged

def publish_run(run_id):
    p=ROOT/f'runs/{run_id}/receipt.json';receipt=read(p)
    if receipt['state']=='PUSH_VERIFIED':
        subprocess.check_call(['git','merge-base','--is-ancestor',receipt['published_sha'],'HEAD'],cwd=WT)
        return receipt
    c=read(ROOT/f'runs/{run_id}/conclusion.json')
    if receipt['state']=='LOCAL_COMMITTED_PUSH_PENDING':commit=receipt['local_commit']
    else:
        index_status();changed=stage_small()
        if not changed:raise RuntimeError('Unpublished result has no staged data')
        cmd(['git','commit','-m',f'results(handoff): {run_id} {c["scientific_status"]}'],WT)
        commit=cmd(['git','rev-parse','HEAD'],WT)
        receipt.update(state='LOCAL_COMMITTED_PUSH_PENDING',local_commit=commit);dump(p,receipt)
    try:push_verify(commit)
    except Exception as exc:
        receipt.update(state='LOCAL_COMMITTED_PUSH_PENDING',push_error=str(exc));dump(p,receipt)
        print(json.dumps(dict(run_id=run_id,status='LOCAL_COMMITTED_PUSH_PENDING',local_commit=commit,error=str(exc)),ensure_ascii=False),flush=True);raise
    receipt.update(state='PUSH_VERIFIED',published_sha=commit,verified_at=now());receipt.pop('push_error',None);dump(p,receipt)
    print(json.dumps(dict(run_id=run_id,status=c['scientific_status'],primary=c['primary'],worlds=c['completed_worlds'],GPU_hours=c['GPU_hours'],cumulative_GPU_hours=c['cumulative_GPU_hours'],report=f'experiments/state_handoff_diagnosis_v1/reports/{run_id}.md',published_sha=commit,remote_verified=True),ensure_ascii=False),flush=True)
    return receipt

def publish(round_):
    with lock('publisher'):
        registry=read(ROOT/'task_registry.json')
        for r in registry['runs']:
            if r['round']==round_ and (ROOT/f'runs/{r["run_id"]}/receipt.json').exists():publish_run(r['run_id'])
        entries=index_status();same=[e for e in entries if e['round']==round_]
        if same and all(e['state']=='PUSH_VERIFIED' for e in same):
            marker=LOCAL/f'publications/{round_}.json'
            if marker.exists():return
            from .summarize import summary_round
            summary_round(round_)
            stage_small();cmd(['git','commit','-m',f'results(handoff): {round_} round summary'],WT)
            commit=cmd(['git','rev-parse','HEAD'],WT);push_verify(commit)
            dump(marker,dict(published_sha=commit,remote_verified=True,time=now()))
            print(round_+' summary PUSH_VERIFIED '+commit,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',required=True);a=p.parse_args();publish(a.round)
