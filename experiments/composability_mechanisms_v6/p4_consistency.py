"""P4 (GPU, before the lock; PLAN B3, B1 new rule 2). For every v6 cell that holds an R case or control (data/r_cases.json), recompute the
latent chain with v6's own locked code (composability_mechanisms_v5: lib6, cells6; imported from that directory so the dynamics are
exactly the locked ones) and compare the argmax of every locked readout, per world and step, with v6's locked simulation
(results/simulate_<bb>.json.gz). Mismatches must be 0 (stop rule). --backbone bart|t5. Output: results/patch/p4_<bb>.json (this
experiment). The backbone engine is needed only to load the trained editors."""
import gzip
import time
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; V6DIR = HERE.parent / 'composability_mechanisms_v5'
sys.path.insert(0, str(V6DIR))                 # v6's symutil / lib6 / cells6 (ROOT = the v6 directory)
from lib6 import *                             # noqa: E402
import cells6                                  # noqa: E402


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time()
    cases = json.loads((HERE / 'data/r_cases.json').read_text())['cases']
    want = sorted({('M' if c['source'] == 'v6M' else 'C', c['domain'], c['method'], c['path']) for c in cases if c['backbone'] == bb})
    with gzip.open(V6DIR / f'results/simulate_{bb}.json.gz', 'rt') as g: locked = json.load(g)
    eng = engine5(bb); gates = read(V6DIR / f'results/gates_{bb}.json'); ops_of = {}
    if any(u == 'M' for u, *_ in want):
        for d, name, ops, fam in cells6.m_cells(eng, bb, gates, CONFIRM): ops_of['M', d, name] = ops
    if any(u == 'C' for u, *_ in want):
        for d, name, ops, cset in cells6.c_cells(eng, CONFIRM): ops_of['C', d, name] = ops
    out = dict(cells={}, mismatches=0, compared=0)
    for u, d, m, p in want:
        ops = ops_of[u, d, m]; ops = ops() if callable(ops) else ops; N = len(S.states(d))
        model = ctx_model(bb, d, CONFIRM) if u == 'C' else vote_model(bb, d)
        sim = simulate_chain(bb, d, ops, cells6.PATHS(N)[p], model, split=CONFIRM); ref = locked[f'{u}/{bb}/{d}/{m}/{p}']
        assert sim['world_ids'] == ref['world_ids'] and sim['states'] == ref['states']
        mm = sum(int(a != b) for k in ref['argmax'] for ra, rb in zip(sim['argmax'][k], ref['argmax'][k]) for a, b in zip(ra, rb))
        n = sum(len(r) for k in ref['argmax'] for r in ref['argmax'][k])
        out['cells'][f'{u}/{bb}/{d}/{m}/{p}'] = dict(compared=n, mismatches=mm); out['mismatches'] += mm; out['compared'] += n
        print('P4', u, bb, d, m, p, n, mm, flush=True)
    out['pass'] = out['mismatches'] == 0; out['seconds'] = time.time() - t0; out['resources'] = eng.resources()
    (HERE / f'results/patch/p4_{bb}.json').write_text(json.dumps(out, indent=2, default=str) + '\n')
    assert out['pass'], 'P4: recomputed latents differ from the v6 locked simulation (stop rule)'


if __name__ == '__main__':
    main()
