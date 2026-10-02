import torch
import torch.nn.functional as F
from common import *
from semantics import gold,render,states,OBJECTS
from sources import source_cache
from train import load_editor

@torch.no_grad()
def features(cache,worlds):
    # Pooling is a small descriptive diagnostic, not a claim about where variables live.
    x=[];labels=[];meta=[]
    domain=next(iter(worlds.values()))['domain'];state_values=states(domain)
    for r in cache:
        m=r['mask'].float();x.append((r['hidden'].float()*m[:,None]).sum(0)/m.sum())
        w=worlds[r['world_id']];g=gold(w,r['state']);state=state_values.index(r['state'])
        binding=(w['people'].index(w['focus']) if domain=='emotion' else r['state'] if domain=='person' else 0)
        labels.append([state,binding,OBJECTS.index(w['object'])]);meta.append(dict(world_id=r['world_id'],state=r['state'],current_correct=r.get('current_score',{}).get('success',True)))
    return torch.stack(x).cuda(),torch.tensor(labels,device='cuda'),meta

def run_probe(eng,folder,published,worlds,index,test_sources):
    if (published/'probe.json').exists():return
    train_ws=[w for w in worlds.values() if w['split']=='train'][:24];d=train_ws[0]['domain']
    P=load_editor(eng,Path(index['P']['path']))
    edited=source_cache(eng,P,train_ws,states(d),0,folder/'probe/P_train.pt',Path(index['P']['path']))
    natural=[]
    for w in train_ws:
        for s in states(d):
            h,m=eng.cached([render(w,s)]);natural.append(dict(world_id=w['world_id'],state=s,hidden=h[0].cpu(),mask=m[0].cpu()))
    results=[];feature_archive=[]
    for training_source,cache in [('natural',natural),('P',edited)]:
        x,y,meta=features(cache,worlds);mean=x.mean(0);scale=x.std(0).clamp_min(.01);x=(x-mean)/scale
        for label,name in [(0,'current_state'),(1,'target_binding'),(2,'target_object')]:
            classes=len(OBJECTS) if label==2 else int(y[:,label].max())+1
            if classes<2:
                results.append(dict(training_source=training_source,variable=name,status='constant label; non-informative; not fitted'));continue
            torch.manual_seed(20261002);linear=torch.nn.Linear(eng.d,classes).cuda();opt=torch.optim.AdamW(linear.parameters(),lr=.01,weight_decay=.01)
            for _ in range(100):
                opt.zero_grad();loss=F.cross_entropy(linear(x),y[:,label]);loss.backward();opt.step()
            with torch.no_grad():
                for source,cache_test in test_sources.items():
                    tx,ty,tm=features(cache_test,worlds);pred=linear((tx-mean)/scale).argmax(1);correct=pred==ty[:,label]
                    results.append(dict(training_source=training_source,test_source=source,variable=name,n=len(tm),accuracy=float(correct.float().mean()),current_correct_accuracy=float(correct[torch.tensor([m['current_correct'] for m in tm],device='cuda')].float().mean()) if any(m['current_correct'] for m in tm) else None))
                    feature_archive.extend(dict(training_source=training_source,test_source=source,variable=name,**m,probe_prediction=int(p),label=int(l),correct=bool(ok)) for m,p,l,ok in zip(tm,pred,ty[:,label],correct))
    jsonl(published/'probe_per_world.jsonl',feature_archive);dump(published/'probe.json',dict(results=results,limitations=['masked mean linear probes are not evidence of editor use','time anchor is derived from E and relative state; no independent anchor-ownership label in core','scope/object and arbitrary participant names not fully probed','no intervention performed']))
