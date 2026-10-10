"""Train-only residual PCA; fixed historical S intervention for final editors."""
from cutil import *

@torch.no_grad()
def main():
    p=verify();eng,loader=old.frozen_engine();qs=bases();train_items=transition_items('train');ws=worlds('eval');out=[];summary=[];newq={}
    for group in ('C1','C2','C3','C4','C5'):
     for seed in SEEDS:
      ed=load_new(eng,group,seed,600);ed.requires_grad_(False)
      eigfile=ROOT/f'local/pca_{group}_s{seed}.pt'
      if eigfile.exists():fit=load(eigfile)
      else:
        sx=torch.zeros(768,device='cuda',dtype=torch.float64);sxx=torch.zeros(768,768,device='cuda',dtype=torch.float64);n=0
        for op,items in train_items.items():
          for lo in range(0,len(items),16):
            h,m,y,ym,_=batch('train',0,items[lo:lo+16]);z=ed[op](h,m);length=max(z.shape[1],y.shape[1]);z,m=old.pad(z,m,length);y,ym=old.pad(y,ym,length);assert torch.equal(m,ym)
            e=(z-y)[m.bool()].double();n+=len(e);sx+=e.sum(0);sxx+=e.T@e
        mu=sx/n;cov=sxx/n-mu[:,None]*mu[None,:];vals,vecs=torch.linalg.eigh(cov.cpu());vals=vals.clamp_min(0).flip(0);q=vecs[:,-4:].flip(1).float()
        fit=dict(q=q,eigenvalues=vals.tolist(),token_mse=float(sxx.trace()/(n*768)),centered_token_mse=float(cov.trace()/768),mean_residual_norm=float(mu.norm()),top4_fraction=float(vals[:4].sum()/vals.sum()),gap4=float(vals[3]-vals[4]),relative_gap4=float((vals[3]-vals[4])/vals[3].clamp_min(1e-30)),train_tokens=n,world_ids=p['worlds_train'])
        save(f'local/pca_{group}_s{seed}.pt',fit)
      newq[group,seed]=fit['q'];summary.append(dict(group=group,seed=seed,**{k:v for k,v in fit.items() if k not in ('q','eigenvalues','world_ids')},lambda4=fit['eigenvalues'][3],lambda5=fit['eigenvalues'][4]))
      hist=loader(eng,old.previous.task(seed)['checkpoint']);hist.requires_grad_(False)
      for t in p['templates_eval']:
       for lo in range(0,len(ws),16):
        file=f'results/shards/injection_{group}_s{seed}_t{t}_{lo:03d}.jsonl'
        if (ROOT/file).exists():continue
        chunk=ws[lo:lo+16];hi=lo+len(chunk);a,b=canonical('eval',t,0),canonical('eval',t,-1);length=max(a['h'].shape[1],b['h'].shape[1]);h,m=old.pad(a['h'][lo:hi].cuda(),a['m'][lo:hi].cuda(),length);ref,rm=old.pad(b['h'][lo:hi].cuda(),b['m'][lo:hi].cuda(),length);assert torch.equal(m,rm)
        delta=old.project(hist['plus'](h,m)-ref,qs[seed])*m[...,None]
        z=ed['plus'](h,m);current=old.evaluate(eng,z,m,chunk,-1,t);base_next=old.evaluate(eng,ed['minus'](z,m),m,chunk,0,t)
        zi=z+delta;injected=old.evaluate(eng,zi,m,chunk,-1,t);nextout=old.evaluate(eng,ed['minus'](zi,m),m,chunk,0,t)
        write(file,[dict(group=group,seed=seed,template=t,world_id=w['world_id'],injection_norm=float(delta[i].norm()),current=current[i],baseline_next=base_next[i],injected_current=injected[i],injected_next=nextout[i]) for i,w in enumerate(chunk)])
      del ed,hist
      print('mechanism',group,seed,'energy',fit['token_mse'],flush=True)
    angles=[]
    for group in ('C1','C2','C3','C4','C5'):
      for i,a in enumerate(SEEDS):
        for b in SEEDS[i+1:]:
          s=torch.linalg.svdvals(newq[group,a].double().T@newq[group,b].double()).clamp(0,1)
          angles.append(dict(group=group,seed_a=a,seed_b=b,angles_deg=torch.rad2deg(torch.acos(s)).tolist(),mean_cos2=float(s.square().mean())))
    csvwrite('results/residual_pca.csv',summary);write('results/cross_seed_angles.jsonl',angles)
    write('results/injection.jsonl',(r for f in sorted((ROOT/'results/shards').glob('injection_*.jsonl')) for r in old.stream(f)))
    dump('results/mechanism_complete.json',dict(resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
