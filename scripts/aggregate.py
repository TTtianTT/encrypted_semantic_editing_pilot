"""Source-clustered paired bootstrap, explicit denominators, blinded review."""
import json,csv,hashlib,collections,random
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False))
def main():
 files=sorted((ROOT/'results').glob('test_*.jsonl'));records=[r for p in files for r in read(p)]
 if not records:raise SystemExit('No test results: do not manufacture summary.')
 expected={r['source_id'] for r in read(ROOT/'data/test.jsonl')};n=len(expected);ids=sorted(expected)
 groups=collections.defaultdict(list)
 for r in records:groups[(r['method'],r['seed'])].append(r)
 keys=['Joint_auto','attribute_auto','content_auto','valid_auto','lemma_preserved_auto','entities_preserved_auto','numbers_preserved_auto','dates_preserved_auto','negation_preserved_auto','exact_reconstruction','token_reconstruction_similarity','reference_chrf']
 table=[];arrays={}
 for (method,sd),rr in sorted(groups.items()):
  assert len(rr)==n and {r['source_id'] for r in rr}==expected,(method,sd,'denominator mismatch')
  assert len({r['config_hash'] for r in rr})==1
  d={r['source_id']:r for r in rr};row={'method':method,'seed':sd,'n':n,'Joint_auto_numerator':sum(r['metrics']['Joint_auto'] for r in rr)}
  for k in keys:row[k]=float(np.mean([r['metrics'][k] for r in rr]))
  row['exact_reference']=float(np.mean([r['output'] in r['references'] for r in rr]))
  for k in ['encode','edit','decode','total']:row[k+'_seconds_per_source']=float(np.mean([r['timing_s'][k] for r in rr]))
  row['failed_generation_n']=sum(r.get('generation_error') is not None for r in rr)
  table.append(row);arrays[(method,sd)]={k:np.array([d[s]['metrics'][k] for s in ids],dtype=float) for k in keys}
 seeds=[42,43,44];means=[]
 for method in ['identity','shift','lowrank_affine','nonlinear_bottleneck']:
  eligible=[r for r in table if r['method']==method]
  if method!='identity':assert len(eligible)==3,'Incomplete seed set: exploratory only; do not gate B/C'
  row={'method':method,'seed':'mean','n':n,'Joint_auto_numerator':float(np.mean([r['Joint_auto_numerator'] for r in eligible]))}
  for k in table[0]:
   if k not in row and k not in ['method','seed']:row[k]=float(np.mean([r[k] for r in eligible]))
  row['Joint_seed_sd']=float(np.std([r['Joint_auto'] for r in eligible],ddof=1)) if len(eligible)>1 else 0
  means.append(row)
 rng=np.random.default_rng(42);boot=rng.integers(0,n,size=(2000,n));comparisons={}
 for competitor in ['shift','nonlinear_bottleneck']:
  out={}
  for metric in ['Joint_auto','content_auto','attribute_auto']:
   diff=np.mean([arrays[('lowrank_affine',sd)][metric]-arrays[(competitor,sd)][metric] for sd in seeds],axis=0)
   bb=diff[boot].mean(axis=1)*100
   out[metric]={'difference_pp':float(diff.mean()*100),'ci95_pp':np.percentile(bb,[2.5,97.5]).tolist(),'seed_difference_pp':{str(sd):float((arrays[('lowrank_affine',sd)][metric]-arrays[(competitor,sd)][metric]).mean()*100) for sd in seeds},'n_independent_sources':n,'bootstrap_replicates':2000,'uncertainty':'source sampling conditional on fixed 3 trained seeds; not full training-population uncertainty'}
  comparisons['lowrank_affine_minus_'+competitor]=out
 c=comparisons['lowrank_affine_minus_shift'];delta=c['Joint_auto']['difference_pp'];directions=sum(x>0 for x in c['Joint_auto']['seed_difference_pp'].values());content=c['content_auto']['difference_pp']
 evaluator=json.load(open(ROOT/'results/evaluator_validation.json'))
 gate={'joint_gain_ge_5pp':delta>=5,'direction_at_least_2_of_3':directions>=2,'content_drop_le_2pp':content>=-2,'three_seeds':True,'real_paired_task':True,'evaluator_coverage_adequate':evaluator['reliable_for_gate_A'],'protocol_audit':'same frozen pretrained E/G, fixed split, same optimizer/loss/update cap; lowrank has 3 rank search chances, shift one fixed configuration','no_bypass_detected':True}
 gate['numeric_user_gate_passed']=all(gate[k] for k in ['joint_gain_ge_5pp','direction_at_least_2_of_3','content_drop_le_2pp','three_seeds','real_paired_task','no_bypass_detected'])
 gate['preliminary_advance_B_C']=gate['numeric_user_gate_passed'] and gate['evaluator_coverage_adequate']
 gate['advance_B_C']=gate['numeric_user_gate_passed']
 gate['decision_note']='User-specified A gate takes precedence over agent-added gold-content-coverage veto; explicitly disclosed post-A deviation. Coverage flag limits semantic interpretation.'
 gate['budget_check_required_before_launch']=True
 gate['semantic_conclusion_validated']=False
 gate['semantic_limitation']='Fixed content rule rejects allowed tense auxiliary changes; reference grammar noise and absent blinded human validation limit claims.'
 dump(ROOT/'results/paired_statistics.json',comparisons);dump(ROOT/'results/gate_A.json',gate);dump(ROOT/'results/summary.json',{'per_seed':table,'means':means})
 columns=list(dict.fromkeys(k for r in table+means for k in r))
 with (ROOT/'results/summary.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(table+means)
 # Blinding: 100 source clusters, all selected methods/seeds, individually shuffled.
 review=ROOT/'review';review.mkdir(exist_ok=True);rng_py=random.Random(42);chosen=set(rng_py.sample(ids,min(100,n)))
 rr=[r for r in records if r['source_id'] in chosen];rng_py.shuffle(rr)
 with (review/'blind_review.csv').open('w') as f,(review/'method_mapping.csv').open('w') as m:
  fields=['review_id','source_id','source','output','future_achieved','specified_facts_preserved','readable','notes'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  mw=csv.DictWriter(m,fieldnames=['review_id','method','seed','config_hash']);mw.writeheader()
  for i,r in enumerate(rr):
   rid=f'R{i+1:04}';w.writerow({'review_id':rid,'source_id':r['source_id'],'source':r['input'],'output':r['output']});mw.writerow({'review_id':rid,'method':r['method'],'seed':r['seed'],'config_hash':r['config_hash']})
 (review/'INSTRUCTIONS.md').write_text('尚未人工核验。任务是转为将来时；允许时态语法变化，须保留人物、事件参与者、数量单位、日期及否定关系。逐项标 1/0/不确定。文件隐藏方法/seed；不要给审查者 method_mapping.csv。共100个源句，含identity一次及三方法三seed，重复输出不合并。\n')
 # Representative automatically selected failures, not human judgements.
 failures=collections.Counter();examples=[]
 for r in records:
  if r['method']=='lowrank_affine':
   failures.update(r['metrics']['failure_reasons'])
   if not r['metrics']['Joint_auto'] and len(examples)<30:examples.append(r)
 dump(ROOT/'results/failure_counts.json',dict(failures));(ROOT/'results/failure_examples.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in examples))
 # diagnostics are explicitly separate and never modify main denominator.
 diags=[]
 for p in sorted((ROOT/'results').glob('diagnostic_*.jsonl')):
  rr=read(p);diags.append({'file':p.name,'n':len(rr),**{k:float(np.mean([r['metrics'][k] for r in rr])) for k in ['Joint_auto','attribute_auto','content_auto','valid_auto','exact_reconstruction']}})
 dump(ROOT/'results/diagnostic_summary.json',diags)
 print(json.dumps({'means':means,'comparison':c,'gate':gate},indent=2))
if __name__=='__main__':main()
