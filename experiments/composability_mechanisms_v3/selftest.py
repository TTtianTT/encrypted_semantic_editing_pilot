"""A.8 synthetic self-test (CPU; must pass before the lock). Part 1 (v3 A.6, unchanged, on lib4): plane recovery, freeze surgery,
plane editor, vote-model recovery, idealized-chain agreement. Part 2 (v4 A.8): per-plane error, FF-r, unrolled-training loss and
path targets, attention editor on a synthetic pointer-copy task, scoring tools (A(m~), discriminability, cluster bootstrap)."""
import time
import torch
from symutil import *
import lib4 as L

D_ = 64; W_ = 96; NOISE = .01   # W = 96 = real train-world count


def synth(N, seed):
    g = torch.Generator().manual_seed(seed); K = N // 2
    E, _ = torch.linalg.qr(torch.randn(D_, D_, generator=g, dtype=torch.float64))
    amps = torch.linspace(1.0, 0.4, K, dtype=torch.float64); x = torch.arange(N, dtype=torch.float64); c = torch.zeros(N, D_, dtype=torch.float64); truth = []
    col = 0
    for k in range(1, K + 1):
        e1 = E[:, col]; c += amps[k - 1] * torch.cos(2 * np.pi * k * x / N)[:, None] * e1[None]
        if 2 * k != N:
            e2 = E[:, col + 1]; c += amps[k - 1] * torch.sin(2 * np.pi * k * x / N)[:, None] * e2[None]; truth.append((k, E[:, col:col + 2])); col += 2
        else:
            truth.append((k, E[:, col:col + 1])); col += 1
    comp = E[:, col:]                                                              # complement of all planes
    off = (torch.randn(W_, comp.shape[1], generator=g, dtype=torch.float64) @ comp.T)[:, None, :]
    X = c[None] + off + NOISE * torch.randn(W_, N, D_, generator=g, dtype=torch.float64)
    X0 = c[None] + off                                                            # noise-free (for operator tests)
    return X, X0, truth, c


def rotation(truth, N):
    R = torch.eye(D_, dtype=torch.float64)
    for k, B in truth:
        th = 2 * np.pi * k / N
        if B.shape[1] == 2:
            Rk = torch.tensor([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]], dtype=torch.float64)
        else:
            Rk = torch.tensor([[np.cos(th)]], dtype=torch.float64)
        R = R + B @ (Rk - torch.eye(B.shape[1], dtype=torch.float64)) @ B.T
    return R


