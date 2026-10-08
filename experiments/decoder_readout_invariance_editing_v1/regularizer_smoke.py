"""Slurm-only acceptance for keep KL and actual/random readout gradients."""
import torch
from .common import *
from .training import cache_sources,loss
from .engine import editors,render,advance


def grad_norm(value,params):
    gradients=torch.autograd.grad(value,params,allow_unused=True,retain_graph=True)
    valid=[g for g in gradients if g is not None]
    assert valid and all(torch.isfinite(g).all() for g in valid)
    norm=float(sum(g.float().square().sum() for g in valid).sqrt())
    assert norm>1e-10,'Regularizer has no editor gradient after fixed CE warmup'
    return norm


def run(eng,folder):
    review=read(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json');assert review['reviewed_by_human']
    ws=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='train'][:8]
    cache=cache_sources(eng,ws,folder);lock=read(ROOT/'configs/MECHANISM_LOCK.json')
    states=[-2,-1,0,1,2,0,3,-3]
    data=[]
    for i,w in enumerate(ws):
        source='natural' if i<4 else 'history';op='plus' if i%2==0 else 'minus'
        r=cache[(w['world_id'],states[i],source)]
        data.append(dict(record=r,operation=op,target=render(w,advance('time',states[i],op))))
    results=[];predictions=[];all_logs=[]
    for method,sites in [('Output-only',[]),('Mechanism-guided',lock['selected']),('Random-site',lock['random_sites'])]:
        ed=editors(eng.d,42);opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0.)
        sample=data[:2];h=torch.stack([s['record']['hidden'] for s in sample]).cuda();m=torch.stack([s['record']['mask'] for s in sample]).cuda()
        # CE warmup moves away from the exact identity, where KL/MSE gradients vanish.
        for _ in range(2):
            opt.zero_grad(set_to_none=True);v,_=loss(eng,ed,'plus',h,m,[render(s['record']['world'],advance('time',s['record']['state'],'plus')) for s in sample],0,.001,[],{},0);v.backward();opt.step()
        initial_hooks=sum(len(z._forward_hooks)+len(z._forward_pre_hooks) for z in eng.model.modules())
        v,metrics,details=loss(eng,ed,'plus',h,m,[render(s['record']['world'],advance('time',s['record']['state'],'plus')) for s in sample],.1,.001,sites,lock['scale_squared'],.1 if sites else 0,return_details=True)
        assert details['teacher_logits_requires_grad'] is False
        assert all(not z for z in details['teacher_sites_require_grad'].values())
        assert all(details['student_sites_require_grad'].values())
        assert not (details['keep_mask'] & (details['labels']==-100)).any()
        assert details['keep_mask'].sum(1).tolist()==[5,5]
        params=list(ed.parameters());probes={'CE':grad_norm(details['terms']['CE'],params),'KL':grad_norm(details['terms']['KL'],params)}
        if sites:probes['mechanism']=grad_norm(details['terms']['mechanism'],params)
        assert sum(len(z._forward_hooks)+len(z._forward_pre_hooks) for z in eng.model.modules())==initial_hooks
        # Reset to matched identity init for the eight-world regularized overfit.
        ed=editors(eng.d,42);opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0.);logs=[]
        for update in range(120):
            opt.zero_grad(set_to_none=True);values=[];objective_value=0.
            for op in ('plus','minus'):
                indices=[i for i,s in enumerate(data) if s['operation']==op]
                for offset in (0,2):
                    samples=[data[i] for i in indices[offset:offset+2]]
                    h=torch.stack([s['record']['hidden'] for s in samples]).cuda();m=torch.stack([s['record']['mask'] for s in samples]).cuda()
                    objective,components=loss(eng,ed,op,h,m,[s['target'] for s in samples],.1,.001,sites,lock['scale_squared'],.1 if sites else 0)
                    (objective/4).backward();values.append(components);objective_value+=float(objective.detach())/4
            assert all(p.grad is None for p in eng.model.parameters())
            assert all(p.grad is None for p in eng.ed.parameters())
            torch.nn.utils.clip_grad_norm_(ed.parameters(),1.,error_if_nonfinite=True);opt.step()
            logs.append(dict(method=method,update=update+1,total=objective_value,**{key:sum(v[key] for v in values)/len(values) for key in values[0]}))
        assert logs[-1]['total']<logs[0]['total'],'Fixed eight-world regularized loss did not decrease'
        for sample in data:
            r=sample['record'];h=r['hidden'][None].cuda();m=r['mask'][None].cuda();op=sample['operation']
            p=eng.evaluate(ed[op](h,m),m,r['world'],advance('time',r['state'],op))
            predictions.append(dict(method=method,world_id=r['world']['world_id'],source=r['source'],state=r['state'],operation=op,prediction=p))
        rs=[r for r in predictions if r['method']==method]
        results.append(dict(method=method,isolated_editor_gradient_norms=probes,teacher_detached=True,student_readout_retains_gradient=True,keep_tokens_in_probe=[5,5],hooks_cleaned=True,updates=120,initial_loss=logs[0]['total'],final_loss=logs[-1]['total'],initial_CE=logs[0]['CE'],final_CE=logs[-1]['CE'],joint_numerator=sum(r['prediction']['score']['success'] for r in rs),denominator=8))
        all_logs.extend(logs);print('regularizer smoke',results[-1],flush=True)
    jsonl(folder/'regularizer_smoke_predictions.jsonl',predictions);jsonl(folder/'regularizer_smoke_training.jsonl',all_logs)
    result=dict(passed=True,worlds=8,checks=results,review_lock_sha256=sha(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json'),train_only=True,test_accessed=0,resources=eng.resources())
    dump(folder/'REGULARIZER_ACCEPTANCE.json',result)
    return result
