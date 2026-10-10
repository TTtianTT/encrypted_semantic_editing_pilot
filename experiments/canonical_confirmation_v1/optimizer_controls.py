"""Matched fixed-panel CE, hidden gradients, and <=100-step C4 controls."""
from futils import *
VARIANTS={'adam_1e3':('AdamW',.001),'adam_1e4':('AdamW',.0001),'sgd_1':('SGD',1.),'sgd_10':('SGD',10.)}
STEPS=[0,5,10,15,20,25,50,75,100]

@torch.no_grad()
def fixed_panel(eng,ed,seed,k,variant):
 render=old.semantics()[0];ww=c.worlds('eval');qs=c.bases();rs=[]
 for op,it in c.transition_items('eval').items():
  for lo in range(0,len(it),16):
   part=it[lo:lo+16];h,m,y,ym,targets=c.batch('eval',0,part);z=ed[op](h,m);texts=[render(ww[i],s,0) for (i,_,_),s in zip(part,targets)];nll,_=eng.ce(z,m,texts);rnll,_=eng.ce(y,ym,texts);ms=old.residual_metrics(z,m,y,ym,qs)
   out=old.evaluate(eng,z,m,[ww[i] for i,_,_ in part],targets,0) if all(i<16 for i,_,_ in part) else None
   for j,(i,s,_) in enumerate(part):rs.append(dict(variant=variant,seed=seed,checkpoint=k,world_id=ww[i]['world_id'],source_state=s,operation=op,nll=float(nll[j]),canonical_nll=float(rnll[j]),output=out[j] if out else None,**ms[j]))
 write(f'results/shards/control_panel_{variant}_s{seed}_c{k}.jsonl',rs)
 # All 80 old worlds on the prospectively specified +1 aligned path.
 rr=[]
 for lo in range(0,len(ww),16):
  chunk=ww[lo:lo+16];hi=lo+len(chunk);a=c.canonical('eval',0,1);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();ok=[True]*len(chunk);s=1
  for j,op in enumerate(PATHS['aligned_from_plus_one']['operations']):
   h=ed[op](h,m);s=old.semantics()[2]('time',s,op);out=old.evaluate(eng,h,m,chunk,s,0);ms=c.metrics(h,m,'eval',0,s,lo,hi,qs)
   for i,w in enumerate(chunk):ok[i]=ok[i] and out[i]['score']['success'];rr.append(dict(variant=variant,seed=seed,checkpoint=k,world_id=w['world_id'],step=j+1,trajectory_success=ok[i],output=out[i],**ms[i]))
 write(f'results/shards/control_chain_{variant}_s{seed}_c{k}.jsonl',rr)

def hidden_gradients(eng):
 ed=c.new_editors(eng,42,True).eval().requires_grad_(False);render=old.semantics()[0];ww=c.worlds('eval');qs=c.bases();rs=[]
 for op,it in c.transition_items('eval').items():
  for lo in range(0,len(it),2):
   part=it[lo:lo+2];h,m,y,ym,targets=c.batch('eval',0,part);z=ed[op](h,m).detach().requires_grad_(True);texts=[render(ww[i],s,0) for (i,_,_),s in zip(part,targets)];nll,_=eng.ce(z,m,texts);g=torch.autograd.grad(nll.sum(),z)[0]*m[...,None];d=(y-h)*m[...,None];en=(z-y).detach()*m[...,None];gn=g.flatten(1).norm(dim=1);dn=d.flatten(1).norm(dim=1);cos=(g*d).sum((1,2))/(gn*dn).clamp_min(1e-30)
   for j,(i,s,_) in enumerate(part):rs.append(dict(world_id=ww[i]['world_id'],source_state=s,operation=op,nll=float(nll[j].detach()),gradient_norm=float(gn[j]),cos_gradient_ideal=float(cos[j]),cos_descent_ideal=float(-cos[j]),S_gradient_energy_fraction={str(seed):float((g[j]@q).square().sum()/gn[j].square().clamp_min(1e-30)) for seed,q in qs.items()},ideal_S_energy_fraction={str(seed):float((d[j]@q).square().sum()/dn[j].square().clamp_min(1e-30)) for seed,q in qs.items()},cos_descent_residual=float((-g[j]*en[j]).sum()/(gn[j]*en[j].norm()).clamp_min(1e-30))))
 write('results/hidden_gradients.jsonl',rs)

def main():
 verify('control_protocol.json');eng,_=old.frozen_engine();render=old.semantics()[0];ww=c.worlds('train');pool=c.transition_items('train');cfg=read(EX/'protocol.json')['training']
 if not (ROOT/'results/hidden_gradients.jsonl').exists():hidden_gradients(eng)
 for name,(kind,lr) in VARIANTS.items():
  for seed in (42,43,44):
   if (ROOT/f'results/control_{name}_s{seed}_complete.json').exists():continue
   ed=c.new_editors(eng,seed,True);opt=(torch.optim.AdamW if kind=='AdamW' else torch.optim.SGD)(ed.parameters(),lr=lr,weight_decay=0);rng=random.Random(seed);hist=[]
   fixed_panel(eng,ed,seed,0,name)
   for k in range(100):
    op=('plus','minus')[k%2];part=[rng.choice(pool[op]) for _ in range(8)];opt.zero_grad(set_to_none=True);ce=0.
    for lo in range(0,8,2):
     chunk=part[lo:lo+2];h,m,y,ym,ts=c.batch('train',0,chunk);loss=eng.ce(ed[op](h,m),m,[render(ww[i],s,0) for (i,_,_),s in zip(chunk,ts)])[0].mean();(loss/4).backward();ce+=float(loss.detach())/4
    gn=torch.nn.utils.clip_grad_norm_(ed.parameters(),1.);opt.step();hist.append(dict(step=k+1,ce_batch=ce,gradient_norm=float(gn)))
    if k+1 in STEPS:
     save(f'local/control_{name}_s{seed}_{k+1:04d}.pt',dict(editor=c.cpu_state(ed),history=hist,optimizer=opt.state_dict()))
     if name=='adam_1e3' and k+1 in (10,25,50,100):
      prev=load(EX/f'local/C4_s{seed}_{k+1:04d}.pt')['editor'];diff=max(float((v-prev[key]).abs().max()) for key,v in c.cpu_state(ed).items());assert diff<1e-6,(seed,k,diff)
     fixed_panel(eng,ed,seed,k+1,name);print('control',name,seed,k+1,ce,flush=True)
   write(f'results/control_training_{name}_s{seed}.jsonl',hist);dump(f'results/control_{name}_s{seed}_complete.json',dict(updates=100,optimizer=kind,lr=lr,resources=eng.resources()))
 for kind in ('control_panel','control_chain'):
  write(f'results/{kind}.jsonl',(r for f in sorted((ROOT/'results/shards').glob(kind+'_*.jsonl')) for r in old.stream(f)))
 dump('results/controls_complete.json',dict(updates=1200,backbone_updates=0,resources=eng.resources()))
if __name__=='__main__':main()
