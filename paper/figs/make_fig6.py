"""Figure 6: latent prediction (locked fitted readout, no decoding) vs observed chain success per cell, both backbones (v5 L,
state-supervised cells), with the naive step-1 prediction. Equal-weight readout and the per-cell majority reference: v6 P1 (pending)."""
from _style import *
P5 = 'experiments/composability_mechanisms_v4/results/predictions.json'


def main():
    require_slurm(); C = read(P5)['L']['cells']; fig, axs = plt.subplots(1, 2, figsize=(7, 3.2), sharey=True)
    for ax, bb in zip(axs, ('bart', 't5')):
        cs = [v for k, v in C.items() if k.split('/')[1] == bb and v['family'] == 'state' and not v['new']]
        ax.scatter([v['obs_rate'] for v in cs], [v['naive_rate'] for v in cs], s=6, c='grey', alpha=.4, marker='.', label='naive (step-1 decode)')
        ax.scatter([v['obs_rate'] for v in cs], [v['pred_rate'] for v in cs], s=9, c=BB_COL[bb], alpha=.75, label=f'latent prediction ({len(cs)} cells)')
        ax.plot([0, 1], [0, 1], 'k:', lw=.6); ax.set_xlabel('observed $R_{2N}$'); ax.set_title(BB_NAME[bb]); ax.legend(loc='lower right')
    axs[0].set_ylabel('predicted $\\hat R_{2N}$')
    finish(fig, 'fig6', [P5])


if __name__ == '__main__':
    main()
