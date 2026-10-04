"""Independent raw-score validation and predefined paired-world summaries on CPU."""
import csv,statistics,collections,random,math
import numpy as np
from study import *
def writecsv(path,rs):
    if not rs:return
    with path.open('w') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def percent(xs):return sum(xs)/len(xs) if xs else None
def validate(rs):
    ws=worldmap()
    for r in rs:
      assert r['score']==score(r['prediction'],r['gold'],ws[r['world_id']],r['ended']),r.get('id')
def boot(worlds):
    keys=sorted(worlds);rng=np.random.default_rng(config()['bootstrap_seed'])
    draws=rng.integers(0,len(keys),size=(config()['bootstrap_replicates'],len(keys)))
    values=np.sort(np.array([worlds[k] for k in keys])[draws].mean(axis=1))
    return float(values[int(.025*len(values))]),float(values[int(.975*len(values))])
def main():
    verify_lock();summaries=[];natural_rows=[];failure_rows=[];contrasts=[];individual={};regressions=[];prefix=[];audited=0;pending=[];quality=[];continuation_cells=[];sequence_rows=[]
    for seed in (42,43,44):
      baseline=ROOT/f'runs/preflight/s{seed}/T0'
      if not (baseline/'complete.json').exists():pending.append(dict(seed=seed,stage='T0 evaluation'));continue
      old={r['id']:r for r in rows(baseline/'old_natural.jsonl')};cohort={r['id']:r['qualified'] for r in rows(baseline/'fixed_diagnostic.jsonl')}
      jobs=[('T0',0,baseline)]+[(m,u,ROOT/f'runs/formal/s{seed}/{m}_u{u}') for m in ('N','F','R') for u in (100,200)]
      for method,u,folder in jobs:
        if not (folder/'complete.json').exists():pending.append(dict(seed=seed,condition=method,update=u));continue
        for file,template_bin in (('old_natural','iid'),('ood_natural','ood')):
          rs=rows(folder/f'{file}.jsonl');validate(rs);audited+=len(rs);cells=collections.defaultdict(list)
          for r in rs:cells[(r['state'],r['operation'])].append(r)
          macro=statistics.mean(percent([r['score']['success'] for r in group]) for group in cells.values())
          summaries.append(dict(seed=seed,condition=method,update=u,test=template_bin,source='natural',metric='atomic_macro',cohort='all',n=len(rs),k=sum(r['score']['success'] for r in rs),rate=macro,denominator=len(rs)))
          individual[(seed,method,u,template_bin,'natural','atomic_macro','all')]={r['id']:(r['world_id'],int(r['score']['success'])) for r in rs}
          for (state,op),group in cells.items():natural_rows.append(dict(seed=seed,condition=method,update=u,test=template_bin,state=state,operation=op,n=len(group),success=sum(r['score']['success'] for r in group),rate=percent([r['score']['success'] for r in group])))
          quality.append(dict(seed=seed,condition=method,update=u,test=template_bin,source='natural',cohort='natural_rows',step=1,n=len(rs),**{k:percent([r['score'][k] for r in rs]) for k in ('success','target','preserved','parseable','grammar','ended')}))
          if file=='old_natural':
            for (state,op),group in cells.items():
              lost=[r['id'] for r in group if old[r['id']]['score']['success'] and not r['score']['success']];repaired=[r['id'] for r in group if not old[r['id']]['score']['success'] and r['score']['success']]
              regressions.append(dict(seed=seed,condition=method,update=u,state=state,operation=op,n=len(group),old_success_lost=len(lost),old_failure_repaired=len(repaired),net=len(repaired)-len(lost),lost_ids=json.dumps(lost),repaired_ids=json.dumps(repaired)))
        for source in ('fixed_T0','U','self','gold_reencode','actual_reencode'):
          rs=rows(folder/f'continuation_{source}.jsonl');validate(rs);audited+=len(rs)
          for t,label in ((0,'iid'),(2,'ood')):
            group=[r for r in rs if r['template']==t]
            quality.append(dict(seed=seed,condition=method,update=u,test=label,source=source,cohort='exhaustive_two_step',step=2,n=len(group),**{k:percent([r['score'][k] for r in group]) for k in ('success','target','preserved','parseable','grammar','ended')}))
            legalcells=collections.defaultdict(list)
            for r in group:legalcells[(r['initial_state'],r['a'],r['current_state'],r['b'],r['target_state'])].append(r)
            for key,cell in sorted(legalcells.items()):
              first=sum(r['first_success'] for r in cell);full=sum(r['full2'] for r in cell)
              continuation_cells.append(dict(seed=seed,condition=method,update=u,test=label,source=source,initial_state=key[0],a=key[1],current_state=key[2],b=key[3],target_state=key[4],n=len(cell),first=first,endpoint2=sum(r['score']['success'] for r in cell),full2=full,conditional_next=None if first==0 else full/first))
            for cohortname,selected in (('all',group),('fixed_diagnostic',[r for r in group if cohort[r['id']]])):
              for metric in ('first','endpoint2','full2','conditional_next','failed_prefix_endpoint_recovery','known_wrong_relative_recovery','unresolved_prefix_endpoint_recovery'):
                ss=selected
                if metric=='conditional_next':ss=[r for r in ss if r['first_success']]
                if metric=='failed_prefix_endpoint_recovery':ss=[r for r in ss if not r['first_success']]
                if metric in ('known_wrong_relative_recovery','unresolved_prefix_endpoint_recovery'):
                  def category(r):
                    p,_=parse(r['first_prediction'],'time',r['template'],False)
                    return 'unresolved' if p is None or p.get('relative') is None else 'wrong' if p['relative']!=r['current_state'] else 'other'
                  ss=[r for r in ss if category(r)==('wrong' if metric=='known_wrong_relative_recovery' else 'unresolved')]
                values=[r['first_success'] if metric=='first' else r['full2'] if metric=='full2' else r['score']['success'] for r in ss]
                summaries.append(dict(seed=seed,condition=method,update=u,test=label,source=source,metric=metric,cohort=cohortname,n=len(selected),k=sum(values),rate=percent(values),denominator=len(values)))
                if metric in ('full2','endpoint2'):
                  individual[(seed,method,u,label,source,metric,cohortname)]={r['id']:(r['world_id'],int(v)) for r,v in zip(ss,values)}
        trajectory=[]
        for p in sorted((folder/'trajectories').glob('*.jsonl')):trajectory+=rows(p)
        validate(trajectory);audited+=len(trajectory)
        for t,label in ((0,'iid'),(2,'ood')):
          for mode in ('latent','gold_reencode','actual_reencode'):
            for step in range(1,6):
              allgroup=[r for r in trajectory if r['template']==t and r['method']==mode and r['step']==step]
              quality.append(dict(seed=seed,condition=method,update=u,test=label,source=mode,cohort='long_paths',step=step,n=len(allgroup),**{k:percent([r['score'][k] for r in allgroup]) for k in ('success','target','preserved','parseable','grammar','ended')}))
              sequences=collections.defaultdict(list)
              for r in allgroup:sequences[(r['initial_state'],tuple(r['operations']))].append(r)
              for (initial,ops),ss in sorted(sequences.items()):
                sequence_rows.append(dict(seed=seed,condition=method,update=u,test=label,source=mode,initial_state=initial,operations=json.dumps(ops),step=step,n=len(ss),endpoint=sum(r['score']['success'] for r in ss),full=sum(r['full_success'] for r in ss)))
            for family in ('all','monotone','alternating','boundary_alternating'):
              for step in range(1,6):
                group=[r for r in trajectory if r['template']==t and r['method']==mode and r['step']==step and (family=='all' or r['family']==family)]
                for metric in ('endpoint','full','conditional'):
                  ss=[r for r in group if r['previous_success']] if metric=='conditional' else group
                  vals=[r['full_success'] if metric=='full' else r['score']['success'] for r in ss]
                  name=f'{metric}{step}_{family}'
                  summaries.append(dict(seed=seed,condition=method,update=u,test=label,source=mode,metric=name,cohort='long_paths',n=len(group),k=sum(vals),rate=percent(vals),denominator=len(vals)))
                  if metric in ('endpoint','full'):individual[(seed,method,u,label,mode,name,'long_paths')]={r['id']:(r['world_id'],int(v)) for r,v in zip(ss,vals)}
        failures=collections.Counter((r['template'],r['method'],r['family'],r['first_failure']) for r in trajectory if r['step']==5)
        for (t,mode,family,k),n in failures.items():failure_rows.append(dict(seed=seed,condition=method,update=u,test='iid' if t==0 else 'ood',source=mode,family=family,first_failure=k,count=n))
      for method in ('N','F','R'):
        tr=ROOT/f'local/s{seed}/{method}';refresh_file=tr/'refreshes.json'
        if not refresh_file.exists():continue
        pool=rows(ROOT/'data/continuation.jsonl');draws=rows(ROOT/f'data/draws_s{seed}.jsonl')
        for refresh in read(refresh_file):
          cachefolder=tr/(f'cache_R/u{refresh["update"]:03}' if method=='R' else 'cache_'+method);obs={r['prefix_id']:r for r in rows(cachefolder/'prefix_quality.jsonl')}
          weighted=[obs[r['prefix_id']] for r in pool]
          selected=[obs[pool[i]['prefix_id']] for d in draws if method!='R' or refresh['update']<=d['update']<refresh['update']+20 for i in d['continuation']]
          for kind,ss in (('unique_prefix',list(obs.values())),('full_pool_weighted',weighted),('actual_draws',selected)):
            prefix.append(dict(seed=seed,condition=method,refresh_update=refresh['update'],sample_kind=kind,n=len(ss),success=sum(r['score']['success'] for r in ss),semantic_error=sum(r['prefix_error']['semantic_error'] for r in ss),content_changed_or_lost=sum(r['prefix_error']['content_changed_or_lost'] for r in ss),unresolved=sum(r['prefix_error']['unresolved'] for r in ss),grammar_incomplete=sum(r['prefix_error']['controlled_completeness_failure'] for r in ss),source_sha=refresh['source_sha'],generation_seconds=refresh['generation_seconds']))
    for key,right in individual.items():
      seed,m,u,test,source,metric,cohort=key
      left_method='F' if m=='R' else 'N' if m=='F' else None
      if not left_method:continue
      left=individual.get((seed,left_method,u,test,source,metric,cohort))
      if not left:continue
      assert left.keys()==right.keys();worlds=collections.defaultdict(list)
      for i,(world,value) in right.items():assert left[i][0]==world;worlds[world].append(value-left[i][1])
      averaged={w:statistics.mean(v) for w,v in worlds.items()};low,high=boot(averaged)
      contrasts.append(dict(seed=seed,contrast=m+'-'+left_method,update=u,test=test,source=source,metric=metric,cohort=cohort,n=len(right),worlds=len(worlds),delta_pp=100*statistics.mean(averaged.values()),ci_low_pp=100*low,ci_high_pp=100*high))
    writecsv(ROOT/'summary_by_seed.csv',summaries);writecsv(ROOT/'natural_cells.csv',natural_rows);writecsv(ROOT/'first_failure.csv',failure_rows);writecsv(ROOT/'old_capability_changes.csv',regressions);writecsv(ROOT/'paired_contrasts.csv',contrasts);writecsv(ROOT/'prefix_quality.csv',prefix)
    writecsv(ROOT/'quality_metrics.csv',quality);writecsv(ROOT/'continuation_cells.csv',continuation_cells);writecsv(ROOT/'sequence_metrics.csv',sequence_rows)
    grouped=collections.defaultdict(list)
    for r in summaries:
      if r['rate'] is not None:grouped[tuple(r[k] for k in ('condition','update','test','source','metric','cohort'))].append(r)
    aggregates=[]
    for key,group in grouped.items():
      rates=[r['rate'] for r in group];aggregates.append(dict(condition=key[0],update=key[1],test=key[2],source=key[3],metric=key[4],cohort=key[5],seeds=len(group),mean=statistics.mean(rates),minimum=min(rates),maximum=max(rates)))
    writecsv(ROOT/'mean_and_range.csv',aggregates);dump(ROOT/'ANALYSIS_AUDIT.json',dict(scores_recomputed_exact=True,prediction_rows_verified=audited,pending=pending,all_seeds_complete=not pending,world_bootstrap_replicates=2000,interval_excludes_training_randomness=True,at_utc=now()));print('Analyzed',audited,'raw rows;',len(pending),'pending checkpoint evaluations')
if __name__=='__main__':main()
