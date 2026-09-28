import random,json,collections,itertools
from datetime import date,timedelta
from common import *
SEED=2026092902
STATUSES=['recorded_plan','reported_completed','reported_cancelled']
def world_key(w):return json.dumps({k:w[k] for k in FIELDS},sort_keys=True)
def build_worlds(split,n,seed,used):
 rng=random.Random(seed);out=[]
 for i in range(n):
  while True:
   author,recipient=rng.sample(['Alice','Bob','Carol','David','Emma','Frank','Grace','Henry'],2)
   rd=date(2026,10,1)+timedelta(days=rng.randrange(75));status=STATUSES[i%3];ed=rd if status=='reported_completed' else rd+timedelta(days=5)
   w=dict(record_id=f'v2_{split}_{i:04d}',split=split,author=author,actor=author,recipient=recipient,action=rng.choice(['send','give','bring','deliver']),object=rng.choice(['sensor','book','parcel','ticket']),quantity=rng.randrange(1,10),record_date=rd.isoformat(),event_date=ed.isoformat(),record_status=status,polarity='negative' if (i//3)%2==0 else 'positive',attribution=author,template_family=(8+(i//3)%4 if split=='test_template_ood' else (i//3)%(12 if split=='calibration' else 8)))
   k=world_key(w)
   if k not in used:used.add(k);out.append(w);break
 return out
def main():
 assert not (ROOT/'data/precheck_manifest.json').exists(),'Do not overwrite prepared data'
 old=[]
 for p in (V1/'data').glob('*worlds.jsonl'):old += [json.loads(l) for l in p.read_text().splitlines()]
 used={world_key(w) for w in old};oldkeys=used.copy();splits={s:build_worlds(s,n,SEED+j,used) for j,(s,n) in enumerate([('calibration',60),('train',480),('dev',80),('test_iid',80),('test_template_ood',80)])}
 for split,ws in splits.items():write(f'data/{split}_worlds.jsonl',ws)
 allworlds={w['record_id']:w for ws in splits.values() for w in ws};assert len(allworlds)==780
 # Six rows per training world and exactly shared record/path sampling across G0/G1/G2.
 pairs={g:[] for g in ['G0','G1']};rng=random.Random(SEED+100)
 for w in splits['train']:
  # Perspective source is identical across groups, independent of temporal coverage.
  pops=[d for d in range(-2,3) if eligible(w,['P_13'],d)];poff=rng.choice(pops)
  for path,ops in ATOMIC.items():
   pers='third' if path.endswith('third') else 'first';u=rng.random()
   for group,extent in [('G0',2),('G1',3)]:
    offsets=[d for d in range(-extent,extent+1) if eligible(w,ops,d,pers)];off=poff if ops[0].startswith('P') else offsets[min(int(u*len(offsets)),len(offsets)-1)]
    row=make_row(w,path,ops,off,pers);row['pair_index']=len(pairs[group]);pairs[group].append(row)
 for g,rs in pairs.items():write(f'data/train_{g}.jsonl',rs)
 assert len(pairs['G0'])==len(pairs['G1'])==2880
 for a,b in zip(pairs['G0'],pairs['G1']):
  assert (a['record_id'],a['path'])==(b['record_id'],b['path'])
  if a['operations'][0].startswith('P'):assert a==b
 # V1 exact six-path round-robin schedule: per-path permutations and 16 samples/update.
 paths=sorted(ATOMIC);rng=random.Random(42);streams={p:[] for p in paths};idx={p:[i for i,r in enumerate(pairs['G1']) if r['path']==p] for p in paths};schedule=[]
 for step in range(600):
  path=paths[step%6]
  if len(streams[path])<16:
   pool=idx[path][:];rng.shuffle(pool);streams[path]+=pool
  indices=streams[path][:16];streams[path]=streams[path][16:];schedule.append(dict(step=step+1,path=path,pair_indices=indices,g2_replace=[False]*16))
 candidates=[(i,j) for i,b in enumerate(schedule) for j,k in enumerate(b['pair_indices']) if pairs['G1'][k]['operations']==['T_plus'] and -2<=pairs['G1'][k]['offsets'][0]<=2]
 random.Random(SEED+101).shuffle(candidates);assert len(candidates)>=1600
 for i,j in candidates[:1600]:schedule[i]['g2_replace'][j]=True
 assert sum(sum(b['g2_replace']) for b in schedule)==1600
 write('data/sample_schedule.jsonl',schedule)
 dump('data/g2_replacement_manifest.json',{'total_samples':9600,'temporal_samples':6400,'T_plus_samples':3200,'replaced_occurrences':1600,'fraction_of_all_temporal':.25,'fraction_of_T_plus':.5,'eligible_occurrences':len(candidates),'unique_replaced_pair_indices':len({schedule[i]['pair_indices'][j] for i,j in candidates[:1600]})})
 # Coverage accounting includes explicit zero/inapplicable cells. No invented future completed events.
 counts=[]
 for g,extent in [('G0',2),('G1',3)]:
  cc=collections.Counter((r['offsets'][0],r['operations'][0],r['record_status'],r['polarity'],r['frames'][0]['perspective']) for r in pairs[g] if r['operations'][0].startswith('T'))
  for d,op,status,pol,pers in itertools.product(range(-extent,extent+1),['T_plus','T_minus'],STATUSES,['negative','positive'],['first','third']):
   w=next(w for w in splits['train'] if w['record_status']==status);legal=eligible(w,[op],d,pers);n=cc[d,op,status,pol,pers];assert not legal or n>0,(g,d,op,status,pol,pers)
   counts.append(dict(group=g,offset=d,operation=op,status=status,polarity=pol,perspective=pers,legal=legal,N=n))
 csvwrite('data/coverage_counts.csv',counts)
 excluded=[]
 for split in ['dev','test_iid','test_template_ood']:
  atom=[];chain=[];extended=[];rng=random.Random(SEED+200+list(splits).index(split))
  for w in splits[split]:
   offsets=[d for d in range(-2,3) if all(eligible(w,op,d,'third' if p.endswith('third') else 'first') for p,op in ATOMIC.items())];off=rng.choice(offsets)
   for path,ops in ATOMIC.items():atom.append(make_row(w,path,ops,off,'third' if path.endswith('third') else 'first'))
   for path,ops in CHAINS.items():
    limit=1 if len(ops)==3 else 2;allowed=[d for d in range(-limit,limit+1) if eligible(w,ops,d)]
    if not allowed:excluded.append(dict(split=split,record_id=w['record_id'],path=path,status=w['record_status'],reason='no legal starting offset with every frame >= record_date'));continue
    d=rng.choice(allowed);row=make_row(w,path,ops,d);assert all(ok for op,ok in zip(ops,row['source_support_G1']) if op.startswith('T')),row;chain.append(row)
   for op in ['T_plus','T_minus']:
    for d in [-3,3]:
     for pers in ['first','third']:
      if eligible(w,[op],d,pers):extended.append(make_row(w,op+'_extended_'+pers,[op],d,pers))
  write(f'data/{split}_atomic.jsonl',atom);write(f'data/{split}_chains.jsonl',chain);write(f'data/{split}_extended.jsonl',extended)
 csvwrite('data/structural_inapplicability.csv',excluded)
 # Calibration exhausts all legal lexical offsets -4..4 and both perspectives.
 cal=[]
 for w in splits['calibration']:
  for d in range(-4,5):
   for pers in ['first','third']:
    c=frame(w,d,pers)
    if valid(w,[c]):cal.append(make_row(w,'reconstruction',[],d,pers))
 write('data/calibration_views.jsonl',cal)
 # Gold coverage + independent source-only rules for all rows and all G2 substituted endpoints.
 auditrows=[]
 for p in (ROOT/'data').glob('*.jsonl'):
  if p.name.endswith('_worlds.jsonl') or p.name=='sample_schedule.jsonl':continue
  auditrows+=read(p.relative_to(ROOT))
 for i,b in enumerate(schedule):
  for j,k in enumerate(b['pair_indices']):
   if b['g2_replace'][j]:
    row=pairs['G1'][k];auditrows.append(make_row(allworlds[row['record_id']],row['path'],['T_plus','T_plus'],row['offsets'][0],row['frames'][0]['perspective']))
 for r in auditrows:
  w=allworlds[r['record_id']];assert score(r['target_text'],r['frames'][-1],w)['joint_ok'];text=r['source_text']
  for op,c0,c1 in zip(r['operations'],r['frames'],r['frames'][1:]):text,e=text_rule(text,c0,c1);assert e is None
  assert score(text,r['frames'][-1],w)['joint_ok']
 texts=collections.defaultdict(set)
 for r in auditrows:
  for t in [r['source_text'],r['target_text']]:texts[' '.join(t.lower().split())].add(r['split'])
 assert not [t for t,sp in texts.items() if len(sp)>1]
 review=random.Random(SEED+300);picked=[]
 for split in ['test_iid','test_template_ood']:picked += sorted(review.sample([w['record_id'] for w in splits[split]],10))
 dump('review/preselected_worlds.json',{'seed':SEED+300,'worlds':picked,'N':20,'selected_before_model_outputs':True})
 dump('path_matrix.json',{'atomic':ATOMIC,'chains':CHAINS,'modes':['latent_chain','decode_reencode'],'structural_inapplicability':'completed/minus3; positive offsets for completed; explicit fixed eligibility file','G2_supervised_chain':['T_plus','T_plus'],'G2_gate':json.loads((ROOT/'config.json').read_text())['c_gate']})
 dump('data/precheck_manifest.json',{'seed':SEED,'world_counts':{s:len(ws) for s,ws in splits.items()},'new_worlds':780,'v1_overlap':len({world_key(w) for w in allworlds.values()}&oldkeys),'gold_and_rule_checked_rows':len(auditrows),'gold_and_rule_joint':1.,'calibration_views':len(cal),'precheck_passed':True,'test_not_locked_until_reconstruction_pass':True,'files':{p.name:digest(p) for p in (ROOT/'data').glob('*') if p.is_file() and p.name!='precheck_manifest.json'}})
 print('prepared',len(auditrows),'gold/rule checks;',len(cal),'calibration views;',len(excluded),'structural exclusions')
if __name__=='__main__':main()
