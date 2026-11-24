"""Figure 1(b): BART month, one-way plus R_k of v1 C1 (CE editor), the closed-form RRR-16 base operator and v4 C3-U4 (state
supervision) on v5 confirm5 (v5 L cells). Panel (a) (schematic) is left to the lead."""
from _style import *
V5 = 'experiments/composability_mechanisms_v4/results/chains.csv'


def main():
    require_slurm(); ch = chains(V5); fig, axs = plt.subplots(1, 2, figsize=(7, 2.6))
    axs[0].text(.5, .5, '(a) schematic: decodable vs composable\n[TODO lead]', ha='center', va='center', fontsize=8); axs[0].axis('off')
    ax = axs[1]
    for stem, lab, c, ls in (('C1v1', 'C1 (CE, one-step)', '#9467bd', '-'), ('C3U4v4', 'C3-U4 (state-supervised, unrolled)', '#2ca02c', '-')):
        x = seed_median(ch, 'bart', 'month', stem, 'plus')
        if x: ax.plot(*x, c=c, ls=ls, label=f'{lab}, seed median')
    x = curve(ch, ('bart', 'month', 'F_empty', 'plus'))
    if x: ax.plot(*x, c='k', ls='--', label='RRR-16 (closed form)')
    ax.set_xlabel('chain length $k$'); ax.set_ylabel('$R_k$ (trajectory success)'); ax.set_ylim(-.03, 1.03); ax.set_title('(b) BART-base, month, one-way plus'); ax.legend(loc='center right')
    finish(fig, 'fig1', [V5])


if __name__ == '__main__':
    main()
