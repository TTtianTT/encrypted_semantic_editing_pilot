"""Frozen source/input integrity, fit disjointness, full panels and Slurm cost."""
from shared import *

def main():
    p=verify();assert not(set(p['fitting_worlds'])&set(p['eval_worlds']))
    assert set(p['fit_partition'])|set(p['dev_partition'])==set(p['fitting_worlds'])
    assert not(set(p['fit_partition'])&set(p['dev_partition']))
    fits=load(ROOT/'local/rrr.pt');assert len(fits)==16
    for (c,op,rank),f in fits.items():
        assert f['left'].shape==(768,rank) and f['right'].shape==(rank,768)
        assert f['fit_worlds']==p['fitting_worlds'] and f['relative_ridge'] in p['ridge_relative_grid']
    keys=set();chains=0;single=0
    for r in stream(ROOT/'results/evaluation.jsonl'):
        assert r['world_id'] in p['eval_worlds']
        key=(r['panel'],r['model'],r['world_id'],r['template'],r.get('sequence'),r.get('source_state'),r.get('operation'))
        assert key not in keys,key;keys.add(key)
        if r['panel']=='chain':
            chains+=1;assert len(r['steps'])==5
            assert r['full_trajectory']==[all(r['step_successes'][:k]) for k in range(1,6)]
        else:single+=1
    assert chains==14*2*2*80 and single==14*2*12*80,(chains,single)
    norms=0
    for r in stream(ROOT/'results/matched_controls.jsonl'):
        if r['condition']!='none':norms=max(norms,abs(r['norm']-r['matched_ridge_norm'])/max(r['matched_ridge_norm'],1e-9))
    assert norms<1e-5
    controls=sum(1 for _ in stream(ROOT/'results/matched_controls.jsonl'));assert controls==3*80*2*10
    assert len(rows(ROOT/'results/probe_states.jsonl'))==480
    assert len(rows(ROOT/'results/probe_calibration.jsonl'))==3*2*7*80*3
    cache=read(ROOT/'results/extract_complete.json')['cache_hashes']
    assert all(sha(ROOT/'local'/k)==v for k,v in cache.items())
    assert sha(ROOT/'local/rrr.pt')==read(ROOT/'results/fit_complete.json')['fit_sha256']
    for stage in ('extract','fit','evaluate','controls','probes','failures','analyze'):assert read(ROOT/f'results/{stage}_complete.json')['training_updates']==0
    jobs=read(ROOT/'run_ledger.json')['job_ids'];raw=read(ROOT/'results/sacct_snapshot.json')['output'];ledger=[]
    for line in raw.splitlines():
        cols=line.split('|')
        if not cols[0].isdigit():continue
        jid,state,elapsed,start,end,tres=cols[:6]
        if int(jid) not in jobs:continue
        assert state=='COMPLETED',(jid,state);assert 'gres/gpu=1' in tres
        ledger.append(dict(job_id=int(jid),state=state,allocation_seconds=int(elapsed),start=start,end=end))
    assert sorted(j['job_id'] for j in ledger)==sorted(jobs)
    intervals=sorted((j['start'],j['end']) for j in ledger);assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
    seconds=sum(j['allocation_seconds'] for j in ledger);assert seconds<=p['total_allocation_cap_seconds']
    dump('results/resources.json',dict(jobs=ledger,total_gpu_allocation_seconds=seconds,peak_concurrent_gpus=1))
    hashes={str(f.relative_to(ROOT)):sha(f) for f in ROOT.rglob('*') if f.is_file() and f.suffix in ('.py','.slurm','.json','.jsonl','.md','.csv','.png','.svg') and not any(part in f.parts for part in ('local','logs','shards')) and f.name not in ('audit.json','artifact_manifest.json')}
    dump('results/artifact_manifest.json',hashes)
    dump('results/audit.json',dict(passed=True,training_updates=0,frozen_inputs=len(p['inputs']),locked_sources=len(p['sources']),all_hashes_verified=True,fit_eval_disjoint=True,
         source_protocol_sha256=sha(ROOT/'protocol.json'),records=dict(single=single,chains=chains,controls=controls),maximum_relative_norm_error=norms,total_gpu_allocation_seconds=seconds,peak_concurrent_gpus=1,
         historical_world_exposure=True,template3_is_OOD_only_for_iid_only=True))
    print('Audit passed.',single,chains,controls,'GPU seconds',seconds)

if __name__=='__main__':main()
