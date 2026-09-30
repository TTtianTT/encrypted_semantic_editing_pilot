"""Same targets and three equal-weight losses; only third-call input differs."""
import argparse,random
import torch
from transformers.modeling_outputs import BaseModelOutput
from common_g12 import *
def seed_all(s):random.seed(s);torch.manual_seed(s);torch.cuda.manual_seed_all(s)
def objective(e,ed,rows,arm,parts=False):
 texts=list(zip(*[r['texts'] for r in rows]));h0,m,_=e.encode(texts[0]);hc,mc,_=e.encode(texts[2]);assert torch.equal(m,mc)
 h1=ed(h0,m);h2=ed(h1,m);h3=ed(hc if arm=='A' else h2.detach(),m)
 losses=[];tokens=[]
 for h,t in zip([h1,h2,h3],texts[1:]):
  y=e.tok(list(t),padding=True,truncation=False,return_tensors='pt').input_ids.cuda();y[y==e.tok.pad_token_id]=-100
  losses.append(e.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=y,use_cache=False).loss);tokens.append(int((y!=-100).sum()))
 l=sum(losses)/3;stats=dict(supervision_tokens=sum(tokens),stage_tokens=tokens,encoder_sample_calls=2*len(rows),operator_sample_calls=3*len(rows),decoder_sample_calls=3*len(rows),encoder_batch_calls=2,operator_batch_calls=3,decoder_batch_calls=3)
 if parts:return l,stats,(h0,h1,h2,h3,m,losses)
 return l,stats
def smoke(e):
 lock();rows=read('data/train_paths.jsonl');ids=read('data/sample_schedule.jsonl')[0]['indices'];batch=[rows[i] for i in ids];checks=[];counts=[];basehash=statehash(e.model.state_dict())
 for arm in ['A','B']:
  seed_all(42);ed=load_editor(42,train=True);l,st,(h0,h1,h2,h3,m,ls)=objective(e,ed,batch,arm,True)
  h1.retain_grad();h2.retain_grad();h3.retain_grad()
  third_prefix=torch.autograd.grad(ls[2],h2,retain_graph=True,allow_unused=True)[0];assert third_prefix is None
  third_grads=torch.autograd.grad(ls[2],list(ed.parameters()),retain_graph=True);assert all(torch.isfinite(g).all() for g in third_grads) and sum(float(g.norm()) for g in third_grads)>0
  l.backward();assert all(p.grad is None for p in e.model.parameters());assert all(torch.isfinite(p.grad).all() for p in ed.parameters())
  assert all(h.grad is not None and torch.isfinite(h.grad).all() and float(h.grad.norm())>0 for h in [h1,h2,h3])
  assert torch.equal(h0[~m.bool()],h1[~m.bool()]) and torch.equal(h1[~m.bool()],h2[~m.bool()])
  checks.append(dict(arm=arm,loss=float(l.detach()),third_to_h2_gradient_absent=True,third_editor_gradient_norms=[float(g.norm()) for g in third_grads],stage_H_gradient_norms=[float(h.grad.norm()) for h in [h1,h2,h3]],backbone_gradients_absent=True,padding_unchanged=True,mask_equal=True));counts.append(st);del ed
 assert counts[0]==counts[1];assert statehash(e.model.state_dict())==basehash
 # Only historical G10 samples, never new confirmation data, for output preflight.
 archive=read(G10/'outputs/trajectory_rank16_seed42.jsonl');old=[r for r in archive if r['split']=='composition_iid' and r['step']==1][:6];ed=load_editor(42);h,m,_=e.encode([r['source_text'] for r in old]);h=ed(h,m)
 a=e.decode(h,m);b=e.decode(h.flip(0),m.flip(0));assert a[0]==[r['output'] for r in old] and a[0]==b[0][::-1]
 dump('smoke_test.json',dict(passed=True,checks=checks,supervision_and_calls=counts,backbone_hash_unchanged=True,backbone_state_hash=basehash,old_archive_reproduced=True,reversed_batch_equal=True,initial_hashes={str(s):digest(original(s)) for s in CFG['seeds']},model_hash=e.model_hash,job_id=os.environ['SLURM_JOB_ID']))
 print('G12 gradient and historical preflight passed',flush=True)
