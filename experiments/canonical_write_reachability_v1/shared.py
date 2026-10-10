"""Frozen-checkpoint reachability analysis; all fitting excludes evaluation worlds."""
import csv
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V2 = ROOT.parent / 'operator_residual_v2'
sys.path.append(str(V2))
import core as previous
torch.set_num_threads(4)
SEEDS = (42, 43, 44)

def read(p): return json.loads(Path(p).read_text())
def rows(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def stream(p):
    with Path(p).open() as f:
        for s in f:
            if s.strip(): yield json.loads(s)
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def dump(name, value):
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix+'.tmp'); q.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n'); q.replace(p)
def write(name, value):
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix+'.tmp')
    with q.open('w') as f:
        for r in value: f.write(json.dumps(r, ensure_ascii=False)+'\n')
    q.replace(p)
def csvwrite(name, values):
    if not values: return
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in values for k in r)), lineterminator='\n')
        w.writeheader(); w.writerows(values)
def save(name, value):
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix('.tmp'); torch.save(value, q); q.replace(p)
def load(p): return torch.load(p, map_location='cpu', weights_only=False)
def canonical(split, template, state): return load(ROOT/f'local/{split}_t{template}_s{state}.pt')
def pool(h,m): return previous.pool(h,m)
def project(x,q): return (x@q)@q.T
def device(x):
    if isinstance(x,dict): return {k:device(v) for k,v in x.items()}
    return x.cuda() if torch.is_tensor(x) else x
def verify():
    p=read(ROOT/'protocol.json')
    for k,v in p['inputs'].items(): assert sha(k)==v, k
    for k,v in p['sources'].items(): assert sha(ROOT/k)==v, k
    return p
def frozen_engine(): return previous.engine()
def semantics(): return previous.semantics()
def evaluate(eng,h,m,worlds,state,template): return previous.evaluate(eng,h,m,worlds,state,template)
def apply_rrr(h,m,fit):
    delta=h.float()@fit['left']@fit['right']+fit['bias']
    return h+delta*m[...,None]
def pad(h,m,length):
    if h.shape[1]<length:
        h=torch.nn.functional.pad(h,(0,0,0,length-h.shape[1])); m=torch.nn.functional.pad(m,(0,length-m.shape[1]))
    return h,m
def residual_metrics(h,m,ref,rm,bases):
    length=max(h.shape[1],ref.shape[1]);h,m=pad(h,m,length);ref,rm=pad(ref,rm,length)
    aligned=(m==rm).all(1);e=(h-ref)*m[...,None];n=m.sum(1).clamp_min(1)
    mse=e.square().sum((1,2))/(n*h.shape[-1]);norm=e.flatten(1).norm(dim=1)
    components={seed:project(e,q).square().sum((1,2))/(n*4) for seed,q in bases.items()}
    return [dict(aligned=bool(aligned[i]),token_mse=float(mse[i]) if aligned[i] else None,
                 residual_norm=float(norm[i]) if aligned[i] else None,
                 S_coordinate_mse={str(s):float(v[i]) for s,v in components.items()} if aligned[i] else None)
            for i in range(len(h))]
def rate(values):
    values=list(values); n=len(values);k=sum(values)
    return dict(n=n,k=k,rate=k/n if n else None,ci95=previous.binomial_ci(k,n))
def bootstrap_mean(values,seed=3101):
    x=np.asarray(values,float)
    if not len(x): return None
    rng=np.random.default_rng(seed);b=x[rng.integers(len(x),size=(2000,len(x)))].mean(1)
    return np.quantile(b,[.025,.975]).tolist()
