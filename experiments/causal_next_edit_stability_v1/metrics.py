"""World-cluster statistics, with equally weighted available editor seeds."""
import numpy as np

def clustered_difference(records,local,random_names,reps=10000,seed=2026100402):
    grouped={}
    for r in records:
        if r['sequence_name']!='primary':continue
        grouped.setdefault((r['world_id'],r['editor_seed']),{})[r['method_name']]=float(r['R1'])
    complete={k:v for k,v in grouped.items() if local in v and all(n in v for n in random_names)}
    worlds=sorted({k[0] for k in complete});seeds=sorted({k[1] for k in complete})
    if not worlds:return dict(n_worlds=0,estimate=None,ci95=None,p_raw=None)
    x=np.full((len(worlds),len(seeds)),np.nan)
    for i,w in enumerate(worlds):
        for j,s in enumerate(seeds):
            if (w,s) in complete:
                v=complete[w,s];x[i,j]=v[local]-np.mean([v[n] for n in random_names])
    def estimate(a):return float(np.nanmean(np.nanmean(a,axis=0)))
    rng=np.random.default_rng(seed);boot=[]
    for _ in range(reps):boot.append(estimate(x[rng.integers(len(worlds),size=len(worlds))]))
    observed=estimate(x);null=[]
    for _ in range(reps):null.append(estimate(x*rng.choice([-1,1],size=(len(worlds),1))))
    return dict(n_worlds=len(worlds),n_seeds=len(seeds),estimate=observed,ci95=np.quantile(boot,[.025,.975]).tolist(),p_raw=(1+sum(abs(v)>=abs(observed)-1e-12 for v in null))/(reps+1),per_seed={str(s):float(np.nanmean(x[:,j])) for j,s in enumerate(seeds)},resampling='union-world clusters shared across seeds; equal-weight seed means; missing seed/world cells kept missing',assumption='two-sided sign flips require symmetric/exchangeable world-level paired differences; not exact randomized-trial p')

def holm(ps):
    valid=sorted((p,i) for i,p in enumerate(ps) if p is not None);out=[None]*len(ps);last=0
    for rank,(p,i) in enumerate(valid):last=max(last,min(1,p*(len(ps)-rank)));out[i]=last
    return out
