"""CPU artifact and protocol audit; no inference, no metric changes."""
import json,collections,hashlib
import torch
from common import *
from engine import tensorhash

def main():
 groups=['G0','G1']+(['G2'] if json.loads((ROOT/'evaluation/c_gate.json').read_text())['run_G2'] else [])
 lock=json.loads((ROOT/'data/test_lock.json').read_text())
 for name,h in lock['files'].items():assert digest(ROOT/'data'/name)==h
 for name,h in json.loads((ROOT/'v1_readonly_manifest.json').read_text()).items():assert digest(V1/name)==h,name
 for g in groups:
  md=json.loads((ROOT/f'checkpoints/{g}/complete.json').read_text());assert md['steps']==600;assert md['initialization_hash']==json.loads((ROOT/'checkpoints/initial.json').read_text())['tensor_hash'];assert md['replaced_occurrences']==(1600 if g=='G2' else 0)
 schedule=read('data/sample_schedule.jsonl');g0=read('data/train_G0.jsonl');g1=read('data/train_G1.jsonl');actual=collections.Counter()
 for b in schedule:
  for k,replace in zip(b['pair_indices'],b['g2_replace']):
   a,z=g0[k],g1[k];assert (a['record_id'],a['path'],a['record_status'],a['polarity'])==(z['record_id'],z['path'],z['record_status'],z['polarity'])
   if z['operations'][0].startswith('P'):assert a==z and not replace
   if replace:assert z['operations']==['T_plus'] and -2<=z['offsets'][0]<=2
   actual[z['operations'][0]]+=1
 assert actual==dict(T_plus=3200,T_minus=3200,P_13=1600,P_31=1600)
 weights={g:torch.load(ROOT/f'checkpoints/{g}/best.pt',weights_only=True,map_location='cpu') for g in groups};parameter_checks={}
 for op in ['P_13','P_31','T_minus']:
  hashes={g:tensorhash({k:v for k,v in sd.items() if k.startswith(op+'.')}) for g,sd in weights.items()};parameter_checks[op]=hashes
  if op.startswith('P'):assert len(set(hashes.values()))==1
  if op=='T_minus' and 'G2' in groups:assert hashes['G1']==hashes['G2']
 complete=json.loads((ROOT/'evaluation/test_complete.json').read_text());formal=[]
 for g in groups:
  rows=read(f'outputs/{g}.jsonl');assert len(rows)==complete['rows_per_group'];assert len({r['uid'] for r in rows})==len(rows)
  for r in rows:
   assert len(r['steps'])==len(r['operations']);assert r['steps'][-1]['frame']==r['frames'][-1]
   if r['mode']=='latent_chain':assert all(s['input_mask_length']==r['source_tokens'] for s in r['steps'])
  formal+=rows
 a=read('diagnostic_a/outputs.jsonl');assert len(a)==1440 and all(r['middle_exact'] and r['first_score']['joint_ok'] for r in a)
 for s in [42,43,44]:
  for p in ['time_twice','time_return']:
   for route in ['A1','A2','A3']:
    rr=[r for r in a if r['seed']==s and r['path']==p and r['route']==route];assert len(rr)==80;assert sum(r['support']=='inside53' for r in rr)==53
 # World count and all per-step legality with real facts.
 counts={}
 for split in ['dev','test_iid','test_template_ood']:
  worlds={w['record_id']:w for w in read(f'data/{split}_worlds.jsonl')};rs=read(f'data/{split}_chains.jsonl')
  counts[split]=dict(collections.Counter(r['path'] for r in rs))
  for r in rs:assert valid(worlds[r['record_id']],r['frames'])
  assert counts[split]['minus3']==53 and all(n==80 for p,n in counts[split].items() if p!='minus3')
 dump('evaluation/final_audit.json',{'passed':True,'v1_unchanged':True,'frozen_data_unchanged':True,'initialization_shared':True,'P_training_inputs_targets_indices_equal':True,'G1_G2_T_minus_weights_equal':True,'operator_checkpoint_hashes':parameter_checks,'actual_samples':dict(actual),'groups':groups,'formal_neural_outputs':len(formal),'A_rows':len(a),'path_world_counts':counts,'normal_end_failures':sum(not r['score']['normal_end'] for r in formal),'human_review':False})
 print('Audit passed',len(formal))
if __name__=='__main__':main()
