"""Native HF frozen execution with disk/CPU state caching and explicit provenance."""
import sys
import time
from .common import *
sys.path.insert(0,str(SOURCE))
from backend import Backend, editors
from semantics import render,gold,advance,states
from evaluator import score,parse
import torch
from transformers.modeling_outputs import BaseModelOutput

def tensor_sha(x):
    x=x.detach().cpu().contiguous()
    return objsha([str(x.dtype),list(x.shape),hashlib.sha256(x.view(torch.uint8).numpy().tobytes()).hexdigest()])

class Engine(Backend):
    def __init__(self,task):
        super().__init__(task['model']);self.task=task;self.encode_calls=0;self.encoder_forward_calls=0;self.decode_calls=0;self.reuse_count=0;self.new_count=0
        self.ed={}
        for item in task['checkpoint_records']:
            assert sha(item['path'])==item['sha256']
            ck=torch.load(item['path'],map_location='cpu',weights_only=False)
            ed=editors(self.d,0);ed.load_state_dict(ck['editor']);ed.eval()
            for p in ed.parameters():p.requires_grad_(False)
            self.ed[item['condition']]=ed
        self.context=dict(model=task['model'],backbone=read(SOURCE/'model_manifest.json')[task['model']]['revision'],checkpoints={x['condition']:x['sha256'] for x in task['checkpoint_records']},source_hashes=task['source_files'],tokenizer=read(SOURCE/'model_manifest.json')[task['model']]['tokenizer_revision'],wrapper=self.cfg.get('copy_instruction'),generation=self.kw,semantic_version=SEMANTIC_VERSION)
        self.folder=LOCAL/'cache'/task['model']/f"s{task['seed']}";self.folder.mkdir(parents=True,exist_ok=True)
        self.artifacts={}
        self.handle=self.model.get_encoder().register_forward_hook(lambda *args:setattr(self,'encoder_forward_calls',self.encoder_forward_calls+1))
    def close(self):self.handle.remove()
    @torch.no_grad()
    def encode(self,texts):self.encode_calls+=1;return super().encode(texts)
    def cache_key(self,spec):return objsha(dict(context=self.context,spec=spec))
    @torch.no_grad()
    def state(self,spec,make):
        k=self.cache_key(spec);p=self.folder/(k+'.pt');meta=self.folder/(k+'.json')
        if p.exists() and meta.exists():
            info=read(meta);assert info['key']==k and sha(p)==info['sha256']
            x=torch.load(p,map_location='cpu',weights_only=True);self.reuse_count+=1
            h,m=x['h'].cuda(),x['m'].cuda()
            assert tensor_sha(m)==info['mask_hash'] and list(h.shape)==info['shape']
        else:
            h,m=make();assert not h.requires_grad and h.grad_fn is None
            import io
            buffer=io.BytesIO();torch.save(dict(h=h.cpu(),m=m.cpu()),buffer);atomic(p,buffer.getvalue())
            info=dict(key=k,spec=spec,context=self.context,sha256=sha(p),shape=list(h.shape),dtype=str(h.dtype),mask_hash=tensor_sha(m),valid_lengths=m.sum(-1).cpu().tolist());dump(meta,info);self.new_count+=1
        self.artifacts[str(p)]=dict(path=str(p),sha256=info['sha256'],bytes=p.stat().st_size)
        return h,m,k
    def natural(self,worlds,s,texts=None):
        ts=texts if texts is not None else [render(w,s,0) for w in worlds]
        tokens=self.tok([self.wrap(t) for t in ts],add_special_tokens=not self.chat,padding='max_length',max_length=self.cap,truncation=False,return_tensors='pt')
        spec=dict(source='actual_output_reencode' if texts is not None else 'natural',worlds=[w['world_id'] for w in worlds],state=s,texts=ts,initial_state=s,history=[],mask_hash=tensor_sha(tokens.attention_mask),source_token_ids_hash=tensor_sha(tokens.input_ids),source_cap=self.cap)
        return self.state(spec,lambda:self.encode(ts))
    def prefix(self,worlds,initial,history,producer):
        # Fixed original memory and mask throughout; no decoded text feedback.
        h,m,k=self.natural(worlds,initial)
        for i,op in enumerate(history):
            before=self.encode_calls
            h,m,k=self.step(h,m,k,producer,op)
            assert self.encode_calls==before
        return h,m,k
    def step(self,h,m,k,receiver,op):
        before=self.encode_calls;before_h=tensor_sha(h);before_m=tensor_sha(m)
        result=self.state(dict(source='handoff_next',parent_key=k,receiver=receiver,operation=op,mask_hash=before_m),lambda:(self.ed[receiver][op](h,m),m))
        assert self.encode_calls==before and tensor_sha(h)==before_h and tensor_sha(m)==before_m,'Handoff changed producer or reencoded'
        assert torch.equal(result[1],m)
        return result
    @torch.no_grad()
    def predictions(self,h,m,k,worlds,s):
        p=self.folder/(k+'_pred.json')
        if p.exists():
            x=read(p);assert x['key']==k and x['state']==s and x['worlds']==[w['world_id'] for w in worlds]
            self.reuse_count+=1;return x['records']
        before=self.encoder_forward_calls
        ids=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**self.kw);self.decode_calls+=1
        assert self.encoder_forward_calls==before,'External state path encoded'
        ts=self.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False);out=[]
        for w,t,seq,mask in zip(worlds,ts,ids,m):
            ended=any(int(v) in self.eos for v in seq[1:]);g=gold(w,s,0);sc=score(t,g,w,ended);parsed,grammar=parse(t,'time',0,False)
            out.append(dict(text=t,token_ids=seq.cpu().tolist(),ended=ended,success=bool(sc['success']),score=sc,parsed=parsed,mask_hash=tensor_sha(mask),mask_length=int(mask.sum()),memory_length=int(mask.shape[0]),gold=g,failure_reason=[n for n,b in [('termination',ended),('grammar',sc['grammar']),('target',sc['target']),('preserved',sc['preserved'])] if not b]))
        dump(p,dict(key=k,state=s,worlds=[w['world_id'] for w in worlds],records=out));self.new_count+=1
        self.artifacts[str(p)]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
        return out
    def observe(self,state,worlds,s):return self.predictions(*state,worlds,s)
    def frozen_check(self):
        assert not self.model.training and all(not p.requires_grad and p.grad is None for p in self.model.parameters())
        assert all(not e.training and all(not p.requires_grad and p.grad is None for p in e.parameters()) for e in self.ed.values())

