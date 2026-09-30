"""World-paired analysis; cohorts are consumed verbatim from the pre-next lock."""
import collections,random
import numpy as np
from g11 import *
def ci(v):
 v=np.asarray(v,float);v=v[np.isfinite(v)]
 return [float(np.quantile(v,.025)),float(np.quantile(v,.975))] if len(v) else [None,None]
def main():
 lock=json.loads((ROOT/'data/cohort_lock.json').read_text());curr=read('outputs/current_states.jsonl');nxt=read('outputs/next_states.jsonl');cross=read('outputs/crossover.jsonl');worlds=read('data/worlds.jsonl');windex={w['record_id']:w for w in worlds};plans=read('data/paths.jsonl')
 c={(x['seed'],x['record_id'],x['anchor'],x['history']):x for x in curr};n={(x['seed'],x['record_id'],x['anchor'],x['history']):x for x in nxt};cohorts={(x['seed'],x['record_id'],x['anchor']):x for x in lock['cohorts']}
 x={(r['seed'],r['record_id'],r['condition']):r for r in cross};summaries=[];pairs=[];crosssummary=[];field_errors=[];rng=np.random.default_rng(CFG['bootstrap_seed'])
 splits=['iid','template_ood'];draws={s:rng.integers(0,80,size=(2000,80)) for s in splits};wid={s:[w['record_id'] for w in worlds if w['split']==s] for s in splits}
 pair_arrays={};cross_arrays={}
 for split in splits:
  ids=wid[split];predefined=80
  for seed in CFG['seeds']:
   for d in CFG['anchors']:
    legal={r['record_id'] for r in plans if r['split']==split and r['anchor']==d and r['legal']}
    flags={r:cohorts[seed,r,d] for r in legal}
    sets={'all':legal,'strict':{r for r in legal if flags[r]['strict_cohort']},'semantic':{r for r in legal if flags[r]['semantic_cohort']},'strict_prefix_clean':{r for r in legal if flags[r]['strict_cohort'] and flags[r]['all_prefix_clean']},'common_strict':set(lock['common_strict_worlds'][f'{split}/{d}'])}
    for cohort,selected in sets.items():
     mask=np.array([r in selected for r in ids]);N=len(selected)
     for history in range(3):
      cr=[c[seed,r,d,history] for r in selected];nr=[n[seed,r,d,history] for r in selected]
      summaries.append(dict(seed=seed,split=split,anchor=d,cohort=cohort,history=history,predefined_worlds=predefined,legal_worlds=len(legal),N=N,strict_N=len(sets['strict']),semantic_N=len(sets['semantic']),equal_mask_02_strict_N=sum(flags[r]['equal_mask_02'] for r in sets['strict']),equal_mask_all_strict_N=sum(flags[r]['equal_mask_all'] for r in sets['strict']),current_joint=sum(r['current']['score']['joint_ok'] for r in cr),current_exact=sum(r['current']['exact'] and r['current']['normal_end'] for r in cr),next_joint=sum(r['next']['score']['joint_ok'] for r in nr),full_history_joint=sum(r['full_history_joint'] for r in nr),next_date_errors=sum(r['next']['score']['parsed_date_error'] for r in nr),next_nondate_errors=sum(r['next']['score']['parsed_nondate_error'] for r in nr),next_unresolved=sum(r['next']['score']['parse_unresolved'] for r in nr),next_non_normal_end=sum(not r['next']['normal_end'] for r in nr),current_joint_rate=sum(r['current']['score']['joint_ok'] for r in cr)/N if N else None,next_joint_rate=sum(r['next']['score']['joint_ok'] for r in nr)/N if N else None))
      summaries[-1].update(current_date_errors=sum(r['current']['score']['parsed_date_error'] for r in cr),current_nondate_errors=sum(r['current']['score']['parsed_nondate_error'] for r in cr),current_unresolved=sum(r['current']['score']['parse_unresolved'] for r in cr),current_non_normal_end=sum(not r['current']['normal_end'] for r in cr),prefix_clean=sum(r['prefix_clean'] for r in cr))
     for other in [1,2]:
      a=np.array([int(n[seed,r,d,0]['next']['score']['joint_ok']) if r in legal else 0 for r in ids]);b=np.array([int(n[seed,r,d,other]['next']['score']['joint_ok']) if r in legal else 0 for r in ids]);den=mask[draws[split]].sum(1);num=((a-b)*mask)[draws[split]].sum(1);bs=np.divide(num,den,out=np.full(2000,np.nan),where=den>0)
      both=sum(bool(a[i] and b[i]) for i,r in enumerate(ids) if r in selected);win=sum(bool(a[i] and not b[i]) for i,r in enumerate(ids) if r in selected);loss=sum(bool(b[i] and not a[i]) for i,r in enumerate(ids) if r in selected)
      row=dict(seed=seed,split=split,anchor=d,cohort=cohort,contrast=f'H0-H{other}',N=N,both_success=both,H0_only=win,other_only=loss,both_fail=N-both-win-loss,S0=float(a[mask].mean()) if N else None,Sother=float(b[mask].mean()) if N else None,delta=(win-loss)/N if N else None,ci95=ci(bs));pairs.append(row);pair_arrays[seed,split,d,cohort,other]=bs
  for seed in CFG['seeds']:
   selected={r['record_id'] for r in cross if r['seed']==seed and r['split']==split};N=len(selected);mask=np.array([r in selected for r in ids]);vals={k:np.array([int(x[seed,r,k]['output']['score']['joint_ok']) if r in selected else 0 for r in ids]) for k in ['cc','ee','ec','ce']}
   for condition in vals:
    rs=[x[seed,r,condition] for r in selected];crosssummary.append(dict(seed=seed,split=split,anchor=-1,condition=condition,N=N,joint=sum(r['output']['score']['joint_ok'] for r in rs),joint_rate=float(vals[condition][mask].mean()) if N else None,date_error=sum(r['output']['score']['parsed_date_error'] for r in rs),nondate_error=sum(r['output']['score']['parsed_nondate_error'] for r in rs),unresolved=sum(r['output']['score']['parse_unresolved'] for r in rs),non_normal_end=sum(not r['output']['normal_end'] for r in rs),standard_next_output_mismatch=sum(r['standard_next_output_equal'] is False for r in rs)))
   for condition in ['ec','ce']:
    a,b=vals[condition],vals['ee'];win=sum(bool(a[i] and not b[i]) for i,r in enumerate(ids) if r in selected);loss=sum(bool(b[i] and not a[i]) for i,r in enumerate(ids) if r in selected);den=mask[draws[split]].sum(1);num=((a-b)*mask)[draws[split]].sum(1);bs=np.divide(num,den,out=np.full(2000,np.nan),where=den>0);cross_arrays[seed,split,condition]=bs
    pairs.append(dict(seed=seed,split=split,anchor=-1,cohort='strict_equal_mask_02',contrast=f'Z{condition}-Zee',N=N,both_success=int(((a*b)*mask).sum()),H0_only=win,other_only=loss,both_fail=int((((1-a)*(1-b))*mask).sum()),S0=float(a[mask].mean()) if N else None,Sother=float(b[mask].mean()) if N else None,delta=(win-loss)/N if N else None,ci95=ci(bs),Zee_failures=int(((1-b)*mask).sum()),rescued=win,harmed=loss))
 # Mean/range and paired world bootstrap of the fixed-three-seed mean; never resample seeds.
 meanrows=[]
 for split in splits:
  for d in CFG['anchors']:
   for cohort in ['all','strict','semantic','strict_prefix_clean','common_strict']:
    for other in [1,2]:
     rs=[r for r in pairs if r['split']==split and r['anchor']==d and r['cohort']==cohort and r['contrast']==f'H0-H{other}' and r['delta'] is not None];bs=np.stack([pair_arrays[r['seed'],split,d,cohort,other] for r in rs]) if rs else np.empty((0,2000));ds=[r['delta'] for r in rs]
     meanrows.append(dict(split=split,anchor=d,cohort=cohort,contrast=f'H0-H{other}',seeds=len(rs),seed_N={str(r['seed']):r['N'] for r in rs},mean_delta=float(np.mean(ds)) if ds else None,min_delta=min(ds) if ds else None,max_delta=max(ds) if ds else None,ci95=ci(np.nanmean(bs,axis=0)) if len(bs) else [None,None],world_sampling_only=True))
  for condition in ['ec','ce']:
   rs=[r for r in pairs if r['split']==split and r['contrast']==f'Z{condition}-Zee' and r['delta'] is not None];ds=[r['delta'] for r in rs];bs=np.stack([cross_arrays[r['seed'],split,condition] for r in rs]) if rs else np.empty((0,2000));meanrows.append(dict(split=split,anchor=-1,cohort='strict_equal_mask_02',contrast=f'Z{condition}-Zee',seeds=len(rs),seed_N={str(r['seed']):r['N'] for r in rs},mean_delta=float(np.mean(ds)) if ds else None,min_delta=min(ds) if ds else None,max_delta=max(ds) if ds else None,ci95=ci(np.nanmean(bs,axis=0)) if len(bs) else [None,None],world_sampling_only=True))
 for kind,rs in [('current',curr),('next',nxt),('crossover',cross)]:
  counts=collections.Counter()
  for r in rs:
   p=(r['current'] if kind=='current' else r['next'] if kind=='next' else r['output'])['score']['parsed'];w=windex[r['record_id']]
   if p:
    for f in FIELDS:
     if p[f]!=w[f]:counts[r['seed'],r['split'],r['anchor'],r.get('history',r.get('condition')),f]+=1
  field_errors += [dict(kind=kind,seed=s,split=sp,anchor=d,history_or_condition=h,field=f,N_confirmed_errors=v) for (s,sp,d,h,f),v in counts.items()]
 for r in pairs:r.update(A_only=r['H0_only'],B_only=r['other_only'],pair_order=r['contrast'])
 csvwrite('evaluation/matched_state_summary.csv',summaries);csvwrite('evaluation/crossover.csv',crosssummary);csvwrite('evaluation/paired_win_loss.csv',pairs);csvwrite('evaluation/seed_means.csv',meanrows);csvwrite('evaluation/field_errors.csv',field_errors)
 dump('evaluation/paired_statistics.json',dict(bootstrap_replicates=2000,cluster='world; shared draws across histories/anchors/seeds within split',training_randomness_included=False,per_seed=pairs,fixed_seed_means=meanrows))
 # Frozen sample and opaque seed/history IDs; labels intentionally empty.
 selected=json.loads((ROOT/'review/selection.json').read_text());mapping={};blind=[];case_lines=['# G11 盲化轨迹案例','', '固定样本在输出前选定。未进行真人审核；human_label为空。条件代码映射另存，案例不能估计总体频率。','']
 cells=[dict(seed=s,history=h) for s in CFG['seeds'] for h in range(3)]+[dict(seed=s,condition=k) for s in CFG['seeds'] for k in ['cc','ee','ec','ce']]
 random.Random(CFG['bootstrap_seed']+200).shuffle(cells)
 mapping={f'M{i+1:02d}':cell for i,cell in enumerate(cells)}
 codes={(v['seed'],v.get('history',v.get('condition'))):k for k,v in mapping.items()}
 for rid in selected:
  w=windex[rid];case_lines += [f'## {rid}', '',f'当前期望：{render(w,frame(w,-1))}',f'下一期望：{render(w,frame(w,-2))}','']
  for seed in CFG['seeds']:
   for d in CFG['anchors']:
    for h in range(3):
     cr=c[seed,rid,d,h];nr=n[seed,rid,d,h];method=codes[seed,h];blind.append(dict(record_id=rid,split=w['split'],anchor=d,method=method,current_target=cr['current_gold'],current_output=cr['current']['output'],prefix_outputs=json.dumps([{k:z[k] for k in ['output','frame','target_text']} for z in cr['prefix']],ensure_ascii=False),next_target=nr['next_target'],next_output=nr['next']['output'],strict=cr['strict_cohort'],human_current_label='',human_next_label='',human_reason=''))
     if d==-1:case_lines += [f'- {method}: 当前 `{cr["current"]["output"]}`；下一步 `{nr["next"]["output"]}`。']
   for condition in ['cc','ee','ec','ce']:
    if (seed,rid,condition) in x:
     r=x[seed,rid,condition];blind.append(dict(record_id=rid,split=w['split'],anchor=-1,method=codes[seed,condition],current_target=render(w,frame(w,-1)),current_output='',prefix_outputs='',next_target=r['target_text'],next_output=r['output']['output'],strict=True,human_current_label='',human_next_label='',human_reason=''));case_lines += [f'- {codes[seed,condition]}: 下一步 `{r["output"]["output"]}`。']
  case_lines+=['']
 csvwrite('review/blind_cases.csv',blind);dump('review/private_method_map.json',mapping);(ROOT/'review/CASES.md').write_text('\n'.join(case_lines).rstrip()+'\n')
 # Resource decision criteria evaluated without post-hoc cohort changes.
 primary=[r for r in pairs if r['anchor']==-1 and r['cohort']=='strict' and r['contrast']=='H0-H2'];i=[r for r in primary if r['split']=='iid'];o=[r for r in primary if r['split']=='template_ood'];mi=next(r for r in meanrows if r['split']=='iid' and r['anchor']==-1 and r['cohort']=='strict' and r['contrast']=='H0-H2')
 decision=dict(coverage_sufficient=all(r['N']>=40 for r in primary),canonical_next_supported=all(r['S0'] is not None and r['S0']>=.9 for r in primary),iid_mean_delta_at_least_15pp=mi['mean_delta'] is not None and mi['mean_delta']>=.15,iid_all_seeds_positive=all(r['delta'] is not None and r['delta']>0 for r in i),iid_paired_world_ci_positive=mi['ci95'][0] is not None and mi['ci95'][0]>0,ood_positive_seeds=sum(r['delta'] is not None and r['delta']>0 for r in o),G12_run=False)
 dump('evaluation/decision.json',decision);print('G11 analysis',decision,flush=True)
if __name__=='__main__':main()
