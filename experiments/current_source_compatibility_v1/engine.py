"""Slurm-only model, source generation, matched supervision, resumable updates."""
import os,time,random,copy,subprocess
import torch
from study import *
from backend import Backend,editors

def guard():
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'Use sbatch and srun'
    assert len(os.environ.get('CUDA_VISIBLE_DEVICES','').split(','))==1,'Exactly one Slurm GPU'
    raw=subprocess.check_output(['squeue','-h','-u',os.environ['USER'],'--states=RUNNING','-o','%i|%b'],text=True)
    import re
    count=sum(int(n) for line in raw.splitlines() for n in re.findall(r'gpu(?::[^,:()]+)*:(\d+)',line))
    assert count<=2,('Account GPU cap exceeded',raw)

def tensorhash(state):
    h=hashlib.sha256()
    for k,v in sorted(state.items()):
      h.update(k.encode());h.update(str(v.dtype).encode());h.update(str(tuple(v.shape)).encode());h.update(v.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
    return h.hexdigest()

def load(eng,path):
    with torch.random.fork_rng(devices=[torch.cuda.current_device()]):
      ed=editors(eng.d,0);ed.load_state_dict(torch.load(path,map_location='cuda',weights_only=True)['editor'])
    return ed.eval()

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');torch.save(value,tmp);tmp.replace(path)

def result(pred,g,w):
    sc=score(pred['text'],g,w,pred['ended']);parsed,grammar=parse(pred['text'],'time',g['structure'],False)
    missing=parsed is None or parsed.get('relative') is None
    semantic_wrong=parsed is not None and parsed.get('relative') is not None and not sc['target']
    content_lost=parsed is not None and not sc['preserved']
    # Categories overlap only in explicit components; unresolved stays unknown.
    return dict(prediction=pred['text'],ended=pred['ended'],generated_tokens=pred['generated_tokens'],score=sc,parsed=parsed,prefix_error=dict(semantic_error=semantic_wrong,content_changed_or_lost=content_lost,unresolved=missing,controlled_completeness_failure=not grammar,termination_failure=not pred['ended']))

@torch.no_grad()
def cache(eng,ed,records,folder,mode,source_sha):
    folder.mkdir(parents=True,exist_ok=True);unique={r['prefix_id']:r for r in records};ordered=sorted(unique.values(),key=lambda r:(r['a'],r['prefix_id']))
    old=folder/'complete.json'
    if old.exists():
      meta=read(old);assert meta['source_sha']==source_sha and meta['mode']==mode
    started=time.monotonic();values={};public=[];shards=[];ws=worldmap();ed.eval()
    batches=[]
    for operation in ('plus','minus'):
      group=[r for r in ordered if r['a']==operation]
      batches.extend(group[j:j+8] for j in range(0,len(group),8))
    for j,batch in enumerate(batches):
      path=folder/f'batch{j:05}.pt';obs=path.with_suffix('.json');op=batch[0]['a'];assert all(r['a']==op for r in batch)
      # Homogeneous prefix sign partitions have lengths divisible by8 formally;
      # smoke data is also constructed to respect this invariant.
      if path.exists() and obs.exists():
       info=read(obs);assert info['source_sha']==source_sha and info['ids']==[r['prefix_id'] for r in batch];payload=torch.load(path,map_location='cpu',weights_only=True);assert digest(path)==info['tensor_file_sha']
      else:
       batch_started=time.monotonic();text=[r['current_text'] if mode=='N' else r['original_text'] for r in batch]
       h,m=eng.encode(text) # Re-encode ORIGINAL natural text at EVERY refresh.
       if mode!='N':
        h=ed[op](h,m).detach()
       assert not h.requires_grad and h.grad_fn is None
       predictions=eng.decode(h,m);payload={r['prefix_id']:{'h':x.cpu(),'m':y.cpu()} for r,x,y in zip(batch,h,m)};save(path,payload)
       observations=[dict(prefix_id=r['prefix_id'],world_id=r['world_id'],initial_state=r['initial_state'],current_state=r['current_state'],a=r['a'],template=r['template'],original_text=r['original_text'],current_text=r['current_text'],mask_length=int(mask.sum()),**result(pred,r['current_gold'],ws[r['world_id']])) for r,pred,mask in zip(batch,predictions,m)]
       torch.cuda.synchronize();info=dict(mode=mode,source_sha=source_sha,at_utc=now(),ids=[r['prefix_id'] for r in batch],tensor_file_sha=digest(path),observations=observations,generation_seconds=time.monotonic()-batch_started);dump(obs,info)
      values.update(payload);public+=info['observations'];shards.append(dict(path=str(path),sha256=digest(path),generation_seconds=info['generation_seconds']))
    jsonl(folder/'prefix_quality.jsonl',public)
    meta=dict(mode=mode,source_sha=source_sha,at_utc=now(),unique_prefixes=len(values),continuation_rows=len(records),generation_depth=0 if mode=='N' else 1,detached=True,fresh_original_encoding=True,shards=shards,success=sum(r['score']['success'] for r in public),semantic_errors=sum(r['prefix_error']['semantic_error'] for r in public),content_changed_or_lost=sum(r['prefix_error']['content_changed_or_lost'] for r in public),unresolved=sum(r['prefix_error']['unresolved'] for r in public),generation_seconds=sum(s['generation_seconds'] for s in shards),seconds_this_invocation=time.monotonic()-started)
    if not old.exists():dump(old,meta)
    return values,read(old)

def rng_state():return dict(python=random.getstate(),torch=torch.get_rng_state(),cuda=torch.cuda.get_rng_state_all())
def restore_rng(r):
    random.setstate(r['python']);torch.set_rng_state(r['torch'].cpu());torch.cuda.set_rng_state_all([x.cpu() for x in r['cuda']])

def optimize(eng,ed,opt,draw,replay,cont,inputs,micro=2):
    ed.train();op=draw['operation'];opt.zero_grad(set_to_none=True);losses={};token_counts={};selected={}
    for role,rs in (('replay',replay),('continuation',cont)):
      total=0;tokens=0;indices=draw[role];selected[role]=[rs[i]['id'] if 'id' in rs[i] else f"{rs[i]['world_id']}_{rs[i]['state']}_{rs[i]['template']}_{rs[i]['operation']}" for i in indices]
      for offset in range(0,4,micro):
       batch=[rs[i] for i in indices[offset:offset+micro]]
       if role=='replay':h,m=eng.cached([r['source'] for r in batch])
       else:h=torch.stack([inputs[r['prefix_id']]['h'] for r in batch]).cuda();m=torch.stack([inputs[r['prefix_id']]['m'] for r in batch]).cuda()
       assert not h.requires_grad and h.grad_fn is None
       out=ed[op](h,m);assert torch.equal(out[m==0],h[m==0])
       ls,nt=eng.ce(out,m,[r['target'] if role=='replay' else r['target_text'] for r in batch]);loss=ls.sum()*.5/4;loss.backward();total+=float(ls.detach().sum())/4;tokens+=int(nt.sum())
      losses[role]=total;token_counts[role]=tokens
    assert all(not p.requires_grad and p.grad is None for p in eng.model.parameters())
    assert not eng.model.training
    assert any(p.grad is not None and float(p.grad.norm())>0 for p in ed[op].parameters())
    torch.nn.utils.clip_grad_norm_(ed.parameters(),1.,error_if_nonfinite=True);opt.step();ed.eval()
    return dict(update=draw['update']+1,operation=op,loss=.5*(losses['replay']+losses['continuation']),losses=losses,target_tokens=token_counts,selected=selected,supervision_units={'replay':4,'continuation':4})

def train_condition(eng,seed,method,stop=200,folder=None,smoke=False):
    folder=folder or ROOT/f'local/s{seed}/{method}';folder.mkdir(parents=True,exist_ok=True)
    cont=rows(ROOT/'data/continuation.jsonl');replay=rows(ROOT/'data/train_core.jsonl');draws=rows(ROOT/f'data/draws_s{seed}.jsonl')
    if smoke:
      allowed={r['prefix_id'] for r in cont[:44]};cont=[r for r in cont if r['prefix_id'] in allowed]
      from prepare import schedule
      draws=schedule(seed,replay,cont,stop)
    ed=load(eng,checkpoint(seed));opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0.0);start=0;logs=[];refreshes=[];active=None
    latest=folder/'latest.pt'
    if latest.exists():
      ck=torch.load(latest,map_location='cuda',weights_only=False);ed.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);restore_rng(ck['rng']);start=ck['update'];logs=ck['logs'];refreshes=ck['refreshes'];active=ck['active_cache']
    began=time.monotonic();opt_seconds=0.;source_seconds=0.;inputs=None
    if method=='N':inputs,meta=cache(eng,ed,cont,folder/'cache_N','N','frozen_encoder');active=str(folder/'cache_N')
    elif method=='F':
      producer=load(eng,checkpoint(seed));inputs,meta=cache(eng,producer,cont,folder/'cache_F','F',digest(checkpoint(seed)));active=str(folder/'cache_F');del producer
    if method in ('N','F') and not refreshes:refreshes=[dict(update=0,**meta)];source_seconds+=meta['seconds_this_invocation']
    for u in range(start,stop):
      if method=='R' and (u%20==0 or inputs is None):
       refresh=u-u%20;active=str(folder/f'cache_R/u{refresh:03}')
       old=next((r for r in refreshes if r['update']==refresh),None)
       source_path=folder/f'sources/update{refresh:03}.pt'
       if old:source_sha=old['source_sha'];assert digest(source_path)==source_sha
       else:
        if not source_path.exists():save(source_path,dict(editor={k:v.detach().cpu() for k,v in ed.state_dict().items()},update=refresh))
        source_sha=digest(source_path)
       producer=load(eng,source_path)
       inputs,meta=cache(eng,producer,cont,Path(active),'R',source_sha);source_seconds+=meta['seconds_this_invocation'];del producer
       if not old:refreshes.append(dict(update=refresh,**meta))
      t=time.monotonic();item=optimize(eng,ed,opt,draws[u],replay,cont,inputs,config()['microbatch']);torch.cuda.synchronize();item['optimizer_seconds']=time.monotonic()-t;opt_seconds+=item['optimizer_seconds'];logs.append(item)
      save(latest,dict(editor=ed.state_dict(),optimizer=opt.state_dict(),update=u+1,rng=rng_state(),logs=logs,refreshes=refreshes,active_cache=active,initial_sha=digest(checkpoint(seed)),draws_sha=digest(ROOT/f'data/draws_s{seed}.jsonl')))
      if (u+1)%20==0:print(f'{seed}/{method} update={u+1}/{stop} loss={item["loss"]:.4f}',flush=True)
      if u+1 in (100,200):save(folder/f'update{u+1:03}.pt',dict(editor={k:v.detach().cpu() for k,v in ed.state_dict().items()},update=u+1,initial_sha=digest(checkpoint(seed))))
    jsonl(folder/'training.jsonl',logs);dump(folder/'refreshes.json',refreshes)
    dump(folder/'training_status.json',dict(seed=seed,method=method,completed_updates=stop,initial_sha=digest(checkpoint(seed)),editor_state_sha=tensorhash(ed.state_dict()),optimizer_seconds_this_invocation=opt_seconds,source_seconds_this_invocation=source_seconds,wall_seconds_this_invocation=time.monotonic()-began))
    return ed,opt,inputs,refreshes
