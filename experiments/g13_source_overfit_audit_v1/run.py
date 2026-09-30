"""All GPU cache, historical audit, four-arm training and inference in one seed job."""
import argparse, collections, random, time
import torch
from torch import nn
from transformers.modeling_outputs import BaseModelOutput
from common_g13 import *

class Editor(nn.Module):
    def __init__(self):
        super().__init__(); self.b=nn.Parameter(torch.zeros(768)); self.v=nn.Linear(768,16,bias=False); self.u=nn.Linear(16,768,bias=False)
    def forward(self,h,m): return h+(self.b+self.u(self.v(h)))*m[...,None].to(h.dtype)
def editor(seed,method='T0',train=False):
    p=original(seed) if method=='T0' else G12/f'checkpoints/{method}_seed{seed}.pt'
    ed=Editor().cuda().float().eval(); ed.load_state_dict(torch.load(p,map_location='cuda',weights_only=True))
    for v in ed.parameters(): v.requires_grad_(train)
    return ed
def seed_all(s): random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)
def other_editors():
    state=torch.load(V3/'checkpoints/G3/best.pt',map_location='cpu',weights_only=True); result={}
    for op in ['T_minus','P_13','P_31']:
        ed=Editor().cuda().eval(); ed.load_state_dict({k[len(op)+1:]:v for k,v in state.items() if k.startswith(op+'.')})
        for p in ed.parameters(): p.requires_grad_(False)
        result[op]=ed
    return result
@torch.no_grad()
def monitor_other(e,eds,ws,s,phase):
    rows=[]
    for op,ed in eds.items():
        pers='third' if op=='P_31' else 'first'; outpers='third' if op=='P_13' else 'first'; offset=0; outoffset=1 if op=='T_minus' else 0
        for bw in chunks(ws):
            h,m,_=e.encode([render(w,frame(w,offset,pers)) for w in bw]); obs,_=observed(e,ed(h,m),m,bw,outoffset,outpers)
            rows.extend(dict(kind='other_operator_monitor',seed=s,method=op,record_id=w['record_id'],**o) for w,o in zip(bw,obs))
    write(ROOT/f'baseline/other_operators_s{s}_{phase}.jsonl',rows)
    return rows
def ce(e,h,m,texts,parts=False):
    """Frozen D parameters, differentiable forward w.r.t. edited memory."""
    y=e.tok(list(texts),padding=True,truncation=False,return_tensors='pt').input_ids.cuda(); y[y==e.tok.pad_token_id]=-100
    out=e.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=y,use_cache=False)
    if not parts: return out.loss, int((y!=-100).sum())
    ell=nn.functional.cross_entropy(out.logits.flatten(0,1),y.flatten(),ignore_index=-100,reduction='none').reshape(y.shape)
    return out.loss,int((y!=-100).sum()),ell.sum(1).detach().cpu().tolist(),(y!=-100).sum(1).cpu().tolist()
def observed(e,h,m,ws,offset,pers='first'):
    out,ends,lens,elapsed=e.decode(h,m)
    return [dict(output=t,normal_end=bool(z),generated_tokens=n,gold=render(w,frame(w,offset,pers)),frame=frame(w,offset,pers),exact=t==render(w,frame(w,offset,pers)),score=score(t,frame(w,offset,pers),w,z)) for t,z,n,w in zip(out,ends,lens,ws)],elapsed
def chunks(xs,n=16):
    for i in range(0,len(xs),n): yield xs[i:i+n]
def model_state(e): return statehash(e.model.state_dict())

