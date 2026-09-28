"""Report locked dev gates; never access model outputs from test."""
import json,csv,random,collections
from pathlib import Path
import numpy as np
from prepare import ROOT,dump,write
from semantics import score,text_rule,FIELDS
METRICS=['frame_ok','content_ok','joint_ok','collateral_error','plan_to_completed','parse_unresolved']
def main():
 rows=[];completed=[]
 worlds={w['record_id']:w for w in map(json.loads,(ROOT/'data/dev_worlds.jsonl').read_text().splitlines())}
 for method in ['Shift','LowRank16']:
  d=ROOT/f'checkpoints/{method}/s42';completed.append(json.loads((d/'complete.json').read_text()));rows += [json.loads(l) for l in (d/'dev_outputs.jsonl').read_text().splitlines()]
 baseline=[]
 for line in (ROOT/'data/dev_pairs.jsonl').read_text().splitlines():
  r=json.loads(line);c=r['allowed_context'];out,err=text_rule(r['source_text'],c['source_frame'],c['target_frame'])
  for method,text in [('Copy',r['source_text']),('Text-rule',out)]:baseline.append({**r,'method':method,'seed':None,'output':text,'score':score(text,c['target_frame'],worlds[r['gold_record_id']]),'rule_error':err if method=='Text-rule' else None})
 write('outputs/dev_cpu_controls.jsonl',baseline);rows+=baseline
 passed=any(m['e1_eligible'] for m in completed)
 dump('evaluation/e1_gate.json',{'passed':passed,'decision':'E2_authorized_by_gate' if passed else 'STOP_E1_no_method_met_preregistered_threshold','methods':completed,'test_opened':False})
 summaries=[]
 for method in sorted({r['method'] for r in rows}):
  rs=[r for r in rows if r['method']==method]
  for path in ['all','time','perspective',*sorted({r['path'] for r in rs})]:
   sub=[r for r in rs if path=='all' or (path=='time' and r['operation_ids'][0].startswith('T')) or (path=='perspective' and r['operation_ids'][0].startswith('P')) or r['path']==path]
   for status in ['all','recorded_plan','reported_completed','reported_cancelled']:
    ss=[r for r in sub if status=='all' or worlds[r['gold_record_id']]['record_status']==status]
    summaries.append({'method':method,'seed':42 if method in ['Shift','LowRank16'] else '', 'test_stratum':'dev_only','path':path,'record_status':status,'N':len(ss),**{k:sum(r['score'][k] for r in ss)/len(ss) for k in METRICS}})
 with (ROOT/'evaluation/summary.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(summaries[0]));writer.writeheader();writer.writerows(summaries)
 per=[]
 for method in sorted({r['method'] for r in rows}):
  for rid in sorted(worlds):
   ss=[r for r in rows if r['method']==method and r['gold_record_id']==rid]
   per.append({'method':method,'seed':42 if method in ['Shift','LowRank16'] else '', 'stratum':'dev','record_id':rid,'N_paths':len(ss),**{k:sum(r['score'][k] for r in ss)/len(ss) for k in METRICS}})
 with (ROOT/'evaluation/per_record.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(per[0]));writer.writeheader();writer.writerows(per)
 rng=np.random.default_rng(20260929);ids=rng.integers(0,80,(2000,80));vectors={m:np.array([r['joint_ok'] for r in per if r['method']==m]) for m in sorted({r['method'] for r in per})}
 statistics={'replicates':2000,'unit':'dev record_id, all six paths together','training_randomness_covered':False,'test_statistics':'not run','methods':{},'paired_differences':{}}
 for m,v in vectors.items():statistics['methods'][m]={'mean':float(v.mean()),'record_bootstrap_95':np.quantile(v[ids].mean(1),[.025,.975]).tolist()}
 for a,b in [('LowRank16','Shift'),('Shift','Copy'),('LowRank16','Copy')]:
  v=vectors[a]-vectors[b];statistics['paired_differences'][a+' - '+b]={'mean':float(v.mean()),'record_bootstrap_95':np.quantile(v[ids].mean(1),[.025,.975]).tolist()}
 dump('evaluation/paired_statistics.json',statistics)
 # Fixed source sampling; convenience unresolved audit is separate.
 picked=sorted(random.Random(20260929).sample(sorted(worlds),10));selected=[r for r in rows if r['method'] in ['Shift','LowRank16'] and r['gold_record_id'] in picked and r['path'] in ['T_plus_first','P_13_first']]
 write('review/fixed_dev_cases.jsonl',[{**r,'world':worlds[r['gold_record_id']]} for r in selected]);dump('review/dev_sample_manifest.json',{'record_ids':picked,'seed':20260929,'paths':['T_plus_first','P_13_first'],'sampling':'uniform 10 dev records independent of output; 40 method/path outputs','not_test':True})
 unresolved=[r for r in rows if r['score']['parse_unresolved']];seen=set();unique=[]
 for r in unresolved:
  if r['output'] not in seen:unique.append(r);seen.add(r['output'])
 write('review/unresolved_unique.jsonl',unique)
 errors=collections.Counter()
 for r in rows:
  if r['method'] not in ['Shift','LowRank16']:continue
  p=r['score']['parsed']
  if p:
   for k in FIELDS:
    if p[k]!=worlds[r['gold_record_id']][k]:errors[r['method']+'/'+k]+=1
 dump('evaluation/parsed_slot_errors.json',dict(errors))
 print(json.dumps({'passed':passed,'methods':{m['method']:m['metrics'] for m in completed},'unique_unresolved':len(unique),'parsed_slot_errors':dict(errors)},indent=2))
if __name__=='__main__':main()
