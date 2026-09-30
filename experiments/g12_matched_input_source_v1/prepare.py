"""Only grammar/tokenizer determine inclusion; no backbone inference."""
import random,collections,importlib.util
from common_g12 import *
def main():
 assert not (ROOT/'data/lock.json').exists(),'Locked data must not be overwritten'
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
 def path(w,ds):return dict(record_id=w['record_id'],world=w,offsets=ds,frames=[frame(w,d) for d in ds],texts=[render(w,frame(w,d)) for d in ds])
 exclusions=[];sets={}
 for split in ['train','dev']:
  rows=[]
  for w in read(V3/f'data/{split}_worlds.jsonl'):
   if w['record_status']!='recorded_plan':continue
   r=path(w,CFG['training_offsets']);xs=tok(r['texts'],padding='max_length',max_length=96,truncation=False)
   reason=None
   if not valid(w,r['frames']):reason='illegal frames'
   elif max(map(len,xs['input_ids']))>96:reason='input length'
   elif xs['attention_mask'][0]!=xs['attention_mask'][2]:reason='y0/y2 true mask differs'
   if reason:exclusions.append(dict(split=split,record_id=w['record_id'],template=w['template_family'],reason=reason));continue
   assert all(score(t,c,w)['joint_ok'] for t,c in zip(r['texts'],r['frames']))
   r['mask']=xs['attention_mask'][0];r['target_tokens']=[sum(a) for a in xs['attention_mask'][1:]];rows.append(r)
  sets[split]=rows;write(f'data/{split}_paths.jsonl',rows)
 assert sets['train'] and {r['world']['template_family'] for r in sets['train']}==set(range(8)),'Systematic missing templates; stop'
 schedule=[];stream=[];rng=random.Random(CFG['schedule_seed'])
 for step in range(1,201):
  while len(stream)<16:
   ids=list(range(len(sets['train'])));rng.shuffle(ids);stream+=ids
  schedule.append(dict(update=step,indices=stream[:16]));stream=stream[16:]
 write('data/sample_schedule.jsonl',schedule);dump('data/training_exclusions.json',exclusions)
 old=[];oldfiles={}
 for p in sorted((REPO/'experiments').rglob('*.jsonl')):
  if ROOT in p.parents or 'world' not in p.name or 'outputs' in p.parts:continue
  ws=[w for w in read(p) if all(k in w for k in FIELDS)]
  if ws:old+=ws;oldfiles[str(p.relative_to(REPO))]=digest(p)
 used={key(w) for w in old};oldkeys=used.copy();norm=lambda t:' '.join(t.lower().split())
 oldtexts={norm(render(w,frame(w,d))) for w in old for d in range(-4,5) if valid(w,[frame(w,d)])}
 spec=importlib.util.spec_from_file_location('g12_world_builder',V3/'prepare.py');vp=importlib.util.module_from_spec(spec);spec.loader.exec_module(vp)
 worlds=[];paths=[];render_rejections=[];seen_new_texts=set()
 for j,split in enumerate(['iid','template_ood']):
  pool=vp.build_worlds('test_iid' if j==0 else 'test_template_ood',240,CFG['data_seed']+j,used)
  ws=[w for w in pool if w['record_status']=='recorded_plan'];assert len(ws)==80
  replacement_pools={}
  for i,w in enumerate(ws):
   round=0
   while any(norm(render(w,frame(w,d))) in oldtexts or norm(render(w,frame(w,d))) in seen_new_texts for d in range(-4,5)):
    render_rejections.append(dict(split=split,index=i,fact_sha256=hashlib.sha256(key(w).encode()).hexdigest(),reason='pre-output normalized render collision'))
    round+=1;assert round<100
    if round not in replacement_pools:replacement_pools[round]=[z for z in vp.build_worlds('test_iid' if j==0 else 'test_template_ood',240,CFG['data_seed']+j+1000*round,used) if z['record_status']=='recorded_plan']
    candidate=replacement_pools[round][i];assert candidate['template_family']==w['template_family'] and candidate['polarity']==w['polarity'];w=candidate
   w=dict(w,record_id=f'g12_{split}_{i:04d}',split=split);assert key(w) not in oldkeys
   worlds.append(w);r=path(w,list(range(-4,5)));r['legal']=valid(w,r['frames']);r['reason']=None if r['legal'] else 'pre-output date/renderer invalid';seen_new_texts.update(norm(t) for t in r['texts'])
   assert r['legal']
   for t,c in zip(r['texts'],r['frames']):assert norm(t) not in oldtexts and score(t,c,w)['joint_ok']
   assert max(map(len,tok(r['texts'])['input_ids']))<60
   r['atomic_legal']={str(d):eligible(w,['T_plus'],d) for d in CFG['atomic_offsets']};r['chain_legal']=valid(w,[frame(w,d) for d in CFG['chain_offsets']]);paths.append(r)
 write('data/worlds.jsonl',worlds);write('data/test_paths.jsonl',paths);dump('data/render_collision_rejections.json',render_rejections)
 assert len({key(w) for w in worlds})==160
 dump('data/prior_fact_hashes.json',dict(fields=FIELDS,hashes=sorted({hashlib.sha256(k.encode()).hexdigest() for k in oldkeys})))
 selected=[]
 for split in ['iid','template_ood']:selected+=random.Random(CFG['review_seed']).sample([w['record_id'] for w in worlds if w['split']==split],10)
 dump('review/selection.json',selected)
 counts=dict(train_N=len(sets['train']),dev_N=len(sets['dev']),exclusions=exclusions,train_templates=dict(collections.Counter(r['world']['template_family'] for r in sets['train'])),new_worlds=160,prior_files=oldfiles,prior_world_rows=len(old),complete_fact_overlap=0,normalized_render_overlap=0,polarity={s:dict(collections.Counter(w['polarity'] for w in worlds if w['split']==s)) for s in ['iid','template_ood']},tokens_max=max(len(x) for r in sets['train']+sets['dev']+paths for x in tok(r['texts'])['input_ids']),all_y0_y2_masks_equal=True,occurrences=3200)
 dump('data/precheck.json',counts)
 deps=[V3/n for n in ['engine.py','common.py','renderer_v1.py','semantics_v1.py','source_model_manifest.json','config.json','data/train_worlds.jsonl','data/dev_worlds.jsonl']]+[original(s) for s in CFG['seeds']]+[G11/n for n in ['REPORT.md','PROTOCOL.md','gpu.py','g11.py','analyze.py']]+[G10/'train.py']
 files=[ROOT/'PROTOCOL.md',ROOT/'config.json']+list((ROOT/'data').glob('*'))+list(ROOT.glob('*.py'))+list(ROOT.glob('*.slurm'))+[ROOT/'review/selection.json']+deps
 dump('data/lock.json',dict(baseline=CFG['baseline'],files={str(p.relative_to(REPO)):digest(p) for p in files if p.is_file()},before_training_and_confirmation=True))
 dump('budget.json',dict(hard_limit_seconds=14400,max_concurrent_gpus=2,jobs=[],gpu_seconds=0,reservations=[]))
 print('G12 locked',counts['train_N'],counts['dev_N'],'old worlds',len(old),'new160',flush=True)
if __name__=='__main__':main()
