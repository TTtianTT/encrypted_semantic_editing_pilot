"""Exp2 native cross-attention K/V interventions, including memory-token groups."""
import contextlib
import re
from core import *

def token_groups(eng,world,text,mask):
    encoded=eng.tok(text,return_offsets_mapping=True,add_special_tokens=True)
    temporal=re.search(r'(?:event is dated|event is) ([^.]+)\.',text);assert temporal
    edited=temporal.span(1)
    entities=[m.span() for m in re.finditer(r'\b'+re.escape(world['object'])+r'\b|\b[1-9]\b',text)]
    result={k:torch.zeros_like(mask,dtype=torch.bool) for k in ('all','edited','entity_quantity','other')}
    result['all']=mask.bool().clone()
    for i,(a,b) in enumerate(encoded['offset_mapping']):
        if i>=len(mask) or not mask[i]:continue
        if b>a and a<edited[1] and b>edited[0]:group='edited'
        elif b>a and any(a<y and b>x for x,y in entities):group='entity_quantity'
        else:group='other'
        result[group][i]=True
    assert torch.equal(result['edited']|result['entity_quantity']|result['other'],result['all'])
    assert not (result['edited']&result['entity_quantity']).any()
    return result

def layers(eng):return eng.model.model.decoder.layers

@contextlib.contextmanager
def kv_hooks(eng,donor,recipient_mask,selected_layers,k_rows,v_rows,positions):
    handles=[]
    for layer in selected_layers:
        mod=layers(eng)[layer].encoder_attn
        for kind,enabled in [('k',k_rows),('v',v_rows)]:
            projected=getattr(mod,kind+'_proj')(donor)
            active=positions&enabled[:,None]&recipient_mask.bool()
            def hook(module,args,out,projected=projected,active=active):
                assert out.shape==projected.shape
                return torch.where(active[...,None],projected,out)
            handles.append(getattr(mod,kind+'_proj').register_forward_hook(hook))
    try:yield
    finally:
        for handle in handles:handle.remove()

@torch.no_grad()
def decode_uncached(eng,h,m,worlds,state=-1):
    from transformers.modeling_outputs import BaseModelOutput
    render,gold,advance,states,score=semantics()
    ids=eng.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**dict(eng.kw,use_cache=False))
    texts=eng.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)
    return [dict(text=t,token_ids=x.cpu().tolist(),score=score(t,gold(w,state,0),w,any(int(v) in eng.eos for v in x[1:]))) for t,x,w in zip(texts,ids,worlds)]

@torch.no_grad()
def trace_queries(eng,h,m,texts):
    cache={};handles=[]
    for layer in range(6):
        def hook(module,args,out,layer=layer):cache[layer]=out.detach().clone()
        handles.append(layers(eng)[layer].encoder_attn.q_proj.register_forward_hook(hook))
    try:logits(eng,h,m,texts)
    finally:
        for handle in handles:handle.remove()
    return cache

