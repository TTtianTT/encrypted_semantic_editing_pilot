"""Exact native memory readout diagnostics; called only by the Slurm worker."""
import contextlib
import itertools
import math
import re
import torch
from .common import *
from .engine import hooks,first,replace,render
from .metrics import effective_ids
from .provenance import control_core_allowed

ALPHAS=[-.5,0,.25,.5,.75,1,1.25,1.5]
RANDOM_SEEDS=list(range(61001,61009))

def token_sites(eng,text):
    # Semantic slots fixed by the controlled time grammar, independent of textual coincidences.
    encoding=eng.tok(text,add_special_tokens=not eng.chat,return_offsets_mapping=True)
    relative=re.search(r'(?:event is dated|event is) (.+?)\.',text)
    spans=[m.span() for word in ('planned','completed','cancelled','blue','red','green','white','black','book','lamp','ticket','parcel','sensor','cup','box','key') for m in re.finditer(r'\b'+word+r'\b',text)]
    spans += [m.span() for m in re.finditer(r'\b[1-9]\b',text)]
    groups=[]
    for lo,hi in encoding['offset_mapping']:
        if hi==lo:groups.append('special')
        elif any(lo<b and hi>a for a,b in spans):groups.append('content')
        elif relative and lo<relative.end(1) and hi>relative.start(1):groups.append('attribute')
        else:groups.append('other')
    if eng.chat:groups.append('special') # explicitly appended output EOS
    return groups

def distribution(a,b,labels,groups=None):
    la=a.log_softmax(-1);lb=b.log_softmax(-1);pa,pb=la.exp(),lb.exp();mix=torch.logaddexp(la,lb)-math.log(2)
    js=.5*((pa*(la-mix)).sum(-1)+(pb*(lb-mix)).sum(-1));klab=(pa*(la-lb)).sum(-1);klba=(pb*(lb-la)).sum(-1)
    result=[]
    for i,token in enumerate(labels[0].tolist()):
        aa=a[0,i];bb=b[0,i];aa_comp=aa.clone();bb_comp=bb.clone();aa_comp[token]=bb_comp[token]=-torch.inf
        result.append(dict(position=i,token_id=token,group=groups[i] if groups and i<len(groups) else 'native-token-unmapped',JS=float(js[0,i]),KL_ab=float(klab[0,i]),KL_ba=float(klba[0,i]),a_target_logprob=float(la[0,i,token]),b_target_logprob=float(lb[0,i,token]),a_entropy=float(-(pa[0,i]*la[0,i]).sum()),b_entropy=float(-(pb[0,i]*lb[0,i]).sum()),a_margin=float(aa[token]-aa_comp.max()),b_margin=float(bb[token]-bb_comp.max()),a_top2_margin=float(aa.topk(2).values.diff().neg()[0]),b_top2_margin=float(bb.topk(2).values.diff().neg()[0])))
    return result

def tensor_difference(a,b,mask=None):
    a=a.float();b=b.float()
    if mask is not None and a.shape[:2]==mask.shape:a=a[mask.bool()];b=b[mask.bool()]
    d=b-a
    return dict(a_RMS=float(a.square().mean().sqrt()),b_RMS=float(b.square().mean().sqrt()),delta_RMS=float(d.square().mean().sqrt()),relative_Frobenius=float(d.norm()/(a.norm()+1e-9)),cosine=float(torch.nn.functional.cosine_similarity(a.flatten(),b.flatten(),dim=0)),norm_units='within same module, not a cross-module shrinkage factor')

@torch.no_grad()
def trace(eng,h,m,ids):
    saved={};specs=[]
    for name,mod in eng.model.named_modules():
        if 'decoder' not in name:continue
        if any(key in name for key in ('encoder_attn','cross_attn','fc1','fc2','mlp','layer_norm','layernorm')) or re.search(r'decoder.layers.\d+$',name):
            def hook(mod,args,out,name=name):
                val=first(out)
                if isinstance(val,torch.Tensor):saved[name]=val.detach().clone()
                if len(args)>0 and isinstance(args[0],torch.Tensor):saved[name+':input']=args[0].detach().clone()
                if isinstance(out,tuple) and len(out)>1 and isinstance(out[1],torch.Tensor):saved[name+':attention_probs']=out[1].detach().clone()
            specs.append((mod,hook,False))
    with hooks(specs):logits=eng.logits(h,m,decoder_ids=ids[:,:-1])
    saved['logits']=logits;return saved

