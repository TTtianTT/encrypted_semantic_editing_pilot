"""T (CPU; PLAN B4, A3). Numerical checks of propositions 1-4 on ideal harmonic codes (T1) and an exploratory comparison with the real
clean encodings of v4 / v5 (T2). Output: results/theory/t_theory.json.

Ideal code (A3): c_w(x) = mu_w + sum_k a_k [cos(2 pi k x / N) u_k + sin(2 pi k x / N) v_k] with orthonormal u_k, v_k (the Nyquist plane
k = N/2 is one-dimensional: a cos(pi x) u); world offsets mu_w lie in a subspace orthogonal to the planes.
Note on units: the data files report s_k = RMS one-step change of the plane-k slot code = 2 a_k sin(pi k / N); PLAN A3 writes the energy
4 a_k^2 sin^2(pi k / N) = s_k^2. Both give the same ordering of 2-D planes.

T1.1 (prop. 1) minimal rank r* at which closed-form RRR maps every c(x) exactly to c(x+1) (max error < 1e-8) vs the dimension
     of the span of the centred code, for several N and amplitude profiles, including missing harmonics. Also reported: the minimal
     rank whose one-way chains compose under the equal-weight nearest-code readout, which can be lower (a dropped plane with little
     readout weight does not break composition; prop. 3).
T1.2 (prop. 2) planes kept by rank-deficient RRR (captured fraction of each plane by the top-r singular directions of the fitted update)
     vs the prediction 'largest one-step energy first'; checked both per plane (s_k^2) and per dimension (s_k^2 / dim_k).
T1.3 (prop. 3) weighted nearest-state readout P(y|h) ~ exp(-sum_k lam_k ||P_k(h - c(y))||^2) under freezing: the closed-form penalty
     agrees with the vector computation; revival at t = N and 'alternating = step-1 outcome' hold for every configuration; F{1} succeeds at
     displacement 1 and fails near N/2 exactly when the derived inequalities hold; F-not-1 fails at step 1 iff
     sum_{k>=2} lam_k a_k^2 sin^2(pi k/N) > lam_1 a_1^2 sin^2(pi/N) (for the competitor y = start).
T1.4 (prop. 4) an operator that is exact on the manifold plus an off-manifold error linear in the centred code: the accumulated
     off-manifold error after a full one-way cycle is 0; on the alternating path it grows linearly in the number of pairs; the A.7 ratios
     are 0 (linear error) and 1 (constant error, identical P / M errors).
T2   (exploratory) (a) v4 pre-lock per-plane errors eps_k of RRR-r (kept iff eps_k <= 0.5) vs the planes predicted from the measured s_k,
     and whether the most degraded plane (largest eps_k) is the one predicted to be dropped first (smallest one-step energy);
     (b) F{1} one-way success by folded displacement predicted from measured a_k and v5's locked plane weights (prop. 3 penalty) vs the
     observed A(m~) of v5 L's F{1} plus chains."""
import csv
import time
from collections import defaultdict
from symutil import *

EXP_ = EXP; V3 = EXP_ / 'composability_mechanisms_v2'; V4 = EXP_ / 'composability_mechanisms_v3'; V5 = EXP_ / 'composability_mechanisms_v4'
NN = dict(weekday=7, month=12, compass=4, hour=12, compass8=8, season=4, egoside=4)


