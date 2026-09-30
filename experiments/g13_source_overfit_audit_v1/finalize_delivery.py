"""CPU-only delivery integrity check and explicit Git artifact hashes."""
import subprocess
from common_g13 import *

def main():
    verify_lock()
    manifests=[]
    for s in CFG['seeds']:
        done=json.loads((ROOT/f'seed_s{s}_complete.json').read_text())
        assert done['passed'] and done['groups']==CFG['methods'] and done['caches_unchanged']
        cohort=json.loads((ROOT/f'data/cohort_s{s}.json').read_text())
        assert cohort['locked_before_all_R']
        initial=[]; budgets=[]
        for method in CFG['methods']:
            meta=json.loads((ROOT/f'training/{method}_s{s}.json').read_text())
            assert meta['updates']==200 and meta['counts']['instances']==6400
            assert all(meta[k] for k in ['G_unchanged','ED_unchanged','caches_unchanged'])
            assert meta['schedule_sha256']==cohort['schedule_sha256']
            initial.append(meta['initial_hash']); budgets.append(meta['counts'])
            for label in ['final','best']:
                path=ROOT/meta[label+'_path']; assert digest(path)==meta[label+'_sha256']
            if method=='F3':
                c=list(meta['anchor_source_counts'].values()); assert max(c)-min(c)<=1 and sum(c)==3200
            manifests.append(dict(method=method,seed=s,updates=meta['updates'],counts=meta['counts'],final_sha256=meta['final_sha256'],best_sha256=meta['best_sha256']))
        assert len(set(initial))==1 and initial[0]==done['G_state_hash']
        assert budgets[1]==budgets[2]==budgets[3]
        assert digest(ROOT/f'baseline/other_operators_s{s}_before.jsonl')==digest(ROOT/f'baseline/other_operators_s{s}_after.jsonl')
    per=json.loads((ROOT/'per_example_manifest.json').read_text()); assert per['rows']==457920
    assert digest(ROOT/'per_example.jsonl.gz')==per['gzip_sha256']
    cases=json.loads((ROOT/'case_selection.json').read_text()); assert cases['actual_total']==24 and cases['no_fabrication']
    budget=json.loads((ROOT/'budget.json').read_text())
    assert budget['within_limit'] and budget['actual_gpu_hours']<=12 and budget['requested_gpu_hours']<=12
    assert budget['max_concurrency']<=2 and budget['concurrency_computed_from_allocation_start_end']
    dump(ROOT/'delivery_verification.json',dict(passed=True,complete_seeds=CFG['seeds'],complete_trainings=len(manifests),lock_unchanged=True,final_and_best_checkpoint_hashes_verified=True,common_initial_state_per_seed=True,independent_operator_outputs_unchanged=True,shared_source_schedule_per_seed=True,F123_instance_and_token_budgets_equal=True,F3_source_counts_balanced=True,per_example_rows=per['rows'],fixed_cases=24,budget=budget,training=manifests,optional_H3_H4='not run, not a zero-success result'))
    relative=str(ROOT.relative_to(REPO))
    files=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','--',relative],cwd=REPO,text=True).splitlines())
    files.discard(relative+'/artifact_manifest.json')
    artifacts=[]
    for rel in sorted(files):
        p=REPO/rel
        assert p.is_file() and not p.is_symlink(),rel
        assert not any(x in p.parts for x in ['local','outputs','learning','__pycache__']),rel
        assert p.name!='per_example.jsonl' and not ('_step' in p.name and p.suffix=='.pt'),rel
        assert p.stat().st_size<100_000_000,rel
        artifacts.append(dict(path=rel,bytes=p.stat().st_size,sha256=digest(p)))
    dump(ROOT/'artifact_manifest.json',dict(baseline_commit=json.loads((ROOT/'runs_manifest.json').read_text())['baseline'],scientific_lock_sha256=digest(ROOT/'data/lock.json'),files=artifacts,self_excluded_to_avoid_circular_hash=True,large_local_artifacts='data/cache_s*.json includes exact latent paths/hashes; per_example_manifest.json records plain-text artifact path/hash; latent caches, base weights, environment and resumable optimizer files are not uploaded'))
    print(json.dumps(dict(passed=True,trainings=len(manifests),artifact_files=len(artifacts),total_bytes=sum(x['bytes'] for x in artifacts))))

if __name__=='__main__': main()
