"""Rank16, one-pass latent editors. Training gold enters losses only."""
import copy
import random
import shutil
import time
import torch
import torch.nn.functional as F
from .common import *
from .engine import editors,render,advance,hooks,first
from .readout import token_sites

def export(path,ed,step,meta):
    temporary=path.with_suffix('.tmp');torch.save(dict(editor={k:v.detach().cpu() for k,v in ed.state_dict().items()},step=step,metadata=meta),temporary);temporary.replace(path)

@torch.no_grad()
def source_record(eng,w,state,source):
    if source=='natural':h,m=eng.encode([render(w,state)])
    else:h,m=eng.history(w,state,history='future_plus' if state<3 else 'past_minus')
    return dict(world=w,state=state,source=source,hidden=h[0].cpu(),mask=m[0].cpu())

@torch.no_grad()
def cache_sources(eng,worlds,folder):
    cache={};parts=folder/'source_worlds';parts.mkdir(exist_ok=True)
    reuse_path=ROOT/'configs/S3_REUSE_LOCK.json'
    reuse=next((r for r in read(reuse_path)['entries'] if r['seed']==eng.task['seed']),None) if reuse_path.exists() else None
    for i,w in enumerate(worlds):
        saved=parts/(w['world_id']+'.pt')
        if reuse:
            original=reuse['source_worlds'][w['world_id']]
            assert sha(original['path'])==original['sha256'],'Reused source memory changed'
            if not saved.exists():shutil.copy2(original['path'],saved)
            assert sha(saved)==original['sha256'],'Reused source memory differs'
        if saved.exists():
            cache.update(torch.load(saved,map_location='cpu',weights_only=False));continue
        current={}
        for s in range(-3,4):
            for source in ('natural','history'):
                key=(w['world_id'],s,source);current[key]=source_record(eng,w,s,source)
        tmp=saved.with_suffix('.tmp');torch.save(current,tmp);tmp.replace(saved);cache.update(current)
        if (i+1)%16==0:print('source cache',i+1,len(worlds),flush=True)
    torch.save(cache,folder/'source_cache.pt');return cache

@torch.no_grad()
def validate(eng,ed,worlds,cache,folder,name):
    path=folder/(name+'_validation.jsonl');records=rows(path) if path.exists() else []
    completed={r['world_id'] for r in records}
    reference_path=ROOT/'configs/S3_REUSE_LOCK.json';prior={}
    if reference_path.exists():
        item=next(r for r in read(reference_path)['entries'] if r['seed']==eng.task['seed'])
        assert sha(item['validation'])==item['validation_sha256']
        for r in rows(item['validation']):
            key=(r['world_id'],r['state'],r['source'])
            if key in prior:assert prior[key]==r['current']
            prior[key]=r['current']
    for wi,w in enumerate(worlds):
        if w['world_id'] in completed:continue
        for state in range(-3,4):
            for op in ('plus','minus'):
                try:next_state=advance('time',state,op)
                except ValueError:continue
                for source in ('natural','history'):
                    r=cache[(w['world_id'],state,source)];h=r['hidden'][None].cuda();m=r['mask'][None].cuda()
                    current=prior[(w['world_id'],state,source)] if prior else eng.evaluate(h,m,w,state)
                    edited=ed[op](h,m);pred=eng.evaluate(edited,m,w,next_state)
                    records.append(dict(world_id=w['world_id'],split=w['split'],state=state,operation=op,source=source,method=name,current=current,prediction=pred,update_norm=float((edited-h).float()[m.bool()].norm()),base_norm=float(h.float()[m.bool()].norm()),extra_test_input=False,inference_editor_forwards=1))
        jsonl(path,records)
        if (wi+1)%8==0:print('validation',name,wi+1,flush=True)
    jsonl(folder/(name+'_validation.jsonl'),records)
    scores=[r['prediction']['score'] for r in records]
    return dict(joint=sum(r['success'] for r in scores)/len(scores),content=sum(r['preserved'] for r in scores)/len(scores),target=sum(r['target'] for r in scores)/len(scores),denominator=len(scores),worlds=len(worlds))

