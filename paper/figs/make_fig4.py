"""Figure 4: one-way plus R_2N of ordinary RRR-r and fundamental-first FF-r against the rank (v5 L grid; T5Gemma confirmatory F cells,
BART exploratory)."""
from _style import *
P5 = 'experiments/composability_mechanisms_v4/results/predictions.json'


def main():
    require_slurm(); L = read(P5)['L']['cells']; doms = ('weekday', 'month', 'hour', 'compass8'); fig, axs = plt.subplots(1, 4, figsize=(8, 2.3), sharey=True)
    for ax, d in zip(axs, doms):
        for bb in ('bart', 't5'):
            for kind, ls, mk in (('RRR', '-', 'o'), ('FF', '--', 's')):
                pts = sorted((int(k.split('/')[3][len(kind):]), v['obs_rate']) for k, v in L.items() if k.startswith(f'L/{bb}/{d}/{kind}') and k.endswith('/plus') and k.split('/')[3][len(kind):].isdigit())
                if pts: ax.plot(*zip(*pts), c=BB_COL[bb], ls=ls, marker=mk, ms=3, label=f'{BB_NAME[bb]} {kind}-r')
        ax.set_title(d); ax.set_xlabel('rank $r$')
    axs[0].set_ylabel('one-way plus $R_{2N}$'); axs[0].legend(fontsize=5.5)
    finish(fig, 'fig4', [P5])


if __name__ == '__main__':
    main()
