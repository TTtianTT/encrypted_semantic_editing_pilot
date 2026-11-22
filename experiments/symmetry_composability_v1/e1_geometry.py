"""E1.2 encoder geometry of the new domains on train+dev only (128 worlds/domain); G1a stop rule."""
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *
import sym_semantics as S


def plus_pairs(d):
    n = len(S.states(d))
    return ([(i, i + 1) for i in range(n - 1)], 'open') if d == 'daysago' else ([(i, (i + 1) % n) for i in range(n)], 'cyclic')


def pooled(d, splits, t):
    xs = [load(ROOT / f'local/e1_pooled_{d}_{sp}_t{t}.pt')['pooled'] for sp in splits]
    import torch
    return torch.cat(xs).double().numpy()


def main():
    require_slurm(); t0 = time.time(); res = {}; nulls = []
    for d in S.DOMAINS:
        pairs, kind = plus_pairs(d); labels = [S.word(d, s) for s in S.states(d)]
        for t in (0, 3):
            name = f'{d}_t{t}'
            out, nr, _ = geometry_report(pooled(d, ('train', 'dev'), t), labels, pairs, kind, name=name)
            res[name] = out; nulls += nr
            print(name, round(out['E_iso']['mean'], 4), 'q', round(out['E_iso_null']['frac_le'], 4), 'R2', out['R2_G'], flush=True)
    g = {d: dict(E_iso=res[f'{d}_t0']['E_iso']['mean'], null_q05=res[f'{d}_t0']['E_iso_null']['null_q05'],
                 below=bool(res[f'{d}_t0']['E_iso_below_null_q05'])) for d in ('weekday', 'month')}
    res['G1a'] = dict(rule='pass if E_iso (template 0, train+dev) of weekday or month is below its permutation-null 5% quantile',
                      per_domain=g, decision='pass' if any(v['below'] for v in g.values()) else 'fail')
    res['note'] = 'train + dev worlds only (128 per domain); confirm encodings are computed only after the protocol lock'
    res['seconds'] = time.time() - t0
    dump('results/e1_geometry.json', res); csvwrite('results/e1_geometry_null.csv', nulls)
    fig, axs = plt.subplots(2, 5, figsize=(18, 7))
    for j, d in enumerate(S.DOMAINS):
        pairs, _ = plus_pairs(d); labels = [S.word(d, s).replace(' days ago', '') for s in S.states(d)]
        for i, t in enumerate((0, 3)):
            pca_plot(axs[i, j], pooled(d, ('train', 'dev'), t), labels, f"{d} t{t}  E_iso={res[f'{d}_t{t}']['E_iso']['mean']:.3f}", pairs)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/e1_state_pca.png', dpi=150)
    print('G1a', res['G1a']['decision'], flush=True)


if __name__ == '__main__':
    main()
