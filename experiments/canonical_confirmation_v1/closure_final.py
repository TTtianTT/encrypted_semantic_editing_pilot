"""C3 and deterministic RRR closures, fixed fresh subset and full affine spectra."""
from futils import *
@torch.no_grad()
def main():
 verify();eng,_=old.frozen_engine();ww=ws()[:80];qs={s:load(ROOT/f'local/mechanism_S_s{s}.pt')['q'].cuda() for s in SEEDS};spectra=[]
 for g,seed in [('C3',s) for s in SEEDS]+[('RRR',0)]:
  ed=model(eng,g,seed)
  for name in ('original_alternating','aligned_from_plus_one','aligned_from_minus_one'):
   sp=PATHS[name];cycle=sp['operations'][:2 if name=='original_alternating' else 4];A=torch.eye(768,dtype=torch.float64);bb=torch.zeros(768,dtype=torch.float64)
   for op in cycle:
    e=ed[op];a=torch.eye(768,dtype=torch.float64)+e.v.weight.T.cpu().double()@e.u.weight.T.cpu().double();b=e.b.cpu().double();A=A@a;bb=bb@a+b
   eigen=torch.linalg.eigvals(A);rho=float(eigen.abs().max());spectra.append(dict(group=g,seed=seed,path=name,cycle=cycle,spectral_radius_cycle=rho,per_step_radius=rho**(1/len(cycle)),unstable_count=int((eigen.abs()>1+1e-7).sum()),affine_bias_norm=float(bb.norm()),interpretation='Spectral instability is not a guarantee that every initial error excites an unstable mode'))
   for t in (0,3):
    for lo in range(0,len(ww),16):
     file=f'results/shards/fresh_closure_{g}_s{seed}_t{t}_{name}_{lo:03d}.jsonl'
     if (ROOT/file).exists():continue
     chunk=ww[lo:lo+16];hi=lo+len(chunk);s=sp['initial_state'];a=cache('time','eval',t,s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();ok=[True]*len(chunk);rr=[]
     for j in range(50):
      op=cycle[j%len(cycle)];s=old.semantics()[2]('time',s,op);h=ed[op](h,m);out=old.evaluate(eng,h,m,chunk,s,t);ms=residual(h,m,'time','eval',t,s,lo,hi,qs)
      for i,w in enumerate(chunk):ok[i]=ok[i] and out[i]['score']['success'];rr.append(dict(domain='time',group=g,seed=seed,template=t,path=name,world_id=w['world_id'],step=j+1,state=s,trajectory_success=ok[i],output=out[i],**ms[i]))
     write(file,rr);print('fresh closure',g,seed,t,name,hi,flush=True)
 write('results/fresh_closure.jsonl',(r for f in sorted((ROOT/'results/shards').glob('fresh_closure_*.jsonl')) for r in old.stream(f)));dump('results/fresh_spectrum.json',spectra);dump('results/fresh_closure_complete.json',dict(resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))
if __name__=='__main__':main()