@torch.no_grad()
def cache(e,g,s,ws,tag):
    path=ROOT/f'local/cache_s{s}_{tag}.pt'; meta=ROOT/f'data/cache_s{s}_{tag}.json'
    if path.exists() and meta.exists():
        z=json.loads(meta.read_text()); assert digest(path)==z['file_sha256']; return torch.load(path,map_location='cpu',weights_only=True),z
    H=[]; M=[]; ids=[]; gates=[]; seconds=0; started=time.monotonic()
    for bw in chunks(ws):
        e.check(120); hs=[]; ms=[]; xs=[]; prefixes=[]
        for k in range(3):
            texts=[render(w,frame(w,-1+k)) for w in bw]; h,m,_=e.encode(texts); x=e.batch(texts).input_ids
            pref=[[] for w in bw]
            if k==0:
                obs,t=observed(e,h,m,bw,-1); seconds+=t
                for j,o in enumerate(obs): pref[j].append(o)
            for step in range(k):
                h=g(h,m); obs,t=observed(e,h,m,bw,-1+k-step-1); seconds+=t
                for j,o in enumerate(obs): pref[j].append(o)
            hs.append(h.cpu()); ms.append(m.cpu()); xs.append(x.cpu()); prefixes.append(pref)
        for j,w in enumerate(bw):
            failures=[]
            for k in range(3):
                o=prefixes[k][j][-1]
                if not o['exact']: failures.append('current_text_H'+str(k))
                if not o['normal_end']: failures.append('normal_end_H'+str(k))
                if not all(a['score']['joint_ok'] for a in prefixes[k][j]): failures.append('prefix_H'+str(k))
            eq02=torch.equal(ms[0][j],ms[2][j]); eqall=eq02 and torch.equal(ms[0][j],ms[1][j])
            if not eq02: failures.append('G11_mask02')
            gates.append(dict(record_id=w['record_id'],split=w['split'],seed=s,matched=not failures,failures=failures,equal_mask02=eq02,equal_mask_all=eqall,lengths=[int(m[j].sum()) for m in ms],prefixes=[pr[j] for pr in prefixes]))
        H.append(torch.stack(hs,1)); M.append(torch.stack(ms,1)); ids.append(torch.stack(xs,1))
    payload=dict(H=torch.cat(H),mask=torch.cat(M),input_ids=torch.cat(ids),record_ids=[w['record_id'] for w in ws],lengths=torch.cat(M).sum(-1))
    assert payload['H'].dtype==torch.float32
    path.parent.mkdir(parents=True,exist_ok=True); torch.save(payload,path)
    z=dict(seed=s,tag=tag,path=str(path),file_sha256=digest(path),tensor_sha256=statehash({k:v for k,v in payload.items() if torch.is_tensor(v)}),frozen_G_hash=statehash(g.state_dict()),gates=gates,locked_before_R_training=True,cache_seconds=time.monotonic()-started,decode_seconds=seconds,job_id=os.environ['SLURM_JOB_ID'],extra_conditions='none; independent b+UV editor receives full memory and mask only')
    dump(meta,z); print('cached',s,tag,'C',sum(x['matched'] for x in gates),'/',len(ws),flush=True)
    return payload,z

def get_anchor(payload,ids,sources):
    ix=torch.tensor(ids,dtype=torch.long); src=torch.tensor(sources,dtype=torch.long)
    return payload['H'][ix,src].cuda(),payload['mask'][ix,src].cuda()
def anchor_targets(ws,ids): return [render(ws[i],frame(ws[i],-2)) for i in ids]
def training_blocks(e,r,payload,ws,byid,batch,method):
    src=batch['mixed_sources'] if method=='F3' else [0 if method=='F2' else 2]*len(batch['anchor_indices'])
    h,m=get_anchor(payload,batch['anchor_indices'],src); la,na=ce(e,r(h,m),m,anchor_targets(ws,batch['anchor_indices']))
    if method=='F0':
        h,m=get_anchor(payload,batch['narrow_indices'],[2]*len(batch['narrow_indices'])); gold=anchor_targets(ws,batch['narrow_indices'])
    else:
        bg=batch['replay']; gold=[render(byid[a['record_id']],frame(byid[a['record_id']],a['offset']-1,a['perspective'])) for a in bg]
        h,m,_=e.encode([render(byid[a['record_id']],frame(byid[a['record_id']],a['offset'],a['perspective'])) for a in bg])
    lb,nb=ce(e,r(h,m),m,gold)
    return .5*la+.5*lb,dict(anchor_loss=float(la.detach()),background_loss=float(lb.detach()),anchor_tokens=na,background_tokens=nb,source_counts=dict(collections.Counter(src)))

