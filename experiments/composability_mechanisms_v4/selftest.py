"""A.7 synthetic self-test (CPU; must pass before the lock).
1. Decoupled freeze: on a synthetic operator with known cross-plane coupling, the standard freeze leaks into the other planes; the
   decoupled freeze makes the other planes equal to the oracle (operator applied with plane S correct), error < 1e-6.
2. Latent predictor: on a synthetic chain whose readout is known (a simulated decoder = nearest canonical state in the planes), the
   predictor (simulate_chain + vote model) agrees with the simulated decoder at every step (agreement 1.0).
3. Template parsing: every multi-template gold text parses to its state; the distractor is never taken for the slot.
4. Att2-U on v4's synthetic pointer-copy task: held-out relative L2 <= 0.05; Tok-U >= 0.5 (unrolled L2 with S = 1 = v4 training).
5. Unrolled L2: with S = 1 the loss equals the single-step relative L2 exactly.
6. D and bootstrap: lcore.world_table / cell_summary / pooled and the cluster bootstrap on hand-built inputs."""
import importlib.util
import time
import lib5 as L
from lib5 import *
import lcore

_v4 = importlib.util.spec_from_file_location('v4selftest', V4DIR / 'selftest.py')


def pointer_data(n, seed):
    import sys as _s; _s.path.insert(0, str(V4DIR)); mod = importlib.util.module_from_spec(_v4); _v4.loader.exec_module(mod); _s.path.pop(0)
    return mod.pointer_data(n, seed)


def t_decoupled(seed=0, steps=3):
    """Operator A rotates plane 1 by 2pi/N and plane 2 by 4pi/N and couples plane 1 into plane 2. Freeze plane 1 (S = {1}).
    Oracle: at each step the input's plane 1 is replaced by the correct canonical value, A is applied, and plane 2 is read.
    The standard freeze F_{1} deviates from the oracle on plane 2 from step 2 on (coupling of the stale plane 1); D_{1} matches it."""
    g = torch.Generator().manual_seed(seed); dim, N, W = 24, 6, 5
    E, _ = torch.linalg.qr(torch.randn(dim, dim, generator=g, dtype=torch.float64)); B1, B2 = E[:, :2], E[:, 2:4]
    th = 2 * np.pi / N; Rk = lambda k: torch.tensor([[np.cos(k * th), -np.sin(k * th)], [np.sin(k * th), np.cos(k * th)]], dtype=torch.float64)
    A = B1 @ Rk(1) @ B1.T + B2 @ Rk(2) @ B2.T + (torch.eye(dim, dtype=torch.float64) - B1 @ B1.T - B2 @ B2.T)
    A = A + 0.3 * B2 @ torch.randn(2, 2, generator=g, dtype=torch.float64) @ B1.T                     # float64 throughout
    class Op:
        def __call__(self, h, m): return h @ A.T.to(h.device, h.dtype)
    e1 = torch.tensor([1., 0.], dtype=torch.float64)
    Cw = torch.stack([torch.stack([B1 @ (Rk(s) @ e1) + B2 @ (Rk(2 * s) @ (.6 * e1)) + 0.1 * torch.randn(dim, generator=g, dtype=torch.float64) @ (E[:, 4:] @ E[:, 4:].T)
                                   for s in range(N)]) for _ in range(W)])
    pos = torch.zeros(W, dtype=torch.long); m = torch.ones(W, 1, device=DEV, dtype=torch.float64); Bs = B1
    Fz = L.Freeze(Op(), Bs.to(DEV), pos); Dz = L.DecoupledFreeze(Op(), Bs, pos, Cw)
    hs = hd = Cw[:, 0][:, None, :].clone().to(DEV); o = Cw[:, 0].clone(); st = 0; leak, err, frozen = [], [], []
    P1 = B1 @ B1.T
    for t in range(steps):
        prev = torch.full((W,), st, dtype=torch.long, device=DEV)
        hs = Fz(hs, m); hd = Dz(hd, m, prev)
        o_in = o - o @ P1 + Cw[:, st] @ P1; o2 = o_in @ A.T; o = o2 - o2 @ P1 + Cw[:, 0] @ P1; st = (st + 1) % N
        p2 = lambda x: x @ B2
        leak.append(float((p2(hs[:, 0].cpu()) - p2(o2)).abs().max())); err.append(float((p2(hd[:, 0].cpu()) - p2(o2)).abs().max()))
        frozen.append(float(((hd[:, 0].cpu() - Cw[:, 0]) @ Bs).abs().max()))
    ok = max(leak[1:]) > 1e-3 and max(err) < 1e-6 and max(frozen) < 1e-6
    return dict(standard_leak_by_step=leak, decoupled_err_by_step=err, frozen_plane_err=frozen, pass_=bool(ok))


