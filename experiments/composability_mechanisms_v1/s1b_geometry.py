"""S1b geometry and slot linear predictability (CPU, before the lock; train+dev only).
Slot predictability: ridge regression (intercept, lambda by 5-fold CV over train worlds) from the source-state slot vector to the
target-state slot vector (plus transitions, template 0, train); R^2 on dev plus transitions."""
import time
import torch
from symutil import *
import sym2_semantics as S

LAMBDAS = [10.0 ** k for k in range(-3, 5)]


def slot_xy(d, split):
    pos = slot_pos(d, 0); C = {s: cache2(d, split, s) for s in S.states(d)}; X = []; Y = []; W = []
    for s in S.states(d):
        y = S.advance(d, s, 'plus')
        X.append(C[s]['h'][:, pos].double().numpy()); Y.append(C[y]['h'][:, pos].double().numpy()); W += list(range(len(C[s]['h'])))
    return np.concatenate(X), np.concatenate(Y), np.array(W)


def cv_lambda(X, Y, W):
    folds = np.array([w % 5 for w in W]); score = {}
    for lam in LAMBDAS:
        sse = 0.
        for f in range(5):
            tr, te = folds != f, folds == f; m = ridge_fit(X[tr], Y[tr], lam); sse += ((ridge_predict(m, X[te]) - Y[te]) ** 2).sum()
        score[lam] = sse
    return min(score, key=score.get), score


def main():
    require_slurm(); t0 = time.time(); res = {}; nulls = []
    for d in S1B_DOMAINS:
        n = 3; pairs = [(i, (i + 1) % n) for i in range(n)]
        for t in (0, 3):
            V = torch.cat([pooled2(d, sp, t)['pooled'] for sp in ('train', 'dev')]).double().numpy()
            out, nr, _ = geometry_report(V, S.states(d), pairs, 'cyclic', name=f'{d}_t{t}'); res[f'{d}_t{t}'] = out; nulls += nr
        X, Y, W = slot_xy(d, 'train'); Xd, Yd, _ = slot_xy(d, 'dev'); lam, sc = cv_lambda(X, Y, W)
        m = ridge_fit(X, Y, lam)
        res[f'{d}_slot_predictability'] = dict(lambda_=lam, cv_sse={str(k): v for k, v in sc.items()}, dev_R2=r2_score(Yd, ridge_predict(m, Xd)),
                                               train_R2=r2_score(Y, ridge_predict(m, X)), slot_position=slot_pos(d, 0), n_train=len(X), n_dev=len(Xd))
        print(d, res[f'{d}_t0']['E_iso']['mean'], 'SEP', res[f'{d}_t0']['SEP'], 'slot R2', res[f'{d}_slot_predictability']['dev_R2'], flush=True)
    r2 = {d: res[f'{d}_slot_predictability']['dev_R2'] for d in S1B_DOMAINS}
    res['B4_pre_lock'] = dict(delta=r2['bind3'] - min(r2['pron3'], r2['name3']), dev_R2=r2,
                              note='Observed before the lock (train+dev only, as the plan specifies); B4 is therefore not prospective.')
    res['seconds'] = time.time() - t0
    dump('results/s1b_geometry.json', res); csvwrite('results/s1b_geometry_null.csv', nulls)


if __name__ == '__main__':
    main()
