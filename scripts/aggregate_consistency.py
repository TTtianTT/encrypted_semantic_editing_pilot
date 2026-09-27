"""Source-paired posthoc analysis; no model selection."""
import json,csv,hashlib,random
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'experiments/latent_consistency_v1';O=P/'results'
def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def boot(d):
 d=np.asarray(d);rng=np.random.default_rng(42);means=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(2000)])*100
 return {'difference_pp':float(d.mean()*100),'CI95_pp':np.percentile(means,[2.5,97.5]).tolist(),'n_sources':len(d),'replicates':2000}
def aligned(a,b):
 assert [x['source_id'] for x in a]==[x['source_id'] for x in b]
def metric(rr,k):return np.array([x['metrics'][k] for x in rr],float)
def summarize(rr):
 return {'n':len(rr),'joint_n':int(metric(rr,'Joint_auto').sum()),**{k:float(metric(rr,k).mean()) for k in ['Joint_auto','content_auto','valid_auto','attribute_auto','reference_chrf','entities_preserved_auto','numbers_preserved_auto','dates_preserved_auto','negation_preserved_auto']},'exact_reference':float(np.mean([x['exact_reference'] for x in rr])),'generation_failures':sum(x['failure'] is not None for x in rr)}
def main():
 assert (O/'complete.json').exists(),'GPU run incomplete'
 B={};summ=[];stats={}
 for context in ['independent','seen_combo']:
  for lam in ['0','0.1']:
   name=context+'_lambda'+lam
   for path in ['latent_once','decode_reencode','single_passive']:
    rr=read(O/f'B_{name}_{path}.jsonl');assert len(rr)==100 and len({x['group_id'] for x in rr})==100
    B[name,path]=rr;row={'context':context,'lambda':lam,'path':path,**summarize(rr)}
    for k in ['future_auto','passive_auto']:row[k]=float(metric(rr,k).mean())
    for k in ['target_memory_error_offline','reencode_memory_error_offline']:
     v=[x[k] for x in rr if x[k] is not None];row[k]=float(np.mean(v)) if v else None;row[k+'_n']=len(v)
    summ.append(row)
  for path in ['latent_once','decode_reencode']:
   a,b=B[context+'_lambda0.1',path],B[context+'_lambda0',path];aligned(a,b)
   stats[context+'_'+path]={k:boot(metric(a,k)-metric(b,k)) for k in ['Joint_auto','content_auto','future_auto','passive_auto']}
 for row in summ:
  single=B[row['context']+'_lambda'+row['lambda'],'single_passive'];row['additional_content_drop_pp']=float((metric(single,'content_auto').mean()-row['content_auto'])*100)
 dump(O/'B_summary.json',summ);dump(O/'B_paired_statistics.json',stats)
 A={};asum=[]
 for method in ['shift_1000','shift_extended','lowrank_1000_budget']:
  for sd in [42,43,44]:
   rr=read(O/f'A_{method}_s{sd}.jsonl');assert len(rr)==364 and len({x['source_id'] for x in rr})==364
   A[method,sd]=rr;asum.append({'method':method,'seed':sd,**summarize(rr)})
 astats={}
 for new,old in [('shift_extended','shift_1000'),('lowrank_1000_budget','shift_1000'),('lowrank_1000_budget','shift_extended')]:
  per={}
  for k in ['Joint_auto','content_auto','attribute_auto']:
   dif=[]
   for sd in [42,43,44]:
    a,b=A[new,sd],A[old,sd];aligned(a,b);aligned(a,A[new,42]);dif.append(metric(a,k)-metric(b,k))
   per[k]={**boot(np.mean(dif,axis=0)),'per_seed_difference_pp':[float(x.mean()*100) for x in dif]}
  astats[new+'_minus_'+old]=per
 dump(O/'A_summary.json',asum);dump(O/'A_paired_statistics.json',astats)
 replay={}
 for context,old in [('independent','independent_lowrank'),('seen_combo','composition_trained_lowrank')]:
  for path in ['latent_once','decode_reencode']:
   a=B[context+'_lambda0',path];b=read(R/f'results/b/{old}_{path}.jsonl');aligned(a,b)
   replay[context+'_'+path]={'n':len(a),'same_output':sum(x['output']==y['output'] for x,y in zip(a,b))}
 for name,old in [('shift_1000','shift'),('lowrank_1000_budget','lowrank_affine')]:
  for sd in [42,43,44]:
   a=A[name,sd];b=read(R/f'results/test_{old}_s{sd}.jsonl');aligned(a,b)
   replay[name+str(sd)]={'n':len(a),'same_output':sum(x['output']==y['output'] for x,y in zip(a,b))}
 dump(O/'original_replay_audit.json',replay)
 examples=[]
 for context in ['independent','seen_combo']:
  a,b=B[context+'_lambda0.1','latent_once'],B[context+'_lambda0','latent_once']
  for improved in [True,False]:
   selected=[(x,y) for x,y in zip(a,b) if x['metrics']['Joint_auto']!=y['metrics']['Joint_auto'] and bool(x['metrics']['Joint_auto'])==improved][:3]
   for x,y in selected:examples.append({'context':context,'auto_improved':improved,'source_id':x['source_id'],'input':x['input'],'reference':x['reference'],'lambda0':y['output'],'lambda01':x['output'],'metrics0':y['metrics'],'metrics01':x['metrics'],'selection':'first three changed Joint_auto cases per direction; not human judgments'})
 dump(O/'changed_examples.json',examples)

 curves=[]
 for sd in [42,43,44]:
  md=json.load(open(P/f'checkpoints/shift_s{sd}/complete.json'))
  curves.extend([{'seed':sd,**x} for x in md['history']])
 for name,rr in [('B_summary',summ),('A_summary',asum),('Shift_learning_curves',curves)]:
  keys=list(dict.fromkeys(k for r in rr for k in r))
  with (O/(name+'.csv')).open('w') as f:w=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");w.writeheader();w.writerows(rr)
 # Anonymized review covers all 100 B source groups, paired methods and paths.
 review=P/'human_review';review.mkdir(exist_ok=True);rng=random.Random(42);reviewrows=[];mapping=[]
 for i in range(100):
  cells=[]
  for (method,path),rr in B.items():
   if path=='single_passive':continue
   q=rr[i];cells.append((method,path,q))
  rng.shuffle(cells)
  for j,(method,path,q) in enumerate(cells):
   rid=f'B{i:03d}-{j}';reviewrows.append({'review_id':rid,'source':q['input'],'output':q['output'],'target':'future tense + passive voice; preserve entities, numbers, negation and event roles','attribute_ok':'','facts_preserved':'','readable':''});mapping.append({'review_id':rid,'source_id':q['source_id'],'method':method,'path':path})
 with (review/'blind.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=reviewrows[0],lineterminator="\n");w.writeheader();w.writerows(reviewrows)
 dump(review/'mapping.json',mapping)
 dump(O/'analysis_audit.json',{'complete_denominators':True,'B_unique_groups':100,'A_unique_sources':364,'bootstrap_unit':'source; A averages paired differences over seeds first','test_reused':True,'human_judgments_received':False})
 print(json.dumps({'B':summ,'B_stats':stats,'A':asum,'A_stats':astats},indent=2))
if __name__=='__main__':main()
