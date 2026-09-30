"""Current-only cohort lock precedes all new next/long-chain inference."""
import argparse
import torch
from common_g12 import *
@torch.no_grad()
def current(e):
 lock();ws=read('data/worlds.jsonl');allrows=[];shards=[];checkpoint_hashes={f'{s}/{a}':digest(checkpoint(a,s)) for s in CFG['seeds'] for a in CFG['methods']}
 for s in CFG['seeds']:
  for arm in CFG['methods']:
   ed=load_editor(s,arm)
   for split in ['iid','template_ood']:
    sub=[w for w in ws if w['split']==split]
    for i in range(0,len(sub),16):
     e.check(reserve=90);batch=sub[i:i+16];tag=f'{arm}_s{s}_{split}_{i:03d}';pt=ROOT/f'local/latents/{tag}.pt';jp=ROOT/f'outputs/current_shards/{tag}.jsonl'
     if pt.exists() and jp.exists():rs=read(jp)
     else:
      hs=[];ms=[];prefixes=[];sources=[]
      for history in range(3):
       source=[render(w,frame(w,-1+history)) for w in batch];h,m,_=e.encode(source);prefix=[]
       if history==0:prefix=[decode(e,h,m,batch,-1)]
       for k in range(history):h=ed(h,m);prefix.append(decode(e,h,m,batch,history-2-k))
       hs.append(h.cpu());ms.append(m.cpu());prefixes.append(prefix);sources.append(source)
      pt.parent.mkdir(parents=True,exist_ok=True);torch.save(dict(H=torch.stack(hs),mask=torch.stack(ms),record_ids=[w['record_id'] for w in batch]),pt);rs=[]
      for j,w in enumerate(batch):
       outs=[prefixes[k][-1][j] for k in range(3)];strict=all(z['normal_end'] and z['exact'] for z in outs);eq02=torch.equal(ms[0][j],ms[2][j]);allclean=all(z[j]['score']['joint_ok'] for p in prefixes for z in p)
       for h in range(3):rs.append(dict(seed=s,method=arm,split=split,record_id=w['record_id'],history=h,source_text=sources[h][j],current=outs[h],prefix=[z[j] for z in prefixes[h]],prefix_clean=all(z[j]['score']['joint_ok'] for z in prefixes[h]),all_prefix_clean=allclean,strict=strict,equal_mask02=eq02,mask=ms[h][j].tolist(),checkpoint_sha256=checkpoint_hashes[f'{s}/{arm}'],model_hash=e.model_hash))
      write(jp.relative_to(ROOT),rs)
     allrows+=rs;shards.append(dict(path=str(pt.relative_to(ROOT)),sha256=digest(pt),outputs=str(jp.relative_to(ROOT)),outputs_sha256=digest(jp),seed=s,method=arm,split=split))
   del ed
 write('outputs/current_states.jsonl',allrows);flags={(r['seed'],r['method'],r['record_id']):r for r in allrows if r['history']==0};common={};crossseed={}
 for split in ['iid','template_ood']:
  sets=[]
  for s in CFG['seeds']:
   sel=[w['record_id'] for w in ws if w['split']==split and all(flags[s,a,w['record_id']]['strict'] for a in ['A','B'])];common[f'{s}/{split}']=sel;sets.append(set(sel))
  crossseed[split]=sorted(set.intersection(*sets))
 dump('data/cohort_lock.json',dict(locked_before_next_and_long_chain=True,current_sha256=digest(ROOT/'outputs/current_states.jsonl'),checkpoint_hashes=checkpoint_hashes,common_AB_strict=common,cross_seed_AB_common=crossseed,cohorts=[{k:r[k] for k in ['seed','method','split','record_id','strict','equal_mask02','all_prefix_clean']} for r in allrows if r['history']==0],latent_shards=shards,job_id=os.environ['SLURM_JOB_ID']))
 print('G12 cohort lock saved',flush=True)
