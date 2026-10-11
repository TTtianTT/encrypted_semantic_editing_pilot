"""Coverage-matched CE, per-example canonical CE floor, and GAN adaptations."""
from mutil import *
import torch.nn.functional as F
class Discriminator(torch.nn.Module):
 def __init__(self,kind,mean,std):
  super().__init__();self.kind=kind;self.register_buffer('mean',mean.cuda());self.register_buffer('std',std.cuda())
  self.phi=torch.nn.Sequential(torch.nn.Linear(768,128),torch.nn.LeakyReLU(.2),torch.nn.Linear(128,128),torch.nn.LeakyReLU(.2)) if kind=='set' else torch.nn.Identity()
  n=256 if kind=='set' else 768
  self.rho=torch.nn.Sequential(torch.nn.Linear(n,128),torch.nn.LeakyReLU(.2),torch.nn.Linear(128,1))
 def forward(self,h,m):
  if self.kind=='pool':v=(h*m[...,None]).sum(1)/m.sum(1)[:,None];v=(v-self.mean)/self.std
  else:
   u=self.phi((h-self.mean)/self.std);avg=(u*m[...,None]).sum(1)/m.sum(1)[:,None];mx=u.masked_fill(~m.bool()[...,None],-float('inf')).max(1).values;v=torch.cat([avg,mx],-1)
  return self.rho(v).squeeze(-1)
def normalization(kind):
 vals=[]
 for s in old.semantics()[3]('time'):
  a=cache('time','train',0,s);h,m=a['h'],a['m']
  vals.append((h*m[...,None]).sum(1)/m.sum(1)[:,None] if kind=='pool' else h[m.bool()])
 v=torch.cat(vals);return v.mean(0),v.std(0).clamp_min(.01)
def real_bank():
 # No padding/length shortcut. Real examples are genuine canonical sequences
 # with exactly the edited source mask length; all states enter the marginal.
 bank=defaultdict(list)
 for s in old.semantics()[3]('time'):
  a=cache('time','train',0,s)
  for i,m in enumerate(a['m']):bank[int(m.sum())].append((s,i))
 return bank
def sample_real(bank,m,rng):
 hs=[]
 for mask in m:
  n=int(mask.sum());s,i=rng.choice(bank[n]);a=cache('time','train',0,s);v=a['h'][i][a['m'][i].bool()];hs.append(F.pad(v,(0,0,0,m.shape[1]-n)))
 return torch.stack(hs).cuda(),m
def labels(p):
 out=['CE_all','floor']
 for kind in ('pool','set'):
  out.extend(f'adv_{kind}_l{l:g}' for l in p['baseline']['lambda_grid'])
 return out
def main():
 p=verify();eng,_=old.frozen_engine();render=old.semantics()[0];ww=ws('time','train');pool=items('time','train');canon=load(ROOT/'local/canonical_ce.pt');bank=real_bank();part_index=int(os.environ.get('PART_INDEX','0'));tasks=[(name,seed) for name in labels(p) for seed in SEEDS];tasks=tasks[part_index::2]
 for name,seed in tasks:
  label=f'{name}_s{seed}';done=ROOT/f'results/train_{label}_complete.json'
  if done.exists():continue
  ed=c.new_editors(eng,seed);opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0);rng=random.Random(seed);rrng=random.Random(seed+7000);hist=[];D=None
  if name.startswith('adv_'):
   kind=name.split('_')[1];lam=float(name.split('_l')[1]);torch.manual_seed(seed+10000);D=Discriminator(kind,*normalization(kind)).cuda();dop=torch.optim.AdamW(D.parameters(),lr=.0001,weight_decay=0)
  start=time.time()
  for k in range(600):
   op=('plus','minus')[k%2];part=[rng.choice(pool[op]) for _ in range(8)];tot=defaultdict(float)
   if D is not None:
    D.requires_grad_(True);dop.zero_grad(set_to_none=True)
    for lo in range(0,8,2):
     h,m,_,_,_=batch('time','train',0,part[lo:lo+2]);real,rm=sample_real(bank,m,rrng)
     with torch.no_grad():z=ed[op](h,m)
     a,b=D(real,rm),D(z,m);dl=(F.softplus(-a).mean()+F.softplus(b).mean())/2;(dl/4).backward();tot['discriminator_loss']+=float(dl.detach())/4;tot['discriminator_accuracy']+=float(((a>0).float().mean()+(b<0).float().mean())/2)/4
    torch.nn.utils.clip_grad_norm_(D.parameters(),1.);dop.step();D.requires_grad_(False)
   opt.zero_grad(set_to_none=True)
   for lo in range(0,8,2):
    chunk=part[lo:lo+2];h,m,_,_,ts=batch('time','train',0,chunk);z=ed[op](h,m);ce=eng.ce(z,m,[render(ww[i],s,0) for (i,_,_),s in zip(chunk,ts)])[0];threshold=torch.tensor([canon[s][i] for (i,_,_),s in zip(chunk,ts)],device='cuda');loss=(ce-threshold).clamp_min(0).mean() if name=='floor' else ce.mean();tot['ce']+=float(ce.detach().mean())/4;tot['canonical_ce']+=float(threshold.mean())/4;tot['above_floor']+=float((ce.detach()>threshold).float().mean())/4
    if D is not None:adv=F.softplus(-D(z,m)).mean();loss=loss+lam*adv;tot['adv']+=float(adv.detach())/4
    (loss/4).backward();tot['objective']+=float(loss.detach())/4
   gn=torch.nn.utils.clip_grad_norm_(ed.parameters(),1.);assert torch.isfinite(gn);opt.step();hist.append(dict(step=k+1,gradient_norm=float(gn),**tot))
   if (k+1)%100==0:print('train',label,k+1,dict(tot),flush=True)
  save(f'local/{label}.pt',dict(editor=c.cpu_state(ed),discriminator=c.cpu_state(D) if D is not None else None,group=name,seed=seed,updates=600,protocol_sha256=sha(ROOT/'protocol.json')))
  write(f'results/train_{label}.jsonl',hist);dump(str(done.relative_to(ROOT)),dict(job_id=os.environ['SLURM_JOB_ID'],gpus=1,updates=600,discriminator_updates=600 if D is not None else 0,seconds=time.time()-start,resources=eng.resources(),checkpoint_sha256=sha(ROOT/f'local/{label}.pt')))
 dump(f'results/training_part{part_index}_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],tasks=[f'{n}_s{s}' for n,s in tasks]))
if __name__=='__main__':main()
