"""Post-run CPU artifact inventory; does not alter scientific inputs or results."""
import csv
import gzip
import json
from pathlib import Path
from common_g14 import ROOT, G13, digest, dump, verify_lock


def main():
    verify_lock()
    results = json.loads((ROOT / 'result_audit.json').read_text())
    assert results['completed_seeds'] == [42, 43, 44]
    assert results['missing_seeds'] == []
    assert results['confirmation_rows'] == 19200 and results['cases'] == 12
    budget = json.loads((ROOT / 'budget.json').read_text())
    assert budget['within_limits'] and budget['max_concurrent_gpus'] == 2
    jobs = list(csv.DictReader((ROOT / 'slurm_jobs.csv').open()))
    assert len(jobs) == 4 and all(j['state'] == 'COMPLETED' and j['exit_code'] == '0:0' for j in jobs)
    expected = json.loads((ROOT / 'per_example_manifest.json').read_text())
    assert digest(ROOT / 'per_example.jsonl.gz') == expected['gzip_sha256']
    with gzip.open(ROOT / 'per_example.jsonl.gz', 'rt', encoding='utf-8') as stream:
        rows = [json.loads(line) for line in stream]
    assert len(rows) == 19200
    assert all(r['matched'] and r['input_unchanged'] for r in rows)
    for seed in [42, 43, 44]:
        audit = json.loads((ROOT / f'seed_s{seed}_complete.json').read_text())
        assert audit['frozen_before'] == audit['frozen_after']
        assert audit['zero_training'] and not audit['optimizer_created'] and not audit['backward_executed']
    entries = []
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(part in ['local', 'outputs', '__pycache__'] for part in rel.parts):
            continue
        if path.name in ['delivery_manifest.json', 'per_example.jsonl'] or path.suffix == '.tmp':
            continue
        assert path.stat().st_size < 100_000_000
        entries.append(dict(path=str(rel), bytes=path.stat().st_size, sha256=digest(path)))
    dump(ROOT / 'delivery_manifest.json', dict(
        G13_base_commit='c124e8c91a5b379725e17ef89937f4cf9da82301',
        frozen_science_lock_sha256=digest(ROOT / 'data/lock.json'),
        artifact_count=len(entries), artifacts=entries,
        post_result_only=['delivery.py', 'INTERPRETATION.md', 'REPORT.md', 'README.md'],
        all_scientific_files_match_pre_inference_lock=True,
        old_scientific_dependencies_unchanged=True,
        no_base_weights_or_repeated_checkpoints_or_latent_uploaded=True,
        confirmation_records=19200, historical_smoke_records=640,
        historical_unique_comparisons=576, historical_physical_comparisons=768,
        actual_gpu_hours=budget['actual_gpu_hours'], requested_gpu_hours=budget['requested_gpu_hours'],
        peak_concurrent_gpus=budget['max_concurrent_gpus'],
        all_jobs_completed=True, artifact_manifest_excludes_itself=True))
    print('G14 delivery verified:', len(entries), 'artifacts')


if __name__ == '__main__':
    main()
