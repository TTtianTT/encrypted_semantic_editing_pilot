"""Locked trajectory and canonical single-edit evaluation; no model selection."""
from cutil import *

@torch.no_grad()
def main():
    p=verify();eng,_=old.frozen_engine();_,_,advance,*_=old.semantics();ws=worlds('eval');qs=bases()
    for group in ('C1','C2','C3','C4','C5'):
     for seed in SEEDS:
      steps=p['training']['evaluation_C4_checkpoints'] if group=='C4' else [600]
      for ck in steps:
       ed=load_new(eng,group,seed,ck);ed.requires_grad_(False)
       for t in p['templates_eval']:
        for name,sp in p['paths'].items():
         for lo in range(0,len(ws),16):
          file=f'results/shards/chain_{group}_s{seed}_c{ck}_t{t}_{name}_{lo:03d}.jsonl'
          if (ROOT/file).exists():continue
          chunk=ws[lo:lo+16];hi=lo+len(chunk);state=sp['initial_state'];a=canonical('eval',t,state);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();rs=[];ok=[True]*len(chunk)
          for k,op in enumerate(sp['operations']):
            h=ed[op](h,m);state=advance('time',state,op);out=old.evaluate(eng,h,m,chunk,state,t);ms=metrics(h,m,'eval',t,state,lo,hi,qs)
            for i,w in enumerate(chunk):
              ok[i]=ok[i] and out[i]['score']['success'];rs.append(dict(group=group,seed=seed,checkpoint=ck,world_id=w['world_id'],template=t,path=name,step=k+1,state=state,trajectory_success=ok[i],output=out[i],**ms[i]))
          write(file,rs)
        for s in range(-3,4):
         for op in ('plus','minus'):
          try:y=advance('time',s,op)
          except ValueError:continue
          a=canonical('eval',t,s)
          for lo in range(0,len(ws),16):
           file=f'results/shards/single_{group}_s{seed}_c{ck}_t{t}_s{s}_{op}_{lo:03d}.jsonl'
           if (ROOT/file).exists():continue
           chunk=ws[lo:lo+16];hi=lo+len(chunk);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();h=ed[op](h,m);out=old.evaluate(eng,h,m,chunk,y,t);ms=metrics(h,m,'eval',t,y,lo,hi,qs)
           write(file,[dict(group=group,seed=seed,checkpoint=ck,world_id=w['world_id'],template=t,source_state=s,target_state=y,operation=op,output=out[i],**ms[i]) for i,w in enumerate(chunk)])
        print('eval',group,seed,ck,t,flush=True)
       del ed
    for kind in ('chain','single'):
      write(f'results/{kind}.jsonl',(r for f in sorted((ROOT/'results/shards').glob(f'{kind}_*.jsonl')) for r in old.stream(f)))
    dump('results/evaluation_complete.json',dict(resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
