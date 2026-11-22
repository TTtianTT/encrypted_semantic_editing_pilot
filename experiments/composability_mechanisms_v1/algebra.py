"""Algebraic diagnostics for every RRR fit (CPU, float64): unit-block eigenvector condition kappa_u, transient growth G,
phase deviation from N-th roots of unity, harmonics present, kappa_N (cyclic), e_inv and DRIFT on confirm canonical states."""
import time
import torch
from symutil import *
import sym2_semantics as S

UNIT = 0.9


def unit_block(AQ, N):
    ev, V = torch.linalg.eig(AQ)
    keep = ev.abs() >= UNIT; lam = ev[keep]; Vu = V[:, keep]
    Vu = Vu / Vu.norm(dim=0, keepdim=True)
    sv = torch.linalg.svdvals(Vu) if Vu.shape[1] else torch.tensor([1.])
    ph = torch.rad2deg(torch.angle(lam)).numpy(); step = 360. / N
    j = np.round(ph / step).astype(int) % N; dev = np.abs(((ph - j * step) + 180) % 360 - 180)
    harm = sorted({int(min(a, N - a)) for a, dv in zip(j, dev) if dv < 2})
    return dict(n_unit=int(keep.sum()), kappa_u=float(sv.max() / sv.min()), max_phase_dev_deg=float(dev.max()) if len(dev) else None,
                harmonics_present=harm, unit_moduli=lam.abs().tolist(), unit_phases_deg=ph.tolist())


def growth(AQ, K):
    P = torch.eye(AQ.shape[0], dtype=torch.float64); g = []
    for _ in range(K):
        P = P @ AQ; g.append(float(torch.linalg.matrix_norm(P, 2)))
    return max(g), g


def apply(f, h, m):
    U, V, b = (x.float() for x in f)
    return h + ((h @ V.T) @ U.T + b) * m[..., None]


def main():
    require_slurm(); p = verify_protocol2(); S.load_maps(ROOT / 'protocol.json'); t0 = time.time(); res = {}
    for spec in p['fits']:
        d, mp = spec['domain'], spec['map']; fits = load(ROOT / f'local/rrr_{d}_{mp}.pt'); N = len(S.states(d))
        split = 'confirm2' if d in V1_DOMAINS else 'confirm'; C = {s: cache2(d, split, s) for s in S.states(d)}; W = len(C[S.states(d)[0]]['h'])
        for r in spec['ranks']:
            F = {op: editor_factors('rrr', fits[op, r], op) for op in ('plus', 'minus')}; out = dict(domain=d, map=mp, rank=r, N=N)
            for op in ('plus', 'minus'):
                st, Q, AQ = operator_stats(*F[op]); st.pop('power_norm')
                st.update(unit_block(AQ, N)); st['G'], _ = growth(AQ, 10 * N); out[op] = st
            for first, inv in (('plus', 'minus'), ('minus', 'plus')):
                num = torch.zeros(W, dtype=torch.float64); den = torch.zeros(W, dtype=torch.float64)
                for x in S.states(d):
                    try: y = S.advance(d, x, first, mp)
                    except ValueError: continue
                    h, m = C[x]['h'].float(), C[x]['m'].float(); v = m[..., None]
                    z = apply(F[inv], apply(F[first], h, m), m)
                    num += ((z - h) * v).square().sum((1, 2)).double(); den += ((C[y]['h'].float() - h) * v).square().sum((1, 2)).double()
                out[f'e_inv_{inv}_o_{first}'] = boot_mean((num / den).sqrt().numpy())
            if d != 'daysago':
                num = torch.zeros(W, dtype=torch.float64); den = torch.zeros(W, dtype=torch.float64)
                for x in S.states(d):
                    h, m = C[x]['h'].float(), C[x]['m'].float(); v = m[..., None]; z = h
                    for _ in range(N): z = apply(F['plus'], z, m)
                    num += ((z - h) * v).square().sum((1, 2)).double(); den += ((apply(F['plus'], h, m) - h) * v).square().sum((1, 2)).double()
                k = (num / den).sqrt().numpy(); out['kappa_N'] = dict(median=float(np.median(k)), mean=float(k.mean()))
            res[f'{d}/{mp}/RRR{r}'] = out
            print(d, mp, r, 'kappa_u', round(out['plus']['kappa_u'], 3), 'G', round(out['plus']['G'], 2), 'harm', out['plus']['harmonics_present'], flush=True)
    res['_definitions'] = dict(kappa_u='sigma_max/sigma_min of unit-normalised eigenvectors with |lambda| >= 0.9 (A_Q)', G='max_{k<=10N} ||A_Q^k||_2',
                               phase='deviation of arg(lambda) from the nearest multiple of 360/N; harmonic k=min(j,N-j) present if deviation < 2 deg')
    res['_seconds'] = time.time() - t0
    dump('results/algebra.json', res)


if __name__ == '__main__':
    main()
