"""Teacher-forced native HF readout paths. These hooks never claim latent repair."""
import contextlib
import torch
from .common import *
from .adapter import render,advance,native_hook
from .pairs import primary_pairs
from .rollout_eval import load_pairs,load_state,get_patch,random_component,evaluate_condition,RANDOM_SEEDS

def components(eng):
    dec=eng.model.get_decoder();out={}
    for i,layer in enumerate(dec.layers):
        if eng.chat:
            modules=[('cross_attention',layer.post_cross_attn_layernorm,'after cross-attention RMSNorm, before dropout/residual addition'),('MLP',layer.post_feedforward_layernorm,'after feedforward RMSNorm, before dropout/residual addition')]
        else:
            modules=[('cross_attention',layer.encoder_attn,'out_proj output, before dropout/residual addition and encoder_attn_layer_norm'),('MLP',layer.fc2,'fc2 output, before dropout/residual addition and final_layer_norm')]
        modules.append(('residual',layer,'decoder block output, after residual addition and block normalization'))
        for kind,module,point in modules:
            out[f'layer{i}.{kind}']=dict(module=module,point=point,layer=i,kind=kind)
    real_paths={id(module):name for name,module in eng.model.named_modules()}
    for x in out.values():x['module_path']=real_paths[id(x['module'])]
    return out

def first_tensor(output):return output[0] if isinstance(output,tuple) else output
def replace_tensor(output,value):return (value,)+output[1:] if isinstance(output,tuple) else value

def prefix_spec(eng,pair):
    w=pair['world'];nxt=advance('time',0,pair['operation'])
    target=render(w,nxt,pair['template']);competitor=render(w,0,pair['template'])
    a=eng.labels([target]);b=eng.labels([competitor]);length=min(a.shape[1],b.shape[1])
    pos=next(i for i in range(length) if int(a[0,i])!=int(b[0,i]))
    assert torch.equal(a[:,:pos],b[:,:pos])
    return dict(labels=a[:,:pos+1],position=pos,correct_id=int(a[0,pos]),wrong_id=int(b[0,pos]),target=target,competitor=competitor)

@torch.no_grad()
def score_and_cache(eng,h,mask,prefix,modules,cache_names=(),patch_values=None):
    from transformers.modeling_outputs import BaseModelOutput
    cache={};patch_values=patch_values or {};pos=prefix['position']
    with contextlib.ExitStack() as stack:
        for name in set(cache_names)|set(patch_values):
            def hook(module,args,out,key=name):
                value=first_tensor(out)
                if key in cache_names:cache[key]=value[:,pos].detach().cpu().clone()
                if key in patch_values:
                    changed=value.clone();changed[:,pos]=patch_values[key].to(value.device,value.dtype)
                    return replace_tensor(out,changed)
                return out
            stack.enter_context(native_hook(modules[name]['module'],hook))
        logits=eng.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,labels=prefix['labels'],use_cache=False).logits
        v=logits[0,pos].float();margin=float(v[prefix['correct_id']]-v[prefix['wrong_id']])
        nll=float(-v.log_softmax(-1)[prefix['correct_id']])
    return dict(margin=margin,key_token_nll=nll),cache

