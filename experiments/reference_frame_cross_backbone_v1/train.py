import argparse,time,signal,copy,torch
from common import *
from backend import Backend,new_editors,tensorhash
STOP=False
def stop(*args):
 global STOP;STOP=True
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGUSR1,stop)
def main(name,group):
 admission=json.loads((ROOT/f'calibration/{name}/admission.json').read_text());assert admission['passed'];assert json.loads((ROOT/f'checkpoints/{name}/budget_gate.json').read_text())['run_training']
 for f,h in json.loads((ROOT/'data/lock.json').read_text())['files'].items():assert digest(ROOT/'data'/f)==h
 be=Backend(name);eds=new_editors(be.d);eds.load_state_dict(torch.load(ROOT/f'checkpoints/{name}/initial.pt',weights_only=True));ih=tensorhash(eds.state_dict());assert ih==json.loads((ROOT/f'checkpoints/{name}/initial.json').read_text())['tensor_hash']
 cfg=json.loads((ROOT/'config.json').read_text());opt=torch.optim.AdamW(eds.parameters(),lr=cfg['lr'],weight_decay=cfg['weight_decay']);micro=be.cfg['micro_batch'];d=ROOT/f'checkpoints/{name}/{group}';d.mkdir(parents=True,exist_ok=True)
 if (d/'complete.json').exists():print('already complete');return
 train=read('data/train_G1.jsonl');dev=read('data/dev_atomic.jsonl');schedule=read('data/sample_schedule.jsonl');worlds={w['record_id']:w for w in read('data/train_worlds.jsonl')}
 step=initial=0;best=float('inf');beststep=0;history=[];counts={op:dict(updates=0,samples=0,weight_tokens=0,supervision_tokens=0,operator_calls=0,decoder_sample_calls=0,decoder_forward_calls=0,seconds=0.) for op in OPS}
 if (d/'latest.pt').exists():
  ck=torch.load(d/'latest.pt',weights_only=False);assert ck['interface_hash']==digest(ROOT/f'models/{name}_interface.json') and ck['initialization_hash']==ih;eds.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);initial=step=ck['step'];best=ck['best'];beststep=ck['beststep'];history=ck['history'];counts=ck['counts'];torch.set_rng_state(ck['rng']);torch.cuda.set_rng_state_all(ck['cuda_rng'])
 def save():
  torch.save(dict(editor=eds.state_dict(),optimizer=opt.state_dict(),step=step,best=best,beststep=beststep,history=history,counts=counts,rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),interface_hash=digest(ROOT/f'models/{name}_interface.json'),initialization_hash=ih),d/'latest.tmp');(d/'latest.tmp').replace(d/'latest.pt')
 @torch.no_grad()
 def devloss():
  total=n=0
  for path in sorted(ATOMIC):
   rs=[r for r in dev if r['path']==path]
   for i in range(0,len(rs),micro):
    batch=rs[i:i+micro];h,mask,_=be.encode([r['source_text'] for r in batch]);h=eds[batch[0]['operations'][0]](h,mask);ce,nt=be.token_ce(h,mask,[r['target_text'] for r in batch]);total+=float((ce*nt).sum());n+=int(nt.sum())
  return total/n
 started=time.monotonic();torch.cuda.reset_peak_memory_stats()
 try:
  for b in schedule[initial:]:
   be.check(120)
   if STOP:raise TimeoutError('signal')
   rs=[train[k] for k in b['pair_indices']];flags=b['g2_replace'];terminal=[render(worlds[r['record_id']],advance(r['frames'][-1],'T_plus')) if group=='G3' and f else r['target_text'] for r,f in zip(rs,flags)];den=sum(map(len,be.label_ids(terminal)));op=rs[0]['operations'][0];assert all(r['operations']==[op] for r in rs)
   opt.zero_grad(set_to_none=True);t=time.monotonic();c=counts[op];batch_loss=0.
   for i in range(0,16,micro):
    loss,stats=be.objective(eds,rs[i:i+micro],flags[i:i+micro],worlds,group,den);assert torch.isfinite(loss);batch_loss+=float(loss.detach());loss.backward()
    for k,v in stats.items():c[k]+=v
   assert all(p.grad is None for p in be.model.parameters());grad_norm=float(torch.nn.utils.clip_grad_norm_(eds.parameters(),1.));opt.step();torch.cuda.synchronize();c['updates']+=1;c['samples']+=16;c['seconds']+=time.monotonic()-t;step=b['step']
   with (d/'training_log.jsonl').open('a') as f:f.write(json.dumps(dict(step=step,operation=op,weighted_loss=batch_loss,gradient_norm_before_clip=grad_norm,chain_occurrences=sum(flags) if group=='G3' else 0))+'\n')
   if step==12:dump(f'checkpoints/{name}/{group}/short_window.json',dict(seconds_per_update=(time.monotonic()-started)/12,remaining_training_estimate=(time.monotonic()-started)/12*588))
   if step%100==0:
    nll=devloss();history.append(dict(step=step,dev_target_token_nll=nll));torch.save(eds.state_dict(),d/f'step{step}.pt')
    if nll<best:best=nll;beststep=step;torch.save(eds.state_dict(),d/'best.pt')
    save();print(name,group,step,nll,flush=True)
 except TimeoutError:
  save();dump(f'checkpoints/{name}/{group}/incomplete.json',dict(step=step,reason='budget or signal'));return
 assert step==600
 dump(f'checkpoints/{name}/{group}/complete.json',dict(model=name,group=group,seed=42,step=step,beststep=beststep,best_dev_nll=best,history=history,counts=counts,initialization_hash=ih,checkpoint_hash=digest(d/'best.pt'),wall_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated(),micro_batch=micro,effective_batch=16))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('group',choices=['G1','G3']);a=p.parse_args();main(a.model,a.group)
