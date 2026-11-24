"""U threshold calibration (CPU, before the lock; PLAN v7 B7, appendix A.4) on the decoded dev chains (results/devchains_<bb>.json.gz).
--backbone bart|t5. Grid tau_m in {none, 0, .1, .2, .3, .4, .5} x tau_r in {none, .05, .1, .2, .3, .5, .75, 1}; per backbone the pair with the
highest per-world agreement over the calibration cells; ties -> the most permissive pair (no limit first, then the lowest tau_m / the
highest tau_r).
Primary version: every dev cell (template-0 dev, training-template dev, dev7-ho). Secondary version: template-0 dev and training-template dev
only (transfer to unseen templates). Also the B7 discriminability pre-check: on the F1 and F2 dev cells, primary U minus slot-only
agreement >= 0.02 (else U1 / U2 become exploratory). Output: results/calib_u_<bb>.json."""
import gzip
import time
from lib7 import *


def _perm(tm, tr):
    return (0 if tm is None else 1 + TAU_M.index(tm), 0 if tr is None else 1 + sorted([x for x in TAU_R if x is not None], reverse=True).index(tr))


def agreement(cells, tm, tr):
    ok = [p == o for sim, obs in cells for p, o in zip(u_predict(sim, tm, tr), obs)]; return float(np.mean(ok)) if ok else None


def calibrate_u(cells, grid_m=None, grid_r=None):
    """cells: [(sim with argmax / states / m / rho, observed trajectory success per world)]. Returns (best, table)."""
    table = []
    for tm in grid_m or TAU_M:
        for tr in grid_r or TAU_R: table.append(dict(tau_m=tm, tau_r=tr, agreement=agreement(cells, tm, tr)))
    best = max(table, key=lambda x: (x['agreement'], tuple(-v for v in _perm(x['tau_m'], x['tau_r']))))
    return dict(best), table


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time()
    with gzip.open(ROOT / f'results/devchains_{bb}.json.gz', 'rt') as g: dc = json.load(g)
    cells = {k: (v['sim'], v['obs']) for k, v in dc['cells'].items()}
    prim = list(cells.values()); sec = [c for k, c in cells.items() if dc['cells'][k]['split'] != 'dev7ho']
    best, table = calibrate_u(prim); best2, table2 = calibrate_u(sec)
    fam = [c for k, c in cells.items() if dc['cells'][k]['family'] in ('F1', 'F2')]
    slot = agreement(fam, None, None); uu = agreement(fam, best['tau_m'], best['tau_r'])
    out = dict(backbone=bb, primary=best, secondary=best2, table_primary=table, table_secondary=table2,
               calibration_cells=dict(primary=len(prim), secondary=len(sec), by_split={s: sum(1 for v in dc['cells'].values() if v['split'] == s) for s in ('dev', 'dev7ho')}),
               precheck=dict(cells=len(fam), slot_only=slot, U=uu, gain=None if slot is None else uu - slot, passes=slot is not None and uu - slot >= .02),
               devchains_sha256=sha(ROOT / f'results/devchains_{bb}.json.gz'), seconds=time.time() - t0)
    dump(ROOT / f'results/calib_u_{bb}.json', out); print(bb, best, best2, out['precheck'], flush=True)


if __name__ == '__main__':
    main()
