import argparse,json,time,signal,os,copy
import torch
from common import *
from engine import Engine,new_editors,tensorhash
from evaluation import Evaluator
STOP=False
def stop(*args):
 global STOP;STOP=True
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGUSR1,stop)
def main(group):
 assert json.loads((ROOT/'calibration/gate.json').read_text())['passed']
 lock=json.loads((ROOT/'data/test_lock.json').read_text())
 for file,h in lock['files'].items():assert digest(ROOT/'data'/file)==h
 if group=='G2':assert json.loads((ROOT/'evaluation/c_gate.json').read_text())['run_G2']
 d=ROOT/f'checkpoints/{group}';d.mkdir(exist_ok=True)
 if (d/'complete.json').exists() and (group!='G1' or (ROOT/'evaluation/c_gate.json').exists()):print('existing complete',group);return
 eng=Engine();eds=new_editors();eds.load_state_dict(torch.load(ROOT/'checkpoints/initial.pt',weights_only=True));ih=tensorhash(eds.state_dict());assert ih==json.loads((ROOT/'checkpoints/initial.json').read_text())['tensor_hash']
 opt=torch.optim.AdamW(eds.parameters(),lr=eng.cfg['lr'],weight_decay=0)
 train=read('data/train_G0.jsonl' if group=='G0' else 'data/train_G1.jsonl');dev=read('data/dev_atomic.jsonl');schedule=read('data/sample_schedule.jsonl');worlds={w['record_id']:w for w in read('data/train_worlds.jsonl')}
 history=[];best=float('inf');beststep=0;initial=0;counts={op:dict(optimizer_updates=0,samples=0,supervision_tokens=0,input_tokens=0,operator_sample_calls=0,seconds=0.) for op in OPS};replacements=0
 latest=d/'latest.pt'
 if latest.exists():
  ck=torch.load(latest,weights_only=False);assert ck['config_hash']==digest(ROOT/'config.json');eds.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);initial=ck['step'];best=ck['best'];beststep=ck['beststep'];history=ck['history'];counts=ck['counts'];replacements=ck['replacements'];torch.set_rng_state(ck['rng']);torch.cuda.set_rng_state_all(ck['cuda_rng'])
 def save(step):
  state={'group':group,'editor':eds.state_dict(),'optimizer':opt.state_dict(),'step':step,'best':best,'beststep':beststep,'history':history,'counts':counts,'replacements':replacements,'rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),'config_hash':digest(ROOT/'config.json'),'initialization_hash':ih};torch.save(state,d/'latest.tmp');(d/'latest.tmp').replace(latest)
 @torch.no_grad()
 def devloss():
  total=n=0
  for path in sorted(ATOMIC):
   rs=[r for r in dev if r['path']==path]
   for i in range(0,len(rs),16):l,nt,_=eng.loss(eds,rs[i:i+16]);total+=l.item()*nt;n+=nt
  return total/n
 start=time.monotonic();step=initial
 try:
  for b in schedule[initial:]:
   eng.check(120)
   if STOP:raise TimeoutError('signal stop')
   rs=[copy.deepcopy(train[k]) for k in b['pair_indices']];replace=b['g2_replace'] if group=='G2' else [False]*16;op=rs[0]['operations'][0]
   for row,flag in zip(rs,replace):
    if flag:
     final=advance(row['frames'][-1],'T_plus');row['target_text']=render(worlds[row['record_id']],final)
   opt.zero_grad(set_to_none=True);torch.cuda.synchronize();t=time.perf_counter();l,nt,nx=eng.loss(eds,rs,replace);assert torch.isfinite(l);l.backward();assert all(p.grad is None for p in eng.model.parameters());assert eds[op].b.grad is not None
   torch.nn.utils.clip_grad_norm_(eds.parameters(),1.);opt.step();torch.cuda.synchronize();elapsed=time.perf_counter()-t;step=b['step']
   c=counts[op];c['optimizer_updates']+=1;c['samples']+=16;c['supervision_tokens']+=nt;c['input_tokens']+=nx;c['operator_sample_calls']+=16+sum(replace);c['seconds']+=elapsed;replacements+=sum(replace)
   if step==12:dump(f'checkpoints/{group}/short_window.json',{'seconds_per_update':(time.monotonic()-start)/12,'remaining_train_estimate_seconds':(time.monotonic()-start)/12*(600-step)})
   if step%100==0:
    value=devloss();history.append(dict(step=step,dev_target_token_nll=value));print(group,step,value,flush=True)
    if value<best:best=value;beststep=step;torch.save(eds.state_dict(),d/'best.pt')
    save(step)
 except TimeoutError:
  save(step);print('Stopped with resumable checkpoint',step,flush=True);return
 assert step==600 and replacements==(1600 if group=='G2' else 0)
 eds.load_state_dict(torch.load(d/'best.pt',weights_only=True));eh=digest(d/'best.pt');evaluator=Evaluator(eng);devout=evaluator.neural(dev,eds,group,f'evaluation/dev/{group}_atomic.jsonl',editor_hash=eh)
 dump(f'checkpoints/{group}/complete.json',{'group':group,'seed':42,'steps':step,'beststep':beststep,'best_dev_token_nll':best,'initialization_hash':ih,'editor_hash':eh,'counts':counts,'replaced_occurrences':replacements,'history':history,'wall_seconds':time.monotonic()-start,'peak_cuda_bytes':torch.cuda.max_memory_allocated(),'dev_joint':sum(r['score']['joint_ok'] for r in devout)/len(devout)})
 if group=='G1':
  chains=[r for r in read('data/dev_chains.jsonl') if r['path'] in TIME2]
  rr=[]
  for mode in ['latent_chain','decode_reencode']:rr=evaluator.neural(chains,eds,group,'evaluation/dev/G1_gate_chains.jsonl',mode,eh)
  temporal=[r for r in devout if r['operations'][0].startswith('T')];single=sum(r['score']['joint_ok'] for r in temporal)/len(temporal);rates={}
  for path in TIME2:
   sub=[r for r in rr if r['path']==path and r['mode']=='decode_reencode'];assert len(sub)==80;rates[path]=sum(r['score']['joint_ok'] for r in sub)/len(sub)
  sub=[r for r in rr if r['path']=='plus_plus' and r['mode']=='latent_chain'];latent=sum(r['score']['joint_ok'] for r in sub)/len(sub)
  run=single>=.95 and min(rates.values())>=.95 and latent<.90
  dump('evaluation/c_gate.json',{'atomic_time_joint':single,'two_step_reencode':rates,'plus_plus_latent':latent,'run_G2':run,'test_outputs_accessed':False,'thresholds':eng.cfg['c_gate']});print('C_GATE',run,single,rates,latent,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('group',choices=['G0','G1','G2']);a=p.parse_args();main(a.group)
