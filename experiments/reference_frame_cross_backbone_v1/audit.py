from common import *
import importlib.util,collections

def main():
 lock=json.loads((ROOT/'data/lock.json').read_text())
 for f,h in lock['files'].items():assert digest(ROOT/'data'/f)==h,f
 assert digest(ROOT/'semantics_v1.py')==lock['scorer_hash'] and digest(ROOT/'common.py')==lock['common_hash']
 old=json.loads((ROOT/'old_readonly_manifest.json').read_text())
 for f,h in old.items():assert digest(REPO/f)==h,f
 for f in ['train_G1.jsonl','train_worlds.jsonl','dev_atomic.jsonl','dev_chains.jsonl','sample_schedule.jsonl']:
  assert digest(ROOT/'data'/f)==digest(V2/'data'/f)
 spec=importlib.util.spec_from_file_location('cross_prepare',ROOT/'prepare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 prior=[w for root in [V1,V2,V3] for p in (root/'data').glob('*worlds.jsonl') for w in [json.loads(l) for l in p.read_text().splitlines()]]
 class Used(set):
  collisions=0
  def __contains__(self,k):
   yes=super().__contains__(k)
   if yes:self.collisions+=1
   return yes
 used=Used(m.world_key(w) for w in prior)
 for j,s in enumerate(['test_iid','test_template_ood']):
  replay=m.build_worlds(s,80,2026092904+j,used)
  for w in replay:w['record_id']=w['record_id'].replace('v2_','cross_v1_')
  assert replay==read(f'data/{s}_worlds.jsonl')
 coverage=collections.Counter()
 for s in ['test_iid','test_template_ood']:
  for kind in ['atomic','chains']:
   for r in read(f'data/{s}_{kind}.jsonl'):
    for k,(op,off,support) in enumerate(zip(r['operations'],r['offsets'],r['source_support_G1'])):
     coverage[s,r['path'],k+1,op,off,r['record_status'],r['polarity'],support]+=1
     if op.startswith('T'):assert support
 csvwrite('evaluation/source_coverage.csv',[dict(split=k[0],path=k[1],step=k[2],operation=k[3],offset=k[4],status=k[5],polarity=k[6],covered=k[7],N=n) for k,n in coverage.items()])
 dump('evaluation/integrity_audit.json',dict(passed=True,old_files_unchanged=len(old),original_data_locks_unchanged=True,scorer_unchanged=True,new_world_generation_replay_identical=True,complete_fact_collisions_rejected=used.collisions,seed=2026092904,training_schedule_byte_identical=True,replaced_occurrences=sum(sum(b['g2_replace']) for b in read('data/sample_schedule.jsonl'))))
 print('audit passed; rejected full-fact collisions',used.collisions)
if __name__=='__main__':main()