@torch.no_grad()
def finish(e):
 lock();co=json.loads((ROOT/'data/cohort_lock.json').read_text());assert digest(ROOT/'outputs/current_states.jsonl')==co['current_sha256'];lh=digest(ROOT/'data/cohort_lock.json');worlds=read('data/worlds.jsonl');wi={w['record_id']:w for w in worlds};nextrows=[];chains=[];atom=[]
 for sh in co['latent_shards']:
  e.check(reserve=90);s=sh['seed'];arm=sh['method'];ed=load_editor(s,arm);assert digest(checkpoint(arm,s))==co['checkpoint_hashes'][f'{s}/{arm}'];assert digest(ROOT/sh['path'])==sh['sha256'];tag=Path(sh['path']).stem;jp=ROOT/f'outputs/final_shards/{tag}.jsonl'
  if jp.exists():
   rs=read(jp);nextrows += [r for r in rs if r['kind']=='next'];chains += [r for r in rs if r['kind']=='chain'];atom += [r for r in rs if r['kind']=='atomic'];continue
  z=torch.load(ROOT/sh['path'],map_location='cuda',weights_only=True);ws=[wi[r] for r in z['record_ids']];rs=[]
  for h in range(3):
   out=decode(e,ed(z['H'][h],z['mask'][h]),z['mask'][h],ws,-2)
   for w,x in zip(ws,out):rs.append(dict(kind='next',seed=s,method=arm,split=w['split'],record_id=w['record_id'],history=h,next=x,cohort_lock_sha256=lh,checkpoint_sha256=digest(checkpoint(arm,s)),model_hash=e.model_hash))
  source=[render(w,frame(w,1)) for w in ws];h,m,enc=e.encode(source);prefix=[True]*len(ws)
  for step in range(1,6):
   h=ed(h,m);out=decode(e,h,m,ws,1-step)
   for j,(w,x) in enumerate(zip(ws,out)):
    prefix[j]=prefix[j] and x['score']['joint_ok'];rs.append(dict(kind='chain',seed=s,method=arm,split=w['split'],record_id=w['record_id'],step=step,source_text=source[j],source_frame=frame(w,1),output=x,trajectory_joint=prefix[j],mask=m[j].tolist(),cohort_lock_sha256=lh,checkpoint_sha256=digest(checkpoint(arm,s)),model_hash=e.model_hash,encode_seconds=enc/len(ws)))
  for offset in CFG['atomic_offsets']:
   legal=[w for w in ws if eligible(w,['T_plus'],offset)];texts=[render(w,frame(w,offset)) for w in legal];h,m,enc=e.encode(texts);out=decode(e,ed(h,m),m,legal,offset-1)
   for w,t,x,mm in zip(legal,texts,out,m):rs.append(dict(kind='atomic',seed=s,method=arm,split=w['split'],record_id=w['record_id'],offset=offset,source_text=t,source_frame=frame(w,offset),output=x,mask=mm.tolist(),cohort_lock_sha256=lh,checkpoint_sha256=digest(checkpoint(arm,s)),model_hash=e.model_hash))
  write(jp.relative_to(ROOT),rs);nextrows += [r for r in rs if r['kind']=='next'];chains += [r for r in rs if r['kind']=='chain'];atom += [r for r in rs if r['kind']=='atomic'];del ed,z;print('G12 evaluated',tag,flush=True)
 write('outputs/next_states.jsonl',nextrows);write('outputs/long_chains.jsonl',chains);write('outputs/atomic.jsonl',atom);dump('evaluation/inference_complete.json',dict(next_rows=len(nextrows),chain_rows=len(chains),atomic_rows=len(atom),cohort_lock_sha256=lh,job_id=os.environ['SLURM_JOB_ID']))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['current','finish']);a=p.parse_args();e=load_gpu()
 if a.phase=='current':current(e)
 else:finish(e)
