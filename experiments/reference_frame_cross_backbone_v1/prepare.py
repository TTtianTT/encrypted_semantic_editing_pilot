import random,collections,subprocess
from common import *
# Original world grammar, running against this independent directory's common module.
exec((V2/'prepare.py').read_text().split('def main():')[0])
SEED=2026092904

def main():
 assert not (ROOT/'data/lock.json').exists(),'Prepared data are immutable'
 oldfiles=[p for root in [V1,V2,V3] for p in (root/'data').glob('*worlds.jsonl')]
 old=[json.loads(l) for p in oldfiles for l in p.read_text().splitlines()];used={world_key(w) for w in old};oldkeys=used.copy();splits={s:build_worlds(s,80,SEED+j,used) for j,s in enumerate(['test_iid','test_template_ood'])}
 excluded=[];confirm=[]
 for j,(split,ws) in enumerate(splits.items()):
  for w in ws:w['record_id']=w['record_id'].replace('v2_','cross_v1_');assert world_key(w) not in oldkeys
  write(f'data/{split}_worlds.jsonl',ws);rng=random.Random(SEED+200+j);atom=[];chains=[]
  for w in ws:
   legal=[d for d in range(-2,3) if all(eligible(w,ops,d,'third' if path.endswith('third') else 'first') for path,ops in ATOMIC.items())];off=rng.choice(legal)
   for path,ops in ATOMIC.items():atom.append(make_row(w,path,ops,off,'third' if path.endswith('third') else 'first'))
   for path,ops in CHAINS.items():
    lim=1 if len(ops)==3 else 2;legal=[d for d in range(-lim,lim+1) if eligible(w,ops,d)]
    if not legal:excluded.append(dict(record_id=w['record_id'],split=split,path=path,reason='all frames must be >= record_date',status=w['record_status']));continue
    r=make_row(w,path,ops,rng.choice(legal));assert all(ok for op,ok in zip(ops,r['source_support_G1']) if op.startswith('T'));chains.append(r)
  for kind,rs in [('atomic',atom),('chains',chains)]:write(f'data/{split}_{kind}.jsonl',rs);confirm+=rs
 csvwrite('data/inapplicable.csv',excluded)
 # Every legal target stage from the calibration world/path matrix; multiplicities retained.
 targets=[];cal=read('data/calibration_worlds.jsonl')
 for w in cal:
  for path,ops in (ATOMIC|CHAINS).items():
   lim=1 if len(ops)==3 else 2;pers='third' if path.endswith('third') else 'first'
   for off in range(-lim,lim+1):
    if not eligible(w,ops,off,pers):continue
    r=make_row(w,path,ops,off,pers)
    for k,(text,c) in enumerate(zip(r['gold_step_texts'],r['frames'][1:])):targets.append(dict(uid=r['row_id']+f'/stage{k+1}',record_id=w['record_id'],text=text,frame=c,status=w['record_status']))
 write('data/calibration_targets.jsonl',targets)
 worlds={w['record_id']:w for p in (ROOT/'data').glob('*worlds.jsonl') for w in read(p.relative_to(ROOT))}
 for r in confirm:
  text=r['source_text']
  for gold,c0,c1 in zip(r['gold_step_texts'],r['frames'],r['frames'][1:]):
   assert score(gold,c1,worlds[r['record_id']])['joint_ok'];text,err=text_rule(text,c0,c1);assert err is None and score(text,c1,worlds[r['record_id']])['joint_ok']
 for r in targets:assert score(r['text'],r['frame'],worlds[r['record_id']])['joint_ok']
 schedule=read('data/sample_schedule.jsonl');assert len(schedule)==600 and sum(sum(b['g2_replace']) for b in schedule)==1600
 assert [len(read(f'data/{s}_worlds.jsonl')) for s in ['train','dev','calibration']]==[480,80,60]
 selected=[]
 for split,ws in splits.items():selected+=random.Random(SEED+999).sample([w['record_id'] for w in ws],10)
 dump('review/selected_worlds.json',selected)
 audit={}
 for g in ['G1','G3']:
  rs=[json.loads(l) for l in (V3/f'outputs/confirmation_{g}.jsonl').read_text().splitlines()]
  for split in splits:
   for path in ['T_plus_first','T_plus_third','plus_plus','plus3','person_plus']:
    sub=[r for r in rs if r['split']==split and r['path']==path and r['mode']=='latent_chain'];audit[f'{g}/{split}/{path}']={'N':len(sub),'endpoint':sum(r['score']['joint_ok'] for r in sub),'trajectory':sum(all(s['score']['joint_ok'] for s in r['steps']) for r in sub)}
 assert audit['G3/test_iid/plus3']['trajectory']==11 and audit['G3/test_iid/person_plus']['trajectory']==74 and audit['G1/test_iid/person_plus']['trajectory']==79
 assert audit['G3/test_template_ood/plus_plus']['trajectory']==64
 dump('evaluation/old_evidence.json',audit)
 oldmanifest={str(p.relative_to(REPO)):digest(p) for root in [V1,V2,V3] for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 dump('old_readonly_manifest.json',oldmanifest)
 dump('data/manifest.json',dict(seed=SEED,new_worlds=160,old_distinct_facts=len(oldkeys),fact_overlap=0,target_stage_occurrences=len(targets),source_views=920,inapplicable_N=len(excluded),path_counts={str(k):n for k,n in collections.Counter((r['split'],r['path']) for r in confirm).items()},old_files={str(p.relative_to(REPO)):digest(p) for p in oldfiles}))
 dump('data/lock.json',dict(files={p.name:digest(p) for p in (ROOT/'data').glob('*') if p.is_file()},protocol_hash=digest(ROOT/'PROTOCOL.md'),config_hash=digest(ROOT/'config.json'),scorer_hash=digest(ROOT/'semantics_v1.py'),common_hash=digest(ROOT/'common.py'),before_model_outputs=True))
 print('Locked:',len(confirm),'confirmation rows;',len(targets),'calibration stage occurrences')
if __name__=='__main__':main()
