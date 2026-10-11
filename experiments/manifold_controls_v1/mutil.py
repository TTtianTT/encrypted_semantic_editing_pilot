"""Frozen-backbone follow-up; every executable phase requires a Slurm step."""
import sys, os, json, time, random, itertools, gzip
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
CONF=ROOT.parent/'canonical_confirmation_v1'
sys.path.insert(0,str(CONF))
import futils as f
import torch
import numpy as np
old,c=f.old,f.c
read,rows,sha,load=f.read,f.rows,f.sha,f.load
SEEDS=(42,43,44)
def require_slurm():
 assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'Use sbatch + srun'
def dump(name,x):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def write(name,rs):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp')
 with q.open('w') as fo:
  for r in rs:fo.write(json.dumps(r,ensure_ascii=False)+'\n')
 q.replace(p)
def save(name,x):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.tmp');torch.save(x,q);q.replace(p)
def verify():
 require_slurm();p=read(ROOT/'protocol.json')
 for k,v in p['sources'].items():assert sha(ROOT/k)==v,k
 for k,v in p['inputs'].items():assert sha(k)==v,k
 return p
def ws(domain,split):
 if split=='train':return f.ws(domain,'train')
 if domain=='time' and split=='dev':return c.worlds('eval')[:32]
 return rows(ROOT/f'data/{domain}_{split}.jsonl')
@lru_cache(None)
def cache(domain,split,t,s):
 if split=='train':return f.cache(domain,split,t,s)
 if domain=='time' and split=='dev':
  a=c.canonical('eval',t,s);return dict(h=a['h'][:32],m=a['m'][:32])
 return load(ROOT/f'local/{domain}_{split}_t{t}_s{s}.pt')
def batch(domain,split,t,part):
 adv=old.semantics()[2];hh=[];mm=[];yy=[];ym=[];ts=[]
 for i,s,op in part:
  y=adv(domain,s,op);a,b=cache(domain,split,t,s),cache(domain,split,t,y);hh.append(a['h'][i]);mm.append(a['m'][i]);yy.append(b['h'][i]);ym.append(b['m'][i]);ts.append(y)
 def stack(hs,ms):
  n=max(len(x) for x in hs);return torch.stack([torch.nn.functional.pad(x,(0,0,0,n-len(x))) for x in hs]).cuda(),torch.stack([torch.nn.functional.pad(x,(0,n-len(x))) for x in ms]).cuda()
 h,m=stack(hh,mm);y,ym=stack(yy,ym);return h,m,y,ym,ts
def items(domain,split,aligned=False):
 adv=old.semantics()[2];out={o:[] for o in ('plus','minus')}
 for s in old.semantics()[3](domain):
  for op in out:
   try:y=adv(domain,s,op)
   except ValueError:continue
   a,b=cache(domain,split,0,s),cache(domain,split,0,y);n=max(a['m'].shape[1],b['m'].shape[1]);_,am=old.pad(a['h'],a['m'],n);_,bm=old.pad(b['h'],b['m'],n)
   out[op].extend((i,s,op) for i in range(len(am)) if not aligned or torch.equal(am[i],bm[i]))
 return out
def paths(domain):
 return f.PATHS if domain=='time' else {'person_forward':dict(initial_state=1,operations=['plus','minus','plus','minus','plus']),'person_reverse':dict(initial_state=2,operations=['minus','plus','minus','plus','minus'])}
def residual(h,m,domain,split,t,s,lo,hi):
 a=cache(domain,split,t,s);q={seed:load(CONF/f'local/mechanism_S_s{seed}.pt')['q'].cuda() for seed in SEEDS} if domain=='time' else {}
 return old.residual_metrics(h,m,a['h'][lo:hi].cuda(),a['m'][lo:hi].cuda(),q)
def run_eval(eng,ed,domain,split,label,templates=(0,),singles=True):
 """All denominators fixed before outcomes; shards allow exact resume."""
 ww=ws(domain,split);adv=old.semantics()[2]
 for t in templates:
  for name,sp in paths(domain).items():
   for lo in range(0,len(ww),16):
    file=f'results/shards/chain_{domain}_{split}_{label}_t{t}_{name}_{lo:03d}.jsonl'
    if (ROOT/file).exists():continue
    chunk=ww[lo:lo+16];hi=lo+len(chunk);s=sp['initial_state'];a=cache(domain,split,t,s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();ok=[True]*len(chunk);rr=[]
    for step,op in enumerate(sp['operations'],1):
     s=adv(domain,s,op)
     if ed is None:a=cache(domain,split,t,s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda()
     else:h=ed[op](h,m)
     out=old.evaluate(eng,h,m,chunk,s,t);ms=residual(h,m,domain,split,t,s,lo,hi)
     for j,w in enumerate(chunk):ok[j]=ok[j] and out[j]['score']['success'];rr.append(dict(domain=domain,split=split,label=label,template=t,path=name,world_id=w['world_id'],step=step,state=s,trajectory_success=ok[j],output=out[j],**ms[j]))
    write(file,rr)
  if singles:
   for s in old.semantics()[3](domain):
    for op in ('plus','minus'):
     try:y=adv(domain,s,op)
     except ValueError:continue
     for lo in range(0,len(ww),16):
      file=f'results/shards/single_{domain}_{split}_{label}_t{t}_s{s}_{op}_{lo:03d}.jsonl'
      if (ROOT/file).exists():continue
      chunk=ww[lo:lo+16];hi=lo+len(chunk);a=cache(domain,split,t,y if ed is None else s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda()
      if ed is not None:h=ed[op](h,m)
      out=old.evaluate(eng,h,m,chunk,y,t);ms=residual(h,m,domain,split,t,y,lo,hi)
      write(file,[dict(domain=domain,split=split,label=label,template=t,world_id=w['world_id'],source_state=s,target_state=y,operation=op,output=out[j],**ms[j]) for j,w in enumerate(chunk)])
  print('eval',domain,split,label,t,flush=True)

class RRR(torch.nn.Module):
 def __init__(self,fit):
  super().__init__();self.register_buffer('left',fit['left'].cuda());self.register_buffer('right',fit['right'].cuda());self.register_buffer('bias',fit['bias'].cuda())
 def forward(self,h,m):return h+(h@self.left@self.right+self.bias)*m[...,None]
def person_editor(rank):
 fits=load(ROOT/'local/person_fits.pt');return {op:RRR(fits[op,rank]) for op in ('plus','minus')}
def baseline_editor(eng,label):
 ed=c.new_editors(eng,int(label.rsplit('_s',1)[1]));ed.load_state_dict(load(ROOT/f'local/{label}.pt')['editor']);return ed.eval().requires_grad_(False)
