import numpy as np
from task import *
def main():
 complete=json.loads((ROOT/'evaluation/complete.json').read_text());methods=complete['methods'];data={m:read(f'outputs/{m}.jsonl') for m in methods};summary=[];flat=[];fields=[];stats=[];timing=[]
 for method,rows in data.items():
  assert len(rows)==160 and len({r['record_id'] for r in rows})==160
  for split in ['test_iid','test_template_ood']:
   rr=[r for r in rows if r['split']==split];assert len(rr)==80
   summary.append(dict(method=method,split=split,N=80,endpoint_joint=sum(r['endpoint_joint'] for r in rr),trajectory_joint=sum(r['trajectory_joint'] for r in rr) if method.startswith('Sequential') else '',first_joint=sum(r['steps'][0]['score']['joint_ok'] for r in rr),endpoint_correct_intermediate_wrong=sum(r['endpoint_joint'] and not r['trajectory_joint'] for r in rr) if method.startswith('Sequential') else '',date_ok=sum(r['score']['date_ok'] for r in rr),person_ok=sum(r['score']['person_ok'] for r in rr),nondate_ok=sum(r['score']['nondate_facts_ok'] for r in rr),confirmed_nondate_error=sum(r['score']['parsed_nondate_error'] for r in rr),confirmed_date_error=sum(r['score']['parsed_date_error'] for r in rr),unresolved=sum(r['score']['parse_unresolved'] for r in rr),normal_end=sum(r['score']['normal_end'] for r in rr),plan_to_completed=sum(r['score']['plan_to_completed'] for r in rr)))
   timing.append(dict(method=method,split=split,N=80,**{k:sum(r['timing'][k] for r in rr) for k in ['encode','edit','decode','diagnostic_decode','actual_path']}))
   for stage in range(len(rr[0]['steps'])):
    ss=[r['steps'][stage]['score'] for r in rr]
    for field in NONDATE:fields.append(dict(method=method,split=split,stage=stage+1,field=field,N=80,confirmed_correct=sum(s['field_ok'][field] for s in ss),confirmed_error=sum(s['parsed'] is not None and not s['field_ok'][field] for s in ss),unresolved=sum(s['parse_unresolved'] for s in ss)))
  for r in rows:
   for k,s in enumerate(r['steps']):flat.append(dict(method=method,split=r['split'],record_id=r['record_id'],source_offset=r['source_offset'],record_status=r['record_status'],polarity=r['polarity'],stage=k+1,**{f:s['score'][f] for f in ['joint_ok','frame_ok','date_ok','person_ok','nondate_facts_ok','parsed_nondate_error','parsed_date_error','parse_unresolved','normal_end','plan_to_completed']},uncertain_reason=s['score']['uncertain_reason']))
 csvwrite('evaluation/summary.csv',summary);csvwrite('evaluation/per_stage.csv',flat);csvwrite('evaluation/field_scores.csv',fields);csvwrite('evaluation/timing.csv',timing)
 strata=[]
 for factor in ['source_offset','record_status','polarity']:
  for method,rows in data.items():
   groups=collections.defaultdict(list)
   for r in rows:groups[r['split'],str(r[factor])].append(r)
   for (split,value),rr in groups.items():strata.append(dict(method=method,split=split,factor=factor,value=value,N=len(rr),endpoint_joint=sum(r['endpoint_joint'] for r in rr),unresolved=sum(r['score']['parse_unresolved'] for r in rr),nondate_error=sum(r['score']['parsed_nondate_error'] for r in rr)))
 csvwrite('evaluation/stratified.csv',strata)
 pairs=[(a,b) for a in ['Joint16','Joint32'] for b in ['Sequential_T_then_P','Sequential_P_then_T']]+[('Joint32','Joint16'),('Sequential_T_then_P','Sequential_P_then_T')]
 for split in ['test_iid','test_template_ood']:
  ids=sorted(r['record_id'] for r in data['Joint16'] if r['split']==split);idx=np.random.default_rng(SEED).integers(0,80,(2000,80));v={m:{r['record_id']:int(r['endpoint_joint']) for r in rows} for m,rows in data.items()}
  for a,b in pairs:
   delta=np.array([v[a][i]-v[b][i] for i in ids]);rep=delta[idx].mean(1);stats.append(dict(split=split,method_a=a,method_b=b,N=80,metric='endpoint_joint',difference=float(delta.mean()),ci95=np.quantile(rep,[.025,.975]).tolist(),wins=int((delta>0).sum()),losses=int((delta<0).sum())))
 dump('evaluation/paired_statistics.json',dict(replicates=2000,unit='world; same paired resamples for all methods',training_randomness_included=False,results=stats))
 folds=[];numerical=read('outputs/fold_numerical.jsonl')
 for order in ORDERS:
  a={r['record_id']:r for r in data['Sequential_'+order]};b={r['record_id']:r for r in data['Folded_'+order]};nums=[r for r in numerical if r['order']==order];assert len(nums)==160
  folds.append(dict(order=order,N=160,max_abs=max(r['max_abs'] for r in nums),max_relative_l2=max(r['relative_l2'] for r in nums),padding_all_equal=all(r['padding_equal'] for r in nums),exact_text=sum(a[k]['output']==b[k]['output'] for k in a),exact_text_and_end=sum(a[k]['output']==b[k]['output'] and a[k]['steps'][-1]['ended']==b[k]['steps'][-1]['ended'] for k in a),exact_token_ids=sum(a[k]['steps'][-1]['token_ids']==b[k]['steps'][-1]['token_ids'] for k in a),endpoint_decision_equal=sum(a[k]['endpoint_joint']==b[k]['endpoint_joint'] for k in a)))
 dump('evaluation/folding_check.json',folds)
 controls=[]
 for split in ['test_iid','test_template_ood']:
  for role in ['source','target']:
   rr=[r for r in read('outputs/controls.jsonl') if r['split']==split and r['role']==role];controls.append(dict(split=split,role=role,N=len(rr),joint_ok=sum(r['result']['score']['joint_ok'] for r in rr)))
 csvwrite('evaluation/controls.csv',controls)
 selected=json.loads((ROOT/'review/selected_worlds.json').read_text());labels=[f'System {i+1}' for i in range(len(methods))];random.Random(SEED).shuffle(labels);mapping=dict(zip(methods,labels));blind=[];cases=[];md=['# 预选20个世界的配对案例','训练前随机固定IID/OOD各10个世界；没有挑选成功例。human_label为空，尚无真人审核。折叠输出完整保存于JSONL和匿名CSV；本页展示四种主要方法。']
 for rid in selected:
  paired={m:next(r for r in rows if r['record_id']==rid) for m,rows in data.items()};r=paired['Joint16'];cases.append(dict(record_id=rid,source=r['source_text'],source_frame=r['source_frame'],target=r['target_text'],target_frame=r['target_frame'],methods=paired));md += [f'## {len(cases)}. {rid}',f"源frame：{json.dumps(r['source_frame'])}",r['source_text'],f"目标frame：{json.dumps(r['target_frame'])}",r['target_text']]
  for m,v in paired.items():
   if not m.startswith('Folded'):md.append('**'+m+'**')
   for k,s in enumerate(v['steps']):
    gold=v['orders'][m.removeprefix('Sequential_')]['gold_step_texts'][k] if m.startswith('Sequential') else v['target_text']
    blind.append(dict(record_id=rid,split=v['split'],system=mapping[m],stage=k+1,source=v['source_text'],source_frame=json.dumps(v['source_frame']),expected_frame=json.dumps(s['frame']),expected=gold,actual=s['output'],human_label='',human_notes=''))
    if not m.startswith('Folded'):md += [f"第{k+1}步：{s['output']}",f"joint={s['score']['joint_ok']}，date={s['score']['date_ok']}，person={s['score']['person_ok']}，非日期事实={s['score']['nondate_facts_ok']}，未决={s['score']['parse_unresolved']}"]
 write('review/cases.jsonl',cases);csvwrite('review/blind_review.csv',blind);dump('review/private_mapping.json',mapping);(ROOT/'review/CASES.md').write_text('\n\n'.join(md)+'\n')
 train=[]
 for rank in [16,32]:
  c=json.loads((ROOT/f'checkpoints/Joint{rank}/complete.json').read_text())
  for h in c['history']:train.append(dict(method=f'Joint{rank}',**h,selected=h['step']==c['beststep']))
 csvwrite('evaluation/dev_curves.csv',train);print('analyzed',len(methods)*160,'outputs, 20 paired cases')
if __name__=='__main__':main()
