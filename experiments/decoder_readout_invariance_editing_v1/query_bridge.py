"""Test upstream-query alignment using online donor queries at actual prefixes."""
import contextlib
import torch
from .common import *
from .engine import hooks
from .readout import pairs,distribution,token_sites

@contextlib.contextmanager
def online_query(eng,recipient,donor,mask,module):
    active={'donor':False,'query':None,'calls':0,'prefixes':[]}
    def before_model(model,args,kwargs):
        if active['donor']:return
        prefix=kwargs.get('decoder_input_ids')
        assert prefix is not None,'Only actual decoder_input_ids; no gold labels accepted'
        captured=[];active['donor']=True
        try:
            with hooks([(module.q_proj,lambda mod,args,out:captured.append(out.detach().clone()),False)]):eng.logits(donor,mask,decoder_ids=prefix)
        finally:active['donor']=False
        assert len(captured)==1;active['query']=captured[0];active['calls']+=1;active['prefixes'].append(prefix[0].tolist())
    def after_query(mod,args,out):
        if active['donor']:return
        assert active['query'] is not None and active['query'].shape==out.shape
        return active['query']
    handle=eng.model.register_forward_pre_hook(before_model,with_kwargs=True)
    try:
        with hooks([(module.q_proj,after_query,False)]):yield active
    finally:handle.remove()

@torch.no_grad()
def run(eng,folder):
    name=read(ROOT/'configs/S2_CANDIDATES.json')['candidate'];module=dict(eng.cross)[name]
    allworlds=rows(ROOT/'configs/worlds.jsonl');worlds=[w for w in allworlds if w['split']=='train'][:16]+[w for w in allworlds if w['split']=='validation'][:16]
    records=[]
    for i,w in enumerate(worlds):
        ps,_,_=pairs(eng,w,folder)
        if not ps:continue
        pair,a,b,mask=ps[0];ids=torch.tensor(pair['a']['token_ids'],device='cuda')[None];labels=ids[:,1:];groups=token_sites(eng,pair['a']['text'])
        for side,recipient,donor in [('a',a,b),('b',b,a)]:
            projected=eng.projected(donor);reference=eng.logits(recipient,mask,decoder_ids=ids[:,:-1]);refids=eng.ids(recipient,mask)
            before_hooks=len(eng.model._forward_pre_hooks)+len(module.q_proj._forward_hooks)
            with online_query(eng,recipient,recipient,mask,module):selflp=eng.logits(recipient,mask,decoder_ids=ids[:,:-1]);selfids=eng.ids(recipient,mask)
            assert torch.equal(reference,selflp) and torch.equal(refids,selfids),'Online query self-patch must be exact'
            assert before_hooks==len(eng.model._forward_pre_hooks)+len(module.q_proj._forward_hooks)
            for condition,change_q,change_kv in [('AA',False,False),('KV_B',False,True),('Q_B',True,False),('QKV_B',True,True)]:
                query_context=online_query(eng,recipient,donor,mask,module) if change_q else contextlib.nullcontext(None)
                with eng.kv_hooks(projected,[name],k=change_kv,v=change_kv),query_context as counters:
                    lp=eng.logits(recipient,mask,decoder_ids=ids[:,:-1]);pred=eng.evaluate(recipient,mask,w,0)
                metrics=distribution(reference,lp,labels,groups)
                records.append(dict(world_id=w['world_id'],split=w['split'],recipient=side,module=name,condition=condition,free=pred,mean_JS=sum(r['JS'] for r in metrics)/len(metrics),online_donor_forward_count=counters['calls'] if counters else 0,actual_prefixes=counters['prefixes'] if counters else [],future_gold_activations_used=False,source_memory_donor_diagnostic=True,student_query_patch_position='q_proj output before head reshape/scaling',online_self_patch_exact=True))
        jsonl(folder/'query_bridge.jsonl',records)
        if (i+1)%4==0:print('query bridge worlds',i+1,flush=True)
    summary=[]
    for split in ('train','validation'):
        for condition in ('AA','KV_B','Q_B','QKV_B'):
            rs=[r for r in records if r['split']==split and r['condition']==condition]
            summary.append(dict(split=split,condition=condition,independent_worlds=len({r['world_id'] for r in rs}),side_denominator=len(rs),joint_numerator=sum(r['free']['score']['success'] for r in rs),target_numerator=sum(r['free']['score']['target'] for r in rs),content_numerator=sum(r['free']['score']['preserved'] for r in rs)))
    return dict(passed=True,worlds=len(worlds),conditions=summary,scope='local query/memory compatibility; exploratory train-validation, not unique circuit',test_evaluations=0,donor_and_extra_forward_used_only_in_diagnostic=True,resources=eng.resources())
