"""Once-only locked fresh-world predictions, including unsupported transitions."""
from futils import *
@torch.no_grad()
def main():
 verify();eng,_=old.frozen_engine();adv=old.semantics()[2];qs={s:load(ROOT/f'local/mechanism_S_s{s}.pt')['q'].cuda() for s in SEEDS}
 for domain,seeds in [('time',SEEDS),('person',(42,43,44))]:
  ww=ws(domain);paths=PATHS if domain=='time' else {'person_forward':dict(initial_state=1,operations=['plus','minus','plus','minus','plus']),'person_reverse':dict(initial_state=2,operations=['minus','plus','minus','plus','minus'])}
  tasks=[(g,s,k) for g in ('C1','C3','C4') for s in seeds for k in (CKS if g=='C4' else [600])]+[('RRR',0,0),('reencode',0,0)]
  for g,seed,k in tasks:
   ed=model(eng,g,seed,k,domain)
   for t in (0,3):
    for name,sp in paths.items():
     for lo in range(0,len(ww),16):
      file=f'results/shards/fresh_chain_{domain}_{g}_s{seed}_c{k}_t{t}_{name}_{lo:03d}.jsonl'
      if (ROOT/file).exists():continue
      chunk=ww[lo:lo+16];hi=lo+len(chunk);s=sp['initial_state'];a=cache(domain,'eval',t,s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();ok=[True]*len(chunk);rr=[]
      for j,op in enumerate(sp['operations']):
       s=adv(domain,s,op)
       if g=='reencode':a=cache(domain,'eval',t,s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda()
       else:h=ed[op](h,m)
       out=old.evaluate(eng,h,m,chunk,s,t);ms=residual(h,m,domain,'eval',t,s,lo,hi,qs)
       for i,w in enumerate(chunk):ok[i]=ok[i] and out[i]['score']['success'];rr.append(dict(domain=domain,group=g,seed=seed,checkpoint=k,template=t,path=name,world_id=w['world_id'],step=j+1,state=s,trajectory_success=ok[i],output=out[i],**ms[i]))
      write(file,rr)
    for s in old.semantics()[3](domain):
     for op in ('plus','minus'):
      try:y=adv(domain,s,op)
      except ValueError:continue
      for lo in range(0,len(ww),16):
       file=f'results/shards/fresh_single_{domain}_{g}_s{seed}_c{k}_t{t}_s{s}_{op}_{lo:03d}.jsonl'
       if (ROOT/file).exists():continue
       chunk=ww[lo:lo+16];hi=lo+len(chunk);a=cache(domain,'eval',t,y if g=='reencode' else s);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda()
       if g!='reencode':h=ed[op](h,m)
       out=old.evaluate(eng,h,m,chunk,y,t);ms=residual(h,m,domain,'eval',t,y,lo,hi,qs)
       write(file,[dict(domain=domain,group=g,seed=seed,checkpoint=k,template=t,world_id=w['world_id'],source_state=s,target_state=y,operation=op,output=out[i],**ms[i]) for i,w in enumerate(chunk)])
    print('fresh eval',domain,g,seed,k,t,flush=True)
 for kind in ('fresh_chain','fresh_single'):write(f'results/{kind}.jsonl',(r for f in sorted((ROOT/'results/shards').glob(kind+'_*.jsonl')) for r in old.stream(f)))
 dump('results/fresh_evaluation_complete.json',dict(resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))
if __name__=='__main__':main()
