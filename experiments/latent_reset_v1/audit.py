"""Independent consistency checks for G6 outputs and stage-limited training."""
import json,sys
from pathlib import Path
import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent;V3=HERE.parent/'reference_frame_pilot_v3';G5=HERE.parent/'projection_hypothesis_v1';REPO=HERE.parents[1]
sys.path.insert(0,str(V3))
from common import score,digest
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def main():
 prov=json.loads((HERE/'provenance.json').read_text());run=json.loads((HERE/'run_complete.json').read_text())
 assert run['completed'] and run['rows']==530
 for key,p in [('g3_checkpoint_sha256',V3/'checkpoints/G3/best.pt'),('bart_sha256',REPO/'models/bart-base/model.safetensors'),('g5_provenance_sha256',G5/'provenance.json'),('g5_pure_sha256',G5/'pure_reset_controls.jsonl'),('g5_dre_sha256',G5/'decode_reencode_trajectories.jsonl'),('train_worlds_sha256',V3/'data/train_worlds.jsonl')]:assert prov[key]==digest(p),key
 for split,h in prov['test_world_files_sha256'].items():assert h==digest(V3/f'data/{split}_worlds.jsonl')
 assert run['reset_sha256']==digest(HERE/'reset.pt') and run['trajectories_sha256']==digest(HERE/'learned_trajectories.jsonl') and run['manifest_sha256']==digest(HERE/'train_manifest.jsonl')
 testids=set(sum(prov['world_ids'].values(),[]));train={w['record_id'] for w in rows(V3/'data/train_worlds.jsonl')};assert not testids.intersection(train)
 manifest=rows(HERE/'train_manifest.jsonl');assert manifest and all(r['stage'] in [1,2] and r['semantic_success'] and r['world_id'] in train for r in manifest)
 assert all(r['world_id'] not in testids for r in manifest)
 learned=rows(HERE/'learned_trajectories.jsonl');assert len(learned)==530
 worlds={w['record_id']:w for s in prov['world_ids'] for w in rows(V3/f'data/{s}_worlds.jsonl')}
 vectors=torch.load(HERE/'pooled_representations.pt',map_location='cpu',weights_only=False);assert len(vectors)==530
 max_error=0.;same_first=0;ids=set();source_continuity=0
 g5={(r['split'],r['world_id'],r['step']):r for r in rows(G5/'pure_reset_controls.jsonl')}
 idx={(r['split'],r['world_id'],r['step']):r for r in learned};assert len(idx)==530
 for r in learned:
  split,w,k=r['split'],r['world_id'],r['step'];ids.add((split,w,k));assert w in prov['world_ids'][split]
  world=worlds[w];f=r['gold_frame'];assert r['gold_text']==g5[split,w,k]['gold_text']
  for key,text,end in [('edited','edited_text','edited'),('reset','decoded_text','reset'),('oracle_mask','oracle_mask_text','oracle_mask')]:
   actual=score(r[text],f,world,r[end]['normal_end']);assert r[end]['success']==bool(actual['joint_ok']) and r[end]['fact_preservation']==bool(actual['nondate_facts_ok'])
  if k==1:
   assert r['source_text']==g5[split,w,k]['source_text'] and r['edited_text']==g5[split,w,k]['decoded_text']
   same_first+=1
  else:assert r['input_text']==idx[split,w,k-1]['decoded_text'];source_continuity+=1
  v=vectors[f'{split}/{w}/{k}'];g=v['gold']
  for key in ('edited','reset','oracle'):
   vec=v[key]
   cos=float(1-F.cosine_similarity(vec[None],g[None]).item());l2=float((vec-g).norm().item()/g.norm().item())
   max_error=max(max_error,abs(cos-r[key+'_distance']['cosine']),abs(l2-r[key+'_distance']['normalized_l2']))
  x=v['reset'];y=v['oracle'];max_error=max(max_error,abs(float((x-y).norm().item()/y.norm().item())-r['reset_to_oracle_distance']['normalized_l2']))
 assert same_first==106 and source_continuity==424 and max_error<1e-5
 report=dict(ok=True,checkpoint_sha256=run['reset_sha256'],g3_checkpoint_sha256=prov['g3_checkpoint_sha256'],train_manifest_rows=len(manifest),train_stages=sorted({r['stage'] for r in manifest}),test_rows=len(learned),test_worlds=len(testids),first_step_source_matches= same_first,continuity_checks=source_continuity,recomputed_scores=3*len(learned),max_distance_error=max_error,train_test_world_overlap=0)
 (HERE/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
