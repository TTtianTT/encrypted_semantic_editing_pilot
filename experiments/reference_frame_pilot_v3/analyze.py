import collections,random
import numpy as np
from common import *
METRICS=['endpoint_joint','trajectory_joint','endpoint_correct_but_intermediate_wrong','first_joint','date_ok','perspective_ok','nondate_facts_ok','parse_unresolved','normal_end','parsed_nondate_error','parsed_date_error']

def load_all():
 out=[]
 for dataset in ['diagnostic','confirmation']:
  for group in ['G1','G2','G3']:
   p=V2/f'outputs/{group}.jsonl' if dataset=='diagnostic' and group!='G3' else ROOT/f'outputs/{dataset}_{group}.jsonl'
   for line in p.read_text().splitlines():
    r=json.loads(line);r['dataset']=dataset;ss=r['steps'];r['endpoint_joint']=bool(r['score']['joint_ok']);r['trajectory_joint']=all(s['score']['joint_ok'] for s in ss);r['first_joint']=bool(ss[0]['score']['joint_ok']);r['endpoint_correct_but_intermediate_wrong']=r['endpoint_joint'] and not r['trajectory_joint'];out.append(r)
 return out

def main():
 rows=load_all();assert len(rows)==6*3732
 worlds={w['record_id']:w for root in [ROOT,V2] for p in (root/'data').glob('*worlds.jsonl') for w in [json.loads(l) for l in p.read_text().splitlines()]}
 flat=[];steps=[];strata=[];dateclasses=[];errors=[];buckets=collections.defaultdict(list)
 for r in rows:
  item={k:r[k] for k in ['dataset','group','split','mode','path','record_id','row_id','record_status','polarity']}
  item.update(source_offset=r['offsets'][0],source_perspective=r['frames'][0]['perspective'])
  item.update({m:int(r[m] if m in r else r['score'][m]) for m in METRICS});flat.append(item)
  paths=[r['path']]
  if len(r['operations'])==1:
   paths+=['atomic_all']
   if r['operations'][0]=='T_plus':paths+=['T_plus']
   else:paths+=['other_atomic']
  for path in paths:buckets[r['dataset'],r['group'],r['split'],r['mode'],path].append(item)
  for k,s in enumerate(r['steps']):
   st={key:item[key] for key in ['dataset','group','split','mode','path','record_id','row_id']};st['step']=k+1
   st.update({m:int(s['score'][m]) for m in ['joint_ok','date_ok','perspective_ok','nondate_facts_ok','parse_unresolved','normal_end','parsed_nondate_error','parsed_date_error']});steps.append(st)
   parsed=s['score']['parsed']
   if parsed is not None:
    w=worlds[r['record_id']]
    for field in NONDATE:
     if parsed[field]!=w[field]:errors.append({**st,'field':field,'expected':w[field],'actual':parsed[field],'output':s['output']})
  if r['path']=='plus_plus':
   s=r['steps'][0];p=s['score']['parsed'];kind='unresolved'
   if p is not None:
    actual_offset=(date.fromisoformat(p['event_date'])-date.fromisoformat(r['frames'][1]['view_date'])).days
    kind='correct_first' if actual_offset==r['offsets'][1] else 'early_two_step_target' if actual_offset==r['offsets'][2] else 'unchanged_source' if actual_offset==r['offsets'][0] else 'other_date'
   r['first_date_class']=kind;dateclasses.append({**item,'first_date_class':kind})
 summary=[]
 for key,rs in buckets.items():
  dataset,group,split,mode,path=key;per=collections.defaultdict(list)
  for r in rs:per[r['record_id']].append(r)
  summary.append(dict(dataset=dataset,group=group,split=split,mode=mode,path=path,N_worlds=len(per),N_outputs=len(rs),**{m:float(np.mean([np.mean([r[m] for r in v]) for v in per.values()])) for m in METRICS}))
 csvwrite('evaluation/per_record.csv',flat);csvwrite('evaluation/steps.csv',steps);csvwrite('evaluation/summary.csv',summary);csvwrite('evaluation/parsed_nondate_errors.csv',errors)
 # Endpoint and stage-specific parsed error denominators are distinct.
 diag=[]
 for dataset in ['diagnostic','confirmation']:
  for g in ['G1','G2','G3']:
   for split in ['test_iid','test_template_ood']:
    for stage,rr in [('endpoint',[r for r in flat if r['dataset']==dataset and r['group']==g and r['split']==split]),('all_steps',[r for r in steps if r['dataset']==dataset and r['group']==g and r['split']==split])]:
     diag.append(dict(dataset=dataset,group=g,split=split,scope=stage,N=len(rr),parsed_N=sum(not r['parse_unresolved'] for r in rr),unresolved_N=sum(r['parse_unresolved'] for r in rr),nondate_error_N=sum(r['parsed_nondate_error'] for r in rr),date_error_N=sum(r['parsed_date_error'] for r in rr),not_ended_N=sum(not r['normal_end'] for r in rr)))
 csvwrite('evaluation/fact_diagnostics.csv',diag)
 for factor in ['source_offset','source_perspective','record_status']:
  b=collections.defaultdict(list)
  for r in flat:
   if r['path'].startswith('T_plus_'):b[r['dataset'],r['group'],r['split'],factor,str(r[factor])].append(r)
  for key,rs in b.items():strata.append(dict(dataset=key[0],group=key[1],split=key[2],factor=key[3],value=key[4],N=len(rs),joint=sum(r['endpoint_joint'] for r in rs)/len(rs),date_ok=sum(r['date_ok'] for r in rs)/len(rs),nondate_facts_ok=sum(r['nondate_facts_ok'] for r in rs)/len(rs),unresolved=sum(r['parse_unresolved'] for r in rs)/len(rs)))
 csvwrite('evaluation/T_plus_stratified.csv',strata);csvwrite('evaluation/first_date_classes.csv',dateclasses)
 cc=collections.Counter((r['dataset'],r['group'],r['split'],r['mode'],r['first_date_class']) for r in dateclasses)
 csvwrite('evaluation/first_date_class_counts.csv',[dict(dataset=k[0],group=k[1],split=k[2],mode=k[3],classification=k[4],N=n) for k,n in cc.items()])
 # A shared bootstrap index matrix per dataset/stratum preserves correlation across all paths.
 stats=[]
 for dataset in ['diagnostic','confirmation']:
  for split in ['test_iid','test_template_ood']:
   ids=sorted({r['record_id'] for r in flat if r['dataset']==dataset and r['split']==split});assert len(ids)==80
   indices=np.random.default_rng(2026093003).integers(0,80,(2000,80))
   for mode,path in sorted({(k[3],k[4]) for k in buckets if k[0]==dataset and k[2]==split}):
    for metric in ['endpoint_joint','trajectory_joint','first_joint']:
     maps={}
     for g in ['G1','G2','G3']:
      temp=collections.defaultdict(list)
      for r in buckets[dataset,g,split,mode,path]:temp[r['record_id']].append(r[metric])
      maps[g]=np.array([np.mean(temp[i]) if i in temp else np.nan for i in ids])
     for base in ['G2','G1']:
      delta=maps['G3']-maps[base];rep=np.nanmean(delta[indices],axis=1);lo,hi=np.quantile(rep,[.025,.975])
      stats.append(dict(dataset=dataset,split=split,mode=mode,path=path,metric=metric,comparison='G3-'+base,delta=float(np.nanmean(delta)),ci95=[float(lo),float(hi)],N_legal_worlds=int(np.isfinite(delta).sum())))
 dump('evaluation/paired_statistics.json',{'replicates':2000,'unit':'world; same sampled indices across all paths/views','training_randomness_included':False,'results':stats})
 def find(g,path):return next(r for r in summary if r['dataset']=='confirmation' and r['split']=='test_iid' and r['mode']=='latent_chain' and r['path']==path and r['group']==g)
 checks={'T_plus':find('G3','T_plus')['endpoint_joint']>=.95,'plus_plus_trajectory':find('G3','plus_plus')['trajectory_joint']>=.9}
 for p in ['plus_person','person_plus']:checks[p]=find('G3',p)['trajectory_joint']>=find('G1',p)['trajectory_joint']-.05-1e-10
 dump('evaluation/next_round_gate.json',{'checks':checks,'all_passed':all(checks.values()),'descriptive_only':True,'requires_OOD_fact_review':True})
 # Anonymous packet: preselected worlds, all methods, all actual trajectories.
 selected=set(json.loads((ROOT/'review/selected_worlds.json').read_text()));gm=dict(zip(['G1','G2','G3'],random.Random(2026093003).sample(['Method A','Method B','Method C'],3)));pm={p:f'Path {i+1:02d}' for i,p in enumerate(sorted(ATOMIC|CHAINS))}
 review=[]
 for r in rows:
  if r['dataset']!='confirmation' or r['record_id'] not in selected:continue
  for k,s in enumerate(r['steps']):review.append(dict(record_id=r['record_id'],method=gm[r['group']],path=pm[r['path']],mode=r['mode'],step=k+1,source=r['source_text'],source_frame=json.dumps(r['frames'][0]),step_frame=json.dumps(s['frame']),gold=r['gold_step_texts'][k],output=s['output'],human_joint='',human_notes=''))
 csvwrite('review/blind_trajectories.csv',review);dump('review/private_mapping.json',{'methods':gm,'paths':pm})
 # Paired convenience examples, not frequency estimation. Each includes both full trajectories.
 lookup={(r['dataset'],r['group'],r['mode'],r['row_id']):r for r in rows};categories=collections.defaultdict(list)
 for r in rows:
  if r['dataset']!='confirmation' or r['group']!='G3' or r['mode']!='latent_chain':continue
  b=lookup[r['dataset'],'G2',r['mode'],r['row_id']]
  cat=[]
  if r['path']=='plus_plus' and b.get('first_date_class')=='early_two_step_target' and r['trajectory_joint']:cat+=['G2_early_G3_correct']
  if r['path'] in ['plus_plus','plus3'] and r['first_joint'] and not r['trajectory_joint']:cat+=['G3_first_restored_later_failed']
  if r['path'] in ['plus_person','person_plus']:cat+=['cross_operator_recovered' if r['trajectory_joint'] and not b['trajectory_joint'] else 'cross_operator_failed' if not r['trajectory_joint'] else 'cross_operator_preserved']
  if any(s['score']['parsed_nondate_error'] for s in r['steps']):cat+=['G3_fact_damage']
  if any(s['score']['parse_unresolved'] for s in r['steps']):cat+=['G3_unresolved']
  for c in cat:
   if len(categories[c])<3:categories[c].append({'category':c,'G2':b,'G3':r})
 cases=[r for rr in categories.values() for r in rr];write('review/paired_cases.jsonl',cases)
 lines=['# 配对案例（便利抽样，不估计频率）','尚无真人审核；下列自动判定保留未决状态。']
 for c in ['G2_early_G3_correct','G3_first_restored_later_failed','cross_operator_recovered','cross_operator_failed','G3_fact_damage','G3_unresolved']:
  lines += ['\n## '+c]
  if not categories[c]:lines+=['没有观察到。'];continue
  for pair in categories[c]:
   r=pair['G3'];lines += [f"\n### {r['record_id']} / {r['path']}",f"源：{r['source_text']}",f"框架：{json.dumps(r['frames'])}"]
   for g in ['G2','G3']:
    for k,s in enumerate(pair[g]['steps']):lines += [f"\n{g} 第{k+1}步：{s['output']}",f"目标：{r['gold_step_texts'][k]}",f"joint={s['score']['joint_ok']}；unresolved={s['score']['parse_unresolved']}"]
 (ROOT/'review/CASES.md').write_text('\n\n'.join(lines)+'\n')
 print(json.dumps(json.loads((ROOT/'evaluation/next_round_gate.json').read_text())))
 for r in summary:
  if r['dataset']=='confirmation' and r['mode']=='latent_chain' and r['path'] in ['T_plus','plus_plus','plus3','plus_person','person_plus']:print(r['split'],r['group'],r['path'],r['first_joint'],r['endpoint_joint'],r['trajectory_joint'])
if __name__=='__main__':main()
