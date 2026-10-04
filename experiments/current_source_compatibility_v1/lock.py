from study import *
def main():
    assert read(ROOT/'CPU_AUDIT.json')['passed']
    existing=ROOT/'scientific_lock.json'
    if existing.exists():verify_lock();print('Existing scientific lock unchanged');return
    files=[*ROOT.glob('*.py'),ROOT/'config.json',ROOT/'EXPERIMENT_PLAN.md',ROOT/'coverage.csv',ROOT/'SOURCE_LINEAGE.json',ROOT/'job.slurm',*list((ROOT/'data').glob('*'))]
    files += [BASE/n for n in ('backend.py','config.json','model_manifest.json','semantics.py','evaluator.py','evaluate.py')]
    files += [checkpoint(s) for s in (42,43,44)]
    dump(existing,dict(created_utc=now(),base_commit='0b73738',files={str(p.relative_to(WORKTREE)):digest(p) for p in sorted(files) if p.is_file()}));print('Scientific configuration locked')
if __name__=='__main__':main()
