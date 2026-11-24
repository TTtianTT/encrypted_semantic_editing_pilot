"""Appendix figure C1 (v5 unit D): one-way plus R_t of the standard frozen-plane surgery F{j} (dashed) and the oracle-decoupled freeze D{j}
(solid; the frozen plane is reset to the correct value before each step and frozen again after it) for j = 2, 3, 4 on month and hour,
both backbones (v5 confirm5, chains.csv)."""
from _style import *
V5 = 'experiments/composability_mechanisms_v4/results/chains.csv'
COL = {2: '#1b9e77', 3: '#d95f02', 4: '#7570b3'}


def main():
    require_slurm(); ch = chains(V5); fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.4), sharey=True)
    for i, bb in enumerate(('bart', 't5')):
        for j_, d in enumerate(('month', 'hour')):
            ax = axs[i, j_]
            for k, c in COL.items():
                for pre, ls in (('F', '--'), ('D', '-')):
                    x = curve(ch, (bb, d, f'{pre}_{{{k}}}', 'plus'))
                    if x: ax.plot(*x, c=c, ls=ls, lw=1, label=f"{'standard' if pre == 'F' else 'decoupled'} $\\{{{k}\\}}$")
            ax.set_title(f'{BB_NAME[bb]}, {d}'); ax.set_ylim(-.03, 1.03); ax.set_xlabel('chain length $t$')
            if j_ == 0: ax.set_ylabel('$R_t$ (one-way plus)')
    h, l = axs[0, 0].get_legend_handles_labels(); fig.tight_layout(); fig.legend(h, l, loc='upper center', bbox_to_anchor=(.5, 0), ncol=3, frameon=False, fontsize=6)
    finish(fig, 'figC1', [V5])


if __name__ == '__main__':
    main()
