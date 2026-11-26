"""L-unit analysis core (PLAN 6, appendix A.1/A.2), shared by p_posthoc.py (P1, on v4 shards) and analyze.py (confirm5).
No torch; operates on chain records. A record needs: world_id, step, state, success, trajectory_success, decoded_state and a latent
readout field (default 'argmax_full': the locked fitted vote model's argmax on the actual latent slot at that step)."""
from collections import defaultdict
import numpy as np


def category(r):
    return 'composable' if r >= .90 else 'fail' if r <= .20 else 'partial'


def world_table(recs, n_steps, latent='argmax_full'):
    """Per world of one cell (operator x path), over steps 1..n_steps:
    pred  = latent readout equals the gold state at every step (A.1.3);
    obs   = decoded trajectory success at step n_steps;
    naive = decoded success at step 1 (PLAN 6.3);
    D1    = step-1 latent readout != decoded state, among worlds whose step-1 decode is parsable (A.2), else None."""
    by = defaultdict(dict)
    for r in recs:
        if r['step'] <= n_steps: by[r['world_id']][r['step']] = r
    out = {}
    for w, st in by.items():
        assert sorted(st) == list(range(1, n_steps + 1)), (w, sorted(st)[:3], n_steps)
        r1 = st[1]
        out[w] = dict(pred=all(st[t][latent] == st[t]['state'] for t in st), obs=bool(st[n_steps]['trajectory_success']),
                      naive=bool(r1['success']), D1=None if r1['decoded_state'] is None else bool(r1[latent] != r1['decoded_state']))
    return out


def cell_summary(tab):
    v = list(tab.values()); n = len(v)
    pr = float(np.mean([x['pred'] for x in v])); ob = float(np.mean([x['obs'] for x in v]))
    d1 = [x['D1'] for x in v if x['D1'] is not None]
    return dict(n=n, pred_rate=pr, obs_rate=ob, pred_cat=category(pr), obs_cat=category(ob), cat_match=category(pr) == category(ob),
                naive_rate=float(np.mean([x['naive'] for x in v])), world_agree=float(np.mean([x['pred'] == x['obs'] for x in v])),
                D=float(np.mean(d1)) if d1 else None, D_n=len(d1))


def pooled(cells, boot=None):
    """cells: {cell: world_table}. Per-world agreement pooled over cells (latent, naive, cell-majority reference);
    boot: optional callable(world_ids, a, b) -> CI dict for latent - naive (A.5 world cluster bootstrap)."""
    wid, lat, nai, maj = [], [], [], []
    for c, tab in cells.items():
        m = float(np.mean([x['obs'] for x in tab.values()])) >= .5
        for w, x in tab.items():
            wid.append(w); lat.append(x['pred'] == x['obs']); nai.append(x['naive'] == x['obs']); maj.append(m == x['obs'])
    out = dict(records=len(wid), latent=float(np.mean(lat)), naive=float(np.mean(nai)), majority_reference=float(np.mean(maj)))
    if boot is not None and wid: out['latent_minus_naive'] = boot(wid, np.array(lat, float), np.array(nai, float))
    return out


# ---------------------------------------------------------------- A.5 world cluster bootstrap (v4 lib4.cluster_boot, numpy only)
def cluster_boot(world_ids, values, reps=2000, seed=3101):
    """Resample worlds with replacement; values (n_records, k); returns column means and per-replicate pooled means (reps, k)."""
    values = np.asarray(values, float); ids = sorted(set(world_ids)); ix = {w: i for i, w in enumerate(ids)}
    g = np.array([ix[w] for w in world_ids]); W = len(ids)
    sums = np.zeros((W, values.shape[1])); cnt = np.bincount(g, minlength=W).astype(float)
    np.add.at(sums, g, values)
    draw = np.random.default_rng(seed).integers(W, size=(reps, W))
    counts = np.stack([np.bincount(r, minlength=W) for r in draw]).astype(float)
    return values.mean(0), (counts @ sums) / (counts @ cnt)[:, None]


def boot_diff_ci(world_ids, a, b, **kw):
    est, rm = cluster_boot(world_ids, np.stack([a, b], 1), **kw); d = rm[:, 0] - rm[:, 1]
    return dict(diff=float(est[0] - est[1]), ci95=np.quantile(d, [.025, .975]).tolist(), a=float(est[0]), b=float(est[1]))
