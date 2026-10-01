"""Slurm-only GPU cache, three independent repairs and held-out final inference."""
import argparse, time
import torch
from common_g15 import *
old = load_module('g15_readonly_g13_editor', G13/'run.py')
Editor = old.Editor
ce = old.ce

def chunks(rows,n=16):
    for i in range(0,len(rows),n): yield rows[i:i+n]
def seed_all(seed):
    random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
def encode(e,texts):
    h,m,_=e.encode(texts)
    return dict(memory=h,mask=m,input_ids=e.batch(texts).input_ids)
def observe(e,state,worlds,offset,perspective='first'):
    texts,ends,lens,seconds=e.decode(state['memory'],state['mask'])
    return [dict(observation(t,end,w,offset,perspective),generated_tokens=int(n)) for t,end,n,w in zip(texts,ends,lens,worlds)],seconds
def edit(editor,state): return dict(state,memory=editor(state['memory'],state['mask']))
def slice_state(state,indices): return {k:v[indices].cuda() for k,v in state.items()}
def state_fields(state,j):
    st={k:v[j:j+1] for k,v in state.items()}
    return dict(input_state_sha256=statehash(st),memory_sha256=statehash({'memory':st['memory']}),mask_sha256=statehash({'mask':st['mask']}),input_token_ids=st['input_ids'][0].detach().cpu().tolist(),attention_mask=st['mask'][0].detach().cpu().tolist(),input_length=int(st['mask'].sum()))
def load_editor(seed,role,train=False,final_heldout=False):
    assert role!='U' or (final_heldout and not train),'U only in final confirmation'
    z=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models'][str(seed)][role]
    assert digest(z['path'])==z['sha256']
    ed=Editor().cuda().float().eval();ed.load_state_dict(torch.load(z['path'],map_location='cuda',weights_only=True))
    for p in ed.parameters():p.requires_grad_(train);p.grad=None
    return ed

@torch.no_grad()
def build_cache(e,P,G,worlds,seed,tag,U=None):
    """Full immutable states; U is legal only for post-training confirmation."""
    assert U is None or tag.startswith('confirm_')
    path=ROOT/f'local/{tag}_s{seed}.pt';metapath=ROOT/f'data/{tag}_s{seed}.json'
    if metapath.exists():
        meta=json.loads(metapath.read_text());assert digest(path)==meta['cache_sha256']
        assert meta['world_ids']==[w['record_id'] for w in worlds]
        return torch.load(path,map_location='cpu',weights_only=True),meta
    begin=time.monotonic(); pieces=[]; currents=collections.defaultdict(list); oldprefix=[]; gates=[]; rows=[]
    for bw in chunks(worlds):
        e.check(90);states={};start=encode(e,[render(w,frame(w,1)) for w in bw]);start_hash=statehash(start)
        states['start']=start;states['E']=encode(e,[render(w,frame(w,0)) for w in bw])
        producers={'P':P}
        if U is not None:producers.update(G=G,U=U)
        obs={}
        for name,producer in producers.items():
            states[name]=edit(producer,start);obs[name],_=observe(e,states[name],bw,0)
            assert statehash(start)==start_hash
        obs['E'],_=observe(e,states['E'],bw,0)
        prefixes=[[] for _ in bw]
        for k in range(3):
            st=encode(e,[render(w,frame(w,-1+k)) for w in bw]);pref=[[] for _ in bw]
            if k==0:
                os_,_=observe(e,st,bw,-1)
                for j,o in enumerate(os_):pref[j].append(o)
            for depth in range(k):
                st=edit(G,st);os_,_=observe(e,st,bw,-1+k-depth-1)
                for j,o in enumerate(os_):pref[j].append(o)
            states['H'+str(k)]=st
            for j,pr in enumerate(pref):prefixes[j].append(pr)
        for j,w in enumerate(bw):
            p_gate=gate_current({'P':obs['P'][j]},True)
            old_gate=gate_current({'H'+str(k):prefixes[j][k][-1] for k in range(3)},torch.equal(states['H0']['mask'][j],states['H2']['mask'][j]))
            for k in range(3):
                if not all(o['joint'] and o['normal_end'] for o in prefixes[j][k]):old_gate['failures'].append('H'+str(k)+'_historical_prefix')
            old_gate['matched']=not old_gate['failures']
            z=dict(world_id=w['record_id'],P_gate=p_gate,old_gate=old_gate,natural_mask_equal=torch.equal(states['E']['mask'][j],states['P']['mask'][j]))
            if U is not None:
                eq=all(torch.equal(states['P']['mask'][j],states[n]['mask'][j]) for n in ['G','U']);assert eq
                z['fixed_gate']=gate_current({n:obs[n][j] for n in ['E','P','G','U']},eq)
                z['producer_masks_equal']=eq
            gates.append(z)
            for name,st in states.items():
                rows.append(dict(world_id=w['record_id'],source=name,**state_fields(st,j),current=obs.get(name,[None]*len(bw))[j],old_prefix=prefixes[j][int(name[-1])] if name.startswith('H') else None))
        pieces.append({n:{k:v.detach().cpu() for k,v in st.items()} for n,st in states.items()})
        for n,values in obs.items():currents[n]+=values
        oldprefix+=prefixes
    states={n:{k:torch.cat([p[n][k] for p in pieces]) for k in pieces[0][n]} for n in pieces[0]}
    assert all(st['memory'].dtype==torch.float32 for st in states.values())
    payload=dict(states=states,current=dict(currents),oldprefix=oldprefix,gates=gates,world_ids=[w['record_id'] for w in worlds])
    path.parent.mkdir(parents=True,exist_ok=True);torch.save(payload,path)
    statepath=ROOT/f'data/{tag}_s{seed}_states.jsonl.gz';write(statepath,rows)
    meta=dict(seed=seed,tag=tag,cache_path=str(path),cache_sha256=digest(path),world_ids=payload['world_ids'],state_metadata=str(statepath.relative_to(ROOT)),state_metadata_sha256=digest(statepath),tensor_hashes={n:statehash(st) for n,st in states.items()},cache_seconds=time.monotonic()-begin,full_FP32_token_memory=True,current_only_gate=True,U_included=U is not None,gates=gates,producer_hashes={'P':statehash(P.state_dict()),'G':statehash(G.state_dict()),**({'U':statehash(U.state_dict())} if U is not None else {})})
    dump(metapath,meta);print('cached',seed,tag,'P',sum(g['P_gate']['matched'] for g in gates),'old',sum(g['old_gate']['matched'] for g in gates),flush=True)
    return payload,meta

