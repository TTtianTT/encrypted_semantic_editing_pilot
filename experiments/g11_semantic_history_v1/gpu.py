"""Two locked inference stages; local activation shards permit restoration."""
import argparse,os,time
import torch
from g11 import *

@torch.no_grad()
def preflight(engine):
 results=[]
 for seed in CFG['seeds']:
  ed=editor(seed);archive=read(G10/f'outputs/trajectory_rank16_seed{seed}.jsonl');old=[r for r in archive if r['split']=='composition_iid' and r['step']==1][:6]
  texts=[r['source_text'] for r in old];h,m,_=engine.encode(texts);assert h.dtype==torch.float32
  for step in range(1,4):
   before=h;h=ed(h,m);assert torch.equal(before[~m.bool()],h[~m.bool()]);out,end,_,_=engine.decode(h,m)
   targets={(r['record_id'],r['step']):r for r in archive}
   assert all(t==targets[r['record_id'],step]['output'] and bool(e)==targets[r['record_id'],step]['normal_end'] for r,t,e in zip(old,out,end))
   rev=engine.decode(h.flip(0),m.flip(0));single=engine.decode(h[:1],m[:1]);assert out==rev[0][::-1] and end==rev[1][::-1] and out[0]==single[0][0] and bool(end[0])==single[1][0]
   results.append(dict(seed=seed,step=step,N=6,archive_equal=True,reversed_batch_equal=True,single_equal=True))
  del ed
 assert all(p.grad is None and not p.requires_grad for p in engine.model.parameters())
 dump('preflight.json',dict(passed=True,checks=results,model_hash=engine.model_hash,checkpoint_hashes={str(s):digest(checkpoint(s)) for s in CFG['seeds']},normal_end_checked=True,padding_unchanged=True,parameter_updates=0,backbone_gradients_absent=True))

