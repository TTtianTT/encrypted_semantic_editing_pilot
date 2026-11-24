"""P (CPU, exploratory, before the lock; PLAN B3). Outputs results/patch/p1_posthoc6.json and inputs_manifest.json.
P0: SHA256 manifest of every v1-v5 input v6 reads (data, caches, planes, fits, editors, protocols, calibrations).
P1a: on v5's L shards (experiments/composability_mechanisms_v4/results/shards; the recorded argmaxes equal v5's locked simulation, 0
     mismatches), per-world agreement and category accuracy of the latent prediction with the fitted (full), equal-weight and
     fundamental-only readouts, and of the naive prediction; scopes: v5 report scope (state family, existing editors; 243 / 201 cells) and
     every non-CE cell incl. new editors (288 / 207 cells).
P1b: the per-cell majority reference (every world predicted as the cell's observed majority outcome) on both scopes.
P1c: v5's D shards (decoupled freeze D_S): per-step readout agreement (fitted model vs parsable decoded state), per-world agreement and
     category matches of the latent prediction.
P1d: BART month, not-converged state editors (v1 C3, v3 C3-l3 / l10, v4 P2b; 3 seeds): type of the first failure per world (another
     state / unparsable) and whether the slot readout is still correct at that step; per path.
Targets (the lead's post-hoc analysis in conversation) are recorded with the observed values; differences are reported, not blocking."""
from collections import defaultdict, Counter
from symutil import *
import lcore

V1D = EXP / 'symmetry_composability_v1'; V3DIR = EXP / 'composability_mechanisms_v2'; V4DIR = EXP / 'composability_mechanisms_v3'; V5DIR = EXP / 'composability_mechanisms_v4'
SH = V5DIR / 'results/shards'
NN = dict(weekday=7, month=12, compass=4, hour=12, compass8=8, season=4)
TARGET = dict(P1a_all_nonCE=dict(world=dict(full=(.931, .959), equal=(.897, .945), fund=(.736, .695), naive=(.630, .641)),
                                  category=dict(full=(.892, .913), equal=(.858, .903), fund=(.615, .599)), cells=(288, 207)),
              P1c=dict(step_full_range=(.83, .99), world=.927, category=(130, 144)),
              P1d=dict(plus_first_fail_all_other_state=True, plus_slot_still_correct_range=(103, 158), plus_failed_range=(128, 160), minus_alt_slot_correct_range=(31, 144)))


def recs_of(bb, d, method, path):
    return [r for f in sorted(SH.glob(f'chain_{bb}_{d}_natural_{method}_{path}_from_start_*.jsonl')) for r in rows(f)]


def manifest():
    pats = [(V5DIR, ['data/*/worlds.jsonl', 'data/*.json', 'protocol.json', 'results/calib_mt_*.json', 'results/gates_mt_*.json', 'results/train_new_*.json',
                     'local/*-mt_train_*', 'local/*-mt_dev_*', 'local/planes_*-mt.pt', 'local/*_rrr_*-mt_natural_base.pt', 'local/n_bart_C3n*', 'local/b_*', 'local/*_R_*_v5.pt']),
            (V4DIR, ['protocol.json', 'data/slot_positions.json', 'results/u_train.json', 'results/x_train.json', 'local/p2_*_month_*', 'local/u_C3U4_month_*',
                     'local/bart_bind3*_train_*', 'local/bart_bind3*_dev_*', 'local/bart_name3_train_*', 'local/bart_name3_dev_*', 'local/bart_rrr_*_natural_base.pt',
                     'local/bart_R_*.pt', 'data/bind3*/worlds.jsonl', 'data/name3/worlds.jsonl']),
            (V3DIR, ['protocol.json', 'data/slot_positions.json', 'local/a_C3_*_month_*', 'local/planes_bart_weekday.pt', 'local/planes_bart_month.pt', 'results/calib_bart.json']),
            (V1D, ['local/e1_C3_*_0600.pt', 'local/e1_weekday_train_*', 'local/e1_weekday_dev_*', 'local/e1_month_train_*', 'local/e1_month_dev_*', 'data/weekday/worlds.jsonl', 'data/month/worlds.jsonl'])]
    files = {}
    for D, ps in pats:
        for p in ps:
            for f in sorted(D.glob(p)):
                if f.is_file(): files[str(f.relative_to(REPO))] = dict(sha256=sha(f), bytes=f.stat().st_size)
    return files


