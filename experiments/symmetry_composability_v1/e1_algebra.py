"""E1.6 algebraic diagnostics on confirm canonical states (no decoding): ISO, NN, eigen-phases, DRIFT, e_inv, and the
closure ratio kappa_N for cyclic domains (RRR-16, C1 x3, C3 x3)."""
import time
import torch
from symutil import *
import sym_semantics as S


def factors(d, method):
    if method.startswith('RRR'):
        f = load(ROOT / f'local/e1_rrr_{d}.pt'); r = int(method[3:])
        return {op: editor_factors('rrr', f[op, r], op) for op in ('plus', 'minus')}
    g, s = method.split('_s'); sd = load(ROOT / f'local/e1_{g}_{d}_s{s}_0600.pt')['editor']
    return {op: editor_factors('editor', sd, op) for op in ('plus', 'minus')}


def apply(f, h, m):
    U, V, b = (x.float().cuda() for x in f)
    return h + ((h @ V.T) @ U.T + b) * m[..., None]


@torch.no_grad()
def main():
    require_slurm(); p = verify_protocol(); t0 = time.time(); res = {}
    for d in S.DOMAINS:
        C = {s: e1_cache(d, 'confirm', s) for s in S.states(d)}; W = len(C[S.states(d)[0]]['h'])
        for method in p['algebra_methods']:
            F = factors(d, method); r = dict(domain=d, method=method)
            for op in ('plus', 'minus'):
                st, _, _ = operator_stats(*(x.cpu() for x in F[op])); st.pop('power_norm'); r[op] = st
            r['ISO_mean'] = float(np.mean([r['plus']['ISO'], r['minus']['ISO']]))
            for first, inv in (('plus', 'minus'), ('minus', 'plus')):
                num = torch.zeros(W, dtype=torch.float64); den = torch.zeros(W, dtype=torch.float64)
                for x in S.states(d):
                    try: y = S.advance(d, x, first)
                    except ValueError: continue
                    h, m = C[x]['h'].cuda(), C[x]['m'].cuda(); g = C[y]['h'].cuda(); v = m[..., None]
                    z = apply(F[inv], apply(F[first], h, m), m)
                    num += ((z - h) * v).square().sum((1, 2)).double().cpu(); den += ((g - h) * v).square().sum((1, 2)).double().cpu()
                r[f'e_inv_{inv}_o_{first}'] = boot_mean((num / den).sqrt().numpy())
            if d != 'daysago':
                N = len(S.states(d)); num = torch.zeros(W, dtype=torch.float64); den = torch.zeros(W, dtype=torch.float64)
                for x in S.states(d):
                    h, m = C[x]['h'].cuda(), C[x]['m'].cuda(); v = m[..., None]; z = h
                    for _ in range(N): z = apply(F['plus'], z, m)
                    num += ((z - h) * v).square().sum((1, 2)).double().cpu()
                    den += ((apply(F['plus'], h, m) - h) * v).square().sum((1, 2)).double().cpu()
                k = (num / den).sqrt().numpy()
                r['kappa_N'] = dict(N=N, median=float(np.median(k)), median_ci95=boot_stat(lambda i: np.median(k[i]), len(k))['ci95'], mean=float(k.mean()),
                                    per_world=k.tolist())
            res[f'{d}/{method}'] = r; print(d, method, 'ISO', round(r['ISO_mean'], 3), 'kappa', r.get('kappa_N', {}).get('median'), flush=True)
    res['_definitions'] = dict(kappa_N='per world sqrt(sum_x ||M(T+^N E_x - E_x)||^2 / sum_x ||M(T+ E_x - E_x)||^2) over all states x; median over 160 confirm worlds',
                               e_inv='per world sqrt(sum_x ||M(T_inv T_first E_x - E_x)||^2 / sum_x ||M(E_gx - E_x)||^2); world mean with bootstrap')
    res['_seconds'] = time.time() - t0
    dump('results/e1_algebra.json', res)


if __name__ == '__main__':
    main()
