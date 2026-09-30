"""Generate independent locked one-step matching and five-step test worlds."""
import importlib.util,sys,random,collections,itertools,argparse
from g10_common import *
sys.path.insert(0,str(V3))
spec=importlib.util.spec_from_file_location('g10_v3_prepare',V3/'prepare.py');vp=importlib.util.module_from_spec(spec);spec.loader.exec_module(vp)
frame,advance,render,score,text_rule=vp.frame,vp.advance,vp.render,vp.score,vp.text_rule
CFG=json.loads((ROOT/'config.json').read_text())

def candidate_worlds(split,count,seed,used):
  # The locked v2 generator supplies facts and template families. Retain plans only,
  # because the complete five-day T+ chain is structurally defined for those records.
  legacy_split='test_template_ood' if split.endswith('template_ood') else 'test_iid'
  allw=vp.build_worlds(legacy_split,count*3,seed,used)
  plans=[w for w in allw if w['record_status']=='recorded_plan']
  assert len(plans)>=count,(split,len(plans))
  out=[]
  for i,w in enumerate(plans[:count]):
    w=dict(w);w['record_id']=f'g10_{split}_{i:04d}';w['split']=split;out.append(w)
  return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--relock-before-model-outputs',action='store_true');args=ap.parse_args()
 assert not (ROOT/'data/lock.json').exists() or args.relock_before_model_outputs,'G10 data are already locked'
 old=[]
 for root in [V1,V2,V3,G7.parent/'projection_hypothesis_v1',G9]:
  if not root.exists():continue
  for p in (root/'data').glob('*worlds.jsonl') if (root/'data').exists() else []:
   old.extend(read(p))
 used={vp.world_key(w) for w in old};oldkeys=set(used)
 names=['match_iid','match_template_ood','composition_iid','composition_template_ood']
 ws={}
 for j,name in enumerate(names):
  ws[name]=candidate_worlds(name,80,CFG['match_data_seed']+j if name.startswith('match') else CFG['test_data_seed']+j,used)
 allkeys=[];allrows={}
 for name,worldlist in ws.items():
  rows=[]
  for w in worldlist:
   assert vp.world_key(w) not in oldkeys
   allkeys.append(vp.world_key(w));f=frame(w,CFG['start_offset'],'first');frames=[f]
   for _ in range(CFG['pure_latent_steps']):frames.append(advance(frames[-1],'T_plus'))
   assert vp.eligible(w,['T_plus']*CFG['pure_latent_steps'],CFG['start_offset'],'first')
   texts=[render(w,c) for c in frames];src=texts[0]
   rule=src
   for a,b in zip(frames,frames[1:]):
    rule,err=text_rule(rule,a,b);assert err is None and score(rule,b,w)['joint_ok']
   assert all(score(t,c,w)['joint_ok'] for t,c in zip(texts,frames))
   rows.append(dict(record_id=w['record_id'],split=name,source_text=src,source_frame=frames[0],
      target_frames=frames[1:],gold_step_texts=texts[1:],gold_endpoint_text=texts[-1],
      start_offset=CFG['start_offset'],record_status=w['record_status'],polarity=w['polarity'],
      template_family=w['template_family'],record_date=w['record_date'],event_date=w['event_date']))
  write(f'data/{name}.jsonl',rows);write(f'data/{name}_worlds.jsonl',worldlist);allrows[name]=rows
 assert len(allkeys)==len(set(allkeys))==320
 assert len({r['source_text'] for name in names for r in allrows[name] if name.startswith('match')})==160
 # Dev matching data come from the pre-existing, disjoint G3 dev worlds. Both
 # perspectives are scored; only source text is passed to inference.
 dev=[r for r in read(V3/'data/dev_atomic.jsonl') if r['operations']==['T_plus']]
 assert len(dev)==160
 write('data/dev_match.jsonl',[dict(record_id=r['record_id'],split=r['split'],source_text=r['source_text'],source_frame=r['frames'][0],target_frame=r['frames'][1],target_text=r['target_text'],perspective=r['frames'][0]['perspective']) for r in dev])
 # Copy source code, editor and training-schedule provenance without mutating old experiments.
 sources={str(p.relative_to(REPO)):digest(p) for p in [ROOT/'PROTOCOL.md',ROOT/'config.json',ROOT/'README.md',ROOT/'g10_common.py',ROOT/'prepare.py',ROOT/'preflight.py',ROOT/'train.py',ROOT/'screen.py',ROOT/'evaluate.py',ROOT/'basin.py',ROOT/'analyze.py',ROOT/'audit.py',ROOT/'report.py',ROOT/'run.slurm',ROOT/'train_array.slurm',ROOT/'preflight.slurm',ROOT/'screen.slurm',ROOT/'evaluate.slurm',ROOT/'basin_array.slurm']}
 lock={'worlds':320,'fact_key_overlap_with_prior':0,'independent_dev_worlds':80,
       'match_worlds_per_stratum':80,'composition_worlds_per_stratum':80,
       'files':{p.name:digest(p) for p in (ROOT/'data').glob('*') if p.is_file()},
       'source_artifacts':{str(p.relative_to(REPO)):digest(p) for p in [V3/'data/train_G1.jsonl',V3/'data/sample_schedule.jsonl',V3/'data/train_worlds.jsonl',V3/'data/dev_atomic.jsonl',V3/'checkpoints/G3/best.pt']},
       'code':sources,'config_sha256':digest(ROOT/'config.json'),'protocol_sha256':digest(ROOT/'PROTOCOL.md'),
       'seed':{'match':CFG['match_data_seed'],'test':CFG['test_data_seed']},'outputs_seen':False}
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
 check_texts=[t for name in names for r in allrows[name] for t in [r['source_text']]+r['gold_step_texts']]
 check_texts += [t for r in dev for t in [r['source_text'],r['target_text']]]
 lengths=[len(x) for x in tok(check_texts,add_special_tokens=True,truncation=False)['input_ids']]
 assert max(lengths)<=96,max(lengths)
 lock['max_token_length']=max(lengths);lock['bart_input_limit']=96
 dump('data/lock.json',lock)
 dump('data/precheck.json',{'prior_world_files_checked':len(old),'new_full_fact_keys':len(allkeys),'fact_overlap':0,
     'strata':{n:{'N':len(r),'status_counts':dict(collections.Counter(x['record_status'] for x in r)),
                    'template_counts':dict(collections.Counter(str(x['template_family']) for x in r))} for n,r in allrows.items()},
     'source_offset':1,'five_step_offsets':[1,0,-1,-2,-3,-4],'all_paths_legal':True,'gold_scoring':1600,'max_token_length':max(lengths),'input_limit':96,
     'source_only_rule_steps':1280,'dev_rows':len(dev),'max_source_or_gold_chars':max(len(t) for name in names for r in allrows[name] for t in [r['source_text']]+r['gold_step_texts'])})
 print('locked G10 worlds; full-fact overlap 0; dev',len(dev),'new match/test',len(allkeys),flush=True)
if __name__=='__main__':main()
