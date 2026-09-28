"""Gate-protected atomic training; no test reads. One method/seed per Slurm job."""
import argparse,json,time,random,signal,os
from pathlib import Path
import torch
from torch import nn
from transformers.modeling_outputs import BaseModelOutput
from e0 import Runner,Editor
from prepare import ROOT,dump,digest
from semantics import select_operation,score
STOP=False
def handle_signal(*args):
 global STOP;STOP=True
signal.signal(signal.SIGTERM,handle_signal);signal.signal(signal.SIGUSR1,handle_signal)
OPS=['T_plus','T_minus','P_13','P_31']
def load(name):return [json.loads(l) for l in (ROOT/'data'/name).read_text().splitlines()]
def run(method,seed):
 gate=json.loads((ROOT/'calibration/gate.json').read_text());assert gate['passed'],'E0 failed; training prohibited'
 if seed!=42:assert json.loads((ROOT/'evaluation/e1_gate.json').read_text())['passed'],'E1 failed; E2 prohibited'
 start=time.monotonic();limit=float(os.environ['RF_WALL_SECONDS']);random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
 runner=Runner();cfg=runner.cfg;eds=nn.ModuleDict({op:Editor(method) for op in OPS}).cuda()
 opt=torch.optim.AdamW(eds.parameters(),lr=cfg['lr'],weight_decay=cfg['weight_decay'])
 train=load('train_pairs.jsonl');dev=load('dev_pairs.jsonl');dev_worlds={w['record_id']:w for w in load('dev_worlds.jsonl')}
 paths=sorted({r['path'] for r in train});groups={p:[r for r in train if r['path']==p] for p in paths}
 # Fixed path-balanced batches, permutation without replacement inside each path.
 rng=random.Random(seed);streams={p:[] for p in paths};schedule=[]
 for step in range(600):
  p=paths[step%6]
  if len(streams[p])<16:
   ids=list(range(len(groups[p])));rng.shuffle(ids);streams[p].extend(ids)
  ids=streams[p][:16];streams[p]=streams[p][16:];schedule.append([groups[p][i] for i in ids])
 directory=ROOT/f'checkpoints/{method}/s{seed}';directory.mkdir(parents=True,exist_ok=True)
 if (directory/'complete.json').exists():print('Already complete');return
 latest=directory/'latest.pt';best=1e10;beststep=0;history=[];seen={o:0 for o in OPS};updates={o:0 for o in OPS};train_tokens={o:0 for o in OPS};initial=0
 def loss(rs):
  op=select_operation(rs[0]['allowed_context']['source_frame'],rs[0]['allowed_context']['target_frame'])
  assert all(select_operation(r['allowed_context']['source_frame'],r['allowed_context']['target_frame'])==op for r in rs)
  x=runner.batch([r['source_text'] for r in rs]);y=runner.tok([r['target_text'] for r in rs],padding=True,truncation=False,return_tensors='pt').input_ids.cuda();y[y==runner.tok.pad_token_id]=-100
  with torch.no_grad():h=runner.model.get_encoder()(**x).last_hidden_state
  out=runner.model(encoder_outputs=BaseModelOutput(last_hidden_state=eds[op](h,x.attention_mask)),attention_mask=x.attention_mask,labels=y,use_cache=False)
  return out.loss,int((y!=-100).sum()),op,int(x.attention_mask.sum())
 @torch.no_grad()
 def devloss():
  total=count=0
  for path in paths:
   rs=[r for r in dev if r['path']==path]
   for i in range(0,len(rs),16):
    l,n,_,_=loss(rs[i:i+16]);total+=l.item()*n;count+=n
  return total/count
 if latest.exists():
  ck=torch.load(latest,weights_only=False);assert ck['config_hash']==digest(ROOT/'config.json');eds.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);initial=ck['step'];best=ck['best'];beststep=ck['beststep'];history=ck['history'];seen=ck['seen'];updates=ck['updates'];train_tokens=ck['train_tokens'];torch.set_rng_state(ck['rng']);torch.cuda.set_rng_state_all(ck['cuda_rng'])
 def save(step):
  ck={'editor':eds.state_dict(),'optimizer':opt.state_dict(),'step':step,'best':best,'beststep':beststep,'history':history,'seen':seen,'updates':updates,'train_tokens':train_tokens,'rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),'config_hash':digest(ROOT/'config.json'),'method':method,'seed':seed}
  torch.save(ck,directory/'latest.tmp');(directory/'latest.tmp').replace(latest)
 window=time.monotonic();step=initial
 for step0 in range(initial,600):
  if STOP or time.monotonic()-start>limit-120:save(step);print('Budget/signal stop, resumable checkpoint saved',flush=True);return
  opt.zero_grad(set_to_none=True);l,n,op,nt=loss(schedule[step0]);assert torch.isfinite(l);l.backward()
  assert all(p.grad is None for p in runner.model.parameters())
  assert eds[op].b.grad is not None and eds[op].b.grad.norm()>0
  torch.nn.utils.clip_grad_norm_(eds.parameters(),1.);opt.step();step=step0+1;seen[op]+=16;updates[op]+=1;train_tokens[op]+=nt+n
  if step==initial+12:
   torch.cuda.synchronize();seconds=(time.monotonic()-window)/12
   dump(f'checkpoints/{method}/s{seed}/short_window.json',{'seconds_per_update':seconds,'remaining_update_estimate_seconds':(600-step)*seconds,'excludes_validation_and_generation':True,'peak_cuda_bytes':torch.cuda.max_memory_allocated()})
  if step%100==0:
   vl=devloss();history.append({'step':step,'dev_target_token_nll':vl});print(f'{method} s{seed} {step} NLL={vl}',flush=True)
   if vl<best:best=vl;beststep=step;torch.save(eds.state_dict(),directory/'best.pt')
   save(step)
 eds.load_state_dict(torch.load(directory/'best.pt',weights_only=True));eh=digest(directory/'best.pt');outpath=directory/'dev_outputs.jsonl'
 outputs=[]
 # At completion, never select by these generations: checkpoint already selected by NLL.
 for path in paths:
  rs=[r for r in dev if r['path']==path];op=rs[0]['operation_ids'][0]
  for i in range(0,len(rs),16):
   batch=rs[i:i+16];outs,ended,timings,lens=runner.generate([r['source_text'] for r in batch],eds[op])
   for r,out,end,ln in zip(batch,outs,ended,lens):outputs.append({**r,'output':out,'method':method,'seed':seed,'editor_hash':eh,'model_hash':json.loads((ROOT/'source_model_manifest.json').read_text())['actual_files'][4]['sha256'],'output_tokens':ln,'source_tokens':len(runner.tok(r['source_text'])['input_ids']),'truncated':not end,'timing_s':timings,'score':score(out,r['allowed_context']['target_frame'],dev_worlds[r['gold_record_id']],end)})
 outpath.write_text(''.join(json.dumps(r)+'\n' for r in outputs))
 strata={'all':outputs,'time':[r for r in outputs if r['operation_ids'][0].startswith('T')],'perspective':[r for r in outputs if r['operation_ids'][0].startswith('P')],'plans':[r for r in outputs if dev_worlds[r['gold_record_id']]['record_status']=='recorded_plan']}
 metrics={s:{'N':len(rs),'joint_ok':sum(r['score']['joint_ok'] for r in rs)/len(rs),'plan_to_completed':sum(r['score']['plan_to_completed'] for r in rs)/len(rs),'parse_unresolved':sum(r['score']['parse_unresolved'] for r in rs)/len(rs)} for s,rs in strata.items()}
 passed=metrics['all']['joint_ok']>=.85 and metrics['time']['joint_ok']>=.8 and metrics['perspective']['joint_ok']>=.8 and metrics['plans']['plan_to_completed']<=.02
 dump(f'checkpoints/{method}/s{seed}/complete.json',{'method':method,'seed':seed,'steps':step,'beststep':beststep,'best_dev_token_nll':best,'seen':seen,'updates':updates,'train_tokens':train_tokens,'metrics':metrics,'e1_eligible':passed,'editor_hash':eh,'parameters':sum(p.numel() for p in eds.parameters()),'wall_seconds':time.monotonic()-start,'peak_cuda_bytes':torch.cuda.max_memory_allocated()})
 print(json.dumps(metrics),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--method',choices=['Shift','LowRank16'],required=True);p.add_argument('--seed',type=int,choices=[42,43,44],required=True);a=p.parse_args();run(a.method,a.seed)
