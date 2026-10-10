"""Shared utilities for frozen-model attribution and reference-free projection."""
import csv
import hashlib
import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V1 = ROOT.parent / 'operator_residual_v1'
CES = REPO / '.causal-next-edit-worktree/experiments/causal_next_edit_stability_v1'
SOURCE = REPO / '.four-domain-worktree/experiments/four_domain_state_coverage_v1'
SEEDS = (42, 43, 44)
torch.set_num_threads(4)

def read(path): return json.loads(Path(path).read_text())
def rows(path): return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def dump(name, value):
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix + '.tmp'); q.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n'); q.replace(p)
def write(name, value):
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix + '.tmp'); q.write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in value)); q.replace(p)
def csvwrite(name, values):
    if not values: return
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in values for k in r))); w.writeheader(); w.writerows(values)
def save(name, value):
    p = ROOT / name; p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix('.tmp'); torch.save(value, q); q.replace(p)
def load(path): return torch.load(path, map_location='cpu', weights_only=False)
def pool(h, m): return (h.float()*m[...,None]).sum(-2)/m.sum(-1).clamp_min(1)[...,None]
def project(x, q): return (x@q)@q.T
def basis(weight):
    _,s,vh = torch.linalg.svd(weight.double(), full_matrices=False)
    rank = int((s>s.max()*max(weight.shape)*torch.finfo(torch.float64).eps).sum())
    return vh[:rank].T.float()
def random_basis(d, rank, seed, constraint=None, complement=False):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(d, rank, generator=g)
    if constraint is not None: x = x-project(x.T, constraint).T if complement else project(x.T, constraint).T
    return torch.linalg.qr(x, mode='reduced')[0]
def matched_random(residual, q, mask, norm):
    x = project(residual, q)*mask[...,None]
    n = x.flatten(1).norm(dim=1)
    assert (n>1e-9).all()
    return x*(norm/n)[:,None,None]
def task(seed): return next(r for r in read(CES/'configs/test_bart_tasks.json')['tasks'] if r['editor_seed']==seed)
def old_basis(seed): return load(CES/f'local/pca/bart_s{seed}.pt')['q'][:,:4]
def selections(seed):
    ids = read(ROOT/'protocol.json')['eval_world_ids']
    rs = [r for r in rows(CES/f'local/scan_bart/bart_s{seed}/pairs.jsonl') if r['world_id'] in ids and r['donor_source']=='N→E' and r['operation']=='plus']
    rs.sort(key=lambda r:r['world_id']); assert [r['world_id'] for r in rs]==ids
    return rs
def patch_pair_batch(rs):
    z = [load(r['state_path']) for r in rs]
    return tuple(torch.cat([x[k] for x in z]).cuda() for k in ('bad','good','mask'))
def auroc(y,x):
    from scipy.stats import rankdata
    y=np.asarray(y,dtype=bool)
    if not len(y) or y.all() or not y.any():return None
    a,b=int(y.sum()),int((~y).sum());return float((rankdata(x)[y].sum()-a*(a+1)/2)/(a*b))
def binomial_ci(k,n):
    # Wilson interval, per seed; no treating seeds or random directions as worlds.
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,float(center-half)),min(1,float(center+half))]
def verify_protocol():
    p=read(ROOT/'protocol.json');assert all(sha(k)==v for k,v in p['inputs'].items()),'Frozen input changed'
    return p

def engine():
    import os
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID')
    sys.path.insert(0,str(SOURCE))
    from backend import Backend
    from train import load_editor
    e=Backend('bart')
    return e, load_editor
def semantics():
    sys.path.insert(0,str(SOURCE))
    from semantics import render,gold,advance,states
    from evaluator import score
    return render,gold,advance,states,score
@torch.no_grad()
def evaluate(eng,h,m,worlds,state,template=0):
    render,gold,advance,states,score=semantics()
    states_arg=[state]*len(worlds) if isinstance(state,int) else state
    return [dict(**o,score=score(o['text'],gold(w,s,template),w,o['ended'])) for o,w,s in zip(eng.decode(h,m),worlds,states_arg)]
@torch.no_grad()
def logits(eng,h,m,texts):
    from transformers.modeling_outputs import BaseModelOutput
    labels=eng.labels(texts)
    out=eng.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=labels,use_cache=False).logits.float()
    return out,labels
def distribution(ref,changed,labels):
    a,b=ref.float().log_softmax(-1),changed.float().log_softmax(-1)
    pa,pb=a.exp(),b.exp();mix=torch.logaddexp(a,b)-np.log(2)
    valid=labels!=-100;n=valid.sum(1)
    kl=(pa*(a-b)).sum(-1);js=.5*((pa*(a-mix)).sum(-1)+(pb*(b-mix)).sum(-1))
    nll_a=-a.gather(-1,labels.clamp_min(0)[...,None]).squeeze(-1)
    nll_b=-b.gather(-1,labels.clamp_min(0)[...,None]).squeeze(-1)
    return [dict(KL=float((kl[i]*valid[i]).sum()/n[i]),JS=float((js[i]*valid[i]).sum()/n[i]),
                 token_KL=kl[i,valid[i]].cpu().tolist(),reference_nll=float((nll_a[i]*valid[i]).sum()/n[i]),changed_nll=float((nll_b[i]*valid[i]).sum()/n[i])) for i in range(len(ref))]