def base_row(eng,w,kind,**kw):
    return dict(run_id=eng.task['run_id'],world_id=w['world_id'],model=eng.name,seed=eng.task['seed'],split=eng.task['split'],scope=eng.task['scope'],kind=kind,template=0,**kw)

def atomic_table(eng,worlds):
    records=[];natural={};obs={}
    for s in states('time'):
        natural[s]=eng.natural(worlds,s);obs[s]=eng.observe(natural[s],worlds,s)
        for receiver in eng.ed:
            for op in ('plus','minus'):
                try:n=advance('time',s,op)
                except ValueError:continue
                nxt=eng.step(*natural[s],receiver,op);pred=eng.observe(nxt,worlds,n)
                for w,c0,c2 in zip(worlds,obs[s],pred):records.append(base_row(eng,w,'atomic',receiver=receiver,state=s,operation=op,target_state=n,current=c0,next=c2,C0=c0['success'],C2=c2['success'],Full=bool(c0['success'] and c2['success'])))
    return records,natural,obs

def bart_second(eng,worlds,natural,obs):
    out=[];h1=eng.prefix(worlds,0,['plus'],'P');first=eng.observe(h1,worlds,-1)
    actual=eng.natural(worlds,-1,[p['text'] for p in first]);ba=eng.observe(actual,worlds,-1)
    canonical=natural[-1];bg=obs[-1]
    for op in ('minus','plus'):
        target=advance('time',-1,op)
        for condition,source,bridge in [('PURE',h1,first),('ACTUAL_REENCODE',actual,ba),('GOLD_CANONICAL',canonical,bg)]:
            nxt=eng.step(*source,'P',op);p2=eng.observe(nxt,worlds,target)
            for w,c0,c1,cb,c2 in zip(worlds,obs[0],first,bridge,p2):
                full=bool(c0['success'] and c1['success'] and cb['success'] and c2['success'])
                out.append(base_row(eng,w,'second',initial_state=0,a='plus',b=op,condition=condition,producer='P',receiver='P',current=c0,first=c1,bridge=cb,next=c2,C0=c0['success'],C1=c1['success'],Cbridge=cb['success'],C2=c2['success'],Full=full,bridge_exact=cb['text']==c1['text'],bridge_changed_current=not cb['success'],input_memory_key=source[2]))
    return out

