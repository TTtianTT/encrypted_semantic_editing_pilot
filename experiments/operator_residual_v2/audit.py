"""Final artifact integrity, held-out separation, panel completeness and allocation audit."""
from core import *

def stream(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():yield json.loads(line)

def main():
    protocol=verify_protocol();manifest=read(ROOT/'execution_source_manifest.json')
    amendments=read(ROOT/'execution_amendments.json');correction=amendments['amendments'][0]
    assert manifest['protocol_sha256']==sha(ROOT/'protocol.json')
    for k,v in manifest['inputs'].items():
        if k==str(ROOT/'cross_conditioned.py'):
            assert v==correction['original_code_sha256'] and sha(k)==correction['current_code_sha256']
        else:assert sha(k)==v
    assert sha(ROOT/'decoder_cumulative.py')==amendments['amendments'][1]['code_sha256']
    assert sha(ROOT/'estimator_diagnostics.py')==amendments['estimator_diagnostic']['code_sha256']
    train=rows(ROOT/'train_worlds.jsonl');evaluation=rows(ROOT/'eval_worlds.jsonl')
    def key(w):return tuple(w[k] for k in ('object','color','quantity','status'))
    assert not(set(map(key,train))&set(map(key,evaluation)))
    counts={};unique={}
    panels={
      'attribution':(28800,('seed','world_id','direction','component','alpha','random_seed')),
      'visibility':(9600,('seed','world_id','context','alpha','random_seed')),
      'generalization':(2880,('target_seed','basis_seed','template','world_id')),
      'projection':(11520,('seed','template','sequence','world_id','method','random_seed')),
      'decoder':(8880,('seed','world_id','layer','group','condition')),
      'decoder_cumulative':(3960,('seed','world_id','direction','layer_count','condition')),
      'canonical_control':(4320,('seed','template','state','method','world_id')),
      'estimator_diagnostics':(240,('seed','world_id')),
      'cross_conditioned':(1440,('target_seed','basis_seed','template','world_id'))}
    norm_error=0.;current_preserved=0
    for name,(expected,fields) in panels.items():
        seen=set();count=0
        for r in stream(ROOT/f'results/{name}.jsonl'):
            item=tuple(r[k] for k in fields);assert item not in seen,(name,item);seen.add(item);count+=1
            assert r['world_id'] in protocol['eval_world_ids']
            if name=='attribution':
                norm_error=max(norm_error,abs(r['norm']-r['matched_real_norm']))
                if r['direction']=='injection' and r['component']=='S_perp' and r['alpha']==1 and r['random_seed'] is None:
                    assert r['current_exact'] and not r['next_success'];current_preserved+=1
            if name=='projection':
                assert r['prediction_is_reference_free'] and len(r['steps'])==5
                assert r['full_trajectory']==[all(r['step_successes'][:k]) for k in range(1,6)]
                assert r['encoder_calls']==(5 if r['method']=='reencode' else 1)
            if name=='generalization' and not r['same_mask']:
                assert r['patched_current'] is None and r['patched_next'] is None
        assert count==expected,(name,count,expected);counts[name]=count;unique[name]=len(seen)
    assert norm_error<1e-5 and current_preserved==240
    for seed in SEEDS:
        fit=load(ROOT/f'local/fit_s{seed}.pt');assert set(fit['fit_worlds'])<=set(protocol['train_world_ids'])
        assert not(set(fit['fit_worlds'])&set(protocol['eval_world_ids']))
        old=load(CES/f'local/pca/bart_s{seed}.pt');assert not(set(old['worlds'])&set(protocol['eval_world_ids']))
        assert (fit['q'].T@fit['projector']['beta']).abs().max()<1e-5
        assert len(rows(ROOT/f'results/training_qualification_s{seed}.jsonl'))==96
    canonical=load(ROOT/'local/canonical.pt')
    assert set(r['world_id'] for r in canonical['metas'])==set(protocol['train_world_ids'])
    assert len(canonical['pooled'])==96*2*7
    del canonical
    g4canonical=load(ROOT/'local/g4_canonical_pooled.pt')
    g4archive=rows(REPO/'experiments/algebraic_generalization_v1/G3_trajectories.jsonl')
    assert not(set(r['world_id'] for r in g4canonical['meta'])&set(r['world_id'] for r in g4archive))
    samefit=load(ROOT/'local/g4_same_editor_fit.pt')
    assert not(set(samefit['fit_worlds'])&set(r['world_id'] for r in g4archive))
    same=read(ROOT/'results/g4_same_editor_complete.json');assert not same['test_fitting'] and same['qualified_training_worlds']>=20
    for phase in ('extraction','fit','interventions','projection','decoder','g4_same_editor','canonical_control','cross_conditioned','estimator_diagnostics','decoder_cumulative'):
        marker=read(ROOT/f'results/{phase}_complete.json');assert marker['training_updates']==0
        if 'code_sha256' in marker:
            filename='extract.py' if phase=='extraction' else phase+'.py'
            assert marker['code_sha256']==sha(ROOT/filename),(phase,'Execution source changed')
        if 'files' in marker:assert all(sha(ROOT/k)==v for k,v in marker['files'].items())
    for phase,filename in [('aggregation','aggregate.py'),('supplement','supplement.py')]:
        marker=read(ROOT/f'results/{phase}_complete.json');assert marker['training_updates']==0
        assert marker['code_sha256']==sha(ROOT/filename)
    # Captured from the approved read-only sacct tool invocation. This keeps
    # the deterministic local audit independent of scheduler network access.
    raw=read(ROOT/'results/sacct_snapshot.json')['output']
    jobs=[]
    for line in raw.splitlines()[1:]:
        parts=line.split('|')
        if '.' in parts[0] or not parts[0]:continue
        jid,state,elapsed,start,end,tres=parts[:6]
        assert state==('FAILED' if jid=='3295' else 'COMPLETED'),(jid,state)
        assert 'gres/gpu=1' in tres
        jobs.append(dict(job_id=int(jid),state=state,allocation_seconds=int(elapsed),start=start,end=end,gpus=1))
    assert len(jobs)==9
    allocated=sum(j['allocation_seconds'] for j in jobs);assert allocated<=protocol['total_allocation_cap_seconds']
    intervals=sorted((j['start'],j['end']) for j in jobs)
    assert all(intervals[i][1]<=intervals[i+1][0] for i in range(len(intervals)-1))
    dump('results/resources.json',dict(jobs=jobs,total_gpu_allocation_seconds=allocated,total_gpu_minutes=allocated/60,peak_concurrent_gpus=1))
    hashes={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.py','.slurm','.json','.jsonl','.csv','.md','.svg','.png') and 'logs' not in p.parts and 'local' not in p.parts and p.name not in ('audit.json','artifact_manifest.json')}
    dump('results/artifact_manifest.json',hashes)
    dump('results/audit.json',dict(passed=True,training_updates=0,protocol_sha256=sha(ROOT/'protocol.json'),
        execution_source_snapshot_sha256=sha(ROOT/'execution_source_manifest.json'),frozen_inputs=len(protocol['inputs']),
        execution_amendments_sha256=sha(ROOT/'execution_amendments.json'),sacct_snapshot_sha256=sha(ROOT/'results/sacct_snapshot.json'),
        fitting_eval_content_disjoint=True,counts=counts,unique_counts=unique,maximum_norm_match_error=norm_error,
        reverse_injection_current_exact_next_failed=240,total_gpu_allocation_seconds=allocated,
        historical_world_exposure_not_new_confirmation=True,lexical_ood_donor_patch_mask_mismatch_reported_as_NA=True,
        all_source_hashes_verified=True,audit_code_sha256=sha(__file__)))
    print('Audit passed:',counts,'GPU seconds:',allocated)

if __name__=='__main__':main()
