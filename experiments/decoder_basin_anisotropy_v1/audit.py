"""Audit frozen checkpoints, matched directions, scores, and G7 trajectory links."""
import csv,json,math,sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent;G7=HERE.parent/'repeated_intervention_stability_v1';V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(V3))
from common import digest,frame,advance,score

def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def key(r):return r['backbone'],r['split'],r['world_id'],r['step']

def main():
 cfg=json.loads((HERE/'config.json').read_text());seen_worlds={};counts={};alpha_checks=0;norm_checks=0;score_checks=0;trajectory_checks=0
 worlds={split:{w['record_id']:w for w in read(V3/f'data/{split}_worlds.jsonl')} for split in ('train','dev','test_iid','test_template_ood')}
 for backbone in cfg['backbones']:
  slug=backbone.lower();provenance=json.loads((HERE/f'extraction_{slug}.json').read_text())
  states=read(HERE/f'states_{slug}.jsonl');scan=read(HERE/f'scan_{slug}.jsonl')
  source=read(G7/f'features_{slug}.jsonl');g7={(r['split'],r['world_id'],r['step']):r for r in source}
  assert not provenance['pilot'] and provenance['editor_training']=='none' and provenance['base_training']=='none'
  assert provenance['config']==cfg
  assert provenance['g7_features_sha256']==digest(G7/f'features_{slug}.jsonl')
  assert provenance['states_sha256']==digest(HERE/f'states_{slug}.jsonl') and provenance['scan_sha256']==digest(HERE/f'scan_{slug}.jsonl')
  if backbone=='T5Gemma' and provenance.get('source_jobs'):
   partial_states=HERE/'premerge_states_t5gemma.jsonl';partial_scan=HERE/'premerge_scan_t5gemma.jsonl'
   shard_states=HERE/'test_template_ood_states_t5gemma.jsonl';shard_scan=HERE/'test_template_ood_scan_t5gemma.jsonl'
   hashes=provenance['merge_source_sha256']
   assert digest(partial_states)==hashes['states_t5gemma.jsonl'] and digest(partial_scan)==hashes['scan_t5gemma.jsonl']
   assert digest(shard_states)==hashes[shard_states.name] and digest(shard_scan)==hashes[shard_scan.name]
   assert [r for r in read(partial_states) if r['split']!='test_template_ood']+read(shard_states)==states
   assert [r for r in read(partial_scan) if r['split']!='test_template_ood']+read(shard_scan)==scan
  assert provenance['editor_sha256']==digest(HERE.parents[1]/cfg['frozen_editor_sources'][backbone])
  assert provenance['states']==len(states) and provenance['scan_rows']==len(scan)
  idx={key(s):s for s in states};assert len(idx)==len(states)
  group=defaultdict(list)
  for r in scan:
   assert key(r) in idx and r['direction'] in cfg['directions'] and r['alpha']>0
   group[key(r),r['direction']].append(r)
   assert r['corridor_success']==(r['current_gold_success'] or r['next_gold_success'])
   assert not r['corridor_success'] or r['content_compatible']
   world=worlds[r['split']][r['world_id']];current=frame(world,1)
   for _ in range(r['step']):current=advance(current,'T_plus')
   following=advance(current,'T_plus')
   q0=score(r['decoded_text'],current,world,r['normal_end']);q1=score(r['decoded_text'],following,world,r['normal_end'])
   assert r['current_gold_success']==bool(q0['joint_ok']) and r['next_gold_success']==bool(q1['joint_ok'])
   assert r['parseable']==bool(q0['readable']) and r['fact_preservation']==bool(q0['nondate_facts_ok'])
   assert r['content_compatible']==bool(q0['readable'] and q0['nondate_facts_ok'] and r['normal_end'])
   for field in ('target_nll_current','target_nll_next','target_nll_best','output_entropy','output_top1_margin','effective_norm_ratio'):
    assert r[field] is not None and math.isfinite(r[field]),(key(r),r['direction'],r['alpha'],field)
   assert abs(r['effective_norm_ratio']-1)<.05,(key(r),r['direction'],r['alpha'],r['effective_norm_ratio'])
   score_checks+=1;norm_checks+=1
  for s in states:
   sk=key(s);old=g7[s['split'],s['world_id'],s['step']]
   assert old['current_success'] and s['next_failure']==old['next_failure']
   assert s['g7_current_text_exact']==(s['current_decoded_text']==old['decoded_text'])
   assert 0<=s['decode_slot_offset']<5
   if backbone=='BART':assert s['decode_slot_offset']==0
   assert s['next_original_decoded_text']==g7[s['split'],s['world_id'],s['step']+1]['decoded_text']
   assert abs(s['directions']['editor_forward']['cosine_to_editor']-1)<1e-5
   assert abs(s['directions']['editor_reverse']['cosine_to_editor']+1)<1e-5
   assert abs(s['directions']['radial_orthogonal_random']['cosine_to_state'])<1e-5
   assert abs(s['directions']['editor_orthogonal_random']['cosine_to_editor'])<1e-5
   norms=[s['directions'][d]['norm'] for d in cfg['directions']]
   assert max(abs(n/s['residual_norm']-1) for n in norms)<1e-5
   for d in cfg['directions']:
    rr=group[sk,d];coarse=[r for r in rr if r['alpha'] in cfg['coarse_alpha']]
    assert len(coarse)==len(cfg['coarse_alpha']) and {r['alpha'] for r in coarse}==set(cfg['coarse_alpha'])
    assert len(rr)<=len(cfg['coarse_alpha'])+cfg['refinement_rounds']
    alpha_checks+=len(rr)
   edit_one=next(r for r in group[sk,'editor_forward'] if r['alpha']==1.)
   assert edit_one['decoded_text']==s['alpha_one_decoded_text']
   assert edit_one['next_gold_success']==s['alpha_one_next_gold_success']
   assert s['alpha_one_match_g7']==(edit_one['decoded_text']==s['next_original_decoded_text'])
   trajectory_checks+=1
  counts[backbone]=dict(states=len(states),scan=len(scan),splits={split:sum(s['split']==split for s in states) for split in provenance['world_ids']},
                        baseline_text_exact=provenance['baseline_text_exact'],baseline_checks=provenance['baseline_checks'],
                        alpha_one_text_exact=provenance['alpha_one_next_state_exact'],
                        alpha_one_semantic_same=provenance['alpha_one_next_semantic_same'],
                        candidate_slot_counts={str(i):sum(s['decode_slot_offset']==i for s in states) for i in range(5)})
  seen_worlds[backbone]={split:set(ids) for split,ids in provenance['world_ids'].items()}
  assert not (seen_worlds[backbone]['train']|seen_worlds[backbone]['dev'])&(seen_worlds[backbone]['test_iid']|seen_worlds[backbone]['test_template_ood'])
 assert seen_worlds['BART']==seen_worlds['T5Gemma']
 radii=list(csv.DictReader((HERE/'directional_radii.csv').open()));paired=list(csv.DictReader((HERE/'paired_bootstrap.csv').open()))
 summary=list(csv.DictReader((HERE/'radius_summary.csv').open()))
 assert len(radii)==5*sum(x['states'] for x in counts.values()) and len(paired)==48 and len(summary)>0
 radius_index={(r['backbone'],r['split'],r['world_id'],int(r['step']),r['direction']):r for r in radii}
 assert len(radius_index)==len(radii)
 for r in radii:
  low=float(r['radius_lower']);high=float(r['radius_upper']) if r['radius_upper'] else None
  assert 0<=low<=cfg['radius_cap'] and (high is None or low<high<=cfg['radius_cap'])
  assert 0<=float(r['radius_capped'])<=cfg['radius_cap'] and 0<=float(r['content_radius_capped'])<=cfg['radius_cap']
 paired_means_checked=0
 for p in paired:
  b,split,control=p['backbone'],p['split'],p['control'];field='radius_capped' if p['endpoint']=='semantic_corridor' else 'content_radius_capped'
  targets=sorted({(r['split'],r['world_id'],int(r['step'])) for r in radii if r['backbone']==b and (r['split']==split or split=='test_combined' and r['split'].startswith('test_'))})
  diffs=[float(radius_index[b,s,w,k,'editor_forward'][field])-float(radius_index[b,s,w,k,control][field]) for s,w,k in targets]
  assert len(diffs)==int(p['n_states']) and abs(sum(diffs)/len(diffs)-float(p['mean_edit_minus_control']))<1e-9
  paired_means_checked+=1
 result=dict(ok=True,config_sha256=digest(HERE/'config.json'),counts=counts,world_split_overlap=0,
             same_world_ids_across_backbones=True,alpha_one_state_links_checked=trajectory_checks,
             candidate_score_checks=score_checks,candidate_norm_checks=norm_checks,alpha_grid_checks=alpha_checks,
             radii_rows=len(radii),radius_summary_rows=len(summary),paired_bootstrap_rows=len(paired),paired_means_checked=paired_means_checked)
 (HERE/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result)

if __name__=='__main__':main()
