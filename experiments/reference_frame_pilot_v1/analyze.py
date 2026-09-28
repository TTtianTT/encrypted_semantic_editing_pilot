"""Full-denominator, record-clustered test summaries and fixed blind review export."""
import csv,json,random,collections,hashlib
import numpy as np
from prepare import ROOT,dump,write
from semantics import FIELDS
METRICS=['frame_ok','content_ok','joint_ok','collateral_error','plan_to_completed','parse_unresolved']
def csvwrite(path,rows):
 with (ROOT/path).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def read(path):return [json.loads(l) for l in (ROOT/path).read_text().splitlines()]
def main():
 assert json.loads((ROOT/'evaluation/test_generation_complete.json').read_text())['completed']
 atomic=read('outputs/atomic.jsonl');chains=read('outputs/composition.jsonl');controls=read('outputs/reconstruction_controls.jsonl');worlds={w['record_id']:w for w in read('data/test_worlds.jsonl')}
 assert len(atomic)==10920,(len(atomic),10920)
 assert len(chains)==9600;assert len(controls)==160
 allrows=atomic+chains+controls;groups=collections.defaultdict(list)
 for r in allrows:
  groups[(r['method'],r['seed'],r['test_stratum'],r['path'])].append(r)
 for r in atomic:
  groups[(r['method'],r['seed'],r['test_stratum'],'atomic_all')].append(r)
  groups[(r['method'],r['seed'],r['test_stratum'],'atomic_time' if r['operation_ids'][0].startswith('T') else 'atomic_perspective')].append(r)
 summary=[];per=[]
 for (method,seed,stratum,path),rs in groups.items():
  summary.append(dict(method=method,seed=seed,test_stratum=stratum,path=path,N=len(rs),**{k:sum(r['score'][k] for r in rs)/len(rs) for k in METRICS}))
  for rid in sorted({r['gold_record_id'] for r in rs}):
   sub=[r for r in rs if r['gold_record_id']==rid];per.append(dict(method=method,seed=seed,test_stratum=stratum,path=path,record_id=rid,N=len(sub),**{k:sum(r['score'][k] for r in sub)/len(sub) for k in METRICS}))
 csvwrite('evaluation/summary.csv',summary);csvwrite('evaluation/per_record.csv',per)
 status_groups=collections.defaultdict(list)
 for r in allrows:status_groups[(r['method'],r['seed'],r['test_stratum'],r['path'],r['record_status'])].append(r)
 csvwrite('evaluation/status_summary.csv',[dict(method=m,seed=s,test_stratum=st,path=p,record_status=status,N=len(rs),**{k:sum(r['score'][k] for r in rs)/len(rs) for k in METRICS}) for (m,s,st,p,status),rs in status_groups.items()])
 # Three seeds remain separately visible. Bootstrap resamples records, never paths.
 seedstats=[];boot={'replicates':2000,'unit':'record_id, all views/paths/seeds kept together','stratification':['test_iid','test_template_ood'],'scope':'record sampling conditional on these 3 trained seeds; not all training randomness','estimates':[],'paired_differences':[]}
 rng=np.random.default_rng(20260929);sample={st:rng.integers(0,80,(2000,80)) for st in ['test_iid','test_template_ood']};vectors={}
 for method in ['Shift','LowRank16']:
  for st in sample:
   paths=sorted({r['path'] for r in per if r['method']==method and r['test_stratum']==st})
   for path in paths:
    vecs=[];means=[]
    for seed in [42,43,44]:
     rr=sorted([r for r in per if r['method']==method and r['seed']==seed and r['test_stratum']==st and r['path']==path],key=lambda r:r['record_id']);assert len(rr)==80
     v=np.array([r['joint_ok'] for r in rr]);vecs.append(v);means.append(float(v.mean()))
    v=np.mean(vecs,axis=0);vectors[(method,st,path)]=v;interval=np.quantile(v[sample[st]].mean(1),[.025,.975]).tolist()
    obj=dict(method=method,stratum=st,path=path,seed42=means[0],seed43=means[1],seed44=means[2],mean=float(v.mean()),minimum=min(means),maximum=max(means),record_bootstrap_low=interval[0],record_bootstrap_high=interval[1]);seedstats.append(obj);boot['estimates'].append(obj)
 for (method,st,path),v in vectors.items():
  if method!='LowRank16':continue
  d=v-vectors[('Shift',st,path)];boot['paired_differences'].append(dict(comparison='LowRank16 - Shift',stratum=st,path=path,mean=float(d.mean()),record_bootstrap_95=np.quantile(d[sample[st]].mean(1),[.025,.975]).tolist()))
 csvwrite('evaluation/seed_summary.csv',seedstats);dump('evaluation/paired_statistics.json',boot)
 consistency=[];inverse=[];crossing=[]
 for method in ['Shift','LowRank16']:
  for seed in [42,43,44]:
   for st in sample:
    for mode in ['latent_chain','decode_reencode']:
     aa={r['gold_record_id']:r for r in chains if r['method']==method and r['seed']==seed and r['test_stratum']==st and r['path']=='time_then_person/'+mode}
     bb={r['gold_record_id']:r for r in chains if r['method']==method and r['seed']==seed and r['test_stratum']==st and r['path']=='person_then_time/'+mode}
     consistency.append(dict(method=method,seed=seed,stratum=st,mode=mode,N=80,semantic_consistency=sum(aa[k]['score']['parsed'] is not None and aa[k]['score']['parsed']==bb[k]['score']['parsed'] for k in aa)/80,both_correct=sum(aa[k]['score']['joint_ok'] and bb[k]['score']['joint_ok'] for k in aa)/80,exact_output_agreement=sum(aa[k]['output']==bb[k]['output'] for k in aa)/80))
     for path in ['time_return','person_return']:
      rr=[r for r in chains if r['method']==method and r['seed']==seed and r['test_stratum']==st and r['path']==path+'/'+mode]
      inverse.append(dict(method=method,seed=seed,stratum=st,path=path+'/'+mode,N=80,forward_joint=sum(r['intermediate_score']['joint_ok'] for r in rr)/80,return_joint=sum(r['score']['joint_ok'] for r in rr)/80,both_correct=sum(r['intermediate_score']['joint_ok'] and r['score']['joint_ok'] for r in rr)/80))
 csvwrite('evaluation/composition_consistency.csv',consistency);csvwrite('evaluation/inverse_forward_return.csv',inverse)
 for (m,s,st,p),rs in groups.items():
  if p.startswith('atomic_'):continue
  sub=[r for r in rs if r['record_status']=='recorded_plan' and r['allowed_context']['source_frame']['view_date']<worlds[r['gold_record_id']]['event_date']<=r['allowed_context']['target_frame']['view_date']]
  if sub:crossing.append(dict(method=m,seed=s,stratum=st,path=p,N=len(sub),joint_ok=sum(r['score']['joint_ok'] for r in sub)/len(sub),plan_to_completed=sum(r['score']['plan_to_completed'] for r in sub)/len(sub),parse_unresolved=sum(r['score']['parse_unresolved'] for r in sub)/len(sub)))
 csvwrite('evaluation/plan_crossing.csv',crossing)
 slot=collections.Counter();unresolved=[]
 for r in allrows:
  p=r['score']['parsed']
  if p:
   for field in FIELDS:
    if p[field]!=worlds[r['gold_record_id']][field]:slot[(r['method'],r['seed'],r['test_stratum'],field)]+=1
  elif r['method'] in ['Shift','LowRank16']:unresolved.append(r)
 csvwrite('evaluation/slot_errors.csv',[dict(method=m,seed=s,stratum=st,field=f,count=n) for (m,s,st,f),n in sorted(slot.items(),key=str)])
 # Same-batch-length-group descriptive timings; no edit-only speed claims.
 timing=collections.defaultdict(list)
 for r in allrows:timing[(r['method'],r['path'],(r['source_tokens']//8)*8)].append(r)
 csvwrite('evaluation/timing.csv',[dict(method=m,path=p,source_length_bin=f'{ln}-{ln+7}',N=len(rs),**{k:sum(r['timing_s'].get(k,0) for r in rs)/len(rs) for k in ['encode','edit','decode','cpu_rule','diagnostic_decode','total']}) for (m,p,ln),rs in timing.items()])
 reviewrng=random.Random(20260929);picked=[]
 for st in ['test_iid','test_template_ood']:picked+=sorted(reviewrng.sample(sorted(w['record_id'] for w in worlds.values() if w['split']==st),20))
 reviewrows=[r for r in allrows if r['gold_record_id'] in picked]
 conditions=sorted({(r['method'],str(r['seed'])) for r in reviewrows});shuffled=conditions[:];reviewrng.shuffle(shuffled);mapping={condition:f'M{i+1:02}' for i,condition in enumerate(shuffled)}
 blind=[]
 for r in reviewrows:blind.append(dict(review_id=hashlib.sha256(r['uid'].encode()).hexdigest()[:16],anonymous_method=mapping[(r['method'],str(r['seed']))],record_id=r['gold_record_id'],path=r['path'],source_text=r['source_text'],allowed_context=json.dumps(r['allowed_context']),target_semantics=json.dumps(worlds[r['gold_record_id']]),output=r['output'],intermediate_output=r.get('intermediate_output',''),human_frame_ok='',human_content_ok='',human_readable='',human_plan_to_completed='',human_notes=''))
 reviewrng.shuffle(blind);csvwrite('review/blind_review.csv',blind);dump('review/private_method_map.json',{v:{'method':k[0],'seed':k[1]} for k,v in mapping.items()});dump('review/sample_manifest.json',{'seed':20260929,'record_ids':picked,'N_records':40,'N_outputs':len(blind),'selection':'20 uniform records per test stratum; all paths and methods','human_completed':False})
 # Fixed report cases chosen without inspecting outcomes: 8 records per stratum, methods alternating.
 caseids=[]
 rngcase=random.Random(20260929)
 for st in ['test_iid','test_template_ood']:caseids+=sorted(rngcase.sample(sorted(w['record_id'] for w in worlds.values() if w['split']==st),8))
 cases=[]
 for i,rid in enumerate(caseids):
  method=['Shift','LowRank16'][i%2];path=['T_plus_first','P_13_first','T_minus_third','P_31_third'][(i//2)%4]
  r=next(r for r in atomic if r['gold_record_id']==rid and r['method']==method and r['seed']==42 and r['path']==path);cases.append({**r,'world':worlds[rid]})

 for st in ['test_iid','test_template_ood']:
  rid=min(w['record_id'] for w in worlds.values() if w['split']==st)
  for method in ['Shift','LowRank16']:
   r=next(r for r in chains if r['gold_record_id']==rid and r['method']==method and r['seed']==42 and r['path']=='time_then_person/latent_chain');cases.append({**r,'world':worlds[rid]})
 write('review/report_cases.jsonl',cases)
 # Fixed convenience review of unresolved: 12 per method, unique strings, plus all parsed non-date invariant errors first 12.
 audit=[]
 for method in ['Shift','LowRank16']:
  seen=set();subset=[r for r in unresolved if r['method']==method];reviewrng.shuffle(subset)
  for r in subset:
   if r['output'] in seen:continue
   audit.append({**r,'world':worlds[r['gold_record_id']],'selection':'convenience unresolved; cannot estimate population accuracy'});seen.add(r['output'])
   if len(seen)==12:break
 bad=[r for r in atomic+chains if r['method'] in ['Shift','LowRank16'] and r['score']['parsed'] is not None and any(r['score']['parsed'][k]!=worlds[r['gold_record_id']][k] for k in FIELDS if k!='event_date')]
 for r in bad[:12]:audit.append({**r,'world':worlds[r['gold_record_id']],'selection':'first parsed non-date invariant errors; not prevalence sample'})
 write('review/model_review_candidates.jsonl',audit)
 dump('evaluation/audit.json',{'atomic_rows':len(atomic),'composition_rows':len(chains),'reconstruction_rows':len(controls),'unique_uids':len({r['uid'] for r in allrows}),'total_rows':len(allrows),'truncated_rows':sum(r['truncated'] for r in allrows),'all_denominators_retained':True,'test_not_tuned':True,'unresolved_neural_rows':len(unresolved),'parsed_nondate_invariant_error_rows':len(bad),'review_type':'structured automatic checks + model review; no human truth'})
 print(json.dumps({'rows':len(allrows),'seed_summary':[x for x in seedstats if x['path'] in ['atomic_all','atomic_time','atomic_perspective','time_then_person/latent_chain','time_twice/latent_chain']],'unresolved':len(unresolved),'parsed_nondate_errors':len(bad)},indent=2))
if __name__=='__main__':main()
