"""Materialize explicit in-session semantic judgments, then source-paired analysis.
This script does not perform automatic semantic judging. Manual TSV records are
Codex model judgments made after reading all 100 groups of four actual outputs.
"""
import collections,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'experiments/single_step_diagnosis_v1';PATHS=['identity_source','identity_target','shift','lowrank'];DIMS=['time_status','meaning_status','readability_status'];NAMES={'P':'pass','F':'fail','U':'uncertain'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def joint(r):
 vals=[r[k] for k in DIMS]
 return 'fail' if 'fail' in vals else ('uncertain' if 'uncertain' in vals else 'pass')
def main():
 cfg=json.loads((P/'config.json').read_text());outputs=[json.loads(s) for s in (P/'outputs.jsonl').read_text().splitlines()];assert len(outputs)==400
 assert sha(P/'outputs.jsonl')==json.loads((P/'generation_summary.json').read_text())['output_sha256']
 tasks={r['case_id']:r for r in csv.DictReader((P/'task_validity.csv').open())};assert len(tasks)==100
 manual={}
 for line in (P/'output_model_judgments.tsv').read_text().splitlines():
  parts=line.split('\t');assert len(parts)==6;case=parts[0];assert case not in manual;manual[case]=parts[1:]
 assert set(manual)==set(tasks)
 mapping={(r['case_id'],r['path']):r['review_id'] for r in json.loads((P/'method_map.json').read_text())};records=[]
 now=datetime.now(timezone.utc).isoformat()
 for o in outputs:
  case,path=o['case_id'],o['path'];code=manual[case][PATHS.index(path)];note=manual[case][4];assert len(code)==3 and set(code)<=set(NAMES)
  tags=[]
  if tasks[case]['task_validity']!='valid':tags.append('input_reference_problem_or_uncertainty')
  if code[0]=='F':tags.append('tense_error')
  if code[2]=='F':tags.append('grammar_error')
  if code[1]=='F':tags.append('information_or_event_error')
  new_reconstruction='not_applicable'
  if path.startswith('identity'):
   new_reconstruction='yes' if case=='S088' else 'no'
   if new_reconstruction=='yes':tags.append('reconstruction_introduced_error')
  specials={('S021','shift'):['temporal_event_relation_loss'],('S026','lowrank'):['information_loss'],('S034','shift'):['information_loss'],('S061','shift'):['role_misassignment','information_loss'],('S072','shift'):['information_loss'],('S072','lowrank'):['event_substitution'],('S093','shift'):['information_addition']}
  tags+=specials.get((case,path),[])
  if case=='S088':tags.append('number_error')
  goal={'identity_source':'原句时态、原句信息、可读性','identity_target':'目标未来时、目标信息、可读性；目标自身问题单列','shift':'未来编辑、原句信息、可读性','lowrank':'未来编辑、原句信息、可读性'}[path]
  r={'review_id':mapping[case,path],'case_id':case,'source_id':o['source_id'],'path':path,'task_validity':tasks[case]['task_validity'],**{k:NAMES[c] for k,c in zip(DIMS,code)},'reason':f"本输出逐项判断（{goal}）：{code}。{note}",'reviewer':'Codex GPT-6 family; exact runtime model revision unavailable','review_type':'substantive model semantic review; exposed to methods; not human or independent blind review','reviewed_at':now,'introduced_reconstruction_error':new_reconstruction,'error_categories':'|'.join(tags),'output_sha256':hashlib.sha256(o['output'].encode()).hexdigest(),'human_time_status':'','human_meaning_status':'','human_readability_status':'','human_reason':'','human_reviewer':''}
  r['joint_status']=joint(r);records.append(r)
 # Preserve score timestamps on exact reruns; changed judgments require explicit new version.
 dest=P/'model_review.csv'
 if dest.exists():
  prev=list(csv.DictReader(dest.open()));assert len(prev)==len(records)
  for a,b in zip(prev,records):
   for k in b:
    if k!='reviewed_at':assert a[k]==b[k],('Scoring changed; create a new review version',a['review_id'],k)
  records=prev
 else:
  with dest.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=records[0],lineterminator='\n');w.writeheader();w.writerows(records)
 freeze={'review_sha256':sha(dest),'judgments_sha256':sha(P/'output_model_judgments.tsv'),'outputs_sha256':sha(P/'outputs.jsonl'),'task_review_sha256':sha(P/'task_validity.csv'),'scoring_type':'model review, not human','all_400_outputs_substantively_reviewed':True,'method_exposure':True,'model_review_was_not_blind':True,'human_fields_empty':True,'frozen_at':records[0]['reviewed_at']}
 dump(P/'model_review_frozen.json',freeze)
 by={(r['case_id'],r['path']):r for r in records};cases=sorted(tasks);valid=[c for c in cases if tasks[c]['task_validity']=='valid'];subset=[c for c in valid if all(by[c,p]['joint_status']=='pass' for p in PATHS[:2])]
 strata={'all_sampled':cases,'fixed_valid':valid,'invalid':[c for c in cases if tasks[c]['task_validity']=='invalid'],'task_uncertain':[c for c in cases if tasks[c]['task_validity']=='uncertain'],'valid_both_reconstructions_pass':subset,'valid_plus_task_uncertain':[c for c in cases if tasks[c]['task_validity']!='invalid']}
 summary=[]
 for name,ids in strata.items():
  for path in PATHS:
   rr=[by[c,path] for c in ids];counts=collections.Counter(r['joint_status'] for r in rr);row={'stratum':name,'path':path,'n':len(ids),'confirmed_n':counts['pass'],'fail_n':counts['fail'],'uncertain_n':counts['uncertain'],'confirmed_rate':counts['pass']/len(ids) if ids else None,'optimistic_rate':(counts['pass']+counts['uncertain'])/len(ids) if ids else None}
   for dim in DIMS:
    for val in NAMES.values():row[dim+'_'+val]=sum(r[dim]==val for r in rr)
   summary.append(row)
 def boot(delta):
  d=np.array(delta,dtype=float)
  if not len(d):return {'n':0,'difference_pp':None,'CI95_pp':None}
  rng=np.random.default_rng(20260928);draw=rng.integers(0,len(d),size=(2000,len(d)));b=d[draw].mean(1)*100
  return {'n':len(d),'difference_pp':float(d.mean()*100),'CI95_pp':np.percentile(b,[2.5,97.5]).tolist(),'bootstrap_replicates':2000,'statistical_seed':20260928}
 paired={};cross={}
 for name,ids in strata.items():
  lp=np.array([by[c,'lowrank']['joint_status']=='pass' for c in ids],float);sp=np.array([by[c,'shift']['joint_status']=='pass' for c in ids],float);lu=np.array([by[c,'lowrank']['joint_status']=='uncertain' for c in ids],float);su=np.array([by[c,'shift']['joint_status']=='uncertain' for c in ids],float)
  paired[name]={'conservative':boot(lp-sp),'uncertain_both_pass':boot(lp+lu-sp-su),'worst_for_lowrank':boot(lp-sp-su),'best_for_lowrank':boot(lp+lu-sp),'case_ids':ids}
  grid={a+'__'+b:sum(by[c,'shift']['joint_status']==a and by[c,'lowrank']['joint_status']==b for c in ids) for a in NAMES.values() for b in NAMES.values()}
  cross[name]={'n':len(ids),'both_confirmed':int(((lp==1)&(sp==1)).sum()),'only_lowrank_confirmed':int(((lp==1)&(sp==0)).sum()),'only_shift_confirmed':int(((lp==0)&(sp==1)).sum()),'neither_confirmed':int(((lp==0)&(sp==0)).sum()),'both_explicit_fail':grid['fail__fail'],'shift_row_lowrank_column_3x3':grid}
 dump(P/'summary.json',summary);dump(P/'paired_statistics.json',paired);dump(P/'paired_outcomes.json',cross)
 with (P/'summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=summary[0],lineterminator='\n');w.writeheader();w.writerows(summary)
 failures={}
 for path in ['shift','lowrank']:
  failed=[c for c in valid if by[c,path]['joint_status']=='fail'];failures[path]={'fixed_valid_failures':failed,'failures_with_both_recon_pass':[c for c in failed if c in subset],'failures_with_reconstruction_not_pass':[c for c in failed if c not in subset],'categories':dict(collections.Counter(t for c in failed for t in by[c,path]['error_categories'].split('|') if t))}
 dump(P/'failure_localization.json',failures)
 exact=[]
 for path in PATHS:
  rr=[o for o in outputs if o['path']==path];exact.append({'path':path,'n':len(rr),'exact_generation_input_n':sum(o['exact_input'] for o in rr),'exact_reference_n':sum(o['exact_reference'] for o in rr),'old_Joint_auto_n':sum(o['old_auto_diagnostic']['Joint_auto'] for o in rr),'old_auto_is_not_semantic_truth':True})
 dump(P/'auxiliary_exact_and_old_auto.json',exact)
 audit={'n_sources':100,'n_outputs':400,'reviewed_rows':len(records),'validity_counts':dict(collections.Counter(t['task_validity'] for t in tasks.values())),'subset_n':len(subset),'all_rows_retained':True,'human_ratings':0,'new_clean_candidate_files_used':False}
 dump(P/'analysis_audit.json',audit)
 print(json.dumps({'audit':audit,'fixed_valid':[r for r in summary if r['stratum']=='fixed_valid'],'paired':paired['fixed_valid'],'localization':failures},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