def project_schedule(payload,order,base,smoke=False):
    ix={rid:i for i,rid in enumerate(payload['world_ids'])}
    main=[ix[r] for r in order['main'] if r in ix and payload['gates'][ix[r]]['P_gate']['matched']]
    maintenance=[ix[r] for r in order['maintenance'] if r in ix and payload['gates'][ix[r]]['old_gate']['matched']]
    assert len(main)>=(8 if smoke else CFG['train_P_gate_min']),f'P train gate too small: {len(main)}'
    assert maintenance,'No valid old-maintenance input'
    return [dict(b,main_indices=[main[p%len(main)] for p in b['main_positions']],maintenance_indices=[maintenance[p%len(maintenance)] for p in b['maintenance_positions']]) for b in base]

def step_inputs(e,payload,plans,byid,batch):
    ix=batch['main_indices'];bw=[plans[i] for i in ix]
    ids=batch['maintenance_indices'];src=batch['maintenance_sources'];oldstates=payload['states']
    h=torch.stack([oldstates['H'+str(k)]['memory'][i] for i,k in zip(ids,src)]).cuda()
    m=torch.stack([oldstates['H'+str(k)]['mask'][i] for i,k in zip(ids,src)]).cuda()
    x=torch.stack([oldstates['H'+str(k)]['input_ids'][i] for i,k in zip(ids,src)]).cuda()
    replay=batch['replay'];bg=encode(e,[render(byid[r['record_id']],frame(byid[r['record_id']],r['offset'],r['perspective'])) for r in replay])
    return dict(start=slice_state(oldstates['start'],ix),natural=slice_state(oldstates['E'],ix),fixed=slice_state(oldstates['P'],ix),background=bg,maintenance=dict(memory=h,mask=m,input_ids=x),worlds=bw,first_gold=[render(w,frame(w,0)) for w in bw],next_gold=[render(w,frame(w,-1)) for w in bw],background_gold=[render(byid[r['record_id']],frame(byid[r['record_id']],r['offset']-1,r['perspective'])) for r in replay],maintenance_gold=[render(plans[i],frame(plans[i],-2)) for i in ids],fixed_current=[payload['current']['P'][i] for i in ix],natural_current=[payload['current']['E'][i] for i in ix])

def continuation_state(method,h1,inputs):
    if method=='O':return dict(inputs['start'],memory=h1.detach())
    return inputs['fixed'] if method=='F' else inputs['natural']

