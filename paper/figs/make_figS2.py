"""Appendix figure S2 (v6 K): one-way plus R_k on bind3, name3 and bind3fix (seed medians) for the binding editors; the oracle-routing
editor OR-U4 is a diagnostic. Read from the locked v6 chains.csv."""
from _style import *
V6 = 'experiments/composability_mechanisms_v5/results/chains.csv'
EDS = (('ORU4', 'OR-U4 (oracle routing, diagnostic)', 'k', '--'), ('Att2LU8', 'Att2L-U8 (two layers, $S\\leq8$)', '#17becf', '-'),
       ('Att2LU4', 'Att2L-U4 (two layers, $S\\leq4$)', '#2ca02c', '-'), ('Att1U8', 'Att1-U8 (one layer, $S\\leq8$)', '#d62728', '-'),
       ('Att1U', 'Att1-U (one layer, $S\\leq4$)', '#ff9896', '-'), ('TokU', 'Tok-U (token-wise)', '#1f77b4', ':'))


def main():
    require_slurm(); ch = chains(V6); fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.3), sharey=True)
    for ax, d in zip(axs, ('bind3', 'name3', 'bind3fix')):
        for stem, lab, c, ls in EDS:
            x = seed_median(ch, 'bart', d, stem, 'plus')
            if x: ax.plot(*x, c=c, ls=ls, lw=1, label=lab)
        ax.set_title(f'BART-base, {d}'); ax.set_xlabel('chain length $k$'); ax.set_ylim(-.03, 1.03)
    axs[0].set_ylabel('$R_k$ (seed median)'); h, l = axs[0].get_legend_handles_labels(); fig.tight_layout(); fig.legend(h, l, loc='upper center', bbox_to_anchor=(.5, 0), ncol=3, frameon=False)
    finish(fig, 'figS2', [V6])


if __name__ == '__main__':
    main()
