"""P9 (CPU, exploratory, before the lock; PLAN v9 section 2). --part a|b|c|d. Results feed the paper directly (exploratory).
a (M3) write geometry of the one-step CE editors - v5's BART C1 (v1 editors, weekday / month), T5Gemma 2B-2B C1 (v3 editors), v8 C1_nat
  (both backbones): on dev worlds, the plus write w = E'(x)_slot - E(x)_slot. Reported: median ||w|| / ||c|| (c = canonical write
  E(x+1) - E(x) at the slot); constant share per world ||mean_x w||^2 / mean_x ||w||^2 (1 = the same write for every source state);
  median cos(w, c) against a null of random Gaussian directions (median and 95% interval of cos(g, c)) and against the matched control
  (the same editor applied to the other domain's encodings; weekday <-> month, month-nat <-> month template 0); state probe - multinomial
  logistic regression on clean slot codes of train worlds, C chosen on dev clean codes, applied to the step-1 edited slots of dev worlds:
  share read as source, target, other.
b (M4) cyclic structure - per harmonic plane (from train slot codes) and world: ellipticity (smaller / larger singular value of the N
  centred 2-D coordinates), mean absolute deviation of the successive angle steps from +-2 pi k / N, share of the centred code energy; for
  the natural order and for the v2 scrambled map sigma_max ('scrmax'; planes recomputed in its cycle order). BART and T5Gemma 2B-2B weekday
  / month template 0, month-nat (both), T5Gemma 9B-9B month.
c (M5) predictor - v5 L (state-supervised cells of the fifth round; locked simulations and shards), v8 N5 and G5: per-world agreement of
  the slot readout, the per-cell majority reference and the paired world-cluster bootstrap CI of their difference; per-cell agreement
  (mean over cells) with a cell bootstrap CI; the rule 'step-1 readout correct'; a learned baseline (logistic regression, 5-fold
  cross-validation grouped by world) on the latent features stored by the locked v8 simulations (step-1 margin m and off-manifold rho, and
  their worst value along the chain). Distance and norm features of the plan need the latent of every v5 / v8 cell, which the locked
  simulations do not store; they were not recomputed (recorded).
d (M6) all CE cells (v5 L CE cells, v8 C1_nat and 9B C1): share of worlds whose step-1 slot readout equals the start state.
Output: results/p9<part>.json."""
import glob
import gzip
from collections import defaultdict
import numpy as np
from lib9 import *
import lcore

V5D = EXP / 'composability_mechanisms_v4'


def editor_cpu(path, dim):
    source_path(); from backend import Editor
    c = load(path); ed = nn.ModuleDict({op: Editor(dim) for op in ('plus', 'minus')}); ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)


def c1_editors():
    out = []
    for s in SEEDS:
        for d in ('weekday', 'month'):
            out.append(('bart', d, f'C1v1_s{s}', V1 / f'local/e1_C1_{d}_s{s}_0600.pt')); out.append(('t5', d, f'C1v3_s{s}', V3DIR / f'local/t5_C1_{d}_s{s}.pt'))
    for bb in ('bart', 't5'):
        for s in (50, 51, 52): out.append((bb, S.NAT, f'C1nat_s{s}', V8DIR / f'local/n8_{bb}_C1_{S.NAT}_s{s}_u600.pt'))
    return out


@torch.no_grad()
def writes(ed, bb, d, split='dev'):
    pos = slots(bb, d, split); ar = torch.arange(len(pos)); W, Cn, E1 = [], [], []
    X = slot_matrix(bb, d, split); nxt = next_idx(d, 'plus')
    for s in S.states(d):
        c = cache5(bb, d, split, s); h = c['h'].float(); out = ed['plus'](h, c['m'])
        W.append((out[ar, pos] - h[ar, pos]).double()); E1.append(out[ar, pos].double())
    W = torch.stack(W, 1); E1 = torch.stack(E1, 1); Cn = X[:, nxt] - X
    return W, Cn, E1, X


def cos(a, b): return (a * b).sum(-1) / (a.norm(dim=-1) * b.norm(dim=-1)).clamp_min(1e-12)


