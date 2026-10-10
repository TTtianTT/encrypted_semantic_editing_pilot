"""Alignment-free pooled frozen-S mismatch, from saved affine editor maps (CPU)."""
from cutil import *

def main():
    adv=old.semantics()[2];qs={s:load(V2/f'local/fit_s{s}.pt')['q'] for s in SEEDS};summary=[];p=read(ROOT/'protocol.json')
    pools={(t,s):old.pool(canonical('eval',t,s)['h'],canonical('eval',t,s)['m']) for t in (0,3) for s in range(-3,4)}
    for g in ('C1','C2','C3','C4','C5'):
     for seed in SEEDS:
      ck=load(ROOT/f'local/{g}_s{seed}_0600.pt')['editor']
      def apply(z,op):return z+z@ck[f'{op}.v.weight'].T@ck[f'{op}.u.weight'].T+ck[f'{op}.b']
      def measure(z,ref,meta):
        e=z-ref
        v=(e@qs[seed]).square().mean(1);summary.append(dict(group=g,seed=seed,**meta,worlds=80,pooled_S_coordinate_mse=float(v.mean()),ci95_world_bootstrap=old.bootstrap_mean(v.numpy()),pooled_full_mse=float(e.square().mean()),note='Mean-token signature mismatch; different units from tokenwise coordinate MSE. No token alignment required.'))
      for t in (0,3):
        for s in range(-3,4):
          for op in ('plus','minus'):
            try:y=adv('time',s,op)
            except ValueError:continue
            measure(apply(pools[t,s],op),pools[t,y],dict(kind='single',template=t,source_state=s,operation=op,target_state=y))
        for path,sp in p['paths'].items():
          state=sp['initial_state'];z=pools[t,state]
          for k,op in enumerate(sp['operations']):
            z=apply(z,op);state=adv('time',state,op);measure(z,pools[t,state],dict(kind='chain',template=t,path=path,step=k+1,state=state))
    # Verify the affine-pooling identity on a full masked token state.
    a=canonical('eval',0,0);h=a['h'][:2];m=a['m'][:2];z=h+(h@ck['plus.v.weight'].T@ck['plus.u.weight'].T+ck['plus.b'])*m[...,None]
    assert torch.allclose(old.pool(z,m),apply(old.pool(h,m),'plus'),atol=3e-6,rtol=1e-5)
    dump('results/pooled_S_geometry.json',summary)

if __name__=='__main__':main()
