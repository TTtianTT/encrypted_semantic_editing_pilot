"""Locked S1/S2 confirmation called only inside an authorized S4 worker."""
import torch
from .common import *
from .engine import hooks,render
from .readout import distribution,token_sites,ALPHAS,RANDOM_SEEDS
from .metrics import effective_ids


@torch.no_grad()
def confirm(eng,w,ps,folder,world_index):
    lock=read(ROOT/'configs/MECHANISM_LOCK.json');sites=lock['selected']+lock['random_sites']
    modules=dict(eng.cross);conditions=[];curves=[];readouts=[];bridges=[]
    for pair,a,b,mask in ps:
        native=torch.tensor(pair['a']['token_ids'],device='cuda')[None];labels=native[:,1:]
        la=eng.logits(a,mask,decoder_ids=native[:,:-1]);lb=eng.logits(b,mask,decoder_ids=native[:,:-1]);groups=token_sites(eng,pair['a']['text'])
        readouts.extend(dict(world_id=w['world_id'],seed=eng.task['seed'],source_pair=pair['source_pair'],**r) for r in distribution(la,lb,labels,groups))
        for op,state in [('plus',-1),('minus',1)]:
            aa=eng.evaluate(eng.ed[op](a,mask),mask,w,state);bb=eng.evaluate(eng.ed[op](b,mask),mask,w,state)
            bridges.append(dict(world_id=w['world_id'],seed=eng.task['seed'],source_pair=pair['source_pair'],operation=op,panel_A=True,panel_B=aa['token_ids']!=bb['token_ids'],legacy_accuracy_fork=aa['score']['success']!=bb['score']['success'],a_next=aa,b_next=bb))
        if eng.task['seed']!=42:continue
        if world_index<8:
            delta=(b-a).float()*mask[...,None];directions=[('real',delta,None)]
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
                for alpha in ALPHAS:
                    hp=(a.float()+alpha*d).to(a.dtype);pred=eng.evaluate(hp,mask,w,0)
                    curves.append(dict(world_id=w['world_id'],split='amended_test_iid',seed=eng.task['seed'],source_pair=pair['source_pair'],direction=kind,random_seed=seed,alpha=alpha,delta_norm=float((hp-a).float()[mask.bool()].norm()),per_token_energy_max_error=float((d.norm(dim=-1)-delta.norm(dim=-1)).abs().max()),text_preserved=pred['text']==pair['a']['text'],tokens_preserved=effective_ids(pred['token_ids'],eng.eos)[0]==effective_ids(pair['a']['token_ids'],eng.eos)[0],prediction=pred,subset_scope='fixed8_world_exploratory'))
    if ps and eng.task['seed']==42:
        pair,a,b,mask=ps[0];native=torch.tensor(pair['a']['token_ids'],device='cuda')[None];labels=native[:,1:];groups=token_sites(eng,pair['a']['text']);content=[j for j,g in enumerate(groups) if g=='content' and j<labels.shape[1]]
        assert content
        projected=[eng.projected(a),eng.projected(b)]
        for name in sites:
            mod=modules[name]
            for side,recipient,donorproj,selfproj in [('a',a,projected[1],projected[0]),('b',b,projected[0],projected[1])]:
                reference=eng.logits(recipient,mask,decoder_ids=native[:,:-1])
                with eng.kv_hooks(selfproj,[name]):same=eng.logits(recipient,mask,decoder_ids=native[:,:-1])
                assert torch.equal(reference,same)
                for scope,head in [('layer',None),('head',0)]:
                    queries=[]
                    for condition,k,v in [('AA',False,False),('BA',True,False),('AB',False,True),('BB',True,True)]:
                        captured=[]
                        with eng.kv_hooks(donorproj,[name],k=k,v=v,head=head),hooks([(mod.q_proj,lambda module,args,out:captured.append(out.detach().clone()),False)]):changed=eng.logits(recipient,mask,decoder_ids=native[:,:-1])
                        queries.append(captured[0]);metrics=distribution(reference,changed,labels,groups)
                        with eng.kv_hooks(donorproj,[name],k=k,v=v,head=head):free=eng.evaluate(recipient,mask,w,0)
                        conditions.append(dict(world_id=w['world_id'],split='amended_test_iid',seed=42,module=name,source_pair=pair['source_pair'],recipient=side,scope=scope,head=head,condition=condition,free=free,content_margin_shift=sum(metrics[j]['b_margin']-metrics[j]['a_margin'] for j in content)/len(content),mean_JS=sum(r['JS'] for r in metrics)/len(metrics),query_path='recipient actual common prefix, same local Q in four conditions'))
                    assert all(torch.equal(q,queries[0]) for q in queries)
                wrong=dict(w,color='red' if w['color']!='red' else 'blue')
                # Unlike the original implementation, no reserved or newly unsealed
                # test world may become a donor. This whitelist is metadata-only.
                forbidden={core(x) for x in rows(ROOT/'configs/worlds.jsonl') if x['split'] in ('test_iid','reserved_iid')}
                old={tuple(x['core_content']) for x in rows(ROOT/'configs/historical_exposure_registry.jsonl')}
                old|={core(x) for x in rows(ROOT/'configs/worlds.jsonl') if x['split'] in ('train','validation')}
                if core(wrong) in forbidden or core(wrong) not in old:
                    conditions.append(dict(world_id=w['world_id'],split='amended_test_iid',seed=42,module=name,recipient=side,scope='layer',condition='NORMAL_COLOR_VALUE_RESAMPLE',status='CONTROL_CORE_PROVENANCE_BLOCKED'));continue
                donor,dm=eng.encode([render(wrong,0)])
                if not torch.equal(dm,mask):
                    conditions.append(dict(world_id=w['world_id'],split='amended_test_iid',seed=42,module=name,recipient=side,scope='layer',condition='NORMAL_COLOR_VALUE_RESAMPLE',status='SHAPE_MASK_MISMATCH'));continue
                with eng.kv_hooks(eng.projected(donor),[name],k=False,v=True):changed=eng.logits(recipient,mask,decoder_ids=native[:,:-1]);free=eng.evaluate(recipient,mask,w,0)
                metrics=distribution(reference,changed,labels,groups)
                conditions.append(dict(world_id=w['world_id'],split='amended_test_iid',seed=42,module=name,recipient=side,scope='layer',condition='NORMAL_COLOR_VALUE_RESAMPLE',status='COMPLETED',control_core=list(core(wrong)),baseline=pair[side],free=free,content_margin_shift=sum(metrics[j]['b_margin']-metrics[j]['a_margin'] for j in content)/len(content),target_damage=not free['score']['target'],content_damage=not free['score']['preserved'],zeroing_OOD=False))
    for name,records in [('readouts',readouts),('causal',conditions),('curves',curves),('bridge',bridges)]:jsonl(folder/(w['world_id']+'_'+name+'.jsonl'),records)
    return dict(readout_tokens=len(readouts),causal_conditions=len(conditions),curve_points=len(curves),bridges=len(bridges))