@torch.no_grad()
def current(engine):
 ensure_lock();preflight(engine);worlds=read('data/worlds.jsonl');plans=read('data/paths.jsonl');index={(r['record_id'],r['anchor']):r for r in plans};manifest=[];allrows=[]
 for seed in CFG['seeds']:
  ed=editor(seed)
  for split in ['iid','template_ood']:
   ws=[w for w in worlds if w['split']==split]
   for d in CFG['anchors']:
    legal=[w for w in ws if index[w['record_id'],d]['legal']]
    for start in range(0,len(legal),CFG['batch_size']):
     engine.check(reserve=90);batch=legal[start:start+CFG['batch_size']];tag=f's{seed}_{split}_a{d}_b{start:03d}';pt=ROOT/f'latents/{tag}.pt';jp=ROOT/f'outputs/current_shards/{tag}.jsonl'
     if pt.exists() and jp.exists():
      rows=read(jp)
     else:
      states=[];masks=[];ids=[];histories=[]
      for history in range(3):
       source=[render(w,frame(w,d+history)) for w in batch];h,m,enc=engine.encode(source);tokenids=engine.batch(source).input_ids
       stage=decode(engine,h,m,batch,[frame(w,d+history) for w in batch],source);prefix=[[] for _ in batch]
       if history==0:prefix=[[x] for x in stage]
       for k in range(history):
        h=ed(h,m);c=[frame(w,d+history-k-1) for w in batch];out=decode(engine,h,m,batch,c,[render(w,f) for w,f in zip(batch,c)])
        for i,x in enumerate(out):prefix[i].append(x)
       states.append(h.cpu());masks.append(m.cpu());ids.append(tokenids.cpu());histories.append(dict(source=source,source_reconstruction=stage,prefix=prefix,encode_seconds=enc/len(batch)))
      payload=dict(H=torch.stack(states),mask=torch.stack(masks),input_ids=torch.stack(ids),record_ids=[w['record_id'] for w in batch],seed=seed,anchor=d,split=split)
      pt.parent.mkdir(parents=True,exist_ok=True);tmp=pt.with_suffix('.tmp');torch.save(payload,tmp);tmp.replace(pt)
      rows=[]
      for j,w in enumerate(batch):
       cs=[histories[k]['prefix'][j][-1] for k in range(3)];strict=all(x['normal_end'] and x['exact'] for x in cs);semantic=all(x['score']['joint_ok'] for x in cs);clean=[all(x['score']['joint_ok'] for x in histories[k]['prefix'][j]) for k in range(3)]
       eq02=bool(torch.equal(masks[0][j],masks[2][j]));eqall=eq02 and bool(torch.equal(masks[0][j],masks[1][j]));gold=render(w,frame(w,d))
       for k in range(3):rows.append(dict(seed=seed,record_id=w['record_id'],split=split,anchor=d,history=k,legal=True,source_text=histories[k]['source'][j],source_frame=frame(w,d+k),current_frame=frame(w,d),current_gold=gold,current=cs[k],prefix=histories[k]['prefix'][j],source_reconstruction=histories[k]['source_reconstruction'][j],prefix_clean=clean[k],all_prefix_clean=all(clean),strict_cohort=strict,semantic_cohort=semantic,equal_mask_02=eq02,equal_mask_all=eqall,mask=masks[k][j].tolist(),input_token_ids=ids[k][j].tolist(),H_sha256=tensorhash(states[k][j]),mask_sha256=tensorhash(masks[k][j]),latent_shard=pt.relative_to(ROOT).as_posix(),latent_index=j,checkpoint_hash=digest(checkpoint(seed)),model_hash=engine.model_hash,encode_seconds=histories[k]['encode_seconds']))
      write(jp.relative_to(ROOT),rows)
     allrows+=rows;manifest.append(dict(path=pt.relative_to(ROOT).as_posix(),sha256=digest(pt),outputs=jp.relative_to(ROOT).as_posix(),outputs_sha256=digest(jp),seed=seed,anchor=d,split=split));print('current',tag,flush=True)
  del ed
 write('outputs/current_states.jsonl',allrows)
 cohorts=[{k:r[k] for k in ['seed','record_id','split','anchor','strict_cohort','semantic_cohort','all_prefix_clean','equal_mask_02','equal_mask_all']} for r in allrows if r['history']==0]
 common={}
 for split in ['iid','template_ood']:
  for d in CFG['anchors']:
   sets=[{r['record_id'] for r in cohorts if r['seed']==s and r['split']==split and r['anchor']==d and r['strict_cohort']} for s in CFG['seeds']];common[f'{split}/{d}']=sorted(set.intersection(*sets))
 dump('data/cohort_lock.json',dict(locked_before_next=True,current_outputs_sha256=digest(ROOT/'outputs/current_states.jsonl'),worlds_sha256=digest(ROOT/'data/worlds.jsonl'),cohorts=cohorts,common_strict_worlds=common,latent_shards=manifest,checkpoint_hashes={str(s):digest(checkpoint(s)) for s in CFG['seeds']},job_id=os.environ['SLURM_JOB_ID']));print('current cohort locked',len(cohorts),flush=True)