def four_block_loss(e,T,inputs,method):
    """A retains producer gradient; O D input is detached, never reencoded."""
    start=inputs['start'];h1=T(start['memory'],start['mask']);first_state=dict(start,memory=h1)
    current,_=observe(e,first_state,inputs['worlds'],0)
    dstate=continuation_state(method,h1,inputs)
    blockstates=[first_state,edit(T,inputs['background']),edit(T,inputs['maintenance']),edit(T,dstate)]
    targets=[inputs[n] for n in ['first_gold','background_gold','maintenance_gold','next_gold']]
    losses={};tokens={}
    for name,state,gold in zip('ABCD',blockstates,targets):
        losses[name],tokens[name]=ce(e,state['memory'],state['mask'],gold)
    total=sum(losses.values())*.25
    source_current=current if method=='O' else inputs['fixed_current'] if method=='F' else inputs['natural_current']
    return total,dict(losses=losses,tokens=tokens,current=current,source_current=source_current,h1=h1,D_input=dstate,first_state=first_state)

def resume_save(path,T,opt,completed,logs,counts,schedule_hash,initial_hash):
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp')
    torch.save(dict(editor=T.state_dict(),optimizer=opt.state_dict(),completed=completed,logs=logs,counts=counts,schedule_hash=schedule_hash,initial_hash=initial_hash,python_rng=random.getstate(),cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),temp);temp.replace(path)
def resume_load(path,T,opt,schedule_hash,initial_hash):
    z=torch.load(path,map_location='cpu',weights_only=False)
    assert z['schedule_hash']==schedule_hash and z['initial_hash']==initial_hash
    T.load_state_dict(z['editor']);opt.load_state_dict(z['optimizer'])
    random.setstate(z['python_rng']);torch.set_rng_state(z['cpu_rng']);torch.cuda.set_rng_state_all(z['cuda_rng'])
    return z

@torch.no_grad()
def atom_eval(e,Q,worlds,seed,method,split,step,with_loss=False):
    rows=[];begin=time.monotonic()
    for status in ['recorded_plan','reported_cancelled','reported_completed']:
        sw=[w for w in worlds if w['record_status']==status]
        for d,p in atomic_specs(sw[0]):
            for bw in chunks(sw):
                e.check(90);st=encode(e,[render(w,frame(w,d,p)) for w in bw]);out=edit(Q,st);obs,_=observe(e,out,bw,d-1,p)
                if with_loss:_,_,ls,ns=ce(e,out['memory'],out['mask'],[o['gold'] for o in obs],True)
                else:ls=[None]*len(bw);ns=[None]*len(bw)
                for j,(w,o,l,n) in enumerate(zip(bw,obs,ls,ns)):
                    rows.append(dict(kind='atomic',seed=seed,method=method,split=split,step=step,world_id=w['record_id'],status=status,offset=d,perspective=p,loss_sum=l,target_tokens=n,**state_fields(st,j),**o))
    return rows,time.monotonic()-begin

@torch.no_grad()
def old_eval(e,Q,payload,plans,seed,method,split,step,indices=None,with_loss=False):
    indices=list(range(len(plans))) if indices is None else indices;rows=[]
    for ix in chunks(indices):
        bw=[plans[i] for i in ix]
        for k in range(3):
            st=slice_state(payload['states']['H'+str(k)],ix);before=statehash(st);out=edit(Q,st);obs,_=observe(e,out,bw,-2)
            assert statehash(st)==before
            if with_loss:_,_,ls,ns=ce(e,out['memory'],out['mask'],[o['gold'] for o in obs],True)
            else:ls=[None]*len(bw);ns=[None]*len(bw)
            for j,(i,w,o,l,n) in enumerate(zip(ix,bw,obs,ls,ns)):
                rows.append(dict(kind='old',seed=seed,method=method,split=split,step=step,world_id=w['record_id'],source='H'+str(k),matched=payload['gates'][i]['old_gate']['matched'],match_failures=payload['gates'][i]['old_gate']['failures'],current=payload['oldprefix'][i][k][-1],loss_sum=l,target_tokens=n,**state_fields(st,j),**o))
    return rows

