"""Pre-lock latent predictions on confirm7 (GPU; encoding only, no decoding; PLAN v7 B10). --backbone bart|t5. For every unit-U cell and
path: simulate_chain7 (readout, normalised margin m, off-manifold rho per world and step) and the per-world predictions of the slot-only
predictor and of U with the calibrated thresholds (primary and secondary versions; results/calib_u_<bb>.json). The unit-A latent quantity
(rho on the F_empty chains of the held-out templates) is stored in these simulations but not summarised here: A1 and A2 are computed
only after the lock (analyze.py, a_cycle.py). Output: results/simulate_<bb>.json.gz,
results/simulate_<bb>_summary.json."""
import gzip
import time
from lib7 import *
from cells7 import u_cells, PATHS


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; split = sys.argv[sys.argv.index('--split') + 1] if '--split' in sys.argv else CONFIRM
    outdir = Path(sys.argv[sys.argv.index('--out') + 1]).resolve() if '--out' in sys.argv else ROOT / 'results'; t0 = time.time(); eng = engine5(bb)
    cal = read(ROOT / f'results/calib_u_{bb}.json'); th = {v: (cal[v]['tau_m'], cal[v]['tau_r']) for v in ('primary', 'secondary')}
    sims = {}; summ = {}; mans = {}; models = {}
    todo = [(c, split) for c in u_cells(eng, bb, split)] + ([(c, "dev7ho") for c in u_cells(eng, bb, "dev7ho")] if split == "dev" else [])
    for (fam, d, name, ops), sp in todo:
        ops = ops() if callable(ops) else ops; N = len(S.states(d))
        if (d, sp) not in mans: mans[d, sp] = manifold(bb, d, sp); models[d] = vote_model(bb, d)
        for path, oplist in PATHS(N).items():
            key = f"U/{bb}/{d}/{name}/{path}" + ("" if sp == split else "@" + sp); sim = simulate_chain7(bb, d, ops, oplist, models[d], split=sp, man=mans[d, sp]); sims[key] = sim
            pred = dict(slot=u_predict(sim, None, None), **{v: u_predict(sim, *th[v]) for v in th})
            summ[key] = dict(family=fam, domain=d, method=name, path=path, N=N, worlds=len(sim['world_ids']), **{f'pred_{k}': float(np.mean(v)) for k, v in pred.items()})
            sim['pred'] = pred
            print('sim', key, fam, {k: round(summ[key][f'pred_{k}'], 3) for k in pred}, flush=True)
    f = outdir / f'simulate_{bb}.json.gz'; f.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(f, 'wt') as g: json.dump(sims, g)
    out = dict(backbone=bb, split=split, thresholds=th, cells=summ, simulate_sha256=sha(f), seconds=time.time() - t0, resources=eng.resources())
    dump(outdir / f'simulate_{bb}_summary.json', out)


if __name__ == '__main__':
    main()
