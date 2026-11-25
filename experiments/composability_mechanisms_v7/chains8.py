"""v8 confirmation chains (GPU, after the lock; PLAN v7 C2, C3, B.3). --unit N|G --backbone bart|t5|t5_9b|t5_bb|t5_ll [--smoke].
Every cell of cells8.py and path (plus, minus, alternating; 2N steps from the world start), decoded every step only to score it (shards,
results/shards/chain_<bb>_<d>_natural_<method>_<path>_from_start_*.jsonl). Also reencode (decode of the clean encodings along the plus path).
Unit N: confirm8 (month-nat). Unit G and ladder: confirm7 (template 0; first evaluation for these models).
--smoke (before the lock): dev split, the first three cells, 3-step paths, shards under local/smoke (code path only).
Output: results/chains8_<unit>_<bb>_complete.json."""
import time
import lib8
from cells8 import *


def main():
    require_slurm(); unit = sys.argv[sys.argv.index('--unit') + 1]; bb = sys.argv[sys.argv.index('--backbone') + 1]; smoke = '--smoke' in sys.argv; t0 = time.time()
    if smoke: lib8.SHARDS = ROOT / 'local/smoke/shards'; split = 'dev'
    else: assert lock_ok(), 'confirmation chains only after the lock'; split = CONFIRM if unit == 'N' else 'confirm7'
    eng = engine8(bb); cells = n_cells(eng, bb, split) if unit == 'N' else g_cells(eng, bb, split); done = []
    if smoke: cells = cells[:3]
    doms = sorted({d for _, d, _, _ in cells})
    for fam, d, name, ops in cells:
        ops = ops() if callable(ops) else ops; N = len(S.states(d))
        for path, oplist in PATHS(N).items():
            ol = oplist[:3] if smoke else oplist
            if smoke: run_chain_any(eng, bb, d, name, ops, path, ol, split)
            else: run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol, split=split)
            done.append(f'{d}/{name}/{path}'); print('chain8', unit, bb, d, name, path, flush=True)
    for d in doms:
        N = len(S.states(d)); ol = ['plus'] * (3 if smoke else 2 * N)
        if smoke: run_chain_any(eng, bb, d, 'reencode', None, 'plus', ol, split)
        else: run_chain(eng, bb, d, 'natural', 'reencode', None, 'plus_from_start', 'world_start', ol, split=split)
        done.append(f'{d}/reencode/plus')
    out = ROOT / ('local/smoke' if smoke else 'results') / f'chains8_{unit}_{bb}_complete.json'
    dump(out, dict(unit=unit, backbone=bb, split=split, smoke=smoke, cells=done, resources=eng.resources(), seconds=time.time() - t0, pass_=True))


def run_chain_any(eng, bb, d, name, ops, path, ol, split):
    """Smoke: run_chain on a non-confirm split (no lock assertion applies to dev)."""
    run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol, split=split)


if __name__ == '__main__':
    main()
