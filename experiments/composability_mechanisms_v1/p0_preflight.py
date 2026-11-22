"""P0: locate and hash the v1 artifacts and shared inputs reused here; verify the frozen BART revision. CPU only."""
import time
from symutil import *
import sym2_semantics as S2

REVISION = 'aadd2ab0ae0c8268c7c9693540e9904811f36177'
SRC = '.four-domain-worktree/experiments/four_domain_state_coverage_v1'
V1R = 'experiments/symmetry_composability_v1'


def entries():
    E = []
    add = lambda key, path, src='symmetry_composability_v1': E.append((key, path, src))
    for f in ('backend.py', 'semantics.py', 'evaluator.py', 'common.py', 'config.json', 'model_manifest.json', 'train.py'):
        add(f'four_domain/{f}', f'{SRC}/{f}', 'four_domain_state_coverage_v1')
    for d in ('time', 'person', 'space', 'emotion'):
        add(f'history/four_domain/{d}', f'{SRC}/data/{d}/worlds.jsonl', 'four_domain_state_coverage_v1')
    for f in sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']:
        add(f'history/{f.parent.name}/{f.name}', str(f.relative_to(REPO)), f.parent.name)
    add('operator_residual_v2/core.py', 'experiments/operator_residual_v2/core.py', 'operator_residual_v2')
    for f in ('fit.py', 'shared.py'):
        add(f'canonical_write_reachability_v1/{f}', f'experiments/canonical_write_reachability_v1/{f}', 'canonical_write_reachability_v1')
    for f in ('sym_semantics.py', 'sym_evaluator.py', 'symutil.py', 'e1_encode.py', 'e1_fit_rrr.py', 'e1_train.py', 'e1_eval.py',
              'e1_algebra.py', 'e1_geometry.py', 'protocol.json', 'protocol_lock.json', 'inputs_manifest.json', 'data/manifest.json'):
        add(f'v1/{f}', f'{V1R}/{f}')
    for d in V1_DOMAINS:
        add(f'v1/data/{d}', f'{V1R}/data/{d}/worlds.jsonl')
        for split in ('train', 'dev'):
            for t in (0, 3):
                add(f'v1/pooled/{d}_{split}_t{t}', f'{V1R}/local/e1_pooled_{d}_{split}_t{t}.pt')
            for s in S2.states(d):
                add(f'v1/cache/{d}_{split}_t0_s{s}', f'{V1R}/local/e1_{d}_{split}_t0_s{s}.pt')
        add(f'v1/rrr/{d}', f'{V1R}/local/e1_rrr_{d}.pt')
        for g in ('C1', 'C3'):
            for seed in SEEDS:
                add(f'v1/editor/{d}/{g}/s{seed}', f'{V1R}/local/e1_{g}_{d}_s{seed}_0600.pt')
    for f in ('config.json', 'model.safetensors', 'tokenizer.json', 'vocab.json', 'merges.txt'):
        add(f'model/bart-base/{f}', f'models/bart-base/{f}', 'models')
    add('model/manifest.json', 'models/manifest.json', 'models'); add('model/bart_metadata.json', 'models/bart_metadata.json', 'models')
    return E


def main():
    require_slurm(); t0 = time.time()
    meta = read(REPO / 'models/bart_metadata.json'); mm = read(SOURCE / 'model_manifest.json')['bart']
    man = {Path(r['path']).name: r for r in read(REPO / 'models/manifest.json') if 'bart-base' in r['path']}
    checks = dict(four_domain_worktree=(REPO / '.four-domain-worktree').is_dir(), bart_revision_metadata=meta['sha'] == REVISION,
                  bart_revision_four_domain_manifest=mm['revision'] == REVISION, bart_revision_repo_config=read(REPO / 'config.json').get('model_revision') == REVISION,
                  bart_files_match_models_manifest=all(sha(REPO / 'models/bart-base' / n) == r['sha256'] for n, r in man.items()),
                  v1_protocol_locked=read(V1 / 'protocol.json').get('locked') is True)
    # v1 local artifacts must match the SHAs v1 recorded at creation time
    rec = {}
    for f in sorted((V1 / 'results').glob('e1_encode_*_complete.json')):
        rec.update({k: v['sha256'] for k, v in read(f)['files'].items()})
    for d in V1_DOMAINS:
        rec[f'e1_rrr_{d}.pt'] = read(V1 / f'results/e1_rrr_{d}_complete.json')['fit_sha256']
        for g in ('C1', 'C3'):
            for seed in SEEDS:
                rec[f'e1_{g}_{d}_s{seed}_0600.pt'] = read(V1 / f'results/e1_train_{g}_{d}_s{seed}_complete.json')['final_sha256']
    files = []; missing = []; mismatch = []
    for key, path, src in entries():
        p = REPO / path
        if not p.exists():
            missing.append(path); continue
        h = sha(p); files.append(dict(key=key, path=path, sha256=h, bytes=p.stat().st_size, source_experiment=src))
        if p.parent.name == 'local' and p.name in rec and rec[p.name] != h:
            mismatch.append(path)
    checks['required_inputs_present'] = not missing; checks['v1_local_sha_match_v1_records'] = not mismatch
    checks['v1_local_files_checked_against_records'] = sum(1 for f in files if Path(f['path']).name in rec)
    dump('inputs_manifest.json', dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), bart_revision=REVISION, checks=checks,
                                      missing=missing, mismatch=mismatch, n_files=len(files), files=files, job_id=os.environ['SLURM_JOB_ID'], seconds=time.time() - t0))
    print(json.dumps(checks, indent=1), missing[:5], mismatch[:5], flush=True)
    assert all(v for k, v in checks.items() if isinstance(v, bool)), checks


if __name__ == '__main__':
    main()
