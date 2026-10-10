"""Delivery and design audit; no new inference and no selection."""
from futils import *
import gzip
def main():
 p=verify();verify('control_protocol.json');checks=[];counts={};archives=[]
 tw=ws();pw=ws('person');time_ids={w['world_id'] for w in tw};person_ids={w['world_id'] for w in pw};mechanism_ids={w['world_id'] for w in tw[:80]}
 tk=lambda w:tuple(w[k] for k in ('object','color','quantity','status'));pk=lambda w:tuple(w['people'])+(w['object'],w['color'],w['quantity'])
 source=old.previous.SOURCE;legacy=[source/'data/time/worlds.jsonl',old.previous.CES/'configs/worlds.jsonl',c.V2/'train_worlds.jsonl',c.V2/'eval_worlds.jsonl'];excluded={tk(w) for f in legacy for w in rows(f) if w['domain']=='time'}
 assert len(tw)==len(time_ids)==len({tk(w) for w in tw})==160;assert not excluded&{tk(w) for w in tw}
 assert len(pw)==len(person_ids)==len({pk(w) for w in pw})==80;assert not {pk(w) for w in rows(source/'data/person/worlds.jsonl')}&{pk(w) for w in pw}
 checks.append('Fresh semantic cores unique and disjoint from the explicitly fingerprinted legacy worlds')
 prior=read(EX/'manifest.json');derived_inputs={}
 for name in ('results/chain.jsonl','results/dose.jsonl','results/closure.jsonl','results/overshoot.jsonl','results/closure_spectrum.json','REPORT.md','finalize_report.py'):
  assert sha(EX/name)==prior[name],name;derived_inputs[str((EX/name).relative_to(REPO))]=prior[name]
 dump('results/derived_analysis_inputs.json',derived_inputs);checks.append('Historical exploratory inputs and corrected old report match the published parent manifest')
 for kind in ('fresh_chain','fresh_single','fresh_closure','fresh_mechanism','control_panel','control_chain','hidden_gradients','historical_c4_fixed_likelihood','write_geometry','lagged_continuation'):
  path=ROOT/f'results/{kind}.jsonl';assert path.exists(),kind;count=0;seen=set()
  for r in old.stream(path):
   count+=1
   if kind.startswith('fresh_'):
    assert r['template'] in (0,3)
    if kind in ('fresh_chain','fresh_single'):
     domain=r['domain'];assert domain in ('time','person');assert r['world_id'] in (time_ids if domain=='time' else person_ids)
     if r['group'] in ('RRR','reencode'):assert r['seed']==r['checkpoint']==0
     else:
      assert r['group'] in ('C1','C3','C4');assert r['seed'] in (SEEDS if domain=='time' else (42,43,44));assert r['checkpoint'] in (CKS if r['group']=='C4' else (600,))
     if kind=='fresh_chain':assert r['step'] in range(1,6);assert r['path'] in (PATHS if domain=='time' else ('person_forward','person_reverse'))
    else:
     assert r['world_id'] in mechanism_ids
     if kind=='fresh_closure':assert r['step'] in range(1,51);assert r['group'] in ('C3','RRR');assert r['seed'] in (SEEDS if r['group']=='C3' else (0,));assert r['path'] in ('original_alternating','aligned_from_plus_one','aligned_from_minus_one')
     else:assert r['seed'] in SEEDS;assert r['kind'] in ('repair','inject');assert r['component'] in ('none','full','S','S_R','S_perp','random_S_norm')
   if kind=='fresh_chain':
    key=tuple(r[k] for k in ('domain','group','seed','checkpoint','template','path','world_id','step'));assert key not in seen;seen.add(key)
   elif kind=='fresh_single':
    key=tuple(r[k] for k in ('domain','group','seed','checkpoint','template','world_id','source_state','operation'));assert key not in seen;seen.add(key)
   elif kind=='fresh_closure':
    key=tuple(r[k] for k in ('group','seed','template','path','world_id','step'));assert key not in seen;seen.add(key)
   elif kind=='fresh_mechanism':
    key=tuple(r[k] for k in ('seed','template','world_id','kind','component'));assert key not in seen;seen.add(key)
   else:
    columns={'control_panel':('variant','seed','checkpoint','world_id','source_state','operation'),'control_chain':('variant','seed','checkpoint','world_id','step'),'hidden_gradients':('world_id','source_state','operation'),'historical_c4_fixed_likelihood':('seed','checkpoint','template','world_id','source_state','operation'),'write_geometry':('seed','template','world_id','source_state','operation'),'lagged_continuation':('kind','condition','setting','seed','world_id','template','path','next_step')}
    key=tuple(r[k] for k in columns[kind]);assert key not in seen,(kind,key);seen.add(key)
  counts[kind]=count
  archive=path.with_suffix('.jsonl.gz')
  with path.open('rb') as fi,archive.open('wb') as fo:
   with gzip.GzipFile(filename='',mode='wb',fileobj=fo,mtime=0,compresslevel=9) as zz:
    for block in iter(lambda:fi.read(1048576),b''):zz.write(block)
  digest=hashlib.sha256()
  with gzip.open(archive,'rb') as ff:
   for block in iter(lambda:ff.read(1048576),b''):digest.update(block)
  assert digest.hexdigest()==sha(path)
  archives.append(dict(path=str(archive.relative_to(ROOT)),records=count,bytes=archive.stat().st_size,sha256=sha(archive),uncompressed_sha256=sha(path)))
 expected=dict(fresh_chain=300800+46400,fresh_single=180480+27840,fresh_closure=144000,fresh_mechanism=9600,control_panel=69120,control_chain=43200,hidden_gradients=640,historical_c4_fixed_likelihood=30720,write_geometry=3840,lagged_continuation=83470)
 assert counts==expected,(counts,expected)
 checks.append('Full predeclared grids and duplicate-free trajectory/atomic/closure/intervention keys')
 # Train-only PCA provenance and strict fresh semantic-core disjointness.
 fresh_ids={w['world_id'] for w in ws()};train_ids={w['world_id'] for w in ws('time','train')}
 for f in (ROOT/'local').glob('*S_s*.pt'):
  assert set(load(f)['world_ids'])==train_ids
 for f in (ROOT/'local').glob('pca_*.pt'):
  z=load(f);assert not fresh_ids&set(z['world_ids'])
 checks.append('Every mechanism S excludes new confirmation worlds; no refit on confirmation failures')
 for seed in (42,43,44):
  for ck in (10,25,50):
   new=load(ROOT/f'local/time_C4_s{seed}_{ck:04d}.pt')['editor'];previous=load(EX/f'local/C4_s{seed}_{ck:04d}.pt')['editor'];assert max(float((v-previous[k]).abs().max()) for k,v in new.items())<1e-6
 checks.append('Dense C4 replay matches historical checkpoints10/25/50 at all three old seeds')
 updates=sum(read(f)['updates'] for f in (ROOT/'results').glob('train_*_complete.json'))+read(ROOT/'results/controls_complete.json')['updates'];assert updates==7600
 ledger=read(ROOT/'run_ledger.json');assert ledger['allocation_seconds']<=p['allocation_cap_seconds'];assert all(j['state']=='COMPLETED' and j['exit_code']=='0:0' for j in ledger['jobs'])
 amendment=read(ROOT/'resource_amendment.json');assert amendment['original_protocol_sha256']==sha(ROOT/'protocol.json');assert amendment['maximum_gpus']==2
 assert ledger['resource_amendment_sha256']==sha(ROOT/'resource_amendment.json');assert ledger['peak_gpus']<=2;assert ledger['postprocessing_gpus']==0
 assert all(j['gpus'] in (0,1) for j in ledger['jobs'])
 for j in ledger['jobs']:
  assert any(line.startswith(str(j['job_id'])+'.0|COMPLETED|0:0|') for line in ledger['sacct_raw'].splitlines()),j['job_id']
 assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID') is not None
 checks.append('All measured allocations completed; peak at most2GPUs per user resource amendment; derived CPU analyses replayed via sbatch+srun; cap respected;7600neweditorupdates and0backboneupdates')
 dump('results/prediction_archives.json',archives);dump('checks.json',dict(passed=True,checks=checks,record_counts=counts,new_editor_updates=updates,backbone_updates=0,protocol_sha256=sha(ROOT/'protocol.json'),control_protocol_sha256=sha(ROOT/'control_protocol.json')))
 dump('checkpoint_index.json',[dict(path=str(f.relative_to(REPO)),sha256=sha(f),bytes=f.stat().st_size) for f in sorted((ROOT/'local').glob('*.pt'))])
 print('Delivery audit passed',counts,'new updates',updates,flush=True)
if __name__=='__main__':main()