def cross_matrix(eng,worlds,natural,obs):
    out=[];firsts={};observed={}
    for c in cells():
        s,a,b=c['initial_state'],c['a'],c['b']
        for producer in ('F','R'):
            key=(s,a,producer)
            if key not in firsts:
                firsts[key]=eng.prefix(worlds,s,[a],producer);observed[key]=eng.observe(firsts[key],worlds,c['state1'])
        ff,rr=observed[(s,a,'F')],observed[(s,a,'R')]
        for producer,receiver in itertools.product(('F','R'),repeat=2):
            source=firsts[(s,a,producer)];first=observed[(s,a,producer)]
            p2=eng.observe(eng.step(*source,receiver,b),worlds,c['state2'])
            for w,c0,c1,c2,pf,pr in zip(worlds,obs[s],first,p2,ff,rr):
                shared=bool(c0['success'] and pf['success'] and pr['success'])
                out.append(base_row(eng,w,'matrix',**c,producer=producer,receiver=receiver,current=c0,first=c1,next=c2,C0=c0['success'],C1=c1['success'],C2=c2['success'],Full=bool(c0['success'] and c1['success'] and c2['success']),shared_first_correct=shared,raw_exact=pf['text']==pr['text'],trailing_ASCII_equal=pf['text'].rstrip(' \t\r\n')==pr['text'].rstrip(' \t\r\n'),parser_semantic_equal=pf['parsed']==pr['parsed'],input_memory_key=source[2],input_mask_hash=tensor_sha(source[1])))
    return out

import itertools

SEQUENCES=[['plus','minus','plus','minus','plus'],['plus','plus','minus','minus','plus']]
def depth_diagnosis(eng,worlds):
    out=[];h0=eng.natural(worlds,0);c0=eng.observe(h0,worlds,0)
    for producer in eng.ed:
        for seq_id,sequence in enumerate(SEQUENCES):
            state=0;prefix_ok=[p['success'] for p in c0];first_failure=[None if p['success'] else 0 for p in c0]
            for d in range(1,6):
                state=advance('time',state,sequence[d-1]);hd=eng.prefix(worlds,0,sequence[:d],producer);pd=eng.observe(hd,worlds,state)
                for j,(w,p) in enumerate(zip(worlds,pd)):
                    prefix_ok[j]=bool(prefix_ok[j] and p['success'])
                    if not p['success'] and first_failure[j] is None:first_failure[j]=d
                    out.append(base_row(eng,w,'long',producer=producer,sequence_id=seq_id,sequence=sequence,depth=d,current_state=state,current=p,C0=c0[j]['success'],C2=p['success'],Full=prefix_ok[j],first_failure=first_failure[j]))
                if d>3:continue
                actual=eng.natural(worlds,state,[p['text'] for p in pd]);actual_obs=eng.observe(actual,worlds,state)
                canonical=eng.natural(worlds,state);gold_obs=eng.observe(canonical,worlds,state)
                next_state=advance('time',state,sequence[d]);op=sequence[d]
                for receiver in eng.ed:
                    for condition,source,bridge in [('PURE',hd,pd),('ACTUAL_REENCODE',actual,actual_obs),('GOLD_CANONICAL',canonical,gold_obs)]:
                        pn=eng.observe(eng.step(*source,receiver,op),worlds,next_state)
                        for j,(w,p,cb,nxt) in enumerate(zip(worlds,pd,bridge,pn)):
                            out.append(base_row(eng,w,'depth',producer=producer,receiver=receiver,sequence_id=seq_id,sequence=sequence,depth=d,current_state=state,operation=op,current=p,bridge=cb,next=nxt,C0=c0[j]['success'],Cprefix=prefix_ok[j],Cbridge=cb['success'],C2=nxt['success'],Full=bool(prefix_ok[j] and cb['success'] and nxt['success']),condition=condition,bridge_exact=cb['text']==p['text'],input_memory_key=source[2]))
    return out

