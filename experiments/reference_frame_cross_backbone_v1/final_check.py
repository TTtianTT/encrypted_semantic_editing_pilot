"""Delivery checks for fixed denominators, trajectory intersections and provenance."""
import collections
from datetime import datetime
from common import *
from audit import main as audit_data

def main():
 audit_data()
 for f,h in json.loads((ROOT/'training_code_manifest.json').read_text()).items():assert digest(ROOT/f)==h,f
 results={};expected={r['row_id']:r for split in ['test_iid','test_template_ood'] for kind in ['atomic','chains'] for r in read(f'data/{split}_{kind}.jsonl')}
 assert len(expected)==2346
 for p in sorted((ROOT/'evaluation').glob('*_complete.json')):
  model=p.name.removesuffix('_complete.json');lock=json.loads((ROOT/f'checkpoints/{model}/evaluation_lock.json').read_text());assert lock['interface_hash']==digest(ROOT/f'models/{model}_interface.json');assert lock['data_lock_hash']==digest(ROOT/'data/lock.json')
  for g in ['G1','G3']:
   rows=read(f'outputs/{model}/{g}.jsonl');assert len(rows)==3732 and len({r['uid'] for r in rows})==3732
   for r in rows:
    e=expected[r['row_id']]
    for f in ['source_text','frames','operations','gold_step_texts','offsets','source_support_G1']:assert r[f]==e[f],(model,g,r['row_id'],f)
    assert len(r['steps'])==len(r['operations'])
    assert r['endpoint_joint']==r['steps'][-1]['score']['joint_ok']
    assert r['trajectory_joint']==all(s['score']['joint_ok'] for s in r['steps'])
    if r['mode']=='latent_chain':assert all(s['input_mask_length']==r['source_tokens'] for s in r['steps'])
    for s,frame in zip(r['steps'],r['frames'][1:]):
     assert s['frame']==frame
     if s['score']['parse_unresolved'] or not s['score']['normal_end']:assert not s['score']['joint_ok']
    if model!='BART':assert r['editor_hash']==lock['checkpoints'][g] and r['interface_hash']==lock['interface_hash']
   counts=collections.Counter((r['split'],r['path'],r['mode']) for r in rows)
   for (split,path,mode),n in counts.items():assert n==(53 if path=='minus3' else 80)
   results[model+'/'+g]={'rows':len(rows),'stages':sum(len(r['steps']) for r in rows),'fixed_denominators':True,'trajectory_recomputed':True,'latent_original_mask':True}
   if model!='BART':
    folder=ROOT/f'checkpoints/{model}/{g}';c=json.loads((folder/'complete.json').read_text());logs=read(f'checkpoints/{model}/{g}/training_log.jsonl')
    assert c['step']==600 and [r['step'] for r in logs]==list(range(1,601))
    assert sum(r['chain_occurrences'] for r in logs)==(1600 if g=='G3' else 0)
    assert c['checkpoint_hash']==digest(folder/'best.pt')==lock['checkpoints'][g]
    assert c['beststep']==min(c['history'],key=lambda x:(x['dev_target_token_nll'],x['step']))['step']
    assert c['initialization_hash']==json.loads((ROOT/f'checkpoints/{model}/initial.json').read_text())['tensor_hash']
    assert {op:v['updates'] for op,v in c['counts'].items()}==dict(T_plus=200,T_minus=200,P_13=100,P_31=100)
  controls=read(f'outputs/{model}/controls.jsonl');assert len(controls)==11730
  assert len({(r['row_id'],r['kind']) for r in controls})==11730
 rules=read('outputs/text_rule.jsonl');assert len(rules)==2346 and {r['row_id'] for r in rules}==set(expected)
 b=json.loads((ROOT/'budget.json').read_text());assert b['total_gpu_seconds']<=14400 and b['preflight_gpu_seconds']<=3600
 events=[]
 for j in b['jobs']:
  assert j['state']=='COMPLETED',j
  assert 'gres/gpu=1' in j['allocation']
  events += [(datetime.fromisoformat(j['start']),1),(datetime.fromisoformat(j['end']),-1)]
 active=peak=0
 for t,delta in sorted(events):active+=delta;peak=max(peak,active)
 assert active==0 and peak<=2
 import csv
 blind=list(csv.DictReader((ROOT/'review/blind_trajectories.csv').open()));selected=set(json.loads((ROOT/'review/selected_worlds.json').read_text()))
 assert {r['record_id'] for r in blind}==selected and len(selected)==20
 assert all(not r['human_label'] and not r['human_notes'] for r in blind)
 assert len(read('review/cases.jsonl'))<=20
 dump('evaluation/final_checks.json',dict(passed=True,models=results,controls_per_model=11730,rule_paths=2346,concurrent_gpus_observed=peak,gpu_seconds=b['total_gpu_seconds'],preflight_gpu_seconds=b['preflight_gpu_seconds'],blind_worlds=len(selected),human_labels=0,training_code_unchanged=True))
 print('final checks passed',results)
if __name__=='__main__':main()
