"""P0: locate and hash every reused input; check worktrees and the frozen BART revision. CPU only."""
import time
from symutil import *

REVISION = 'aadd2ab0ae0c8268c7c9693540e9904811f36177'
SRC = '.four-domain-worktree/experiments/four_domain_state_coverage_v1'
CESR = '.causal-next-edit-worktree/experiments/causal_next_edit_stability_v1'


def entries():
    E = []
    def add(key, path, source, required=True): E.append((key, path, source, required))
    # four-domain generator / evaluator / backend
    for f in ('backend.py', 'semantics.py', 'evaluator.py', 'common.py', 'config.json', 'model_manifest.json', 'train.py'):
        add(f'four_domain/{f}', f'{SRC}/{f}', 'four_domain_state_coverage_v1')
    for d in ('time', 'person', 'space', 'emotion'):
        add(f'four_domain/data/{d}', f'{SRC}/data/{d}/worlds.jsonl', 'four_domain_state_coverage_v1')
    # shared code
    for f in ('core.py', 'interventions.py', 'protocol.json', 'eval_worlds.jsonl', 'train_worlds.jsonl'):
        add(f'operator_residual_v2/{f}', f'experiments/operator_residual_v2/{f}', 'operator_residual_v2')
    for f in ('fit.py', 'shared.py', 'local/rrr.pt'):
        add(f'canonical_write_reachability_v1/{f}', f'experiments/canonical_write_reachability_v1/{f}', 'canonical_write_reachability_v1')
    for split in ('train', 'eval'):
        for t in (0, 3):
            for s in range(-3, 4):
                add(f'cache/cwr/{split}_t{t}_s{s}', f'experiments/canonical_write_reachability_v1/local/{split}_t{t}_s{s}.pt', 'canonical_write_reachability_v1')
    for f in ('protocol.json', 'train_c.py', 'cutil.py'):
        add(f'canonical_objective_v1/{f}', f'experiments/canonical_objective_v1/{f}', 'canonical_objective_v1')
    for g in ('C1', 'C3'):
        for seed in (42, 43, 44):
            add(f'editor/time/{g}/s{seed}', f'experiments/canonical_objective_v1/local/{g}_s{seed}_0600.pt', 'canonical_objective_v1')
        for seed in (45, 46):
            add(f'editor/time/{g}/s{seed}', f'experiments/canonical_confirmation_v1/local/time_{g}_s{seed}_0600.pt', 'canonical_confirmation_v1')
        for seed in (42, 43, 44):
            add(f'editor/person/{g}/s{seed}', f'experiments/canonical_confirmation_v1/local/person_{g}_s{seed}_0600.pt', 'canonical_confirmation_v1', False)
    for f in ('futils.py', 'protocol.json', 'data/time_eval.jsonl', 'data/person_train.jsonl', 'data/person_eval.jsonl', 'results/fresh_closure_summary.json'):
        add(f'canonical_confirmation_v1/{f}', f'experiments/canonical_confirmation_v1/{f}', 'canonical_confirmation_v1')
    for dom, states in (('time', range(-3, 4)), ('person', range(3))):
        for split in (('eval',) if dom == 'time' else ('train', 'eval')):
            for t in ((0, 3) if split == 'eval' else (0,)):
                for s in states:
                    add(f'cache/conf/{dom}_{split}_t{t}_s{s}', f'experiments/canonical_confirmation_v1/local/{dom}_{split}_t{t}_s{s}.pt', 'canonical_confirmation_v1')
    for lab in ('CE_all', 'floor', 'adv_pool_l0.01', 'adv_set_l0.01'):
        for seed in (42, 43, 44):
            add(f'editor/time/{lab}/s{seed}', f'experiments/manifold_controls_v1/local/{lab}_s{seed}.pt', 'manifold_controls_v1')
    for f in ('mutil.py', 'local/person_fits.pt', 'protocol.json', 'job.slurm', 'job_cpu.slurm'):
        add(f'manifold_controls_v1/{f}', f'experiments/manifold_controls_v1/{f}', 'manifold_controls_v1')
    for f in sorted((MAN / 'data').glob('*.jsonl')):
        add(f'history_worlds/manifold_controls_v1/{f.name}', str(f.relative_to(REPO)), 'manifold_controls_v1')
    # E2 residual inputs
    add('ces/configs/test_bart_tasks.json', f'{CESR}/configs/test_bart_tasks.json', 'causal_next_edit_stability_v1')
    for seed in SEEDS:
        add(f'ces/pca/bart_s{seed}', f'{CESR}/local/pca/bart_s{seed}.pt', 'causal_next_edit_stability_v1')
        add(f'ces/pairs/bart_s{seed}', f'{CESR}/local/scan_bart/bart_s{seed}/pairs.jsonl', 'causal_next_edit_stability_v1')
        add(f'ces/editor/bart_time_s{seed}', f'{SRC}/local/formal/bart_time_s{seed}/P/best.pt', 'four_domain_state_coverage_v1')
        add(f'operator_residual_v2/fit_s{seed}', f'experiments/operator_residual_v2/local/fit_s{seed}.pt', 'operator_residual_v2')
    # G3 reference values (cited only)
    for f in ('residual_dynamics.csv', 'jacobian_spectrum.csv'):
        add(f'g3/{f}', f'experiments/algebraic_generalization_v1/{f}', 'algebraic_generalization_v1')
    # model
    for f in ('config.json', 'model.safetensors', 'tokenizer.json', 'vocab.json', 'merges.txt'):
        add(f'model/bart-base/{f}', f'models/bart-base/{f}', 'models')
    add('model/manifest.json', 'models/manifest.json', 'models'); add('model/bart_metadata.json', 'models/bart_metadata.json', 'models')
    return E