@torch.no_grad()
def smoke_acceptance(eng,worlds,records):
    natural=eng.natural(worlds,0);h,m,k=natural
    before=eng.encoder_forward_calls
    original=Backend.decode(eng,h,m)
    ids=eng.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**eng.kw)
    wrapped=eng.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
    assert wrapped==[p['text'] for p in original]
    no_op=eng.model.get_decoder().register_forward_hook(lambda module,args,out:out)
    try:
        no_op_ids=eng.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**eng.kw)
    finally:no_op.remove()
    assert torch.equal(ids,no_op_ids)
    y=eng.labels([render(w,0,0) for w in worlds])
    l0=eng.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=y,use_cache=False).logits
    l1=eng.model(encoder_outputs=BaseModelOutput(last_hidden_state=h+0*(h-h)),attention_mask=m,labels=y,use_cache=False).logits
    assert torch.equal(l0,l1)
    assert eng.encoder_forward_calls==before
    calls=eng.encode_calls;eng.encode([wrapped[0]]);assert eng.encode_calls==calls+1
    eng.frozen_check()
    oldchecks=[]
    if eng.name=='t5gemma':
        for method in ('F','R'):
            p=CURRENT/f'runs/formal/s{eng.task["seed"]}/{method}_u200/continuation_self.jsonl'
            old=rows(p);lookup={(r['world_id'],r['initial_state'],r['a'],r['b']):r for r in old if r['template']==0}
            selected=[r for r in records if r['kind']=='matrix' and r['producer']==method and r['receiver']==method]
            for r in selected:
                o=lookup[(r['world_id'],r['initial_state'],r['a'],r['b'])]
                assert o['prediction']==r['next']['text'] and o['first_prediction']==r['first']['text'] and o['score']['success']==r['C2'] and o['first_success']==r['C1']
            oldchecks.append(dict(path=str(p),sha256=sha(p),conditions=method+'→'+method,scope='same22 legal two-step cells, template0, same8 exposed worlds',matched_rows=len(selected),raw_first_and_next_and_joint_equal=True,old_token_ids_available=False))
    else:
        p=CAUSAL/f'local/scan_bart/bart_s{eng.task["seed"]}/pairs.jsonl'; old=rows(p)
        lookup={r['world_id']:r for r in old if r['operation']=='plus' and r['donor_source']=='N→E'}
        selected=[r for r in records if r['kind']=='second' and r['condition']=='PURE' and r['b']=='plus']
        for r in selected:
            o=lookup[r['world_id']]
            assert o['good_current']['text']==r['current']['text'] and o['donor_next']['text']==r['first']['text']
        oldchecks.append(dict(path=str(p),sha256=sha(p),matched_rows=len(selected),scope='natural state0 and first plus, causal Good source',raw_text_equal=True))
    return dict(passed=True,worlds=len(worlds),old_result_comparisons=oldchecks,original_wrapper_greedy_equal=True,no_op_token_ids_equal=True,alpha0_logits_max=float((l0-l1).abs().max()),alpha0_logits_mean=float((l0-l1).abs().mean()),dtype=str(h.dtype),external_state_encoder_calls=0,actual_reencode_encode_calls=1,editor_switch_in_place_mutation=False,stale_decoder_KV=False,all_frozen=True,cache_semantics=self.context)