def main():
    require_slurm(); p5 = read(V5DIR / 'results/predictions.json'); out = dict(target=TARGET)
    files = manifest(); dump('inputs_manifest.json', dict(files=files, n=len(files), bytes=sum(v['bytes'] for v in files.values())))
    out['P0'] = dict(files=len(files), bytes=sum(v['bytes'] for v in files.values()))
    # ---- P1a / P1b
    cells = defaultdict(dict)
    for key, c in p5['L']['cells'].items():
        _, bb, d, method, path = key.split('/')
        if c['family'] == 'CE': continue
        rs = recs_of(bb, d, method, path); assert rs, key; n = 2 * NN[d]
        for lat in ('full', 'equal', 'fund'): cells[bb, 'all_nonCE', lat][key] = lcore.world_table(rs, n, f'argmax_{lat}')
        if not c['new']:
            for lat in ('full', 'equal', 'fund'): cells[bb, 'report', lat][key] = lcore.world_table(rs, n, f'argmax_{lat}')
    P1a = {}
    for (bb, scope, lat), cs in cells.items():
        po = lcore.pooled(cs, boot=lcore.boot_diff_ci); cat = float(np.mean([lcore.cell_summary(t)['cat_match'] for t in cs.values()]))
        P1a.setdefault(scope, {}).setdefault(bb, {})[lat] = dict(cells=len(cs), world=po['latent'], category=cat, naive=po['naive'], majority_reference=po['majority_reference'],
                                                                  latent_minus_naive=po.get('latent_minus_naive'))
    out['P1a'] = P1a; out['P1b'] = {scope: {bb: v['full']['majority_reference'] for bb, v in d_.items()} for scope, d_ in P1a.items()}
    # ---- P1c
    step = defaultdict(list); tabs = defaultdict(dict)
    for key, c in p5['D']['cells'].items():
        bb, d, Sname, path = key.split('/'); rs = recs_of(bb, d, f'D_{Sname}', path); assert rs, key
        tabs[bb][key] = lcore.world_table(rs, 2 * NN[d])
        for r in rs:
            if r['decoded_state'] is not None: step[bb, r['step']].append(r['argmax_full'] == r['decoded_state'])
    out['P1c'] = {bb: dict(cells=len(t), world=lcore.pooled(t)['latent'], category=sum(lcore.cell_summary(x)['cat_match'] for x in t.values()),
                           step_agreement={str(s): float(np.mean(v)) for (b, s), v in sorted(step.items()) if b == bb}) for bb, t in tabs.items()}
    allt = {f'{bb}/{k}': v for bb, t in tabs.items() for k, v in t.items()}
    out['P1c']['pooled'] = dict(cells=len(allt), world=lcore.pooled(allt)['latent'], category=sum(lcore.cell_summary(x)['cat_match'] for x in allt.values()),
                                step_range=[min(float(np.mean(v)) for v in step.values()), max(float(np.mean(v)) for v in step.values())])
    # ---- P1d
    P1d = {}
    for name in [f'{v}_s{s}' for v in ('C3v1', 'C3l3v3', 'C3l10v3', 'P2b') for s in (42, 43, 44)]:
        for path in ('plus', 'minus', 'alt'):
            rs = recs_of('bart', 'month', name, path); by = defaultdict(dict)
            for r in rs: by[r['world_id']][r['step']] = r
            c = Counter()
            for w, st in by.items():
                ff = next((t for t in sorted(st) if not st[t]['success']), None)
                if ff is None or ff > 24: continue
                r = st[ff]; c['failed'] += 1; c['unparsable' if r['decoded_state'] is None else 'other_state'] += 1; c['slot_still_correct'] += r['argmax_full'] == r['state']
            P1d[f'{name}/{path}'] = dict(c)
    out['P1d'] = P1d
    pl = [v for k, v in P1d.items() if k.endswith('/plus')]; ma = [v for k, v in P1d.items() if not k.endswith('/plus')]
    out['P1d_summary'] = dict(plus_unparsable=sum(v.get('unparsable', 0) for v in pl), plus_slot_correct_range=[min(v.get('slot_still_correct', 0) for v in pl), max(v.get('slot_still_correct', 0) for v in pl)],
                              plus_failed_range=[min(v.get('failed', 0) for v in pl), max(v.get('failed', 0) for v in pl)],
                              minus_alt_slot_correct_range=[min(v.get('slot_still_correct', 0) for v in ma), max(v.get('slot_still_correct', 0) for v in ma)],
                              alt_unparsable=sum(v.get('unparsable', 0) for k, v in P1d.items() if k.endswith('/alt')))
    r3 = lambda x: round(x, 3); a = P1a['all_nonCE']
    out['comparison'] = dict(P1a_cells=(a['bart']['full']['cells'], a['t5']['full']['cells']),
                             P1a_world={lat: (r3(a['bart'][lat]['world']), r3(a['t5'][lat]['world'])) for lat in ('full', 'equal', 'fund')} | dict(naive=(r3(a['bart']['full']['naive']), r3(a['t5']['full']['naive']))),
                             P1a_category={lat: (r3(a['bart'][lat]['category']), r3(a['t5'][lat]['category'])) for lat in ('full', 'equal', 'fund')},
                             P1c=dict(world=r3(out['P1c']['pooled']['world']), category=(out['P1c']['pooled']['category'], out['P1c']['pooled']['cells']), step_range=[r3(x) for x in out['P1c']['pooled']['step_range']]))
    dump('results/patch/p1_posthoc6.json', out); print(json.dumps(dict(comparison=out['comparison'], P1b=out['P1b'], P1d=out['P1d_summary']), indent=1, default=str), flush=True)


if __name__ == '__main__':
    main()
