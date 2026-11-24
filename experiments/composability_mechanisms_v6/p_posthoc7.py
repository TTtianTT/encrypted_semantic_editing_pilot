"""P (CPU, exploratory, before the lock; PLAN B3). Reads the decoded shards of v5 L (experiments/composability_mechanisms_v4/results/
shards) and v6 M / C (experiments/composability_mechanisms_v5/results/shards); writes results/patch/p_posthoc7.json and the frozen R case
list data/r_cases.json (P3). The recorded argmaxes in these shards equal the locked simulations (0 mismatches in v5 and v6).

Cells: every state-supervised cell (v5 L family != CE; v6 M family 'state'; every v6 C cell). Identical cells (same editor weights,
as listed by the v6 analysis) are removed first and only the first of each group is counted (design rule 10).
P1: per (source, backbone, domain, editor family): over-estimates (predicted success, observed failure), under-estimates, precision of a
    predicted failure P(obs fail | pred fail) and of a predicted success.
P2: first failure of a world whose slot readout is still correct at that step ('slot right, decode wrong'): decoded state = previous gold
    state (prev), = chain start (start), both coincide (prev_eq_start: step 1 and the odd steps of alternating chains), another state
    (other) or unparsable. Reported per (source, backbone, domain, family, path).
P3: R cases (B6). R-A: v6 M, F_empty alternating chains, first 'slot right, decode wrong' failure (all; T5Gemma month-mt primary, BART
    multi-template secondary). R-B: v6 C, BART month, editor families C3v1, C3l3v3, C3l10v3, P2b, C3n900: first failures of that kind whose
    decoded state is the previous gold state; stratified by (seed, path), 100 per family (all if fewer). Controls: per case one successful
    step of another world of the same cell, |step difference| <= 2. Sampling rng seed 3101."""
import hashlib
import json
import random
import re
from collections import defaultdict, Counter
from symutil import *

V5DIR = EXP / 'composability_mechanisms_v4'; V6DIR = EXP / 'composability_mechanisms_v5'
NN = dict(weekday=7, month=12, compass=4, hour=12, compass8=8, season=4, **{'weekday-mt': 7, 'month-mt': 12, 'hour-mt': 12})
RB_FAM = ('C3v1', 'C3l3v3', 'C3l10v3', 'P2b', 'C3n900')
TARGET = dict(P1=dict(pred_fail_precision_range=(.91, .98), t5_mt_over_under=(482, 27), C_over_to_under=(4, 6), bart_mt='over ~ under'),
              P2=dict(bart_month_undertrained_prev=(.76, .93), F1_oneway_mt_start=(.26, .59), t5_Fempty_alt_unparsable=.61),
              P3=dict(RA_t5=69, RA_bart=56, RB=500))


def recs_of(sh, bb, d, method, path):
    return [r for f in sorted(sh.glob(f'chain_{bb}_{d}_natural_{method}_{path}_from_start_*.jsonl')) for r in rows(f)]


def family(method):
    return re.sub(r'_s\d+$', '', method)


def by_world(rs, n):
    by = defaultdict(dict)
    for r in rs:
        if r['step'] <= n: by[r['world_id']][r['step']] = r
    for w, st in by.items(): assert sorted(st) == list(range(1, n + 1)), (w, n)
    return by


def cells():
    """(source, bb, d, method, path, shard dir) for every state-supervised cell."""
    out = []
    for key, c in read(V5DIR / 'results/predictions.json')['L']['cells'].items():
        _, bb, d, m, p = key.split('/')
        if c['family'] != 'CE': out.append(('v5L', bb, d, m, p, V5DIR / 'results/shards'))
    for bb in ('bart', 't5'):
        for key, c in read(V6DIR / f'results/simulate_{bb}_summary.json')['cells'].items():
            if c['unit'] == 'M' and c['family'] == 'state': out.append(('v6M', bb, c['domain'], c['method'], c['path'], V6DIR / 'results/shards'))
            if c['unit'] == 'C': out.append(('v6C', bb, c['domain'], c['method'], c['path'], V6DIR / 'results/shards'))
    return out


