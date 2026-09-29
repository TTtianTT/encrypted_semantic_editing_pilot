"""Recompute scores, geometry, pairing and frozen-training boundaries."""
import json,sys,hashlib
from pathlib import Path
import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent;V3=HERE.parent/'reference_frame_pilot_v3';G5=HERE.parent/'projection_hypothesis_v1'
sys.path.insert(0,str(V3))
from common import score,frame,digest
def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def streaming_sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while chunk:=f.read(8*1024*1024):h.update(chunk)
 return h.hexdigest()
def main():
 t=json.loads((HERE/'training_provenance.json').read_text());p=json.loads((HERE/'eval_provenance.json').read_text());e=json.loads((HERE/'eval_complete.json').read_text())
 assert e['completed'] and e['trajectory_rows']==1060 and t['backbone_trainable_parameters']==0 and t['trained_operators']==['T_plus'] and not t['long_chain_training']
 for field,path in [('model_config_sha256',Path(t['local_model'])/'config.json'),('model_index_sha256',Path(t['local_model'])/'model.safetensors.index.json'),('tokenizer_sha256',Path(t['local_model'])/'tokenizer.json'),('train_rows_sha256',V3/'data/train_G1.jsonl'),('train_worlds_sha256',V3/'data/train_worlds.jsonl'),('schedule_sha256',V3/'data/sample_schedule.jsonl'),('dev_atomic_sha256',V3/'data/dev_atomic.jsonl'),('editor_best_sha256',HERE/'editor_best.pt')]:assert t[field]==digest(path),field
 trainrows=read(V3/'data/train_G1.jsonl')
 schedule=[b for b in read(V3/'data/sample_schedule.jsonl') if b['path'].startswith('T_plus')]
 assert len(schedule)==200 and all(trainrows[i]['operations']==['T_plus'] and len(trainrows[i]['frames'])==2 for b in schedule for i in b['pair_indices'])
 manifest=json.loads((HERE/'base_model_manifest.json').read_text())
 assert manifest['local_directory']==t['local_model']
 for name,sha in manifest['weight_files_sha256'].items():assert streaming_sha(Path(t['local_model'])/name)==sha,name
 assert p['editor_checkpoint_sha256']==digest(HERE/'editor_best.pt') and p['train_provenance_sha256']==digest(HERE/'training_provenance.json') and p['g5_provenance_sha256']==digest(G5/'provenance.json')
 for s,h in p['world_file_sha256'].items():assert h==digest(V3/f'data/{s}_worlds.jsonl')
 assert e['trajectories_sha256']==digest(HERE/'trajectories.jsonl') and e['vectors_sha256']==digest(HERE/'pooled_representations.pt')
 trainids={w['record_id'] for w in read(V3/'data/train_worlds.jsonl')};testids=set(sum(p['world_ids'].values(),[]));assert not trainids.intersection(testids)
 worlds={w['record_id']:w for s in p['world_ids'] for w in read(V3/f'data/{s}_worlds.jsonl')}
 bart={(r['split'],r['world_id'],r['step']):r for r in read(G5/'pure_reset_controls.jsonl')}
 rows=read(HERE/'trajectories.jsonl');idx={(r['path'],r['split'],r['world_id'],r['step']):r for r in rows};assert len(idx)==1060
 vectors=torch.load(HERE/'pooled_representations.pt',map_location='cpu',weights_only=False);assert len(vectors)==1060
 err=0.;scored=0;matched=0;first_matches=0;continuity=0
 for r in rows:
  path,s,w,k=r['path'],r['split'],r['world_id'],r['step'];assert path in ('pure_latent','decode_reencode') and w in p['world_ids'][s] and 1<=k<=5
  b=bart[s,w,k];assert r['source_text']==bart[s,w,1]['source_text'] and r['gold_text']==b['gold_text'] and r['gold_frame']==b['gold_frame'];matched+=1
  actual=score(r['decoded_text'],r['gold_frame'],worlds[w],r['edited']['normal_end']);assert r['edited']['success']==bool(actual['joint_ok']) and r['edited']['fact_preservation']==bool(actual['nondate_facts_ok']);scored+=1
  if k==1:
   assert r['input_text']==r['source_text'];first_matches+=1
  elif path=='decode_reencode':
   assert r['input_text']==idx[path,s,w,k-1]['decoded_text'];continuity+=1
  v=vectors[f'{path}/{s}/{w}/{k}'];g=v['gold']
  for key in ('edited','reset'):
   x=v[key];cos=float(1-F.cosine_similarity(x[None],g[None]).item());l2=float((x-g).norm().item()/g.norm().item())
   err=max(err,abs(cos-r[key+'_distance']['cosine']),abs(l2-r[key+'_distance']['normalized_l2']))
 for r in read(HERE/'identity_controls.jsonl'):
  assert r['score']['success']==bool(score(r['decoded_text'],frame(worlds[r['world_id']],1),worlds[r['world_id']],r['score']['normal_end'])['joint_ok']);scored+=1
 for r in read(HERE/'gold_autoencode_controls.jsonl'):
  assert r['score']['success']==bool(score(r['decoded_text'],bart[r['split'],r['world_id'],r['step']]['gold_frame'],worlds[r['world_id']],r['score']['normal_end'])['joint_ok']);scored+=1
 assert matched==1060 and first_matches==212 and continuity==424 and scored==1696 and err<1e-5
 report=dict(ok=True,model=t['base_model'],editor_checkpoint_sha256=t['editor_best_sha256'],train_test_world_overlap=0,trained_operators=t['trained_operators'],long_chain_training=False,test_worlds=len(testids),paired_rows=matched,first_step_source_matches=first_matches,dre_chain_continuity_checks=continuity,recomputed_scores=scored,max_pooled_distance_error=err)
 (HERE/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