def loss(eng,ed,op,h,m,targets,keep_weight,size_weight,mechanism_sites,scales,mechanism_weight,return_details=False):
    labels=eng.labels(targets);student=ed[op](h,m);assert torch.equal(student[m==0],h[m==0])
    keep=torch.zeros(labels.shape,device='cuda',dtype=torch.bool)
    if keep_weight or mechanism_weight:
        for i,target in enumerate(targets):
            groups=token_sites(eng,target)
            for j,g in enumerate(groups):
                if j<keep.shape[1] and g=='content':keep[i,j]=True
    modules=dict(eng.cross);teacher_sites={};student_sites={}
    def capture(storage,key):
        def hook(mod,args,out):storage[key]=first(out)
        return hook
    teacher_logits=None
    if keep_weight or mechanism_weight:
        with torch.no_grad(),hooks([(modules[n],capture(teacher_sites,n),False) for n in mechanism_sites]):teacher_logits=eng.logits(h,m,labels)
    with hooks([(modules[n],capture(student_sites,n),False) for n in mechanism_sites]):logits=eng.logits_with_memory_grad(student,m,labels)
    token_loss=F.cross_entropy(logits.reshape(-1,logits.shape[-1]),labels.reshape(-1),ignore_index=-100,reduction='none').reshape(labels.shape)
    ce=(token_loss.sum(1)/(labels!=-100).sum(1)).mean()
    size=((student-h).float().square().sum(-1)*m).sum()/(m.sum()*h.shape[-1])
    size/=((h.float().square().sum(-1)*m).sum()/(m.sum()*h.shape[-1])+1e-9)
    kl=logits.new_tensor(0);mech=logits.new_tensor(0)
    if keep_weight and keep.any():
        t=teacher_logits.detach().log_softmax(-1);s=logits.log_softmax(-1);kl=(t.exp()*(t-s)).sum(-1)[keep].mean()
    if mechanism_weight and keep.any():
        mech=sum((student_sites[n].float()-teacher_sites[n].detach().float()).square().mean(-1)[keep].mean()/max(scales[n],1e-9) for n in mechanism_sites)/len(mechanism_sites)
    total=ce+keep_weight*kl+mechanism_weight*mech+size_weight*size
    metrics=dict(CE=float(ce.detach()),KL=float(kl.detach()),mechanism=float(mech.detach()),size=float(size.detach()),keep_available_fraction=float(keep.any(1).float().mean()))
    if return_details:
        return total,metrics,dict(terms={'CE':ce,'KL':kl,'mechanism':mech,'size':size},keep_mask=keep,
            labels=labels,teacher_logits_requires_grad=teacher_logits.requires_grad if teacher_logits is not None else None,
            teacher_sites_require_grad={n:z.requires_grad for n,z in teacher_sites.items()},
            student_sites_require_grad={n:z.requires_grad for n,z in student_sites.items()})
    return total,metrics