def run(N, seed):
    out = {}; X, X0, truth, c = synth(N, seed)
    # 1 plane recovery
    P = L.gram_planes(L.cbar_of(X)); ang = []
    for (k, B), (k2, Bt) in zip(P, truth):
        sv = torch.linalg.svdvals(B.T @ Bt).clamp(max=1); ang.append(float(torch.rad2deg(torch.arccos(sv.min()))))
    out['max_principal_angle_deg'] = max(ang); out['n_planes'] = [len(P), len(truth)]
    # 2 freeze surgery with the exact rotation T (true planes)
    R = rotation(truth, N); T = lambda h, m: h @ R.T
    h = X0[:, :1, :].clone(); m = torch.ones(W_, 1); pos = torch.zeros(W_, dtype=torch.long); e2 = []
    for k, B in truth:
        F = L.Freeze(T, B, pos); h1 = F(h, m)[:, 0]; h0 = h[:, 0]
        e2.append(float(((h1 - h0) @ B).abs().max()))
        for k2, B2 in truth:
            if k2 != k: e2.append(float(((h1 @ B2) - (h0 @ R.T @ B2)).abs().max()))
    out['freeze_max_err'] = max(e2)
    # 3 plane editor on noise-free training pairs (offsets orthogonal to the planes)
    e3 = []; ks = [k for k, _ in truth]
    for K in ([ks[0]], ks[:2] if len(ks) > 1 else ks, ks):
        B = torch.cat([b for k, b in truth if k in K], 1); A, cc = L.fit_plane_editor(X0, B, 'weekday' if N == 7 else 'month' if N == 12 else 'compass', 'plus')
        E = L.PlaneEd(A, cc, B, pos); h1 = E(h.float(), m)[:, 0].double(); h0 = h[:, 0]
        e3.append(float(((h1 - h0 @ R.T) @ B).abs().max()))
        for k2, B2 in truth:
            if k2 not in K: e3.append(float(((h1 - h0) @ B2).abs().max()))
    out['plane_editor_max_err'] = max(e3)
    # 4 vote-model recovery from simulated probes (decoder samples from softmax with known lambda)
    Ed = torch.stack([((X[:, [(s + 1) % N for s in range(N)]] - X) @ B).square().sum(-1).mean() for _, B in truth])
    lam_true = torch.tensor([3.0, 1.5, 0.75, 0.5, 0.3, 0.2][:len(truth)], dtype=torch.float64) / Ed
    g = torch.Generator().manual_seed(seed + 1); H = []; Cw = []
    for w in range(W_):
        for x in range(N):
            for j, (k, B) in enumerate(truth):
                Pk = B @ B.T; Pc = torch.eye(D_, dtype=torch.float64) - Pk
                for mshift in range(1, N):
                    dlt = X[w, (x + mshift) % N] - X[w, x]
                    H += [X[w, x] + dlt @ Pk, X[w, x] + dlt @ Pc]; Cw += [X[w], X[w]]
    H = torch.stack(H); Cw = torch.stack(Cw); Dm = L.plane_dists(H, Cw, truth)
    y = torch.multinomial(torch.softmax(L.vote_scores(Dm, lam_true), -1), 1, generator=g)[:, 0]
    lam0 = 1 / torch.stack([((X[:, [(s + 1) % N for s in range(N)]] - X) @ B).square().sum(-1).median() for _, B in truth])
    lam_fit, nll = L.fit_vote(Dm, y, 'full', lam0)
    w_true = L.omega(lam_true, Ed); w_fit = L.omega(lam_fit, Ed)
    out['omega_true'] = w_true; out['omega_fit'] = w_fit; out['omega_max_abs_err'] = float(max(abs(a - b) for a, b in zip(w_true, w_fit)))
    # 5 idealized chains: fitted-model argmax vs simulated decoder (true-lambda argmax)
    agree = []; ks = [k for k, _ in truth]
    for n_ in range(0, len(ks) + 1):
        for fr in [set(ks[:n_]), set(ks[n_:])]:
            Bf = [B for k, B in truth if k in fr]
            for kind in ('plus', 'minus', 'alt'):
                for x0 in range(N):
                    gseq = []; s = x0
                    for op in L.path_ops(N, kind): s = (s + (1 if op == 'plus' else -1)) % N; gseq.append(s)
                    Hc = X[:, gseq]
                    for B in Bf: Hc = Hc + ((X[:, [x0]] - X[:, gseq]) @ B) @ B.T
                    Dc = torch.stack([((Hc[:, :, None, :] - X[:, None]) @ B).square().sum(-1) for _, B in truth], -1)
                    agree.append((L.vote_scores(Dc, lam_fit).argmax(-1) == L.vote_scores(Dc, lam_true).argmax(-1)).double().flatten())
    out['ideal_chain_agreement'] = float(torch.cat(agree).mean())
    # 5b lib3.ideal_R (plane-coordinate implementation used by calib) equals the brute-force full-space computation
    dname = {7: 'weekday', 12: 'month', 4: 'compass'}[N]; diffs = []
    for n_ in range(0, len(ks) + 1):
        for fr in [set(ks[:n_]), set(ks[n_:])]:
            fast = L.ideal_R(X, truth, lam_true, fr, dname); Bf = [B for k, B in truth if k in fr]
            for kind in ('plus', 'minus', 'alt'):
                okk = []
                for x0 in range(N):
                    gseq = []; s = x0
                    for op in L.path_ops(N, kind): s = (s + (1 if op == 'plus' else -1)) % N; gseq.append(s)
                    Hc = X[:, gseq]
                    for B in Bf: Hc = Hc + ((X[:, [x0]] - X[:, gseq]) @ B) @ B.T
                    Dc = torch.stack([((Hc[:, :, None, :] - X[:, None]) @ B).square().sum(-1) for _, B in truth], -1)
                    okk.append((L.vote_scores(Dc, lam_true).argmax(-1) == torch.tensor(gseq)).all(1))
                diffs.append(abs(fast[kind] - float(torch.cat(okk).double().mean())))
    out['ideal_R_vs_bruteforce_max_diff'] = max(diffs)
    out['pass'] = bool(out['max_principal_angle_deg'] < 1 and out['freeze_max_err'] < 1e-6 and out['plane_editor_max_err'] < 1e-4
                       and out['omega_max_abs_err'] < .05 and out['ideal_chain_agreement'] >= .99 and out['n_planes'][0] == out['n_planes'][1]
                       and out['ideal_R_vs_bruteforce_max_diff'] < 1e-12)
    return out




