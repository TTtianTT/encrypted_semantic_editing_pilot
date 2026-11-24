"""Figure 5: (a) unrolled CE editors (C1-U4, trained with S <= 4; v4 U unit, BART) - R_k along the one-way plus path: perfect inside
the training horizon, collapse after it; (b) step-1 disagreement D against one-way R_2N per (editor, domain, direction) (v5 L3)."""
from _style import *
V4 = 'experiments/composability_mechanisms_v3/results/chains.csv'; P5 = 'experiments/composability_mechanisms_v4/results/predictions.json'


def chains4(f):
    out = defaultdict(dict)
    with open(REPO / f) as g:
        for r in csv.DictReader(g):
            if r['map'] == 'natural': out[(r['backbone'], r['domain'], r['method'], r['path'].replace('_from_start', ''))][int(r['t'])] = dict(A=float(r['A_t']), R=float(r['R_t']))
    return out


def main():
    require_slurm(); ch = chains4(V4); fig, axs = plt.subplots(1, 2, figsize=(7, 2.6))
    for d, c in (('compass', '#ff7f0e'), ('weekday', '#2ca02c'), ('month', '#9467bd')):
        x = seed_median(ch, 'bart', d, 'C1U4', 'plus')
        if x: axs[0].plot(*x, c=c, label=f'C1-U4, {d} (seed median)')
    axs[0].axvline(4, c='grey', lw=.6, ls=':'); axs[0].set_xlabel('chain length $k$'); axs[0].set_ylabel('$R_k$'); axs[0].set_title('(a) unrolled CE, training horizon $S\\leq4$'); axs[0].legend()
    cells = read(P5)['L']['L3']['cells']
    for fam, c, mk, lab in (('CE', '#9467bd', 'o', 'CE family'), ('state', '#2ca02c', 's', 'state-supervised family')):
        pts = [(v['D'], v['R2N']) for v in cells.values() if v['D'] is not None and (v['family'] == 'CE') == (fam == 'CE')]
        axs[1].scatter(*zip(*pts), c=c, marker=mk, s=10, alpha=.7, label=f'{lab} ({len(pts)} cells)')
    axs[1].axvline(.5, c='k', ls=':', lw=.6); axs[1].set_xlabel('step-1 disagreement $D$'); axs[1].set_ylabel('one-way $R_{2N}$'); axs[1].set_title('(b) $D$ separates the two families'); axs[1].legend()
    finish(fig, 'fig5', [V4, P5])


if __name__ == '__main__':
    main()