@torch.no_grad()
def seen_eval(e,Q,payload,plans,seed,method,split,step,indices):
    rows=[]
    for ix in chunks(indices):
        bw=[plans[i] for i in ix];start=slice_state(payload['states']['start'],ix);h1=Q(start['memory'],start['mask']);firstst=dict(start,memory=h1)
        first,_=observe(e,firstst,bw,0)
        _,_,ls,ns=ce(e,h1,start['mask'],[o['gold'] for o in first],True)
        for w,o,l,n in zip(bw,first,ls,ns):rows.append(dict(kind='seen_A',seed=seed,method=method,split=split,step=step,world_id=w['record_id'],loss_sum=l,target_tokens=n,**o))
        ds=continuation_state(method,h1,dict(start=start,natural=slice_state(payload['states']['E'],ix),fixed=slice_state(payload['states']['P'],ix)))
        current=first if method=='O' else [payload['current']['P' if method=='F' else 'E'][i] for i in ix]
        out=edit(Q,ds);obs,_=observe(e,out,bw,-1);_,_,ls,ns=ce(e,out['memory'],out['mask'],[o['gold'] for o in obs],True)
        for j,(w,o,cur,l,n) in enumerate(zip(bw,obs,current,ls,ns)):
            rows.append(dict(kind='seen_D',seed=seed,method=method,split=split,step=step,world_id=w['record_id'],source=method,current=cur,current_joint=cur['joint'],current_exact=cur['exact'],trajectory_target=not cur['joint'],full=full_success(cur,o),loss_sum=l,target_tokens=n,**state_fields(ds,j),**o))
    return rows

def diagnostic_summary(rows):
    groups=collections.defaultdict(list)
    for r in rows:groups[r['kind']].append(r)
    atoms=collections.defaultdict(list)
    for r in groups['atomic']:atoms[r['status'],r['offset'],r['perspective']].append(r['joint'])
    olds=collections.defaultdict(dict)
    for r in groups['old']:
        if r['matched']:olds[r['world_id']][r['source']]=r['joint']
    nll={k:sum(r['loss_sum'] for r in v)/sum(r['target_tokens'] for r in v) for k,v in groups.items()}
    return dict(atomic_macro=sum(sum(v)/len(v) for v in atoms.values())/40,atomic_cells={str(k):sum(v)/len(v) for k,v in atoms.items()},old_all3=sum(all(v.values()) for v in olds.values())/len(olds) if olds else None,old_n=len(olds),old_sources={k:sum(v[k] for v in olds.values())/len(olds) if olds else None for k in ['H0','H1','H2']},seen_A=sum(r['joint'] for r in groups['seen_A'])/len(groups['seen_A']),seen_D=sum(r['joint'] for r in groups['seen_D'])/len(groups['seen_D']),seen_D_full=sum(r['full'] for r in groups['seen_D'])/len(groups['seen_D']),seen_D_current_wrong=sum(r['trajectory_target'] for r in groups['seen_D']),nll=nll,U_used=False,G_today_used=False)

@torch.no_grad()
def diagnose(e,Q,payloads,plans,byid,seed,method,step):
    diag=json.loads((ROOT/'data/diagnostic_ids.json').read_text());curves=[]
    for split in ['train','dev']:
        index={w['record_id']:i for i,w in enumerate(plans[split])};ix=[index[rid] for rid in diag[split]['main']]
        ar,_=atom_eval(e,Q,[byid[rid] for rid in diag[split]['atomic']],seed,method,split,step,True)
        rows=ar+old_eval(e,Q,payloads[split],plans[split],seed,method,split,step,ix,True)+seen_eval(e,Q,payloads[split],plans[split],seed,method,split,step,ix)
        write(ROOT/f'learning/{method}_s{seed}_{split}_{step}.jsonl',rows)
        curves.append(dict(seed=seed,method=method,step=step,split=split,**diagnostic_summary(rows)))
    print('diagnostic',seed,method,step,curves[-1]['atomic_macro'],curves[-1]['old_all3'],curves[-1]['seen_D_full'],flush=True)
    return curves