def probe_fit(bb, d):
    Xtr = slot_matrix(bb, d, 'train'); Xdv = slot_matrix(bb, d, 'dev'); N = Xtr.shape[1]; mu, sd = Xtr.reshape(-1, Xtr.shape[-1]).mean(0), Xtr.reshape(-1, Xtr.shape[-1]).std(0) + 1e-6
    Z = lambda X: (X - mu) / sd; ytr = torch.arange(N).repeat(Xtr.shape[0]); ydv = torch.arange(N).repeat(Xdv.shape[0]); best = None
    for C in (0.01, 0.1, 1.0, 10.0):
        Wt, b = logreg(Z(Xtr.reshape(-1, Xtr.shape[-1])), ytr, C, N); acc = float(((Z(Xdv.reshape(-1, Xdv.shape[-1])) @ Wt + b).argmax(-1) == ydv).double().mean())
        if best is None or acc > best[0]: best = (acc, C, Wt, b)
    acc, C, Wt, b = best; return dict(C=C, dev_clean_acc=acc, f=lambda X: (Z(X) @ Wt + b).argmax(-1))


def part_a():
    out = {}; g = torch.Generator().manual_seed(BOOT_SEED); probes = {}
    other = {'weekday': 'month', 'month': 'weekday', S.NAT: 'month'}
    for bb, d, name, path in c1_editors():
        dim = cache5(bb, d, 'dev', 0)['h'].shape[-1]; ed = editor_cpu(path, dim); W, Cn, E1, X = writes(ed, bb, d)
        n = W.norm(dim=-1); cw = Cn.norm(dim=-1); mw = W.mean(1, keepdim=True)
        const = (mw.squeeze(1).square().sum(-1) / W.square().sum(-1).mean(1)).median()
        cs = cos(W, Cn).flatten(); G = torch.randn(4000, dim, generator=g, dtype=torch.float64); Cs = Cn.reshape(-1, dim)[torch.randint(len(Cn.reshape(-1, dim)), (4000,), generator=g)]
        nul = cos(G, Cs)
        Wo, Co, _, _ = writes(ed, bb, other[d])
        if (bb, d) not in probes: probes[bb, d] = probe_fit(bb, d)
        pr = probes[bb, d]; N = X.shape[1]; pred = pr['f'](E1.reshape(-1, dim)).reshape(E1.shape[0], N); src = torch.arange(N)[None].expand_as(pred); tgt = torch.tensor(next_idx(d, 'plus'))[None].expand_as(pred)
        out[f'{bb}/{d}/{name}'] = dict(norm_ratio_median=float((n / cw).median()), constant_share_median=float(const), cos_canonical_median=float(cs.median()),
                                      cos_canonical_abs_median=float(cs.abs().median()), null_cos_median=float(nul.median()), null_cos_abs_median=float(nul.abs().median()),
                                      null_cos_q95=[float(nul.quantile(.025)), float(nul.quantile(.975))],
                                      matched_control=dict(domain=other[d], cos_canonical_median=float(cos(Wo, Co).flatten().median())),
                                      probe=dict(C=pr['C'], dev_clean_accuracy=pr['dev_clean_acc'], source=float((pred == src).double().mean()), target=float((pred == tgt).double().mean()),
                                                 other=float(((pred != src) & (pred != tgt)).double().mean())))
        print('P9a', bb, d, name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[f'{bb}/{d}/{name}'].items() if k != 'probe'}, out[f'{bb}/{d}/{name}']['probe'], flush=True)
    return out


def plane_stats(X, P, order):
    """X (W, N, dim) in natural state order; order: states along the plus cycle of the map; P: planes in that order."""
    Xo = X[:, order]; C = Xo - Xo.mean(1, keepdim=True); N = X.shape[1]; tot = C.square().sum((1, 2)); out = {}
    for k, B in P:
        Z = C @ B.double(); share = (Z.square().sum((1, 2)) / tot)
        if B.shape[1] == 2:
            sv = torch.linalg.svdvals(Z); ell = sv[:, 1] / sv[:, 0]
            th = torch.atan2(Z[..., 1], Z[..., 0]); dth = torch.remainder(th.roll(-1, 1) - th + np.pi, 2 * np.pi) - np.pi
            dev = torch.stack([(torch.remainder(dth - sgn * 2 * np.pi * k / N + np.pi, 2 * np.pi) - np.pi).abs().mean(1) for sgn in (1, -1)], 1).min(1).values
            out[k] = dict(dim=2, ellipticity_median=float(ell.median()), angle_dev_median_rad=float(dev.median()), energy_share_median=float(share.median()))
        else: out[k] = dict(dim=1, energy_share_median=float(share.median()))
    return out


