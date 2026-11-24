"""Appendix figure S2 (v7 K): one-way plus R_k on bind3 (100 steps), name3 and bind3fix (30 steps) from the locked v7 shards
(experiments/composability_mechanisms_v6/results/shards_bart_<d>.tar.xz). Att2L-U8: every one of the 8 seeds (thin lines); Att2L-U4,
Att1-U8 and the oracle-routing OR-U8 (diagnostic): seed medians."""
import io
import tarfile
from collections import defaultdict
import numpy as np
from _style import *
TAR = {d: f'experiments/composability_mechanisms_v6/results/shards_bart_{d}.tar.xz' for d in ('bind3', 'name3', 'bind3fix')}


def curves(d):
    out = defaultdict(lambda: defaultdict(dict))
    with tarfile.open(REPO / TAR[d]) as t:
        for m in t.getmembers():
            if not m.isfile() or '_plus_from_start_' not in m.name or 'abl' in m.name: continue
            meth = m.name.split(f'chain_bart_{d}_natural_')[1].split('_plus_from_start')[0]
            for line in t.extractfile(m).read().decode().split('\n'):
                if line.strip(): r = json.loads(line); out[meth][r['world_id']][r['step']] = r['trajectory_success']
    R = {}
    for meth, ws in out.items():
        T = max(max(s) for s in ws.values()); R[meth] = (list(range(1, T + 1)), [float(np.mean([ws[w][t] for w in ws])) for t in range(1, T + 1)])
    return R


def main():
    require_slurm(); fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), gridspec_kw=dict(width_ratios=[2, 1, 1]), sharey=True)
    for ax, d in zip(axs, ('bind3', 'name3', 'bind3fix')):
        R = curves(d)
        for meth, (x, y) in sorted(R.items()):
            if meth.startswith('Att2LU8_s'): ax.plot(x, y, c='#17becf', lw=.7, alpha=.9, label='Att2L-U8 (each of 8 seeds)' if meth.endswith('s42') else None)
        for stem, c, ls, lab in (('Att2LU4', '#2ca02c', '-', 'Att2L-U4 (median)'), ('Att1U8', '#d62728', '-', 'Att1-U8 (median)'), ('ORU8', 'k', '--', 'OR-U8, oracle (median)')):
            ys = [y for m, (x, y) in R.items() if m.startswith(stem + '_s')]
            if ys: n = min(map(len, ys)); ax.plot(range(1, n + 1), np.median([y[:n] for y in ys], 0), c=c, ls=ls, lw=1.2, label=lab)
        ax.set_title(f'BART-base, {d}'); ax.set_xlabel('chain length $k$'); ax.set_ylim(-.03, 1.03)
    axs[0].set_ylabel('$R_k$ (one-way plus)'); h, l = axs[0].get_legend_handles_labels(); fig.tight_layout()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(.5, 0), ncol=4, frameon=False)
    finish(fig, 'figS2', list(TAR.values()))


if __name__ == '__main__':
    main()
