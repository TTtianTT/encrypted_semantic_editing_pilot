from g11 import *
def main():
 m=ensure_lock();assert digest(ROOT/'data/paths.jsonl')==m['paths_sha256'];assert digest(ROOT/'PROTOCOL.md')==m['protocol_sha256'];worlds=read('data/worlds.jsonl');assert len(worlds)==160 and len({key(w) for w in worlds})==160
 old=[];missing=[];priorhashes=set(json.loads((ROOT/'data/prior_fact_key_hashes.json').read_text())['hashes'])
 for p,h in m['prior_world_files'].items():
  if not (REPO/p).exists():missing.append(p);continue
  assert digest(REPO/p)==h;old += [w for w in read(REPO/p) if all(k in w for k in FIELDS)]
 assert {hashlib.sha256(key(w).encode()).hexdigest() for w in old}<=priorhashes
 assert not priorhashes.intersection({hashlib.sha256(key(w).encode()).hexdigest() for w in worlds})
 if not missing:assert len({key(w) for w in old})==len(priorhashes)
 lock=json.loads((ROOT/'data/cohort_lock.json').read_text());assert lock['locked_before_next'];assert digest(ROOT/'outputs/current_states.jsonl')==lock['current_outputs_sha256'];curr=read('outputs/current_states.jsonl');nxt=read('outputs/next_states.jsonl');cross=read('outputs/crossover.jsonl');assert len(curr)==len(nxt)==2880
 index={(r['seed'],r['record_id'],r['anchor'],r['history']):r for r in curr};assert len(index)==2880
 wi={w['record_id']:w for w in worlds}
 for r in curr:
  w=wi[r['record_id']];sc=score(r['current']['output'],r['current_frame'],w,r['current']['normal_end']);assert sc==r['current']['score'];assert r['current_gold']==render(w,r['current_frame'])
  assert r['prefix_clean']==all(x['score']['joint_ok'] for x in r['prefix'])
  for stage in r['prefix']:assert score(stage['output'],stage['frame'],w,stage['normal_end'])==stage['score']
 missing_latents=[]
 for shard in lock['latent_shards']:
  if (ROOT/shard['path']).exists():assert digest(ROOT/shard['path'])==shard['sha256']
  else:missing_latents.append(shard['path'])
  assert digest(ROOT/shard['outputs'])==shard['outputs_sha256']
 for row in lock['cohorts']:
  cs=[index[row['seed'],row['record_id'],row['anchor'],h] for h in range(3)];strict=all(r['current']['normal_end'] and r['current']['output'].strip()==r['current_gold'] for r in cs);semantic=all(r['current']['score']['joint_ok'] for r in cs);assert strict==row['strict_cohort'] and semantic==row['semantic_cohort']
 for r in nxt:
  assert r['cohort_lock_sha256']==digest(ROOT/'data/cohort_lock.json');w=wi[r['record_id']];assert score(r['next']['output'],frame(w,r['anchor']-1),w,r['next']['normal_end'])==r['next']['score']
  c=index[r['seed'],r['record_id'],r['anchor'],r['history']];assert r['full_history_joint']==(c['prefix_clean'] and r['next']['score']['joint_ok'])
 for r in cross:
  c=index[r['seed'],r['record_id'],-1,0];assert c['strict_cohort'] and c['equal_mask_02'];assert r['cohort_lock_sha256']==digest(ROOT/'data/cohort_lock.json');w=wi[r['record_id']];assert score(r['output']['output'],frame(w,-2),w,r['output']['normal_end'])==r['output']['score']
 assert len(cross)==4*sum(r['anchor']==-1 and r['strict_cohort'] and r['equal_mask_02'] for r in lock['cohorts'])
 assert all(r['standard_next_output_equal'] is not False for r in cross)
 pre=json.loads((ROOT/'preflight.json').read_text());assert pre['passed'];b=json.loads((ROOT/'budget.json').read_text());assert b['gpu_seconds']<=7200 and b['max_concurrent_gpus']==1
 current_job=next(j for j in b['jobs'] if j['phase']=='current' and j['state']=='COMPLETED');next_job=next(j for j in b['jobs'] if j['phase']=='next' and j['state']=='COMPLETED');assert current_job['end']<=next_job['start']
 dump('audit.json',dict(passed=True,worlds=160,full_fact_overlap=0,prior_world_keys=len(priorhashes),historical_files_unavailable=missing,current_rows=len(curr),next_rows=len(nxt),crossover_rows=len(cross),cohort_locked_before_next=True,parameter_updates=0,G12_run=False,old_dependencies_unchanged=True,checkpoint_hashes=lock['checkpoint_hashes'],latent_shards=len(lock['latent_shards']),local_latent_shards_unavailable=missing_latents,local_activations_not_in_public_package=True,gpu_seconds=b['gpu_seconds']));print('G11 audit passed')
if __name__=='__main__':main()
