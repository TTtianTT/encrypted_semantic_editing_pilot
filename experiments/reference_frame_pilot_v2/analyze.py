import json,collections,random,hashlib,itertools
import numpy as np
from common import *
METRICS=['joint_ok','date_ok','perspective_ok','nondate_facts_ok','content_ok','frame_ok','parse_unresolved','normal_end','collateral_error','plan_to_completed','parsed_nondate_error','parsed_date_error']
def summarize(rs):
 worlds=collections.defaultdict(list)
 for r in rs:worlds[r['record_id']].append(r)
 n=len(worlds);parsed=[r for r in rs if not r['score']['parse_unresolved']]
 return dict(N_worlds=n,N_outputs=len(rs),**{m:sum(sum(r['score'][m] for r in rr)/len(rr) for rr in worlds.values())/n for m in METRICS},N_parsed_outputs=len(parsed),nondate_errors_among_parsed=sum(r['score']['parsed_nondate_error'] for r in parsed),nondate_error_rate_among_parsed=sum(r['score']['parsed_nondate_error'] for r in parsed)/len(parsed) if parsed else None)
def main():
 completed=json.loads((ROOT/'evaluation/test_complete.json').read_text());groups=completed['groups'];rows=[]
 for g in groups:rows+=read(f'outputs/{g}.jsonl')
 controls=read('outputs/text_rule.jsonl')+read('outputs/target_reconstruction.jsonl')+read('outputs/reconstruction_controls.jsonl');allrows=rows+controls
 assert all(len(read(f'outputs/{g}.jsonl'))==completed['rows_per_group'] for g in groups)
 buckets=collections.defaultdict(list)
 for r in allrows:
  key=(r['group'],r['split'],r['path'],r['mode'],r['kind']);buckets[key].append(r)
  if len(r['operations'])==1:
   buckets[(r['group'],r['split'],'atomic_all',r['mode'],r['kind'])].append(r)
   buckets[(r['group'],r['split'],'atomic_time' if r['operations'][0].startswith('T') else 'atomic_person',r['mode'],r['kind'])].append(r)
 summary=[];per=[]
 for (g,split,path,mode,kind),rs in buckets.items():
  info=dict(group=g,split=split,path=path,mode=mode,kind=kind);summary.append({**info,**summarize(rs)})
  for rid in sorted({r['record_id'] for r in rs}):
   sub=[r for r in rs if r['record_id']==rid];per.append({**info,'record_id':rid,'N_outputs':len(sub),**{m:sum(r['score'][m] for r in sub)/len(sub) for m in METRICS}})
 csvwrite('evaluation/summary.csv',summary);csvwrite('evaluation/per_record.csv',per)
 strata=[]
 for (g,split,path,mode,kind),rs in buckets.items():
  for status in ['recorded_plan','reported_completed','reported_cancelled']:
   sub=[r for r in rs if r['record_status']==status]
   if sub:strata.append(dict(group=g,split=split,path=path,mode=mode,kind=kind,record_status=status,**summarize(sub)))
 csvwrite('evaluation/status_summary.csv',strata)
 offsetrows=[]
 for (g,split,path,mode,kind),rs in buckets.items():
  if g not in groups:continue
  for off in sorted({r['offsets'][0] for r in rs}):
   sub=[r for r in rs if r['offsets'][0]==off];offsetrows.append(dict(group=g,split=split,path=path,mode=mode,source_offset=off,**summarize(sub)))
 csvwrite('evaluation/offset_summary.csv',offsetrows)
 extended=[]
 for g in groups:
  rr=read(f'outputs/{g}_extended.jsonl')
  for split in ['test_iid','test_template_ood']:
   for op in ['T_plus','T_minus']:
    sub=[r for r in rr if r['split']==split and r['operations'][0]==op];extended.append(dict(group=g,split=split,operation=op,**summarize(sub)))
 csvwrite('evaluation/extended_atomic.csv',extended)
 # Same bootstrap draw of the 80 worlds is used for every path within a stratum.
 stats={'replicates':2000,'seed':2026092902,'unit':'world/record_id','stratification':['test_iid','test_template_ood'],'scope':'seed42 record sampling only; all paths/views kept together','estimates':[],'paired_differences':[]}
 rng=np.random.default_rng(2026092902)
 for split in ['test_iid','test_template_ood']:
  universe=sorted({r['record_id'] for r in rows if r['split']==split});assert len(universe)==80;idx={k:i for i,k in enumerate(universe)};draw=rng.integers(0,80,(2000,80));vectors={}
  for (g,st,p,mode,kind),rs in buckets.items():
   if g not in groups or st!=split:continue
   v=np.full(80,np.nan)
   for rid in sorted({r['record_id'] for r in rs}):v[idx[rid]]=np.mean([r['score']['joint_ok'] for r in rs if r['record_id']==rid])
   vectors[(g,p,mode)]=v;sampled=np.nanmean(v[draw],axis=1);stats['estimates'].append(dict(group=g,split=split,path=p,mode=mode,N_worlds=int(np.isfinite(v).sum()),mean=float(np.nanmean(v)),low=float(np.quantile(sampled,.025)),high=float(np.quantile(sampled,.975))))
  for a,b in [('G1','G0')]+([('G2','G1')] if 'G2' in groups else []):
   for g,p,mode in vectors:
    if g!=a:continue
    delta=vectors[(a,p,mode)]-vectors[(b,p,mode)];boot=np.nanmean(delta[draw],axis=1);stats['paired_differences'].append(dict(comparison=a+'-'+b,split=split,path=p,mode=mode,N_worlds=int(np.isfinite(delta).sum()),mean=float(np.nanmean(delta)),low=float(np.quantile(boot,.025)),high=float(np.quantile(boot,.975))))
 dump('evaluation/paired_statistics.json',stats)
 # Every-step score, fixed path denominators; do not select on successful intermediates.
 stepgroups=collections.defaultdict(list)
 for r in rows:
  for i,s in enumerate(r['steps']):stepgroups[(r['group'],r['split'],r['path'],r['mode'],i+1)].append(s)
 csvwrite('evaluation/step_summary.csv',[dict(group=g,split=st,path=p,mode=m,step=i,N=len(ss),**{k:sum(s['score'][k] for s in ss)/len(ss) for k in METRICS}) for (g,st,p,m,i),ss in stepgroups.items()])
 # Separate actual-path and diagnostics time; no end-to-end speed claim.
 csvwrite('evaluation/timing.csv',[dict(group=g,split=st,path=p,mode=m,kind=k,N_outputs=len(rs),**{key:sum(r['timing'].get(key,0) for r in rs)/len(rs) for key in ['encode','edit','decode','diagnostic_decode','actual_path','total_including_diagnostics','cpu_rule']}) for (g,st,p,m,k),rs in buckets.items() if not p.startswith('atomic_')])
 # Fixed twenty worlds, anonymize method and path/mode; reveal frames required to judge meaning.
 selected=set(json.loads((ROOT/'review/preselected_worlds.json').read_text())['worlds']);rngreview=random.Random(2026092903);gs=sorted({r['group'] for r in allrows});rngreview.shuffle(gs);gm={g:f'M{i+1:02}' for i,g in enumerate(gs)};ps=sorted({(r['path'],r['mode'],r['kind']) for r in allrows});rngreview.shuffle(ps);pm={p:f'P{i+1:03}' for i,p in enumerate(ps)};worlds={w['record_id']:w for split in ['test_iid','test_template_ood'] for w in read(f'data/{split}_worlds.jsonl')}
 blind=[]
 for r in allrows:
  if r['record_id'] not in selected:continue
  blind.append(dict(review_id=hashlib.sha256(r['uid'].encode()).hexdigest()[:20],world_id=r['record_id'],method_code=gm[r['group']],path_code=pm[(r['path'],r['mode'],r['kind'])],source_text=r['source_text'],source_frame=json.dumps(r['frames'][0]),evaluated_target_frame=json.dumps(r['steps'][-1]['frame']),gold_world=json.dumps(worlds[r['record_id']]),output=r['output'],step_outputs=json.dumps([s['output'] for s in r['steps']]),human_date_ok='',human_perspective_ok='',human_nondate_facts_ok='',human_readable='',human_notes=''))
 rngreview.shuffle(blind);csvwrite('review/blind_review.csv',blind);dump('review/private_mapping.json',{'methods':{v:k for k,v in gm.items()},'paths':{v:k for k,v in pm.items()}})
 # Convenience examples selected reproducibly, explicitly not prevalence estimates.
 maps={g:{(r['record_id'],r['path'],r['mode']):r for r in rows if r['group']==g} for g in groups};cases=[]
 def add(category,candidates,n=4):
  for r in candidates[:n]:cases.append({'category':category,**r,'gold_world':worlds[r['record_id']],'selection':'convenience, not prevalence estimation'})
 add('coverage_repair',[r for key,r in maps['G1'].items() if not maps['G0'][key]['score']['joint_ok'] and r['score']['joint_ok'] and r['mode']=='decode_reencode'])
 if 'G2' in groups:add('chain_repair',[r for key,r in maps['G2'].items() if not maps['G1'][key]['score']['joint_ok'] and r['score']['joint_ok'] and r['mode']=='latent_chain' and len(r['operations'])>1])
 last=groups[-1];add('still_failed',[r for r in rows if r['group']==last and not r['score']['joint_ok'] and len(r['operations'])>1]);add('parsed_facts_damaged',[r for r in rows if r['score']['parsed_nondate_error']]);add('unresolved',[r for r in rows if r['group']==last and r['score']['parse_unresolved']])
 write('review/explanatory_cases.jsonl',cases)
 # Supplementary model-review candidates: fixed shuffle of unique unresolved per group + first parsed errors.
 candidates=[]
 for g in groups:
  subset=[r for r in rows if r['group']==g and r['score']['parse_unresolved']];rngreview.shuffle(subset);seen=set()
  for r in subset:
   if r['output'] in seen:continue
   candidates.append({**r,'gold_world':worlds[r['record_id']],'review_selection':'8 unique unresolved per group, convenience'});seen.add(r['output'])
   if len(seen)==8:break
 addbad=[r for r in rows if r['score']['parsed_nondate_error']][:8]
 for r in addbad:candidates.append({**r,'gold_world':worlds[r['record_id']],'review_selection':'first 8 parsed nondate errors, convenience'})
 write('review/model_review_candidates.jsonl',candidates)
 # A norm statistics are descriptive only, no unaligned representation distances.
 a=read('diagnostic_a/outputs.jsonl');normgroups=collections.defaultdict(list)
 for r in a:normgroups[(r['seed'],r['path'],r['route'],r['support'])]+=r['second_update_over_input_per_valid_token']
 csvwrite('diagnostic_a/update_norm_summary.csv',[dict(seed=s,path=p,route=rt,support=sp,N_valid_tokens=len(v),mean=float(np.mean(v)),median=float(np.median(v)),p95=float(np.quantile(v,.95))) for (s,p,rt,sp),v in normgroups.items()])
 dump('evaluation/analysis_complete.json',{'groups':groups,'neural_rows':len(rows),'baseline_rows':len(controls),'blind_worlds':len(selected),'blind_rows':len(blind),'explanatory_cases':len(cases),'model_review_candidates':len(candidates),'human_review':False,'structural_exclusions_not_counted_as_model_failures':True})
 print(json.dumps([s for s in summary if s['group'] in groups and s['path'] in ['atomic_all','plus_plus','minus_minus','plus_minus','minus_plus','plus3','minus3']],indent=2))
if __name__=='__main__':main()