@torch.no_grad()
def main():
    protocol=verify_protocol();eng,load_editor=engine();render,gold,advance,states,score=semantics();audits=[]
    for seed in SEEDS:
        ed=load_editor(eng,task(seed)['checkpoint']);ed.requires_grad_(False);pairs=selections(seed)[:protocol['decoder_worlds']]
        for start in range(0,len(pairs),8):
            name=f'results/decoder/s{seed}_b{start:03d}.jsonl'
            if (ROOT/name).exists():continue
            rs=pairs[start:start+8];bad,good,m=patch_pair_batch(rs);ws=[r['world'] for r in rs];B=len(rs)
            hb,hg=ed['plus'](bad,m),ed['plus'](good,m);texts=[render(w,-1,0) for w in ws]
            reference,y=logits(eng,hg,m,texts);base,_=logits(eng,hb,m,texts)
            baseline=decode_uncached(eng,hb,m,ws);donor=decode_uncached(eng,hg,m,ws)
            qa,qb=trace_queries(eng,hb,m,texts),trace_queries(eng,hg,m,texts)
            groups=[]
            for r,mm in zip(rs,m):
                recipient=token_groups(eng,r['world'],render(r['world'],r['recipient_history']['start'],0),mm)
                reference_groups=token_groups(eng,r['world'],render(r['world'],0,0),mm)
                assert all(torch.equal(recipient[k],reference_groups[k]) for k in recipient),'Semantic memory spans are not aligned'
                groups.append(recipient)
            records=[]
            for layer in protocol['decoder_layers']:
                for group in protocol['decoder_groups']:
                    # Simultaneous K-only/V-only/KV conditions. All are native hooks.
                    h=hb.repeat(3,1,1);g=hg.repeat(3,1,1);mm=m.repeat(3,1);ww=ws*3;tt=texts*3
                    positions=torch.stack([r[group] for r in groups]).repeat(3,1)
                    kr=torch.tensor([True]*B+[False]*B+[True]*B,device='cuda');vr=torch.tensor([False]*B+[True]*B+[True]*B,device='cuda')
                    with kv_hooks(eng,g,mm,[layer],kr,vr,positions):
                        changed,labels=logits(eng,h,mm,tt);free=decode_uncached(eng,h,mm,ww)
                    metrics=distribution(reference.repeat(3,1,1),changed,labels)
                    for block,condition in enumerate(protocol['decoder_conditions']):
                        for i,r in enumerate(rs):
                            k=block*B+i
                            current_labels=eng.labels([render(r['world'],0,0)])[0]
                            target_labels=y[i]
                            divergence=next(j for j in range(min(len(current_labels),len(target_labels))) if current_labels[j]!=target_labels[j])
                            margin=float(changed[k,divergence,target_labels[divergence]]-changed[k,divergence,current_labels[divergence]])
                            q_shift=float((qa[layer][i]-qb[layer][i]).norm())
                            records.append(dict(seed=seed,world_id=r['world_id'],layer=layer,group=group,condition=condition,
                                                memory_positions=int(positions[k].sum()),baseline=baseline[i],donor=donor[i],output=free[k],
                                                next_success=free[k]['score']['success'],target_margin=margin,
                                                donor_recipient_query_shift=q_shift,teacher_forced_vs_donor=metrics[k],cache=False))
            for label,donor_h in [('self',hb),('all_layer_reference',hg)]:
                enabled=torch.ones(B,dtype=torch.bool,device='cuda')
                with kv_hooks(eng,donor_h,m,list(range(6)),enabled,enabled,m.bool()):
                    changed,labels=logits(eng,hb,m,texts);free=decode_uncached(eng,hb,m,ws)
                if label=='self':assert torch.equal(base,changed),'Self K/V replacement failed native exactness'
                else:assert torch.allclose(reference,changed,rtol=0,atol=1e-5),'All-layer K/V must reproduce reference under a shared prefix'
                for i,r in enumerate(rs):
                    assert free[i]['token_ids']==(baseline[i] if label=='self' else donor[i])['token_ids']
                    records.append(dict(seed=seed,world_id=r['world_id'],layer='all',group='all',condition=label,
                                        baseline=baseline[i],donor=donor[i],output=free[i],next_success=free[i]['score']['success'],cache=False))
            assert all(not getattr(layer.encoder_attn,kind+'_proj')._forward_hooks for layer in layers(eng) for kind in ('k','v','q'))
            write(name,records);audits.append(dict(seed=seed,start=start,self_exact=True,all_layer_reference_exact=True,hooks_removed=True,positions_aligned=True))
            print('decoder K/V localization',seed,start+B,flush=True)
        del ed
    write('results/decoder.jsonl',[r for p in sorted((ROOT/'results/decoder').glob('*.jsonl')) for r in rows(p)])
    dump('results/decoder_complete.json',dict(resources=eng.resources(),audits=audits,training_updates=0,protocol_sha256=sha(ROOT/'protocol.json'),code_sha256=sha(__file__)))

if __name__=='__main__':main()
