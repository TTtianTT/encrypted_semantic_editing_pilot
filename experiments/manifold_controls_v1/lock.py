from mutil import *
def main():
 require_slurm();assert not (ROOT/'protocol.json').exists(),'Prospective protocol is immutable'
 source=old.previous.SOURCE;old.semantics();import semantics
 legacy=[source/'data/time/worlds.jsonl',old.previous.CES/'configs/worlds.jsonl',c.V2/'train_worlds.jsonl',c.V2/'eval_worlds.jsonl',CONF/'data/time_eval.jsonl']
 key=lambda w:tuple(w[k] for k in ('object','color','quantity','status'));excluded=set()
 for p in legacy:excluded.update(key(w) for w in rows(p) if w['domain']=='time')
 cores=[k for k in itertools.product(semantics.OBJECTS,semantics.COLORS,range(1,10),['planned','completed','cancelled']) if k not in excluded];random.Random(161803).shuffle(cores);assert len(cores)>=160
 worlds=[]
 for i,k in enumerate(cores[:160]):
  w=dict(c.worlds('train')[0]);w.update(object=k[0],color=k[1],quantity=k[2],status=k[3],world_id=f'manifold_time_{i:04d}',split='confirmation',new_generated=True,event_date='2027-01-12',quote_date='2027-01-10');worlds.append(w)
 write('data/time_confirm.jsonl',worlds)
 pp=rows(source/'data/person/worlds.jsonl');pkey=lambda w:tuple(w['people'])+(w['object'],w['color'],w['quantity']);seen=set(map(pkey,pp+rows(CONF/'data/person_eval.jsonl')));rng=random.Random(141421);person=[]
 while len(person)<240:
  w=dict(pp[0]);w.update(people=rng.sample(semantics.NAMES,3),object=rng.choice(semantics.OBJECTS),color=rng.choice(semantics.COLORS),quantity=rng.randrange(1,10));k=pkey(w)
  if k in seen:continue
  seen.add(k);w.update(world_id=f'reachability_person_{len(person):04d}',new_generated=True);person.append(w)
 for split,ww in [('dev',person[:80]),('confirm',person[80:])]:
  for w in ww:w['split']=split
  write(f'data/person_{split}.jsonl',ww)
 sources={n:sha(ROOT/n) for n in ['mutil.py','extract.py','person_fit.py','person_dev.py','baseline_train.py','baseline_dev.py','confirm.py','job.slurm','job_cpu.slurm']}
 inputs={str(p.resolve()):sha(p) for p in legacy+[source/'data/person/worlds.jsonl',CONF/'data/person_eval.jsonl',CONF/'futils.py',c.ROOT/'cutil.py',c.PRIOR/'fit.py']}
 for p in (ROOT/'data').glob('*.jsonl'):inputs[str(p.resolve())]=sha(p)
 # Every pre-existing cache/checkpoint consulted by fitting/training is pinned.
 for p in (CONF/'local').glob('person_train_t0_s*.pt'):inputs[str(p.resolve())]=sha(p)
 for s in range(-3,4):
  for split in ('train','eval'):
   for t in ((0,) if split=='train' else (0,3)):
    p=c.PRIOR/'local'/f'{split}_t{t}_s{s}.pt'
    if p.exists():inputs[str(p.resolve())]=sha(p)
 p=dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),lock_job_id=os.environ['SLURM_JOB_ID'],maximum_global_gpus=2,model='Frozen BART, existing semantic editor interface',seeds=list(SEEDS),person=dict(train_worlds=96,dev_worlds=80,confirmation_worlds=160,ranks=[16,64,256,768],ridge_grid=[1e-6,1e-5,1e-4,.001,.01],ridge_selection='Per operation/rank minimum dev token MSE; train96 only; no dev refit',rank_selection='Maximum mean dev R5 over forward/reverse paths, then mean all-legal single success, then minimum aligned token MSE, then smallest rank',confirm='Once-only all four ranks for a predeclared rank curve; selected rank is primary. Templates0 and3; report unsupported canonical/single floors. No train updates'),baseline=dict(train_worlds=96,all_legal_transitions=True,template=0,rank=16,updates=600,batch=8,microbatch=2,optimizer='AdamW',lr=.001,weight_decay=0,clip=1,groups=['CE_all','floor','adv_pool','adv_set'],lambda_grid=[.01,.1,1.],dev_worlds=32,dev_origin='First32 of historical80, explicitly exploratory and previously exposed',dev_template=0,selection='Each discriminator: best mean dev R5 across all four paths and all3seeds; then all-legal single success; then smallest lambda. Floor/CE_all no selection; fixed final600',floor='Per-example max(CE(z,y)-stopgrad(CE(E(y),y)),0), before mean; no latent alignment',adversarial='Non-saturating logistic BCE; one discriminator update per editor update; discriminator AdamW lr1e-4 wd0 clip1; frozen backbone; generator CE+lambda*softplus(-D(z))',discriminator_architecture='pool: normalized masked mean ->128 LeakyReLU ->1; set: normalized token ->128->128 LeakyReLU, masked mean and max ->128->1',normalization='Canonical train-only feature mean/std, clamp std0.01',real_sampling='Uniform train canonical sequences from all states, conditioned on exactly same valid length as edited source. No direct access to mask length or padding. Marginal manifold constraint; not target-paired L2. Accessible source lengths differ from target lengths on some transitions',confirmation_worlds=160,templates=[0,3],paths=paths('time'),confirmation='Fresh semantic cores excluded from original data and earlier confirmation; run once after dev selection. Report per seed/path Wilson95, non-target preservation and aligned/mask-changing subsets'),limitations=['Emb2Emb-style adaptation to token memory with CE task loss, not reproduction of original sentence-embedding/cosine objective','A failed finite discriminator or lambda grid does not disprove all manifold methods','CE floor removes incentive but does not prohibit optimizer momentum drift below floor','Development worlds are excluded from selected-model confirmation; three exploratory seeds do not replace a final5-seed confirmation','Decoder-only model/layer/read-write specification awaits user clarification'],inputs=inputs,sources=sources)
 dump('protocol.json',p);print('locked',sha(ROOT/'protocol.json'),'time excluded',len(excluded),'available',len(cores),flush=True)
if __name__=='__main__':main()