def part_b():
    out = {}
    for bb, d in [(b, dd) for b in ('bart', 't5') for dd in ('weekday', 'month', S.NAT)] + [('t5_9b', 'month')]:
        X = slot_matrix(bb, d, 'train'); r = {}
        for mp in ('natural', 'scrmax'):
            if mp == 'scrmax' and d == S.NAT: dd = 'month'
            else: dd = d
            try: order = cycle_order(dd, mp)
            except Exception as e: r[mp] = dict(error=type(e).__name__); continue
            P = gram_planes(cbar_of(X)[order]); r[mp] = plane_stats(X, P, order)
        out[f'{bb}/{d}'] = r; print('P9b', bb, d, {mp: {k: {kk: round(vv, 3) for kk, vv in v.items() if isinstance(vv, float)} for k, v in x.items()} for mp, x in r.items() if 'error' not in x}, flush=True)
    return out


def shards_v5(bb, d, method, path):
    rs = []
    for f in sorted(glob.glob(str(V5D / f'results/shards/chain_{bb}_{d}_natural_{method}_{path}_*.jsonl'))): rs += rows(f)
    return rs


def tables_v5(family='state', new=False):
    p = read(V5D / 'protocol.json'); tabs = defaultdict(dict); fams = {}
    for bb in ('bart', 't5'):
        with gzip.open(V5D / f'results/simulate_{bb}.json.gz', 'rt') as g: sims = json.load(g)
        for key, c in p['simulate'][bb]['cells'].items():
            if c['unit'] != 'L' or (family and c['family'] != family) or c['new'] != new: continue
            rs = shards_v5(bb, c['domain'], c['method'], c['path'] + '_from_start'); sim = sims.get(f"L/{bb}/{c['domain']}/{c['method']}/{c['path']}")
            if not rs or sim is None: continue
            idx = {w: i for i, w in enumerate(sim['world_ids'])}; q = []
            for r in rs:
                i = idx[r['world_id']]; t = r['step'] - 1
                if t < len(sim['states'][i]): q.append(dict(r, argmax_locked=sim['argmax']['full'][i][t], start_state=sim['start'][i] if 'start' in sim else r['start']))
            n = min(2 * c['N'], max(r['step'] for r in q)); tabs[bb][key] = lcore.world_table(q, n, latent='argmax_locked'); fams[bb, key] = c['family']
            for w, x in tabs[bb][key].items():
                r1 = next(r for r in q if r['world_id'] == w and r['step'] == 1); x['step1_readout_correct'] = r1['argmax_locked'] == r1['state']; x['step1_readout_start'] = r1['argmax_locked'] == r1['start']
    return tabs, fams


def tables_v8(unit, bb):
    sims = json.load(gzip.open(V8DIR / f'results/simulate8_{unit}_{bb}.json.gz', 'rt')); meta = read(V8DIR / f'results/simulate8_{unit}_{bb}_summary.json')['cells']; tabs = {}
    for key, sim in sims.items():
        if meta[key]['family'] == 'ref': continue
        dm, name, path = key.split('/'); rs = []
        for f in sorted(glob.glob(str(V8DIR / f'results/shards/chain_{bb}_{dm}_natural_{name}_{path}_from_start_*.jsonl'))): rs += rows(f)
        if not rs: continue
        by = defaultdict(dict)
        for r in rs: by[r['world_id']][r['step']] = r
        ix = {w: i for i, w in enumerate(sim['world_ids'])}; n = len(sim['states'][0]); tab = {}
        for w, st in by.items():
            i = ix[w]; r1 = st[1]
            tab[w] = dict(pred=bool(sim['pred']['slot'][i]), obs=bool(st[n]['trajectory_success']), naive=bool(r1['success']),
                          step1_readout_correct=sim['argmax'][i][0] == sim['states'][i][0], step1_readout_start=sim['argmax'][i][0] == sim['start'][i],
                          feats=[sim['m'][i][0], sim['rho'][i][0], min(sim['m'][i]), max(sim['rho'][i])])
        tabs[key] = (meta[key]['family'], f'{dm}/', tab)
    return tabs


def cell_boot(vals_a, vals_b, reps=2000, seed=BOOT_SEED):
    a, b = np.array(vals_a), np.array(vals_b); r = np.random.default_rng(seed).integers(len(a), size=(reps, len(a))); d = a[r].mean(1) - b[r].mean(1)
    return dict(diff=float(a.mean() - b.mean()), ci95=np.quantile(d, [.025, .975]).tolist())