def planes_of(N):
    return [(k, 1 if 2 * k == N else 2) for k in range(1, N // 2 + 1)]


def ideal(N, a, W=6, d=None, seed=0, off=4):
    """Returns codes (W, N, d), plane bases {k: (d, dim)}, offsets."""
    rng = np.random.default_rng(seed); P = planes_of(N); dim = sum(m for _, m in P); d = d or dim + off + 4
    Q, _ = np.linalg.qr(rng.normal(size=(d, d))); B = {}; j = 0
    for k, m in P: B[k] = Q[:, j:j + m]; j += m
    Off = Q[:, j:j + off]; mu = rng.normal(size=(W, off)) @ Off.T * 3
    x = np.arange(N); c = np.zeros((N, d))
    for k, m in P:
        th = 2 * np.pi * k * x / N
        c += a[k - 1] * (np.stack([np.cos(th), np.sin(th)], 1)[:, :m] if m == 2 else np.cos(th)[:, None]) @ B[k].T
    return mu[:, None, :] + c[None], B, Q


def rrr(codes, r):
    W, N, d = codes.shape; X = codes.reshape(-1, d); Y = np.roll(codes, -1, 1).reshape(-1, d) - X
    Xt = np.hstack([X, np.ones((len(X), 1))]); Bh = np.linalg.lstsq(Xt, Y, rcond=None)[0]; Yh = Xt @ Bh
    V = np.linalg.svd(Yh, full_matrices=False)[2][:r].T; Br = Bh @ V @ V.T
    return (lambda h: h + np.hstack([h, np.ones((len(h), 1))]) @ Br), V


def composes(codes, op, steps):
    W, N, d = codes.shape; ok = True
    for x0 in range(N):
        h = codes[:, x0].copy(); x = x0
        for _ in range(steps):
            h = op(h); x = (x + 1) % N
            y = np.argmin(((h[:, None, :] - codes) ** 2).sum(-1), 1)
            if not (y == x).all(): return False
    return ok


def t1_1():
    out = []
    for N, prof in [(7, 'flat'), (12, 'flat'), (8, 'flat'), (4, 'flat'), (12, 'decay1'), (12, 'miss5'), (12, 'miss2_4'), (7, 'miss3'), (8, 'miss4')]:
        K = N // 2; a = np.ones(K)
        if prof == 'decay1': a = 1 / np.arange(1, K + 1)
        for m in {'miss5': [5], 'miss2_4': [2, 4], 'miss3': [3], 'miss4': [4]}.get(prof, []): a[m - 1] = 0
        codes, B, _ = ideal(N, a); pred = sum(m for k, m in planes_of(N) if a[k - 1] > 0)
        cen = codes - codes.mean(1, keepdims=True); span = int(np.linalg.matrix_rank(cen.reshape(-1, codes.shape[2]), tol=1e-8))
        def exact(r):
            op = rrr(codes, r)[0]; X = codes.reshape(-1, codes.shape[2]); Y = np.roll(codes, -1, 1).reshape(-1, codes.shape[2])
            return float(np.abs(op(X) - Y).max()) < 1e-8
        rstar = next((r for r in range(1, codes.shape[2] + 1) if exact(r)), None)
        rcomp = next((r for r in range(1, codes.shape[2] + 1) if composes(codes, rrr(codes, r)[0], 2 * N)), None)
        out.append(dict(N=N, profile=prof, predicted=pred, centred_span=span, r_star_exact=rstar, r_compose_nearest_readout=rcomp, holds=rstar == pred == span))
    return out


def t1_2():
    out = []
    for N in (7, 8, 12):
        for alpha in (0, .5, 1, 1.5, 2, 3):
            K = N // 2; a = np.arange(1, K + 1) ** -float(alpha); codes, B, _ = ideal(N, a, seed=1); P = planes_of(N)
            e = {k: 4 * a[k - 1] ** 2 * np.sin(np.pi * k / N) ** 2 for k, _ in P}; dimk = dict(P)
            for crit in ('per_plane', 'per_dim'):
                key = (lambda k: e[k]) if crit == 'per_plane' else (lambda k: e[k] / dimk[k])
                order = sorted(dimk, key=key, reverse=True); agree = 0; tot = 0; det = []
                for r in range(1, N - 1):
                    _, V = rrr(codes, r); cap = {k: float(np.linalg.norm(V.T @ B[k]) ** 2 / dimk[k]) for k in dimk}
                    kept = {k for k in dimk if cap[k] > .99}; budget = r; pk = set()
                    for k in order:
                        if dimk[k] <= budget: pk.add(k); budget -= dimk[k]
                        else: break
                    full = {k for k in dimk if cap[k] > .99 or cap[k] < .01}
                    if len(full) == len(dimk): tot += 1; agree += kept == pk; det.append(dict(r=r, kept=sorted(kept), predicted=sorted(pk)))
                s1min = min(e, key=lambda k: e[k] / (dimk[k] if crit == 'per_dim' else 1)) == 1
                _, V = rrr(codes, N - 1 - dimk[1]); cap1 = float(np.linalg.norm(V.T @ B[1]) ** 2 / 2)
                out.append(dict(N=N, alpha=alpha, criterion=crit, ranks_compared=tot, agree=agree, s1_smallest=s1min, fundamental_dropped_at_r_star_minus_2=cap1 < .01,
                                detail=det))
    return out


def penalty(N, lam, a, x_plane, y):
    """Prop. 3 closed form: sum_k lam_k * 4 a_k^2 sin^2(pi k (y - x_k) / N) with x_k the state each plane encodes (Nyquist: 4 a^2 [odd])."""
    return sum(lam[k - 1] * 4 * a[k - 1] ** 2 * np.sin(np.pi * k * (y - x_plane[k]) / N) ** 2 for k, _ in planes_of(N))


def readout_vec(N, lam, a, codes, B, h):
    sc = [-sum(lam[k - 1] * np.linalg.norm(B[k].T @ (h - codes[0, y])) ** 2 for k, _ in planes_of(N)) for y in range(N)]
    return int(np.argmax(sc))


def t1_3(trials=300):
    rng = np.random.default_rng(5); out = dict(trials=0, vector_equals_closed_form=0, revival=0, alt_equals_step1=0, fnot1_rule=0,
                                               f1_m1_rule=0, f1_half_rule=0, pattern_small_ok_half_fail=0)
    for _ in range(trials):
        N = int(rng.choice([7, 8, 12])); P = planes_of(N); a = rng.uniform(.3, 2, N // 2); lam = rng.uniform(0, 3, N // 2)
        codes, B, _ = ideal(N, a, W=1, seed=int(rng.integers(1e6))); out['trials'] += 1
        x0 = int(rng.integers(N)); okv = True; res = {}
        def state_vec(xp):
            h = codes[0, 0] * 0 + (codes[0].mean(0))
            for k, m in P: h = h + B[k] @ (B[k].T @ (codes[0, xp[k]] - codes[0].mean(0)))
            return h
        for t in range(1, 2 * N + 1):                                # F{1}, one-way plus
            xt = (x0 + t) % N; xp = {k: (x0 if k == 1 else xt) for k, _ in P}
            pen = [penalty(N, lam, a, xp, y) for y in range(N)]; yv = readout_vec(N, lam, a, codes, B, state_vec(xp)); yc = int(np.argmin(pen))
            okv &= pen[yv] <= min(pen) + 1e-9 * max(1, abs(min(pen)))       # ties: any minimiser
            res[t] = yc == xt
        out['vector_equals_closed_form'] += okv; out['revival'] += res[N] and res[2 * N]
        alt = []; x = x0                                             # F{1}, alternating (plane 1 frozen at x0)
        for t in range(1, 2 * N + 1):
            x = (x + 1) % N if t % 2 else (x - 1) % N; xp = {k: (x0 if k == 1 else x) for k, _ in P}
            alt.append(int(np.argmin([penalty(N, lam, a, xp, y) for y in range(N)])) == x)
        out['alt_equals_step1'] += all(alt) == res[1]
        xp = {k: ((x0 + 1) % N if k == 1 else x0) for k, _ in P}     # F-not-1, step 1
        f = int(np.argmin([penalty(N, lam, a, xp, y) for y in range(N)])) != (x0 + 1) % N
        rule = sum(lam[k - 1] * a[k - 1] ** 2 * np.sin(np.pi * k / N) ** 2 for k, _ in P if k > 1) > lam[0] * a[0] ** 2 * np.sin(np.pi / N) ** 2
        out['fnot1_rule'] += (not f) or rule                           # failure implies the rule (rule is necessary for the y = start competitor)
        h = N // 2; small = res[1]; half = not res[h]
        out['pattern_small_ok_half_fail'] += small and half
        r1 = all(penalty(N, lam, a, {k: (x0 if k == 1 else (x0 + 1) % N) for k, _ in P}, (x0 + 1) % N) < penalty(N, lam, a, {k: (x0 if k == 1 else (x0 + 1) % N) for k, _ in P}, y)
                 for y in range(N) if y != (x0 + 1) % N)
        out['f1_m1_rule'] += r1 == res[1]
        xh = (x0 + h) % N; xp = {k: (x0 if k == 1 else xh) for k, _ in P}
        out['f1_half_rule'] += all(penalty(N, lam, a, xp, xh) < penalty(N, lam, a, xp, y) for y in range(N) if y != xh) == res[h]
    out['holds'] = all(out[k] == out['trials'] for k in ('vector_equals_closed_form', 'revival', 'alt_equals_step1', 'fnot1_rule', 'f1_m1_rule', 'f1_half_rule'))
    return out


def t1_4():
    out = []
    for N in (7, 12):
        a = np.ones(N // 2); codes, B, Q = ideal(N, a, W=1, off=4, seed=3); d = codes.shape[2]; P = planes_of(N)
        mu = codes[0].mean(0); C = codes[0] - mu; Pi = sum(B[k] @ B[k].T for k, _ in P); dim = sum(m for _, m in P)
        offb = Q[:, dim + 4:]; no = offb.shape[1]; rng = np.random.default_rng(7)
        R = np.linalg.lstsq(C, np.roll(C, -1, 0), rcond=None)[0]; Rm = np.linalg.lstsq(C, np.roll(C, 1, 0), rcond=None)[0]
        res = {}
        for kind in ('linear', 'constant'):
            E = offb @ rng.normal(size=(no, d)) @ Pi * .05; Em = offb @ rng.normal(size=(no, d)) @ Pi * .05; cst = offb @ rng.normal(size=no) * .05
            err = (lambda c: E @ c) if kind == 'linear' else (lambda c: cst)
            errm = (lambda c: Em @ c) if kind == 'linear' else (lambda c: cst)
            def run(path):
                h = C[0].copy(); off = np.zeros(d); rho = []
                for op in path:
                    on = Pi @ h
                    if op == 'p': h_on = on @ R; off = off + err(on)
                    else: h_on = on @ Rm; off = off + errm(on)
                    h = h_on; rho.append(float(np.linalg.norm(off) / np.median(np.linalg.norm(C, axis=1))))
                return rho
            one = run('p' * (2 * N)); alt = run('pm' * N)
            eP = np.stack([err(C[x]) for x in range(N)]); eM = np.stack([errm(C[(x + 1) % N]) for x in range(N)])
            cyc = float(np.linalg.norm(eP.sum(0)) / np.linalg.norm(eP, axis=1).sum())
            con = float(np.median([np.linalg.norm(eP[x] + eM[x]) / (np.linalg.norm(eP[x]) + np.linalg.norm(eM[x])) for x in range(N)]))
            res[kind] = dict(rho_oneway_tN=one[N - 1], rho_oneway_t1=one[0], rho_alt_t2N=alt[-1], rho_oneway_t2N=one[-1], cycle_sum_ratio=cyc, alt_contrast=con)
        same = float(np.median([np.linalg.norm(2 * C[x]) / (2 * np.linalg.norm(C[x])) for x in range(N)]))
        out.append(dict(N=N, **res, identical_errors_alt_contrast=same,
                        holds=res['linear']['rho_oneway_tN'] < 1e-9 and res['linear']['cycle_sum_ratio'] < 1e-9 and abs(res['constant']['cycle_sum_ratio'] - 1) < 1e-9
                        and res['linear']['rho_alt_t2N'] > 10 * res['linear']['rho_oneway_t1'] and abs(same - 1) < 1e-9))
    return out


def t2():
    out = dict(a={}, b={})
    amp = {}
    for bb in ('bart', 't5'):
        for d, v in read(V3 / f'results/gates_{bb}.json')['amplitudes'].items(): amp[bb, d] = ({int(k): x['a'] for k, x in v.items()}, {int(k): x['s'] for k, x in v.items()})
    for key, v in read(V4 / 'results/predictions.json')['V']['V0']['cells'].items():
        bb, d = key.split('/'); amp[bb, d] = ({int(k): x for k, x in v['a'].items()}, {int(k): x for k, x in v['s'].items()})
    for bb in ('bart', 't5'):                                           # (a)
        pre = defaultdict(dict)
        for key, c in read(V4 / f"results/prelock_{bb}.json")["cells"].items(): _, d_, rk = key.split("/"); pre[d_][rk] = c
        for d, cells in pre.items():
            if (bb, d) not in amp: continue
            a, s = amp[bb, d]; N = NN[d]; dimk = dict(planes_of(N))
            for crit in ('per_plane', 'per_dim'):
                key = (lambda k: s[k] ** 2) if crit == 'per_plane' else (lambda k: s[k] ** 2 / dimk[k]); order = sorted(dimk, key=key, reverse=True); rows_ = []
                for rk, c in cells.items():
                    r = int(rk[1:]); kept = {int(k) for k, e in c['eps_RRR'].items() if e <= .5}; budget = r; pk = set()
                    for k in order:
                        if dimk[k] <= budget: pk.add(k); budget -= dimk[k]
                        else: break
                    eps = {int(k): e for k, e in c["eps_RRR"].items()}; worst = max(eps, key=eps.get); first = order[-1]
                    rows_.append(dict(r=r, kept=sorted(kept), predicted=sorted(pk), agree=kept == pk, eps=eps, worst_plane=worst, predicted_first_dropped=first,
                                      worst_is_predicted=worst == first))
                out["a"][f"{bb}/{d}/{crit}"] = dict(agree=sum(x["agree"] for x in rows_), ranks=len(rows_), worst_is_predicted=sum(x["worst_is_predicted"] for x in rows_), rows=rows_)
    vm = read(V5 / 'protocol.json')['vote_models']; A = defaultdict(lambda: defaultdict(list))    # (b)
    with open(V5 / 'results/chains.csv') as f:
        for r in csv.DictReader(f):
            if r['method'] == 'F_{1}' and r['path'] == 'plus_from_start':
                N = NN[r['domain']]; m = int(r['t']) % N; A[r['backbone'], r['domain']][min(m, N - m)].append(float(r['A_t']))
    for (bb, d), byd in A.items():
        if (bb, d) not in amp or d not in vm.get(bb, {}): continue
        a, _ = amp[bb, d]; N = NN[d]; lam = vm[bb][d]['full']; av = [a[k] for k in range(1, N // 2 + 1)]
        pred = {}
        for mt in range(N // 2 + 1):
            xp = {k: (0 if k == 1 else mt) for k, _ in planes_of(N)}
            pred[mt] = int(np.argmin([penalty(N, lam, av, xp, y) for y in range(N)])) == mt
        obs = {mt: float(np.mean(v)) for mt, v in byd.items()}
        out['b'][f'{bb}/{d}'] = dict(predicted_success=pred, observed_A=obs, agree=sum(pred[m] == (obs[m] >= .5) for m in obs), n=len(obs))
    return out


def main():
    require_slurm(); t0 = time.time(); out = dict(T1_1=t1_1(), T1_2=t1_2(), T1_3=t1_3(), T1_4=t1_4())
    out['T1_holds'] = dict(prop1=all(x['holds'] for x in out['T1_1']), prop3=out['T1_3']['holds'], prop4=all(x['holds'] for x in out['T1_4']),
                           prop2_per_plane=sum(x['agree'] for x in out['T1_2'] if x['criterion'] == 'per_plane'),
                           prop2_per_dim=sum(x['agree'] for x in out['T1_2'] if x['criterion'] == 'per_dim'),
                           prop2_ranks=sum(x['ranks_compared'] for x in out['T1_2'] if x['criterion'] == 'per_dim'))
    out['T2'] = t2(); out['seconds'] = time.time() - t0
    dump(ROOT / 'results/theory/t_theory.json', out); print(json.dumps(out['T1_holds']), flush=True)


if __name__ == '__main__':
    main()
