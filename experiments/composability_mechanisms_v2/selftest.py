"""A.6 synthetic self-test (CPU; must pass before the lock): plane recovery, freeze surgery, plane editor, vote-model recovery,
idealized-chain agreement. Synthetic Z_N representation, d = 64, noise 0.01."""
import time
import torch
from symutil import *
import lib3 as L

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


def main():
    require_slurm(); t0 = time.time(); res = {f'N{N}': run(N, BOOT_SEED + N) for N in (7, 12, 4)}
    res['pass'] = all(v['pass'] for v in res.values()); res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('lib3.py', 'selftest.py')}
    dump('results/selftest.json', res); print(json.dumps(res, indent=1), flush=True)
    assert res['pass'], 'synthetic self-test failed'


if __name__ == '__main__':
    main()