# ================================================================ part 2: v4 A.8
def t_eps(N, seed):
    """A.8.1: synthetic rotation-scaling operator with known (rho, delta) per plane; one plane frozen."""
    X, X0, truth, c = synth(N, seed); cb = L.cbar_of(X0); P = L.gram_planes(cb); ideal = L.ideal_from_cbar(cb, P, 'plus')
    g = np.random.default_rng(seed); Us = []; Vs = []; true = {}; frozen = P[-1][0] if len(P) > 1 else None
    for k, B in P:
        if k == frozen: M = torch.eye(B.shape[1], dtype=torch.float64); true[k] = None
        elif B.shape[1] == 2:
            rho, dl = g.uniform(.8, 1.2), g.uniform(-.5, .5)
            R = torch.tensor([[np.cos(dl), -np.sin(dl)], [np.sin(dl), np.cos(dl)]], dtype=torch.float64); M = rho * R @ ideal[k]; true[k] = (rho, dl)
        else:
            q = g.choice([-1, 1]) * g.uniform(.8, 1.2); M = q * ideal[k]; true[k] = (abs(q), 0.0 if q > 0 else np.pi)
        Us.append(B @ (M - torch.eye(B.shape[1], dtype=torch.float64))); Vs.append(B.T)
    e = L.plane_errors(torch.cat(Us, 1), torch.cat(Vs, 0), P, ideal, N); err = 0.; fr_eps = None
    for k, v in e.items():
        if true[k] is None: fr_eps = v['eps']; continue
        err = max(err, abs(v['rho'] - true[k][0]), abs(((v['delta'] - true[k][1] + np.pi) % (2 * np.pi)) - np.pi))
        expect = max(abs(true[k][0] ** t * np.exp(1j * t * true[k][1]) - 1) for t in range(1, 2 * N + 1)); err = max(err, abs(v['eps'] - expect))
    th = 2 * np.pi * frozen / N if frozen else None
    fr_expect = (max(abs(np.exp(-1j * t * th) - 1) for t in range(1, 2 * N + 1)) if P[-1][1].shape[1] == 2 else 2.0) if frozen else None
    return dict(max_recovery_err=err, frozen_plane=frozen, frozen_eps=fr_eps, frozen_eps_expected=fr_expect,
                pass_=err < 1e-6 and fr_eps is not None and abs(fr_eps - fr_expect) < 1e-6 and fr_eps >= 1.9)


def t_ff(seed=BOOT_SEED):
    """A.8.2: synthetic Z12 with s_1 smallest; RRR-9 loses plane 1 (eps_1 > 0.5), FF-9 keeps it (eps_1 <= 0.01)."""
    N = 12; X, X0, truth, c = synth(N, seed); cb = L.cbar_of(X0); P = L.gram_planes(cb); ideal = L.ideal_from_cbar(cb, P, 'plus')
    nxt = [(s + 1) % N for s in range(N)]; Xr = X0.reshape(-1, D_); Yr = (X0[:, nxt] - X0).reshape(-1, D_)
    s_k = {k: float(((X0[:, nxt] - X0) @ B).norm(dim=-1).mean()) for k, B in P}
    F = L._F(); st = F.sufficient(Xr, Yr); rel = 1e-8
    rrr = F.solve(st, rel, [9, 11])[9]; ff = L.solve_ff(st, rel, [9, 11], P[0][1])
    e_r = L.plane_errors(*editor_factors('rrr', rrr, 'plus')[:2], P, ideal, N); e_f = L.plane_errors(*editor_factors('rrr', ff[9], 'plus')[:2], P, ideal, N)
    full_r = F.solve(st, rel, [11])[11]; diff11 = float((full_r['left'].double() @ full_r['right'].double() - ff[11]['left'].double() @ ff[11]['right'].double()).abs().max())
    return dict(s_k=s_k, s1_smallest=min(s_k, key=s_k.get) == 1, eps1_rrr9=e_r[1]['eps'], eps1_ff9=e_f[1]['eps'], eps_ff9={str(k): v['eps'] for k, v in e_f.items()},
                ff11_equals_rrr11_maxdiff=diff11, pass_=min(s_k, key=s_k.get) == 1 and e_r[1]['eps'] > .5 and e_f[1]['eps'] <= .01 and diff11 < 1e-4)