@torch.no_grad()
def fixed_eval(e,r,payload,gates,ws,s,method,split,checkpoint,indices=None):
    indices=list(range(len(ws))) if indices is None else indices; rows=[]
    for ix in chunks(indices):
        e.check(90); bw=[ws[i] for i in ix]
        for source in range(3):
            h,m=get_anchor(payload,ix,[source]*len(ix)); h=r(h,m); targets=anchor_targets(ws,ix)
            _,_,losses,tokens=ce(e,h,m,targets,True); obs,_=observed(e,h,m,bw,-2)
            for i,o,l,n in zip(ix,obs,losses,tokens):
                rows.append(dict(kind='fixed',seed=s,method=method,split=split,checkpoint=checkpoint,record_id=ws[i]['record_id'],source=source,current_text=render(ws[i],frame(ws[i],-1)),matched=gates[i]['matched'],loss_sum=l,target_tokens=n,**o))
    return rows

@torch.no_grad()
def atomic_eval(e,r,ws,s,method,split,checkpoint):
    rows=[]
    for status in ['recorded_plan','reported_cancelled','reported_completed']:
        sw=[w for w in ws if w['record_status']==status]
        if not sw: continue
        for d,p in atomic_specs(sw[0]):
            for bw in chunks(sw):
                e.check(90); h,m,_=e.encode([render(w,frame(w,d,p)) for w in bw]); h=r(h,m)
                obs,_=observed(e,h,m,bw,d-1,p)
                for w,o in zip(bw,obs): rows.append(dict(kind='atomic',seed=s,method=method,split=split,checkpoint=checkpoint,record_id=w['record_id'],status=status,offset=d,perspective=p,source_text=render(w,frame(w,d,p)),**o))
    return rows

@torch.no_grad()
def rollout_eval(e,r,ws,s,method,split,checkpoint):
    rows=[]
    for mode in ['latent','reencode']:
        for bw in chunks(ws):
            h,m,_=e.encode([render(w,frame(w,1)) for w in bw]); clean=[True]*len(bw); first=[None]*len(bw)
            for k in range(1,6):
                e.check(90); h=r(h,m); obs,_=observed(e,h,m,bw,1-k)
                for j,(w,o) in enumerate(zip(bw,obs)):
                    if not o['score']['joint_ok'] and first[j] is None: first[j]=k
                    clean[j]=clean[j] and o['score']['joint_ok']
                    rows.append(dict(kind='rollout',seed=s,method=method,split=split,checkpoint=checkpoint,mode=mode,step=k,record_id=w['record_id'],trajectory_ok=clean[j],first_failure=first[j],input_length=int(m[j].sum()),**o))
                if mode=='reencode' and k<5:
                    # The only encoder reset uses freely generated text, never gold.
                    h,m,_=e.encode([o['output'] for o in obs])
    return rows

