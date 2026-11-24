"""Figure 2: (a) rank-deficient RRR (BART month, r = N - 4 .. N - 2, v5 L grid): per-step A_t on the one-way plus path (revival at t = N)
and the alternating path; (b) freezing the fundamental F{1} vs every other plane F_not1, plus path, A_t, both backbones (v5 L cells)."""
from _style import *
V5 = 'experiments/composability_mechanisms_v4/results/chains.csv'


def main():
    require_slurm(); ch = chains(V5); fig, axs = plt.subplots(1, 2, figsize=(7, 2.6))
    for r, c in ((8, '#c6dbef'), (9, '#6baed6'), (10, '#08519c')):
        for path, ls in (('plus', '-'), ('alt', ':')):
            x = curve(ch, ('bart', 'month', f'RRR{r}', path), 'A')
            if x: axs[0].plot(*x, c=c, ls=ls, label=f'RRR-{r}, {"one-way plus" if path == "plus" else "alternating"}')
    axs[0].axvline(12, c='grey', lw=.6); axs[0].set_xlabel('step $t$'); axs[0].set_ylabel('$A_t$'); axs[0].set_title('(a) BART month, rank below $N-1=11$'); axs[0].legend(fontsize=5.5)
    for bb in ('bart', 't5'):
        for m, ls in (('F_{1}', '-'), ('F_not1', '--')):
            x = curve(ch, (bb, 'month', m, 'plus'), 'A')
            if x: axs[1].plot(*x, c=BB_COL[bb], ls=ls, label=f'{BB_NAME[bb]}, {"freeze fundamental $F_{\\{1\\}}$" if m == "F_{1}" else "freeze all others $F_{\\neg 1}$"}')
    axs[1].set_xlabel('step $t$'); axs[1].set_ylabel('$A_t$'); axs[1].set_title('(b) month, one-way plus'); axs[1].legend(fontsize=5.5)
    finish(fig, 'fig2', [V5])


if __name__ == '__main__':
    main()
