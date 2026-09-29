import copy,time,signal,torch
from common import *
from engine import Engine,new_editors,tensorhash
from evaluation import Evaluator
from validate import validate
STOP=False
def stop(*args):
 global STOP;STOP=True
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGUSR1,stop)

def main():
 lock=json.loads((ROOT/'data/lock.json').read_text())
 for f,h in lock['files'].items():assert digest(ROOT/'data'/f)==h
 assert digest(ROOT/'config.json')==lock['config'] and digest(ROOT/'PROTOCOL.md')==lock['protocol']
 eng=Engine();validate(eng)
 eds=new_editors();eds.load_state_dict(torch.load(ROOT/'checkpoints/initial.pt',weights_only=True));ih=tensorhash(eds.state_dict());assert ih==json.loads((ROOT/'checkpoints/initial.json').read_text())['tensor_hash']
 opt=torch.optim.AdamW(eds.parameters(),lr=eng.cfg['lr'],weight_decay=0)
 train=read('data/train_G1.jsonl');dev=read('data/dev_atomic.jsonl');chain=[r for r in read('data/dev_chains.jsonl') if r['path']=='plus_plus'];schedule=read('data/sample_schedule.jsonl');worlds={w['record_id']:w for w in read('data/train_worlds.jsonl')};ev=Evaluator(eng)
 d=ROOT/'checkpoints/G3';latest=d/'latest.pt';history=[];best=float('inf');beststep=initial=step=replacements=0
 counts={op:dict(optimizer_updates=0,samples=0,supervision_tokens=0,endpoint_weight_tokens=0,input_tokens=0,operator_sample_calls=0,decoder_batch_calls=0,decoder_sample_calls=0,seconds=0.) for op in OPS}
 if (d/'complete.json').exists():print('already complete');return
 if latest.exists():
  ck=torch.load(latest,weights_only=False);assert ck['config_hash']==digest(ROOT/'config.json');eds.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);initial=step=ck['step'];best=ck['best'];beststep=ck['beststep'];history=ck['history'];counts=ck['counts'];replacements=ck['replacements'];torch.set_rng_state(ck['rng']);torch.cuda.set_rng_state_all(ck['cuda_rng'])
 def save():
  torch.save(dict(editor=eds.state_dict(),optimizer=opt.state_dict(),step=step,best=best,beststep=beststep,history=history,counts=counts,replacements=replacements,rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),config_hash=digest(ROOT/'config.json'),initialization_hash=ih),d/'latest.tmp');(d/'latest.tmp').replace(latest)
 @torch.no_grad()
 def devloss():
  total=n=0
  for path in sorted(ATOMIC):
   rows=[r for r in dev if r['path']==path]
   for i in range(0,len(rows),16):l,nt,_=eng.loss(eds,rows[i:i+16]);total+=l.item()*nt;n+=nt
  return total/n
 torch.cuda.reset_peak_memory_stats();started=time.monotonic()
 try:
  for b in schedule[initial:]:
   eng.check(120)
   if STOP:raise TimeoutError('signal')
   rows=[copy.deepcopy(train[k]) for k in b['pair_indices']];flags=b['g2_replace'];op=rows[0]['operations'][0]
   opt.zero_grad(set_to_none=True);torch.cuda.synchronize();t=time.perf_counter();loss,stats=eng.stage_loss(eds,rows,flags,worlds);assert torch.isfinite(loss);loss.backward();assert all(p.grad is None for p in eng.model.parameters());torch.nn.utils.clip_grad_norm_(eds.parameters(),1.);opt.step();torch.cuda.synchronize()
   step=b['step'];c=counts[op];c['optimizer_updates']+=1;c['samples']+=16;c['seconds']+=time.perf_counter()-t
   for k,v in stats.items():c[k]+=v
   replacements+=sum(flags)
   if step==12:dump('checkpoints/G3/short_window.json',{'seconds_per_update':(time.monotonic()-started)/12,'remaining_train_estimate_seconds':(time.monotonic()-started)/12*588})
   if step%100==0:
    nll=devloss()
    if nll<best:best=nll;beststep=step;torch.save(eds.state_dict(),d/'best.pt')
    p=f'evaluation/dev/step{step}.jsonl';hh=tensorhash(eds.state_dict());a=ev.neural([r for r in dev if r['operations']==['T_plus']],eds,'G3',p,editor_hash=hh);out=ev.neural(chain,eds,'G3',p,editor_hash=hh);ch=[r for r in out if r['path']=='plus_plus']
    history.append(dict(step=step,dev_target_token_nll=nll,T_plus_joint=sum(r['score']['joint_ok'] for r in a)/len(a),plus_plus_endpoint=sum(r['score']['joint_ok'] for r in ch)/len(ch),plus_plus_trajectory=sum(all(s['score']['joint_ok'] for s in r['steps']) for r in ch)/len(ch)))
    save();print('CHECKPOINT',history[-1],flush=True)
 except TimeoutError:
  save();print('STOPPED with resumable checkpoint',step,flush=True);return
 assert step==600 and replacements==1600
 dump('checkpoints/G3/complete.json',dict(group='G3',seed=42,steps=step,beststep=beststep,best_dev_token_nll=best,initialization_hash=ih,editor_hash=digest(d/'best.pt'),counts=counts,replaced_occurrences=replacements,history=history,wall_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated()))
 print('TRAIN COMPLETE',flush=True)
if __name__=='__main__':main()