def train_group(e,P,G,payloads,metas,plans,byid,schedule,seed,method):
    done=ROOT/f'training/{method}_s{seed}.json';initial=statehash(P.state_dict());schedhash=digest(ROOT/f'data/schedule_s{seed}.jsonl')
    if done.exists():
        z=json.loads(done.read_text());assert z['updates']==200 and digest(ROOT/z['final_path'])==z['final_sha256'];return
    seed_all(seed);T=load_editor(seed,'P',train=True);assert statehash(T.state_dict())==initial
    assert all(p.data_ptr()!=q.data_ptr() for p,q in zip(T.parameters(),P.parameters()))
    opt=torch.optim.AdamW(T.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay']);assert not opt.state
    start=time.monotonic();logs=[];curves=[];counts=dict(instances=0,block_instances={k:0 for k in 'ABCD'},tokens={k:0 for k in 'ABCD'},first_current_joint_wrong=0,first_current_exact_wrong=0,D_trajectory_targets=0,D_current_exact_wrong=0);completed=0
    resume=ROOT/f'local/resume_{method}_s{seed}.pt';curvepath=ROOT/f'training/{method}_s{seed}_curves.json'
    if resume.exists():
        z=resume_load(resume,T,opt,schedhash,initial);completed=z['completed'];logs=z['logs'];counts=z['counts'];curves=json.loads(curvepath.read_text()) if curvepath.exists() else []
    def save():
        resume_save(resume,T,opt,completed,logs,counts,schedhash,initial);dump(curvepath,curves)
    try:
        if completed==0 and not curves:curves+=diagnose(e,T,payloads,plans,byid,seed,method,0);save()
        for batch in schedule[completed:]:
            e.check(150);opt.zero_grad(set_to_none=True);inputs=step_inputs(e,payloads['train'],plans['train'],byid,batch)
            before=statehash(T.state_dict());loss,z=four_block_loss(e,T,inputs,method);assert torch.isfinite(loss)
            loss.backward();assert any(p.grad is not None and p.grad.abs().sum()>0 for p in T.parameters())
            assert all(p.grad is None for p in e.model.parameters()) and all(p.grad is None for ed in [P,G] for p in ed.parameters())
            torch.nn.utils.clip_grad_norm_(T.parameters(),CFG['gradient_clip']);opt.step();completed=batch['update']
            wrong=sum(not o['joint'] for o in z['current']);exactwrong=sum(not o['exact'] for o in z['current']);traj=sum(not o['joint'] for o in z['source_current']);dex=sum(not o['exact'] for o in z['source_current'])
            counts['instances']+=32;counts['first_current_joint_wrong']+=wrong;counts['first_current_exact_wrong']+=exactwrong;counts['D_trajectory_targets']+=traj;counts['D_current_exact_wrong']+=dex
            for k in 'ABCD':counts['tokens'][k]+=z['tokens'][k];counts['block_instances'][k]+=8
            logs.append(dict(step=completed,loss=float(loss.detach()),block_losses={k:float(v.detach()) for k,v in z['losses'].items()},tokens=z['tokens'],T_before_update_hash=before,D_producer_hash=before if method=='O' else initial if method=='F' else 'frozen encoder',D_input_hash=statehash(z['D_input']),first_wrong=wrong,D_trajectory_targets=traj,current_records=[dict(world_id=w['record_id'],**o,D_current=z['source_current'][j],D_trajectory_target=not z['source_current'][j]['joint']) for j,(w,o) in enumerate(zip(inputs['worlds'],z['current']))]))
            if completed%10==0:save()
            if completed in CFG['checkpoints']:
                curves+=diagnose(e,T,payloads,plans,byid,seed,method,completed)
                snap=ROOT/f'local/{method}_s{seed}_step{completed}.pt';torch.save({k:v.detach().cpu() for k,v in T.state_dict().items()},snap);save()
        assert completed==200 and counts['instances']==6400 and statehash(T.state_dict())!=initial
        for meta in metas.values():assert digest(meta['cache_path'])==meta['cache_sha256']
        final=ROOT/f'checkpoints/{method}_s{seed}_final.pt';final.parent.mkdir(parents=True,exist_ok=True);torch.save({k:v.detach().cpu() for k,v in T.state_dict().items()},final)
        write(ROOT/f'training/{method}_s{seed}_steps.jsonl.gz',logs)
        dump(done,dict(seed=seed,method=method,updates=200,initial_hash=initial,final_path=str(final.relative_to(ROOT)),final_sha256=digest(final),final_state_hash=statehash(T.state_dict()),schedule_sha256=schedhash,counts=counts,maintenance_source_counts=dict(collections.Counter(src for b in schedule for src in b['maintenance_sources'])),training_seconds=time.monotonic()-start,peak_cuda_bytes=torch.cuda.max_memory_allocated(),frozen_cache_unchanged=True,fresh_optimizer=True,no_U_or_G_today_in_train_dev=True,curves=curves,job_id=os.environ['SLURM_JOB_ID']))
    finally:save()
    del T,opt;torch.cuda.empty_cache()

@torch.no_grad()
def final_model(e,Q,payload,plans,atomic_worlds,seed,method,split):
    rows,_=atom_eval(e,Q,atomic_worlds,seed,method,split,200)
    rows+=old_eval(e,Q,payload,plans,seed,method,split,200)
    for ix in chunks(list(range(len(plans)))):
        bw=[plans[i] for i in ix];gates=[payload['gates'][i] for i in ix];st={n:slice_state(v,ix) for n,v in payload['states'].items()};current={n:[v[i] for i in ix] for n,v in payload['current'].items()}
        def record(kind,source,input_state,cur,obs,reset_same=None):
            for j,(w,o,c) in enumerate(zip(bw,obs,cur)):
                row=dict(kind=kind,seed=seed,method=method,split=split,step=200,world_id=w['record_id'],source=source,matched=gates[j]['fixed_gate']['matched'],match_failures=gates[j]['fixed_gate']['failures'],natural_mask_equal=gates[j]['natural_mask_equal'],current=c,current_joint=c['joint'],current_exact=c['exact'],full=full_success(c,o),full_exact=c['exact'] and o['exact'],**state_fields(input_state,j),**o)
                if reset_same is not None:row['reset_equals_natural']=reset_same[j]
                rows.append(row)
        for source in ['E','P','G','U']:
            before=statehash(st[source]);obs,_=observe(e,edit(Q,st[source]),bw,-1);assert statehash(st[source])==before
            record('fixed',source,st[source],current[source],obs)
        for source in ['P','G','U']:
            reset=encode(e,[o['output'] for o in current[source]]);same=[all(torch.equal(reset[k][j],st['E'][k][j]) for k in reset) for j in range(len(bw))]
            for j,g in enumerate(gates):
                if g['fixed_gate']['matched']:assert same[j]
            obs,_=observe(e,edit(Q,reset),bw,-1);record('reset_fixed',source,reset,current[source],obs,same)
        h1=edit(Q,st['start']);first,_=observe(e,h1,bw,0);h1hash=statehash(h1);second,_=observe(e,edit(Q,h1),bw,-1);assert statehash(h1)==h1hash
        for j,(w,a,b) in enumerate(zip(bw,first,second)):
            rows.append(dict(kind='self_first',seed=seed,method=method,split=split,step=200,world_id=w['record_id'],source='Q',**state_fields(st['start'],j),**a))
        record('self_second','Q',h1,first,second)
        for r in rows[-len(bw):]:r['first_failure']=1 if not r['current_joint'] else 2 if not r['joint'] else None
        reset=encode(e,[a['output'] for a in first]);same=[all(torch.equal(reset[k][j],st['E'][k][j]) for k in reset) for j in range(len(bw))]
        obs,_=observe(e,edit(Q,reset),bw,-1);record('reset_self','Q',reset,first,obs,same)
    return rows

@torch.no_grad()
def final_confirmation(e,P,G,worlds,seed):
    assert all(json.loads((ROOT/f'training/{m}_s{seed}.json').read_text())['updates']==200 for m in CFG['methods'])
    U=load_editor(seed,'U',final_heldout=True);uh=statehash(U.state_dict());caches={};metas={};plans={}
    for split in ['iid','template_ood']:
        plans[split]=[w for w in worlds if w['split']==split and w['record_status']=='recorded_plan']
        caches[split],metas[split]=build_cache(e,P,G,plans[split],seed,'confirm_'+split,U)
    dump(ROOT/f'data/confirm_cohort_s{seed}.json',dict(locked_before_any_receiver=True,T_current_not_used=True,files={sp:digest(ROOT/f'data/confirm_{sp}_s{seed}.json') for sp in plans},coverage={sp:sum(g['fixed_gate']['matched'] for g in caches[sp]['gates']) for sp in plans}))
    for method in ['P']+CFG['methods']:
        if method=='P':Q=P
        else:
            z=json.loads((ROOT/f'training/{method}_s{seed}.json').read_text());p=ROOT/z['final_path'];assert digest(p)==z['final_sha256']
            Q=Editor().cuda().float().eval();Q.load_state_dict(torch.load(p,map_location='cuda',weights_only=True))
            for param in Q.parameters():param.requires_grad_(False);param.grad=None
        for split in plans:
            e.check(120);out=ROOT/f'outputs/{method}_s{seed}_{split}.jsonl'
            if not out.exists():
                rows=final_model(e,Q,caches[split],plans[split],[w for w in worlds if w['split']==split],seed,method,split)
                assert len(rows)==8480;write(out,rows);print('confirmation',seed,method,split,len(rows),flush=True)
        if method!='P':del Q
    assert statehash(U.state_dict())==uh and all(p.grad is None and not p.requires_grad for p in U.parameters())
    for meta in metas.values():assert digest(meta['cache_path'])==meta['cache_sha256']
    return dict(U_frozen_before=uh,U_frozen_after=statehash(U.state_dict()),U_loaded_only_after_three_trainings=True,cohort_counts={sp:sum(g['fixed_gate']['matched'] for g in caches[sp]['gates']) for sp in plans})

@torch.no_grad()
def historical_smoke(e,P,G):
    hist=json.loads((G14/'data/history_batches.json').read_text())['worlds']['iid'];expected=read(G14/'data/history_expected.jsonl');checks=[]
    start=encode(e,[render(w,frame(w,1)) for w in hist])
    for label,Q in [('G',G),('F3',P)]:
        st=start
        for step in [1,2]:
            st=edit(Q,st);obs,_=observe(e,st,hist,1-step)
            for w,o in zip(hist,obs):
                oldrow=next(r for r in expected if r['seed']==42 and r['split']=='iid' and r['method']==('T0' if label=='G' else label) and r['record_id']==w['record_id'] and r['step']==step)
                assert o['output']==oldrow['output'] and o['score']==oldrow['score'] and o['normal_end']==oldrow['normal_end']
                checks.append(dict(model=label,world_id=w['record_id'],step=step,passed=True))
    return checks

def smoke(e):
    verify_lock();seed_all(42);P=load_editor(42,'P');G=load_editor(42,'G');bh=statehash(e.model.state_dict());ph=statehash(P.state_dict());gh=statehash(G.state_dict())
    history_checks=historical_smoke(e,P,G);ws=read(ROOT/'data/train_worlds.jsonl');byid={w['record_id']:w for w in ws}
    plans=[w for w in ws if w['record_status']=='recorded_plan'][:16];payload,meta=build_cache(e,P,G,plans,42,'smoke_train')
    order=dict(main=[w['record_id'] for w in plans],maintenance=[w['record_id'] for w in plans]);base=read(ROOT/'data/sample_schedule.jsonl')[:2];sched=project_schedule(payload,order,base,True)
    checks=[];times=[];beforecache=meta['cache_sha256']
    for method in CFG['methods']:
        seed_all(42);T=load_editor(42,'P',True);initial=statehash(T.state_dict());assert initial==ph
        opt=torch.optim.AdamW(T.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay']);assert not opt.state
        inp=step_inputs(e,payload,plans,byid,sched[0]);h1=T(inp['start']['memory'],inp['start']['mask']);h1.retain_grad()
        dinput=continuation_state('O',h1,inp);lD,_=ce(e,T(dinput['memory'],dinput['mask']),dinput['mask'],inp['next_gold']);lD.backward()
        assert h1.grad is None and any(p.grad is not None and p.grad.abs().sum()>0 for p in T.parameters());opt.zero_grad(set_to_none=True)
        lA,_=ce(e,h1,inp['start']['mask'],inp['first_gold']);lA.backward();assert h1.grad is not None and h1.grad.abs().sum()>0;opt.zero_grad(set_to_none=True)
        begin=time.monotonic();loss,z=four_block_loss(e,T,inp,method);loss.backward();norms=[float(p.grad.norm()) for p in T.parameters()];assert sum(norms)>0
        torch.nn.utils.clip_grad_norm_(T.parameters(),CFG['gradient_clip']);opt.step();torch.cuda.synchronize();times.append(time.monotonic()-begin)
        assert statehash(T.state_dict())!=initial and all(p.grad is None for p in e.model.parameters())
        path=ROOT/f'local/smoke_resume_{method}.pt';resume_save(path,T,opt,1,[],{},'smoke_schedule',initial)
        inp2=step_inputs(e,payload,plans,byid,sched[1]);opt.zero_grad(set_to_none=True);loss2,z2=four_block_loss(e,T,inp2,method);loss2.backward();torch.nn.utils.clip_grad_norm_(T.parameters(),1.0);opt.step();after2=statehash(T.state_dict())
        restored=load_editor(42,'P',True);ropt=torch.optim.AdamW(restored.parameters(),lr=.001,weight_decay=0);resume_load(path,restored,ropt,'smoke_schedule',initial)
        assert all(p.data_ptr()!=q.data_ptr() for p,q in zip(T.parameters(),restored.parameters()))
        ropt.zero_grad(set_to_none=True);rloss,_=four_block_loss(e,restored,inp2,method);rloss.backward();torch.nn.utils.clip_grad_norm_(restored.parameters(),1.0);ropt.step();assert statehash(restored.state_dict())==after2
        checks.append(dict(method=method,initial_hash=initial,independent_optimizer=True,loss=float(loss),grad_norms=norms,first_gradient_retained=True,second_detached=True,decoder_gradient_reaches_T=True,save_optimizer_RNG_resume_equal=True,T_updated=True,actual_first_outputs=z['current']))
    atomws=[]
    for status in ['recorded_plan','reported_cancelled','reported_completed']:atomws += [w for w in ws if w['record_status']==status][:16]
    ar,atomseconds=atom_eval(e,P,atomws,42,'smoke','train',0,True);assert len(ar)==640
    write(ROOT/'smoke_atomic.jsonl.gz',ar)
    assert ph==statehash(P.state_dict()) and gh==statehash(G.state_dict()) and bh==statehash(e.model.state_dict()) and beforecache==digest(meta['cache_path'])
    loaded=torch.load(meta['cache_path'],map_location='cpu',weights_only=True);assert all(statehash(loaded['states'][n])==h for n,h in meta['tensor_hashes'].items())
    st=slice_state(payload['states']['P'],list(range(16)));replay=e.decode(st['memory'],st['mask'])[0];assert replay==[o['output'] for o in payload['current']['P']]
    dump(ROOT/'smoke_test.json',dict(passed=True,job_id=os.environ['SLURM_JOB_ID'],checks=checks,historical_checks=history_checks,U_never_loaded=True,new_confirmation_never_accessed=True,frozen_ED_P_G=True,cache_unchanged=True,cache_save_replay_equal=True,update_seconds=times,atomic_640_seconds=atomseconds,cache16_seconds=meta['cache_seconds'],elapsed_seconds=time.monotonic()-e.start,gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated()))
    print('G15 smoke passed',flush=True)

def main_seed(e,seed):
    verify_lock();assert json.loads((ROOT/'smoke_test.json').read_text())['passed'];seed_all(seed)
    P=load_editor(seed,'P');G=load_editor(seed,'G');before=dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()))
    worlds=read(ROOT/'data/worlds.jsonl');byid={w['record_id']:w for w in worlds};plans={};payloads={};metas={}
    for split in ['train','dev']:
        plans[split]=[w for w in worlds if w['split']==split and w['record_status']=='recorded_plan'];payloads[split],metas[split]=build_cache(e,P,G,plans[split],seed,'repair_'+split)
    order=json.loads((ROOT/'data/world_order.json').read_text());schedule=project_schedule(payloads['train'],order,read(ROOT/'data/sample_schedule.jsonl'))
    schedulepath=ROOT/f'data/schedule_s{seed}.jsonl'
    if schedulepath.exists():assert read(schedulepath)==schedule
    else:write(schedulepath,schedule)
    dump(ROOT/f'data/train_cohort_s{seed}.json',dict(before_any_T_update=True,P_gate_n=sum(g['P_gate']['matched'] for g in payloads['train']['gates']),old_gate_n=sum(g['old_gate']['matched'] for g in payloads['train']['gates']),schedule_sha256=digest(schedulepath),shared_by=['N','F','O'],U_used=False))
    for method in CFG['methods']:
        train_group(e,P,G,payloads,metas,plans,byid,schedule,seed,method)
        assert before==dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()))
    finalaudit=final_confirmation(e,P,G,worlds,seed)
    after=dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()));assert before==after
    dump(ROOT/f'seed_s{seed}_complete.json',dict(passed=True,seed=seed,methods=CFG['methods'],updates_per_method=200,frozen_before=before,frozen_after=after,**finalaudit,caches_unchanged=True,job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ.get('SLURM_ARRAY_JOB_ID'),array_task_id=os.environ.get('SLURM_ARRAY_TASK_ID'),gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-e.start))
    print('G15 SEED COMPLETE',seed,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true');parser.add_argument('--seed-index',type=int);args=parser.parse_args()
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'All GPU requires sbatch allocation and srun step'
    from engine import Engine
    engine=Engine();engine.limit=float(os.environ['G15_WALL_SECONDS']);assert engine.kw=={k:CFG[k] for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']}
    if args.smoke:smoke(engine)
    else:main_seed(engine,json.loads((ROOT/'runs_manifest.json').read_text())['array_mapping'][args.seed_index]['seed'])