def metrics(fixed,atomic):
    cells=collections.defaultdict(list)
    for x in atomic: cells[x['status'],x['offset'],x['perspective']].append(x['score']['joint_ok'])
    mac=sum(sum(v)/len(v) for v in cells.values())/len(cells) if cells else None
    by=collections.defaultdict(dict)
    for x in fixed:
        if x['matched']: by[x['record_id']][x['source']]=x
    all3=sum(all(r[k]['score']['joint_ok'] for k in range(3)) for r in by.values())/len(by) if by else None
    source={str(k):sum(r[k]['score']['joint_ok'] for r in by.values())/len(by) if by else None for k in range(3)}
    nll={str(k):sum(r['loss_sum'] for r in fixed if r['source']==k)/sum(r['target_tokens'] for r in fixed if r['source']==k) for k in range(3)}
    return dict(atomic_macro=mac,all3=all3,source=source,token_nll=nll,matched_n=len(by),original_n=len(fixed)//3)

@torch.no_grad()
def reproduce(e,s):
    checks=[]
    archive=read(G12/'outputs/long_chains.jsonl')
    worlds={w['record_id']:w for w in read(G12/'data/worlds.jsonl')}
    for method in ['Original','A','B']:
        ed=editor(s,'T0' if method=='Original' else method)
        candidates=[x for x in archive if x['seed']==s and x['method']==method and x['split']=='iid' and x['step']==1][:6]
        targets={(x['record_id'],x['step']):x for x in archive if x['seed']==s and x['method']==method}
        bw=[worlds[x['record_id']] for x in candidates]; h,m,_=e.encode([x['source_text'] for x in candidates])
        for k in range(1,4):
            h=ed(h,m); obs,_=observed(e,h,m,bw,1-k)
            for w,o in zip(bw,obs):
                old=targets[w['record_id'],k]['output']; assert o['output']==old['output'] and o['normal_end']==old['normal_end'],(s,method,k,w['record_id'])
                checks.append(dict(seed=s,method=method,step=k,record_id=w['record_id'],output_equal=True,normal_end_equal=True))
        del ed
    dump(ROOT/f'baseline/reproduction_s{s}.json',dict(passed=True,checks=checks))
    # Independently rescore all archived G12 key rows for this seed, without rewriting them.
    counts=collections.defaultdict(lambda:dict(n=0,joint=0,trajectory=0)); mismatches=[]
    clean={}
    for x in archive:
        if x['seed']!=s: continue
        z=x['output']; sc=score(z['output'],z['frame'],worlds[x['record_id']],z['normal_end'])
        if sc!=z['score']: mismatches.append(x['record_id'])
        q=(x['method'],x['split'],x['record_id']); clean[q]=clean.get(q,True) and sc['joint_ok']
        cell=counts[x['method'],x['split'],x['step']]; cell['n']+=1; cell['joint']+=int(sc['joint_ok']); cell['trajectory']+=int(clean[q])
    assert not mismatches
    dump(ROOT/f'baseline/archive_rescore_s{s}.json',dict(passed=True,key_rows=[dict(method=k[0],split=k[1],step=k[2],**v) for k,v in counts.items()],old_outputs_untouched=True))

@torch.no_grad()
def old_diagnostic(e,s,new_worlds):
    import importlib.util
    spec=importlib.util.spec_from_file_location('g13_preparation',ROOT/'prepare.py'); prep=importlib.util.module_from_spec(spec); spec.loader.exec_module(prep); stratified=prep.stratified
    oldworlds={w['record_id']:w for w in read(V3/'data/train_worlds.jsonl')}; g12worlds={r['record_id']:r['world'] for r in read(G12/'data/train_paths.jsonl')}
    selected=json.loads((ROOT/'data/old_train_diagnostic.json').read_text())['g12_worlds']; rows=[]; tasks=[]
    for method in ['A','B']:
        for rid in selected: tasks.append(dict(method=method,task='g12_3stage',world=g12worlds[rid],offset=1,perspective='first',length=3))
    training=read(V3/'data/train_G1.jsonl'); sched=[z for z in read(V3/'data/sample_schedule.jsonl') if z['path'].startswith('T_plus')]
    for replacement,length in [(False,1),(True,2)]:
        candidates=[]
        for b in sched:
            for i,flag in zip(b['pair_indices'],b['g2_replace']):
                if flag==replacement: candidates.append(training[i])
        unique={r['record_id']:r for r in candidates}; chosen=stratified([oldworlds[k] for k in unique],80,'old_original/'+str(length))
        for w in chosen:
            r=unique[w['record_id']]; tasks.append(dict(method='Original',task='original_supervised_'+str(length),world=w,offset=r['offsets'][0],perspective=r['frames'][0]['perspective'],length=length))
    # Pair actual training tasks to independently generated worlds with the same status/template/polarity and legal offset.
    manifest=[]
    for method in ['Original','A','B']:
        ed=editor(s,'T0' if method=='Original' else method)
        for task in sorted({t['task'] for t in tasks if t['method']==method}):
            ts=[t for t in tasks if t['method']==method and t['task']==task]; bycell=collections.defaultdict(list)
            for w in new_worlds: bycell[w['record_status'],w['template_family'],w['polarity']].append(w)
            used=set(); paired=[]
            for t in ts:
                w=t['world']; candidates=[x for x in bycell[w['record_status'],w['template_family'],w['polarity']] if x['record_id'] not in used and eligible(x,['T_plus']*t['length'],t['offset'],t['perspective'])]
                assert candidates,'No independent IID world for audited training task'
                nw=candidates[0]; used.add(nw['record_id']); paired.append(dict(t,world=nw)); manifest.append(dict(method=method,task=task,train_world=w['record_id'],iid_world=nw['record_id'],offset=t['offset'],perspective=t['perspective'],supervised_length=t['length']))
            for split,group in [('old_train',ts),('new_iid',paired)]:
                # Batches group offset/perspective, preserving masks and source semantics.
                buckets=collections.defaultdict(list)
                for t in group: buckets[t['offset'],t['perspective']].append(t)
                for (d,p),bucket in buckets.items():
                    for bt in chunks(bucket):
                        bw=[t['world'] for t in bt]; h,m,_=e.encode([render(w,frame(w,d,p)) for w in bw]); clean=[True]*len(bw); free_h=h; free_mask=m; free_clean=[True]*len(bw)
                        for k in range(1,bt[0]['length']+1):
                            free_h=ed(free_h,free_mask); free_obs,_=observed(e,free_h,free_mask,bw,d-k,p)
                            for j,(w,o) in enumerate(zip(bw,free_obs)):
                                free_clean[j]=free_clean[j] and o['score']['joint_ok']
                                rows.append(dict(kind='old_free',seed=s,method=method,split=split,task=task,record_id=w['record_id'],source='own_depth_'+str(k-1),supervised_length=bt[0]['length'],step=k,source_offset=d-k+1,perspective=p,trajectory_ok=free_clean[j],**o))
                            if method=='A' and k==3: h,m,_=e.encode([render(w,frame(w,-1)) for w in bw])
                            h=ed(h,m); targets=[render(w,frame(w,d-k,p)) for w in bw]; _,_,ls,ns=ce(e,h,m,targets,True); obs,_=observed(e,h,m,bw,d-k,p)
                            for j,(w,o,l,n) in enumerate(zip(bw,obs,ls,ns)):
                                clean[j]=clean[j] and o['score']['joint_ok']
                                rows.append(dict(kind='old_diagnostic',seed=s,method=method,split=split,task=task,record_id=w['record_id'],source=('natural_yesterday' if method=='A' and k==3 else 'own_depth_'+str(k-1)),supervised_length=bt[0]['length'],step=k,source_offset=d-k+1,perspective=p,loss_sum=l,target_tokens=n,conditioned_task_all_steps=clean[j],**o))
        del ed
    write(ROOT/f'baseline/train_iid_s{s}.jsonl',rows); dump(ROOT/f'data/old_task_pairs_s{s}.json',manifest)
    print('old train/IID diagnostic',s,len(rows),flush=True)

def smoke(e):
    verify_lock(); s=42; seed_all(s); ws=[w for w in read(ROOT/'data/train_worlds.jsonl') if w['record_status']=='recorded_plan'][:16]
    g=editor(s); gh=statehash(g.state_dict()); bh=model_state(e); payload,meta=cache(e,g,s,ws,'smoke')
    before=statehash({k:v for k,v in payload.items() if torch.is_tensor(v)}); byid={w['record_id']:w for w in read(ROOT/'data/train_worlds.jsonl')}
    b=read(ROOT/'data/sample_schedule.jsonl')[0]; b=dict(b,anchor_indices=list(range(16)),narrow_indices=list(range(16)))
    checks=[]; decode_times=[]; update_times=[]
    previous=None
    for method in CFG['methods']:
        seed_all(s); r=editor(s,train=True); opt=torch.optim.AdamW(r.parameters(),lr=.001,weight_decay=0)
        assert not opt.state
        init=statehash(r.state_dict()); t=time.monotonic(); opt.zero_grad(); loss,st=training_blocks(e,r,payload,ws,byid,b,method); loss.backward()
        norms=[float(p.grad.norm()) for p in r.parameters()]; assert sum(norms)>0 and all(torch.isfinite(p.grad).all() for p in r.parameters())
        assert all(p.grad is None and not p.requires_grad for p in e.model.parameters()) and all(p.grad is None for p in g.parameters())
        torch.nn.utils.clip_grad_norm_(r.parameters(),1.); opt.step(); torch.cuda.synchronize(); update_times.append(time.monotonic()-t)
        assert statehash(r.state_dict())!=init
        if previous is not None: assert all(p.data_ptr()!=q.data_ptr() for p,q in zip(r.parameters(),previous.parameters()))
        h,m=get_anchor(payload,list(range(16)),[2]*16)
        with torch.no_grad():
            out,_,_,t=e.decode(r(h,m),m); decode_times.append(t); again=e.decode(r(h,m),m)[0]; assert out==again
        p=ROOT/f'local/smoke_{method}.pt'; torch.save(r.state_dict(),p); restored=Editor().cuda(); restored.load_state_dict(torch.load(p,map_location='cuda',weights_only=True)); assert statehash(restored.state_dict())==statehash(r.state_dict())
        checks.append(dict(method=method,loss=float(loss),gradient_norms=norms,R_updated=True,fresh_optimizer=True,cache_replay_equal=True,save_reload_equal=True,**st)); previous=r
    assert gh==statehash(g.state_dict()) and bh==model_state(e) and before==statehash({k:v for k,v in payload.items() if torch.is_tensor(v)})
    reproduce(e,42)
    r=editor(42); roll=rollout_eval(e,r,ws[:2],42,'smoke','train','smoke'); write(ROOT/'local/smoke_rollout.jsonl',roll)
    dump(ROOT/'smoke_test.json',dict(passed=True,job_id=os.environ['SLURM_JOB_ID'],checks=checks,backbone_unchanged=True,G_unchanged=True,cache_unchanged=True,decoder_gradient_reaches_R=True,update_seconds=update_times,decode_16_seconds=decode_times,elapsed_seconds=time.monotonic()-e.start,gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),historical_reproduction_passed=True,train_only_smoke=True))
    print('G13 smoke passed',flush=True)

