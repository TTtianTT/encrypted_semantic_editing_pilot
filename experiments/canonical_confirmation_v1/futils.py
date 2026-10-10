"""Explicitly separate exploratory controls, fresh confirmation and replication."""
import sys, os, json, time, random, hashlib
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
import numpy as np
import torch
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
EX=ROOT.parent/'canonical_objective_v1'
sys.path.append(str(EX))
import cutil as c
old=c.old
read,rows,sha,load=old.read,old.rows,old.sha,old.load
torch.set_num_threads(4)
SEEDS=(42,43,44,45,46)
CKS=[0,5,10,15,20,25,50]
PATHS=read(EX/'protocol.json')['paths']
def dump(name,x):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def write(name,x):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp')
 with q.open('w') as f:
  for r in x:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 q.replace(p)
def save(name,x):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.tmp');torch.save(x,q);q.replace(p)
def verify(name='protocol.json'):
 p=read(ROOT/name)
 for k,v in p['sources'].items():assert sha(ROOT/k)==v,k
 for k,v in p['inputs'].items():assert sha(k)==v,k
 return p
def ws(domain='time',split='eval'):
 return c.worlds('train') if domain=='time' and split=='train' else rows(ROOT/f'data/{domain}_{split}.jsonl')
@lru_cache(None)
def cache(domain,split,t,s):
 return c.canonical('train',t,s) if domain=='time' and split=='train' else load(ROOT/f'local/{domain}_{split}_t{t}_s{s}.pt')
def items(domain='time',split='train'):
 render,gold,advance,states,score=old.semantics();out={op:[] for op in ('plus','minus')}
 for s in states(domain):
  for op in out:
   try:y=advance(domain,s,op)
   except ValueError:continue
   a,b=cache(domain,split,0,s),cache(domain,split,0,y);n=max(a['m'].shape[1],b['m'].shape[1]);_,am=old.pad(a['h'],a['m'],n);_,bm=old.pad(b['h'],b['m'],n)
   out[op]+=[(i,s,op) for i in range(len(am)) if torch.equal(am[i],bm[i])]
 return out
def batch(domain,split,t,part):
 advance=old.semantics()[2];hh=[];mm=[];yy=[];ym=[];targets=[]
 for i,s,op in part:
  y=advance(domain,s,op);a,b=cache(domain,split,t,s),cache(domain,split,t,y);hh.append(a['h'][i]);mm.append(a['m'][i]);yy.append(b['h'][i]);ym.append(b['m'][i]);targets.append(y)
 def stack(xs,ms):
  n=max(len(x) for x in xs);return torch.stack([torch.nn.functional.pad(x,(0,0,0,n-len(x))) for x in xs]).cuda(),torch.stack([torch.nn.functional.pad(m,(0,n-len(m))) for m in ms]).cuda()
 h,m=stack(hh,mm);y,ym=stack(yy,ym);return h,m,y,ym,targets
def fits(domain):
 return {op:load(c.PRIOR/'local/rrr.pt')['iid_only',op,16] for op in ('plus','minus')} if domain=='time' else load(ROOT/'local/person_rrr.pt')
def new_ed(eng,seed,domain='time',rrr=False):
 if domain=='time':return c.new_editors(eng,seed,rrr)
 from backend import editors
 ed=editors(eng.d,seed)
 if rrr:
  with torch.no_grad():
   for op,f in fits(domain).items():
    b=f['left'].double()@f['right'].double();u,s,vh=torch.linalg.svd(b,full_matrices=False);ed[op].v.weight.copy_((u[:,:16]*s[:16].sqrt()).T.float());ed[op].u.weight.copy_((s[:16].sqrt()[:,None]*vh[:16]).T.float());ed[op].b.copy_(f['bias'])
 return ed
def model(eng,g,seed,step=600,domain='time'):
 ed=new_ed(eng,seed,domain,g=='RRR')
 if g not in ('RRR','reencode'):
  p=ROOT/f'local/{domain}_{g}_s{seed}_{step:04d}.pt'
  if not p.exists() and domain=='time' and seed<45 and g in ('C1','C3'):p=EX/f'local/{g}_s{seed}_{step:04d}.pt'
  ed.load_state_dict(load(p)['editor'])
 return ed.eval().requires_grad_(False)
def residual(h,m,domain,split,t,s,lo,hi,q):
 ref=cache(domain,split,t,s)
 return old.residual_metrics(h,m,ref['h'][lo:hi].cuda(),ref['m'][lo:hi].cuda(),q)
def qfit(ed,domain,only_pair=False):
 # PCA never observes evaluation worlds. Centering and eigengap reported.
 adv=old.semantics()[2];sumv=torch.zeros(768,dtype=torch.float64,device='cuda');cross=torch.zeros(768,768,dtype=torch.float64,device='cuda');n=0
 with torch.no_grad():
  for op,rs in items(domain).items():
   if only_pair:rs=[r for r in rs if r[1]==1 and op=='plus']
   for lo in range(0,len(rs),16):
    h,m,y,ym,_=batch(domain,'train',0,rs[lo:lo+16]);assert torch.equal(m,ym);e=(ed[op](h,m)-y)[m.bool()].double();sumv+=e.sum(0);cross+=e.T@e;n+=len(e)
 mean=sumv/n;cov=cross/n-mean[:,None]*mean[None,:];vals,vecs=torch.linalg.eigh(cov.cpu());vals=vals.flip(0).clamp_min(0);q=vecs[:,-4:].flip(1).float()
 return dict(q=q,mean=mean.cpu(),n=n,energy=float(cross.trace()/n/768),centered_energy=float(vals.sum()/768),top4_fraction=float(vals[:4].sum()/vals.sum()),eigengap4=float(vals[3]-vals[4]),relative_gap4=float((vals[3]-vals[4])/vals[3]),eigenvalues=vals.tolist(),world_ids=[w['world_id'] for w in ws(domain,'train')])
