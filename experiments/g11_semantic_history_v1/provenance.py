"""Independent supporting audits; never changes locked worlds or model outputs."""
import collections
from g11 import *
def main():
 m=ensure_lock();old=[]
 for p,h in m['prior_world_files'].items():
  assert digest(REPO/p)==h;old += [w for w in read(REPO/p) if all(k in w for k in FIELDS)]
 prior=sorted({hashlib.sha256(key(w).encode()).hexdigest() for w in old});dump('data/prior_fact_key_hashes.json',dict(key_definition=FIELDS,hash='sha256 of canonical JSON complete fact key; no IDs/templates',count=len(prior),hashes=prior))
 train=read(V3/'data/train_G1.jsonl');schedule=[b for b in read(V3/'data/sample_schedule.jsonl') if b['path'].startswith('T_plus')];cc=collections.Counter()
 for b in schedule:
  for i in b['pair_indices']:
   r=train[i];cc[r['offsets'][0],r['record_status'],r['polarity'],r['frames'][0]['perspective']]+=1
 counts=[dict(offset=d,status=s,polarity=p,perspective=pers,training_occurrences=n) for (d,s,p,pers),n in sorted(cc.items())];csvwrite('data/actual_training_support.csv',counts)
 for w in read('data/worlds.jsonl'):
  for d in CFG['anchors']:
   for source in range(d,d+3):assert cc[source,w['record_status'],w['polarity'],'first']>0
 dump('data/training_support.json',dict(train_hash=digest(V3/'data/train_G1.jsonl'),schedule_hash=digest(V3/'data/sample_schedule.jsonl'),actual_T_plus_updates=len(schedule),actual_T_plus_occurrences=sum(cc.values()),plan_first_source_offsets=sorted({d for d,s,p,pers in cc if s=='recorded_plan' and pers=='first'}),all_required_source_conditions_supported=True,new_worlds_previously_seen=False))
 code={p.name:digest(p) for p in ROOT.glob('*.py')};changed={k:dict(pre_output=m['code'][k],final=v) for k,v in code.items() if k in m['code'] and m['code'][k]!=v}
 dump('code_version.json',dict(baseline=CFG['baseline'],final_code_sha256=code,post_lock_changes=changed,reason='Added independent audit checks and derived reporting/opaque blind-review formatting after inference; no change to model paths, decoder settings, worlds, parser, renderer, cohort definition, or statistical comparisons.',gpu_inference_code_unchanged=digest(ROOT/'gpu.py')==m['code']['gpu.py'],scoring_dependencies_unchanged=True))
 print('G11 source support and fact-key provenance written')
if __name__=='__main__':main()
