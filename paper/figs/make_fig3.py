"""Figure 3. (a) per-plane one-step change s_k and (a') amplitude a_k of the canonical slot code (v4 V0 cells: hour, compass8, season; both
backbones). (b) vote share of the fundamental by displacement m (v3 ERRATUM_01 section 2): with the locked plane weights lam_k (v4
protocol calibration) and the measured amplitudes a_k (v3 gate files), the share of plane 1 in the weighted distance between the codes
of x and x + m under the cyclic-symmetric approximation, lam_1 a_1^2 sin^2(pi m / N) / sum_k lam_k a_k^2 sin^2(pi k m / N); weekday and
month, both backbones."""
import numpy as np
from _style import *
P4 = 'experiments/composability_mechanisms_v3/results/predictions.json'; PR4 = 'experiments/composability_mechanisms_v3/protocol.json'
G3 = {bb: f'experiments/composability_mechanisms_v2/results/gates_{bb}.json' for bb in ('bart', 't5')}
NN = dict(weekday=7, month=12)


def main():
    require_slurm(); cells = read(P4)['V']['V0']['cells']; cal = read(PR4)['calib']; fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4))
    for key, v in cells.items():
        bb, d = key.split('/'); ks = sorted(v['s'], key=int); ls = {'hour': '-', 'compass8': '--', 'season': ':'}.get(d, '-')
        sm, am = max(v['s'].values()), max(v['a'].values())
        axs[0].plot([int(k) for k in ks], [v['s'][k] / sm for k in ks], c=BB_COL[bb], ls=ls, marker='o', ms=2.5, label=f'{BB_NAME[bb]} {d}')
        axs[1].plot([int(k) for k in ks], [v['a'][k] / am for k in ks], c=BB_COL[bb], ls=ls, marker='o', ms=2.5, label=f'{BB_NAME[bb]} {d}')
    for bb in ('bart', 't5'):
        amp = read(G3[bb])['amplitudes']
        for d, ls in (('weekday', '-'), ('month', '--')):
            N = NN[d]; lam = np.array(cal[bb][d]['models']['full']['lam']); a = np.array([amp[d][str(k)]['a'] for k in range(1, N // 2 + 1)]); ms = np.arange(1, N // 2 + 1)
            tot = lambda m: sum(lam[k - 1] * a[k - 1] ** 2 * np.sin(np.pi * k * m / N) ** 2 for k in range(1, N // 2 + 1))
            sh = [lam[0] * a[0] ** 2 * np.sin(np.pi * m / N) ** 2 / tot(m) for m in ms]
            axs[2].plot(ms, sh, c=BB_COL[bb], ls=ls, marker='o', ms=2.5, label=f'{BB_NAME[bb]} {d}')
    axs[0].set_xlabel('harmonic $k$'); axs[0].set_ylabel('$s_k / \max_j s_j$'); axs[0].set_title('(a) $s_1$ is the smallest'); axs[0].legend(fontsize=5)
    axs[1].set_xlabel('harmonic $k$'); axs[1].set_ylabel('$a_k / \max_j a_j$'); axs[1].set_title("(a') amplitude per plane")
    axs[2].set_xlabel('displacement $m$'); axs[2].set_ylabel('vote share of $k=1$'); axs[2].set_ylim(0, 1); axs[2].set_title('(b) fundamental share'); axs[2].legend(fontsize=5)
    finish(fig, 'fig3', [P4, PR4, *G3.values()])


if __name__ == '__main__':
    main()