def t_predictor(seed=1):
    """Synthetic chain: canonical slots of N states in two planes, a rotation operator with a small error; the simulated decoder
    reads the nearest canonical state in the planes (= vote argmax with equal weights); the predictor must agree at every step."""
    g = torch.Generator().manual_seed(seed); dim, N, W, K = 16, 7, 9, 14
    E, _ = torch.linalg.qr(torch.randn(dim, dim, generator=g, dtype=torch.float64)); P = [(1, E[:, :2]), (2, E[:, 2:4])]
    th = 2 * np.pi / N; Rk = lambda a: torch.tensor([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], dtype=torch.float64)
    Cw = torch.stack([torch.stack([E[:, :2] @ (Rk(s * th) @ torch.tensor([1., 0.], dtype=torch.float64)) + E[:, 2:4] @ (Rk(2 * s * th) @ torch.tensor([.5, 0.], dtype=torch.float64))
                                   for s in range(N)]) for _ in range(W)])
    A = E[:, :2] @ Rk(th * 1.03) @ E[:, :2].T + E[:, 2:4] @ Rk(2 * th * 1.05) @ E[:, 2:4].T + torch.eye(dim, dtype=torch.float64) - E[:, :4] @ E[:, :4].T
    lam = torch.tensor([1., 1.], dtype=torch.float64); h = Cw[:, 0].clone(); agree = []
    for t in range(K):
        h = h @ A.T; Dm = L.plane_dists(h, Cw, P); pred = L.vote_scores(Dm, lam).argmax(-1)
        dec_ = ((h[:, None, :] - Cw) @ E[:, :4]).square().sum(-1).argmin(-1); agree.append(float((pred == dec_).double().mean()))
    return dict(agreement=float(np.mean(agree)), pass_=float(np.mean(agree)) == 1.0)


def t_parse():
    fails = Counter(); n = 0
    for d in S.MT:
        ws = rows(ROOT / f'data/{d}/worlds.jsonl')[:30]
        for t in S.mt_templates()[d]:
            for w in ws:
                w = dict(w, template_id=t['id'])
                for s in S.states(d):
                    g = S.gold(w, s); n += 1
                    if Ev.parse_state(g['text'], d, gold=g)[0] != s: fails['gold_parse'] += 1
                    if t['has_Y'] and s != w['distractor'] and Ev.parse_state(g['text'], d, gold=g)[0] == w['distractor']: fails['distractor_taken'] += 1
    return dict(n=n, failures=dict(fails), pass_=not fails)


def t_att2(seed=42, updates=4000):
    Htr = pointer_data(2000, 11); Hte = pointer_data(500, 12); out = {}
    adv = lambda s, op: (s + 1) % 3
    for kind in ('Tok', 'Att2'):
        ed, hist = L.train_unrolled_l2(None, None, seed, kind, updates=updates, Sset=(1,), H=Htr, adv=adv)
        with torch.no_grad():
            num = den = 0.
            for j in range(3):
                x, m = Hte[j]; y, _ = Hte[(j + 1) % 3]; x, m, y = x.to(DEV), m.to(DEV), y.to(DEV); e = ed['plus'](x, m); v = m[..., None]
                num += float(((e - y).square() * v).sum()); den += float(((y - x).square() * v).sum())
        out[kind] = dict(heldout_rel_l2=num / den, final_train_loss=hist[-1]['loss'])
    out['pass_'] = out['Att2']['heldout_rel_l2'] <= .05 and out['Tok']['heldout_rel_l2'] >= .5
    return out


