import csv
from datetime import datetime
from task import *
def main():
 assert_lock()
 old=json.loads((ROOT/'old_readonly_manifest.json').read_text())
 for f,h in old.items():assert digest(REPO/f)==h,f
 for f,h in json.loads((ROOT/'training_code_manifest.json').read_text()).items():assert digest(ROOT/f)==h,f
 for f,h in json.loads((ROOT/'evaluation_code_manifest.json').read_text()).items():assert digest(ROOT/f)==h,f
 assert json.loads((ROOT/'model_environment_audit.json').read_text())['passed']
 w=worlds();support=support_counts();train=read('data/train_joint.jsonl');schedule=read('data/sample_schedule.jsonl');counts=collections.Counter(train[i]['record_id'] for b in schedule for i in b['pair_indices']);assert len(schedule)==600 and set(counts.values())=={20}
 # Independence by the full facts, not only IDs or texts.
 prior={world_key(x) for root in [V1,V2,V3,CROSS] for p in (root/'data').glob('*worlds.jsonl') for x in read(p)};newkeys=[]
 for split in ['test_iid','test_template_ood']:
  for r in read(f'data/{split}_joint.jsonl'):
   assert joint_row(w[r['record_id']],r['source_offset'],support)==r
   key=world_key(w[r['record_id']]);assert key not in prior;newkeys.append(key)
 assert len(newkeys)==len(set(newkeys))==160
 complete=json.loads((ROOT/'evaluation/complete.json').read_text());expected={r['record_id']:r for s in ['test_iid','test_template_ood'] for r in read(f'data/{s}_joint.jsonl')}
 for method in complete['methods']:
  rows=read(f'outputs/{method}.jsonl');assert len(rows)==160 and {r['record_id'] for r in rows}==set(expected)
  for r in rows:
   for f in ['source_text','target_text','source_frame','target_frame','orders']:assert r[f]==expected[r['record_id']][f]
   assert r['endpoint_joint']==r['steps'][-1]['score']['joint_ok']
   if method.startswith('Sequential'):assert r['trajectory_joint']==all(s['score']['joint_ok'] for s in r['steps'])
   else:assert r['trajectory_joint'] is None and len(r['steps'])==1
   assert all(s['input_mask_length']==r['source_tokens'] for s in r['steps'])
   for s in r['steps']:
    if s['score']['parse_unresolved'] or not s['ended']:assert not s['score']['joint_ok']
 for rank in [16,32]:
  folder=ROOT/f'checkpoints/Joint{rank}';c=json.loads((folder/'complete.json').read_text());log=read(folder/'training_log.jsonl')
  assert c['updates']==600 and len(log)==600 and [x['step'] for x in log]==list(range(1,601))
  assert c['beststep']==min(c['history'],key=lambda r:(r['dev_target_token_nll'],r['step']))['step']
  assert c['checkpoint_hash']==digest(folder/'best.pt')==complete['provenance']['joints'][f'Joint{rank}']
  assert c['supervision_tokens']==sum(r['target_tokens'] for r in log)
 selected=json.loads((ROOT/'review/selected_worlds.json').read_text());assert len(selected)==20 and len(set(selected))==20
 assert digest(ROOT/'review/selected_worlds.json')==json.loads((ROOT/'review/selection_lock.json').read_text())['selected_worlds_sha256']
 assert {r['record_id'] for r in read('review/cases.jsonl')}==set(selected)
 assert all(not r['human_label'] and not r['human_notes'] for r in csv.DictReader((ROOT/'review/blind_review.csv').open()))
 b=json.loads((ROOT/'budget.json').read_text());events=[]
 for j in b['jobs']:
  assert j['state']=='COMPLETED' and 'gres/gpu=1' in j['allocation'];events += [(datetime.fromisoformat(j['start']),1),(datetime.fromisoformat(j['end']),-1)]
 active=peak=0
 for t,d in sorted(events):active+=d;peak=max(peak,active)
 assert active==0 and peak<=2 and b['total_gpu_seconds']<=7200
 dump('evaluation/final_checks.json',dict(passed=True,old_files_unchanged=len(old),data_code_locks_unchanged=True,common_sources_targets=True,world_overlap=0,worlds=160,methods=len(complete['methods']),outputs=960,training_updates_per_rank=600,each_training_world_occurrences=20,selected_case_worlds=20,human_labels=0,peak_concurrent_gpus=peak,gpu_seconds=b['total_gpu_seconds']))
 print('final checks passed')
if __name__=='__main__':main()
