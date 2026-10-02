"""Slurm-only descriptive identity probes over immutable existing source caches."""
import os,argparse
import torch
import torch.nn.functional as F
from common import *
from semantics import NAMES,OBJECTS,states

def labels(r,w):
    d=w['domain'];a,b,c=w['people'];s=r['state']
    out=dict(current_state=states(d).index(s),target_object=OBJECTS.index(w['object']))
    if d=='space':out.update(target_subject=NAMES.index(a),anchor_owner=NAMES.index(a))
    if d=='emotion':out.update(target_subject=NAMES.index(w['focus']),scope_owner=NAMES.index(w['focus']),non_target_subject=NAMES.index(b if w['focus']==a else a))
    if d=='person':out.update(target_subject=NAMES.index(a),anchor_owner=NAMES.index(w['people'][s]),listener_identity=NAMES.index(w['people'][(s+1)%3]),agent_identity=NAMES.index(a),patient_identity=NAMES.index(b),owner_identity=NAMES.index(c))
    return out

def load(path):
    manifest=read(path.with_suffix('.json'));assert manifest['cache_sha']==digest(path)
    return torch.load(path,map_location='cpu',weights_only=False)

def features(cache,worlds):
    xs=[];ys=[]
    for r in cache:
        m=r['mask'].float();xs.append((r['hidden'].float()*m[:,None]).sum(0)/m.sum());ys.append(labels(r,worlds[r['world_id']]))
    return torch.stack(xs).cuda(),ys

def main():
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'Probe GPU must use Slurm+srun'
    torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    arg=argparse.ArgumentParser();arg.add_argument('--index',type=int,required=True);args=arg.parse_args();task=read(ROOT/'identity_probe_tasks.json')[args.index]
    base=ROOT.parent/task['study'];run=f"{task['model']}_{task['domain']}_s{task['seed']}";pub=base/'runs/formal'/run;dest=pub/'identity_probe';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():return
    status=read(pub/'complete.json') if (pub/'complete.json').exists() else {}
    if status.get('status') not in ('completed','source_training_infeasible'):
        dump(dest/'complete.json',dict(task=task,status='not_executed_not_admitted_or_behavior_incomplete',behavior_status=status.get('status')));return
    local=base/'local/formal'/run;trainpath=local/'probe/P_train.pt'
    if not trainpath.exists():dump(dest/'complete.json',dict(task=task,status='not_executed_no_all_state_probe_cache'));return
    ws={w['world_id']:w for w in rows(base/f"data/{task['domain']}/worlds.jsonl")};tr=load(trainpath);x,y=features(tr,ws);mean=x.mean(0);scale=x.std(0).clamp_min(.01);x=(x-mean)/scale
    caches={source:load(local/f'sources/{source}_test_t0.pt') for source in ('P','Q','U')}
    test={source:features(cache,ws) for source,cache in caches.items()};metrics=[];predictions=[]
    for variable in y[0]:
        classes=len(states(task['domain'])) if variable=='current_state' else len(OBJECTS) if variable=='target_object' else len(NAMES)
        target=torch.tensor([v[variable] for v in y],device='cuda');torch.manual_seed(20261002);model=torch.nn.Linear(x.shape[1],classes).cuda();opt=torch.optim.AdamW(model.parameters(),lr=.01,weight_decay=.01)
        for _ in range(100):
            opt.zero_grad();loss=F.cross_entropy(model(x),target);loss.backward();opt.step()
        with torch.no_grad():
            fit=model(x).argmax(1);fit_rate=float((fit==target).float().mean())
            for source,(tx,ty) in test.items():
                pred=model((tx-mean)/scale).argmax(1);target_test=torch.tensor([v[variable] for v in ty],device='cuda');ok=pred==target_test;cache=caches[source];eligible=torch.tensor([r['current_score']['success'] for r in cache],device='cuda')
                metrics.append(dict(training_source='P',test_source=source,variable=variable,n=len(cache),accuracy=float(ok.float().mean()),current_correct_n=int(eligible.sum()),current_correct_accuracy=float(ok[eligible].float().mean()) if eligible.any() else None,train_accuracy=fit_rate,train_classes=sorted(set(v[variable] for v in y)),classes=classes))
                predictions.extend(dict(training_source='P',test_source=source,variable=variable,world_id=r['world_id'],state=r['state'],current_correct=r['current_score']['success'],label=int(label),prediction=int(p),correct=bool(a)) for r,label,p,a in zip(cache,target_test,pred,ok))
    jsonl(dest/'predictions.jsonl',predictions);dump(dest/'metrics.json',metrics)
    dump(dest/'complete.json',dict(task=task,status='completed',job_id=os.environ['SLURM_JOB_ID'],step_id=os.environ['SLURM_STEP_ID'],gpu=torch.cuda.get_device_name(),visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),plan_sha=digest(ROOT/'MECHANISM_EXTENSION_PLAN.md'),cache_files=[dict(path=str(p),sha256=digest(p)) for p in [trainpath]+[local/f'sources/{s}_test_t0.pt' for s in caches]],limitations=['linear readout does not establish editor use','time core anchor-owner label is constant and not fitted','no quote-versus-external-anchor probe labels available','fit/test representations are edited sources; no new natural encoding performed']))

if __name__=='__main__':main()
