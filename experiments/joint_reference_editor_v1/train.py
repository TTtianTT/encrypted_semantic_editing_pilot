import signal,time
from engine import *
STOP=False
def stop(*args):
 global STOP;STOP=True
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGUSR1,stop)
def main(rank):
 assert_lock();assert json.loads((ROOT/'calibration/interface_check.json').read_text())['passed'];be=Backend(NAME);ed=new_joint(be.d,rank);ed.load_state_dict(torch.load(ROOT/f'checkpoints/initial_rank{rank}.pt',weights_only=True));ih=tensorhash(ed.state_dict());d=ROOT/f'checkpoints/Joint{rank}';d.mkdir(exist_ok=True)
 if (d/'complete.json').exists():return
 opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0);train=read('data/train_joint.jsonl');dev=read('data/dev_joint.jsonl');schedule=read('data/sample_schedule.jsonl');step=0;best=float('inf');beststep=0;hist=[];tokens=0;seconds=0.
 if (d/'latest.pt').exists():
  c=torch.load(d/'latest.pt',weights_only=False);ed.load_state_dict(c['editor']);opt.load_state_dict(c['optimizer']);step=c['step'];best=c['best'];beststep=c['beststep'];hist=c['history'];tokens=c['tokens'];seconds=c['train_seconds'];torch.set_rng_state(c['rng']);torch.cuda.set_rng_state_all(c['cuda_rng'])
 def save():
  torch.save(dict(editor=ed.state_dict(),optimizer=opt.state_dict(),step=step,best=best,beststep=beststep,history=hist,tokens=tokens,train_seconds=seconds,rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),d/'latest.tmp');(d/'latest.tmp').replace(d/'latest.pt')
 started=time.monotonic();torch.cuda.reset_peak_memory_stats()
 try:
  for b in schedule[step:]:
   be.check(120)
   if STOP:raise TimeoutError('signal')
   rr=[train[k] for k in b['pair_indices']];den=sum(map(len,be.label_ids([r['target_text'] for r in rr])));opt.zero_grad(set_to_none=True);lossvalue=0.;t=time.monotonic()
   for i in range(0,16,4):
    r=rr[i:i+4];h,m,_=be.encode([x['source_text'] for x in r]);ell,n=be.token_ce(ed(h,m),m,[x['target_text'] for x in r]);loss=(ell*n).sum()/den;assert torch.isfinite(loss);lossvalue+=float(loss.detach());loss.backward()
   assert all(p.grad is None for p in be.model.parameters());grad=float(torch.nn.utils.clip_grad_norm_(ed.parameters(),1.));opt.step();torch.cuda.synchronize();seconds+=time.monotonic()-t;step=b['step'];tokens+=den
   with (d/'training_log.jsonl').open('a') as f:f.write(json.dumps(dict(step=step,loss=lossvalue,gradient_norm_before_clip=grad,target_tokens=den))+'\n')
   if step%100==0:
    nll=devloss(be,ed,dev);hist.append(dict(step=step,dev_target_token_nll=nll));torch.save(ed.state_dict(),d/f'step{step}.pt')
    if nll<best:best=nll;beststep=step;torch.save(ed.state_dict(),d/'best.pt')
    save();print('Joint',rank,step,nll,flush=True)
 except TimeoutError:
  save();dump(f'checkpoints/Joint{rank}/incomplete.json',dict(step=step,reason='budget or signal'));return
 assert step==600
 dump(f'checkpoints/Joint{rank}/complete.json',dict(rank=rank,seed=42,updates=step,beststep=beststep,best_dev_nll=best,history=hist,parameters=sum(p.numel() for p in ed.parameters()),supervision_tokens=tokens,supervised_samples=9600,operator_sample_calls=9600,decoder_forward_batches=2400,train_seconds=seconds,wall_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated(),initial_tensor_hash=ih,checkpoint_hash=digest(d/'best.pt'),effective_batch=16,micro_batch=4))
if __name__=='__main__':
 import sys;main(int(sys.argv[1]))
