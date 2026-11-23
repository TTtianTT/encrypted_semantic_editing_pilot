"""P1 (CPU, exploratory; PLAN 4): reproduce the lead's post-hoc analysis of v4 with the L-unit analysis code (lcore.py) on v4's V shards
(experiments/composability_mechanisms_v3/results/shards). Per world the latent prediction uses the locked fitted vote model's argmax on
the actual latent slot (recorded by v4 as argmax_full); the idealized prediction is v4's locked derived category.
Targets (PLAN 1.1.2): 131/150 vs 92/150; per-world 0.933/0.934; naive 0.706/0.653; cell-majority reference 0.896/0.905;
hour: idealized 19/20 wrong, readout agreement 0.941/0.912.
Definitions (found by this reproduction, DEVIATIONS pre-lock): category counts over the 150 non-empty freeze cells; per-world agreement,
naive and majority reference pooled over all 180 cells including F_empty; hour 'idealized 20 cells' = the V3 cells (F{j}, j >= 2, plus and
minus, both backbones); hour 'readout agreement' = per-step agreement of the latent readout with the parsable decoded state (V4 metric)."""
from collections import defaultdict
from symutil import *
import lcore

V4DIR = EXP / 'composability_mechanisms_v3'
N = dict(weekday=7, month=12, hour=12, compass8=8, season=4)
TARGET = dict(cat_latent=131, cat_ideal=92, cells=150, world=dict(bart=.933, t5=.934), naive=dict(bart=.706, t5=.653), majority=dict(bart=.896, t5=.905),
              hour_ideal_wrong=19, hour_ideal_cells=20, hour_readout=dict(bart=.941, t5=.912))


def main():
    require_slurm(); p4 = read(V4DIR / 'protocol.json'); sh = V4DIR / 'results/shards'; cells = defaultdict(dict); out = dict(cells={}); step_agree = defaultdict(list)
    for bb in ('bart', 't5'):
        for d in N:
            for cond in p4['calib'][bb][d]['derived']:
                if d == 'season' and cond == 'F_{2}': continue      # season: F{2} is F{not 1}, run once
                for path, pk in (('plus_from_start', 'plus'), ('minus_from_start', 'minus'), ('alt_from_start', 'alt')):
                    recs = [r for f in sorted(sh.glob(f'chain_{bb}_{d}_natural_{cond}_{path}_*.jsonl')) for r in rows(f)]
                    assert recs, (bb, d, cond, path)
                    tab = lcore.world_table(recs, 2 * N[d]); s = lcore.cell_summary(tab)
                    s['ideal_cat'] = p4['calib'][bb][d]['derived'][cond]['category'][pk]; s['ideal_match'] = s['ideal_cat'] == s['obs_cat']
                    key = f'{bb}/{d}/{cond}/{pk}'; out['cells'][key] = s; cells[bb][key] = tab
                    for r in recs:
                        if r['decoded_state'] is not None: step_agree[bb, d, cond == 'F_empty'].append(r['argmax_full'] == r['decoded_state'])
    C = out['cells']; ne = {k: c for k, c in C.items() if '/F_empty/' not in k}
    hour_v3 = {k: c for k, c in ne.items() if '/hour/F_{' in k and not k.endswith('/alt') and k.split('/')[2] != 'F_{1}'}
    sa = lambda bb, d, incl: float(np.mean([v for (b, dd, e), x in step_agree.items() if b == bb and dd == d and (incl or not e) for v in x]))
    out['summary'] = dict(
        n_cells_nonempty=len(ne), cat_latent=sum(c['cat_match'] for c in ne.values()), cat_ideal=sum(c['ideal_match'] for c in ne.values()),
        per_backbone_all180={bb: lcore.pooled(cells[bb], boot=lcore.boot_diff_ci) for bb in cells},
        per_backbone_nonempty150={bb: lcore.pooled({k: v for k, v in cells[bb].items() if '/F_empty/' not in k}, boot=lcore.boot_diff_ci) for bb in cells},
        hour_v3cells=dict(cells=len(hour_v3), ideal_wrong=sum(not c['ideal_match'] for c in hour_v3.values())),
        hour_all=dict(cells=sum(1 for k in ne if '/hour/' in k), ideal_wrong=sum(1 for k, c in ne.items() if '/hour/' in k and not c['ideal_match'])),
        hour_step_readout={bb: dict(nonempty=sa(bb, 'hour', False), incl_empty=sa(bb, 'hour', True)) for bb in cells},
        hour_world_agree={bb: lcore.pooled({k: v for k, v in cells[bb].items() if '/hour/' in k})['latent'] for bb in cells})
    s = out['summary']; pb = s['per_backbone_all180']; r3 = lambda x: round(x, 3)
    chk = dict(cells=s['n_cells_nonempty'] == TARGET['cells'], cat_latent=s['cat_latent'] == TARGET['cat_latent'], cat_ideal=s['cat_ideal'] == TARGET['cat_ideal'],
               world={bb: r3(pb[bb]['latent']) == TARGET['world'][bb] for bb in pb}, naive={bb: r3(pb[bb]['naive']) == TARGET['naive'][bb] for bb in pb},
               majority={bb: r3(pb[bb]['majority_reference']) == TARGET['majority'][bb] for bb in pb},
               hour_ideal=(s['hour_v3cells']['cells'], s['hour_v3cells']['ideal_wrong']) == (TARGET['hour_ideal_cells'], TARGET['hour_ideal_wrong']),
               hour_readout={bb: r3(s['hour_step_readout'][bb]['nonempty']) == TARGET['hour_readout'][bb] or r3(s['hour_step_readout'][bb]['incl_empty']) == TARGET['hour_readout'][bb] for bb in pb})
    out['target'] = TARGET; out['check'] = chk
    out['reproduced'] = bool(all(v if isinstance(v, bool) else all(v.values()) for v in chk.values()))
    dump('results/patch/p1_posthoc.json', out)
    print(json.dumps(dict(summary={k: v for k, v in s.items()}, check=chk, reproduced=out['reproduced']), indent=1, default=str), flush=True)


if __name__ == '__main__':
    main()