@torch.no_grad()
def pairs(eng,w,folder):
    states={};h,m=eng.encode([render(w,0)]);states['N']=(h,m)
    for name,hist in [('E_future_plus','future_plus'),('E_past_minus','past_minus')]:states[name]=eng.history(w,history=hist)
    pred={n:eng.evaluate(*hm,w,0) for n,hm in states.items()}
    # Re-encoding an incorrect content output could introduce a different reserved
    # core. Such an E:R pair cannot qualify anyway; record it without encoding.
    if pred['E_future_plus']['score']['preserved'] and pred['E_future_plus']['score']['parseable']:
        states['R']=eng.encode([pred['E_future_plus']['text']]);pred['R']=eng.evaluate(*states['R'],w,0)
    if eng.name=='bart':
        pca_path=read(ROOT/'manifests/INPUTS.json').get('PCA_path')
        if pca_path:
            assert sha(pca_path)==read(ROOT/'manifests/INPUTS.json')['PCA_sha256']
            q=torch.load(pca_path,map_location='cuda',weights_only=True)['q'].float();bad,bm=states['E_future_plus']
            if torch.equal(bm,m):
                delta=((h.float()-bad.float())@q)@q.T;states['P']=(bad+delta*bm[...,None],bm);pred['P']=eng.evaluate(*states['P'],w,0)
    records=[];eligible=[];dedup=[]
    order=[('E_future_plus','N'),('E_past_minus','N'),('E_future_plus','E_past_minus'),('E_future_plus','R'),('E_future_plus','P')]
    seen=[]
    for an,bn in order:
        if an not in states or bn not in states:
            records.append(dict(world_id=w['world_id'],split=w['split'],source_pair=an+':'+bn,eligible=False,reasons=['SOURCE_UNAVAILABLE_CONTENT_PROVENANCE_GUARD'],delta_norm=None,a=pred.get(an),b=pred.get(bn),length=None,qualification_requires_next_fork=False));continue
        a,ma=states[an];b,mb=states[bn];pa,pb=pred[an],pred[bn]
        reasons=[];same_shape=a.shape==b.shape and torch.equal(ma,mb)
        if not(pa['score']['success'] and pb['score']['success']):reasons.append('CURRENT_NOT_DOUBLE_CORRECT')
        ia,ea=effective_ids(pa['token_ids'],eng.eos);ib,eb=effective_ids(pb['token_ids'],eng.eos)
        if ia!=ib:reasons.append('TEXT_MATCH_ONLY' if pa['text']==pb['text'] else 'TOKEN_AND_TEXT_MISMATCH')
        if pa['text']!=pb['text']:reasons.append('RAW_TEXT_MISMATCH')
        if not(ea and eb):reasons.append('NO_NORMAL_EOS')
        if not same_shape:reasons.append('SHAPE_MASK_MISMATCH')
        norm=float((b-a).float()[ma.bool()].norm()) if same_shape else None
        if norm is not None and norm<=1e-5:reasons.append('NUMERICALLY_IDENTICAL')
        if same_shape and any(torch.equal(a,x) and torch.equal(b,y) for x,y in seen):reasons.append('DUPLICATE_NUMERIC_SOURCE_PAIR')
        if same_shape:seen.append((a,b))
        r=dict(world_id=w['world_id'],split=w['split'],source_pair=an+':'+bn,eligible=not reasons,reasons=reasons,delta_norm=norm,a=pa,b=pb,length=int(ma.sum()) if same_shape else None,qualification_requires_next_fork=False)
        records.append(r)
        if not reasons:eligible.append((r,a,b,ma))
    jsonl(folder/(w['world_id']+'_qualification.jsonl'),records)
    return eligible,states,pred

