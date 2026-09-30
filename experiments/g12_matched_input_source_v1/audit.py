"""CPU audit of immutable sources, supervised calls, fixed denominators and scores."""
from common_g12 import *
def main():
 l=lock();ws=read('data/worlds.jsonl');wi={w['record_id']:w for w in ws};prior=set(json.loads((ROOT/'data/prior_fact_hashes.json').read_text())['hashes']);assert len(ws)==160 and len({key(w) for w in ws})==160 and not any(hashlib.sha256(key(w).encode()).hexdigest() in prior for w in ws)
 schedule=read('data/sample_schedule.jsonl');train=read('data/train_paths.jsonl');assert len(schedule)==200 and sum(len(b['indices']) for b in schedule)==3200
 expected=[sum(train[i]['target_tokens'][k] for b in schedule for i in b['indices']) for k in range(3)]
 for s in CFG['seeds']:
  a=json.loads((ROOT/f'training/A_seed{s}.json').read_text());b=json.loads((ROOT/f'training/B_seed{s}.json').read_text());assert a['initial_state_hash']==b['initial_state_hash'] and a['initial_checkpoint_sha256']==b['initial_checkpoint_sha256']==digest(original(s));assert a['counts']==b['counts'] and a['stage_token_counts']==b['stage_token_counts']==expected
  for method,m in [('A',a),('B',b)]:assert m['updates']==200 and m['final_checkpoint_no_selection'] and m['checkpoint_sha256']==digest(checkpoint(method,s)) and m['backbone_unchanged']
 co=json.loads((ROOT/'data/cohort_lock.json').read_text());assert co['locked_before_next_and_long_chain'] and co['current_sha256']==digest(ROOT/'outputs/current_states.jsonl');lh=digest(ROOT/'data/cohort_lock.json');rows={}
 for filename,component,expectedN in [('current_states','current',4320),('next_states','next',4320),('long_chains','output',7200),('atomic','output',10080)]:
  rs=read(f'outputs/{filename}.jsonl');assert len(rs)==expectedN
  for r in rs:
   x=r[component];assert x['score']==score(x['output'],x['frame'],wi[r['record_id']],x['normal_end']);assert x['target_text']==render(wi[r['record_id']],x['frame'])
   if filename!='current_states':assert r['cohort_lock_sha256']==lh
  rows[filename]=len(rs)
 cur={(r['seed'],r['method'],r['record_id'],r['history']):r for r in read('outputs/current_states.jsonl')}
 for s in CFG['seeds']:
  for method in CFG['methods']:
   for w in ws:
    cs=[cur[s,method,w['record_id'],h] for h in range(3)];strict=all(r['current']['normal_end'] and r['current']['output'].strip()==r['current']['target_text'] for r in cs);assert all(r['strict']==strict for r in cs)
  for split in ['iid','template_ood']:assert set(co['common_AB_strict'][f'{s}/{split}'])=={w['record_id'] for w in ws if w['split']==split and all(cur[s,a,w['record_id'],0]['strict'] for a in ['A','B'])}
 budget=json.loads((ROOT/'budget.json').read_text());assert budget['gpu_seconds']<=14400 and budget.get('reserved_seconds',0)==0;events=[]
 for j in budget['jobs']:
  if j['gpu_count']:events += [(j['start'],1),(j['end'],-1)]
 count=peak=0
 for _,d in sorted(events,key=lambda x:(x[0],x[1])):count+=d;peak=max(peak,count)
 assert peak<=2
 current_job=co['job_id'];curend=next(j['end'] for j in budget['jobs'] if j['job_id']==current_job);evaluation_jobs=[j for j in budget['jobs'] if j['phase']=='finish'];assert all(j['start']>=curend for j in evaluation_jobs)
 dump('audit.json',dict(passed=True,worlds=160,fact_overlap=0,supervision_tokens_per_stage=expected,paired_initialization_and_budget=True,score_recomputed=True,all_fixed_denominators=True,rows=rows,cohort_locked_before_future_inference=True,backbone_updates=0,editor_training_updates_per_arm=200,gpu_seconds=budget['gpu_seconds'],peak_concurrent_gpus=peak,next_experiment_started=False,code_sha256={p.name:digest(p) for p in ROOT.glob('*.py')}));print('G12 audit passed')
if __name__=='__main__':main()