def train_one(eng,cache,worlds,seed,method,keep_weight,mechanism_weight,sites,scales,folder):
    ed=editors(eng.d,seed);opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0.)
    logs=[];meta=dict(method=method,seed=seed,rank=16,keep_weight=keep_weight,mechanism_weight=mechanism_weight,size_weight=.001,sites=sites,scales=copy.deepcopy(scales),updates=400,batch=16,microbatch=2,lr=.001,inference_inputs=['H','mask','operation'])
    start=time.monotonic();resume_path=folder/'training_state.pt';first_update=0;previous_wall=0.
    if resume_path.exists():
        saved=torch.load(resume_path,map_location='cuda',weights_only=False)
        assert saved['metadata']==meta,'Resume configuration changed'
        ed.load_state_dict(saved['editor']);opt.load_state_dict(saved['optimizer']);logs=saved['logs'];first_update=saved['next_update'];previous_wall=saved['wall_seconds']
        torch.set_rng_state(saved['torch_rng'].cpu());torch.cuda.set_rng_state_all([s.cpu() for s in saved['cuda_rng']])
    for update in range(first_update,400):
        op='plus' if update%2==0 else 'minus';states=list(range(-2,4)) if op=='plus' else list(range(-3,3))
        rng=random.Random(seed*100000+update);draws=[]
        for source in ('natural','history'):
            for j in range(8):
                w=rng.choice(worlds);state=states[(update//2*8+j)%len(states)];draws.append(cache[(w['world_id'],state,source)])
        opt.zero_grad(set_to_none=True);values=[]
        for offset in range(0,16,2):
            r=draws[offset:offset+2]
            h=torch.nn.utils.rnn.pad_sequence([x['hidden'] for x in r],batch_first=True,padding_value=0).cuda()
            m=torch.nn.utils.rnn.pad_sequence([x['mask'] for x in r],batch_first=True,padding_value=0).cuda()
            targets=[render(x['world'],advance('time',x['state'],op)) for x in r]
            objective,components=loss(eng,ed,op,h,m,targets,keep_weight,.001,sites,scales,mechanism_weight);(objective*len(r)/16).backward();values.append(components)
        assert all(p.grad is None for p in eng.model.parameters())
        assert any(p.grad is not None and p.grad.norm()>0 for p in ed[op].parameters())
        torch.nn.utils.clip_grad_norm_(ed.parameters(),1.,error_if_nonfinite=True);opt.step()
        logs.append(dict(update=update+1,operation=op,draws=[dict(world_id=r['world']['world_id'],state=r['state'],source=r['source']) for r in draws],**{k:sum(v[k] for v in values)/len(values) for k in values[0]}))
        if (update+1)%20==0:jsonl(folder/'training.jsonl',logs);print(method,seed,update+1,logs[-1]['CE'],flush=True)
        if update+1 in (200,400):export(folder/f'update{update+1}.pt',ed,update+1,meta)
        state=dict(editor=ed.state_dict(),optimizer=opt.state_dict(),logs=logs,next_update=update+1,metadata=meta,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),wall_seconds=previous_wall+time.monotonic()-start)
        temporary=resume_path.with_suffix('.tmp');torch.save(state,temporary);temporary.replace(resume_path)
    jsonl(folder/'training.jsonl',logs);dump(folder/'TRAINING_COMPLETE.json',dict(metadata=meta,wall_seconds=previous_wall+time.monotonic()-start,checkpoints=[dict(path=str(p),sha256=sha(p)) for p in folder.glob('update*.pt')],editor_parameters=sum(p.numel() for p in ed.parameters()),decoder_parameters_updated=0,update_matched=True,teacher_forwards_per_update=8 if keep_weight or mechanism_weight else 0,student_forwards_per_update=8,backwards_per_update=8,resumed_from_update=first_update))
    reuse=next((r for r in read(ROOT/'configs/S3_REUSE_LOCK.json')['entries'] if r['seed']==seed),None) if (ROOT/'configs/S3_REUSE_LOCK.json').exists() else None
    if reuse:
        assert sha(reuse['training_draws'])==reuse['training_draws_sha256']
        reference=rows(reuse['training_draws'])
        assert len(reference)==len(logs)==400
        assert all((a['operation'],a['draws'])==(b['operation'],b['draws']) for a,b in zip(reference,logs)), 'Minibatch sequence differs from Plain'
        dump(folder/'MATCHED_DRAW_ACCEPTANCE.json',dict(passed=True,updates=400,seed=seed,reference= reuse['training_draws'],reference_sha256=reuse['training_draws_sha256']))
    return ed

def reuse_plain(eng,folder):
    item=next(r for r in read(ROOT/'configs/S3_REUSE_LOCK.json')['entries'] if r['seed']==eng.task['seed'])
    assert sha(item['checkpoint'])==item['checkpoint_sha256'] and sha(item['validation'])==item['validation_sha256']
    original=Path(item['checkpoint']).parent;dest=folder/'Plain';dest.mkdir(exist_ok=True)
    for name in ('update200.pt','update400.pt','training.jsonl','Plain_validation.jsonl','TRAINING_COMPLETE.json'):
        shutil.copy2(original/name,dest/name)
    result=read(item['summary'])['validation']
    dump(dest/'REUSE_RECEIPT.json',dict(seed=eng.task['seed'],checkpoint_sha256=item['checkpoint_sha256'],validation_sha256=item['validation_sha256'],source='completed S3_PLAIN run',additional_Plain_updates=0,additional_Plain_neural_forwards=0,original_GPU_allocation_already_in_ledger=True))
    return dict(method='Plain',selection_score=result,path=str(dest/'update400.pt'),reused=True)

def run(eng,folder):
    lock=read(ROOT/'configs/MECHANISM_LOCK.json');seed=eng.task['seed'];ws=rows(ROOT/'configs/worlds.jsonl');train=[w for w in ws if w['split']=='train'];validation=[w for w in ws if w['split']=='validation']
    assert read(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json')['reviewed_by_human'],'Required manual content-mask review missing'
    cache=cache_sources(eng,train+validation,folder);summaries=[]
    if seed==42:
        summaries.append(reuse_plain(eng,folder))
        output=[]
        for kw in (.1,1.):
            name='Output-only_k'+str(kw);mf=folder/name;mf.mkdir(exist_ok=True);ed=train_one(eng,cache,train,seed,name,kw,0.,[],{},mf);vs=validate(eng,ed,validation,cache,mf,name);output.append(dict(method='Output-only',keep_weight=kw,selection_score=vs,path=str(mf/'update400.pt')))
        best=min(output,key=lambda r:(-r['selection_score']['joint'],-r['selection_score']['content'],r['keep_weight']));summaries+=output;kw=best['keep_weight']
        if lock['selected']:
            proposed=[];randoms=[]
            for mw in (.1,1.):
                for method,sites in [('Mechanism-guided',lock['selected']),('Random-site',lock['random_sites'])]:
                    name=method+'_m'+str(mw);mf=folder/name;mf.mkdir(exist_ok=True);ed=train_one(eng,cache,train,seed,name,kw,mw,sites,lock['scale_squared'],mf);vs=validate(eng,ed,validation,cache,mf,name)
                    item=dict(method=method,keep_weight=kw,mechanism_weight=mw,selection_score=vs,path=str(mf/'update400.pt'))
                    (proposed if method=='Mechanism-guided' else randoms).append(item);summaries.append(item)
            eligible=[r for r in proposed if r['selection_score']['content']>=best['selection_score']['content']-.02]
            chosen=min(eligible,key=lambda r:(-r['selection_score']['joint'],r['mechanism_weight'])) if eligible else min(proposed,key=lambda r:r['mechanism_weight'])
            chosen['content_gate_passed']=bool(eligible);randomchosen=next(r for r in randoms if r['mechanism_weight']==chosen['mechanism_weight'])
            selected=[summaries[0],best,chosen,randomchosen]
        else:selected=[summaries[0],best]
        choice=dict(methods=selected,keep_weight=kw,mechanism_weight=next((r['mechanism_weight'] for r in selected if r['method']=='Mechanism-guided'),None),selection='update400, validation joint after content constraint; no test',all_validation_candidates=summaries,test_unopened=True)
        dump(folder/'TRAINING_SELECTION_LOCK.json',choice)
    else:
        selection=read(ROOT/'configs/TRAINING_SELECTION_LOCK.json');kw=selection['keep_weight'];mw=selection['mechanism_weight']
        for method in [r['method'] for r in selection['methods']]:
            if method=='Plain':summaries.append(reuse_plain(eng,folder));continue
            sites=lock['selected'] if method=='Mechanism-guided' else lock['random_sites'] if method=='Random-site' else []
            mf=folder/method;mf.mkdir(exist_ok=True);ed=train_one(eng,cache,train,seed,method,0 if method=='Plain' else kw,0 if method in ('Plain','Output-only') else mw,sites,lock['scale_squared'],mf);vs=validate(eng,ed,validation,cache,mf,method);summaries.append(dict(method=method,selection_score=vs,path=str(mf/'update400.pt')))
    dump(folder/'TRAINING_SUMMARY.json',summaries)
    return dict(passed=True,worlds=len(train)+len(validation),seed=seed,methods=summaries,test_accessed=0,mechanism_status=lock['status'],resources=eng.resources())

def run_plain(eng,folder):
    seed=eng.task['seed'];ws=rows(ROOT/'configs/worlds.jsonl');train=[w for w in ws if w['split']=='train'];validation=[w for w in ws if w['split']=='validation']
    cache=cache_sources(eng,train+validation,folder);mf=folder/'Plain';mf.mkdir(exist_ok=True)
    ed=train_one(eng,cache,train,seed,'Plain',0.,0.,[],{},mf);result=validate(eng,ed,validation,cache,mf,'Plain')
    dump(folder/'PLAIN_SUMMARY.json',result)
    return dict(passed=True,worlds=256,seed=seed,method='Plain',rank=16,updates=400,validation=result,checkpoint=str(mf/'update400.pt'),checkpoint_sha256=sha(mf/'update400.pt'),human_keep_mask_not_used=True,test_accessed=0,resources=eng.resources())
