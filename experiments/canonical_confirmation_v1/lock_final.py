"""Create disjoint data and prospectively lock the once-only final experiment."""
from futils import *
import itertools
def main():
 assert not (ROOT/'protocol.json').exists(),'Never overwrite executed confirmation protocol'
 source=old.previous.SOURCE;legacy=[source/'data/time/worlds.jsonl',old.previous.CES/'configs/worlds.jsonl',c.V2/'train_worlds.jsonl',c.V2/'eval_worlds.jsonl']
 def key(w):return tuple(w[k] for k in ('object','color','quantity','status'))
 excluded=set()
 for p in legacy:excluded.update(key(w) for w in rows(p) if w['domain']=='time')
 render,gold,adv,states,score=old.semantics();import semantics
 candidates=[k for k in itertools.product(semantics.OBJECTS,semantics.COLORS,range(1,10),['planned','completed','cancelled']) if k not in excluded];rng=random.Random(271828);rng.shuffle(candidates);assert len(candidates)>=160
 ww=[];prototype=dict(c.worlds('train')[0])
 for i,k in enumerate(candidates[:160]):
  w=dict(prototype);w.update(object=k[0],color=k[1],quantity=k[2],status=k[3],world_id=f'confirm_time_{i:04d}',split='confirmation',new_generated=True,event_date='2026-12-01',quote_date='2026-11-29');ww.append(w)
 write('data/time_eval.jsonl',ww);assert not(excluded&set(map(key,ww)))
 pp=rows(source/'data/person/worlds.jsonl');train=[w for w in pp if w['split']=='train'];assert len(train)==96;write('data/person_train.jsonl',train)
 def pk(w):return tuple(w['people'])+(w['object'],w['color'],w['quantity'])
 seen=set(map(pk,pp));prng=random.Random(314159);person=[]
 while len(person)<80:
  w=dict(pp[0]);w.update(people=prng.sample(semantics.NAMES,3),object=prng.choice(semantics.OBJECTS),color=prng.choice(semantics.COLORS),quantity=prng.randrange(1,10));k=pk(w)
  if k in seen:continue
  seen.add(k);w.update(world_id=f'confirm_person_{len(person):04d}',split='replication',new_generated=True);person.append(w)
 write('data/person_eval.jsonl',person)
 inputs=dict(read(ROOT/'control_protocol.json')['inputs'])
 for f in legacy+[source/'data/person/worlds.jsonl',ROOT/'data/time_eval.jsonl',ROOT/'data/person_train.jsonl',ROOT/'data/person_eval.jsonl',EX/'cutil.py']:
  inputs[str(f.resolve())]=sha(f)
 for seed in (42,43,44):
  for g in ('C1','C3'):f=EX/f'local/{g}_s{seed}_0600.pt';inputs[str(f.resolve())]=sha(f)
 sources={n:sha(ROOT/n) for n in ['futils.py','extract_fresh.py','train_final.py','eval_final.py','closure_final.py','mechanism_final.py','job.slurm']}
 p=dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),rank=16,confirmation_seeds=list(SEEDS),train_worlds=96,confirmation_worlds=160,confirmation_generation_seed=271828,excluded_legacy_cores=len(excluded),available_new_cores=len(candidates),disjoint_key=['object','color','quantity','status'],time_templates=[0,3],paths=PATHS,path_origin='Aligned paths selected post hoc before canonical-objective round; fixed here before all fresh-world scores',
  main_groups=['C1','C3','RRR','reencode'],C4_checkpoints=CKS,training=dict(C1_C3_updates=600,C4_updates=50,optimizer='AdamW',lr=.001,weight_decay=0,clip=1,batch=8,microbatch=2,l2_weight=1,l2_normalization='Per-operation train canonical ideal-write token energy, unchanged from prior experiment',batch_rng='persistent Random(seed), alternation plus first',selection='None; final600 and predeclared C4 checkpoints',reuse='Reuse unchanged C1/C3 endpoints seeds42-44; train45-46 on same96worlds. Replay all5 C4 to50 for dense checkpoints. Exact equality with old10/25/50 required for42-44. RRR deterministic single map, not five independent fits'),
  closure=dict(groups=['C3','RRR'],worlds='First80 newly generated time worlds, fixed before scores',horizons=[10,20,50],paths=['original_alternating','aligned_from_plus_one','aligned_from_minus_one'],evaluate_every_step=True,spectra='Full affine token mapping over closed2/4step cycles; report amplification and forcing, not universal divergence'),
  mechanism=dict(worlds='First80 fresh time worlds',source=1,first_operation='plus',matched_state=0,next_operation='plus',next_state=-1,S='Centered PCA4 of C1 train96 source1->0 differences, per seed, frozen before new-world inference',read_space='row(C1 plus.v)',conditions=['none','full','S','S_R','S_perp','random_S_norm'],alpha=1,eligible='Current edited and canonical states decode correctly, canonical next succeeds, edited next fails; publish all counts and conditional denominators',visibility='KL(canonical||canonical+S_perp) on current and KL(edited_canonical||edited_canonical+S_perp) on next; gold teacher forcing',random_seed=91001),
  replication=dict(model='bart',domain='person',seeds=[42,43,44],train_worlds=96,new_worlds=80,generation_seed=314159,templates=[0,3],groups=['C1','C3','C4','RRR','reencode'],fit='All mask-identical template0 train transitions; fixed ridge1e-4, no evaluation selection',paths='1 plus/minus alternation and2 minus/plus alternation, five steps',boundary='State0 generally length-changing and excluded from aligned fit. Template3 not previously admitted: report canonical/single floors before any composition claim'),
  confidence='Per seed/path/template Wilson95 for one complete trajectory per world; means and state-aggregated metrics bootstrap worlds2000. Deterministic RRR/reencode evaluated once and not counted as independent seeds',limits=['Controlled synthetic worlds; confirmation is fresh semantic cores, not natural text','No new length-changing method, KL or target-network exploration','Sensitivity prevention and robustness are distinct','Finite50steps do not prove closure'],maximum_gpus=1,allocation_cap_seconds=14400,inputs=inputs,sources=sources)
 dump('protocol.json',p);print('locked fresh confirmation',sha(ROOT/'protocol.json'),'excluded',len(excluded),'remaining',len(candidates),flush=True)
if __name__=='__main__':main()
