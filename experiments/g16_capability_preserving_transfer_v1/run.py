"""G16 Slurm-only N/F training, immutable dev selection, then globally gated confirmation."""
import argparse, contextlib, shutil, time
import torch
from common_g16 import *
from selection import qualify,write_once,check_selection_lock

# Reuse actual G15 full-state/scorer/CE interfaces, in a separately loaded module.
# Only module-local output/config bindings change; old files and artifacts stay read-only.
base=load_module('g16_readonly_g15_runtime',G15/'run.py');base.ROOT=ROOT;base.CFG=CFG
_original_loader=base.load_editor
def load_editor(seed,role,train=False,final_heldout=False):
    if role=='U':
        assert final_heldout and not train;check_selection_lock()
    if train:assert role=='P'
    return _original_loader(seed,role,train,final_heldout)
base.load_editor=load_editor
Editor=base.Editor;ce=base.ce;encode=base.encode;state_fields=base.state_fields
edit=base.edit;observe=base.observe;chunks=base.chunks;slice_state=base.slice_state
build_cache=base.build_cache;step_inputs=base.step_inputs;seed_all=base.seed_all

@contextlib.contextmanager
def preserve_rng():
    py=random.getstate();cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_initialized() else None
    try:yield
    finally:
        random.setstate(py);torch.set_rng_state(cpu)
        if cuda is not None:torch.cuda.set_rng_state_all(cuda)

def save_editor(path,T):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert statehash(torch.load(path,map_location='cpu',weights_only=True))==statehash(T.state_dict());return digest(path)
    tmp=path.with_suffix('.tmp');torch.save({k:v.detach().cpu() for k,v in T.state_dict().items()},tmp);tmp.replace(path);return digest(path)

def four_loss(e,T,inputs,method):
    assert method in ['N','F']
    return base.four_block_loss(e,T,inputs,method)

def diagnostic_rows(e,Q,payload,plans,worlds,seed,method,step,split,full_dev):
    diag=json.loads((ROOT/'data/diagnostic_ids.json').read_text())
    if full_dev:ix=list(range(len(plans)));aw=[w for w in worlds if w['split']=='dev']
    else:
        index={w['record_id']:i for i,w in enumerate(plans)};ix=[index[rid] for rid in diag[split]['main']]
        byid={w['record_id']:w for w in worlds};aw=[byid[rid] for rid in diag[split]['atomic']]
    ar,seconds=base.atom_eval(e,Q,aw,seed,method,split,step,True)
    rows=ar+base.old_eval(e,Q,payload,plans,seed,method,split,step,ix,True)+base.seen_eval(e,Q,payload,plans,seed,method,split,step,ix)
    for r in rows:
        r['D_input_source']='fixed P' if method=='F' else 'natural E'
        r['not_updated_self_second']=r['kind']=='seen_D'
    return rows,seconds

def counts_for_selection(rows,seed,step,method):
    atoms=[]
    for status,d,p in sorted({(r['status'],r['offset'],r['perspective']) for r in rows if r['kind']=='atomic'}):
        rs=[r for r in rows if r['kind']=='atomic' and (r['status'],r['offset'],r['perspective'])==(status,d,p)]
        atoms.append(dict(status=status,offset=d,perspective=p,k=sum(r['joint'] for r in rs),n=len(rs)))
    old=collections.defaultdict(dict)
    for r in rows:
        if r['kind']=='old' and r['matched']:old[r['world_id']][r['source']]=r['joint']
    assert all(set(v)=={'H0','H1','H2'} for v in old.values())
    a=[r for r in rows if r['kind']=='seen_A'];d=[r for r in rows if r['kind']=='seen_D' and r['current_joint'] and r['current_exact'] and r['current']['normal_end']]
    return dict(seed=seed,step=step,split='dev',method=method,atomic_cells=atoms,old_k=sum(all(v.values()) for v in old.values()),old_n=len(old),A_k=sum(r['joint'] for r in a),A_n=len(a),D_k=sum(r['joint'] for r in d),D_n=len(d))