def t_unrolled():
    """A.8.3 (CPU part; the real-decoder identity is checked again on GPU in the smoke test): S = 1 unrolled loss equals the
    v3 single-step CE formula; path target sequences."""
    torch.manual_seed(0); d = 16; ed = torch.nn.ModuleDict({op: L.TokAttEditor(d, 4) for op in ('plus', 'minus')})
    with torch.no_grad():
        for op in ed: ed[op].u.weight.normal_()
    h = torch.randn(3, 5, d); m = torch.ones(3, 5); m[0, 4] = 0
    ce_fn = lambda hh, mm, texts: ((hh.float().square().sum(-1) * mm).sum(1) / mm.sum(1)).mean() + 1e-3 * sum(len(t) for t in texts)
    texts = ['a b c', 'de', 'fgh']; diffs = []
    for op in ('plus', 'minus'):
        ref = ce_fn(ed[op](h, m), m, texts); got, ce, l2 = L.unrolled_loss(ed, ce_fn, None, h, m, [op], [texts]); diffs.append(abs(float(ref - got)))
    seqs = {kind: L.path_seq(kind, 3) for kind in ('plus', 'minus', 'alt')}; tg = {}
    for kind, ops in seqs.items():
        s = 5; out = []
        for op in ops: s = L.S.advance('weekday', s, op); out.append(s)
        tg[kind] = out
    ok_t = tg == dict(plus=[6, 0, 1], minus=[4, 3, 2], alt=[6, 5, 6]) and seqs['alt'] == ['plus', 'minus', 'plus']
    return dict(max_loss_diff=max(diffs), targets=tg, pass_=max(diffs) < 1e-6 and ok_t)


def pointer_data(n_seq, seed, d=128):
    """A.8.4 synthetic pointer copy: length 8; positions 1-3 hold names (list subspace) + position markers; the slot (position 5) holds
    the slot-coded name_j + slot marker p_j; the target slot holds name_{j+1} (cyclic) + p_{j+1}; other positions unchanged.
    Names in one sequence share a random component (name_i = c + e_i), so that the best token-wise predictor cannot reach 0.5."""
    g = torch.Generator().manual_seed(seed); E, _ = torch.linalg.qr(torch.randn(d, d, generator=torch.Generator().manual_seed(1234), dtype=torch.float64))
    Lsub, SN, POS, PS, FIL = E[:, :16], E[:, 16:32], E[:, 32:40], E[:, 40:43], E[:, 43:]
    c = torch.randn(n_seq, 1, 16, generator=g, dtype=torch.float64) * np.sqrt(.75 / 16); e = torch.randn(n_seq, 3, 16, generator=g, dtype=torch.float64) * np.sqrt(.25 / 16)
    names = c + e                                                                    # (n, 3, 16)
    base = torch.zeros(n_seq, 8, d, dtype=torch.float64) + POS.T[None]               # position markers
    for p in (0, 4, 6, 7): base[:, p] += torch.randn(n_seq, FIL.shape[1], generator=g, dtype=torch.float64) * .2 @ FIL.T
    for i in range(3): base[:, 1 + i] += names[:, i] @ Lsub.T
    H = {}
    for j in range(3):
        h = base.clone(); h[:, 5] += names[:, j] @ SN.T + .3 * PS[:, j]; H[j] = (h.float(), torch.ones(n_seq, 8))
    return H


