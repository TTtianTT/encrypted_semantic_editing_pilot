"""CPU final delivery audit; no model loading or CUDA operation."""
import collections, gzip, subprocess, torch
from study import *

def check_folder(folder, seed, expected_sha):
    marker=read(folder/'complete.json')
    assert marker['checkpoint_sha']==expected_sha
    for name,sha in marker['outputs'].items():assert digest(folder/name)==sha,(folder,name)
    pairs={r['id']:r for r in rows(ROOT/'data/test_pairs.jsonl')};ws=worldmap()
    for source in ('fixed_T0','U','self','gold_reencode','actual_reencode'):
        rs=rows(folder/f'continuation_{source}.jsonl')
        assert len(rs)==len(pairs)==1408 and {r['id'] for r in rs}==pairs.keys()
        for r in rs:
            p=pairs[r['id']]
            assert r['gold']==p['target_gold'] and r['target']==p['target_text']
            assert r['first_score']==score(r['first_prediction'],p['current_gold'],ws[r['world_id']],r['first_score']['ended'])
            assert r['full2']==bool(r['first_success'] and r['score']['success'])
    for file,n in (('old_natural',768),('ood_natural',384)):
        rs=rows(folder/f'{file}.jsonl');assert len(rs)==n and len({r['id'] for r in rs})==n
    paths={r['id']:r for r in rows(ROOT/'data/long_paths.jsonl')}
    trajectory=collections.defaultdict(list)
    for p in sorted((folder/'trajectories').glob('*.jsonl')):
        for r in rows(p):trajectory[(r['method'],r['id'])].append(r)
    assert len(paths)==512 and len(trajectory)==512*3
    for (method,identifier),rs in trajectory.items():
        path=paths[identifier];rs.sort(key=lambda r:r['step'])
        assert [r['step'] for r in rs]==list(range(1,6))
        full=True;prev=True;first=None
        for k,r in enumerate(rs):
            assert r['operation']==path['operations'][k] and r['current_state']==path['states'][k]
            assert advance('time',path['initial_state'] if k==0 else path['states'][k-1],r['operation'])==r['current_state']
            assert r['previous_success']==prev
            ok=r['score']['success'];full=full and ok
            if not ok and first is None:first=k+1
            assert r['full_success']==full and r['first_failure']==first
            if method=='latent':assert r['latent_reencoded'] is False
            prev=ok
    return dict(seed=seed,path=str(folder.relative_to(ROOT)),continuation_rows=5*1408,trajectory_rows=3*512*5,natural_rows=1152,checkpoint_sha=expected_sha)

