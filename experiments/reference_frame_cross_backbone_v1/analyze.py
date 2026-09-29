import collections,csv,random
import numpy as np
from common import *
METRICS=['endpoint_joint','trajectory_joint','first_joint','endpoint_correct_but_intermediate_wrong','date_ok','person_ok','nondate_facts_ok','parse_unresolved','normal_end','parsed_nondate_error','parsed_date_error']
def main():
 rows=[];models=[]
 for p in sorted((ROOT/'evaluation').glob('*_complete.json')):
  name=p.name.removesuffix('_complete.json');models.append(name)
  for g in ['G1','G3']:
   rr=read(f'outputs/{name}/{g}.jsonl');assert len(rr)==3732 and len({r['uid'] for r in rr})==3732;rows+=rr
 flat=[];steps=[];buckets=collections.defaultdict(list);errors=[];dateclass=[]
 worlds={w['record_id']:w for s in ['test_iid','test_template_ood'] for w in read(f'data/{s}_worlds.jsonl')}
 for r in rows:
  item={k:r[k] for k in ['model','group','mode','split','path','record_id','row_id','record_status','polarity']};item.update(source_offset=r['offsets'][0],source_person=r['frames'][0]['perspective']);item.update({m:int(r.get(m,r['score'].get(m,False))) for m in METRICS});item['first_joint']=int(r['steps'][0]['score']['joint_ok']);item['endpoint_correct_but_intermediate_wrong']=int(r['endpoint_joint'] and not r['trajectory_joint']);flat.append(item)
  paths=[r['path']]
  if len(r['operations'])==1:paths+=['atomic_all',r['operations'][0]]
  for path in paths:buckets[r['model'],r['group'],r['split'],r['mode'],path].append(item)
  for k,s in enumerate(r['steps']):
   st={key:item[key] for key in ['model','group','mode','split','path','record_id','row_id']};st['step']=k+1;st.update({key:int(s['score'][key]) for key in ['frame_ok','joint_ok','date_ok','person_ok','nondate_facts_ok','parse_unresolved','normal_end','parsed_nondate_error','parsed_date_error','missing_header','repeated_header','empty_output','repeated_trigram']});st.update({f+'_ok':int(s['score']['field_ok'][f]) for f in NONDATE});steps.append(st)
   p=s['score']['parsed']
   if p:
    for f in NONDATE:
     if p[f]!=worlds[r['record_id']][f]:errors.append({**st,'field':f,'expected':worlds[r['record_id']][f],'actual':p[f],'output':s['output']})
  if r['path']=='plus_plus':
   p=r['steps'][0]['score']['parsed'];cl='unresolved'
   if p:
    off=(date.fromisoformat(p['event_date'])-date.fromisoformat(r['frames'][1]['view_date'])).days;cl='correct_first' if off==r['offsets'][1] else 'early_endpoint' if off==r['offsets'][2] else 'unchanged_source' if off==r['offsets'][0] else 'other_date'
   dateclass.append({**item,'date_class':cl})
 summary=[]
 for key,rs in buckets.items():
  model,g,split,mode,path=key;per=collections.defaultdict(list)
  for r in rs:per[r['record_id']].append(r)
  summary.append(dict(model=model,group=g,split=split,mode=mode,path=path,N_worlds=len(per),N_outputs=len(rs),endpoint_successes=sum(r['endpoint_joint'] for r in rs),trajectory_successes=sum(r['trajectory_joint'] for r in rs),**{m:float(np.mean([np.mean([r[m] for r in rr]) for rr in per.values()])) for m in METRICS}))
 csvwrite('evaluation/summary.csv',summary);csvwrite('evaluation/per_record.csv',flat);csvwrite('evaluation/per_step.csv',steps);csvwrite('evaluation/fact_errors.csv',errors);csvwrite('evaluation/first_date_classes.csv',dateclass)
 field_counts=collections.Counter((r['model'],r['group'],r['split'],r['mode'],r['path'],r['step'],r['field']) for r in errors)
 csvwrite('evaluation/fact_error_counts.csv',[dict(model=k[0],group=k[1],split=k[2],mode=k[3],path=k[4],step=k[5],field=k[6],N=n) for k,n in field_counts.items()])
 stage_facts=[]
 for model in models:
  for g in ['G1','G3']:
   for split in ['test_iid','test_template_ood']:
    rr=[r for r in rows if (r['model'],r['group'],r['split'])==(model,g,split)];ss=[s for r in rr for s in r['steps']]
    stage_facts.append(dict(model=model,group=g,split=split,N_stages=len(ss),parsed_N=sum(not s['score']['parse_unresolved'] for s in ss),nondate_error_N=sum(s['score']['parsed_nondate_error'] for s in ss),unresolved_N=sum(s['score']['parse_unresolved'] for s in ss),not_ended_N=sum(not s['score']['normal_end'] for s in ss),missing_header_N=sum(s['score']['missing_header'] for s in ss),repeated_header_N=sum(s['score']['repeated_header'] for s in ss),empty_N=sum(s['score']['empty_output'] for s in ss),repeated_trigram_N=sum(s['score']['repeated_trigram'] for s in ss),plan_to_completed_N=sum(bool(s['score']['parsed'] and s['score']['parsed']['record_status']=='reported_completed') for r in rr if r['record_status']=='recorded_plan' for s in r['steps'])))
 csvwrite('evaluation/stage_fact_summary.csv',stage_facts)
 facts=[];strata=[]
 for model in models:
  for g in ['G1','G3']:
   for split in ['test_iid','test_template_ood']:
    rr=[r for r in flat if (r['model'],r['group'],r['split'])==(model,g,split)];facts.append(dict(model=model,group=g,split=split,N=len(rr),parsed_N=sum(not r['parse_unresolved'] for r in rr),unresolved_N=sum(r['parse_unresolved'] for r in rr),nondate_error_N=sum(r['parsed_nondate_error'] for r in rr),date_error_N=sum(r['parsed_date_error'] for r in rr),not_ended_N=sum(not r['normal_end'] for r in rr)))
 for factor in ['source_offset','source_person','record_status','polarity']:
  b=collections.defaultdict(list)
  for r in flat:
   if r['path'].startswith('T_plus_'):b[r['model'],r['group'],r['split'],str(r[factor])].append(r)
  for key,rs in b.items():strata.append(dict(model=key[0],group=key[1],split=key[2],factor=factor,value=key[3],N=len(rs),joint=sum(r['endpoint_joint'] for r in rs),date_ok=sum(r['date_ok'] for r in rs),nondate_ok=sum(r['nondate_facts_ok'] for r in rs),unresolved=sum(r['parse_unresolved'] for r in rs)))
 csvwrite('evaluation/fact_summary.csv',facts);csvwrite('evaluation/T_plus_strata.csv',strata)
 # Controls retain the same fixed world/path denominators; cached generations are not independent samples.
 controls=[];timings=[]
 for model in models:
  cb=collections.defaultdict(list)
  for r in read(f'outputs/{model}/controls.jsonl'):cb[r['split'],r['path'],r['kind']].append(r)
  for (split,path,kind),rs in cb.items():
   controls.append(dict(model=model,split=split,path=path,kind=kind,N=len(rs),endpoint_N=sum(r['endpoint_joint'] for r in rs),trajectory_N=sum(r['trajectory_joint'] for r in rs),stage_N=sum(len(r['steps']) for r in rs),unresolved_stage_N=sum(s['score']['parse_unresolved'] for r in rs for s in r['steps']),not_ended_stage_N=sum(not s['score']['normal_end'] for r in rs for s in r['steps'])))
 for key,rs in buckets.items():
  model,g,split,mode,path=key
  if path not in ATOMIC and path not in CHAINS:continue
  source=[r for r in rows if (r['model'],r['group'],r['split'],r['mode'],r['path'])==key]
  timings.append(dict(model=model,group=g,split=split,mode=mode,path=path,N=len(source),**{k:sum(r['timing'][k] for r in source) for k in ['encode','edit','decode','diagnostic_decode','actual_path']},batch_sizes=','.join(map(str,sorted({r['timing']['batch_size'] for r in source})))))
 csvwrite('evaluation/control_summary.csv',controls);csvwrite('evaluation/timing_summary.csv',timings)
 dc=collections.Counter((r['model'],r['group'],r['split'],r['mode'],r['date_class']) for r in dateclass)
 csvwrite('evaluation/first_date_class_summary.csv',[dict(model=k[0],group=k[1],split=k[2],mode=k[3],date_class=k[4],N=v) for k,v in dc.items()])
 training=[];curves=[]
 for model in MODELS:
  for g in ['G1','G3']:
   p=ROOT/f'checkpoints/{model}/{g}/complete.json'
   if not p.exists():continue
   c=json.loads(p.read_text())
   for op,v in c['counts'].items():training.append(dict(model=model,group=g,operation=op,**v))
   curves += [dict(model=model,group=g,**h,selected=h['step']==c['beststep']) for h in c['history']]
 csvwrite('evaluation/training_counts.csv',training);csvwrite('evaluation/dev_curves.csv',curves)
 stats=[]
 for split in ['test_iid','test_template_ood']:
  ids=sorted(w['record_id'] for w in read(f'data/{split}_worlds.jsonl'));idx=np.random.default_rng(2026092904).integers(0,80,(2000,80))
  def values(model,g,mode,path,metric):
   per=collections.defaultdict(list)
   for r in buckets[model,g,split,mode,path]:per[r['record_id']].append(r[metric])
   return np.array([np.mean(per[i]) if i in per else np.nan for i in ids])
  def pair(a,b,meta):
   delta=a-b;rep=np.nanmean(delta[idx],axis=1);lo,hi=np.quantile(rep,[.025,.975]);stats.append(dict(split=split,**meta,delta=float(np.nanmean(delta)),ci95=[float(lo),float(hi)],N=int(np.isfinite(delta).sum())))
  for model in models:
   keys=sorted({(k[3],k[4]) for k in buckets if k[0]==model and k[2]==split})
   for mode,path in keys:
    for metric in ['endpoint_joint','trajectory_joint']:
     pair(values(model,'G3',mode,path,metric),values(model,'G1',mode,path,metric),dict(model=model,comparison='G3-G1',mode=mode,path=path,metric=metric))
     if mode=='latent_chain' and path in CHAINS:
      for g in ['G1','G3']:pair(values(model,g,mode,path,metric),values(model,g,'decode_reencode',path,metric),dict(model=model,comparison='latent-reencode',group=g,path=path,metric=metric))
     if model!='BART' and 'BART' in models:
      for g in ['G1','G3']:pair(values(model,g,mode,path,metric),values('BART',g,mode,path,metric),dict(model=model,comparison='model-BART',group=g,mode=mode,path=path,metric=metric))
 dump('evaluation/paired_statistics.json',dict(replicates=2000,unit='world; shared indices across every model/path/view',training_randomness_included=False,exploratory=True,results=stats))
 selected=set(json.loads((ROOT/'review/selected_worlds.json').read_text()));combos=[(m,g) for m in models for g in ['G1','G3']];labels=[f'System {i+1:02d}' for i in range(len(combos))];random.Random(2026092904).shuffle(labels);mapping=dict(zip(combos,labels));review=[]
 for r in rows:
  if r['record_id'] not in selected:continue
  for k,s in enumerate(r['steps']):review.append(dict(record_id=r['record_id'],system=mapping[r['model'],r['group']],path=r['path'],mode=r['mode'],step=k+1,source=r['source_text'],source_frame=json.dumps(r['frames'][0]),expected_frame=json.dumps(r['frames'][k+1]),expected_text=r['gold_step_texts'][k],actual=s['output'],human_label='',human_notes=''))
 csvwrite('review/blind_trajectories.csv',review);dump('review/private_mapping.json',{'/'.join(k):v for k,v in mapping.items()})
 # At most 20 convenience cases, including one reconstruction failure per rejected candidate.
 cases=[]
 for model in MODELS:
  p=ROOT/f'calibration/{model}/admission.json'
  if not p.exists():continue
  a=json.loads(p.read_text())
  if a['status']=='reconstruction_failed':
   rs=read(f"calibration/{model}/{a['selected_wrapper']}_scored.jsonl");r=next(r for r in rs if not r['score']['joint_ok']);cases.append(dict(category='reconstruction_failure',model=model,record=r))
 lookup={(r['model'],r['group'],r['mode'],r['row_id']):r for r in rows};cats=collections.defaultdict(list);candidates=collections.defaultdict(list)
 for r in rows:
  if r['mode']!='latent_chain' or len(r['operations'])<2:continue
  other=lookup[r['model'],'G3' if r['group']=='G1' else 'G1',r['mode'],r['row_id']];rec=lookup[r['model'],r['group'],'decode_reencode',r['row_id']];labels=[]
  if r['group']=='G1' and r['steps'][0]['score']['joint_ok'] and not r['trajectory_joint']:labels+=['single_success_chain_failure']
  if not r['trajectory_joint'] and rec['trajectory_joint']:labels+=['reencode_recovers']
  if r['group']=='G3' and r['trajectory_joint'] and not other['trajectory_joint']:labels+=['G3_local_repair']
  if r['group']=='G3' and not r['trajectory_joint'] and other['trajectory_joint']:labels+=['G3_tradeoff']
  if r['group']=='G3' and r['path']=='plus3' and all(s['score']['joint_ok'] for s in r['steps'][:2]) and not r['steps'][2]['score']['joint_ok']:labels+=['untrained_three_failure']
  if any(s['score']['parsed_nondate_error'] for s in r['steps']):labels+=['fact_damage']
  if any(s['score']['parse_unresolved'] for s in r['steps']):labels+=['unresolved']
  for c in labels:
   if len(candidates[c,r['model']])<20:candidates[c,r['model']].append(dict(category=c,model=r['model'],record=r,paired=other,reencoded=rec))
 categories=['single_success_chain_failure','reencode_recovers','G3_local_repair','G3_tradeoff','untrained_three_failure','fact_damage','unresolved'];used=set()
 for c in categories:
  for model in models:
   available=[v for v in candidates[c,model] if (model,v['record']['row_id']) not in used]
   if not available and candidates[c,model]:available=candidates[c,model][:1]
   if available:
    v=available[0];cats[c].append(v);used.add((model,v['record']['row_id']))
  cases+=cats[c]
 cases=cases[:20];write('review/cases.jsonl',cases)
 lines=['# 配对案例（便利抽样；不是准确率估计）','human_label为空，尚无真人审核。']
 for i,c in enumerate(cases):
  r=c['record'];lines += [f"\n## {i+1}. {c['category']} / {c['model']}"]
  if c['category']=='reconstruction_failure':lines += ['源：'+r['text'],'输出：'+r['output'],'判定：'+json.dumps(r['score'],ensure_ascii=False)];continue
  lines+=['源：'+r['source_text'],'框架：'+json.dumps(r['frames'])]
  for kind in ['record','paired','reencoded']:
   rr=c[kind];lines += [f"{rr['group']} / {rr['mode']}"]
   for k,s in enumerate(rr['steps']):lines += [f"第{k+1}步目标：{rr['gold_step_texts'][k]}",f"实际：{s['output']}",f"joint={s['score']['joint_ok']}, unresolved={s['score']['parse_unresolved']}"]
 for c in categories:
  if not cats[c]:lines+=['没有观察到类别：'+c]
 (ROOT/'review/CASES.md').write_text('\n\n'.join(lines)+'\n');print('analyzed',models,len(rows),'examples',len(cases))
if __name__=='__main__':main()
