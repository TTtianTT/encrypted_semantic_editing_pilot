"""World-clustered fixed likelihood, honest common-range loss alignment."""
from futils import *
def main():
 panel=rows(ROOT/'results/control_panel.jsonl');chain=rows(ROOT/'results/control_chain.jsonl');out=[];curves={}
 def groups(rs,keys):
  dd=defaultdict(list)
  for r in rs:dd[tuple(r[k] for k in keys)].append(r)
  return dd
 cg=groups(chain,['variant','seed','checkpoint']);pg=groups(panel,['variant','seed','checkpoint'])
 for (v,s,k),rs in sorted(pg.items()):
  world=groups(rs,['world_id']);means={name:[np.mean([r[name] for r in rr]) for rr in world.values()] for name in ('nll','canonical_nll','token_mse')};r5=[r['trajectory_success'] for r in cg[v,s,k] if r['step']==5];checked=[r for r in rs if r['output'] is not None];cw=groups(checked,['world_id']);rates={}
  for name,metric in [('atomic_first16','success'),('preserved_first16','preserved')]:
   av=[np.mean([r['output']['score'][metric] for r in one]) for one in cw.values()];rates[name]=dict(n_worlds=len(av),mean=float(np.mean(av)),ci95_world_bootstrap=old.bootstrap_mean(av),all_edges_correct=old.rate([all(r['output']['score'][metric] for r in one) for one in cw.values()]))
  rr=dict(variant=v,seed=s,checkpoint=k,worlds=len(world),**{n:dict(mean=float(np.mean(a)),ci95_world_bootstrap=old.bootstrap_mean(a)) for n,a in means.items()},R5=old.rate(r5),**rates);out.append(rr);curves.setdefault((v,s),[]).append(rr)
 dump('results/control_summary.json',out)
 match=[]
 for (v,s),rs in curves.items():
  rs.sort(key=lambda r:r['checkpoint']);n0=rs[0]['nll']['mean'];best=[];lowest=float('inf')
  for r in rs:
   if r['nll']['mean']<lowest:best.append(r);lowest=r['nll']['mean']
  for frac in (.1,.25,.5,.75,.9,.95,.98):
   target=n0*(1-frac);r0=r1=None
   for a,b in zip(best,best[1:]):
    if a['nll']['mean']>=target>=b['nll']['mean']:r0,r1=a,b;break
   if r0 is None:match.append(dict(variant=v,seed=s,CE_reduction_fraction=frac,attained=False));continue
   weight=(r0['nll']['mean']-target)/(r0['nll']['mean']-r1['nll']['mean']);match.append(dict(variant=v,seed=s,CE_reduction_fraction=frac,attained=True,bracket_checkpoints=[r0['checkpoint'],r1['checkpoint']],interpolation_weight=weight,token_mse_interpolated=(1-weight)*r0['token_mse']['mean']+weight*r1['token_mse']['mean'],R5_interpolated=(1-weight)*r0['R5']['rate']+weight*r1['R5']['rate'],caution='Linear interpolation between measured checkpoints, not a measured intermediate model; see endpoint rates'))
 dump('results/matched_CE_reduction.json',match)
 grad=rows(ROOT/'results/hidden_gradients.jsonl');gs=[]
 for name in ('gradient_norm','cos_gradient_ideal','cos_descent_ideal','cos_descent_residual'):
  vals=[np.mean([r[name] for r in rr]) for rr in groups(grad,['world_id']).values()];gs.append(dict(metric=name,mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals)))
 for s in (42,43,44):
  for name in ('S_gradient_energy_fraction','ideal_S_energy_fraction'):
   vals=[np.mean([r[name][str(s)] for r in rr]) for rr in groups(grad,['world_id']).values()];gs.append(dict(metric=name,seed=s,mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals),mean_subspace_angle_degrees=float(np.mean([np.degrees(np.arccos(np.sqrt(np.clip(r[name][str(s)],0,1)))) for r in grad]))))
 dump('results/hidden_gradient_summary.json',gs)
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axs=plt.subplots(2,3,figsize=(12,7),sharex=True)
 variants=['adam_1e3','adam_1e4','sgd_1','sgd_10']
 for j,s in enumerate((42,43,44)):
  for i,v in enumerate(variants):
   rs=sorted(curves[v,s],key=lambda r:r['checkpoint']);n0=rs[0]['nll']['mean'];x=[r['nll']['mean']/n0 for r in rs];axs[0,j].plot(x,[r['token_mse']['mean'] for r in rs],'-o',color=f'C{i}',ms=3,label=v);axs[1,j].plot(x,[r['R5']['rate'] for r in rs],'-o',color=f'C{i}',ms=3)
  axs[0,j].set_title(f'Seed{s}');axs[0,j].set_yscale('log');axs[1,j].set_ylim(-.03,1.03);axs[1,j].set_xlabel('Fixed-panel CE / initial CE (smaller = better)')
  for ax in axs[:,j]:ax.set_xscale('log');ax.invert_xaxis()
 axs[0,0].set_ylabel('Token MSE');axs[1,0].set_ylabel('Aligned +1 R5');axs[0,0].legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'results/optimizer_matched_loss.svg');fig.savefig(ROOT/'results/optimizer_matched_loss.png',dpi=160)
if __name__=='__main__':main()