@torch.no_grad()
def run(eng,config,folder):
    method_lock=read(ROOT/f'results/{eng.name}_method_lock.json');assert method_lock['gate_passed'],'S3 requires validation gate'
    spec=method_lock['methods'][0];pairs=primary_pairs(load_pairs(eng),'discovery',32)
    pca=torch.load(ROOT/f'local/pca/{eng.name}_s{eng.task["editor_seed"]}.pt',map_location='cpu',weights_only=True)['q']
    modules=components(eng);coarse=[];contexts=[]
    for pair in pairs:
        bad,good,mask=load_state(pair);repaired,component,actual,_=get_patch(eng,pair,bad,good,mask,spec,pca)
        op=eng.ed[pair['operation']];bnext,rnext,gnext=op(bad,mask),op(repaired,mask),op(good,mask)
        prefix=prefix_spec(eng,pair)
        bscore,bc=score_and_cache(eng,bnext,mask,prefix,modules,list(modules))
        gscore,gc=score_and_cache(eng,gnext,mask,prefix,modules,list(modules))
        noop,_=score_and_cache(eng,bnext,mask,prefix,modules,patch_values=bc)
        assert noop==bscore,'Decoder self-cache patch drift'
        for name in modules:
            patched,_=score_and_cache(eng,bnext,mask,prefix,modules,patch_values={name:gc[name]})
            coarse.append(dict(world_id=pair['world_id'],module=name,point=modules[name]['point'],prefix_position=prefix['position'],baseline=bscore,donor=gscore,readout_patch=patched,margin_gain=patched['margin']-bscore['margin'],interpretation='teacher-forced readout effect, not latent repair'))
        contexts.append(pair)
    means={name:sum(r['margin_gain'] for r in coarse if r['module']==name)/len(pairs) for name in modules}
    selected=sorted(modules,key=lambda n:(-means[n],n))[:3]
    lock=dict(selected=selected,coarse_means=means,discovery_worlds=[r['world_id'] for r in pairs],selection='top mean donor-vs-bad teacher-forced first-divergent semantic-token margin gain',components={n:{k:v for k,v in x.items() if k!='module'} for n,x in modules.items()},self_patch_score_exact=True,free_generation_patching='not performed; auxiliary effects exclusively teacher-forced')
    dump(folder/'decoder_lock.json',lock);jsonl(folder/'coarse.jsonl',coarse)
    # Shared module low-dimensional refinement is fit exclusively on discovery R-B.
    differences={n:[] for n in selected};cached=[]
    for pair in contexts:
        bad,good,mask=load_state(pair);repaired,comp,actual,_=get_patch(eng,pair,bad,good,mask,spec,pca);op=eng.ed[pair['operation']]
        prefix=prefix_spec(eng,pair);bnext,rnext=op(bad,mask),op(repaired,mask)
        bscore,bc=score_and_cache(eng,bnext,mask,prefix,modules,selected)
        rscore,rc=score_and_cache(eng,rnext,mask,prefix,modules,selected)
        for n in selected:differences[n].append((rc[n]-bc[n]).float()[0])
        cached.append((pair,bscore,rscore,bc,rc))
    bases={n:torch.linalg.svd(torch.stack(xs),full_matrices=False).Vh[:4].T for n,xs in differences.items()}
    pathrows=[]
    for pair,bscore,rscore,bc,rc in cached:
        bad,good,mask=load_state(pair);repaired,comp,actual,_=get_patch(eng,pair,bad,good,mask,spec,pca);op=eng.ed[pair['operation']]
        prefix=prefix_spec(eng,pair);bnext,rnext=op(bad,mask),op(repaired,mask)
        gnext=op(good,mask);reverse_next=op(torch.where(mask.bool()[...,None],(good.float()-comp).to(good.dtype),good),mask)
        gs,gc=score_and_cache(eng,gnext,mask,prefix,modules,selected);rev,revc=score_and_cache(eng,reverse_next,mask,prefix,modules,selected)
        for name in selected:
            off=next(n for n in modules if modules[n]['kind']==modules[name]['kind'] and n not in selected)
            _,bo=score_and_cache(eng,bnext,mask,prefix,modules,[off])
            _,ro=score_and_cache(eng,rnext,mask,prefix,modules,[off])
            blocked,_=score_and_cache(eng,rnext,mask,prefix,modules,patch_values={name:bc[name]})
            inserted,_=score_and_cache(eng,bnext,mask,prefix,modules,patch_values={name:rc[name]})
            offblocked,_=score_and_cache(eng,rnext,mask,prefix,modules,patch_values={off:bo[off]})
            q=bases[name];delta=(rc[name]-bc[name]).float();low=(delta@q)@q.T
            lowread,_=score_and_cache(eng,bnext,mask,prefix,modules,patch_values={name:(bc[name].float()+low)})
            pathrows.append(dict(world_id=pair['world_id'],pair_id=pair['pair_id'],model=eng.name,editor_seed=eng.task['editor_seed'],module=name,offpath_module=off,prefix_position=prefix['position'],B=bscore,R=rscore,R_mediator_B=blocked,B_mediator_R=inserted,R_offpath_B=offblocked,Good=gs,Good_reverse=rev,B_lowrank_R=lowread,effective_mediator_rank=q.shape[1],R_mediator_shift_norm=float(delta.norm()),offpath_shift_norm=float((ro[off]-bo[off]).float().norm()),offpath_matching='same tensor dimension and token position; norms reported separately, not normalized',reverse_mediator_shift_norm=float((revc[name]-gc[name]).float().norm()),blocked_gain_removed=rscore['margin']-blocked['margin'],offpath_gain_removed=rscore['margin']-offblocked['margin'],inserted_gain=inserted['margin']-bscore['margin'],upstream_gain=rscore['margin']-bscore['margin'],meaning='candidate upstream–mediator–readout evidence at a fixed gold prefix; does not identify unique/full circuit'))
    jsonl(folder/'paths.jsonl',pathrows);atomic_torch_save(folder/'module_bases.pt',bases)
    doses=[];divergences=[]
    for pair in contexts[:8]:
        bad,good,mask=load_state(pair);w=pair['world'];op=eng.ed[pair['operation']];nxt=advance('time',0,pair['operation'])
        for alpha in (0,.25,.5,1.0):
            dose=dict(spec,alpha=alpha);h,comp,_,_=get_patch(eng,pair,bad,good,mask,dose,pca)
            now=eng.confidence(h,mask,render(w,0,0),competitor=render(w,1,0))
            after=eng.confidence(op(h,mask),mask,render(w,nxt,0),competitor=render(w,0,0))
            doses.append(dict(world_id=pair['world_id'],alpha=alpha,current=now,next=after,patch_norm=float(comp.norm()),current_joint=eng.evaluate(h,mask,w,0,0)['success'],next_joint=eng.evaluate(op(h,mask),mask,w,nxt,0)['success'],interpretation='finite dose; first-divergent token margins are local prefix scores'))
        if len(divergences)<4:
            for label,bh,gh,target,competitor in [('current',bad,good,render(w,0,0),render(w,1,0)),('next',op(bad,mask),op(good,mask),render(w,nxt,0),render(w,0,0))]:
                lb,y=eng.logits(bh,mask,target);lg,_=eng.logits(gh,mask,target);alt=eng.labels([competitor]);pos=next(i for i in range(min(y.shape[1],alt.shape[1])) if int(y[0,i])!=int(alt[0,i]))
                p=lg[0,pos].log_softmax(-1);q=lb[0,pos].log_softmax(-1);mix=torch.logaddexp(p,q)-__import__('math').log(2)
                divergences.append(dict(world_id=pair['world_id'],stage=label,position=pos,KL_good_bad=float((p.exp()*(p-q)).sum()),JS=float(.5*((p.exp()*(p-mix)).sum()+(q.exp()*(q-mix)).sum())),full_distributions_saved=False))
    jsonl(folder/'dose_curves.jsonl',doses);jsonl(folder/'key_position_divergences.jsonl',divergences)
    token_controls=[]
    for pair in contexts[:16]:
        bad,good,mask=load_state(pair);delta=(good.float()-bad.float())*mask[...,None]
        h,comp,actual,_=get_patch(eng,pair,bad,good,mask,dict(method='token',alpha=1),pca)
        token_controls.append(evaluate_condition(eng,pair,h,mask,'token_span_aux',actual,comp,'primary',[pair['operation']]))
        reversed_h=torch.where(mask.bool()[...,None],(good.float()-comp).to(good.dtype),good)
        token_controls.append(evaluate_condition(eng,pair,reversed_h,mask,'reverse_token_span_aux',dict(actual,reverse=True),-comp,'primary',[pair['operation']]))
        for seed in RANDOM_SEEDS:
            rc,meta=random_component(pair,delta,mask,comp,actual,seed)
            rh=torch.where(mask.bool()[...,None],(bad.float()+rc).to(bad.dtype),bad)
            token_controls.append(evaluate_condition(eng,pair,rh,mask,f'random_token_positions_{seed}',dict(actual,positions=meta['random_positions'],**meta),rc,'primary',[pair['operation']]))
    jsonl(folder/'token_position_controls.jsonl',token_controls)
    return dict(n_worlds=len(pairs),selected=selected,readout_only=True,resources=eng.resources())
