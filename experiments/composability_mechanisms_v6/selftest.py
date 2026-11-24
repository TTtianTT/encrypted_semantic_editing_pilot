"""Synthetic self-test (CPU, before the lock; PLAN v7 appendix A.9). Every check has a known answer. Output: results/selftest.json.
1 manifold quantities on an ideal harmonic code: rank N-1, R analytic, rho = 0 on clean codes and = ||delta|| / R for a planted off-manifold
  delta, normalised margin m = 1 on clean codes (symmetric code), m <= 0 when the readout is wrong;
2 repairs: PROJ removes a planted off-manifold perturbation, PUSH removes a planted in-span perturbation, SNAP+CTX equals the clean
  encoding, CTX keeps the slot and restores the context;
3 U threshold calibration recovers planted thresholds (outcome = m >= 0.3 and rho <= 0.2 at every step), ties -> most permissive;
4 S-RRR inverse: P^-1(P(h)) = h (relative error < 1e-5);
5 first-order error ratios: linear error -> cycle-sum ratio 0; constant error -> 1; identical P / M errors -> alternating contrast 1;
6 Att2L ablation (c) equals the forward pass with only the token-wise term (z0 + (b + U V z0) * mask);
7 propositions 1-4: results/theory/t_theory.json T1 holds."""
import types
from lib7 import *
from calib_u import calibrate_u