def train_group(e,P,G,payloads,plans,worlds,schedule,seed,method):
    done=ROOT/f'training/{method}_s{seed}.json';initial=statehash(P.state_dict());schedhash=digest(ROOT/f'data/schedule_s{seed}.jsonl')
    if done.exists():
        z=json.loads(done.read_text());assert z['updates']==200 and digest(ROOT/z['final_path'])==z['final_sha256'];return
    seed_all(seed);T=load_editor(seed,'P',True);assert statehash(T.state_dict())==initial
    assert all(p.data_ptr()!=q.data_ptr() for p,q in zip(T.parameters(),P.parameters()))
    opt=torch.optim.AdamW(T.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay']);assert not opt.state
    byid={w['record_id']:w for w in worlds};completed=0;logs=[];curves=[];candidates=[]
    counts=dict(instances=0,block_instances={k:0 for k in 'ABCD'},tokens={k:0 for k in 'ABCD'},first_current_joint_wrong=0,first_current_exact_wrong=0,D_trajectory_targets=0,D_current_exact_wrong=0)
    resume=ROOT/f'local/resume_{method}_s{seed}.pt';progress=ROOT/f'training/{method}_s{seed}_progress.json';start=time.monotonic()
    if resume.exists():
        z=base.resume_load(resume,T,opt,schedhash,initial);completed=z['completed'];logs=z['logs'];counts=z['counts']
        q=json.loads(progress.read_text());curves=q['curves'];candidates=q['candidates']
    def save():
        base.resume_save(resume,T,opt,completed,logs,counts,schedhash,initial)
        dump(progress,dict(curves=curves,candidates=candidates))
    def monitor(step):
        nonlocal curves,candidates
        for split in ['train','dev']:
            needed=step in CFG['checkpoints'] if split=='train' else step==0 or step in CFG['candidates']
            if not needed or any(c['step']==step and c['split']==split for c in curves):continue
            e.check(120);before=statehash(T.state_dict());path=ROOT/f'local/{method}_s{seed}_step{step}.pt';sha=save_editor(path,T)
            with preserve_rng():rows,_=diagnostic_rows(e,T,payloads[split],plans[split],worlds,seed,method,step,split,split=='dev')
            assert statehash(T.state_dict())==before
            write(ROOT/f'learning/{method}_s{seed}_{split}_{step}.jsonl',rows)
            curves.append(dict(seed=seed,method=method,step=step,split=split,checkpoint_sha256=sha,checkpoint_state_hash=before,full_dev=split=='dev',**base.diagnostic_summary(rows)))
            if split=='dev' and step in CFG['candidates']:
                candidate=counts_for_selection(rows,seed,step,method)
                candidate.update(checkpoint_sha256=sha,checkpoint_state_hash=before,checkpoint_path=str(path.relative_to(ROOT)))
                candidates.append(candidate);dump(ROOT/f'training/{method}_s{seed}_candidates.json',candidates)
                if method=='F' and qualify(candidate)['qualified'] and not (ROOT/f'selection_s{seed}.json').exists():
                    guard=ROOT/f'checkpoints/F_s{seed}_guard.pt';shutil.copyfile(path,guard);assert digest(guard)==sha
                    write_once(ROOT/f'selection_s{seed}.json',dict(seed=seed,selected_step=step,checkpoint_path=str(guard.relative_to(ROOT)),checkpoint_sha256=sha,checkpoint_state_hash=before,candidate=candidate,U_used=False,G_today_next_used=False,confirm_used=False,rule='earliest qualifying; immutable',created_at_optimizer_step=step))
            save();print('G16 diagnostic',seed,method,step,split,curves[-1]['atomic_macro'],curves[-1]['old_all3'],curves[-1]['seen_D'],flush=True)
    try:
        # Restore a completed optimizer update before any interrupted diagnostic.
        monitor(completed)
        for batch in schedule[completed:]:
            e.check(180);opt.zero_grad(set_to_none=True);inp=step_inputs(e,payloads['train'],plans['train'],byid,batch)
            before=statehash(T.state_dict());loss,z=four_loss(e,T,inp,method);assert torch.isfinite(loss)
            loss.backward();assert any(p.grad is not None and p.grad.abs().sum()>0 for p in T.parameters())
            assert all(p.grad is None for p in e.model.parameters()) and all(p.grad is None for ed in [P,G] for p in ed.parameters())
            torch.nn.utils.clip_grad_norm_(T.parameters(),CFG['gradient_clip']);opt.step();completed=batch['update']
            wrong=sum(not o['joint'] for o in z['current']);exactwrong=sum(not o['exact'] for o in z['current']);traj=sum(not o['joint'] for o in z['source_current']);dex=sum(not o['exact'] for o in z['source_current'])
            counts['instances']+=32;counts['first_current_joint_wrong']+=wrong;counts['first_current_exact_wrong']+=exactwrong;counts['D_trajectory_targets']+=traj;counts['D_current_exact_wrong']+=dex
            for k in 'ABCD':counts['tokens'][k]+=z['tokens'][k];counts['block_instances'][k]+=8
            logs.append(dict(step=completed,loss=float(loss.detach()),block_losses={k:float(v.detach()) for k,v in z['losses'].items()},tokens=z['tokens'],T_before_update_hash=before,D_producer_hash=initial if method=='F' else 'frozen encoder',D_input_hash=statehash(z['D_input']),first_wrong=wrong,D_trajectory_targets=traj,current_records=[dict(world_id=w['record_id'],**o,D_current=z['source_current'][j],D_trajectory_target=not z['source_current'][j]['joint']) for j,(w,o) in enumerate(zip(inp['worlds'],z['current']))]))
            if completed%10==0 or completed in CFG['candidates']:save()
            monitor(completed)
        assert completed==200 and counts['instances']==6400 and [c['step'] for c in candidates]==CFG['candidates']
        if method=='F' and not (ROOT/f'selection_s{seed}.json').exists():write_once(ROOT/f'selection_s{seed}.json',dict(seed=seed,selected_step=None,reason='no qualifying candidate',U_used=False,confirm_used=False))
        final=ROOT/f'checkpoints/{method}_s{seed}_final.pt';shutil.copyfile(ROOT/f'local/{method}_s{seed}_step200.pt',final)
        write(ROOT/f'training/{method}_s{seed}_steps.jsonl.gz',logs)
        dump(done,dict(seed=seed,method=method,updates=200,initial_hash=initial,final_path=str(final.relative_to(ROOT)),final_sha256=digest(final),final_state_hash=statehash(T.state_dict()),schedule_sha256=schedhash,counts=counts,curves=curves,training_seconds=time.monotonic()-start,fresh_optimizer=True,no_U_or_G_today_receiver_in_train_dev=True,RNG_preserved_around_all_diagnostics=True,peak_cuda_bytes=torch.cuda.max_memory_allocated(),job_id=os.environ['SLURM_JOB_ID']))
    finally:save()
    del T,opt;torch.cuda.empty_cache()

def train_seed(e,seed):
    verify_lock();seed_all(seed);P=load_editor(seed,'P');G=load_editor(seed,'G');before=dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()))
    worlds=read(ROOT/'data/worlds.jsonl');plans={};payloads={};metas={}
    for split in ['train','dev']:
        plans[split]=[w for w in worlds if w['split']==split and w['record_status']=='recorded_plan'];payloads[split],metas[split]=build_cache(e,P,G,plans[split],seed,'repair_'+split)
    schedule=base.project_schedule(payloads['train'],json.loads((ROOT/'data/world_order.json').read_text()),read(ROOT/'data/sample_schedule.jsonl'))
    path=ROOT/f'data/schedule_s{seed}.jsonl'
    if path.exists():assert read(path)==schedule
    else:write(path,schedule)
    dump(ROOT/f'data/train_cohort_s{seed}.json',dict(before_any_T_update=True,P_n=sum(g['P_gate']['matched'] for g in payloads['train']['gates']),old_n=sum(g['old_gate']['matched'] for g in payloads['train']['gates']),N=512,shared_by=['N','F'],schedule_sha256=digest(path),U_used=False))
    for method in CFG['methods']:
        train_group(e,P,G,payloads,plans,worlds,schedule,seed,method)
        assert before==dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()))
    for m in metas.values():assert digest(m['cache_path'])==m['cache_sha256']
    dump(ROOT/f'seed_s{seed}_train_complete.json',dict(passed=True,seed=seed,frozen_before=before,frozen_after=before,all_methods200=True,U_never_loaded=True,caches_unchanged=True,job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ.get('SLURM_ARRAY_JOB_ID'),array_task_id=os.environ.get('SLURM_ARRAY_TASK_ID'),gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-e.start))
    print('G16 TRAIN COMPLETE',seed,flush=True)