def train_seed(e,s):
    verify_lock(); assert json.loads((ROOT/'smoke_test.json').read_text())['passed']; bh=model_state(e); g=editor(s); gh=statehash(g.state_dict()); allws=read(ROOT/'data/worlds.jsonl'); byid={w['record_id']:w for w in allws}
    reproduce(e,s); old_diagnostic(e,s,[w for w in allws if w['split']=='iid'])
    others=other_editors(); other_hashes={k:statehash(v.state_dict()) for k,v in others.items()}; monitor_ws=[w for w in allws if w['split']=='dev' and w['record_status']=='recorded_plan'][:16]; other_before=monitor_other(e,others,monitor_ws,s,'before')
    caches={}; gates={}; plans={}; metas={}
    for split in CFG['plan_world_counts']:
        plans[split]=[w for w in allws if w['split']==split and w['record_status']=='recorded_plan']; caches[split],metas[split]=cache(e,g,s,plans[split],split); gates[split]=metas[split]['gates']
    # Persist one immutable cohort / schedule before any arm updates.
    order=json.loads((ROOT/'data/anchor_order.json').read_text()); index={w['record_id']:i for i,w in enumerate(plans['train'])}; C={x['record_id'] for x in gates['train'] if x['matched']}; assert C,'No train matched cohort; do not silently train unmatched sources'
    a=[index[r] for r in order['anchor_worlds'] if r in C]; b=[index[r] for r in order['narrow_worlds'] if r in C]
    schedule=[dict(z,anchor_indices=[a[i%len(a)] for i in z['anchor_positions']],narrow_indices=[b[i%len(b)] for i in z['narrow_positions']]) for z in read(ROOT/'data/sample_schedule.jsonl')]
    schedule_path=ROOT/f'data/schedule_s{s}.jsonl'
    if schedule_path.exists(): assert read(schedule_path)==schedule
    else: write(schedule_path,schedule)
    cohort=dict(seed=s,cohorts={sp:[x['record_id'] for x in gates[sp] if x['matched']] for sp in gates},cache_hashes={sp:metas[sp]['file_sha256'] for sp in metas},schedule_sha256=digest(schedule_path),locked_before_all_R=True)
    dump(ROOT/f'data/cohort_s{s}.json',cohort)
    dids=json.loads((ROOT/'data/diagnostic_ids.json').read_text()); initial=statehash(g.state_dict())
    for method in CFG['methods']:
        done=ROOT/f'training/{method}_s{s}.json'
        if done.exists():
            z=json.loads(done.read_text()); assert z['updates']==200 and digest(ROOT/z['final_path'])==z['final_sha256']; continue
        seed_all(s); r=editor(s,train=True); assert statehash(r.state_dict())==initial
        opt=torch.optim.AdamW(r.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay']); assert not opt.state
        start=time.monotonic(); curve=[]; steps=[]; counts=dict(instances=0,anchor_tokens=0,background_tokens=0); sources=collections.Counter(); best_score=-1.; best_step=None; completed=0
        resume=ROOT/f'local/resume_{method}_s{s}.pt'; best_path=ROOT/f'checkpoints/{method}_s{s}_best.pt'; final_path=ROOT/f'checkpoints/{method}_s{s}_final.pt'; final_path.parent.mkdir(parents=True,exist_ok=True)
        if resume.exists():
            z=torch.load(resume,map_location='cpu',weights_only=False); assert z['initial']==initial and z['schedule_hash']==digest(schedule_path)
            r.load_state_dict(z['editor']); opt.load_state_dict(z['optimizer']); completed=z['completed']; curve=z['curve']; steps=z['steps']; counts=z['counts']; sources=collections.Counter(z['sources']); best_score=z['best_score']; best_step=z['best_step']; torch.set_rng_state(z['cpu_rng']); torch.cuda.set_rng_state_all(z['cuda_rng'])
        def save():
            resume.parent.mkdir(parents=True,exist_ok=True); q=resume.with_suffix('.tmp')
            torch.save(dict(editor=r.state_dict(),optimizer=opt.state_dict(),initial=initial,schedule_hash=digest(schedule_path),completed=completed,curve=curve,steps=steps,counts=counts,sources=dict(sources),best_score=best_score,best_step=best_step,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),q); q.replace(resume)
        def diagnose(step):
            nonlocal best_score,best_step
            for split in ['train','dev']:
                pidx={w['record_id']:i for i,w in enumerate(plans[split])}; ix=[pidx[x] for x in dids[split]['anchor']]; aws=[byid[x] for x in dids[split]['atomic']]
                fr=fixed_eval(e,r,caches[split],gates[split],plans[split],s,method,split,str(step),ix); ar=atomic_eval(e,r,aws,s,method,split,str(step)); z=metrics(fr,ar)
                row=dict(seed=s,method=method,step=step,split=split,**z); curve.append(row); write(ROOT/f'learning/{method}_s{s}_{split}_{step}.jsonl',fr+ar)
                if split=='dev' and z['all3'] is not None:
                    devscore=.5*z['atomic_macro']+.5*z['all3']
                    if devscore>best_score:
                        best_score=devscore; best_step=step; torch.save({k:v.detach().cpu() for k,v in r.state_dict().items()},best_path)
            torch.save({k:v.detach().cpu() for k,v in r.state_dict().items()},ROOT/f'checkpoints/{method}_s{s}_step{step}.pt')
            print('diagnostic',s,method,step,curve[-1]['atomic_macro'],curve[-1]['all3'],flush=True)
        torch.cuda.reset_peak_memory_stats()
        try:
            if completed==0 and not curve: diagnose(0); save()
            for batch in schedule[completed:]:
                e.check(150); opt.zero_grad(set_to_none=True); loss,st=training_blocks(e,r,caches['train'],plans['train'],byid,batch,method); assert torch.isfinite(loss); loss.backward()
                assert all(p.grad is None for p in e.model.parameters()) and all(p.grad is None for p in g.parameters())
                torch.nn.utils.clip_grad_norm_(r.parameters(),CFG['gradient_clip']); opt.step(); completed=batch['update']; counts['instances']+=32; counts['anchor_tokens']+=st['anchor_tokens']; counts['background_tokens']+=st['background_tokens']; sources.update({int(k):v for k,v in st['source_counts'].items()}); steps.append(dict(step=completed,loss=float(loss.detach()),**st))
                if completed in CFG['checkpoints']: diagnose(completed); save()
                elif completed%10==0: save()
        finally: save()
        assert completed==200 and statehash(r.state_dict())!=initial
        torch.save({k:v.detach().cpu() for k,v in r.state_dict().items()},final_path)
        # Check all immutable artifacts after every arm, before confirmation.
        assert statehash(g.state_dict())==gh and model_state(e)==bh
        for sp,z in metas.items(): assert digest(z['path'])==z['file_sha256']
        meta=dict(seed=s,method=method,updates=completed,initial_hash=initial,final_path=str(final_path.relative_to(ROOT)),final_sha256=digest(final_path),best_path=str(best_path.relative_to(ROOT)) if best_step is not None else None,best_sha256=digest(best_path) if best_step is not None else None,best_step=best_step,best_score=best_score,counts=counts,anchor_source_counts=dict(sources),curve=curve,step_log=steps,training_and_diagnostic_seconds=time.monotonic()-start,peak_cuda_bytes=torch.cuda.max_memory_allocated(),G_unchanged=True,ED_unchanged=True,caches_unchanged=True,job_id=os.environ['SLURM_JOB_ID'],schedule_sha256=digest(schedule_path))
        dump(ROOT/f'training/{method}_s{s}_trained.json',meta)
        # Full final confirmation and secondary best-dev, with separate output labels.
        for cp in ['final','best']:
            if cp=='best' and best_step is None: continue
            r.load_state_dict(torch.load(final_path if cp=='final' else best_path,map_location='cuda',weights_only=True))
            for split in ['iid','template_ood']:
                output=ROOT/f'outputs/{method}_s{s}_{split}_{cp}.jsonl'
                if output.exists(): continue
                fr=fixed_eval(e,r,caches[split],gates[split],plans[split],s,method,split,cp); ar=atomic_eval(e,r,[w for w in allws if w['split']==split],s,method,split,cp); rr=rollout_eval(e,r,plans[split],s,method,split,cp)
                write(output,fr+ar+rr); print('confirmation',s,method,cp,split,len(fr+ar+rr),flush=True)
        dump(done,meta); del r,opt; torch.cuda.empty_cache()
    # T0 on exactly the new denominator is the atomic-protection reference.
    for split in ['iid','template_ood']:
        path=ROOT/f'outputs/T0_s{s}_{split}_final.jsonl'
        if not path.exists(): write(path,fixed_eval(e,g,caches[split],gates[split],plans[split],s,'T0',split,'final')+atomic_eval(e,g,[w for w in allws if w['split']==split],s,'T0',split,'final')+rollout_eval(e,g,plans[split],s,'T0',split,'final'))
    assert statehash(g.state_dict())==gh and model_state(e)==bh
    assert {k:statehash(v.state_dict()) for k,v in others.items()}==other_hashes
    assert monitor_other(e,others,monitor_ws,s,'after')==other_before
    dump(ROOT/f'seed_s{s}_complete.json',dict(seed=s,groups=CFG['methods'],passed=True,job_id=os.environ['SLURM_JOB_ID'],elapsed_seconds=time.monotonic()-e.start,gpu=torch.cuda.get_device_name(),gpu_total_memory=torch.cuda.get_device_properties(0).total_memory,peak_cuda_bytes=torch.cuda.max_memory_allocated(),backbone_state_hash=bh,G_state_hash=gh,caches_unchanged=True,optional_H3_H4='not run; optional source screening omitted; no zero-success inference'))
    print('SEED COMPLETE',s,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--smoke',action='store_true'); p.add_argument('--seed-index',type=int); args=p.parse_args()
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'), 'sbatch + srun required'
    from engine import Engine
    eng=Engine(); eng.limit=float(os.environ.get('G13_WALL_SECONDS','1100'))
    assert eng.kw=={k:CFG[k] for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']}
    if args.smoke: smoke(eng)
    else: train_seed(eng,json.loads((ROOT/'runs_manifest.json').read_text())['array_mapping'][args.seed_index]['seed'])