@torch.no_grad()
def run(eng,folder):
    ws=rows(ROOT/'configs/worlds.jsonl');discovery=[w for w in ws if w['split']=='train'][:32];validation=[w for w in ws if w['split']=='validation'][:32]
    replay=rows(ROOT/'configs/replay_worlds.jsonl')
    # Eager is prohibited after failed optional backend parity. All interventions stay native SDPA.
    h,m=eng.encode([render(discovery[0],0)]);y=eng.labels([render(discovery[0],0)]);reference=eng.logits(h,m,y);ids=eng.ids(h,m)
    with eng.kv_hooks(eng.projected(h)):
        aligned=eng.logits(h,m,y);aligned_ids=eng.ids(h,m)
    error=float((reference-aligned).abs().max())
    assert error==0,'Native SDPA self-projection hook changed logits'
    assert torch.equal(ids,aligned_ids),'Native SDPA self-projection hook changed generation'
    dump(folder/'NATIVE_HOOK_ACCEPTANCE.json',dict(logit_max_error=error,tolerance=0,tokens_equal=True,backend='sdpa',eager_switch=False,failed_eager_retained=True))
    allscores=[];curves=[];propagation=[];prefixcontrols=[];causal=[];counts={};cache=folder/'tensor_cache';cache.mkdir(exist_ok=True)
    for wi,w in enumerate(discovery+validation+replay):
        group='discovery' if w['split']=='train' else 'validation' if w['split']=='validation' else 'replay';ps,states,pred=pairs(eng,w,folder)
        counts.setdefault(group,dict(scanned_worlds=0,qualified_worlds=0,qualified_pairs=0));counts[group]['scanned_worlds']+=1;counts[group]['qualified_worlds']+=bool(ps);counts[group]['qualified_pairs']+=len(ps)
        for ri,(pair,a,b,mask) in enumerate(ps):
            native=torch.tensor(pair['a']['token_ids'],device='cuda')[None];labels=native[:,1:]
            la=eng.logits(a,mask,decoder_ids=native[:,:-1]);lb=eng.logits(b,mask,decoder_ids=native[:,:-1]);groups=token_sites(eng,pair['a']['text'])
            for op,next_state in [('plus',-1),('minus',1)]:
                next_a=eng.evaluate(eng.ed[op](a,mask),mask,w,next_state);next_b=eng.evaluate(eng.ed[op](b,mask),mask,w,next_state)
                jsonl(folder/(w['world_id']+'_'+str(ri)+'_'+op+'_bridge.jsonl'),[dict(world_id=w['world_id'],split=group,source_pair=pair['source_pair'],panel_A=True,panel_B=next_a['token_ids']!=next_b['token_ids'],legacy_accuracy_fork=next_a['score']['success']!=next_b['score']['success'],panel_B_definition='different next native generated token sequence',operation=op,a_next=next_a,b_next=next_b)])
            scores=distribution(la,lb,labels,groups)
            for s in scores:allscores.append(dict(world_id=w['world_id'],split=group,source_pair=pair['source_pair'],**s))
            # Complete raw logits only for fixed 4 discovery worlds, never test.
            if wi<4:
                torch.save(dict(raw_a=la.cpu(),raw_b=lb.cpu(),prefix_ids=native.cpu(),processor_note='main greedy; forced BOS scored separately, not equated to raw logits'),cache/(w['world_id']+'_'+str(ri)+'_logits.pt'))
                ta=trace(eng,a,mask,native);tb=trace(eng,b,mask,native)
                for name in ta:propagation.append(dict(world_id=w['world_id'],source_pair=pair['source_pair'],module=name,**tensor_difference(ta[name],tb[name],mask)))
                if wi==0:torch.save(dict(a={n:v.cpu() for n,v in ta.items()},b={n:v.cpu() for n,v in tb.items()}),cache/(pair['source_pair'].replace(':','_')+'_trace.pt'))
            # Finite paths on fixed first8 worlds per group and all strict source pairs.
            index=wi if group=='discovery' else wi-len(discovery) if group=='validation' else wi-len(discovery)-len(validation)
            if index<8:
                delta=(b-a).float()*mask[...,None]
                directions=[('real',delta,None)]
                for seed in RANDOM_SEEDS:
                    rng=torch.Generator(device='cuda').manual_seed(seed)
                    for kind in ('isotropic','shared_rank4'):
                        if kind=='isotropic':d=torch.randn(a.shape,generator=rng,device='cuda')
                        else:
                            q=torch.linalg.qr(torch.randn(a.shape[-1],4,generator=rng,device='cuda')).Q
                            d=torch.randn(*a.shape[:-1],4,generator=rng,device='cuda')@q.T
                        d*=mask[...,None];d=d/(d.norm(dim=-1,keepdim=True)+1e-9)*delta.norm(dim=-1,keepdim=True)
                        directions.append((kind,d,seed))
                for kind,d,seed in directions:
                    grid=ALPHAS
                    for alpha in grid:
                        hp=(a.float()+alpha*d).to(a.dtype);p=eng.evaluate(hp,mask,w,0)
                        curves.append(dict(world_id=w['world_id'],split=group,source_pair=pair['source_pair'],direction=kind,random_seed=seed,alpha=alpha,delta_norm=float((hp-a).float()[mask.bool()].norm()),per_token_energy_max_error=float((d.norm(dim=-1)-delta.norm(dim=-1)).abs().max()),text_preserved=p['text']==pair['a']['text'],tokens_preserved=effective_ids(p['token_ids'],eng.eos)[0]==effective_ids(pair['a']['token_ids'],eng.eos)[0],prediction=p))
            # Source/prefix controls, fixed first4 worlds per group.
            if index<4 and ri==0:
                for side,mem in [('a',a),('b',b)]:
                    for fraction in (0,.25,.5,.75):
                        end=1+int((native.shape[1]-2)*fraction);prefix=native[:,:end]
                        projected=eng.projected(mem);zero={k:torch.zeros_like(v) if k[1]=='v' else v for k,v in projected.items()}
                        with eng.kv_hooks(zero,k=False,v=True):zero_pred=eng.evaluate(mem,mask,w,0,prefix=prefix)
                        donor_w=dict(w,color='red' if w['color']!='red' else 'blue')
                        if control_core_allowed(donor_w,w['split']):
                            donor,donor_mask=eng.encode([render(donor_w,0)])
                            if torch.equal(donor_mask,mask):
                                with eng.kv_hooks(eng.projected(donor),k=False,v=True):resample=eng.evaluate(mem,mask,w,0,prefix=prefix)
                            else:resample=dict(status='SHAPE_MASK_MISMATCH')
                        else:resample=dict(status='CONTROL_CORE_PROVENANCE_BLOCKED')
                        prefixcontrols.append(dict(world_id=w['world_id'],split=group,side=side,prefix_fraction=fraction,prefix_ids=prefix[0].tolist(),zeroing_OOD=True,zero=zero_pred,resample=resample))
            # All-layer observational ranking then exact layer K/V 2x2 and symmetric value ablations.
            if ri==0:
                proj_a=eng.projected(a);proj_b=eng.projected(b)
                for name,module in eng.cross:
                    for side,recipient,donorproj in [('a',a,proj_b),('b',b,proj_a)]:
                        base=la if side=='a' else lb;local_query=[]
                        for condition,k,v in [('AA',False,False),('BA',True,False),('AB',False,True),('BB',True,True)]:
                            with eng.kv_hooks(donorproj,[name],k=k,v=v):
                                lp=eng.logits(recipient,mask,decoder_ids=native[:,:-1]);pp=eng.evaluate(recipient,mask,w,0)
                            metrics=distribution(base,lp,labels,groups)
                            causal.append(dict(world_id=w['world_id'],split=group,module=name,recipient=side,condition=condition,free_generation=pp,content_margin_shift=sum(s['b_margin']-s['a_margin'] for s in metrics if s['group']=='content')/max(1,sum(s['group']=='content' for s in metrics)),mean_JS=sum(s['JS'] for s in metrics)/len(metrics)))
                        zeros={key:torch.zeros_like(val) if key[1]=='v' else val for key,val in donorproj.items()}
                        with eng.kv_hooks(zeros,[name],k=False,v=True):lp=eng.logits(recipient,mask,decoder_ids=native[:,:-1]);pp=eng.evaluate(recipient,mask,w,0)
                        metrics=distribution(base,lp,labels,groups)
                        causal.append(dict(world_id=w['world_id'],split=group,module=name,recipient=side,condition='VALUE_ZERO_OOD',free_generation=pp,content_margin_shift=sum(s['b_margin']-s['a_margin'] for s in metrics if s['group']=='content')/max(1,sum(s['group']=='content' for s in metrics)),mean_JS=sum(s['JS'] for s in metrics)/len(metrics)))
        if (wi+1)%4==0:
            print(eng.name,group,'processed',wi+1,counts,flush=True)
            jsonl(folder/'readout_scores.jsonl',allscores);jsonl(folder/'perturbation_curves.jsonl',curves);jsonl(folder/'propagation.jsonl',propagation);jsonl(folder/'source_prefix_controls.jsonl',prefixcontrols);jsonl(folder/'causal_conditions.jsonl',causal)
    jsonl(folder/'readout_scores.jsonl',allscores);jsonl(folder/'perturbation_curves.jsonl',curves);jsonl(folder/'propagation.jsonl',propagation);jsonl(folder/'source_prefix_controls.jsonl',prefixcontrols);jsonl(folder/'causal_conditions.jsonl',causal)
    return dict(passed=True,worlds=len(discovery+validation+replay),panel_counts=counts,maximum_JS=max((r['JS'] for r in allscores),default=None),mean_JS=sum(r['JS'] for r in allscores)/max(1,len(allscores)),mechanism_status='DISCOVERY_VALIDATION_ONLY; head-level/fixed-pattern controls still required before regularizer',independent_test_accessed=0,resources=eng.resources())
