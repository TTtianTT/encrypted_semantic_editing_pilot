"""Reuse locked exploratory endpoints; add two seeds and dense C4 replays."""
from futils import *
def main():
 verify();eng,_=old.frozen_engine();render=old.semantics()[0];tasks=[]
 for domain,seeds in [('time',SEEDS),('person',(42,43,44))]:
  for g in ('C1','C3','C4'):
   for seed in seeds:
    if domain=='time' and g!='C4' and seed<45:continue
    tasks.append((domain,g,seed,50 if g=='C4' else 600))
 for domain,g,seed,total in tasks:
  end=ROOT/f'results/train_{domain}_{g}_s{seed}_complete.json'
  if end.exists():continue
  ed=new_ed(eng,seed,domain,g=='C4');opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0);rng=random.Random(seed);pool=items(domain);ww=ws(domain,'train');scale=read(EX/'protocol.json')['training']['l2_scale'] if domain=='time' else read(ROOT/'results/person_fit.json')['scale'];hist=[]
  def ck(k):save(f'local/{domain}_{g}_s{seed}_{k:04d}.pt',dict(editor=c.cpu_state(ed),group=g,domain=domain,seed=seed,step=k,history=hist,protocol_sha256=sha(ROOT/'protocol.json')))
  ck(0)
  for k in range(total):
   op=('plus','minus')[k%2];part=[rng.choice(pool[op]) for _ in range(8)];opt.zero_grad(set_to_none=True);tot={'ce':0.,'l2':0.}
   for lo in range(0,8,2):
    chunk=part[lo:lo+2];h,m,y,ym,ts=batch(domain,'train',0,chunk);z=ed[op](h,m);ce=eng.ce(z,m,[render(ww[i],s,0) for (i,_,_),s in zip(chunk,ts)])[0].mean();l2=c.aligned_error(z,m,y,ym).mean()/scale[op] if g=='C3' else torch.zeros((),device='cuda');((ce+l2)/4).backward();tot['ce']+=float(ce.detach())/4;tot['l2']+=float(l2.detach())/4
   gn=torch.nn.utils.clip_grad_norm_(ed.parameters(),1.);assert torch.isfinite(gn);opt.step();hist.append(dict(step=k+1,gradient_norm=float(gn),**tot))
   if (g=='C4' and k+1 in CKS) or k+1==total:
    ck(k+1)
    if domain=='time' and g=='C4' and seed<45 and k+1 in (10,25,50):
     before=load(EX/f'local/C4_s{seed}_{k+1:04d}.pt')['editor'];assert max(float((v-before[key]).abs().max()) for key,v in c.cpu_state(ed).items())<1e-6
    print('final train',domain,g,seed,k+1,tot,flush=True)
  write(f'results/train_{domain}_{g}_s{seed}.jsonl',hist);dump(str(end.relative_to(ROOT)),dict(updates=total,resources=eng.resources(),final_sha256=sha(ROOT/f'local/{domain}_{g}_s{seed}_{total:04d}.pt')))
 # Fixed S for confirmation intervention, and final-group geometric diagnostics.
 for domain,seeds in [('time',SEEDS),('person',(42,43,44))]:
  for seed in seeds:
   for g in ('C1','C3','C4'):
    ed=model(eng,g,seed,50 if g=='C4' else 600,domain);save(f'local/pca_{domain}_{g}_s{seed}.pt',qfit(ed,domain))
    if domain=='time' and g=='C1':save(f'local/mechanism_S_s{seed}.pt',qfit(ed,domain,True))
 dump('results/final_training_complete.json',dict(new_updates=sum(t[3] for t in tasks),reused_C1_C3_seeds=[42,43,44],resources=eng.resources()))
if __name__=='__main__':main()
