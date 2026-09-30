"""Lock new worlds before any new-world inference."""
import importlib.util,random,collections
from g11 import *
def main():
 assert not (ROOT/'data/manifest.json').exists(),'Locked data may not be overwritten'
 spec=importlib.util.spec_from_file_location('g11_v3_prepare',V3/'prepare.py');vp=importlib.util.module_from_spec(spec);spec.loader.exec_module(vp)
 old=[];files=[]
 for p in sorted((REPO/'experiments').rglob('*.jsonl')):
  if ROOT in p.parents or 'world' not in p.name or 'outputs' in p.parts:continue
  rows=read(p);ws=[w for w in rows if all(k in w for k in FIELDS)]
  if ws:old.extend(ws);files.append(p)
 used={key(w) for w in old};oldkeys=used.copy();worlds=[]
 for j,split in enumerate(['iid','template_ood']):
  legacy='test_template_ood' if j else 'test_iid';pool=vp.build_worlds(legacy,240,CFG['data_seed']+j,used);ws=[w for w in pool if w['record_status']=='recorded_plan'];assert len(ws)==80
  for i,w in enumerate(ws):
   w=dict(w);w.update(record_id=f'g11_{split}_{i:04d}',split=split);assert key(w) not in oldkeys;worlds.append(w)
 assert len({key(w) for w in worlds})==160
 rows=[]
 for w in worlds:
  for d in CFG['anchors']:
   frames=[frame(w,k) for k in range(d-1,d+3)]
   legal=valid(w,frames)
   texts={str(k):render(w,frame(w,k)) for k in range(d-1,d+3)} if legal else {}
   assert not legal or all(score(t,frame(w,int(k)),w)['joint_ok'] for k,t in texts.items())
   support={str(k):(-3<=k<=3 and eligible(w,['T_plus'],k)) for k in range(d,d+3)}
   rows.append(dict(record_id=w['record_id'],split=w['split'],anchor=d,legal=legal,reason=None if legal else 'frame/date/renderer invalid',texts=texts,source_support=support))
 write('data/worlds.jsonl',worlds);write('data/paths.jsonl',rows)
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True);texts=[t for r in rows for t in r['texts'].values()];lengths=[len(v) for v in tok(texts)['input_ids']];assert max(lengths)<=96 and max(lengths)<60
 selection=[]
 for split in ['iid','template_ood']:
  selection+=random.Random(CFG['data_seed']+99).sample([w['record_id'] for w in worlds if w['split']==split],5)
 dump('review/selection.json',selection)
 dependencies=depfiles();manifest=dict(baseline=CFG['baseline'],worlds_sha256=digest(ROOT/'data/worlds.jsonl'),paths_sha256=digest(ROOT/'data/paths.jsonl'),config_sha256=digest(ROOT/'config.json'),protocol_sha256=digest(ROOT/'PROTOCOL.md'),dependencies={str(p.relative_to(REPO)):digest(p) for p in dependencies},prior_world_files={str(p.relative_to(REPO)):digest(p) for p in files},prior_world_rows=len(old),prior_unique_keys=len(oldkeys),new_fact_overlap=0,worlds=160,paths=len(rows),legal_paths=sum(r['legal'] for r in rows),max_tokens=max(lengths),polarity_counts={s:dict(collections.Counter(w['polarity'] for w in worlds if w['split']==s)) for s in ['iid','template_ood']},template_counts={s:dict(collections.Counter(str(w['template_family']) for w in worlds if w['split']==s)) for s in ['iid','template_ood']},code={p.name:digest(p) for p in ROOT.glob('*.py')},locked_before_outputs=True)
 dump('data/manifest.json',manifest);dump('budget.json',dict(hard_limit_seconds=7200,max_concurrent_gpus=1,jobs=[],gpu_seconds=0));print('G11 locked',manifest['worlds'],manifest['legal_paths'],'paths; prior rows',len(old),flush=True)
if __name__=='__main__':main()