def main():
    require_slurm(); out = dict(target=TARGET); data = {}; dup = []
    # identical editors (same weights): v6 analysis list, detected on the continuous context drift of the locked simulation (v6 DEVIATIONS
    # #11). Decoded records cannot detect them: different editors with perfect chains give identical records.
    same = {}
    for g in read(V6DIR / "results/predictions.json")["C"]["exploratory"]["identical_cells"]:
        rep = min(g, key=lambda k: (0 if "/C3v1_" in k else 1, k))      # keep the named v1 C3 (PLAN B6) as the representative
        for k in g:
            if k != rep: same[k] = rep
    for src, bb, d, m, p, sh in cells():
        k6 = f"C/{bb}/{d}/{m}/{p}"
        if src == "v6C" and k6 in same: dup.append([k6, same[k6]]); continue
        rs = recs_of(sh, bb, d, m, p); assert rs, (src, bb, d, m, p); data[src, bb, d, m, p] = by_world(rs, 2 * NN[d])
    out['duplicates_removed'] = dup
    # ---- P1
    P1 = defaultdict(lambda: Counter())
    for (src, bb, d, m, p), by in data.items():
        n = 2 * NN[d]
        for w, st in by.items():
            pred = all(st[t]['argmax_full'] == st[t]['state'] for t in st); obs = bool(st[n]['trajectory_success'])
            P1[src, bb, d, family(m)][('pp' if pred else 'pf') + ('o' if obs else 'x')] += 1
    def summ(c):
        over, under = c['ppx'], c['pfo']; pf = c['pfx'] + c['pfo']; pp = c['ppo'] + c['ppx']
        return dict(worlds=sum(c.values()), over=over, under=under, prec_pred_fail=c['pfx'] / pf if pf else None, prec_pred_success=c['ppo'] / pp if pp else None,
                    pred_fail=pf, pred_success=pp)
    out['P1'] = {'/'.join(k): summ(c) for k, c in sorted(P1.items())}
    agg = defaultdict(Counter)
    for (src, bb, d, f), c in P1.items(): agg[src, bb, d].update(c); agg[src, bb, 'all'].update(c)
    out['P1_by_domain'] = {'/'.join(k): summ(c) for k, c in sorted(agg.items())}
    # ---- P2
    P2 = defaultdict(Counter); cases = []
    for (src, bb, d, m, p), by in data.items():
        for w, st in by.items():
            t = next((t for t in sorted(st) if not st[t]['success']), None)
            if t is None or st[t]['argmax_full'] != st[t]['state']: continue
            r = st[t]; prev = st[t - 1]['state'] if t > 1 else r['start']; dec = r['decoded_state']
            k = ('unparsable' if dec is None else 'prev_eq_start' if dec == prev == r['start'] else 'prev' if dec == prev else 'start' if dec == r['start'] else 'other')
            P2[src, bb, d, family(m), p][k] += 1
            cases.append(dict(source=src, backbone=bb, domain=d, method=m, family=family(m), path=p, world_id=w, step=t, start=r['start'], gold=r['state'],
                              prev_gold=prev, decoded_state=dec, decoded_word=r.get('decoded_word'), argmax_full=r['argmax_full'], kind_first_failure=k))
    out['P2'] = {'/'.join(k): dict(n=sum(c.values()), **{x: c[x] / sum(c.values()) for x in ('prev', 'start', 'prev_eq_start', 'other', 'unparsable')}, counts=dict(c))
                 for k, c in sorted(P2.items())}
    # ---- P3
    rng = random.Random(3101); R = []
    RA = [c for c in cases if c['source'] == 'v6M' and c['method'] == 'F_empty' and c['path'] == 'alt']
    for c in RA: R.append(dict(c, group='R-A-t5' if c['backbone'] == 't5' else 'R-A-bart', role='case'))
    for fam in RB_FAM:
        pool = [c for c in cases if c['source'] == 'v6C' and c['backbone'] == 'bart' and c['domain'] == 'month' and c['family'] == fam and c['decoded_state'] == c['prev_gold']]
        strata = defaultdict(list)
        for c in sorted(pool, key=lambda c: (c['method'], c['path'], c['world_id'])): strata[c['method'], c['path']].append(c)
        pick = []
        if len(pool) <= 100: pick = list(pool)
        else:
            keys = sorted(strata); quota = {k: 0 for k in keys}; left = 100
            while left:                                               # round-robin over strata until 100 are allocated
                for k in keys:
                    if left and quota[k] < len(strata[k]): quota[k] += 1; left -= 1
            for k in keys: pick += rng.sample(strata[k], quota[k])
        for c in pick: R.append(dict(c, group=f'R-B-{fam}', role='case'))
    ctrl = []
    for c in R:
        by = data[c['source'], c['backbone'], c['domain'], c['method'], c['path']]
        opts = sorted((w, t) for w, st in by.items() if w != c['world_id'] for t, r in st.items() if abs(t - c['step']) <= 2 and r['success'])
        assert opts, c; w, t = rng.choice(opts); r = by[w][t]
        ctrl.append(dict(source=c['source'], backbone=c['backbone'], domain=c['domain'], method=c['method'], family=c['family'], path=c['path'], world_id=w, step=t,
                         start=r['start'], gold=r['state'], prev_gold=by[w][t - 1]['state'] if t > 1 else r['start'], decoded_state=r['decoded_state'],
                         decoded_word=r.get('decoded_word'), argmax_full=r['argmax_full'], kind_first_failure=None, group=c['group'], role='control'))
    allc = R + ctrl
    for i, c in enumerate(allc): c['case_id'] = f"{c['group']}/{c['role']}/{i:04d}"
    dump(ROOT / 'data/r_cases.json', dict(rule='PLAN B6; p_posthoc7.py P3; rng seed 3101', cases=allc))
    out['P3'] = dict(counts={g: dict(Counter(c['role'] for c in allc if c['group'] == g)) for g in sorted({c['group'] for c in allc})},
                     RB_pool={fam: sum(1 for c in cases if c['source'] == 'v6C' and c['backbone'] == 'bart' and c['domain'] == 'month' and c['family'] == fam
                                       and c['decoded_state'] == c['prev_gold']) for fam in RB_FAM},
                     r_cases_sha256=sha(ROOT / 'data/r_cases.json'))
    out['cells'] = len(data)
    dump(ROOT / 'results/patch/p_posthoc7.json', out); print('cells', len(data), 'duplicates', len(dup), out['P3'], flush=True)


if __name__ == '__main__':
    main()
