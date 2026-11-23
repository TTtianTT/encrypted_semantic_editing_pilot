"""Post-lock, descriptive only (not a locked source; DEVIATIONS post-lock #3). The locked analysis gives point values for some
prediction-table entries; REPORT §3 asks for a 95% CI on every observed value. This script adds, from the same confirm4 shards:
- Wilson 95% CIs (symutil.rate) for every success rate quoted in the table (V1, U1/U1b, X1/X2, S1, R exploratory);
- A.7 world cluster bootstrap CIs (2000 reps, seed 3101) for V2a/V2b (per-world A(1) - A(floor(N/2)) and reverse) and for S1
  (paired per-world R_10N(natural) - R_10N(sigma_max)).
No verdict is recomputed or changed. Output: results/report_ci.json."""
import analyze_svg  # noqa: F401  (patches rows() to split on '\n' only; DEVIATIONS post-lock #2)
import analyze
from analyze import R_at, recs, load_chains
from lib4 import *

SEEDS = (42, 43, 44)


def ci(x): return None if x is None else dict(rate=x['rate'], n=x['n'], ci95=x['ci95'])


def v2(bb, d, method, m_hi_first):
    N = len(S.states(d)); h = N // 2; per = {}
    for r in recs(bb, d, method, 'plus_from_start'):
        if r['step'] > 2 * N: continue
        m_ = disp_fold(r['state'], r['start'], N)
        if m_ in (1, h): per.setdefault(r['world_id'], {}).setdefault(m_, []).append(float(r['success']))
    ws = sorted(per); a1 = np.array([np.mean(per[w][1]) for w in ws]); ah = np.array([np.mean(per[w][h]) for w in ws])
    a, b = (a1, ah) if m_hi_first else (ah, a1)
    return boot_diff_ci(ws, a, b)


def main():
    require_slurm(); load_chains(); out = {}
    for bb in ('bart', 't5'):
        for d in ('weekday', 'month', 'hour', 'compass8'):
            k = f'{bb}/{d}'; N = len(S.states(d))
            out[f'V1/{k}'] = dict(plus=ci(R_at(bb, d, 'F_{1}', 'plus_from_start', 2 * N)), alt=ci(R_at(bb, d, 'F_{1}', 'alt_from_start', 2 * N)))
            out[f'V2a/{k}'] = v2(bb, d, 'F_{1}', True); out[f'V2b/{k}'] = v2(bb, d, 'F_not1', False)
    for v, doms in (('C1U4', ('weekday', 'month', 'compass')), ('C1UN', ('weekday', 'month')), ('C3U4', ('month',))):
        for d in doms:
            N = len(S.states(d))
            for s in SEEDS:
                x = R_at('bart', d, f'{v}_s{s}', 'plus_from_start', 2 * N)
                if x is not None: out[f'U/{v}/{d}/s{s}'] = dict(R_2N=ci(x), R_N=ci(R_at('bart', d, f'{v}_s{s}', 'plus_from_start', N)),
                                                                 R_4=ci(R_at('bart', d, f'{v}_s{s}', 'plus_from_start', 4)))
    for d in ('name3', 'bind3fix', 'bind3'):
        for kind in ('Att', 'Tok'):
            for s in SEEDS: out[f'X/{d}/{kind}_s{s}'] = dict(R_1=ci(R_at('bart', d, f'{kind}_s{s}', 'plus_from_start', 1)), R_6=ci(R_at('bart', d, f'{kind}_s{s}', 'plus_from_start', 6)))
        for name in ('RRR32', 'reencode'): out[f'X/{d}/{name}'] = dict(R_6=ci(R_at('bart', d, name, 'plus_from_start', 6)))
    for d in ('weekday', 'month'):
        N = len(S.states(d)); per = {}
        for mp in ('natural', 'scrmax'):
            out[f'S/{d}/{mp}'] = dict(R_2N=ci(R_at('t5', d, 'RRR32', 'longplus', 2 * N, mp)), R_10N=ci(R_at('t5', d, 'RRR32', 'longplus', 10 * N, mp)))
            per[mp] = {r['world_id']: float(r['trajectory_success']) for r in recs('t5', d, 'RRR32', 'longplus', mp) if r['step'] == 10 * N}
        ws = sorted(set(per['natural']) & set(per['scrmax']))
        out[f'S/{d}/diff'] = dict(boot_diff_ci(ws, np.array([per['natural'][w] for w in ws]), np.array([per['scrmax'][w] for w in ws])), worlds=len(ws))
    for bb in ('bart', 't5'):
        cells = read(ROOT / 'results/predictions.json')['R']['R1']['cells']
        for c in cells:
            if not c.startswith(bb): continue
            _, d, r = c.split('/'); N = len(S.states(d))
            out[f'R/{c}'] = dict(RRR=ci(R_at(bb, d, f'RRR{r[1:]}', 'plus_from_start', 2 * N)), FF=ci(R_at(bb, d, f'FF{r[1:]}', 'plus_from_start', 2 * N)))
    dump('results/report_ci.json', out); print(len(out), 'entries', flush=True)


if __name__ == '__main__':
    main()
