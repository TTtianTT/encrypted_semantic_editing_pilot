import shutil,subprocess
from task import *
from transformers import AutoTokenizer
def main():
 assert not (ROOT/'data/lock.json').exists()
 # Reuse the world generator definitions; never run the old experiment's main.
 ns={};exec((V2/'prepare.py').read_text().split('def main():')[0],ns)
 oldroots=[V1,V2,V3,CROSS];prior=[w for root in oldroots for p in (root/'data').glob('*worlds.jsonl') for w in read(p)];used={world_key(w) for w in prior};oldkeys=used.copy()
 support=support_counts();allrows={};exclusions=[]
 for split in ['train','dev','calibration','test_iid','test_template_ood']:
  if split.startswith('test'):
   ws=ns['build_worlds'](split,80,SEED+(split=='test_template_ood'),used)
   for w in ws:w['record_id']=w['record_id'].replace('v2_','joint_v1_');assert world_key(w) not in oldkeys
   write(f'data/{split}_worlds.jsonl',ws)
  else:ws=read(f'data/{split}_worlds.jsonl')
  rs=[];rng=random.Random(SEED+100+len(allrows))
  for w in ws:
   legal=[]
   for off in range(-2,3):
    r=joint_row(w,off,support)
    if r:legal.append(r)
    else:exclusions.append(dict(split=split,record_id=w['record_id'],offset=off,reason='date legality or actual G1 source support absent'))
   assert legal,w['record_id']
   rs.extend([rng.choice(legal)] if split.startswith('test') else legal)
  allrows[split]=rs;write(f'data/{split}_joint.jsonl',rs)
 # Backend reads this first source only to measure the encoder dimension.
 write('data/train_G1.jsonl',allrows['train'])
 by=collections.defaultdict(list)
 for i,r in enumerate(allrows['train']):by[r['record_id']].append(i)
 rng=random.Random(42);stream=[]
 for epoch in range(20):
  ids=list(by);rng.shuffle(ids)
  for rid in ids:stream.append(by[rid][epoch%len(by[rid])])
 assert len(stream)==9600
 write('data/sample_schedule.jsonl',[dict(step=i//16+1,pair_indices=stream[i:i+16]) for i in range(0,9600,16)])
 csvwrite('data/excluded_views.csv',exclusions)
 csvwrite('data/old_support_counts.csv',[dict(operation=k[0],offset=k[1],status=k[2],polarity=k[3],perspective=k[4],N=n) for k,n in sorted(support.items())])
 ws=worlds();oldcal=read(CROSS/f'calibration/{NAME}/B_unique_outputs.jsonl');print('calibration keys',list(oldcal[0]),flush=True)
 # Scored source views provide an exact input -> actual output map, independent of task labels.
 cache={r['text']:r for r in read(CROSS/f'calibration/{NAME}/B_scored.jsonl')};calproof=[]
 for split,rs in allrows.items():
  for r in rs:
   w=ws[r['record_id']]
   for order,o in r['orders'].items():
    text=r['source_text']
    for c0,c1,gold in zip(o['frames'],o['frames'][1:],o['gold_step_texts']):
     assert metric(gold,c1,w,True)['joint_ok'];text,e=text_rule(text,c0,c1);assert e is None and metric(text,c1,w,True)['joint_ok']
   if split=='calibration':
    for role,t,c in [('source',r['source_text'],r['source_frame']),('target',r['target_text'],r['target_frame'])]:
     actual=cache[t];assert metric(actual['output'],c,w,actual['score']['normal_end'])['joint_ok'];calproof.append(dict(row_id=r['row_id'],role=role,text=t,output=actual['output'],joint_ok=True))
 write('calibration/reused_reconstruction.jsonl',calproof)
 # Token limits are inherited exactly, not chosen using confirmation content.
 manifest=json.loads((ROOT/f'models/{NAME}.json').read_text());cfg=json.loads((ROOT/f'models/{NAME}_interface.json').read_text());tok=AutoTokenizer.from_pretrained(manifest['directory'],local_files_only=True);lengths=[]
 for split,rs in allrows.items():
  texts={t for r in rs for t in [r['source_text'],r['target_text']]+[g for o in r['orders'].values() for g in o['gold_step_texts']]}
  wrapped=[tok.apply_chat_template([dict(role='user',content='Copy the following text exactly. Output only the copied text.\n\n'+t)],tokenize=False,add_generation_prompt=True) for t in texts]
  a=max(len(x) for x in tok(wrapped,add_special_tokens=False)['input_ids']);b=max(len(x)+1 for x in tok(list(texts),add_special_tokens=False)['input_ids']);assert a<=80 and b<65
  lengths.append(dict(split=split,max_input=a,max_target=b,source_cap=80,generation_cap=65))
 dump('data/length_check.json',lengths)
 selected=[]
 for split in ['test_iid','test_template_ood']:selected+=random.Random(SEED+999).sample([r['record_id'] for r in allrows[split]],10)
 dump('review/selected_worlds.json',selected)
 original={str(p.relative_to(REPO)):digest(p) for root in oldroots for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='latest.pt'};dump('old_readonly_manifest.json',original)
 dump('data/manifest.json',dict(seed=SEED,worlds={s:len(read(f'data/{s}_worlds.jsonl')) for s in allrows},joint_views={s:len(rs) for s,rs in allrows.items()},old_fact_count=len(oldkeys),confirmation_overlap=0,endpoint_orders_equal=True,all_intermediate_conditions_supported=True,training_occurrences=9600,each_train_world_occurrences=20,calibration_reuse_occurrences=len(calproof),old_G1_hash=digest(CROSS/f'checkpoints/{NAME}/G1/best.pt')))
 files=[p for p in (ROOT/'data').glob('*') if p.is_file()]+[ROOT/f for f in ['PROTOCOL.md','config.json','common.py','semantics_v1.py','renderer_v1.py','backend.py','task.py']]+list((ROOT/'models').glob('*.json'))
 dump('data/lock.json',dict(before_training_and_generation=True,files={str(p.relative_to(ROOT)):digest(p) for p in files}));print('locked', {s:len(rs) for s,rs in allrows.items()})
if __name__=='__main__':main()
