"""No new inference: write geometry and strictly lagged continuation risks."""
from futils import *
import math

def auc(y,p):
 from scipy.stats import rankdata
 y=np.asarray(y,bool);n=int(y.sum());m=len(y)-n
 return float((rankdata(p)[y].sum()-n*(n+1)/2)/(n*m)) if n*m else None
def logistic(x,y,weights):
 X=np.c_[np.ones(len(x)),x];b=np.zeros(2)
 for _ in range(80):
  p=1/(1+np.exp(-np.clip(X@b,-35,35)));v=p*(1-p);g=X.T@(weights*(p-y))+1e-5*b;H=X.T@(X*(weights*v)[:,None])+1e-5*np.eye(2);step=np.linalg.solve(H,g);b-=step
  if np.linalg.norm(step)<1e-8:break
 return b
def main():
 geo=[]
 for r in old.stream(EX/'results/overshoot.jsonl'):
  dn=r['ideal_write_norm'];en=r['residual_norm'];a=r['projection_coefficient'];wn=math.sqrt(max(0,en*en+(1+2*a)*dn*dn));ratio=wn/dn
  geo.append(dict(seed=r['seed'],template=r['template'],world_id=r['world_id'],source_state=r['source_state'],operation=r['operation'],write_to_ideal_norm=ratio,cos_write_ideal=(a+1)/max(ratio,1e-12),write_projection=a+1))
 write('results/write_geometry.jsonl',geo)
 out=[]
 for k,rs in grouped(geo,['seed','template']).items():
  d=defaultdict(list)
  for r in rs:d[r['world_id']].append(r)
  z={v:[np.mean([r[v] for r in one]) for one in d.values()] for v in ['write_to_ideal_norm','cos_write_ideal','write_projection']}
  out.append(dict(seed=k[0],template=k[1],n_worlds=len(d),**{v:dict(mean=float(np.mean(a)),ci95_world_bootstrap=old.bootstrap_mean(a)) for v,a in z.items()}))
 dump('results/write_geometry_summary.json',out)
 lag=[];counts={}
 for kind in ('chain','dose','closure'):
  trajectories=defaultdict(list);nr=0
  for r in old.stream(EX/f'results/{kind}.jsonl'):
   nr+=1
   keys=['group','seed','checkpoint'] if kind=='chain' else ['seed','lambda_'] if kind=='dose' else []
   key=tuple(r.get(k) for k in keys+['template','path','world_id']);trajectories[key].append(r)
  counts[kind]=nr
  for rs in trajectories.values():
   rs.sort(key=lambda r:r['step'])
   for prev,nxt in zip(rs,rs[1:]):
    assert nxt['step']==prev['step']+1
    # Valid-current, complete-prefix continuations only; no token-mismatch floors.
    if not prev['trajectory_success'] or prev.get('token_mse') is None or nxt.get('token_mse') is None:continue
    seed=prev.get('seed');ss=prev['S_coordinate_mse'];sv=ss[str(seed)] if seed in (42,43,44) else float(np.mean(list(ss.values())))
    condition=prev.get('group',kind);setting=str(prev.get('checkpoint',prev.get('lambda_',0)))
    lag.append(dict(kind=kind,condition=condition,setting=setting,seed=seed,world_id=prev['world_id'],template=prev['template'],path=prev['path'],next_step=nxt['step'],entering_token_mse=prev['token_mse'],entering_S_mse=sv,next_success=nxt['output']['score']['success']))
 write('results/lagged_continuation.jsonl',lag);dump('results/existing_input_counts.json',dict(step_records=counts,eligible_lagged=len(lag),total_original_archive_records=308640))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axs=plt.subplots(2,2,figsize=(11,8),sharey=True);fitsout=[];binsout=[]
 for t in (0,3):
  rs=[r for r in lag if r['template']==t];y=np.array([r['next_success'] for r in rs],float);fold=np.array([int(hashlib.sha256(r['world_id'].encode()).hexdigest(),16)%2 for r in rs]);cond=np.array([r['condition'] for r in rs]);uniq=sorted(set(cond))
  for j,metric in enumerate(('entering_token_mse','entering_S_mse')):
   x=np.log10(np.maximum([r[metric] for r in rs],1e-12));ax=axs[0 if t==0 else 1,j]
   cn={v:int(sum((fold==0)&(cond==v))) for v in uniq};weights=np.array([1/cn[v] if cn[v] else 0 for v in cond]);train=fold==0;test=fold==1;b=logistic(x[train],y[train],weights[train]);pred=1/(1+np.exp(-np.clip(b[0]+b[1]*x[test],-35,35)))
   overall=dict(template=t,metric=metric,fit_worlds=len(set(r['world_id'] for r,f in zip(rs,fold) if f==0)),test_worlds=len(set(r['world_id'] for r,f in zip(rs,fold) if f==1)),fit_weighting='equal total weight per condition, within condition per eligible record',intercept=float(b[0]),slope=float(b[1]),threshold_50=float(10**(-b[0]/b[1])) if b[1] else None,test_auc_failure=auc(1-y[test],1-pred),test_brier=float(np.mean((pred-y[test])**2)),by_condition=[])
   for ci,v in enumerate(uniq):
    ix=(cond==v)&test;xx=x[ix];yy=y[ix];pp=1/(1+np.exp(-np.clip(b[0]+b[1]*xx,-35,35)))
    if len(xx):overall['by_condition'].append(dict(condition=v,n=len(xx),observed_success=float(yy.mean()),predicted_success=float(pp.mean()),brier=float(np.mean((pp-yy)**2)),failure_auc=auc(1-yy,1-pp)))
    # Points retain condition labels, with world-cluster bootstrap intervals.
    edges=np.linspace(float(x.min())-.001,float(x.max())+.001,13)
    for a,z in zip(edges[:-1],edges[1:]):
     ii=np.where(ix&(x>=a)&(x<z))[0]
     if len(ii)<10:continue
     wv=defaultdict(list)
     for i in ii:wv[rs[i]['world_id']].append(y[i])
     ci95=old.bootstrap_mean([np.mean(vv) for vv in wv.values()]);mu=float(y[ii].mean());xm=float(x[ii].mean());ax.plot(10**xm,mu,'o',color=f'C{ci}',label=v if a==edges[0] else None,ms=4,alpha=.75)
     binsout.append(dict(template=t,metric=metric,condition=v,x=10**xm,n=len(ii),worlds=len(wv),success=mu,ci95_equal_world_weighted=ci95))
   grid=np.linspace(x.min(),x.max(),200);ax.plot(10**grid,1/(1+np.exp(-np.clip(b[0]+b[1]*grid,-35,35))),'k--',lw=1.5);ax.set_xscale('log');ax.set_ylim(-.03,1.03);ax.set_title(f'Template {t}: {metric}');ax.set_ylabel('Next success | prefix correct');ax.set_xlabel('Residual entering next edit');fitsout.append(overall)
 from matplotlib.lines import Line2D
 fig.legend([Line2D([0],[0],marker='o',ls='',color=f'C{i}') for i in range(len(uniq))],uniq,loc='lower center',ncol=7);fig.tight_layout(rect=(0,.04,1,1));fig.savefig(ROOT/'results/continuation_risk.svg');fig.savefig(ROOT/'results/continuation_risk.png',dpi=160);plt.close(fig)
 dump('results/continuation_risk_models.json',fitsout);dump('results/continuation_risk_bins.json',binsout)
 # Leave an entire family out as a portability check; no evaluation labels used in fit.
 loo=[]
 for t in (0,3):
  rs=[r for r in lag if r['template']==t];cond=np.array([r['condition'] for r in rs]);y=np.array([r['next_success'] for r in rs],float);fold=np.array([int(hashlib.sha256(r['world_id'].encode()).hexdigest(),16)%2 for r in rs])
  for metric in ('entering_token_mse','entering_S_mse'):
   x=np.log10(np.maximum([r[metric] for r in rs],1e-12))
   for v in sorted(set(cond)):
    tr=(cond!=v)&(fold==0);te=(cond==v)&(fold==1);cn={q:int(sum(tr&(cond==q))) for q in set(cond)};weights=np.array([1/max(1,cn[q]) for q in cond]);b=logistic(x[tr],y[tr],weights[tr]);pp=1/(1+np.exp(-np.clip(b[0]+b[1]*x[te],-35,35)));loo.append(dict(template=t,metric=metric,held_family=v,n=int(te.sum()),observed=float(y[te].mean()),predicted=float(pp.mean()),brier=float(np.mean((pp-y[te])**2)),failure_auc=auc(1-y[te],1-pp)))
 dump('results/continuation_leave_family_out.json',loo)
def grouped(rs,keys):
 d=defaultdict(list)
 for r in rs:d[tuple(r[k] for k in keys)].append(r)
 return d
if __name__=='__main__':main()
