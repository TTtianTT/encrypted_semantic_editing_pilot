import random,time,copy
import torch
from common import *
from backend import editors

def save_checkpoint(path,ed,opt,step,rng,extra):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp')
    torch.save(dict(editor=ed.state_dict(),optimizer=opt.state_dict(),step=step,random=rng.getstate(),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),extra=extra),tmp);tmp.replace(path)

@torch.no_grad()
def dev_nll(eng,ed,rs):
    total=0
    for i in range(0,len(rs),2):
        batch=rs[i:i+2];h,m=eng.cached([r['source'] for r in batch]);op=batch[0]['operation']
        # Keep grouping even when a source state has only one legal operation.
        for operation in ('plus','minus'):
            ix=[j for j,r in enumerate(batch) if r['operation']==operation]
            if ix:
                loss,_=eng.ce(ed[operation](h[ix],m[ix]),m[ix],[batch[j]['target'] for j in ix]);total+=float(loss.sum())
    return total/len(rs)

def train(eng,run,rs,dev,seed,steps,initial=None,pools=None,condition=None):
    run.mkdir(parents=True,exist_ok=True)
    if (run/'complete.json').exists():return load_editor(eng,run/'final.pt')
    ed=editors(eng.d,seed);opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0.0);rng=random.Random(seed);best=float('inf');start=0;log=[]
    if initial:ed.load_state_dict(torch.load(initial,map_location='cuda',weights_only=False)['editor'])
    latest=run/'latest.pt'
    if latest.exists():
        ck=torch.load(latest,map_location='cuda',weights_only=False);ed.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);start=ck['step'];rng.setstate(ck['random']);torch.set_rng_state(ck['torch_rng'].cpu());torch.cuda.set_rng_state_all([v.cpu() for v in ck['cuda_rng']]);best=ck['extra']['best'];log=ck['extra']['log']
    by_op={op:[r for r in rs if r['operation']==op] for op in ('plus','minus')}
    started=time.monotonic()
    for step in range(start,steps):
        op=('plus','minus')[step%2]
        # Independent deterministic per-step draws keep general/old protection
        # byte-identical across S/M even when focus pool sizes differ.
        general_rng=random.Random(seed*100000+step)
        batch=[dict(general_rng.choice(by_op[op])) for _ in range(8 if pools is None else 4)]
        if pools is not None:
            for role in ('focus','old'):
                available=pools[role][op];covered=sorted({r['state'] for r in available});selected=[]
                slot_rng=random.Random(seed*200000+step+(10000000 if role=='old' else 0))
                for slot in range(2):
                    current=covered[((step//2)*2+slot)%len(covered)]
                    selected.append(dict(slot_rng.choice([r for r in available if r['state']==current])))
                if condition=='N':
                    for r in selected:r.pop('hidden',None);r.pop('mask',None)
                batch+=selected
        opt.zero_grad(set_to_none=True);loss_value=0;tokens=0
        for offset in range(0,8,eng.cfg['microbatch']):
            mb=batch[offset:offset+eng.cfg['microbatch']];hs=[];ms=[]
            natural=[r['source'] for r in mb if 'hidden' not in r]
            if natural:nh,nm=eng.cached(natural)
            j=0
            for r in mb:
                if 'hidden' in r:hs.append(r['hidden'].cuda());ms.append(r['mask'].cuda())
                else:hs.append(nh[j]);ms.append(nm[j]);j+=1
            h=torch.stack(hs);m=torch.stack(ms)
            out=ed[op](h,m);assert torch.equal(out[m==0],h[m==0]),'padding edited'
            losses,nt=eng.ce(out,m,[r['target'] for r in mb]);loss=losses.sum()/8;loss.backward();loss_value+=float(loss.detach());tokens+=int(nt.sum())
        assert all(p.grad is None for p in eng.model.parameters()),'Frozen backbone gradient'
        assert any(p.grad is not None and p.grad.norm()>0 for p in ed[op].parameters()),'Editor gradient absent'
        torch.nn.utils.clip_grad_norm_(ed.parameters(),1.,error_if_nonfinite=True);opt.step()
        item=dict(step=step+1,loss=loss_value,supervised_semantic_units=8,target_tokens=tokens,operation=op,world_ids=[r['world_id'] for r in batch],states=[r['state'] for r in batch],roles=['natural']*8 if pools is None else ['natural']*4+['focus']*2+['old']*2)
        if pools is None and (step+1)%100==0:
            value=dev_nll(eng,ed,dev);item['dev_nll']=value
            if value<best:
                best=value;save_checkpoint(run/'best.pt',ed,opt,step+1,rng,dict(best=best,log=log+[item]))
        log.append(item)
        if (step+1)%20==0 or step+1==steps:
            save_checkpoint(latest,ed,opt,step+1,rng,dict(best=best,log=log));dump(run/'progress.json',dict(step=step+1,total=steps,condition=condition,wall_seconds=time.monotonic()-started));print(f'{run.name} step={step+1}/{steps} loss={loss_value:.4f}',flush=True)
        if pools is None and step+1==300:save_checkpoint(run/'step300.pt',ed,opt,step+1,rng,dict(best=best,log=log))
    if pools is None and not (run/'best.pt').exists():save_checkpoint(run/'best.pt',ed,opt,steps,rng,dict(best=best,log=log))
    save_checkpoint(run/'final.pt',ed,opt,steps,rng,dict(best=best,log=log));jsonl(run/'training.jsonl',log);dump(run/'complete.json',dict(step=steps,seed=seed,semantic_units=sum(r['supervised_semantic_units'] for r in log),target_tokens=sum(r['target_tokens'] for r in log),final_sha=digest(run/'final.pt'),best_sha=digest(run/'best.pt') if pools is None else None))
    return ed

def load_editor(eng,path):
    ed=editors(eng.d,0);ed.load_state_dict(torch.load(path,map_location='cuda',weights_only=False)['editor']);return ed.eval()
