"""Appendix figure S1 (v6 M, held-out templates): per-step accuracy A_t of the slot-centred base operator (F_empty), F{1} and F-not-1 on
the one-way plus path, and the full-sequence RRR-16 reference; one panel per (backbone, domain). Read from the locked v6 chains.csv."""
from _style import *
V6 = 'experiments/composability_mechanisms_v5/results/chains.csv'
CELLS = (('bart', 'weekday-mt'), ('bart', 'month-mt'), ('bart', 'hour-mt'), ('t5', 'month-mt'))
CONDS = (('F_empty', 'S-RRR-16 (slot-centred base, $F_\\emptyset$)', '#2ca02c', '-'), ('F_{1}', '$F\\{1\\}$ (fundamental frozen)', '#1f77b4', '-'),
         ('F_not1', '$F\\neg1$ (all but fundamental frozen)', '#d62728', '-'), ('RRR16full', 'full-sequence RRR-16', '#7f7f7f', '--'))


def main():
    require_slurm(); ch = chains(V6); fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.1), sharey=True)
    for ax, (bb, d) in zip(axs, CELLS):
        for m, lab, c, ls in CONDS:
            x = curve(ch, (bb, d, m, 'plus'), 'A')
            if x: ax.plot(*x, c=c, ls=ls, lw=1, label=lab)
        ax.set_title(f'{BB_NAME[bb]}, {d}'); ax.set_xlabel('step $t$'); ax.set_ylim(-.03, 1.03)
    axs[0].set_ylabel('$A_t$ (one-way plus)'); h, l = axs[0].get_legend_handles_labels(); fig.tight_layout(); fig.legend(h, l, loc='upper center', bbox_to_anchor=(.5, 0), ncol=4, frameon=False)
    finish(fig, 'figS1', [V6])


if __name__ == '__main__':
    main()
