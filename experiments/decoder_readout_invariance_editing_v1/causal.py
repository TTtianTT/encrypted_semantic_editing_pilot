"""Exact native projection/readout interventions; train/validation only."""
import torch
from .common import *
from .engine import hooks,first,replace,render
from .readout import pairs,distribution,token_sites

@torch.no_grad()
def run(eng,folder):
    selection=read(ROOT/'configs/S2_CANDIDATES.json');candidate=selection['candidate'];offpath=selection['random_site']
    modules=dict(eng.cross);assert candidate in modules and offpath in modules
    ws=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='train'][:32]+[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='validation'][:32]
    records=[];scale={candidate:[],offpath:[]};validation=[]
    for i,w in enumerate(ws):
        ps,states,pred=pairs(eng,w,folder)
        if not ps:continue
        pair,a,b,mask=ps[0];ids=torch.tensor(pair['a']['token_ids'],device='cuda')[None];labels=ids[:,1:];groups=token_sites(eng,pair['a']['text']);content=[j for j,g in enumerate(groups) if g=='content' and j<labels.shape[1]]
        assert content
        proj_a,proj_b=eng.projected(a),eng.projected(b)
        for name in [candidate,offpath]:
            mod=modules[name]
            head_dim=mod.head_dim;head=int(selection.get('head',0))
            for side,recipient,donor,recipient_proj,donorproj in [('a',a,b,proj_a,proj_b),('b',b,a,proj_b,proj_a)]:
                reference=eng.logits(recipient,mask,decoder_ids=ids[:,:-1]);queries=[];readout_cache=[]
                with hooks([(mod,lambda mod,args,out:readout_cache.append(first(out).detach().clone()),False)]):eng.logits(recipient,mask,decoder_ids=ids[:,:-1])
                z=readout_cache[0]
                if w['split']=='train':scale[name].append(float(z[:,content].square().mean()))
                # Self replacement and handle cleanup are exact on the native network.
                with eng.kv_hooks(recipient_proj,[name]):selflp=eng.logits(recipient,mask,decoder_ids=ids[:,:-1])
                assert torch.equal(selflp,reference)
                # Fixed attention pattern is an explicitly modified diagnostic network.
                qcache=[];avcache=[]
                output_projection=mod.o_proj if eng.chat else mod.out_proj
                with hooks([(mod.q_proj,lambda module,args,out:qcache.append(out.detach().clone()),False),(output_projection,lambda module,args:avcache.append(args[0].detach().clone()),True)]):eng.logits(recipient,mask,decoder_ids=ids[:,:-1])
                if not eng.chat:
                    heads=mod.num_heads;q=qcache[0].view(1,-1,heads,mod.head_dim).transpose(1,2)
                    def pattern(projected):
                        key=projected[(name,'k')].view(1,-1,heads,mod.head_dim).transpose(1,2)
                        scores=q@key.transpose(-1,-2)*mod.scaling
                        scores=scores.masked_fill(~mask.bool()[:,None,None,:],-torch.inf)
                        return scores.softmax(-1)
                    aa=pattern(recipient_proj);ab=pattern(donorproj)
                    va=recipient_proj[(name,'v')].view(1,-1,heads,mod.head_dim).transpose(1,2);vb=donorproj[(name,'v')].view(1,-1,heads,mod.head_dim).transpose(1,2)
                    native_av=(aa@va).transpose(1,2).reshape_as(avcache[0]);reconstruction_error=float((native_av-avcache[0]).abs().max())
                    assert reconstruction_error<=3e-6,'Native SDPA AV reconstruction failed local acceptance'
                    delta_exact=ab@vb-aa@va;decomposed=(ab-aa)@va+aa@(vb-va)+(ab-aa)@(vb-va)
                    decomposition_error=float((delta_exact-decomposed).abs().max());assert decomposition_error<=1e-5
                    for label,pattern_value,value in [('FIX_A_REPLACE_V',aa,vb),('FIX_V_REPLACE_K',ab,va)]:
                        changed=(pattern_value@value).transpose(1,2).reshape_as(avcache[0])
                        with hooks([(output_projection,lambda module,args,changed=changed:(changed,)+args[1:],True)]):lp=eng.logits(recipient,mask,decoder_ids=ids[:,:-1])
                        metrics=distribution(reference,lp,labels,groups)
                        records.append(dict(world_id=w['world_id'],split=w['split'],module=name,scope='layer',recipient=side,condition=label,free_generation_status='NOT_RUN_DIAGNOSTIC_TEACHER_PREFIX_ONLY',content_margin_shift=sum(metrics[j]['b_margin']-metrics[j]['a_margin'] for j in content)/len(content),mean_JS=sum(r['JS'] for r in metrics)/len(metrics),diagnostic_modified_network=True,reconstructed_A_not_materialized_SDPA_probs=True,local_AV_max_error=reconstruction_error,KV_interaction_decomposition_max_error=decomposition_error,recipient_query_fixed=True))
                for scope,head_id in [('layer',None),('head',head)]:
                    current_queries=[]
                    for condition,k,v in [('AA',False,False),('BA',True,False),('AB',False,True),('BB',True,True)]:
                        query=[]
                        with eng.kv_hooks(donorproj,[name],k=k,v=v,head=head_id),hooks([(mod.q_proj,lambda mod,args,out:query.append(out.detach().clone()),False)]):lp=eng.logits(recipient,mask,decoder_ids=ids[:,:-1])
                        current_queries.append(query[0]);metrics=distribution(reference,lp,labels,groups)
                        with eng.kv_hooks(donorproj,[name],k=k,v=v,head=head_id):free=eng.evaluate(recipient,mask,w,0)
                        records.append(dict(world_id=w['world_id'],split=w['split'],module=name,scope=scope,head=head_id,recipient=side,condition=condition,free=free,content_margin_shift=sum(metrics[j]['b_margin']-metrics[j]['a_margin'] for j in content)/len(content),mean_JS=sum(r['JS'] for r in metrics)/len(metrics),query_path='recipient recomputed, no gold future activations'))
                    assert all(torch.equal(q,current_queries[0]) for q in current_queries),'Local recipient query changed across K/V conditions'
                # Matched normal source value resampling; protects content not judged by attention mass.
                wrong_world=dict(w,color='red' if w['color']!='red' else 'blue');wrong,wm=eng.encode([render(wrong_world,0)])
                if torch.equal(mask,wm):
                    wrongproj=eng.projected(wrong)
                    with eng.kv_hooks(wrongproj,[name],k=False,v=True):lp=eng.logits(recipient,mask,decoder_ids=ids[:,:-1]);free=eng.evaluate(recipient,mask,w,0)
                    metrics=distribution(reference,lp,labels,groups)
                    r=dict(world_id=w['world_id'],split=w['split'],module=name,scope='layer',recipient=side,condition='NORMAL_COLOR_VALUE_RESAMPLE',same_shape_mask=True,baseline=pair['a' if side=='a' else 'b'],free=free,content_margin_shift=sum(metrics[j]['b_margin']-metrics[j]['a_margin'] for j in content)/len(content),target_damage=not free['score']['target'],content_damage=not free['score']['preserved'],zeroing_OOD=False)
                    records.append(r)
                    if name==candidate and w['split']=='validation':validation.append(r)
                else:records.append(dict(world_id=w['world_id'],split=w['split'],module=name,condition='NORMAL_COLOR_VALUE_RESAMPLE',status='SHAPE_MASK_MISMATCH'))
        if (i+1)%4==0:jsonl(folder/'causal_conditions.jsonl',records);print('S2 worlds',i+1,flush=True)
    jsonl(folder/'causal_conditions.jsonl',records)
    nworlds=len({r['world_id'] for r in validation});content_damage=sum(r['content_damage'] for r in validation)/max(1,len(validation));target_damage=sum(r['target_damage'] for r in validation)/max(1,len(validation));margin=sum(r['content_margin_shift'] for r in validation)/max(1,len(validation))
    # Gate prelocked before S2; no test-guided component change.
    gate=nworlds>=20 and content_damage>=.1 and content_damage>=target_damage and margin<=-.2
    lock=dict(status='IDENTIFIED_LOCAL_CONTENT_READOUT' if gate else 'MECHANISM_NOT_IDENTIFIED',selected=[candidate] if gate else [],random_sites=[offpath] if gate else [],scale_squared={n:sum(v)/max(1,len(v)) for n,v in scale.items()},validation_worlds=nworlds,validation_side_records=len(validation),content_damage=content_damage,target_damage=target_damage,content_margin_shift=margin,gate=dict(min_worlds=20,content_damage_min=.1,content_damage_gte_target_damage=True,mean_content_margin_shift_max=-.2),site='whole cross-attention after W_O before residual (actual combined A V); only semantic content token positions',support='local content dependency under matched normal value resampling, not unique invariance circuit',independent_test_accessed=0,selection=selection)
    dump(folder/'MECHANISM_LOCK.json',lock)
    return dict(passed=True,status='COMPLETED' if gate else 'NOT_LOCALIZED',worlds=64,mechanism_lock=lock,resources=eng.resources())