@torch.no_grad()
def next_states(engine):
 ensure_lock();lock=json.loads((ROOT/'data/cohort_lock.json').read_text());assert lock['locked_before_next'];assert digest(ROOT/'outputs/current_states.jsonl')==lock['current_outputs_sha256'];lockhash=digest(ROOT/'data/cohort_lock.json')
 worlds={w['record_id']:w for w in read('data/worlds.jsonl')};currents={(r['seed'],r['record_id'],r['anchor'],r['history']):r for r in read('outputs/current_states.jsonl')};nextrows=[];crossrows=[];algebra=[];batch_checks=[]
 for shard in lock['latent_shards']:
  engine.check(reserve=90);assert digest(ROOT/shard['path'])==shard['sha256'];tag=Path(shard['path']).stem;jp=ROOT/f'outputs/next_shards/{tag}.jsonl';cp=ROOT/f'outputs/cross_shards/{tag}.jsonl';ap=ROOT/f'outputs/algebra_shards/{tag}.json'
  if jp.exists() and cp.exists() and ap.exists():
   nextrows+=read(jp);crossrows+=read(cp);algebra+=json.loads(ap.read_text())['checks'];continue
  payload=torch.load(ROOT/shard['path'],weights_only=True,map_location='cuda');H=payload['H'];m=payload['mask'];seed=payload['seed'];d=payload['anchor'];ed=editor(seed);batch=[worlds[r] for r in payload['record_ids']];frames=[frame(w,d-1) for w in batch];golds=[render(w,f) for w,f in zip(batch,frames)];rows=[];cross=[];checks=[];usual=[]
  for k in range(3):
   hn=ed(H[k],m[k]);out=decode(engine,hn,m[k],batch,frames,golds);usual.append(out)
   for j,(w,x) in enumerate(zip(batch,out)):
    c=currents[seed,w['record_id'],d,k];rows.append(dict(seed=seed,split=w['split'],record_id=w['record_id'],anchor=d,history=k,next=x,full_history_joint=c['prefix_clean'] and x['score']['joint_ok'],strict_cohort=c['strict_cohort'],semantic_cohort=c['semantic_cohort'],all_prefix_clean=c['all_prefix_clean'],equal_mask_02=c['equal_mask_02'],equal_mask_all=c['equal_mask_all'],checkpoint_hash=c['checkpoint_hash'],model_hash=engine.model_hash,cohort_lock_sha256=lockhash,mask=c['mask'],current_output=c['current']['output'],current_gold=c['current_gold'],next_target=golds[j]))
  ix=[j for j,w in enumerate(batch) if d==-1 and currents[seed,w['record_id'],d,0]['strict_cohort'] and currents[seed,w['record_id'],d,0]['equal_mask_02']]
  if ix:
   hc,he,mm=H[0,ix],H[2,ix],m[0,ix];rc=ed(hc,mm)-hc;re=ed(he,mm)-he;pred=ed.u(ed.v(he-hc))*mm[...,None];err=((re-rc)-pred)[mm.bool()];absmax=float(err.abs().max());rel=float(err.norm()/(pred[mm.bool()].norm()+1e-12));assert absmax<1e-5 and rel<1e-4,(absmax,rel)
   checks.append(dict(shard=tag,N=len(ix),identity_max_abs_error=absmax,identity_relative_l2_error=rel,padding_unchanged=bool(torch.equal(rc[~mm.bool()],torch.zeros_like(rc[~mm.bool()])))))
   conditions={'cc':hc+rc,'ee':he+re,'ec':he+rc,'ce':hc+re};bw=[batch[j] for j in ix];bf=[frames[j] for j in ix];bg=[golds[j] for j in ix]
   for condition,z in conditions.items():
    out=decode(engine,z,mm,bw,bf,bg)
    if not any(x.get('seed')==seed for x in batch_checks):
     rev=decode(engine,z.flip(0),mm.flip(0),bw[::-1],bf[::-1],bg[::-1]);solo=decode(engine,z[:1],mm[:1],bw[:1],bf[:1],bg[:1]);assert [x['output'] for x in out]==[x['output'] for x in rev][::-1] and out[0]['output']==solo[0]['output'] and out[0]['normal_end']==solo[0]['normal_end']
    for j,(w,x) in enumerate(zip(bw,out)):
     actual=usual[0 if condition=='cc' else 2][ix[j]] if condition in ['cc','ee'] else None
     cross.append(dict(seed=seed,split=w['split'],record_id=w['record_id'],anchor=d,condition=condition,output=x,mask=mm[j].tolist(),target_text=bg[j],cohort_lock_sha256=lockhash,checkpoint_hash=digest(checkpoint(seed)),model_hash=engine.model_hash,standard_next_output_equal=None if actual is None else x['output']==actual['output'],source_input_ids_canonical=payload['input_ids'][0,ix[j]].tolist(),source_input_ids_edited=payload['input_ids'][2,ix[j]].tolist()))
   if not any(x.get('seed')==seed for x in batch_checks):batch_checks.append(dict(seed=seed,shard=tag,N=len(ix),all_four_conditions_reversed_and_single_equal=True))
  write(jp.relative_to(ROOT),rows);write(cp.relative_to(ROOT),cross);dump(ap.relative_to(ROOT),dict(checks=checks));nextrows+=rows;crossrows+=cross;algebra+=checks;del ed,payload,H,m;print('next',tag,len(cross),'cross outputs',flush=True)
 write('outputs/next_states.jsonl',nextrows);write('outputs/crossover.jsonl',crossrows);dump('intervention_checks.json',dict(algebra=algebra,batch_checks=batch_checks,parameter_updates=0,cohort_lock_sha256=lockhash));assert all(p.grad is None for p in engine.model.parameters());print('next complete',len(nextrows),len(crossrows),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['current','next']);args=p.parse_args();eng=load_gpu()
 with torch.no_grad():
  if args.phase=='current':current(eng)
  else:next_states(eng)