def summarise(cells):
    """cells: {key: {world: dict(pred, obs, naive, step1_readout_correct, [feats])}} -> agreement table, CIs, learned baseline."""
    wid, lat, maj, nai, s1 = [], [], [], [], []; cl, cm = [], []; Xf, yf, gf = [], [], []
    for k, tab in cells.items():
        m = float(np.mean([x['obs'] for x in tab.values()])) >= .5; ca, cmj = [], []
        for w, x in tab.items():
            wid.append(f'{k.split("/")[0]}|{w}'); lat.append(x['pred'] == x['obs']); maj.append(m == x['obs']); nai.append(x['naive'] == x['obs'])
            s1.append(x['step1_readout_correct'] == x['obs']); ca.append(lat[-1]); cmj.append(maj[-1])
            if 'feats' in x: Xf.append(x['feats']); yf.append(x['obs']); gf.append(w)
        cl.append(np.mean(ca)); cm.append(np.mean(cmj))
    f = lambda v: np.array(v, float)
    out = dict(records=len(wid), cells=len(cells), per_world=dict(latent=float(np.mean(lat)), majority=float(np.mean(maj)), naive=float(np.mean(nai)), step1_rule=float(np.mean(s1)),
                                                            latent_minus_majority=lcore.boot_diff_ci(wid, f(lat), f(maj)), step1_rule_minus_majority=lcore.boot_diff_ci(wid, f(s1), f(maj))),
               per_cell=dict(latent=float(np.mean(cl)), majority=float(np.mean(cm)), latent_minus_majority=cell_boot(cl, cm)))
    if Xf:
        X = torch.tensor(Xf, dtype=torch.float64); y = torch.tensor(yf).long(); groups = sorted(set(gf)); rng = np.random.default_rng(BOOT_SEED); perm = rng.permutation(len(groups))
        fold = {groups[j]: int(i % 5) for i, j in enumerate(perm)}; fid = np.array([fold[g] for g in gf]); pred = np.zeros(len(y), bool)
        for k in range(5):
            tr, te = fid != k, fid == k; mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9; Wt, b = logreg((X[tr] - mu) / sd, y[tr], 1.0, 2)
            pred[te] = (((X[te] - mu) / sd) @ Wt + b).argmax(-1).numpy() == 1
        out['learned_baseline'] = dict(features=['m_step1', 'rho_step1', 'm_min', 'rho_max'], accuracy=float((pred == y.numpy().astype(bool)).mean()), n=len(y))
    return out


def part_c():
    out = {}
    tabs, _ = tables_v5('state', False)
    for bb in ('bart', 't5'): out[f'v5_L/{bb}'] = summarise(tabs[bb]); print('P9c v5', bb, out[f'v5_L/{bb}']['per_world'], flush=True)
    for unit, bbs in (('N', ('bart', 't5')), ('G', ('t5_9b',))):
        for bb in bbs:
            t = tables_v8(unit, bb); out[f'v8_{unit}/{bb}'] = summarise({k: tab for k, (fam, _, tab) in t.items()})
            print('P9c v8', unit, bb, out[f'v8_{unit}/{bb}']['per_world'], out[f'v8_{unit}/{bb}'].get('learned_baseline'), flush=True)
    out['not_computed'] = 'distance and norm features: the locked simulations store readout, margin and rho only; v5 has no stored m / rho, so the learned baseline is fitted on v8 cells only'
    return out


def part_d():
    out = {}
    tabs, fams = tables_v5('CE', False)
    for bb in ('bart', 't5'):
        v = {k: float(np.mean([x['step1_readout_start'] for x in t.values()])) for k, t in tabs[bb].items()}
        out[f'v5_L_CE/{bb}'] = dict(cells=len(v), per_cell=v, min=min(v.values()) if v else None, median=float(np.median(list(v.values()))) if v else None)
    for unit, bbs in (('N', ('bart', 't5')), ('G', ('t5_9b',))):
        for bb in bbs:
            t = tables_v8(unit, bb); v = {k: float(np.mean([x['step1_readout_start'] for x in tab.values()])) for k, (fam, _, tab) in t.items() if fam == 'CE'}
            out[f'v8_{unit}_CE/{bb}'] = dict(cells=len(v), per_cell=v, min=min(v.values()) if v else None, median=float(np.median(list(v.values()))) if v else None)
    for k, v in out.items(): print('P9d', k, v['cells'], v['min'], v['median'], flush=True)
    return out


def main():
    require_slurm(); part = sys.argv[sys.argv.index('--part') + 1]; t0 = time.time() if 'time' in globals() else None
    res = dict(a=part_a, b=part_b, c=part_c, d=part_d)[part](); dump(ROOT / f'results/p9{part}.json', res)


if __name__ == '__main__':
    import time
    main()