def ideal_code(N, a, W, d, seed):
    g = np.random.default_rng(seed); Q, _ = np.linalg.qr(g.normal(size=(d, d))); P = []; j = 0; c = np.zeros((N, d)); x = np.arange(N)
    for k in range(1, N // 2 + 1):
        m = 1 if 2 * k == N else 2; B = Q[:, j:j + m]; j += m; th = 2 * np.pi * k * x / N
        c += a[k - 1] * (np.stack([np.cos(th), np.sin(th)], 1)[:, :m] if m == 2 else np.cos(th)[:, None]) @ B.T; P.append((k, torch.tensor(B)))
    off = torch.tensor(Q[:, j:]); mu = torch.tensor(g.normal(size=(W, 1)) * 0 + g.normal(size=(W, d - j)) @ Q[:, j:].T)
    return torch.tensor(c)[None] + mu[:, None], P, off


def main():
    require_slurm(); torch.manual_seed(0); out = {}; N, W, d = 12, 5, 40; a = np.linspace(1.5, .6, N // 2)
    Cw, P, off = ideal_code(N, a, W, d, 1); man = manifold(None, None, None, Cw=Cw)
    Rth = float(np.sqrt(sum(a[k - 1] ** 2 * (1 if 2 * k != N else 1) for k in range(1, N // 2 + 1))))   # ||c(x) - mu||: 2-D planes a^2, Nyquist a^2 cos^2 = a^2
    lam = torch.rand(N // 2, dtype=torch.float64) + .5; Mw = margin_scale(man, P, lam)
    rho_clean = max(float(rho_of(man, Cw[:, y]).abs().max()) for y in range(N))
    delta = (off @ torch.randn(off.shape[1], dtype=torch.float64))[None].expand(W, -1) * .3
    rho_pl = rho_of(man, Cw[:, 3] + delta); rho_true = delta.norm(dim=-1) / Rth
    m_clean = torch.stack([margin_raw(Cw[:, y], Cw, P, lam)[1] / Mw for y in range(N)])
    wrong = Cw[:, 4] + .0; am, mr = margin_raw(wrong, Cw, P, lam)
    out['A9_1'] = dict(rank=man['rank'].tolist(), R_err=float((man['R'] - Rth).abs().max()), rho_clean=rho_clean, rho_planted_err=float((rho_pl - rho_true).abs().max()),
                       m_clean_err=float((m_clean - 1).abs().max()))
    out['A9_1']['pass'] = all(r == N - 1 for r in out['A9_1']['rank']) and out['A9_1']['R_err'] < 1e-6 and rho_clean < 1e-6 and out['A9_1']['rho_planted_err'] < 1e-6 and out['A9_1']['m_clean_err'] < 1e-6
    # 2 repairs
    g = torch.full((W,), 5, dtype=torch.long); Eg = Cw[:, 5]
    inspan = proj_in(man, Cw[:, 7]) * .4
    r_proj = repair_slot('PROJ', Eg + delta, man, g); r_push = repair_slot('PUSH', Eg + inspan, man, g); r_snap = repair_slot('SNAP', Eg + delta + inspan, man, g)
    L = 6; pos = torch.full((W,), 2); hfull = torch.randn(W, L, d, dtype=torch.float64); m = torch.ones(W, L, dtype=torch.bool); m[:, -1] = False
    hg = torch.randn(W, L, d, dtype=torch.float64); hg[torch.arange(W), pos] = Eg; hfull[:, -1] = 0; hg[:, -1] = 0
    sc, _ = repair('SNAP+CTX', hfull, m, pos, man, g, (hg, m)); cx, _ = repair('CTX', hfull, m, pos, man, g, (hg, m))
    keep = torch.ones(L, dtype=torch.bool); keep[2] = False
    out['A9_2'] = dict(proj_err=float((r_proj - Eg).abs().max()), push_err=float((r_push - Eg).abs().max()), snap_err=float((r_snap - Eg).abs().max()),
                       snapctx_err=float((sc - hg).abs().max()), ctx_slot_err=float((cx[torch.arange(W), pos] - hfull[torch.arange(W), pos]).abs().max()),
                       ctx_context_err=float((cx[:, keep] - hg[:, keep]).abs().max()))
    out['A9_2']['pass'] = all(v < 1e-9 for k, v in out['A9_2'].items())
    # 3 calibration
    rng = np.random.default_rng(3); cells = []
    for c in range(20):
        n, T = 40, 1; sim = dict(world_ids=list(range(n)), states=[[0] * T for _ in range(n)], argmax=[[0] * T for _ in range(n)],
                                 m=rng.uniform(-.1, 1, (n, T)).round(3).tolist(), rho=rng.uniform(0, .6, (n, T)).round(3).tolist())
        obs = [all(sim['m'][i][t] >= .3 and sim['rho'][i][t] <= .2 for t in range(T)) for i in range(n)]; cells.append((sim, obs))
    best, table = calibrate_u(cells)
    out['A9_3'] = dict(recovered=best, planted=[.3, .2], pass_=best['tau_m'] == .3 and best['tau_r'] == .2 and best['agreement'] == 1.0)
    # 4 inverse
    dim, r = 30, 6; op = types.SimpleNamespace(left=torch.randn(dim, r) * .2, right=torch.randn(r, dim) * .2, bias=torch.randn(dim) * .1, pos=torch.zeros(3, dtype=torch.long))
    inv = SlotRRRinv(op); hs = torch.randn(10, dim, dtype=torch.float64); back = inv.slot(slot_map(op, hs))
    out['A9_4'] = dict(rel_err=float((back - hs).norm() / hs.norm()), cond=inv.cond); out['A9_4']['pass'] = out['A9_4']['rel_err'] < 1e-5
    # 5 first-order error ratios on one world of the ideal code
    m1 = manifold(None, None, None, Cw=Cw[:1]); mu = m1['mu'][0]; C = Cw[0] - mu
    Rot = torch.linalg.lstsq(C, torch.roll(C, -1, 0)).solution; Rinv = torch.linalg.lstsq(C, torch.roll(C, 1, 0)).solution
    Pi = m1['B'][0] @ m1['B'][0].T; Eo = torch.randn(d, off.shape[1], dtype=torch.float64) @ off.T * .05; dc = off @ torch.randn(off.shape[1], dtype=torch.float64) * .05
    def mk(Mlin, bias): return types.SimpleNamespace(left=Mlin - torch.eye(d, dtype=torch.float64), right=torch.eye(d, dtype=torch.float64), bias=bias)
    lin_P = mk(Rot + Pi @ Eo, mu @ (torch.eye(d, dtype=torch.float64) - Rot) - mu @ Pi @ Eo); lin_M = mk(Rinv, mu @ (torch.eye(d, dtype=torch.float64) - Rinv))
    cst_P = mk(Rot, mu @ (torch.eye(d, dtype=torch.float64) - Rot) + dc); cst_M = mk(Rinv, mu @ (torch.eye(d, dtype=torch.float64) - Rinv) + dc)
    e_lin = first_order_errors(m1, lin_P, lin_M, None); e_cst = first_order_errors(m1, cst_P, cst_M, None)
    out['A9_5'] = dict(linear_cycle=float(e_lin['cycle_sum_ratio'][0]), constant_cycle=float(e_cst['cycle_sum_ratio'][0]), identical_alt_contrast=float(e_cst['alt_contrast'][0]))
    out['A9_5']['pass'] = out['A9_5']['linear_cycle'] < 1e-6 and abs(out['A9_5']['constant_cycle'] - 1) < 1e-6 and abs(out['A9_5']['identical_alt_contrast'] - 1) < 1e-6
    # 6 ablation (c)
    torch.manual_seed(1); e = Att2LEditor(24)                         # float32, as the editor computes in float32
    for p_ in e.parameters(): nn.init.normal_(p_, std=.1)
    h = torch.randn(4, 7, 24); mk_ = torch.ones(4, 7); mk_[:, -2:] = 0
    with torch.no_grad():
        abl = Att2LAblated(e, 'drop')(h, mk_); ref = h + (e.b + e.u(e.v(h))) * mk_[..., None]
        full = e(h, mk_); unif = Att2LAblated(e, 'uniform')(h, mk_); selfa = Att2LAblated(e, 'self')(h, mk_)
    out['A9_6'] = dict(drop_err=float((abl - ref).abs().max()), drop_differs_from_full=float((abl - full).abs().max()), uniform_finite=bool(torch.isfinite(unif).all()),
                       self_finite=bool(torch.isfinite(selfa).all()))
    out['A9_6']['pass'] = out['A9_6']['drop_err'] < 1e-6 and out['A9_6']['drop_differs_from_full'] > 1e-6 and out['A9_6']['uniform_finite'] and out['A9_6']['self_finite']
    # 7 propositions
    th = read(ROOT / 'results/theory/t_theory.json')['T1_holds']
    out['A9_7'] = dict(T1=th, pass_=th['prop1'] and th['prop3'] and th['prop4'] and th['prop2_per_dim'] == th['prop2_ranks'])
    out['pass'] = all(v.get('pass', v.get('pass_')) for k, v in out.items() if k.startswith('A9'))
    dump(ROOT / 'results/selftest.json', out); print(json.dumps({k: v.get('pass', v.get('pass_')) for k, v in out.items() if k.startswith('A9')}), out['pass'], flush=True)
    assert out['pass'], 'self-test failed'


if __name__ == '__main__':
    main()