def final_versions(seed):
    mapping=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models'][str(seed)]
    versions=[dict(method='P',step=0,path=mapping['P']['path'],sha256=mapping['P']['sha256'])]
    for m in ['N','F']:
        z=json.loads((ROOT/f'training/{m}_s{seed}.json').read_text());versions.append(dict(method=m+'-final',step=200,path=str(ROOT/z['final_path']),sha256=z['final_sha256']))
    selected=json.loads((ROOT/f'selection_s{seed}.json').read_text())
    if selected['selected_step'] is not None:versions.append(dict(method='F-guard',step=selected['selected_step'],path=str(ROOT/selected['checkpoint_path']),sha256=selected['checkpoint_sha256']))
    return versions

@torch.no_grad()
def confirm_seed(e,seed):
    verify_lock();lock=check_selection_lock();seed_all(seed);P=load_editor(seed,'P');G=load_editor(seed,'G');U=load_editor(seed,'U',final_heldout=True)
    before=dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()),U=statehash(U.state_dict()))
    worlds=read(ROOT/'data/worlds.jsonl');payloads={};metas={};plans={}
    for split in ['iid','template_ood']:
        plans[split]=[w for w in worlds if w['split']==split and w['record_status']=='recorded_plan'];payloads[split],metas[split]=build_cache(e,P,G,plans[split],seed,'confirm_'+split,U)
    dump(ROOT/f'data/confirm_cohort_s{seed}.json',dict(locked_before_receiver=True,T_current_unused=True,coverage={sp:sum(g['fixed_gate']['matched'] for g in p['gates']) for sp,p in payloads.items()},selection_lock_sha256=digest(ROOT/'selection_lock.json')))
    reused=[];previous={}
    for v in final_versions(seed):
        assert digest(v['path'])==v['sha256'];Q=Editor().cuda().float().eval();Q.load_state_dict(torch.load(v['path'],map_location='cuda',weights_only=True))
        for p in Q.parameters():p.requires_grad_(False)
        for split in plans:
            path=ROOT/f'outputs/{v["method"]}_s{seed}_{split}.jsonl'
            if path.exists():previous[v['sha256'],split]=path;continue
            key_=v['sha256'],split
            if key_ in previous:
                rows=read(previous[key_]);reused.append(dict(version=v['method'],same_SHA_as='F-final',split=split))
                for r in rows:r['method']=v['method'];r['actual_updates']=v['step'];r['duplicate_same_checkpoint']=True
            else:
                e.check(120);rows=base.final_model(e,Q,payloads[split],plans[split],[w for w in worlds if w['split']==split],seed,v['method'],split)
                for r in rows:r['actual_updates']=v['step'];r['checkpoint_sha256']=v['sha256'];r['duplicate_same_checkpoint']=False
                previous[key_]=path
            assert len(rows)==8480;write(path,rows);print('G16 confirmation',seed,v['method'],split,len(rows),flush=True)
        del Q;torch.cuda.empty_cache()
    after=dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()),U=statehash(U.state_dict()));assert before==after
    for m in metas.values():assert digest(m['cache_path'])==m['cache_sha256']
    dump(ROOT/f'seed_s{seed}_confirm_complete.json',dict(passed=True,seed=seed,versions=final_versions(seed),same_SHA_reused=reused,frozen_before=before,frozen_after=after,U_loaded_after_global_lock=True,selection_lock_sha256=digest(ROOT/'selection_lock.json'),caches_unchanged=True,job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ.get('SLURM_ARRAY_JOB_ID'),array_task_id=os.environ.get('SLURM_ARRAY_TASK_ID'),gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-e.start))
    print('G16 CONFIRM COMPLETE',seed,flush=True)

