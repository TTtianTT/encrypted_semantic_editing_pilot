"""Slurm-only native injection/gradient/overfit acceptance. No test data access."""
import hashlib
import json
import torch
import torch.nn.functional as F
from .common import *
from .engine import Engine, hooks, editors, render, first

def parameter_sha(model):
    h=hashlib.sha256()
    for name,p in model.state_dict().items():h.update(name.encode());h.update(p.detach().cpu().view(torch.uint8).numpy().tobytes())
    return h.hexdigest()

def run(eng,folder):
    ws=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='train'][:8]
    before=parameter_sha(eng.model);records=[];mapping=[];names={id(mod):name for name,mod in eng.model.named_modules()}
    # Capture actual module shapes once; retain tuple meaning rather than flattening silently.
    h,m=eng.encode([render(ws[0],0)]);y=eng.labels([render(ws[0],0)])
    specs=[]
    for name,mod in eng.model.named_modules():
        if 'decoder' not in name:continue
        if any(key in name for key in ('attn','layer_norm','layernorm','fc1','fc2','mlp','norm')) or name.endswith('layers.5'):
            def record(module,args,out,name=name):
                value=first(out)
                if isinstance(value,torch.Tensor):mapping.append(dict(name=name,class_name=module.__class__.__name__,input_shapes=[list(a.shape) for a in args if isinstance(a,torch.Tensor)],output_shape=list(value.shape),dtype=str(value.dtype),tuple_output=isinstance(out,tuple),observational=True))
            specs.append((mod,record,False))
    with hooks(specs):eng.logits(h,m,y)
    crossmap=[]
    for name,mod in eng.cross:
        crossmap.append(dict(name=name,heads=getattr(mod,'num_heads',getattr(mod.config,'num_attention_heads',None)),KV_heads=getattr(mod.config,'num_key_value_heads',getattr(mod,'num_heads',None)),head_dim=mod.head_dim,layer_index=mod.layer_idx,zero_based=True,K_V_site='linear projection output before head reshape/replication; cross-attention has no RoPE',output_projection='o_proj' if eng.chat else 'out_proj',includes_residual=False,normalization='T5Gemma pre_cross_attn RMSNorm and post_cross_attn RMSNorm before residual' if eng.chat else 'BART residual then encoder_attn_layer_norm (post norm)'))
    dump(folder/'HOOK_MAP.json',dict(model=eng.task['model'],cross_attention=crossmap,modules=mapping,module_tree=[dict(name=n,class_name=mod.__class__.__name__) for n,mod in eng.model.named_modules()],memory_dependencies='audited source: cross K/V only, plus source attention mask; validated all-layer replacement'))
    for w in ws:
        h,m=eng.encode([render(w,0)]);repeated,m2=eng.encode([render(w,0)]);bad,mb=eng.history(w)
        assert torch.equal(m,m2)
        noise=float((h-repeated).float()[m.bool()].norm())
        y=eng.labels([render(w,0)]);l=eng.logits(h,m,y)
        orig=eng.decode(h,m)[0];native_ids=eng.ids(h,m,native=True);ids=eng.ids(h,m)
        assert torch.equal(native_ids,ids),'native/cacheless generation boundary changed'
        assert orig['text']==eng.evaluate(h,m,w,0)['text']
        old=eng.model(encoder_outputs=__import__('transformers').modeling_outputs.BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=y,use_cache=False).logits.float()
        assert torch.equal(old,l)
        counts=[]
        with hooks([(eng.model.get_encoder(),lambda *args:counts.append(1),False)]):eng.ids(h,m);eng.logits(h,m,y)
        assert not counts
        initial_hooks=sum(len(mod._forward_hooks)+len(mod._forward_pre_hooks) for mod in eng.model.modules())
        for kind in ('noop','self','alpha0'):
            hp=h if kind!='alpha0' else h+torch.zeros_like(h)
            with hooks([(eng.model.get_decoder(),lambda mod,args,out:out,False)]):lp=eng.logits(hp,m,y)
            assert torch.equal(lp,l)
        assert sum(len(mod._forward_hooks)+len(mod._forward_pre_hooks) for mod in eng.model.modules())==initial_hooks
        padded=h.clone();padded[~m.bool()]+=10
        assert torch.equal(eng.logits(padded,m,y),l),'Padding-only logits changed'
        assert torch.equal(eng.ids(padded,m),ids)
        assert torch.equal(m,mb),'Pair shape/mask mismatch in acceptance'
        projected=eng.projected(h)
        with eng.kv_hooks(projected):full=eng.logits(bad,m,y);fullids=eng.ids(bad,m)
        kv_error=float((full-l).abs().max());assert kv_error<=2e-5 if not eng.chat else kv_error<=.125
        assert torch.equal(fullids,ids),'All-layer K/V failed donor generation equivalence'
        inp=eng.tok(eng.wrap(render(w,0)),add_special_tokens=not eng.chat,padding='max_length',max_length=eng.cap,return_tensors='pt')
        valid_source_ids=inp.input_ids[0][inp.attention_mask[0].bool()].tolist()
        records.append(dict(world_id=w['world_id'],split='train',repeat_noise_norm=noise,native_ids=ids[0].tolist(),text=orig['text'],original_logits_max_error=0.,noop_self_alpha0_max_error=0.,all_layer_KV_max_error=kv_error,padding_max_error=0.,encoder_calls=0,valid_memory_length=int(m.sum()),valid_source_ids=valid_source_ids,special_tokens_in_mask='all source BOS/EOS valid; only mask0 excluded',cacheless_native_tokens_equal=True))
    # Autograd/finite differences on a real frozen decoder, teacher path detached.
    w=ws[0];h,m=eng.encode([render(w,0)]);y=eng.labels([render(w,-1)]);leaf=h.detach().clone().requires_grad_(True)
    student_logits=eng.logits_with_memory_grad(leaf,m,y)
    loss=F.cross_entropy(student_logits.reshape(-1,student_logits.shape[-1]),y.reshape(-1))
    grad=torch.autograd.grad(loss,leaf)[0];assert torch.isfinite(grad).all() and grad[m.bool()].norm()>0
    direction=grad.float()*m[...,None];direction/=direction.square().mean().sqrt();direction=direction.to(h.dtype)
    analytic=float((grad.float()*direction.float()).sum());fd=[]
    epsilons=[.001,.003,.01] if not eng.chat else [.015625,.03125,.0625]
    for eps in epsilons:
        values=[]
        for sign in (-1,1):
            logits=eng.logits((h+sign*eps*direction).to(h.dtype),m,y)
            values.append(float(F.cross_entropy(logits.reshape(-1,logits.shape[-1]),y.reshape(-1))))
        derivative=(values[1]-values[0])/(2*eps);relative=abs(derivative-analytic)/(abs(analytic)+1e-9)
        fd.append(dict(epsilon=eps,analytic=analytic,finite_difference=derivative,relative_error=relative))
    # Lock tolerances before observation. BF16 has quantization, reported separately.
    fd_pass=any(r['relative_error']<(.05 if not eng.chat else .20) for r in fd)
    dump(folder/'GRADIENT_CHECK.json',dict(checks=fd,passed=fd_pass,tolerance_relative=.05 if not eng.chat else .20,memory_grad_norm=float(grad.norm()),backbone_gradients=0,precision=str(h.dtype)))
    assert fd_pass,'Finite difference failed locked precision tolerance'
    assert all(p.grad is None for p in eng.model.parameters())
    ed=editors(eng.d,42);opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0.)
    # Balanced operations on 8 distinct train worlds, no independent test access.
    hs=[];ms=[];targets=[]
    for i,w in enumerate(ws):
        hh,mm=eng.encode([render(w,0)]);hs.append(hh[0]);ms.append(mm[0]);targets.append(render(w,-1 if i%2==0 else 1))
    h=torch.stack(hs);m=torch.stack(ms);logs=[]
    for update in range(120):
        opt.zero_grad(set_to_none=True);value=0.
        for op,indices in [('plus',[0,2,4,6]),('minus',[1,3,5,7])]:
            for ix in (indices[:2],indices[2:]):
                out=ed[op](h[ix],m[ix]);ls,_=eng.ce(out,m[ix],[targets[j] for j in ix]);v=ls.sum()/8;v.backward();value+=float(v.detach())
        assert all(p.grad is None for p in eng.model.parameters())
        assert any(p.grad is not None and p.grad.norm()>0 for p in ed.parameters())
        torch.nn.utils.clip_grad_norm_(ed.parameters(),1.,error_if_nonfinite=True);opt.step();logs.append(dict(update=update+1,CE=value))
        if (update+1)%20==0:print(eng.name,'overfit smoke',update+1,value,flush=True)
    predictions=[]
    for i,w in enumerate(ws):
        op='plus' if i%2==0 else 'minus';predictions.append(dict(world_id=w['world_id'],operation=op,**eng.evaluate(ed[op](h[i:i+1],m[i:i+1]),m[i:i+1],w,-1 if op=='plus' else 1)))
    jsonl(folder/'smoke_predictions.jsonl',predictions);jsonl(folder/'smoke_training.jsonl',logs)
    assert logs[-1]['CE']<logs[0]['CE']*.5,'8-world training loss did not decrease sufficiently'
    after=parameter_sha(eng.model);assert before==after,'Frozen backbone changed'
    jsonl(folder/'acceptance_records.jsonl',records)
    result=dict(passed=True,worlds=8,checks=records,gradient_check=fd,overfit=dict(updates=120,initial_CE=logs[0]['CE'],final_CE=logs[-1]['CE'],joint_success=sum(p['score']['success'] for p in predictions),denominator=8),backbone_before_sha=before,backbone_after_sha=after,encoder_decoder_gradients=0,resources=eng.resources(),test_worlds_accessed=0)
    dump(folder/'S0_ACCEPTANCE.json',result);return result
