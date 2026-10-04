"""Reuse audited HF backend and parser without any backbone conversion."""
import contextlib
import sys
import torch
from transformers.modeling_outputs import BaseModelOutput
from .common import SOURCE, sha, ROOT, read
sys.path.insert(0,str(SOURCE))
from backend import Backend
from train import load_editor
from semantics import render, gold, advance, states
from evaluator import score

class Engine(Backend):
    def __init__(self,task):
        super().__init__(task['model'])
        assert sha(task['checkpoint'])==task['checkpoint_hash']
        self.ed=load_editor(self,task['checkpoint']); self.task=task

    @torch.no_grad()
    def ids(self,h,m):
        return self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**self.kw)

    @torch.no_grad()
    def evaluate(self,h,m,w,s,template):
        ids=self.ids(h,m); text=self.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
        ended=any(int(v) in self.eos for v in ids[0,1:])
        sc=score(text,gold(w,s,template),w,ended)
        return dict(text=text,token_ids=ids[0].cpu().tolist(),score=sc,success=bool(sc['success']),ended=ended)

    @torch.no_grad()
    def logits(self,h,m,text):
        labels=self.labels([text])
        return self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=labels,use_cache=False).logits.float(),labels

    @torch.no_grad()
    def confidence(self,h,m,text):
        logits,y=self.logits(h,m,text); lp=logits.log_softmax(-1); valid=y!=-100
        nll=-lp.gather(-1,y.clamp_min(0)[...,None]).squeeze(-1)[valid].mean()
        entropy=-(lp.exp()*lp).sum(-1)[valid].mean()
        return dict(token_mean_nll=float(nll),mean_entropy=float(entropy),key_margin=None,margin_status='NLL-only subset: relative-date candidates have variable multi-token lengths; no stable single-logit margin threshold')

@contextlib.contextmanager
def native_hook(module,hook,pre=False):
    handle=module.register_forward_pre_hook(hook) if pre else module.register_forward_hook(hook)
    try:yield
    finally:handle.remove()

def reconstruct(eng,w,history,template):
    h,m=eng.encode([render(w,history['start'],template)])
    for op in history['operations']: h=eng.ed[op](h,m)
    return h,m
