"""Editor-level composability, basin AUC, descriptive association, and plots."""
import collections,csv,json,math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from g10_common import *
CFG=json.loads((ROOT/'config.json').read_text())
DIRECTIONS=CFG['directions'];GRID=CFG['alpha_grid']

def area(points):
 x=np.array([0.]+[float(a) for a in GRID]);y=np.array([0.]+[1-float(points[a]) for a in GRID]);return float(np.trapezoid(y,x)/2.)
def ci_mean(v,rng):
 v=np.asarray(v,float);draw=rng.choice(v,size=(CFG['bootstrap_replicates'],len(v)),replace=True).mean(1)
 return [float(np.quantile(draw,.025)),float(np.quantile(draw,.975))]
def write_json(path,obj):dump(path,obj)

def main():
 gate=json.loads((ROOT/'evaluation/gate_lock.json').read_text());retained=set(gate['matched_editors']);all_ids=[f'rank{r}_seed{s}' for r in CFG['ranks'] for s in CFG['seeds']]
 trajectories={i:read(f'outputs/trajectory_{i}.jsonl') for i in all_ids}
 trainmeta={i:json.loads((ROOT/f'checkpoints/rank{int(i.split("_")[0][4:])}/{i}.json').read_text()) for i in all_ids}
 comparison=[];raw=[];rng=np.random.default_rng(CFG['bootstrap_seed']);test_sets=['composition_iid','composition_template_ood']
 for ident in all_ids:
  rr=trajectories[ident]
  for split in test_sets:
   sub=[x for x in rr if x['split']==split];nworld=80
   by=collections.defaultdict(dict)
   for x in sub:by[x['record_id']][x['step']]=x
   for rid,steps in by.items():
    for k,v in steps.items():raw.append(dict(editor=ident,split=split,record_id=rid,step=k,joint_ok=v['score']['joint_ok'],date_ok=v['score']['date_ok'],person_ok=v['score']['perspective_ok'],nondate_facts_ok=v['score']['nondate_facts_ok'],parse_unresolved=v['score']['parse_unresolved'],normal_end=v['normal_end'],parsed_nondate_error=v['score']['parsed_nondate_error'],decoded_text=v['output'],gold_text=v['gold_text'],pooled_l2=v['pooled_l2'],token_l2=v['token_l2'],residual_norm=v['residual_norm'],residual_previous_cosine=v['residual_previous_cosine']))
   if not sub:continue
   maxstep=max(len(x) for x in by.values());step_counts={k:sum(by[r][k]['score']['joint_ok'] for r in by if k in by[r]) if k<=maxstep else None for k in range(1,6)}
   firstfail=[]
   if ident in retained:
    for steps in by.values():firstfail.append(next((k for k in range(1,6) if not steps[k]['score']['joint_ok']),6))
   horizon={k:sum(all(by[r][j]['score']['joint_ok'] for j in range(1,k+1)) for r in by)/nworld for k in (1,2,3,4,5) if k<=maxstep}
   ep35=float(np.mean([step_counts[k]/nworld for k in (3,4,5)])) if ident in retained else None
   row=dict(editor=ident,rank=trainmeta[ident]['rank'],seed=trainmeta[ident]['seed'],split=split,gate_pass=ident in retained,N=nworld,
      step1_success=step_counts[1],step1_rate=step_counts[1]/nworld,step2_success=step_counts[2],step2_rate=step_counts[2]/nworld if step_counts[2] is not None else None,
      step3_success=step_counts[3],step3_rate=step_counts[3]/nworld if step_counts[3] is not None else None,step4_success=step_counts[4],step4_rate=step_counts[4]/nworld if step_counts[4] is not None else None,
      step5_success=step_counts[5],step5_rate=step_counts[5]/nworld if step_counts[5] is not None else None,steps3to5_endpoint_mean=ep35,
      trajectory_through_3=sum(all(by[r][j]['score']['joint_ok'] for j in range(1,4)) for r in by) if maxstep>=3 else None,
      trajectory_through_5=sum(all(by[r][j]['score']['joint_ok'] for j in range(1,6)) for r in by) if maxstep>=5 else None,
      mean_first_failure_step=float(np.mean(firstfail)) if firstfail else None,first_fail_none=sum(k==6 for k in firstfail) if firstfail else None,
      unresolved=sum(x['score']['parse_unresolved'] for x in sub),confirmed_nondate_errors=sum(x['score']['parsed_nondate_error'] for x in sub),
      confirmed_date_errors=sum(x['score']['parsed_date_error'] for x in sub),normal_end=sum(x['normal_end'] for x in sub),
      train_updates=trainmeta[ident]['updates'],supervised_samples=trainmeta[ident]['counts']['supervised_samples'],supervision_tokens=trainmeta[ident]['counts']['supervision_tokens'],
      parameters=trainmeta[ident]['parameters'],checkpoint_sha256=trainmeta[ident]['checkpoint_sha256'])
   row['trajectory_through_3_rate']=row['trajectory_through_3']/nworld if row['trajectory_through_3'] is not None else None;row['trajectory_through_5_rate']=row['trajectory_through_5']/nworld if row['trajectory_through_5'] is not None else None
   row['steps3to5_ci95']=ci_mean([np.mean([by[r][k]['score']['joint_ok'] for k in (3,4,5)]) for r in by],rng) if ident in retained else None
   comparison.append(row)
 csvwrite('evaluation/per_editor_composition.csv',comparison);csvwrite('evaluation/per_step_raw.csv',raw)
 geometry=[]
 for ident in all_ids:
  for split in test_sets:
   for step in range(1,6):
    vals=[x for x in raw if x['editor']==ident and x['split']==split and x['step']==step]
    if vals:
     row=dict(editor=ident,split=split,step=step,N=len(vals),pooled_l2='',token_l2='',residual_norm='',residual_previous_cosine='')
     for k in ['pooled_l2','token_l2','residual_norm','residual_previous_cosine']:
      present=[v[k] for v in vals if v[k] is not None]
      if present:row[k]=float(np.mean(present))
     geometry.append(row)
 csvwrite('evaluation/geometry_summary.csv',geometry)

 states={};scans={}
 for ident in retained:
  states[ident]=read(f'basin/states_{ident}.jsonl');scans[ident]=read(f'basin/scan_{ident}.jsonl')
 bystate=collections.defaultdict(list)
 for ident,rows in scans.items():
  for x in rows:bystate[ident,x['split'],x['world_id'],x['step']].append(x)
 auc_rows=[]
 for ident,rows in states.items():
  for st in rows:
   pts=bystate[ident,st['split'],st['world_id'],st['step']];coarse={}
   for d in DIRECTIONS:
    coarse[d]={float(x['alpha']):x for x in pts if x['direction']==d and float(x['alpha']) in GRID}
   vals={d:area({a:coarse[d][a]['content_compatible'] for a in GRID}) for d in DIRECTIONS}
   corridor={d:area({a:coarse[d][a]['corridor_success'] for a in GRID}) for d in DIRECTIONS}
   auc_rows.append(dict(editor=ident,split=st['split'],record_id=st['world_id'],step=st['step'],
      **{f'{d}_content_failure_area':vals[d] for d in DIRECTIONS},
      **{f'{d}_corridor_failure_area':corridor[d] for d in DIRECTIONS},
      random_control_mean=(vals['radial_orthogonal_random']+vals['editor_orthogonal_random'])/2,
      excess_forward_failure_area=vals['editor_forward']-(vals['radial_orthogonal_random']+vals['editor_orthogonal_random'])/2))
 csvwrite('evaluation/auc_by_state.csv',auc_rows)

 basin_summary=[];curve=[];radius=[]
 for ident in retained:
  allscan=scans[ident];allstates=states[ident]
  for split in test_sets:
   for step in range(1,5):
    ss=[x for x in auc_rows if x['editor']==ident and x['split']==split and x['step']==step]
    if not ss:continue
    agg={k:float(np.mean([x[k] for x in ss])) for k in ss[0] if k.endswith('_content_failure_area') or k.endswith('_corridor_failure_area') or k=='excess_forward_failure_area' or k=='random_control_mean'}
    basin_summary.append(dict(editor=ident,split=split,step=step,N=len(ss),**agg))
    stateids={(x['split'],x['world_id'],x['step']) for x in allstates if x['split']==split and x['step']==step}
    for d in DIRECTIONS:
     for alpha in GRID:
      v=[x for x in allscan if x['split']==split and x['step']==step and x['direction']==d and float(x['alpha'])==alpha]
      if v:curve.append(dict(editor=ident,split=split,step=step,direction=d,alpha=alpha,N=len(v),
        content_success_pct=100*np.mean([x['content_compatible'] for x in v]),corridor_success_pct=100*np.mean([x['corridor_success'] for x in v]),
        next_gold_success_pct=100*np.mean([x['next_gold_success'] for x in v]),fact_preservation_pct=100*np.mean([x['fact_preservation'] for x in v])))
    for key in sorted(stateids):
     for d in DIRECTIONS:
      v=[x for x in allscan if (x['split'],x['world_id'],x['step'])==key and x['direction']==d]
      failed=[float(x['alpha']) for x in v if not x['corridor_success']]
      radius.append(dict(editor=ident,split=split,world_id=key[1],step=step,direction=d,
         first_failed_alpha=min(failed) if failed else None,censored_at_2=not bool(failed),n_samples=len(v)))
 csvwrite('evaluation/fragility_summary.csv',basin_summary);csvwrite('evaluation/success_vs_alpha.csv',curve);csvwrite('evaluation/first_failure_radius.csv',radius)

 # Editor-level association over IID+OOD combined; each editor is one point.
 editor_metrics=[]
 for ident in retained:
  rr=[x for x in comparison if x['editor']==ident];combined={}
  combined['step1_rate']=float(np.mean([x['step1_rate'] for x in rr]));combined['steps3to5_endpoint_mean']=float(np.mean([x['steps3to5_endpoint_mean'] for x in rr]))
  combined['mean_first_failure_step']=float(np.mean([x['mean_first_failure_step'] for x in rr]))
  for step in [1,2]:
   f=[x['excess_forward_failure_area'] for x in basin_summary if x['editor']==ident and x['split'] in test_sets and x['step']==step]
   combined[f'excess_fragility_step{step}']=float(np.mean(f))
  identparts=ident.split('_');combined.update(editor=ident,rank=int(identparts[0][4:]),seed=int(identparts[1][4:]))
  editor_metrics.append(combined)
 csvwrite('evaluation/editor_association_raw.csv',editor_metrics)
 assoc=[];rho_boot=[]
 for split in ['combined']+test_sets:
  select=[x for x in comparison if x['editor'] in retained and (split=='combined' or x['split']==split)]
  for outcome in ['steps3to5_endpoint_mean','mean_first_failure_step']:
   xx=[];yy=[];ids=[]
   for ident in sorted(retained):
    ers=[x for x in select if x['editor']==ident]
    if not ers:continue
    fr=[x['excess_fragility_step1'] for x in editor_metrics if x['editor']==ident][0]
    xx.append(fr);yy.append(float(np.mean([r[outcome] for r in ers])));ids.append(ident)
   rho,p=(float(spearmanr(xx,yy).statistic),float(spearmanr(xx,yy).pvalue)) if len(set(xx))>1 and len(set(yy))>1 else (None,None)
   # Descriptive linear model: fragility, observed one-step rate, numeric rank, numeric seed.
   X=np.array([[1.,xx[i],float(np.mean([r['step1_rate'] for r in select if r['editor']==ids[i]])),float(editor_metrics[[z['editor'] for z in editor_metrics].index(ids[i])]['rank']),float(editor_metrics[[z['editor'] for z in editor_metrics].index(ids[i])]['seed'])] for i in range(len(ids))]);y=np.array(yy)
   beta=np.linalg.lstsq(X,y,rcond=None)[0] if len(X) else np.array([]);pred=X@beta if len(X) else np.array([])
   assoc.append(dict(split=split,outcome=outcome,n_editors=len(ids),spearman_rho=rho,nominal_two_sided_p=p,
      ols_terms=['intercept','excess_fragility_step1','single_step_rate','rank_numeric','seed_numeric'],ols_coefficients=beta.tolist(),ols_r2=float(1-np.sum((y-pred)**2)/np.sum((y-y.mean())**2)) if len(y)>1 and np.sum((y-y.mean())**2)>0 else None,
      editors=ids,fragility=xx,outcome_values=yy,interpretation='exploratory; editor-level n is at most nine; p is descriptive and does not cover training randomness'))
  if split!='combined':continue
  # World-cluster paired bootstrap of Spearman: same sampled IID/OOD worlds for every editor.
  byid={x['editor']:x for x in editor_metrics};split_rows={i:{x['split']:x for x in comparison if x['editor']==i} for i in retained}
  worlds={s:sorted({x['record_id'] for x in trajectories[sorted(retained)[0]] if x['split']==s and x['step']==1}) for s in test_sets}
  draws=[]
  for _ in range(CFG['bootstrap_replicates']):
   outcomev=[];fragv=[]
   for ident in sorted(retained):
    ys=[];fs=[]
    for s in test_sets:
     ids0=rng.choice(worlds[s],size=len(worlds[s]),replace=True)
     lookup={(x['record_id'],x['step']):x for x in trajectories[ident] if x['split']==s}
     ys.append(float(np.mean([np.mean([lookup[r,k]['score']['joint_ok'] for k in (3,4,5)]) for r in ids0])))
     aa=[x['excess_forward_failure_area'] for x in auc_rows if x['editor']==ident and x['split']==s and x['step']==1];alook={x['record_id']:x['excess_forward_failure_area'] for x in auc_rows if x['editor']==ident and x['split']==s and x['step']==1}
     fs.append(float(np.mean([alook[r] for r in ids0 if r in alook])))
    outcomev.append(float(np.mean(ys)));fragv.append(float(np.mean(fs)))
   if len(set(fragv))>1 and len(set(outcomev))>1:draws.append(float(spearmanr(fragv,outcomev).statistic))
  rho_ci=[float(np.quantile(draws,.025)),float(np.quantile(draws,.975))] if draws else [None,None]
  rho_boot.append(dict(split='combined',metric='step1_excess_fragility_vs_steps3to5_success',n_world_bootstrap=len(draws),ci95=rho_ci,world_sampling_only=True,training_randomness_included=False))
 csvwrite('evaluation/association.csv',assoc);write_json('evaluation/association_world_bootstrap.json',rho_boot)
 # Cases: choose lowest/highest excess fragility among retained, with actual full trajectory outputs.
 ordered=sorted(editor_metrics,key=lambda r:r['steps3to5_endpoint_mean']);cases=[]
 for label,ident in [('least_stable_3to5',ordered[0]['editor']),('most_stable_3to5',ordered[-1]['editor'])]:
  candidate=next((x for x in trajectories[ident] if x['split']=='composition_iid' and x['step']==1),None)
  if candidate:
   rid=candidate['record_id'];cases.append(dict(label=label,editor=ident,steps3to5_endpoint_mean=next(x['steps3to5_endpoint_mean'] for x in editor_metrics if x['editor']==ident),fragility=next(x['excess_fragility_step1'] for x in editor_metrics if x['editor']==ident),trajectory=[x for x in trajectories[ident] if x['record_id']==rid],
      basin=[x for x in scans[ident] if x['world_id']==rid and x['step']==1]))
 write_json('review/stable_unstable_trajectories.json',cases)
 try:
  import matplotlib
  matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axs=plt.subplots(1,2,figsize=(13,5))
  colors=plt.cm.tab10(np.linspace(0,1,max(1,len(retained))))
  for color,ident in zip(colors,sorted(retained)):
   for ax,split in zip(axs,test_sets):
    vals=[x for x in curve if x['editor']==ident and x['split']==split and x['step']==1 and x['direction']=='editor_forward']
    ax.plot([x['alpha'] for x in vals],[x['content_success_pct'] for x in vals],marker='o',color=color,label=ident)
    ax.set(title=split,xlabel='alpha (next-editor residual norm units)',ylabel='content/structure success (%)',ylim=(-3,103));ax.grid(alpha=.25)
  axs[-1].legend(fontsize=7,loc='lower left');fig.tight_layout();fig.savefig(ROOT/'evaluation/success_vs_alpha.svg');plt.close(fig)
  fig,ax=plt.subplots(figsize=(7,5))
  for x in editor_metrics:ax.scatter(x['excess_fragility_step1'],x['steps3to5_endpoint_mean'],label=x['editor'])
  ax.set(xlabel='step-1 forward excess content failure area',ylabel='step 3–5 endpoint success (mean)',title='G10 editor-level association');ax.grid(alpha=.25);ax.legend(fontsize=7);fig.tight_layout();fig.savefig(ROOT/'evaluation/fragility_vs_horizon.svg');plt.close(fig)
 except ImportError:
  # Dependency-free SVG fallback: preserve the requested curves on lean cluster envs.
  import html
  ids=sorted(retained);colors=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#17becf']
  W,H=1120,520;parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>']
  for pi,split in enumerate(test_sets):
   x0=75+pi*540;y0=430;pw=440;ph=340
   parts += [f'<text x="{x0+pw/2}" y="42" text-anchor="middle" font-size="18">{split}</text>']
   for pct0 in [0,25,50,75,100]:
    y=y0-ph*pct0/100;parts += [f'<line x1="{x0}" y1="{y}" x2="{x0+pw}" y2="{y}" stroke="#ddd"/><text x="{x0-10}" y="{y+4}" text-anchor="end" font-size="11">{pct0}</text>']
   for alpha in GRID:
    x=x0+pw*float(alpha)/2;parts += [f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0-ph}" stroke="#eee"/><text x="{x}" y="{y0+18}" text-anchor="middle" font-size="11">{alpha}</text>']
   for ci,ident in enumerate(ids):
    vv=[x for x in curve if x['editor']==ident and x['split']==split and x['step']==1 and x['direction']=='editor_forward']
    pts=' '.join(f"{x0+pw*float(v['alpha'])/2:.1f},{y0-ph*float(v['content_success_pct'])/100:.1f}" for v in vv)
    parts += [f'<polyline points="{pts}" fill="none" stroke="{colors[ci%len(colors)]}" stroke-width="2"/>']
   parts += [f'<text x="{x0+pw/2}" y="{y0+42}" text-anchor="middle" font-size="13">alpha (editor residual norm units)</text>',f'<text x="{x0-48}" y="{y0-ph/2}" transform="rotate(-90 {x0-48} {y0-ph/2})" text-anchor="middle" font-size="13">content/structure success (%)</text>']
  for ci,ident in enumerate(ids):parts += [f'<text x="80" y="490" font-size="11" fill="{colors[ci%len(colors)]}">{html.escape(ident)}</text>']
  parts += ['</svg>'];(ROOT/'evaluation/success_vs_alpha.svg').write_text(''.join(parts))
  points=[x for x in editor_metrics if x['editor'] in retained];W,H=720,500;parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>','<text x="360" y="28" text-anchor="middle" font-size="16">G10 editor-level fragility vs steps 3-5 success</text>']
  for x in points:
   xx=80+520*(x['excess_fragility_step1']+.03)/.16;yy=420-330*x['steps3to5_endpoint_mean'];parts += [f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5" fill="#1f77b4"/><text x="{xx+7:.1f}" y="{yy-6:.1f}" font-size="10">{html.escape(x["editor"])}</text>']
  parts += ['<line x1="80" y1="420" x2="600" y2="420" stroke="black"/><line x1="80" y1="90" x2="80" y2="420" stroke="black"/>','<text x="340" y="470" text-anchor="middle" font-size="12">step-1 excess forward failure area</text>','<text x="24" y="250" transform="rotate(-90 24 250)" text-anchor="middle" font-size="12">mean step 3-5 endpoint success</text>','</svg>'];(ROOT/'evaluation/fragility_vs_horizon.svg').write_text(''.join(parts))
 dump('evaluation/analysis_manifest.json',dict(retained_editors=sorted(retained),editors=len(retained),trajectory_rows=sum(map(len,trajectories.values())),basin_state_rows=sum(map(len,states.values())),basin_scan_rows=sum(map(len,scans.values())),association_editor_n=len(retained),world_bootstrap=CFG['bootstrap_replicates']))
 print('analysis complete',len(retained),'matched editors',flush=True)
if __name__=='__main__':main()