def t_attention(seed=42, updates=4000):
    Htr = pointer_data(2000, 11); Hte = pointer_data(500, 12); out = {}
    for name, att in (('Tok-L2', False), ('Att-L2', True)):
        ed, hist = L.train_l2_editor(None, None, 'plus', seed, att, updates=updates, H=Htr)
        with torch.no_grad():
            num = den = 0.
            for j in range(3):
                x, m = Hte[j]; y, _ = Hte[(j + 1) % 3]; e = ed['plus'](x, m); v = m[..., None]
                num += float(((e - y).square() * v).sum()); den += float(((y - x).square() * v).sum())
        out[name] = dict(heldout_rel_l2=num / den, final_train_loss=hist[-1]['loss'])
    out['pass_'] = out['Att-L2']['heldout_rel_l2'] <= .05 and out['Tok-L2']['heldout_rel_l2'] >= .5
    return out


def t_scoring():
    """A.8.5: A(m~), discriminability scoring and the cluster bootstrap on hand-built inputs."""
    N = 4; recs = []
    for w, x0 in enumerate([0, 1, 2, 3]):
        s = x0
        for t in range(1, 2 * N + 1):
            s = (s + 1) % N; m_ = min(t % N, N - t % N)
            recs.append(dict(world_id=f'w{w}', step=t, start=x0, state=s, success=(m_ == 1) or (m_ == 0 and w < 2)))
    A = L.A_by_disp(recs, N); okA = A == {0: .5, 1: 1.0, 2: 0.0}
    alt = [dict(world_id='w', step=t, start=0, state=(1 if t % 2 else 0), success=bool(t % 2)) for t in range(1, 9)]; okA &= L.A_by_disp(alt, N) == {0: 0.0, 1: 1.0}
    ph = {'a': 'composable', 'b': 'fail', 'c': 'partial', 'd': 'composable', 'e': 'fail'}; pf = {k: 'composable' for k in ph}
    ds = L.disc_score(ph, pf, {'a': 'composable', 'b': 'fail', 'c': 'partial', 'd': 'fail', 'e': 'fail'}, 3)
    okD = ds['n'] == 3 and ds['match_H'] == 1.0 and ds['match_H2'] == 0.0 and ds['verdict'] == 'H wins' and L.disc_score(ph, pf, {}, 4)['verdict'] == 'not evaluable'
    rng = np.random.default_rng(0); ids = [f'w{i}' for i in rng.integers(0, 7, 60)]; vals = rng.random((60, 2))
    est, rm = L.cluster_boot(ids, vals, reps=50, seed=5)
    ws = sorted(set(ids)); draw = np.random.default_rng(5).integers(len(ws), size=(50, len(ws))); naive = []
    for r in draw:
        sel = np.concatenate([np.where(np.array(ids) == ws[i])[0] for i in r]); naive.append(vals[sel].mean(0))
    okB = np.abs(np.array(naive) - rm).max() < 1e-12 and np.abs(est - vals.mean(0)).max() < 1e-12
    const = L.boot_diff_ci(['a', 'a', 'b'], [1., 1., 1.], [0., 0., 0.]); okB &= const['ci95'] == [1.0, 1.0]
    return dict(A=A, disc=ds, boot_max_diff=float(np.abs(np.array(naive) - rm).max()), pass_=bool(okA and okD and okB))


def main():
    require_slurm(); t0 = time.time(); res = {f'N{N}': run(N, BOOT_SEED + N) for N in (7, 12, 4)}
    res['A8_1_eps'] = {f'N{N}': t_eps(N, BOOT_SEED + 100 + N) for N in (7, 12, 8, 4)}
    res['A8_2_ff'] = t_ff(); res['A8_3_unrolled'] = t_unrolled(); res['A8_4_attention'] = t_attention(); res['A8_5_scoring'] = t_scoring()
    res['pass'] = (all(res[f'N{N}']['pass'] for N in (7, 12, 4)) and all(v['pass_'] for v in res['A8_1_eps'].values())
                   and all(res[k]['pass_'] for k in ('A8_2_ff', 'A8_3_unrolled', 'A8_4_attention', 'A8_5_scoring')))
    res['seconds'] = time.time() - t0; res['sources'] = {f: sha(ROOT / f) for f in ('lib4.py', 'selftest.py')}
    dump('results/selftest.json', res); print(json.dumps(res, indent=1, default=str)[:6000], flush=True)
    assert res['pass'], 'synthetic self-test failed'


if __name__ == '__main__':
    main()
