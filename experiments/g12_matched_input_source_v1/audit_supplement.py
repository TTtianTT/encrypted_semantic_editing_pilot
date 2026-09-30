"""Additional provenance checks; never modifies locked inference or scoring."""
from common_g12 import *
def main():
 l=lock();worlds=read('data/worlds.jsonl');wi={w['record_id']:w for w in worlds};curr=read('outputs/current_states.jsonl');ci={(r['seed'],r['method'],r['record_id'],r['history']):r for r in curr};prefix_checks=0
 for r in curr:
  expected=[]
  if r['history']==0:expected=[-1]
  else:expected=[r['history']-2-k for k in range(r['history'])]
  for x,d in zip(r['prefix'],expected):
   assert x['frame']==frame(wi[r['record_id']],d);assert x['target_text']==render(wi[r['record_id']],x['frame']);assert x['score']==score(x['output'],x['frame'],wi[r['record_id']],x['normal_end']);prefix_checks+=1
  assert len(r['prefix'])==len(expected) and r['prefix_clean']==all(x['score']['joint_ok'] for x in r['prefix'])
  cc=[ci[r['seed'],r['method'],r['record_id'],h] for h in range(3)];assert r['equal_mask02']==(cc[0]['mask']==cc[2]['mask']) and r['all_prefix_clean']==all(z['prefix_clean'] for z in cc)
 chains=read('outputs/long_chains.jsonl');idx={(r['seed'],r['method'],r['record_id'],r['step']):r for r in chains}
 for r in chains:
  assert r['trajectory_joint']==all(idx[r['seed'],r['method'],r['record_id'],k]['output']['score']['joint_ok'] for k in range(1,r['step']+1));assert r['output']['frame']==frame(wi[r['record_id']],1-r['step']);assert r['mask']==idx[r['seed'],r['method'],r['record_id'],1]['mask']
 # Independent CPU tokenizer verifies the mask constraint and gold lengths.
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
 for r in read('data/train_paths.jsonl')+read('data/dev_paths.jsonl'):
  x=tok(r['texts'],padding='max_length',max_length=96,truncation=False);assert x['attention_mask'][0]==x['attention_mask'][2]==r['mask'];assert max(map(len,x['input_ids']))<=96
 budget=json.loads((ROOT/'budget.json').read_text());jobs=budget['jobs'];trainjobs=[j for j in jobs if j['phase']=='train'];currentjobs=[j for j in jobs if j['phase']=='current'];smokejobs=[j for j in jobs if j['phase']=='preflight'];assert all(t['start']>=max(j['end'] for j in smokejobs) for t in trainjobs);assert all(c['start']>=max(j['end'] for j in trainjobs) for c in currentjobs)
 for s in CFG['seeds']:
  for arm in ['A','B']:
   m=json.loads((ROOT/f'training/{arm}_seed{s}.json').read_text());counts=m['counts'];assert counts['encoder_batch_calls']==400 and counts['decoder_batch_calls']==600 and counts['operator_batch_calls']==600;assert counts['encoder_sample_calls']==6400 and counts['decoder_sample_calls']==9600 and counts['operator_sample_calls']==9600;assert len(m['curve'])==200 and [r['update'] for r in m['dev_diagnostics']]==[50,100,150,200]
 dump('audit_supplement.json',dict(passed=True,prefix_scores_rechecked=prefix_checks,trajectory_intersections_rechecked=len(chains),true_masks_retokenized=True,paired_forward_calls_verified=True,training_before_confirmation_barrier_verified=True,all_locked_sources_unchanged=True,local_activations_uploaded=False))
 print('G12 supplemental audit passed')
if __name__=='__main__':main()
