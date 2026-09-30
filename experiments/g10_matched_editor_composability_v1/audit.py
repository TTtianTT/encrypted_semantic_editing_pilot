"""Recompute locked-data, matched-cohort, output, and resource provenance checks."""
import collections,json,sys
from g10_common import *
sys.path.insert(0,str(V3))
from common import score,advance,render
CFG=json.loads((ROOT/'config.json').read_text())

def main():
 lock=json.loads((ROOT/'data/lock.json').read_text())
 assert all(digest(REPO/f)==h for f,h in lock['code'].items())
 assert digest(ROOT/'config.json')==lock['config_sha256'] and digest(ROOT/'PROTOCOL.md')==lock['protocol_sha256']
 for f,h in lock['files'].items():assert digest(ROOT/'data'/f)==h,f
 for f,h in lock['source_artifacts'].items():assert digest(REPO/f)==h,f
 prior=[]
 for root in [V1,V2,V3,G7.parent/'projection_hypothesis_v1',G9]:
  if (root/'data').exists():
   for p in (root/'data').glob('*worlds.jsonl'):prior+=read(p)
 import importlib.util
 sys.path.insert(0,str(V3));sp=importlib.util.spec_from_file_location('g10_audit_v3_prepare',V3/'prepare.py');vp=importlib.util.module_from_spec(sp);sp.loader.exec_module(vp)
 oldkeys={vp.world_key(w) for w in prior};new=[]
 for split in ['match_iid','match_template_ood','composition_iid','composition_template_ood']:
  ws=read(f'data/{split}_worlds.jsonl');assert len(ws)==80 and all(w['record_status']=='recorded_plan' for w in ws)
  assert not oldkeys.intersection(vp.world_key(w) for w in ws);new += [vp.world_key(w) for w in ws]
 assert len(new)==len(set(new))==320
 sched=[x for x in read(V3/'data/sample_schedule.jsonl') if x['path'].startswith('T_plus')];assert len(sched)==200 and sum(sum(x['g2_replace']) for x in sched)==1600
 sm=[]
 for rank in CFG['ranks']:
  m=json.loads((ROOT/f'training/rank{rank}.json').read_text());assert len(m)==3
  for x in m:
   assert x['updates']==200 and x['counts']['supervised_samples']==3200
   assert x['counts']['supervision_tokens']>0 and x['parameters']==2*768*rank+768
   assert x['checkpoint_sha256']==digest(ROOT/x['checkpoint']) if 'checkpoint' in x else x['checkpoint_sha256']==digest(ROOT/f"checkpoints/rank{rank}/{x['editor']}.pt")
  sm += m
 assert len({x['counts']['supervision_tokens'] for x in sm})==1
 gate=json.loads((ROOT/'evaluation/gate_lock.json').read_text());retained=set(gate['matched_editors'])
 import csv
 match=list(csv.DictReader((ROOT/'evaluation/matching_gate.csv').open()));assert len(match)==18
 outputs=read('outputs/matching_gate.jsonl');assert len(outputs)==1440
 manifest=json.loads((ROOT/'evaluation/trajectory_manifest.json').read_text())
 per_editor={x['editor']:read(f"outputs/trajectory_{x['editor']}.jsonl") for x in manifest}
 assert set(per_editor)=={x['editor'] for x in manifest}
 for ident,rows in per_editor.items():
  should=800 if ident in retained else 160
  assert len(rows)==should,(ident,len(rows),should)
  for split in ['composition_iid','composition_template_ood']:
   sub=[x for x in rows if x['split']==split];assert len(sub)==(400 if ident in retained else 80)
   assert len({x['record_id'] for x in sub})==80
   if ident in retained:
    assert all(sum(x['record_id']==rid and x['step']==k for x in sub)==1 for rid in {x['record_id'] for x in sub} for k in range(1,6))
 for ident in retained:
  p=json.loads((ROOT/f'basin/{ident}.json').read_text());assert p['states']>0 and p['scan_points']>0
  assert p['checkpoint_sha256']==digest(ROOT/f"checkpoints/rank{int(ident.split('_')[0][4:])}/{ident}.pt")
  assert p['states_sha256']==digest(ROOT/f'basin/states_{ident}.jsonl') and p['scan_sha256']==digest(ROOT/f'basin/scan_{ident}.jsonl')
  scans=read(f'basin/scan_{ident}.jsonl');assert all(x['direction'] in CFG['directions'] for x in scans)
  assert all(float(x['effective_norm_ratio'])>0.999 for x in scans)
 dump('evaluation/audit.json',dict(ok=True,locked_code=len(lock['code']),prior_worlds=len(prior),new_fact_unique_worlds=320,
   train_updates_each=200,train_samples_each=3200,supervision_tokens_per_editor=sm[0]['counts']['supervision_tokens'],
   matched=sorted(retained),candidate_count=9,matching_output_rows=1440,test_worlds_per_stratum=80,
   trajectory_rows=sum(map(len,per_editor.values())),basin_editor_count=len(retained),old_experiments_mutated=False))
 print('G10 audit passed',len(retained),'matched editors',flush=True)
if __name__=='__main__':main()
