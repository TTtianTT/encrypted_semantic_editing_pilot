"""Section 7.2 (GPU host, deterministic, train/dev only, before the lock). --backbone bart|t5.
R: for each R domain kept by GB and each grid rank r, fit ordinary RRR-r and FF-r (appendix A.3; same ridge-selection procedure),
compute per-plane eps_k (A.2), RRR-r 'missing fundamental' (eps_1 > 0.5), S_FF = {k: eps_k > 0.5} of FF-r, and the vote model's
idealized category for FF-r (S_FF frozen, the rest rotating; dev canonical states; plus path). Scorable cells: RRR-r misses the
fundamental AND |S_FF| <= 1 AND the predicted FF-r category is composable. Dev single-step success is recorded (exploratory).
S (T5Gemma only): RRR-32 fits for weekday and month under the natural map and sigma_max."""
import time
from lib4 import *


def grid(bb, N):
    return [N - 4, N - 3, N - 2] if bb == 'bart' else [N - 2, N - 1, N, N + 2]


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine4(bb)
    gates = read(ROOT / f'results/gates_{bb}.json'); cal = read(ROOT / f'results/calib_{bb}.json')['domains']; res = dict(backbone=bb, cells={})
    for d in gates['R_domains']:
        N = len(S.states(d)); ranks = grid(bb, N); P = planes(bb, d); Q1 = P[0][1]; assert P[0][0] == 1 and Q1.shape[1] == 2
        rr, ri = fit_rrr4(bb, d, 'natural', ranks); ff, fi = fit_rrr4(bb, d, 'natural', ranks, ff=True, Q1=Q1)
        fits = {('RRR', op, r): rr[op, r] for op in ('plus', 'minus') for r in ranks} | {('FF', op, r): ff[op, r] for op in ('plus', 'minus') for r in ranks}
        save(f'local/{bb}_R_{d}.pt', fits); lam = torch.tensor(cal[d]['models']['full']['lam'], dtype=torch.float64); Cw = slot_matrix(bb, d, 'dev')
        for r in ranks:
            er = op_plane_errors('rrr', rr['plus', r], 'plus', bb, d); ef = op_plane_errors('rrr', ff['plus', r], 'plus', bb, d)
            S_FF = sorted(k for k, v in ef.items() if v['eps'] > .5); pred = ideal_R(Cw, P, lam, set(S_FF), d)
            miss = er[1]['eps'] > .5; cat = category(pred['plus'])
            c = dict(domain=d, rank=r, N=N, eps_RRR={str(k): v['eps'] for k, v in er.items()}, eps_FF={str(k): v['eps'] for k, v in ef.items()},
                     RRR_missing_fundamental=miss, S_FF=S_FF, S_RRR=sorted(k for k, v in er.items() if v['eps'] > .5),
                     FF_pred_R_hat=pred, FF_pred_category=cat, ridge=dict(RRR=ri, FF=fi),
                     dev_single=dict(RRR=dev_single(eng, bb, d, 'natural', {op: RRRop(rr[op, r]) for op in ('plus', 'minus')})['rate'],
                                     FF=dev_single(eng, bb, d, 'natural', {op: RRRop(ff[op, r]) for op in ('plus', 'minus')})['rate']))
            c['scorable'] = bool(miss and len(S_FF) <= 1 and cat == 'composable')
            res['cells'][f'{bb}/{d}/r{r}'] = c
            print('R pre', bb, d, r, 'miss1', miss, 'S_FF', S_FF, 'cat', cat, 'scorable', c['scorable'], 'dev', c['dev_single'], flush=True)
        res[f'{d}_fits_sha256'] = sha(ROOT / f'local/{bb}_R_{d}.pt')
    res['scorable_cells'] = [k for k, v in res['cells'].items() if v['scorable']]
    if bb == 't5':
        res['S_fits'] = {}
        for d in S_DOMAINS:
            for mp in ('natural', 'scrmax'):
                f, info = fit_rrr4('t5', d, mp, [32]); save(f'local/t5_S_{d}_{mp}.pt', f)
                res['S_fits'][f'{d}/{mp}'] = dict(ridge=info, sha256=sha(ROOT / f'local/t5_S_{d}_{mp}.pt'),
                                                  dev_single=dev_single(eng, 't5', d, mp, {op: RRRop(f[op, 32]) for op in ('plus', 'minus')})['rate'])
                print('S fit', d, mp, res['S_fits'][f'{d}/{mp}'], flush=True)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/prelock_{bb}.json', res)


if __name__ == '__main__':
    main()
