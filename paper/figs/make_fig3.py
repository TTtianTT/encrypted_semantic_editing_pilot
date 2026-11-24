"""Figure 3(a): per-plane amplitude a_k and one-step change s_k of the canonical slot code (v4 V0 cells: hour, compass8, season; both
backbones). Panel (b) (vote share by displacement) pending."""
from _style import *
P4 = 'experiments/composability_mechanisms_v3/results/predictions.json'


def main():
    require_slurm(); cells = read(P4)['V']['V0']['cells']; fig, axs = plt.subplots(1, 2, figsize=(7, 2.6))
    for key, v in cells.items():
        bb, d = key.split('/'); ks = sorted(v['s'], key=int); ls = {'hour': '-', 'compass8': '--', 'season': ':'}.get(d, '-')
        axs[0].plot([int(k) for k in ks], [v['s'][k] for k in ks], c=BB_COL[bb], ls=ls, marker='o', ms=2.5, label=f'{BB_NAME[bb]} {d}')
        axs[1].plot([int(k) for k in ks], [v['a'][k] for k in ks], c=BB_COL[bb], ls=ls, marker='o', ms=2.5, label=f'{BB_NAME[bb]} {d}')
    axs[0].set_xlabel('harmonic $k$'); axs[0].set_ylabel('one-step change $s_k$'); axs[0].set_title('(a) $s_1$ is the smallest'); axs[0].legend(fontsize=5.5)
    axs[1].set_xlabel('harmonic $k$'); axs[1].set_ylabel('amplitude $a_k$'); axs[1].set_title('(a\') amplitude per plane')
    finish(fig, 'fig3', [P4])


if __name__ == '__main__':
    main()
