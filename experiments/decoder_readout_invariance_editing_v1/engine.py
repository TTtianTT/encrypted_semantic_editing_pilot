"""Snapshot-native backend; inference and differentiable memory paths explicit."""
import contextlib
import sys
import torch
from transformers.modeling_outputs import BaseModelOutput
from .common import ROOT, sha
sys.path.insert(0,str(ROOT/'native'))
from backend import Backend, editors
from train import load_editor
from semantics import render, gold, advance
from evaluator import score

@contextlib.contextmanager
def hooks(specs):
    handles=[]
    try:
        for module,fn,pre in specs:
            handles.append(module.register_forward_pre_hook(fn) if pre else module.register_forward_hook(fn))
        yield
    finally:
        for handle in handles:handle.remove()

def first(x):return x[0] if isinstance(x,tuple) else x
def replace(x,v):return (v,)+x[1:] if isinstance(x,tuple) else v

class Engine(Backend):
    def __init__(self,task):
        super().__init__(task['model']);self.task=task
        assert sha(task['checkpoint'])==task['checkpoint_hash']
        self.ed=load_editor(self,task['checkpoint'])
        for p in self.ed.parameters():p.requires_grad_(False)
        self.native_kw=dict(self.kw);self.kw=dict(self.kw,use_cache=False)
        self.kw.pop('cache_implementation',None)
        self.cross=[]
        for name,module in self.model.named_modules():
            if module.__class__.__name__ in ('BartAttention','T5GemmaCrossAttention') and ('encoder_attn' in name or 'cross_attn' in name) and hasattr(module,'k_proj'):
                self.cross.append((name,module))
        assert self.cross
        self.encoder_calls=0;self.decoder_forwards=0
        def encoder_counter(mod,args):self.encoder_calls+=1
        def decoder_counter(mod,args):self.decoder_forwards+=1
        self.encoder_counter_handle=self.model.get_encoder().register_forward_pre_hook(encoder_counter)
        self.decoder_counter_handle=self.model.register_forward_pre_hook(decoder_counter)

    @torch.no_grad()
    def ids(self,h,m,prefix=None,native=False):
        kw=dict(self.native_kw if native else self.kw)
        if prefix is not None:kw['decoder_input_ids']=prefix
        before=self.encoder_calls
        result=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**kw)
        assert self.encoder_calls==before,'Memory generation unexpectedly executed encoder'
        return result

    def logits_with_memory_grad(self,h,m,labels=None,decoder_ids=None):
        kw=dict(labels=labels) if labels is not None else dict(decoder_input_ids=decoder_ids)
        before=self.encoder_calls
        result=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,use_cache=False,**kw).logits.float()
        assert self.encoder_calls==before,'Memory logits unexpectedly executed encoder'
        return result

    def resources(self):
        return dict(super().resources(),encoder_calls=self.encoder_calls,decoder_forward_calls=self.decoder_forwards,SLURM_JOB_GPUS=__import__('os').environ.get('SLURM_JOB_GPUS'),SLURM_STEP_GPUS=__import__('os').environ.get('SLURM_STEP_GPUS'))

    @torch.no_grad()
    def logits(self,h,m,labels=None,decoder_ids=None):return self.logits_with_memory_grad(h,m,labels,decoder_ids)

    @torch.no_grad()
    def evaluate(self,h,m,w,s,template=0,prefix=None):
        ids=self.ids(h,m,prefix);tokens=ids[0].tolist()
        text=self.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
        ended=any(v in self.eos for v in tokens[1:])
        return dict(text=text,token_ids=tokens,ended=ended,score=score(text,gold(w,s,template),w,ended),gold_text=render(w,s,template))

    @torch.no_grad()
    def history(self,w,state=0,history='future_plus',template=0):
        start=state+(1 if history=='future_plus' else -1)
        h,m=self.encode([render(w,start,template)])
        return self.ed['plus' if history=='future_plus' else 'minus'](h,m),m

    @torch.no_grad()
    def projected(self,h):
        # Both audited native decoders read memory exclusively through these projections.
        return {(name,kind):getattr(module,kind+'_proj')(h).detach() for name,module in self.cross for kind in ('k','v')}

    def kv_hooks(self,projected,layers=None,k=True,v=True,head=None):
        specs=[]
        for name,module in self.cross:
            if layers is not None and name not in layers:continue
            for kind,enabled in [('k',k),('v',v)]:
                if not enabled:continue
                donor=projected[(name,kind)]
                def hook(mod,args,out,donor=donor,module=module):
                    if head is None:return donor.to(out)
                    result=out.clone();lo=head*module.head_dim;hi=lo+module.head_dim
                    result[...,lo:hi]=donor[...,lo:hi].to(out);return result
                specs.append((getattr(module,kind+'_proj'),hook,False))
        return hooks(specs)