def main():
    lock_sha=verify_lock()
    for name in ('CPU_AUDIT','CPU_SMOKE_VERIFICATION','SMOKE_AUDIT','REPOSITORY_AUDIT','PUBLICATION_AUDIT'):
        assert read(ROOT/(name+'.json'))['passed'],name
    assert read(ROOT/'ANALYSIS_AUDIT.json')['all_seeds_complete']
    checks=[];training=[]
    preflights=[read(ROOT/f'runs/preflight/s{s}/complete.json') for s in (42,43,44)]
    assert all(p['passed'] and p['old_natural_predictions_reproduced']==768 for p in preflights)
    last_preflight=max(p['at_utc'] for p in preflights)
    for seed in (42,43,44):
        baseline=ROOT/f'runs/preflight/s{seed}/T0'
        checks.append(check_folder(baseline,seed,digest(checkpoint(seed))))
        first={r['id']:r for r in rows(baseline/'continuation_self.jsonl')}
        goldnext={r['id']:r for r in rows(baseline/'continuation_gold_reencode.jsonl')}
        for r in rows(baseline/'fixed_diagnostic.jsonl'):
            assert r['qualified']==bool(first[r['id']]['first_success'] and goldnext[r['id']]['score']['success'])
        peer={42:43,43:44,44:42}[seed]
        assert read(ROOT/f'local/preflight/s{seed}/fixed_U/complete.json')['source_sha']==digest(checkpoint(peer))
        initial=torch.load(checkpoint(seed),map_location='cpu',weights_only=True)['editor']
        draws=rows(ROOT/f'data/draws_s{seed}.jsonl')
        replay=rows(ROOT/'data/train_core.jsonl');continuation=rows(ROOT/'data/continuation.jsonl')
        reference=None
        for method in ('N','F','R'):
            folder=ROOT/f'local/s{seed}/{method}';logs=rows(folder/'training.jsonl');refresh=read(folder/'refreshes.json')
            assert len(logs)==200 and [r['update'] for r in logs]==list(range(1,201))
            assert all(r['supervision_units']=={'replay':4,'continuation':4} for r in logs)
            selected=[r['selected'] for r in logs]
            if reference is None:reference=selected
            else:assert selected==reference,(seed,method,'sample order')
            for draw,item in zip(draws,logs):
                assert item['operation']==draw['operation']
                assert item['selected']['continuation']==[continuation[i]['id'] for i in draw['continuation']]
                for i in draw['replay']:assert replay[i]['operation']==draw['operation']
                for i in draw['continuation']:assert continuation[i]['b']==draw['operation']
            assert [r['update'] for r in refresh]==(list(range(0,200,20)) if method=='R' else [0])
            for event in refresh:
                cachefolder=folder/(f'cache_R/u{event["update"]:03}' if method=='R' else 'cache_'+method)
                manifest=read(cachefolder/'complete.json')
                assert manifest['detached'] and manifest['fresh_original_encoding']
                assert manifest['unique_prefixes']==768 and manifest['continuation_rows']==1408
                assert manifest['generation_depth']==(0 if method=='N' else 1)
                assert min(read(Path(s['path']).with_suffix('.json'))['at_utc'] for s in manifest['shards'])>last_preflight
                prefixgold={r['prefix_id']:r['current_gold'] for r in continuation}
                ws=worldmap()
                observations=rows(cachefolder/'prefix_quality.jsonl')
                assert {r['prefix_id'] for r in observations}==prefixgold.keys()
                for r in observations:
                    assert r['score']==score(r['prediction'],prefixgold[r['prefix_id']],ws[r['world_id']],r['ended'])
                if method=='F':assert manifest['source_sha']==digest(checkpoint(seed))
                if method=='R':
                    source=folder/f'sources/update{event["update"]:03}.pt'
                    assert digest(source)==manifest['source_sha']==event['source_sha']
                    weights=torch.load(source,map_location='cpu',weights_only=True)['editor']
                    if event['update']==0:assert all(torch.equal(weights[k],v) for k,v in initial.items())
                    if event['update']==100:
                        exported=torch.load(folder/'update100.pt',map_location='cpu',weights_only=True)['editor']
                        assert all(torch.equal(weights[k],v) for k,v in exported.items())
            latest=torch.load(folder/'latest.pt',map_location='cpu',weights_only=False)
            assert latest['update']==200 and latest['initial_sha']==digest(checkpoint(seed))
            assert latest['draws_sha']==digest(ROOT/f'data/draws_s{seed}.jsonl')
            assert set(latest['rng'])=={'python','torch','cuda'} and latest['optimizer']['state']
            for update in (100,200):
                cp=folder/f'update{update:03}.pt'
                weights=torch.load(cp,map_location='cpu',weights_only=True)
                assert weights['initial_sha']==digest(checkpoint(seed)) and weights['update']==update
                assert set(weights['editor'])==set(initial) and sum(t.numel() for t in weights['editor'].values())==152064
                checks.append(check_folder(ROOT/f'runs/formal/s{seed}/{method}_u{update}',seed,digest(cp)))
            training.append(dict(seed=seed,condition=method,optimizer_updates=200,replay=800,continuation=800,source_refreshes=len(refresh),supervision_identical=True))
        assert read(ROOT/f'runs/formal/s{seed}/complete.json')['passed']
    published=read(ROOT/'PUBLICATION_AUDIT.json')
    assert published['archives']==21 and published['exact_editor_exports']==18 and published['supplement_source_manifests']==36
    assert published['exact_R_source_snapshots']==30
    for source in read(ROOT/'SOURCE_SNAPSHOT_INDEX.json'):assert digest(ROOT/source['path'])==source['sha256']
    resource=read(ROOT/'resource_usage.json')
    assert resource['peak_project_gpus']<=2 and resource['peak_account_gpus_since_first_allocation']<=2
    assert all(r['State'] not in ('RUNNING','PENDING','COMPLETING') for r in resource['records'])
    changed=subprocess.check_output(['git','diff','--name-only','0b73738','--','experiments/four_domain_state_coverage_v1'],cwd=WORKTREE,text=True);assert not changed
    original_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ORIGINAL,text=True).strip()
    original_status=subprocess.check_output(['git','status','--porcelain=v1','-uno'],cwd=ORIGINAL,text=True)
    assert original_head==read(ROOT/'CPU_AUDIT.json')['original_git_head'] and not original_status
    for name in ('EXPERIMENT_PLAN.md','coverage.csv','RESULTS.md','ERROR_ANALYSIS.md','RESOURCE_USAGE.md','README.md','summary_by_seed.csv','paired_contrasts.csv','mean_and_range.csv','SOURCE_LINEAGE_RESOLVED.json','CHECKPOINT_INDEX.json','PREDICTION_INDEX.json','LOG_INDEX.json'):
        assert (ROOT/name).exists(),name
    assert not torch.cuda.is_initialized()
    report=dict(passed=True,base_commit='0b73738',scientific_lock_sha256=lock_sha,backbone_files_verified=12,all_seeds_complete=True,checkpoint_evaluations=checks,training_runs=training,published=published,resources=resource,original_worktree_unchanged=True,baseline_experiment_unchanged=True,no_cuda_initialized=True,not_executed=['additional_domains','new_scope_challenges','new_probes','hyperparameter_search'],recovered_technical_failures=read(ROOT/'ENGINEERING_EVENTS.json'),unpassed_admission=[],still_running=[],at_utc=now())
    dump(ROOT/'FINAL_DELIVERY_AUDIT.json',report);print('Final audit passed:21 checkpoints,9 matched training runs,18 small exports')
if __name__=='__main__':main()
