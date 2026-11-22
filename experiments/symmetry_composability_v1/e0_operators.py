"""E0.2 group laws of existing operators (no training, no decoding). Exploratory."""
import time
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from symutil import *

DEV = 'cuda'


def operators():
    """name -> dict(domain, family, seed, kind, obj)."""
    ops = {}
    for g in ('C1', 'C3'):
        for s in (42, 43, 44):
            ops[f'time/{g}/s{s}'] = dict(domain='time', family=g, seed=s, kind='editor', path=COBJ / f'local/{g}_s{s}_0600.pt')
        for s in (45, 46):
            ops[f'time/{g}/s{s}'] = dict(domain='time', family=g, seed=s, kind='editor', path=CONF / f'local/time_{g}_s{s}_0600.pt')
    for lab in ('CE_all', 'floor', 'adv_pool_l0.01', 'adv_set_l0.01'):
        for s in SEEDS:
            ops[f'time/{lab}/s{s}'] = dict(domain='time', family=lab, seed=s, kind='editor', path=MAN / f'local/{lab}_s{s}.pt')
    ops['time/RRR16'] = dict(domain='time', family='RRR16', seed=None, kind='rrr', path=CWR / 'local/rrr.pt', key=lambda op: ('iid_only', op, 16))
    for r in (16, 64, 256, 768):
        ops[f'person/RRR{r}'] = dict(domain='person', family=f'RRR{r}', seed=None, kind='rrr', path=MAN / 'local/person_fits.pt', key=lambda op, r=r: (op, r))
    for g in ('C1', 'C3'):
        for s in SEEDS:
            ops[f'person/{g}/s{s}'] = dict(domain='person', family=g, seed=s, kind='editor', path=CONF / f'local/person_{g}_s{s}_0600.pt')
    return ops


def factors(spec):
    obj = load(spec['path'])
    out = {}
    for op in ('plus', 'minus'):
        if spec['kind'] == 'editor':
            out[op] = tuple(x.to(DEV) for x in editor_factors('editor', obj['editor'], op))
        else:
            out[op] = tuple(x.to(DEV) for x in editor_factors('rrr', obj[spec['key'](op)], op))
    return out


def apply(f, h, m):
    U, V, b = (x.float().to(DEV) for x in f)
    return h + ((h @ V.T) @ U.T + b) * m[..., None]


def caches(domain, S):
    return {s: load(CONF / f'local/{domain}_eval_t0_s{s}.pt') for s in S.states(domain)}


def pad(h, m, n):
    return torch.nn.functional.pad(h, (0, 0, 0, n - h.shape[1])), torch.nn.functional.pad(m, (0, n - m.shape[1]))


@torch.no_grad()
def inverse_errors(F, domain, S, C):
    """e_inv for T_inv o T_first on mask-aligned canonical pairs; per-world ratio sqrt(sum num^2 / sum den^2)."""
    out = {}
    for first, inv in (('plus', 'minus'), ('minus', 'plus')):
        W = len(C[S.states(domain)[0]]['h']); num = torch.zeros(W, dtype=torch.float64); den = torch.zeros(W, dtype=torch.float64); npair = torch.zeros(W)
        for x in S.states(domain):
            try:
                y = S.advance(domain, x, first)
            except ValueError:
                continue
            a, b = C[x], C[y]; n = max(a['h'].shape[1], b['h'].shape[1])
            h, m = pad(a['h'], a['m'], n); g, gm = pad(b['h'], b['m'], n)
            ok = (m == gm).all(1)
            if not ok.any():
                continue
            h, m, g = h[ok].to(DEV).float(), m[ok].to(DEV).float(), g[ok].to(DEV).float()
            z = apply(F[inv], apply(F[first], h, m), m)
            idx = ok.nonzero().squeeze(1)
            num[idx] += (((z - h) * m[..., None]) ** 2).sum((1, 2)).double().cpu()
            den[idx] += (((g - h) * m[..., None]) ** 2).sum((1, 2)).double().cpu(); npair[idx] += 1
        has = npair > 0
        ratio = (num[has] / den[has]).sqrt().numpy()
        out[f'{inv}_o_{first}'] = dict(world_mean=boot_mean(ratio), pooled=float((num[has].sum() / den[has].sum()).sqrt()),
                                      worlds=int(has.sum()), aligned_pairs=int(npair.sum()))
    out['mean_both'] = float(np.mean([out['minus_o_plus']['world_mean']['mean'], out['plus_o_minus']['world_mean']['mean']]))
    return out


def loop_growth(F, kmax=50):
    """L = A- A+ is the identity off span[U+, V+^T, U-, V-^T]; compute exactly in that subspace (CPU, float64)."""
    fs = [tuple(x.double().cpu() for x in F[o]) for o in ('plus', 'minus')]
    M = torch.cat([fs[0][0], fs[0][1].T, fs[1][0], fs[1][1].T], 1)
    q, s, _ = torch.linalg.svd(M, full_matrices=False); Q = q[:, s > s.max() * max(M.shape) * 1e-15]
    I = torch.eye(Q.shape[1], dtype=torch.float64)
    Ap = I + (Q.T @ fs[0][0]) @ (fs[0][1] @ Q); Am = I + (Q.T @ fs[1][0]) @ (fs[1][1] @ Q)
    L = Am @ Ap; P = I.clone(); g = []; d = []
    for _ in range(kmax):
        P = P @ L; g.append(max(1., float(torch.linalg.matrix_norm(P, 2)))); d.append(float(torch.linalg.matrix_norm(P - I, 2)))
    return dict(loop_power_norm=g, loop_power_minus_I_norm=d, loop_subspace_dim=int(Q.shape[1]))


