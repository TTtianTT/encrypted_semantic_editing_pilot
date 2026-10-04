"""Condition-independent manifests and actual supervision coverage, no neural code."""
import random,csv,collections,shutil
from study import *

def pairs(ws,templates):
    out=[]
    for w in ws:
      for t in templates:
       for s in states('time'):
        for a in ('plus','minus'):
         try:c=advance('time',s,a)
         except ValueError:continue
         for b in ('plus','minus'):
          try:z=advance('time',c,b)
          except ValueError:continue
          pid=f"{w['world_id']}_t{t}_s{s}_a{a}"
          out.append(dict(id=pid+'_b'+b,prefix_id=pid,world_id=w['world_id'],template=t,initial_state=s,a=a,current_state=c,b=b,target_state=z,original_text=render(w,s,t),current_text=render(w,c,t),target_text=render(w,z,t),current_gold=gold(w,c,t),target_gold=gold(w,z,t)))
    return out

def schedule(seed,replay,cont,updates=200):
    rng=random.Random(seed);pools={}
    for role,rs in (('replay',replay),('continuation',cont)):
     for op in ('plus','minus'):
      cells=collections.defaultdict(list)
      for i,r in enumerate(rs):
       if r.get('operation',r.get('b'))==op:
        key=(r['state'],r['template']) if role=='replay' else (r['current_state'],r['a'],r['template'])
        cells[key].append(i)
      for v in cells.values():rng.shuffle(v)
      keys=sorted(cells);rng.shuffle(keys);pools[role,op]=(cells,keys,collections.Counter())
    out=[]
    for u in range(updates):
     op=('plus','minus')[u%2];item=dict(update=u,operation=op)
     for role in ('replay','continuation'):
      cells,keys,pos=pools[role,op];ids=[]
      for k in range(4):
       key=keys[((u//2)*4+k)%len(keys)];v=cells[key];ids.append(v[pos[key]%len(v)]);pos[key]+=1
      item[role]=ids
     out.append(item)
    return out

def main():
    (ROOT/'data').mkdir(parents=True,exist_ok=True)
    ws=rows(BASE/'data/time/worlds.jsonl');train=[w for w in ws if w['split']=='train'];test=[w for w in ws if w['split']=='test']
    jsonl(ROOT/'data/worlds.jsonl',ws)
    for f in ('train_core','dev_core','test_core','test_expression'):
      shutil.copyfile(BASE/f'data/time/{f}.jsonl',ROOT/f'data/{f}.jsonl')
    cont=pairs(train[:32],[0,1]);testpairs=pairs(test,[0,2]);jsonl(ROOT/'data/continuation.jsonl',cont);jsonl(ROOT/'data/test_pairs.jsonl',testpairs)
    long=[]
    specifications=[(3,['plus']*5,'monotone'),(2,['plus']*5,'monotone'),(-3,['minus']*5,'monotone'),(-2,['minus']*5,'monotone'),(0,['plus','minus','plus','minus','plus'],'alternating'),(0,['minus','plus','minus','plus','minus'],'alternating'),(3,['plus','minus','plus','minus','plus'],'boundary_alternating'),(-3,['minus','plus','minus','plus','minus'],'boundary_alternating')]
    for w in test:
     for t in (0,2):
      for i,(s,ops,fam) in enumerate(specifications):
       st=s;ss=[]
       for op in ops:st=advance('time',st,op);ss.append(st)
       long.append(dict(id=f"{w['world_id']}_t{t}_path{i}",world_id=w['world_id'],template=t,initial_state=s,operations=ops,states=ss,family=fam,original_text=render(w,s,t)))
    jsonl(ROOT/'data/long_paths.jsonl',long)
    replay=rows(ROOT/'data/train_core.jsonl');coverage=[]
    for seed in (42,43,44):
     draws=schedule(seed,replay,cont);jsonl(ROOT/f'data/draws_s{seed}.jsonl',draws);counts=collections.Counter()
     for d in draws:
      for role in ('replay','continuation'):
       for i in d[role]:
        r=(replay if role=='replay' else cont)[i]
        key=(role,r.get('state',r.get('initial_state')),r.get('a','natural'),r.get('current_state',r.get('state')),r.get('operation',r.get('b')),r.get('target_state',r['gold']['state'] if 'gold' in r else None),r['template'])
        counts[key]+=1
     for key,n in sorted(counts.items(),key=str):
      for method in ('N','F','R'):coverage.append(dict(seed=seed,condition=method,role=key[0],initial_state=key[1],prefix=key[2],current_state=key[3],operation=key[4],target_state=key[5],template=key[6],units=n))
    with (ROOT/'coverage.csv').open('w') as f:
     writer=csv.DictWriter(f,fieldnames=list(coverage[0]));writer.writeheader();writer.writerows(coverage)
    lineage=[]
    index=read(BASE/'checkpoints_index.json')
    for seed in (42,43,44):
     ent=next(v for v in index if v['phase']=='formal' and v['run']==f't5gemma_time_s{seed}' and v['role']=='P')
     assert digest(checkpoint(seed))==ent['published_sha'];lineage.append(dict(seed=seed,U_seed={42:43,43:44,44:42}[seed],checkpoint=str(checkpoint(seed)),sha256=digest(checkpoint(seed)),old_checkpoint=ent))
    dump(ROOT/'SOURCE_LINEAGE.json',dict(reference_commit='0b73738',sources=lineage,source_rule='U is the next seed original P, frozen; neither old supplement checkpoints nor offset-U is used'))
    dump(ROOT/'data/manifest.json',dict(generation_seed=20261003,world_counts=dict(collections.Counter(w['split'] for w in ws)),continuation_train_worlds=[w['world_id'] for w in train[:32]],test_worlds=[w['world_id'] for w in test],test_worlds_shared_across_IID_OOD=True,files={str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'data').glob('*.jsonl'))},baseline_commit='0b73738',reachable_current_states=states('time'),unreachable_current_states=[]))
    print('Prepared',len(cont),'continuation records;',len(testpairs),'two-step tests;',len(long),'long paths')
if __name__=='__main__':main()
