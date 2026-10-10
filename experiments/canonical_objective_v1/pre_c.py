"""No-training closure, per-step mixture dose, and geometric/likelihood overshoot."""
from cutil import *

@torch.no_grad()
def main():
    p=verify();eng,loader=old.frozen_engine();render,_,advance,*_=old.semantics();ws=worlds('eval');qs=bases();fs=fits()
    # Repeat closed cycles, not the five-operation path (which ends off its start).
    for t in p['templates_eval']:
      for name in p['closure']['paths']:
        sp=p['paths'][name];cycle=sp['operations'][:2 if name=='original_alternating' else 4]
        for lo in range(0,len(ws),16):
          file=f'results/shards/closure_t{t}_{name}_{lo:03d}.jsonl'
          if (ROOT/file).exists():continue
          chunk=ws[lo:lo+16];hi=lo+len(chunk);state=sp['initial_state'];a=canonical('eval',t,state);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();rs=[[] for _ in chunk];ok=[True]*len(chunk)
          for k in range(50):
            op=cycle[k%len(cycle)];h=rrr(h,m,fs,op);state=advance('time',state,op)
            ms=metrics(h,m,'eval',t,state,lo,hi,qs);out=old.evaluate(eng,h,m,chunk,state,t)
            for i,w in enumerate(chunk):
              assert ms[i]['aligned'];ok[i]=ok[i] and out[i]['score']['success']
              rs[i].append(dict(kind='closure',world_id=w['world_id'],template=t,path=name,step=k+1,state=state,operation=op,trajectory_success=ok[i],output=out[i],**ms[i]))
          write(file,(r for one in rs for r in one));print('closure',t,name,hi,flush=True)
    for seed in SEEDS:
      ed=loader(eng,old.previous.task(seed)['checkpoint']);ed.requires_grad_(False)
      for lam in p['dose']['lambdas']:
       for t in p['templates_eval']:
        for name,sp in p['paths'].items():
         for lo in range(0,len(ws),16):
          file=f'results/shards/dose_s{seed}_l{lam}_t{t}_{name}_{lo:03d}.jsonl'
          if (ROOT/file).exists():continue
          chunk=ws[lo:lo+16];hi=lo+len(chunk);state=sp['initial_state'];a=canonical('eval',t,state);h=a['h'][lo:hi].cuda();m=a['m'][lo:hi].cuda();rs=[];ok=[True]*len(chunk)
          for k,op in enumerate(sp['operations']):
            ce=ed[op](h,m);r=rrr(h,m,fs,op);h=(1-lam)*ce+lam*r;state=advance('time',state,op)
            ms=metrics(h,m,'eval',t,state,lo,hi,qs);out=old.evaluate(eng,h,m,chunk,state,t)
            for i,w in enumerate(chunk):
              ok[i]=ok[i] and out[i]['score']['success'];rs.append(dict(kind='dose',seed=seed,lambda_=lam,world_id=w['world_id'],template=t,path=name,step=k+1,state=state,trajectory_success=ok[i],output=out[i],**ms[i]))
          write(file,rs)
        print('dose',seed,lam,t,flush=True)
      # Canonical-source aligned single edits, independent of chain history.
      for t in p['templates_eval']:
       for s in range(-3,4):
        for op in ('plus','minus'):
         try:y=advance('time',s,op)
         except ValueError:continue
         a,b=canonical('eval',t,s),canonical('eval',t,y);n=max(a['h'].shape[1],b['h'].shape[1]);ah,am=old.pad(a['h'],a['m'],n);bh,bm=old.pad(b['h'],b['m'],n)
         if not torch.equal(am,bm):continue
         for lo in range(0,len(ws),16):
          file=f'results/shards/overshoot_s{seed}_t{t}_s{s}_{op}_{lo:03d}.jsonl'
          if (ROOT/file).exists() and all((ROOT/f'results/shards/mixsingle_s{seed}_l{lam}_t{t}_s{s}_{op}_{lo:03d}.jsonl').exists() for lam in p['dose']['lambdas']):continue
          chunk=ws[lo:lo+16];hi=lo+len(chunk);h=ah[lo:hi].cuda();m=am[lo:hi].cuda();ref=bh[lo:hi].cuda();edited=ed[op](h,m);e=(edited-ref)*m[...,None];d=(ref-h)*m[...,None]
          coeff=(e*d).sum((1,2))/d.square().sum((1,2));orth=e-coeff[:,None,None]*d
          texts=[render(w,y,t) for w in chunk];nll,nlabels=eng.ce(edited,m,texts);rnll,_=eng.ce(ref,m,texts);out=old.evaluate(eng,edited,m,chunk,y,t)
          rs=[]
          for i,w in enumerate(chunk):
            rs.append(dict(seed=seed,template=t,world_id=w['world_id'],source_state=s,target_state=y,operation=op,
              projection_coefficient=float(coeff[i]),orthogonal_norm=float(orth[i].norm()),residual_norm=float(e[i].norm()),ideal_write_norm=float(d[i].norm()),
              ce_logp_sum=float(-nll[i]*nlabels[i]),canonical_logp_sum=float(-rnll[i]*nlabels[i]),ce_logp_token=float(-nll[i]),canonical_logp_token=float(-rnll[i]),
              joint_overshoot=bool(coeff[i]>0 and nll[i]<rnll[i]),output=out[i]))
          write(file,rs)
          for lam in p['dose']['lambdas']:
            sf=f'results/shards/mixsingle_s{seed}_l{lam}_t{t}_s{s}_{op}_{lo:03d}.jsonl'
            if (ROOT/sf).exists():continue
            mix=(1-lam)*edited+lam*rrr(h,m,fs,op);mo=out if lam==0 else old.evaluate(eng,mix,m,chunk,y,t);mm=old.residual_metrics(mix,m,ref,m,qs)
            write(sf,[dict(seed=seed,lambda_=lam,template=t,source_state=s,operation=op,world_id=w['world_id'],output=mo[i],**mm[i]) for i,w in enumerate(chunk)])
      del ed
    for kind in ('closure','dose','overshoot','mixsingle'):
      write(f'results/{kind}.jsonl',(r for f in sorted((ROOT/'results/shards').glob(f'{kind}_*.jsonl')) for r in old.stream(f)))
    dump('results/pre_complete.json',dict(training_updates=0,resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
