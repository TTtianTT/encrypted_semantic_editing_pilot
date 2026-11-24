"""Appendix figure S3 (v7 K, exploratory): distance between the slot and the clean encoding of the gold state, in slot radii R_w (median
over worlds), along 100 one-way plus steps on bind3, for each of the 8 Att2L-U8 seeds (seeds whose R_30 >= 0.90 solid, others dashed;
non-finite values omitted). From experiments/composability_mechanisms_v6/results/predictions.json (K exploratory contraction)."""
import numpy as np
from _style import *
P7 = 'experiments/composability_mechanisms_v6/results/predictions.json'


def main():
    require_slurm(); p = read(P7)['K']; r30 = p['table']['bind3/Att2LU8/R30']; fig, ax = plt.subplots(figsize=(3.6, 2.4))
    for s in range(42, 50):
        y = np.array([np.nan if v is None else v for v in p['exploratory'][f'contraction/Att2LU8_s{s}']], float)
        ax.plot(range(1, len(y) + 1), y, lw=.9, ls='-' if r30[str(s)] >= .9 else '--', label=f'seed {s}')
    ax.set_yscale('log'); ax.set_xlabel('step $t$'); ax.set_ylabel('distance to gold encoding / $R_w$'); ax.legend(fontsize=5, ncol=2)
    finish(fig, 'figS3', [P7])


if __name__ == '__main__':
    main()