def train(e,s):
 lock();assert json.loads((ROOT/'smoke_test.json').read_text())['passed'];rows=read('data/train_paths.jsonl');dev=read('data/dev_paths.jsonl');schedule=read('data/sample_schedule.jsonl');basehash=statehash(e.model.state_dict())
 for arm in ['A','B']:
  target=checkpoint(arm,s);meta=ROOT/f'training/{arm}_seed{s}.json'
  if target.exists() and meta.exists():assert digest(target)==json.loads(meta.read_text())['checkpoint_sha256'];continue
  seed_all(s);ed=load_editor(s,train=True);initial=statehash(ed.state_dict());opt=torch.optim.AdamW(ed.parameters(),lr=CFG['learning_rate'],weight_decay=0)
  resume=ROOT/f'local/resume_{arm}_seed{s}.pt';completed=0;curve=[];counts={k:0 for k in ['supervision_tokens','encoder_sample_calls','operator_sample_calls','decoder_sample_calls','encoder_batch_calls','operator_batch_calls','decoder_batch_calls']};stage_counts=[0,0,0];diagnostics=[]
  if resume.exists():
   z=torch.load(resume,map_location='cpu',weights_only=False);assert z['initial_hash']==initial;ed.load_state_dict(z['editor']);opt.load_state_dict(z['optimizer']);completed=z['completed'];curve=z['curve'];counts=z['counts'];stage_counts=z['stage_counts'];diagnostics=z['diagnostics'];torch.set_rng_state(z['cpu_rng']);torch.cuda.set_rng_state_all(z['cuda_rng']);random.setstate(z['python_rng'])
  def save():
   resume.parent.mkdir(parents=True,exist_ok=True);tmp=resume.with_suffix('.tmp');torch.save(dict(editor=ed.state_dict(),optimizer=opt.state_dict(),completed=completed,initial_hash=initial,curve=curve,counts=counts,stage_counts=stage_counts,diagnostics=diagnostics,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),python_rng=random.getstate()),tmp);tmp.replace(resume)
  started=time.monotonic();torch.cuda.reset_peak_memory_stats()
  try:
   for b in schedule[completed:]:
    e.check(reserve=150);batch=[rows[i] for i in b['indices']];opt.zero_grad(set_to_none=True);l,st=objective(e,ed,batch,arm);assert torch.isfinite(l);l.backward();assert all(p.grad is None for p in e.model.parameters());torch.nn.utils.clip_grad_norm_(ed.parameters(),CFG['gradient_clip']);opt.step();completed=b['update']
    for k in counts:counts[k]+=st[k]
    stage_counts=[a+b for a,b in zip(stage_counts,st['stage_tokens'])];curve.append(dict(update=completed,loss=float(l.detach()),stage_tokens=st['stage_tokens'],elapsed_seconds=time.monotonic()-started))
    if completed%50==0:
     with torch.no_grad():
      ds=[]
      for i in range(0,len(dev),16):dl,dst=objective(e,ed,dev[i:i+16],arm);ds.append(dict(loss=float(dl),N=len(dev[i:i+16]),counts=dst))
     diagnostics.append(dict(update=completed,dev_fixed_stage_loss=sum(r['loss']*r['N'] for r in ds)/sum(r['N'] for r in ds),batches=ds,used_for_selection=False));save();print('trained',arm,s,completed,float(l.detach()),flush=True)
  finally:save()
  assert completed==200 and statehash(e.model.state_dict())==basehash
  target.parent.mkdir(parents=True,exist_ok=True);torch.save({k:v.detach().cpu() for k,v in ed.state_dict().items()},target)
  dump(f'training/{arm}_seed{s}.json',dict(arm=arm,seed=s,updates=completed,initial_state_hash=initial,initial_checkpoint_sha256=digest(original(s)),checkpoint_sha256=digest(target),parameters=sum(p.numel() for p in ed.parameters()),counts=counts,stage_token_counts=stage_counts,curve=curve,dev_diagnostics=diagnostics,training_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated(),backbone_unchanged=True,backbone_state_hash=basehash,job_id=os.environ['SLURM_JOB_ID'],schedule_sha256=digest(ROOT/'data/sample_schedule.jsonl'),final_checkpoint_no_selection=True))
  del ed,opt;torch.cuda.empty_cache()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed-index',type=int);p.add_argument('--preflight',action='store_true');a=p.parse_args();e=load_gpu()
 if a.preflight:smoke(e)
 else:train(e,CFG['seeds'][a.seed_index])