def main():
    require_slurm(); verify_inputs(['editor/', 'canonical_write_reachability_v1/local/rrr.pt', 'manifold_controls_v1/local/person_fits.pt', 'cache/conf/', 'canonical_confirmation_v1/results/fresh_closure_summary.json'])
    t0 = time.time(); S, _ = semantics(); res = {}; Cs = {d: caches(d, S) for d in ('time', 'person')}
    for name, spec in operators().items():
        if not spec['path'].exists():
            res[name] = dict(status='NA', reason=f'missing {spec["path"].name}'); continue
        F = factors(spec); r = dict(domain=spec['domain'], family=spec['family'], seed=spec['seed'], status='ok')
        for op in ('plus', 'minus'):
            st, _, _ = operator_stats(*(x.cpu() for x in F[op])); r[op] = st
        r['ISO_mean'] = float(np.mean([r['plus']['ISO'], r['minus']['ISO']]))
        r['e_inv'] = inverse_errors(F, spec['domain'], S, Cs[spec['domain']])
        r.update(loop_growth(F))
        res[name] = r
        print(name, 'ISO', round(r['ISO_mean'], 4), 'e_inv', round(r['e_inv']['mean_both'], 4), flush=True)
    # Exploratory: C3 measured closure (fresh_closure_summary) vs loop growth, per seed (report correlation only).
    cl = read(CONF / 'results/fresh_closure_summary.json'); comp = []
    for row in cl:
        if row['group'] == 'C3' and row['template'] == 0 and row['step'] in (20, 50):
            k = f"time/C3/s{row['seed']}"
            if k in res and res[k].get('status') == 'ok':
                comp.append(dict(seed=row['seed'], path=row['path'], step=row['step'], closure_rate=row['trajectory']['rate'],
                                 loop_minus_I_at_step=res[k]['loop_power_minus_I_norm'][row['step'] - 1],
                                 e_inv=res[k]['e_inv']['mean_both'], ISO=res[k]['ISO_mean']))
    corr = {}
    for step in (20, 50):
        for path in sorted({c['path'] for c in comp}):
            xs = [c for c in comp if c['step'] == step and c['path'] == path]
            if len(xs) >= 3 and len({c['closure_rate'] for c in xs}) > 1:
                corr[f'{path}@{step}'] = {m: float(spearmanr([c[m] for c in xs], [c['closure_rate'] for c in xs])[0]) for m in ('loop_minus_I_at_step', 'e_inv', 'ISO')}
    res['_closure_comparison'] = dict(rows=comp, spearman=corr, note='Exploratory; n=5 seeds; no prediction.')
    res['_definitions'] = dict(e_inv='per-world sqrt(sum ||M(T_inv T_first E_x - E_x)||^2 / sum ||M(E_gx - E_x)||^2) over mask-aligned canonical pairs; world mean with bootstrap; mean_both averages the two compositions',
                               cache=dict(time='canonical_confirmation_v1 time_eval (160 confirm worlds, exposed)', person='canonical_confirmation_v1 person_eval'))
    res['_seconds'] = time.time() - t0
    dump('results/e0_operators.json', res)
    # figure: eigenvalues of A_Q (plus) in the complex plane + singular values
    fams = [('time', 'C1'), ('time', 'C3'), ('time', 'RRR16'), ('time', 'CE_all'), ('person', 'RRR16'), ('person', 'C3')]
    fig, axs = plt.subplots(2, len(fams), figsize=(3 * len(fams), 6))
    th = np.linspace(0, 2 * np.pi, 200)
    for j, (d, fam) in enumerate(fams):
        ks = [k for k, v in res.items() if not k.startswith('_') and v.get('status') == 'ok' and v['domain'] == d and v['family'] == fam]
        ax = axs[0, j]; ax.plot(np.cos(th), np.sin(th), color='#cccccc', lw=.8)
        for k in ks:
            mod = np.array(res[k]['plus']['eig_modulus']); ph = np.array(res[k]['plus']['eig_phase'])
            ax.plot(mod * np.cos(ph), mod * np.sin(ph), '.', ms=3, alpha=.6)
            axs[1, j].plot(sorted(res[k]['plus']['singular_values'], reverse=True), lw=.8)
        ax.set_title(f'{d} {fam} plus: eig(A_Q)', fontsize=8); ax.set_aspect('equal')
        axs[1, j].axhline(1, color='#999999', lw=.6); axs[1, j].set_title('singular values', fontsize=8)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/e0_spectra.png', dpi=140)


if __name__ == '__main__':
    main()