def e2_state_files():
    """State tensors referenced by the 80 operator_residual_v2 eval pairs (N->E, plus), per seed."""
    ids = set(read(V2 / 'protocol.json')['eval_world_ids']); out = []
    for seed in SEEDS:
        rs = [r for r in rows(CES / f'local/scan_bart/bart_s{seed}/pairs.jsonl')
              if r['world_id'] in ids and r['donor_source'] == 'N→E' and r['operation'] == 'plus']
        assert len(rs) == len(ids), (seed, len(rs))
        for r in rs:
            p = Path(r['state_path']); p = p if p.is_absolute() else CES / p
            out.append((f'ces/state/s{seed}/{r["world_id"]}', str(p.relative_to(REPO)), 'causal_next_edit_stability_v1', True))
    return out


def main():
    require_slurm(); t0 = time.time(); checks = {}
    checks['four_domain_worktree'] = (REPO / '.four-domain-worktree').is_dir()
    checks['causal_next_edit_worktree'] = (REPO / '.causal-next-edit-worktree').is_dir()
    meta = read(REPO / 'models/bart_metadata.json'); mm = read(SOURCE / 'model_manifest.json')['bart']
    man = {Path(r['path']).name: r for r in read(REPO / 'models/manifest.json') if 'bart-base' in r['path']}
    checks['bart_revision_metadata'] = meta['sha'] == REVISION
    checks['bart_revision_four_domain_manifest'] = mm['revision'] == REVISION
    checks['bart_revision_repo_config'] = read(REPO / 'config.json').get('model_revision') == REVISION
    checks['bart_files_match_models_manifest'] = all(sha(REPO / 'models/bart-base' / n) == r['sha256'] for n, r in man.items())
    checks['bart_dir_matches_backend'] = Path(mm['directory']).resolve() == (REPO / 'models/bart-base').resolve()
    files = []; missing = []
    for key, path, source, required in entries() + e2_state_files():
        p = REPO / path
        if not p.exists():
            missing.append(dict(key=key, path=path, required=required)); continue
        files.append(dict(key=key, path=path, sha256=sha(p), bytes=p.stat().st_size, source_experiment=source))
        print('hashed', key, flush=True)
    checks['required_inputs_present'] = not any(m['required'] for m in missing)
    # person C1/C3 are optional: E0.2 marks them NA when absent
    dump('inputs_manifest.json', dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), bart_revision=REVISION,
                                       checks=checks, missing=missing, n_files=len(files), files=files,
                                       job_id=os.environ['SLURM_JOB_ID'], seconds=time.time() - t0))
    print(json.dumps(checks, indent=1), 'missing', missing, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
