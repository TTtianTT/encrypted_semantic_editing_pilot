from mutil import *
def grouped(rs,keys):
 dd=defaultdict(list)
 for r in rs:dd[tuple(r[k] for k in keys)].append(r)
 return dd
def worldmean(rs,fn):
 vv=[float(np.mean([fn(r) for r in v])) for v in grouped(rs,['world_id']).values()]
 return dict(n_worlds=len(vv),mean=float(np.mean(vv)),ci95_world_bootstrap=old.bootstrap_mean(vv)) if vv else None
def auc(a,b):
 a=np.array(a);b=np.array(b);return float(((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:])).mean())
def main():
 p=verify();sel=read(ROOT/'selection.json');summary=[];expected=0
 for domain,labels in [('person',[f'RRR{r}' for r in p['person']['ranks']]+['reencode']),('time',[f'{n}_s{s}' for n in sel['time']['selected_groups'] for s in SEEDS]+['reencode'])]:
  n=len(ws(domain,'confirm'));assert n==160
  fit_graph={(s,op) for op,it in f.items(domain).items() for _,s,_ in it}
  world_index={w['world_id']:i for i,w in enumerate(ws(domain,'confirm'))}
  def naturally_aligned(r):
   a,b=cache(domain,'confirm',r['template'],r['source_state']),cache(domain,'confirm',r['template'],r['target_state']);i=world_index[r['world_id']];size=max(a['m'].shape[1],b['m'].shape[1]);am=torch.nn.functional.pad(a['m'][i],(0,size-a['m'].shape[1]));bm=torch.nn.functional.pad(b['m'][i],(0,size-b['m'].shape[1]));return torch.equal(am,bm)
  for label in labels:
   for t in (0,3):
    chain=[r for path in sorted((ROOT/'results/shards').glob(f'chain_{domain}_confirm_{label}_t{t}_*.jsonl')) for r in old.stream(path)];single=[r for path in sorted((ROOT/'results/shards').glob(f'single_{domain}_confirm_{label}_t{t}_*.jsonl')) for r in old.stream(path)]
    assert len(chain)==n*len(paths(domain))*5,(domain,label,t,len(chain));assert len(single)==n*(12 if domain=='time' else 6),(domain,label,t,len(single));expected+=len(chain)+len(single)
    keys=[(r['world_id'],r['path'],r['step']) for r in chain];assert len(set(keys))==len(keys)
    # Scope is defined from canonical source/target masks, independent of method.
    # Re-encoding changes its mask and otherwise would incorrectly move every
    # transition into the aligned stratum.
    aligned=[r for r in single if naturally_aligned(r)];unaligned=[r for r in single if not naturally_aligned(r)]
    fit_edges=[r for r in single if (r['source_state'],r['operation']) in fit_graph];fit_aligned=[r for r in fit_edges if naturally_aligned(r)]
    out=dict(domain=domain,label=label,template=t,worlds=n,single=worldmean(single,lambda r:r['output']['score']['success']),preserved=worldmean(single,lambda r:r['output']['score']['preserved']),parseable=worldmean(single,lambda r:r['output']['score']['parseable']),aligned_single=worldmean(aligned,lambda r:r['output']['score']['success']),mask_changing_single=worldmean(unaligned,lambda r:r['output']['score']['success']),token_mse=worldmean(aligned,lambda r:r['token_mse']),scope_counts=dict(aligned_edges=len(aligned),mask_changing_edges=len(unaligned)),paths={})
    if domain=='time':out['S_coordinate_mse']={str(seed):worldmean(aligned,lambda r:r['S_coordinate_mse'][str(seed)]) for seed in SEEDS}
    out['canonical_fit_single']=worldmean(fit_edges,lambda r:r['output']['score']['success']);out['canonical_fit_token_mse']=worldmean(fit_aligned,lambda r:r['token_mse']);out['scope_counts']['canonical_fit_edges']=len(fit_edges);out['scope_counts']['canonical_fit_aligned_edges']=len(fit_aligned)
    out['all_edges_correct']=old.rate([all(r['output']['score']['success'] for r in ww) for ww in grouped(single,['world_id']).values()]);out['all_non_target_preserved']=old.rate([all(r['output']['score']['preserved'] for r in ww) for ww in grouped(single,['world_id']).values()]);out['canonical_fit_all_edges_correct']=old.rate([all(r['output']['score']['success'] for r in ww) for ww in grouped(fit_edges,['world_id']).values()])
    for name,rs in grouped(chain,['path']).items():
     panel={f'R{k}':old.rate([r['trajectory_success'] for r in rs if r['step']==k]) for k in range(1,6)};index={(r['world_id'],r['step']):r for r in rs};panel['conditional_continuation']={f'R{k}_given_R{k-1}':old.rate([r['trajectory_success'] for r in rs if r['step']==k and index[r['world_id'],k-1]['trajectory_success']]) for k in range(2,6)}
     assert all(panel[f'R{k}']['k']>=panel[f'R{k+1}']['k'] for k in range(1,5));out['paths'][name[0]]=panel
    summary.append(out)
 dump('results/confirmation_summary.json',summary)
 # Generalization of the selected discriminator, measured on held-out dev.
 ds=[]
 for name in sel['time']['selected_groups']:
  if not name.startswith('adv_'):continue
  for s in SEEDS:
   rs=rows(ROOT/f'results/discriminator_dev_{name}_s{s}.jsonl');a=[r['real_logit'] for r in rs];b=[r['fake_logit'] for r in rs];ds.append(dict(group=name,seed=s,worlds=32,AUROC_real_vs_fake=auc(a,b),accuracy=worldmean(rs,lambda r:((r['real_logit']>0)+(r['fake_logit']<0))/2),real_probability=worldmean(rs,lambda r:1/(1+np.exp(-r['real_logit']))),fake_probability=worldmean(rs,lambda r:1/(1+np.exp(-r['fake_logit'])))))
 dump('results/discriminator_summary.json',ds)
 # Fresh core disjointness against explicit legacy and prospective dev.
 pk=lambda w:tuple(w['people'])+(w['object'],w['color'],w['quantity']);tk=lambda w:tuple(w[k] for k in ('object','color','quantity','status'))
 for d,key in [('person',pk),('time',tk)]:
  fresh=set(map(key,ws(d,'confirm')));assert len(fresh)==160;assert not fresh.intersection(map(key,ws(d,'train')));assert not fresh.intersection(map(key,ws(d,'dev')));assert not fresh.intersection(map(key,f.ws(d,'eval')))
  for path in p['inputs']:
   if path.endswith('worlds.jsonl'):
    assert not fresh.intersection(key(w) for w in rows(path) if w.get('domain')==d)
 # Verify actual update counts, fixed canonical-loss batch fingerprints, and
 # checkpoint digests; do not infer successful training from job exit alone.
 from baseline_train import labels
 fingerprint={};updates=0;checkpoint_index={}
 for group in labels(p):
  for seed in SEEDS:
   label=f'{group}_s{seed}';hist=rows(ROOT/f'results/train_{label}.jsonl');done=read(ROOT/f'results/train_{label}_complete.json');assert len(hist)==600 and done['updates']==600;assert [r['step'] for r in hist]==list(range(1,601));assert all(np.isfinite(v) for r in hist for v in r.values());updates+=len(hist)
   batch_signature=[r['canonical_ce'] for r in hist]
   if seed in fingerprint:assert batch_signature==fingerprint[seed],'Matched groups must use same canonical target batch fingerprints'
   else:fingerprint[seed]=batch_signature
   path=ROOT/f'local/{label}.pt';digest=sha(path);assert digest==done['checkpoint_sha256'];checkpoint_index[label]=dict(sha256=digest,updates=600,group=group,seed=seed)
 dump('checkpoint_index.json',checkpoint_index)
 verify();dump('checks.json',dict(job_id=os.environ['SLURM_JOB_ID'],expected_confirmation_records=expected,unique_complete_grids=True,dev_confirm_train_core_disjoint=True,protocol_verified=True,selection_sha256=sha(ROOT/'selection.json'),training_updates=updates,backbone_updates=0,all_training_histories_finite=True,matched_canonical_batch_fingerprints=True,checkpoint_digests_verified=True))
 # Compact raw evidence while preserving uncompressed digest and deterministic gzip.
 evidence={}
 for kind in ('chain','single'):
  paths0=sorted((ROOT/'results/shards').glob(f'{kind}_*.jsonl'));p0=ROOT/f'results/{kind}.jsonl.gz';import hashlib
  digest=hashlib.sha256();count=0
  with p0.open('wb') as fo:
   with gzip.GzipFile(filename='',mode='wb',fileobj=fo,mtime=0) as gz:
    for source in paths0:
     for line in source.read_bytes().splitlines(keepends=True):digest.update(line);gz.write(line);count+=1
  evidence[str(p0.relative_to(ROOT))]=dict(records=count,sha256=sha(p0),uncompressed_sha256=digest.hexdigest())
 dump('results/evidence.json',evidence)
 print('confirmed audit',expected,'records',flush=True)
if __name__=='__main__':main()
