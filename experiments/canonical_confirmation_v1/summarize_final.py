"""Derived, complete per-seed tables with worlds as independent units."""
from futils import *
def grouped(rs,keys):
 d=defaultdict(list)
 for r in rs:d[tuple(r[k] for k in keys)].append(r)
 return d
def main():
 single=rows(ROOT/'results/fresh_single.jsonl');chain=rows(ROOT/'results/fresh_chain.jsonl');closure=rows(ROOT/'results/fresh_closure.jsonl');mech=rows(ROOT/'results/fresh_mechanism.jsonl');render=old.semantics()[0];worldmap={d:{w['world_id']:w for w in ws(d)} for d in ('time','person')};index={d:{w['world_id']:i for i,w in enumerate(ws(d))} for d in ('time','person')};supported={d:{(s,op) for op,rr in items(d).items() for _,s,_ in rr} for d in ('time','person')}
 for r in single:
  i=index[r['domain']][r['world_id']];am=cache(r['domain'],'eval',r['template'],r['source_state'])['m'][i];bm=cache(r['domain'],'eval',r['template'],r['target_state'])['m'][i];n=max(len(am),len(bm));r['_input_target_mask_aligned']=torch.equal(torch.nn.functional.pad(am,(0,n-len(am))),torch.nn.functional.pad(bm,(0,n-len(bm))))
 cs=[];prefix={tuple(r[k] for k in ('domain','group','seed','checkpoint','template','path','world_id','step')):r['trajectory_success'] for r in chain}
 chain_groups=grouped(chain,['domain','group','seed','checkpoint','template','path','step'])
 for keys,rs in chain_groups.items():
  a=dict(zip(['domain','group','seed','checkpoint','template','path','step'],keys));a['trajectory']=old.rate([r['trajectory_success'] for r in rs]);a['current']=old.rate([r['output']['score']['success'] for r in rs]);a['preserved']=old.rate([r['output']['score']['preserved'] for r in rs]);a['current_exact']=old.rate([r['output']['text']==render(worldmap[r['domain']][r['world_id']],r['state'],r['template']) for r in rs]);vals=[r['token_mse'] for r in rs if r['token_mse'] is not None];a['token_mse']=dict(mean=float(np.mean(vals)),ci95=old.bootstrap_mean(vals)) if vals else None;cs.append(a)
 for a in cs:
  rr=chain_groups[tuple(a[k] for k in ('domain','group','seed','checkpoint','template','path','step'))]
  entered=[r for r in rr if r['step']==1 or prefix[tuple(r[k] for k in ('domain','group','seed','checkpoint','template','path','world_id'))+(r['step']-1,)]]
  a['conditional_continuation']=old.rate([r['output']['score']['success'] for r in entered])
 dump('results/fresh_chain_summary.json',cs)
 cells=[]
 for key,rs in grouped(single,['domain','group','seed','checkpoint','template','source_state','operation']).items():
  cells.append(dict(zip(['domain','group','seed','checkpoint','template','source_state','operation'],key),success=old.rate([r['output']['score']['success'] for r in rs]),exact=old.rate([r['output']['text']==render(worldmap[r['domain']][r['world_id']],r['target_state'],r['template']) for r in rs]),preserved=old.rate([r['output']['score']['preserved'] for r in rs]),aligned_input_target_n=sum(r['_input_target_mask_aligned'] for r in rs),train_supported=(key[5],key[6]) in supported[key[0]]))
 dump('results/fresh_single_cells.json',cells)
 ss=[]
 for key,rs in grouped(single,['domain','group','seed','checkpoint','template']).items():
  for scope in ('all_legal','mask_aligned','train_supported'):
   rr=rs if scope=='all_legal' else [r for r in rs if r['_input_target_mask_aligned']] if scope=='mask_aligned' else [r for r in rs if (r['source_state'],r['operation']) in supported[r['domain']]];ww=grouped(rr,['world_id']);metrics={}
   for name in ('success','target','preserved','scope','parseable','grammar'):
    vals=[np.mean([r['output']['score'][name] for r in one]) for one in ww.values()];metrics[name]=dict(mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals),all_edges=old.rate([all(r['output']['score'][name] for r in one) for one in ww.values()])) if vals else None
   vals=[np.mean([r['token_mse'] for r in one if r['token_mse'] is not None]) for one in ww.values() if any(r['token_mse'] is not None for r in one)];metrics['token_mse']=dict(mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals)) if vals else None
   sm={}
   for seed in SEEDS:
    vals=[np.mean([r['S_coordinate_mse'][str(seed)] for r in one if r['S_coordinate_mse'] is not None]) for one in ww.values() if any(r['S_coordinate_mse'] is not None for r in one)];sm[str(seed)]=dict(mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals)) if vals else None
   ss.append(dict(zip(['domain','group','seed','checkpoint','template'],key),scope=scope,worlds=len(ww),observations=len(rr),metrics=metrics,S_coordinates=sm))
 dump('results/fresh_single_summary.json',ss)
 cl=[]
 for key,rs in grouped(closure,['group','seed','template','path','step']).items():
  if key[-1] not in (1,5,10,20,50):continue
  vals=[r['token_mse'] for r in rs];cl.append(dict(zip(['group','seed','template','path','step'],key),trajectory=old.rate([r['trajectory_success'] for r in rs]),current=old.rate([r['output']['score']['success'] for r in rs]),token_mse=dict(mean=float(np.mean(vals)),ci95=old.bootstrap_mean(vals))))
 dump('results/fresh_closure_summary.json',cl)
 ms=[]
 for key,rs in grouped(mech,['seed','template','kind','component']).items():
  eligible=[r for r in rs if r['eligible']];current=[r for r in eligible if r['current']['score']['success']];exact=[r for r in eligible if r['current']['text']==render(worldmap['time'][r['world_id']],0,r['template'])];ms.append(dict(zip(['seed','template','kind','component'],key),total=len(rs),eligible=len(eligible),current_retention=old.rate([r['current']['score']['success'] for r in eligible]),current_exact_retention=old.rate([r in exact for r in eligible]),paired_success=old.rate([r['current']['score']['success'] and r['next']['score']['success'] for r in eligible]),next_failure_given_current=old.rate([not r['next']['score']['success'] for r in current]),next_failure_given_current_exact=old.rate([not r['next']['score']['success'] for r in exact]),current_correct_next_failed=old.rate([r['current']['score']['success'] and not r['next']['score']['success'] for r in eligible]),mean_delta_norm=float(np.mean([r['delta_norm'] for r in rs]))))
 dump('results/fresh_mechanism_summary.json',ms)
 visibility=[]
 for key,rs in grouped([r for r in mech if r['kind']=='repair' and r['component']=='none'],['seed','template']).items():
  eligible=[r for r in rs if r['eligible']];visibility.append(dict(seed=key[0],template=key[1],eligible=len(eligible),**{n:dict(mean=float(np.mean([r[n] for r in eligible])),ci95_world_bootstrap=old.bootstrap_mean([r[n] for r in eligible])) if eligible else None for n in ('KL_pre_S_perp','KL_post_S_perp')}))
 dump('results/fresh_visibility.json',visibility)
 pca=[];angles=[]
 for domain,seeds in [('time',SEEDS),('person',(42,43,44))]:
  for g in ('C1','C3','C4'):
   qq={}
   for seed in seeds:
    f=load(ROOT/f'local/pca_{domain}_{g}_s{seed}.pt');qq[seed]=f['q'].double();pca.append(dict(domain=domain,group=g,seed=seed,**{n:f[n] for n in ('n','energy','centered_energy','top4_fraction','eigengap4','relative_gap4')}))
   for a in seeds:
    for b in seeds:
     if a>=b:continue
     sv=torch.linalg.svdvals(qq[a].T@qq[b]).clamp(0,1);aa=torch.rad2deg(torch.acos(sv));angles.append(dict(domain=domain,group=g,seed_a=a,seed_b=b,angles_degrees=aa.tolist(),mean_cos2=float(sv.square().mean())))
 dump('results/fresh_pca.json',pca);dump('results/fresh_cross_seed_angles.json',angles)
 # First failed output once per complete trajectory, not every downstream step.
 failure=[]
 for key,rs in grouped(chain,['domain','group','seed','checkpoint','template','path','world_id']).items():
  r=next((r for r in sorted(rs,key=lambda z:z['step']) if not r['trajectory_success']),None)
  if r is None:continue
  score=r['output']['score'];category='unparseable' if not score['parseable'] else 'grammar' if not score['grammar'] else 'non_target' if not score['preserved'] else 'target_state' if not score['target'] else 'scope_or_end'
  failure.append(dict(domain=r['domain'],group=r['group'],seed=r['seed'],checkpoint=r['checkpoint'],template=r['template'],path=r['path'],world_id=r['world_id'],first_failure_step=r['step'],category=category))
 fd=[]
 for key,rs in grouped(failure,['domain','group','seed','checkpoint','template']).items():
  fd.append(dict(zip(['domain','group','seed','checkpoint','template'],key),failed_trajectories=len(rs),categories={v:sum(r['category']==v for r in rs) for v in sorted(set(r['category'] for r in rs))}))
 dump('results/fresh_first_failure_categories.json',fd)
 admitted=[]
 for key,rs in grouped([r for r in failure if r['path']!='original_reordered'],['domain','group','seed','checkpoint','template']).items():
  admitted.append(dict(zip(['domain','group','seed','checkpoint','template'],key),failed_trajectories=len(rs),categories={v:sum(r['category']==v for r in rs) for v in sorted(set(r['category'] for r in rs))},scope='All predeclared paths except time original_reordered; person template3 still has single-step floors'))
 dump('results/fresh_aligned_first_failure_categories.json',admitted)
 # Prospectively locked C4 checkpoints: plot every depth, no inferred collapse time.
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axs=plt.subplots(2,5,figsize=(16,6),sharey=True,sharex=True)
 for i,t in enumerate((0,3)):
  for j,seed in enumerate(SEEDS):
   ax=axs[i,j]
   for k in range(1,6):
    rr=sorted([r for r in cs if r['domain']=='time' and r['group']=='C4' and r['seed']==seed and r['template']==t and r['path']=='aligned_from_plus_one' and r['step']==k],key=lambda r:r['checkpoint']);ax.plot([r['checkpoint'] for r in rr],[r['trajectory']['rate'] for r in rr],'-o',ms=3,label=f'R{k}')
   ax.set_title(f'T{t}, seed{seed}');ax.set_ylim(-.03,1.03);ax.set_xticks(CKS);ax.tick_params(axis='x',labelrotation=45);ax.set_xlabel('AdamW updates')
 axs[0,0].legend(fontsize=8);axs[0,0].set_ylabel('Complete prefix success');axs[1,0].set_ylabel('Complete prefix success');fig.tight_layout();fig.savefig(ROOT/'results/fresh_C4_depths.svg');fig.savefig(ROOT/'results/fresh_C4_depths.png',dpi=160)
 dump('results/summary_complete.json',dict(raw_counts=dict(single=len(single),chain=len(chain),closure=len(closure),mechanism=len(mech))))
 likelihood=[]
 for key,rs in grouped(rows(ROOT/'results/historical_c4_fixed_likelihood.jsonl'),['seed','checkpoint','template']).items():
  wm=grouped(rs,['world_id']);metrics={}
  for name in ('nll','canonical_nll','token_mse'):
   vals=[float(np.mean([r[name] for r in one])) for one in wm.values()];metrics[name]=dict(mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals))
  likelihood.append(dict(seed=key[0],checkpoint=key[1],template=key[2],worlds=len(wm),**metrics))
 dump('results/historical_c4_likelihood_summary.json',likelihood)
if __name__=='__main__':main()