def t_unrolled_identity():
    """S = 1: lib5.unrolled_l2_loss (the function train_unrolled_l2 optimises) equals the single-step relative L2 exactly; S = 2 equals the
    hand-unrolled mean of the two steps' relative L2."""
    H = pointer_data(64, 3); torch.manual_seed(0); ed = L.tokatt_pair(128, 7, True, heads=2)
    with torch.no_grad():
        for p in ed.parameters(): p.normal_(std=.05)
        x, m = H[0]; y, _ = H[1]; z, _ = H[2]; x, m, y, z = x.to(DEV), m.to(DEV), y.to(DEV), z.to(DEV)
        single = float(L.rel_l2(ed['plus'](x, m), y, x, m)); u1 = float(L.unrolled_l2_loss(ed, x, m, ['plus'], [y], [x]))
        h1 = ed['plus'](x, m); h2 = ed['plus'](h1, m); hand2 = float((L.rel_l2(h1, y, x, m) + L.rel_l2(h2, z, y, m)) / 2)
        u2 = float(L.unrolled_l2_loss(ed, x, m, ['plus', 'plus'], [y, z], [x, y]))
    return dict(single=single, unrolled_S1=u1, hand_S2=hand2, unrolled_S2=u2, pass_=single == u1 and abs(hand2 - u2) < 1e-6)


def t_lcore():
    recs = []
    for w, (lat, dec_, ok1) in enumerate([([0, 1, 2], [0, 1, 2], True), ([0, 1, 5], [0, 1, 2], True), ([0, 9, 2], [3, 9, 2], False), ([0, 1, 2], [0, None, 2], True)]):
        okt = True
        for t in range(1, 4):
            succ = (dec_[t - 1] == [0, 1, 2][t - 1]); okt = okt and succ
            recs.append(dict(world_id=f'w{w}', step=t, state=[0, 1, 2][t - 1], argmax_full=lat[t - 1], decoded_state=dec_[t - 1], success=succ, trajectory_success=okt))
    tab = lcore.world_table(recs, 3)
    exp = {'w0': dict(pred=True, obs=True, naive=True, D1=False), 'w1': dict(pred=False, obs=True, naive=True, D1=False),
           'w2': dict(pred=False, obs=False, naive=False, D1=True), 'w3': dict(pred=True, obs=False, naive=True, D1=False)}
    okT = tab == exp; s = lcore.cell_summary(tab)
    okS = s['pred_rate'] == .5 and s['obs_rate'] == .5 and s['D'] == 0.25 and s['world_agree'] == .5 and s['naive_rate'] == .75
    p = lcore.pooled({'c': tab}); okP = p['latent'] == .5 and p['naive'] == .75 and p['majority_reference'] == .5   # naive agrees with obs in w0, w1, w2
    rng = np.random.default_rng(0); ids = [f'w{i}' for i in rng.integers(0, 7, 60)]; vals = rng.random((60, 2))
    est, rm = lcore.cluster_boot(ids, vals, reps=50, seed=5); e2, r2 = L.cluster_boot(ids, vals, reps=50, seed=5)
    okB = np.abs(rm - r2).max() < 1e-12 and lcore.boot_diff_ci(['a', 'a', 'b'], [1., 1., 1.], [0., 0., 0.])['ci95'] == [1.0, 1.0]
    return dict(table=tab, summary=s, pooled=p, pass_=bool(okT and okS and okP and okB))


def main():
    require_slurm(); t0 = time.time(); res = {}
    for name, fn in (('A7_1_decoupled', t_decoupled), ('A7_2_predictor', t_predictor), ('A7_3_parse', t_parse), ('A7_4_att2', t_att2),
                     ('A7_5_unrolled_identity', t_unrolled_identity), ('A7_6_D_bootstrap', t_lcore)):
        res[name] = fn(); print(name, {k: v for k, v in res[name].items() if k not in ('table', 'summary')}, flush=True)
    res['pass'] = all(v['pass_'] for v in res.values()); res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('lib5.py', 'lcore.py', 'selftest.py', 'sym5_semantics.py', 'sym5_evaluator.py')}
    dump('results/selftest.json', res); assert res['pass'], 'self-test failed'


if __name__ == '__main__':
    from collections import Counter
    main()
