"""Fixed world-cluster comparisons; no checkpoint or cohort selection."""
import collections,random
import numpy as np
from common_g12 import *
def finite_mean(x):
 x=np.asarray(x,float);x=x[np.isfinite(x)];return float(x.mean()) if len(x) else None
def interval(x):
 x=np.asarray(x,float);x=x[np.isfinite(x)];return [float(v) for v in np.quantile(x,[.025,.975])] if len(x) else [None,None]
def bootmean(a,draw):
 x=np.asarray(a,float)[draw];nn=np.isfinite(x).sum(1);return np.divide(np.nansum(x,axis=1),nn,out=np.full(len(draw),np.nan),where=nn>0)
def errors(xs):
 return dict(date_errors=sum(x['score']['parsed_date_error'] for x in xs),nondate_errors=sum(x['score']['parsed_nondate_error'] for x in xs),unresolved=sum(x['score']['parse_unresolved'] for x in xs),non_normal_end=sum(not x['normal_end'] for x in xs))
def main():
 lock();co=json.loads((ROOT/'data/cohort_lock.json').read_text());ws=read('data/worlds.jsonl');cirows=read('outputs/current_states.jsonl');nr=read('outputs/next_states.jsonl');chain=read('outputs/long_chains.jsonl');at=read('outputs/atomic.jsonl');cur={(r['seed'],r['method'],r['record_id'],r['history']):r for r in cirows};nxt={(r['seed'],r['method'],r['record_id'],r['history']):r['next'] for r in nr};ch={(r['seed'],r['method'],r['record_id'],r['step']):r for r in chain};aa={(r['seed'],r['method'],r['record_id'],r['offset']):r for r in at};mainrows=[];step_rows=[];history_rows=[];atomic_rows=[];firstfails=[];fields=[];contrasts=[];means=[];rng=np.random.default_rng(CFG['bootstrap_seed'])
 for split in ['iid','template_ood']:
  ids=[w['record_id'] for w in ws if w['split']==split];draw=rng.integers(0,80,size=(2000,80));arr={};contrast_arrays=collections.defaultdict(list)
  for s in CFG['seeds']:
   common=set(co['common_AB_strict'][f'{s}/{split}']);crosscommon=set(co['cross_seed_AB_common'][split])
   for arm in CFG['methods']:
    strict={r for r in ids if cur[s,arm,r,0]['strict']};eq={r for r in strict if cur[s,arm,r,0]['equal_mask02']};prefix={r for r in eq if cur[s,arm,r,0]['all_prefix_clean']};common_eq={r for r in common if all(cur[s,a,r,0]['equal_mask02'] for a in ['A','B'])};common_prefix={r for r in common_eq if all(cur[s,a,r,0]['all_prefix_clean'] for a in ['A','B'])}
    protection=np.array([np.mean([aa[s,arm,r,d]['output']['score']['joint_ok'] for d in CFG['atomic_offsets'] if (s,arm,r,d) in aa]) for r in ids]);arr[s,arm,'atomic']=protection
    for step in range(1,6):
     rows=[ch[s,arm,r,step] for r in ids];ep=[r['output']['score']['joint_ok'] for r in rows];tr=[r['trajectory_joint'] for r in rows];arr[s,arm,f'trajectory{step}']=np.array(tr,float);arr[s,arm,f'endpoint{step}']=np.array(ep,float)
     step_rows.append(dict(seed=s,method=arm,split=split,N=80,step=step,endpoint_joint=sum(ep),trajectory_joint=sum(tr),endpoint_rate=np.mean(ep),trajectory_rate=np.mean(tr),**errors([r['output'] for r in rows])))
    for d in CFG['atomic_offsets']:
     rows=[aa[s,arm,r,d] for r in ids if (s,arm,r,d) in aa];atomic_rows.append(dict(seed=s,method=arm,split=split,offset=d,record_status='recorded_plan',N=len(rows),joint=sum(x['output']['score']['joint_ok'] for x in rows),rate=np.mean([x['output']['score']['joint_ok'] for x in rows]),**errors([r['output'] for r in rows])))
    fails=collections.Counter(next((k for k in range(1,6) if not ch[s,arm,r,k]['output']['score']['joint_ok']),0) for r in ids)
    for k in range(6):firstfails.append(dict(seed=s,method=arm,split=split,first_failure_step=k,count=fails[k],N=80,zero_means_all_five_correct=True))
    sets={'all':set(ids),'own_strict':strict,'own_strict_equal_mask':eq,'own_prefix_clean':prefix,'AB_common':common,'AB_common_equal_mask':common_eq,'AB_common_prefix_clean':common_prefix,'cross_seed_AB_common':crosscommon}
    for cohort,selected in sets.items():
     for h in range(3):
      selected_rows=[cur[s,arm,r,h] for r in ids if r in selected];outs=[nxt[s,arm,r,h] for r in ids if r in selected];success=np.array([float(nxt[s,arm,r,h]['score']['joint_ok']) if r in selected else np.nan for r in ids]);arr[s,arm,cohort,h]=success
      history_rows.append(dict(seed=s,method=arm,split=split,cohort=cohort,history=h,N=len(selected),low_coverage=len(selected)<40,current_joint=sum(r['current']['score']['joint_ok'] for r in selected_rows),current_exact=sum(r['current']['exact'] and r['current']['normal_end'] for r in selected_rows),next_joint=sum(x['score']['joint_ok'] for x in outs),next_rate=finite_mean(success),full_history_joint=sum(cur[s,arm,r,h]['prefix_clean'] and nxt[s,arm,r,h]['score']['joint_ok'] for r in selected),**errors(outs)))
    outs=[r['output'] for r in chain+at if r['seed']==s and r['method']==arm and r['split']==split]+[r['next'] for r in nr if r['seed']==s and r['method']==arm and r['split']==split]
    mainrows.append(dict(method=arm,seed=s,split=split,fixed_worlds=80,single_step_world_mean=float(protection.mean()),third_endpoint=int(arr[s,arm,'endpoint3'].sum()),fourth_trajectory=int(arr[s,arm,'trajectory4'].sum()),fifth_trajectory=int(arr[s,arm,'trajectory5'].sum()),H0_all=int(arr[s,arm,'all',0].sum()),H2_all=int(arr[s,arm,'all',2].sum()),own_strict=len(strict),own_equal_mask=len(eq),AB_common=len(common),AB_common_equal_mask=len(common_eq),H0_common=finite_mean(arr[s,arm,'AB_common',0]),H2_common=finite_mean(arr[s,arm,'AB_common',2]),**errors(outs)))
   # All contrasts consume identical world resampling indexes across all seeds/states.
   def add(name,v,cohort='all'):
    b=bootmean(v,draw);record=dict(seed=s,split=split,contrast=name,cohort=cohort,N=int(np.isfinite(v).sum()),difference=finite_mean(v),ci95=interval(b),positive_worlds=int(np.sum(v>0)),negative_worlds=int(np.sum(v<0)),tied_worlds=int(np.sum(v==0)));contrasts.append(record);contrast_arrays[name,cohort].append((v,b,record))
   for metric in ['trajectory4','trajectory5','endpoint3','atomic']:
    add('B-A/'+metric,arr[s,'B',metric]-arr[s,'A',metric]);add('B-Original/'+metric,arr[s,'B',metric]-arr[s,'Original',metric])
   for cohort in ['all','AB_common','AB_common_equal_mask','AB_common_prefix_clean','cross_seed_AB_common']:
    for arm in CFG['methods']:add(arm+'/Delta2',arr[s,arm,cohort,0]-arr[s,arm,cohort,2],cohort)
    add('B-A/Delta2',(arr[s,'B',cohort,0]-arr[s,'B',cohort,2])-(arr[s,'A',cohort,0]-arr[s,'A',cohort,2]),cohort)
    for h in [0,2]:
     add(f'B-A/H{h}',arr[s,'B',cohort,h]-arr[s,'A',cohort,h],cohort);add(f'B-Original/H{h}',arr[s,'B',cohort,h]-arr[s,'Original',cohort,h],cohort)
  for (name,cohort),vals in contrast_arrays.items():
   rates=[v[2]['difference'] for v in vals];m=finite_mean(rates);stack=np.stack([v[1] for v in vals]);den=np.isfinite(stack).sum(0);bs=np.divide(np.nansum(stack,axis=0),den,out=np.full(2000,np.nan),where=den>0);fr=[r for r in rates if r is not None]
   means.append(dict(split=split,contrast=name,cohort=cohort,mean_difference=m,min_seed=min(fr) if fr else None,max_seed=max(fr) if fr else None,seed_N={str(v[2]['seed']):v[2]['N'] for v in vals},positive_seeds=sum(r is not None and r>0 for r in rates),ci95=interval(bs),world_bootstrap_not_training_randomness=True))
 # Field errors with independent observation and world denominators; unresolved separate.
 allobservations=[('current',r,r['current']) for r in cirows]+[('next',r,r['next']) for r in nr]+[('chain',r,r['output']) for r in chain]+[('atomic',r,r['output']) for r in at]
 for kind in ['current','next','chain','atomic']:
  for split in ['iid','template_ood']:
   for s in CFG['seeds']:
    for arm in CFG['methods']:
     obs=[(r,x) for k,r,x in allobservations if k==kind and r['split']==split and r['seed']==s and r['method']==arm];parsed=[(r,x) for r,x in obs if x['score']['parsed'] is not None];worldindex={w['record_id']:w for w in ws}
     for f in FIELDS+['perspective']:
      err=[r['record_id'] for r,x in parsed if x['score']['parsed'][f]!=(x['frame']['perspective'] if f=='perspective' else worldindex[r['record_id']][f])]
      fields.append(dict(kind=kind,method=arm,seed=s,split=split,field=f,observations=len(obs),parsed_N=len(parsed),unresolved=len(obs)-len(parsed),confirmed_error_observations=len(err),confirmed_error_worlds=len(set(err))))
 csvwrite('evaluation/main.csv',mainrows);csvwrite('evaluation/per_step.csv',step_rows);csvwrite('evaluation/atomic_by_state.csv',atomic_rows);csvwrite('evaluation/history.csv',history_rows);csvwrite('evaluation/first_failure.csv',firstfails);csvwrite('evaluation/field_errors.csv',fields);csvwrite('evaluation/paired_contrasts.csv',contrasts);csvwrite('evaluation/fixed_seed_means.csv',means);dump('evaluation/paired_statistics.json',dict(per_seed=contrasts,fixed_seed_means=means,bootstrap_replicates=2000,seed=CFG['bootstrap_seed'],world_unit=True,shared_indexes_across_methods_seeds_states_steps=True))
 mi=next(r for r in means if r['split']=='iid' and r['contrast']=='B-A/trajectory5');mo=next(r for r in means if r['split']=='template_ood' and r['contrast']=='B-A/trajectory5');atomic_means=[r for r in means if r['contrast'] in ['B-A/atomic','B-Original/atomic']]
 decision=dict(iid_mean_fifth_gain_at_least10pp=mi['mean_difference']>=.1,iid_at_least_two_positive_seeds=mi['positive_seeds']>=2,iid_world_ci_lower_positive=mi['ci95'][0]>0,ood_mean_same_positive_direction=mo['mean_difference']>0,atomic_protection_within5pp_all_comparisons=all(r['mean_difference']>=-.05 for r in atomic_means),next_experiment_started=False)
 decision['all_predefined_numerical_gates_met']=all(v for k,v in decision.items() if k!='next_experiment_started');dump('evaluation/decision.json',decision)
 # Fixed world sample; opaque randomized method codes, human labels empty.
 selected=json.loads((ROOT/'review/selection.json').read_text());cells=[(s,a) for s in CFG['seeds'] for a in CFG['methods']];random.Random(CFG['review_seed']+1).shuffle(cells);mapping={f'M{i+1:02d}':dict(seed=s,method=a) for i,(s,a) in enumerate(cells)};codes={(v['seed'],v['method']):k for k,v in mapping.items()};blind=[];lines=['# G12 fixed paired cases','', '20 worlds selected before outputs, anonymous methods; no human review. Convenience descriptions do not estimate frequency. Mapping is in private_method_map.json.','']
 for rid in selected:
  lines += [f'## {rid}','']
  for s,a in cells:
   prefix=[ch[s,a,rid,k]['output'] for k in range(1,6)];current=[cur[s,a,rid,h]['current'] for h in range(3)];nexts=[nxt[s,a,rid,h] for h in range(3)];blind.append(dict(record_id=rid,method=codes[s,a],source_text=ch[s,a,rid,1]['source_text'],source_frame=json.dumps(ch[s,a,rid,1]['source_frame']),current_states=json.dumps(current,ensure_ascii=False),next_states=json.dumps(nexts,ensure_ascii=False),five_step_trajectory=json.dumps(prefix,ensure_ascii=False),human_label='',human_reason=''))
   lines += [f'### {codes[s,a]}',f'Source: {ch[s,a,rid,1]["source_text"]}',f'Current H0/H1/H2: '+json.dumps([x['output'] for x in current],ensure_ascii=False),f'Next H0/H1/H2: '+json.dumps([x['output'] for x in nexts],ensure_ascii=False)]
   for k,x in enumerate(prefix,1):lines.append(f'- {k}: target `{x["target_text"]}`; output `{x["output"]}`; joint={x["score"]["joint_ok"]}; trajectory={ch[s,a,rid,k]["trajectory_joint"]}.')
   lines+=['']
 csvwrite('review/blind_cases.csv',blind);dump('review/private_method_map.json',mapping);(ROOT/'review/CASES.md').write_text('\n'.join(lines).rstrip()+'\n');print('G12 analysis',decision,flush=True)
if __name__=='__main__':main()
