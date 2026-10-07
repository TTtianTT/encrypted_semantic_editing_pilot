"""Reproduce failed backend acceptance only; no downstream mechanism analysis."""
import torch
from .common import *
from .engine import render,hooks

@torch.no_grad()
def run(eng,folder):
    w=next(w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='train')
    h,m=eng.encode([render(w,0)]);y=eng.labels([render(w,0)])
    reference=eng.logits(h,m,y);ids=eng.ids(h,m)
    baseline=eng.logits(h,m,y);noise=float((baseline-reference).abs().max())
    eng.model.set_attn_implementation('eager');new=eng.logits(h,m,y);newids=eng.ids(h,m)
    delta=(new-reference).abs();flat=delta.flatten();worst=int(flat.argmax());vocab=delta.shape[-1]
    error=float(delta.max());passed=error<=3e-5 and torch.equal(ids,newids)
    r=dict(passed=passed,status='COMPLETED' if passed else 'BLOCKED_BACKEND_PARITY',worlds=1,world_id=w['world_id'],split='train',reference_backend='sdpa',candidate_backend='eager',dtype=str(h.dtype),repeat_noise_max=noise,logit_max_error=error,logit_mean_error=float(delta.mean()),logit_quantiles={str(q):float(torch.quantile(flat,q)) for q in [.5,.9,.95,.99]},tolerance=3e-5,unchanged_tolerance=True,greedy_tokens_equal=torch.equal(ids,newids),reference_ids=ids[0].tolist(),candidate_ids=newids[0].tolist(),worst_position=worst//vocab,worst_vocab_id=worst%vocab,reference_value=float(reference.flatten()[worst]),candidate_value=float(new.flatten()[worst]),after_failed_S1=True,downstream_analysis=False,test_accessed=0,resources=eng.resources())
    dump(folder/'PARITY_DIAGNOSTIC.json',r)
    torch.save(dict(reference=reference.cpu(),candidate=new.cpu(),labels=y.cpu()),folder/'parity_logits.pt')
    return r