def historical(e,P):
    expected={(r['world_id'],r['kind']):r for r in read(ROOT/'data/history_expected.jsonl')};checks=[]
    for split,ws in json.loads((ROOT/'data/history_worlds.json').read_text()).items():
        start=encode(e,[render(w,frame(w,1)) for w in ws]);h=edit(P,start)
        for kind,d in [('self_first',0),('self_second',-1)]:
            if kind=='self_second':h=edit(P,h)
            os_,_=observe(e,h,ws,d)
            for w,o in zip(ws,os_):
                r=expected[w['record_id'],kind];assert all(o[k]==r[k] for k in ['output','normal_end','score','exact','joint'])
                checks.append(dict(split=split,world_id=w['record_id'],kind=kind,passed=True))
    return checks

def smoke(e):
    verify_lock();seed_all(42);P=load_editor(42,'P');G=load_editor(42,'G');before=dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict()))
    history=historical(e,P);worlds=read(ROOT/'data/worlds.jsonl');plans=[w for w in worlds if w['split']=='train' and w['record_status']=='recorded_plan'][:16]
    payload,meta=build_cache(e,P,G,plans,42,'smoke_train');order={n:[w['record_id'] for w in plans] for n in ['main','maintenance']};schedule=base.project_schedule(payload,order,read(ROOT/'data/sample_schedule.jsonl')[:2],True)
    byid={w['record_id']:w for w in worlds};inp=step_inputs(e,payload,plans,byid,schedule[0]);times=[];checks=[]
    for method in CFG['methods']:
        seed_all(42);T=load_editor(42,'P',True);assert statehash(T.state_dict())==before['P'];opt=torch.optim.AdamW(T.parameters(),lr=.001,weight_decay=0);assert not opt.state
        h1=T(inp['start']['memory'],inp['start']['mask']);h1.retain_grad();l,_=ce(e,h1,inp['start']['mask'],inp['first_gold']);l.backward();assert h1.grad is not None and h1.grad.abs().sum()>0;opt.zero_grad(set_to_none=True)
        begin=time.monotonic();loss,z=four_loss(e,T,inp,method);loss.backward();assert any(p.grad is not None and p.grad.abs().sum()>0 for p in T.parameters());torch.nn.utils.clip_grad_norm_(T.parameters(),1);opt.step();torch.cuda.synchronize();times.append(time.monotonic()-begin)
        path=ROOT/f'local/smoke_resume_{method}.pt';base.resume_save(path,T,opt,1,[],{},'smoke',before['P'])
        second=step_inputs(e,payload,plans,byid,schedule[1])
        with preserve_rng():random.random();torch.rand(8,device='cuda')
        opt.zero_grad(set_to_none=True);l,z=four_loss(e,T,second,method);l.backward();torch.nn.utils.clip_grad_norm_(T.parameters(),1);opt.step();goldhash=statehash(T.state_dict())
        clone=load_editor(42,'P',True);co=torch.optim.AdamW(clone.parameters(),lr=.001,weight_decay=0);base.resume_load(path,clone,co,'smoke',before['P']);co.zero_grad(set_to_none=True);l,z=four_loss(e,clone,second,method);l.backward();torch.nn.utils.clip_grad_norm_(clone.parameters(),1);co.step();assert statehash(clone.state_dict())==goldhash
        assert all(p.data_ptr()!=q.data_ptr() for p,q in zip(T.parameters(),clone.parameters()))
        checks.append(dict(method=method,initial_equal_P=True,fresh_independent_optimizer=True,T_updated=True,decoder_memory_gradient=True,first_gradient_retained=True,save_optimizer_rng_and_inserted_monitor_next_update_equal=True))
    dp=[w for w in worlds if w['split']=='dev' and w['record_status']=='recorded_plan'];dev,dm=build_cache(e,P,G,dp,42,'smoke_dev')
    begin=time.monotonic()
    with preserve_rng():dr,_=diagnostic_rows(e,P,dev,dp,worlds,42,'F',0,'dev',True)
    devseconds=time.monotonic()-begin;assert len(dr)==5760
    write(ROOT/'smoke_dev.jsonl.gz',dr)
    # Final-evaluation throughput on16 TRAIN worlds/status; structural U slot is
    # a labeled P placeholder. No U weights or new confirmation worlds accessed.
    pp=json.loads(json.dumps({k:v for k,v in payload.items() if k!='states'}));pp['states']=payload['states'].copy();pp['states']['G']=pp['states']['P'];pp['states']['U']=pp['states']['P'];pp['current']['G']=pp['current']['P'];pp['current']['U']=pp['current']['P']
    for g in pp['gates']:g['fixed_gate']=g['P_gate']
    aw=[]
    for status in ['recorded_plan','reported_cancelled','reported_completed']:aw += [w for w in worlds if w['split']=='train' and w['record_status']==status][:16]
    begin=time.monotonic();fr=base.final_model(e,P,pp,plans,aw,42,'smoke_placeholder_only','train');finalseconds=time.monotonic()-begin;assert len(fr)==848
    write(ROOT/'smoke_final_flow.jsonl.gz',fr)
    assert before==dict(ED=statehash(e.model.state_dict()),P=statehash(P.state_dict()),G=statehash(G.state_dict())) and digest(meta['cache_path'])==meta['cache_sha256']
    assert all(p.grad is None for p in e.model.parameters()) and all(p.grad is None for ed in [P,G] for p in ed.parameters())
    dump(ROOT/'smoke_test.json',dict(passed=True,checks=checks,historical_checks=history,U_never_loaded=True,new_confirmation_never_accessed=True,placeholder_U_is_P_not_scientific=True,frozen_ED_P_G=True,full_dev_rows=5760,full_dev_seconds=devseconds,final_flow_848_seconds=finalseconds,update_seconds=times,cache16_seconds=meta['cache_seconds'],cache128_seconds=dm['cache_seconds'],job_id=os.environ['SLURM_JOB_ID'],gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-e.start))
    print('G16 SMOKE PASSED',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['smoke','train','confirm'],required=True);parser.add_argument('--seed-index',type=int);args=parser.parse_args()
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'All GPU work requires sbatch and srun'
    if args.phase=='confirm':check_selection_lock()
    from engine import Engine
    e=Engine();e.limit=float(os.environ['G16_WALL_SECONDS']);assert e.kw=={k:CFG[k] for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']}
    if args.phase=='smoke':smoke(e)
    else:
        seed=json.loads((ROOT/'runs_manifest.json').read_text())['array_mapping'][args.seed_index]['seed']
        assert json.loads((ROOT/'smoke_test.json').read_text())['passed']
        (train_seed if args.phase=='train' else confirm_seed)(e,seed)
