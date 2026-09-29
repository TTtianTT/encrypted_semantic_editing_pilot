"""Audit G7 split isolation, stage labels, frozen checkpoints, and legacy agreement."""
import json,sys,math,csv
from pathlib import Path
import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent;V3=HERE.parent/'reference_frame_pilot_v3';G5=HERE.parent/'projection_hypothesis_v1';T5=HERE.parent/'t5gemma_composition_v1'
sys.path.insert(0,str(V3))
from common import frame,advance,score,digest
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]

def spectral(state,prefix,hidden,seed=42):
 U=state[prefix+'u.weight'].float();V=state[prefix+'v.weight'].float()
 gen=torch.Generator().manual_seed(seed);z=F.normalize(torch.randn(hidden,generator=gen),dim=0)
 J=lambda x:x+F.linear(F.linear(x,V),U)
 JT=lambda x:x+F.linear(F.linear(x,U.T),V.T)
 for _ in range(80):z=F.normalize(JT(J(z)),dim=0)
 return float(J(z).norm())

def main():
 cfg=json.loads((HERE/'config.json').read_text());g5=json.loads((G5/'provenance.json').read_text())
 train={w['record_id']:w for w in rows(V3/'data/train_worlds.jsonl') if w['record_status']=='recorded_plan'}
 dev={w['record_id']:w for w in rows(V3/'data/dev_worlds.jsonl') if w['record_status']=='recorded_plan'}
 tests={s:{w['record_id']:w for w in rows(V3/f'data/{s}_worlds.jsonl')} for s in g5['world_ids']}
 assert len(train)==160 and len(dev)==27 and not (set(train)&set(dev)) and not (set(train)|set(dev))&set(sum(g5['world_ids'].values(),[]))
 counts={};max_jac_error=0.;score_checks=0;label_checks=0;finite_checks=0;test_labels={}
 for name,checkpoint,prefix,hidden in [('BART',V3/'checkpoints/G3/best.pt','T_plus.',768),('T5Gemma',T5/'editor_best.pt','',2304)]:
  slug=name.lower();provenance=json.loads((HERE/f'extraction_{slug}.json').read_text());agree=json.loads((HERE/f'agreement_{slug}.json').read_text())
  assert provenance['backbone']==name and provenance['editor_sha256']==digest(checkpoint) and provenance['g5_provenance_sha256']==digest(G5/'provenance.json')
  assert provenance['editor_training']=='none' and provenance['base_training']=='none'
  assert agree['n']==agree['decoded_exact']==agree['success_same']==530 and agree['max_pooled_l2_delta']<1e-3
  state=torch.load(checkpoint,map_location='cpu',weights_only=True);j=spectral(state,prefix,hidden)
  max_jac_error=max(max_jac_error,abs(j-provenance['jacobian_spectral_norm']))
  records=rows(HERE/f'features_{slug}.jsonl');assert len(records)==1465 and provenance['features_sha256']==digest(HERE/f'features_{slug}.jsonl')
  index={(r['split'],r['world_id'],r['step']):r for r in records};assert len(index)==len(records)
  counts[name]={s:sum(r['split']==s for r in records) for s in ['train','dev','test_iid','test_template_ood']}
  assert counts[name]=={'train':800,'dev':135,'test_iid':265,'test_template_ood':265}
  for r in records:
   s,w,k=r['split'],r['world_id'],r['step'];assert 1<=k<=5
   world=(train if s=='train' else dev if s=='dev' else tests[s])[w]
   f=frame(world,1)
   for _ in range(k):f=advance(f,'T_plus')
   q=score(r['decoded_text'],f,world,r['normal_end'])
   assert r['current_success']==bool(q['joint_ok']) and r['fact_preservation']==bool(q['nondate_facts_ok']);score_checks+=1
   if k<5:
    nextrow=index[s,w,k+1]
    assert r['next_success']==nextrow['current_success'] and r['next_failure']==(not nextrow['current_success']);label_checks+=1
    if s.startswith('test_') and r['current_success']:test_labels[name,s,w,k]=int(r['next_failure'])
   else:assert r['next_success'] is None and r['next_failure'] is None
   for field in ('pooled_l2','pooled_cosine_distance','token_l2','token_cosine_distance','token_gram_rms','token_spread_log_ratio','target_nll','target_worst_token_nll','output_entropy','output_top1_margin','residual_norm','jvp_residual_gain','jacobian_spectral_norm'):
    assert r[field] is not None and math.isfinite(r[field]),(name,s,w,k,field);finite_checks+=1
   assert abs(r['jacobian_spectral_norm']-provenance['jacobian_spectral_norm'])<1e-7
 assert max_jac_error<1e-3
 comparison=list(csv.DictReader((HERE/'predictor_comparison.csv').open()))
 predictions=list(csv.DictReader((HERE/'test_predictions.csv').open()))
 assert len(comparison)==210 and len(predictions)==21*len(test_labels)
 for r in predictions:
  key=r['backbone'],r['split'],r['world_id'],int(r['step'])
  assert key in test_labels and int(r['next_failure']=='True')==test_labels[key]
  assert (r['predicted_failure']=='True')==(float(r['score'])>=float(r['threshold']))
 result=dict(ok=True,config_sha256=digest(HERE/'config.json'),records_per_backbone=counts,train_test_overlap=0,legacy_exact_text_matches={'BART':530,'T5Gemma':530},recomputed_scores=score_checks,next_step_link_checks=label_checks,finite_feature_checks=finite_checks,analysis_rows=len(comparison),test_prediction_rows=len(predictions),test_prediction_label_checks=len(predictions),analytic_affine_jacobian_state_independent=True,max_spectral_recompute_error=max_jac_error)
 (HERE/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
