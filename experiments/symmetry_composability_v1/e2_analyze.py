"""E2 analysis (CPU): H-curv decision per seed at alpha = 1 on the S_perp residual; supplementary S and S_R."""
import time
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *

CTX = ('pre', 'post', 'transport', 'post_RRR')


def main():
    require_slurm(); t0 = time.time(); res = dict(per_seed={}, rule=dict(
        support='median_w KL_transport/KL_post >= 0.5 and median_w KL_transport/KL_pre >= 10 and median random transport KL <= 0.2 x median real transport KL',
        deny='median_w KL_transport/KL_post <= 0.2', overall='support/deny when >= 2 of 3 seeds agree; otherwise mixed'))
    all_rows = []
    for seed in SEEDS:
        rs = rows(ROOT / f'results/e2/s{seed}.jsonl'); all_rows += rs
        kl = defaultdict(dict); rnd = defaultdict(list); dist = defaultdict(dict); geo = []
        for r in rs:
            if r['component'] == 'base_distance_to_canonical':
                dist[r['context']][r['world_id']] = r['value']; continue
            if r['context'] == 'geometry':
                geo.append(r); continue
            k = (r['context'], r['component'], r['alpha'])
            if r['random_seed'] is None: kl[k][r['world_id']] = r['KL']
            else: rnd[k].append(r['KL'])
        ids = sorted(kl['pre', 'S_perp', 1.0])
        def ratio(a, b, comp='S_perp', alpha=1.0):
            return float(np.median([kl[a, comp, alpha][w] / max(kl[b, comp, alpha][w], 1e-12) for w in ids]))
        seedres = {}
        for comp in ('S_perp', 'S', 'S_R'):
            for alpha in (0.5, 1.0):
                med = {c: float(np.median([kl[c, comp, alpha][w] for w in ids])) for c in CTX}
                medr = {c: float(np.median(rnd[c, comp, alpha])) for c in CTX}
                seedres[f'{comp}_a{alpha}'] = dict(median_KL=med, median_random_KL=medr,
                    transport_over_post=ratio('transport', 'post', comp, alpha), transport_over_pre=ratio('transport', 'pre', comp, alpha),
                    post_over_pre=ratio('post', 'pre', comp, alpha), postRRR_over_transport=ratio('post_RRR', 'transport', comp, alpha),
                    random_over_real_transport=medr['transport'] / max(med['transport'], 1e-12))
        m = seedres['S_perp_a1.0']
        support = m['transport_over_post'] >= .5 and m['transport_over_pre'] >= 10 and m['random_over_real_transport'] <= .2
        deny = m['transport_over_post'] <= .2
        seedres['verdict'] = 'support' if support else 'deny' if deny else 'mixed'
        seedres['base_distance_to_canonical_median'] = {c: float(np.median(list(dist[c].values()))) for c in dist}
        seedres['canonical_subspace_energy_fraction'] = {k: boot_mean([g[k] for g in geo]) for k in ('e', 'S', 'S_perp')}
        seedres['canonical_subspace_dim_median'] = float(np.median([g['subspace_dim'] for g in geo]))
        res['per_seed'][seed] = seedres
    v = [res['per_seed'][s]['verdict'] for s in SEEDS]
    res['overall'] = 'support H-curv' if v.count('support') >= 2 else 'deny H-curv' if v.count('deny') >= 2 else 'mixed'
    res['note'] = 'Exploratory: the 80 operator_residual_v2 eval worlds were evaluated before.'
    res['seconds'] = time.time() - t0
    dump('results/e2_summary.json', res)
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for ax, seed in zip(axs, SEEDS):
        rs = [r for r in all_rows if r['seed'] == seed and r.get('component') == 'S_perp' and r['alpha'] == 1.0]
        for i, c in enumerate(CTX):
            real = [r['KL'] for r in rs if r['context'] == c and r['random_seed'] is None]
            rand = [r['KL'] for r in rs if r['context'] == c and r['random_seed'] is not None]
            ax.boxplot([real], positions=[i - .18], widths=.3, showfliers=False, patch_artist=True, boxprops=dict(facecolor='#3b6fb6'))
            ax.boxplot([rand], positions=[i + .18], widths=.3, showfliers=False, patch_artist=True, boxprops=dict(facecolor='#cccccc'))
        ax.set_xticks(range(len(CTX))); ax.set_xticklabels(CTX); ax.set_yscale('log'); ax.set_title(f"seed {seed}: {res['per_seed'][seed]['verdict']}", fontsize=9)
    axs[0].set_ylabel('KL(ref || ref + S_perp), alpha=1 (blue real, grey random)')
    fig.tight_layout(); fig.savefig(ROOT / 'figs/e2_visibility.png', dpi=150)
    print('E2', res['overall'], v, flush=True)


if __name__ == '__main__':
    main()
