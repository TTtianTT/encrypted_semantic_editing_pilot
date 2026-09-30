"""Train one rank's three seed-matched T+ editors on the fixed G3 schedule."""
import argparse,sys,time,random,json
from pathlib import Path
import torch
from torch import nn
from g10_common import *
sys.path.insert(0,str(G7));sys.path.insert(0,str(V3))
from extract import Backbone,readjsonl
from common import advance,render
CFG=json.loads((ROOT/'config.json').read_text())

class LowRank(nn.Module):
 def __init__(self,d,r):
  super().__init__();self.b=nn.Parameter(torch.zeros(d));self.v=nn.Linear(d,r,bias=False);self.u=nn.Linear(r,d,bias=False)
  nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,h,m):
  z=h.float();return (z+(self.b+self.u(self.v(z)))*m[...,None]).to(h.dtype)

def main(rank):
 assert __import__('os').environ.get('SLURM_JOB_ID'),'Use sbatch and srun for GPU training'
 lock=json.loads((ROOT/'data/lock.json').read_text());assert digest(ROOT/'config.json')==lock['config_sha256'] and digest(ROOT/'PROTOCOL.md')==lock['protocol_sha256']
 base=Backbone('BART');base.model.eval();assert all(not p.requires_grad for p in base.model.parameters())
 rows=readjsonl(V3/'data/train_G1.jsonl');worlds={w['record_id']:w for w in readjsonl(V3/'data/train_worlds.jsonl')}
 schedule=[b for b in readjsonl(V3/'data/sample_schedule.jsonl') if b['path'].startswith('T_plus')];assert len(schedule)==200 and sum(sum(b['g2_replace']) for b in schedule)==1600
 dev=readjsonl(V3/'data/dev_atomic.jsonl');dev=[r for r in dev if r['operations']==['T_plus']]
 folder=ROOT/f'checkpoints/rank{rank}';folder.mkdir(parents=True,exist_ok=True);results=[]
 for seed in CFG['seeds']:
  ident=f'rank{rank}_seed{seed}';target=folder/f'{ident}.pt';meta=folder/f'{ident}.json'
  if target.exists() and meta.exists():
   previous=json.loads(meta.read_text());assert previous['checkpoint_sha256']==digest(target);results.append(previous);continue
  import hashlib
  torch.manual_seed(seed);torch.cuda.manual_seed_all(seed);random.seed(seed)
  ed=LowRank(base.U.shape[0],rank).cuda().eval();torch.cuda.reset_peak_memory_stats();init_hash=hashlib.sha256(b''.join(p.detach().flatten().cpu().numpy().tobytes() for p in ed.parameters())).hexdigest()
  opt=torch.optim.AdamW(ed.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay'])
  perstep=[];counts={'supervised_samples':0,'supervision_tokens':0,'endpoint_weight_tokens':0,'operator_sample_calls':0,'decoder_sample_calls':0,'decoder_batch_calls':0};started=time.monotonic();torch.cuda.reset_peak_memory_stats()
  for b in schedule:
   batch=[rows[k] for k in b['pair_indices']];flags=b['g2_replace'];opt.zero_grad(set_to_none=True)
   loss,stats=base.eng.stage_loss(nn.ModuleDict({'T_plus':ed}),batch,flags,worlds,alpha=.5,beta=.5)
   assert torch.isfinite(loss);loss.backward();assert all(p.grad is None for p in base.model.parameters())
   torch.nn.utils.clip_grad_norm_(ed.parameters(),CFG['gradient_clip']);opt.step()
   for key in ('supervision_tokens','endpoint_weight_tokens','operator_sample_calls','decoder_sample_calls','decoder_batch_calls'):counts[key]+=stats[key]
   counts['supervised_samples']+=len(batch);perstep.append(dict(step=b['step'],loss=float(loss.detach()),supervision_tokens=stats['supervision_tokens']))
  elapsed=time.monotonic()-started
  # Record common dev token NLL; the training endpoint remains fixed at update 200.
  total=tokens=0;eds=nn.ModuleDict({'T_plus':ed})
  with torch.no_grad():
   for i in range(0,len(dev),16):
    l,n,_=base.eng.loss(eds,dev[i:i+16]);total+=float(l)*n;tokens+=n
  torch.save(ed.cpu().state_dict(),target);item=dict(editor=ident,rank=rank,seed=seed,updates=len(schedule),dev_atomic_token_nll=total/tokens,
      parameters=sum(p.numel() for p in ed.parameters()),initialization_hash=init_hash,checkpoint_sha256=digest(target),
      training_seconds=elapsed,peak_cuda_bytes=torch.cuda.max_memory_allocated(),counts=counts,step_log=perstep,
      train_data_sha256=digest(V3/'data/train_G1.jsonl'),schedule_sha256=digest(V3/'data/sample_schedule.jsonl'),
      task_source='G3 T_plus schedule; 1600 fixed G2 replacement occurrences use two-stage G3 supervision')
  dump(f'checkpoints/rank{rank}/{ident}.json',item);results.append(item);print('trained',ident,item['dev_atomic_token_nll'],elapsed,flush=True)
  del opt,ed,eds;torch.cuda.empty_cache()
 dump(f'training/rank{rank}.json',results)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--rank',type=int,choices=[8,16,32],required=True);main(p.parse_args().rank)
