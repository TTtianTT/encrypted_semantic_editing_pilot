"""Pre-lock gates (GPU, train+dev only). bart: GR-B (S1b' reencode), GA-B (pron3/name3 RRR-16 dev single), B4' slot R^2, a_k/s_k.
t5: GR-T (reencode), GA-T (RRR-16 dev single), a_k/s_k. No editor is fitted or evaluated for bind3 / bind3fix."""
import time
from lib3 import *

LAMBDAS = [10.0 ** k for k in range(-3, 5)]


def slot_r2(bb, d):
    def xy(split):
        X = slot_matrix(bb, d, split).numpy(); nxt = [S.advance(d, s, 'plus') for s in S.states(d)]
        W = np.repeat(np.arange(X.shape[0])[:, None], X.shape[1], 1).reshape(-1)
        return X.reshape(-1, X.shape[-1]), X[:, nxt].reshape(-1, X.shape[-1]), W
    X, Y, W = xy('train'); Xd, Yd, _ = xy('dev'); folds = W % 5; sc = {}
    for lam in LAMBDAS:
        sc[lam] = sum(((ridge_predict(ridge_fit(X[folds != f], Y[folds != f], lam), X[folds == f]) - Y[folds == f]) ** 2).sum() for f in range(5))
    lam = min(sc, key=sc.get); m = ridge_fit(X, Y, lam)
    return dict(lambda_=lam, dev_R2=r2_score(Yd, ridge_predict(m, Xd)), train_R2=r2_score(Y, ridge_predict(m, X)))


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine3(bb); res = dict(backbone=bb)
    if bb == 'bart':
        gr = {d: reencode_rate(eng, bb, d) for d in S.S1B}; res['GR_B'] = {d: dict(**v, pass_=v['rate'] >= .99) for d, v in gr.items()}
        ga = {}
        for d in ('pron3', 'name3'):
            fits, info = fit_rrr3(bb, d, 'natural', [16]); save(f'local/bart_rrr_{d}_natural_pre.pt', fits)
            ga[d] = dict(**dev_single(eng, bb, d, 'natural', {op: RRRop(fits[op, 16]) for op in ('plus', 'minus')}), ridge=info)
            ga[d]['pass_'] = ga[d]['rate'] >= .95
        res['GA_B'] = ga
        B_domains = [d for d in S.S1B if res['GR_B'][d]['pass_']]
        res['B_status'] = 'stop' if not all(res['GR_B'][d]['pass_'] for d in ('pron3', 'name3')) or not all(v['pass_'] for v in ga.values()) else 'go'
        res['B_domains'] = B_domains
        res['B4p'] = {d: slot_r2(bb, d) for d in S.S1B}
        r2 = {d: v['dev_R2'] for d, v in res['B4p'].items()}
        res['B4p_delta'] = r2['bind3'] - min(r2['pron3'], r2['name3'], r2['bind3fix'])
        res['amplitudes'] = {d: amplitudes(bb, d) for d in CYC}
    else:
        gr = {d: reencode_rate(eng, bb, d) for d in T_DOMAINS}; res['GR_T'] = {d: dict(**v, pass_=v['rate'] >= .99) for d, v in gr.items()}
        kept = [d for d in T_DOMAINS if res['GR_T'][d]['pass_']]; ga = {}
        for d in kept:
            fits, info = fit_rrr3(bb, d, 'natural', [16]); save(f'local/t5_rrr_{d}_natural_pre.pt', fits)
            ga[d] = dict(**dev_single(eng, bb, d, 'natural', {op: RRRop(fits[op, 16]) for op in ('plus', 'minus')}), ridge=info); ga[d]['pass_'] = ga[d]['rate'] >= .95
        res['GA_T'] = ga; res['T_domains'] = kept; res['T_rrr_domains'] = [d for d in kept if ga[d]['pass_']]
        res['T_status'] = 'stop' if not any(d in kept for d in ('weekday', 'month')) else 'go'
        res['amplitudes'] = {d: amplitudes(bb, d) for d in kept}
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0
    dump(f'results/gates_{bb}.json', res); print(json.dumps({k: v for k, v in res.items() if k not in ('amplitudes', 'resources')}, indent=1), flush=True)


if __name__ == '__main__':
    main()
