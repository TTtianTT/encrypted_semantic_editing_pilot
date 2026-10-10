"""Prospective objective comparison, reusing frozen canonical caches."""
import json, sys, time, hashlib, os
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
import numpy as np
import torch
ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / 'canonical_write_reachability_v1'
sys.path.append(str(PRIOR))
import shared as old
V2 = old.V2
REPO = old.REPO
SEEDS = old.SEEDS
read, rows, sha, load = old.read, old.rows, old.sha, old.load
torch.set_num_threads(4)

def dump(name, value):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def write(name, values):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_suffix(p.suffix+'.tmp')
    with q.open('w') as f:
        for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    q.replace(p)
def save(name, value):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_suffix('.tmp');torch.save(value,q);q.replace(p)
def csvwrite(name, records):
    import csv
    if not records:return
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in records for k in r)),lineterminator='\n');w.writeheader();w.writerows(records)
def verify():
    p=read(ROOT/'protocol.json')
    for k,v in p['inputs'].items():assert sha(k)==v,k
    for k,v in p['sources'].items():assert sha(ROOT/k)==v,k
    return p
@lru_cache(None)
def canonical(split,t,s):return old.canonical(split,t,s)
def worlds(split):return rows(V2/f'{split}_worlds.jsonl')
def bases():return {s:load(V2/f'local/fit_s{s}.pt')['q'].cuda() for s in SEEDS}
def fits():return old.device(load(PRIOR/'local/rrr.pt'))
def rrr(h,m,fs,op):return old.apply_rrr(h,m,fs['iid_only',op,16])
def metrics(h,m,split,t,s,lo,hi,qs):
    ref=canonical(split,t,s)
    return old.residual_metrics(h,m,ref['h'][lo:hi].cuda(),ref['m'][lo:hi].cuda(),qs)
def batch(split,t,items):
    # items = (world index, source state, op); source and target padded independently.
    adv=old.semantics()[2];hs=[];ms=[];ys=[];yms=[];targets=[]
    for i,s,op in items:
        y=adv('time',s,op);a=canonical(split,t,s);b=canonical(split,t,y)
        hs.append(a['h'][i]);ms.append(a['m'][i]);ys.append(b['h'][i]);yms.append(b['m'][i]);targets.append(y)
    def stack(xs,mm):
        n=max(len(x) for x in xs)
        return torch.stack([torch.nn.functional.pad(x,(0,0,0,n-len(x))) for x in xs]).cuda(),torch.stack([torch.nn.functional.pad(m,(0,n-len(m))) for m in mm]).cuda()
    h,m=stack(hs,ms);y,ym=stack(ys,yms)
    return h,m,y,ym,targets
def aligned_error(h,m,y,ym):
    n=max(h.shape[1],y.shape[1]);h,m=old.pad(h,m,n);y,ym=old.pad(y,ym,n)
    assert torch.equal(m,ym),'L2 requires identical masks'
    return ((h-y).square()*m[...,None]).sum((1,2))/(m.sum(1)*h.shape[-1])
def transition_items(split,aligned=True):
    adv=old.semantics()[2];out={op:[] for op in ('plus','minus')}
    for s in range(-3,4):
        for op in out:
            try:y=adv('time',s,op)
            except ValueError:continue
            a,b=canonical(split,0,s),canonical(split,0,y)
            length=max(a['m'].shape[1],b['m'].shape[1]);_,am=old.pad(a['h'],a['m'],length);_,bm=old.pad(b['h'],b['m'],length)
            for i in range(len(a['h'])):
                if not aligned or torch.equal(am[i],bm[i]):out[op].append((i,s,op))
    return out
def new_editors(eng,seed,rrr_initial=False):
    from backend import editors
    ed=editors(eng.d,seed)
    if rrr_initial:
        fs=load(PRIOR/'local/rrr.pt')
        with torch.no_grad():
            for op in ('plus','minus'):
                f=fs['iid_only',op,16]
                # Balance the factors without altering their product or the bias.
                b=f['left'].double()@f['right'].double();u,s,vh=torch.linalg.svd(b,full_matrices=False)
                ed[op].v.weight.copy_((u[:,:16]*s[:16].sqrt()).T.float())
                ed[op].u.weight.copy_((s[:16].sqrt()[:,None]*vh[:16]).T.float())
                ed[op].b.copy_(f['bias'])
                got=ed[op].v.weight.T.cpu().double()@ed[op].u.weight.T.cpu().double()
                assert float((got-b).abs().max())<2e-6
    return ed
def load_new(eng,group,seed,step):
    ed=new_editors(eng,seed);c=load(ROOT/f'local/{group}_s{seed}_{step:04d}.pt');ed.load_state_dict(c['editor']);ed.eval();return ed
def cpu_state(ed):return {k:v.detach().cpu() for k,v in ed.state_dict().items()}
def logits(eng,h,m,texts):
    from transformers.modeling_outputs import BaseModelOutput
    labels=eng.labels(texts)
    out=eng.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=labels,use_cache=False).logits.float()
    return out,labels
def kl(teacher,student,labels):
    a=teacher.log_softmax(-1);b=student.log_softmax(-1);valid=labels!=-100
    return ((a.exp()*(a-b)).sum(-1)*valid).sum(1)/valid.sum(1)
def aggregate(records,keys,value):
    d=defaultdict(list)
    for r in records:d[tuple(r[k] for k in keys)].append(r)
    return [{**dict(zip(keys,k)),**value(v)} for k,v in sorted(d.items(),key=lambda z:str(z[0]))]
