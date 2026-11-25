"""v8 locked analysis (CPU, after the lock; PLAN v7 C2, C3, B.3; operational rules in protocol.json). Reads the confirmation shards
(chains8.py), the pre-lock simulations (simulate8_<unit>_<bb>.json.gz: the slot-only primary predictor and U) and the pre-check decisions
recorded in the protocol. Writes results/predictions.json (N1-N5, Q24 per backbone and overall; G1-G6, Q25; ladder table, exploratory).
--self-test: runs the decision functions on synthetic inputs only (selftest8.py)."""
import gzip
from collections import defaultdict
import numpy as np
from symutil import *
import lcore

UNITS = dict(N=['bart', 't5'], G=['t5_9b'], L=['t5_bb', 't5_ll'])


# ---------------------------------------------------------------- per-cell world tables
def world_tab(recs, sim, n_steps):
    """Per world: pred = locked slot-only prediction; obs = trajectory success at the last step; naive = step-1 success;
    D1 = step-1 latent readout (simulation) != step-1 decoded state (None if unparsable)."""
    by = defaultdict(dict)
    for r in recs: by[r['world_id']][r['step']] = r
    ix = {w: i for i, w in enumerate(sim['world_ids'])}; out = {}
    for w, st in by.items():
        assert sorted(st) == list(range(1, n_steps + 1)), (w, n_steps); i = ix[w]; r1 = st[1]
        out[w] = dict(pred=bool(sim['pred']['slot'][i]), predU=bool(sim['pred']['U'][i]), obs=bool(st[n_steps]['trajectory_success']), naive=bool(r1['success']),
                      D1=None if r1['decoded_state'] is None else bool(sim['argmax'][i][0] != r1['decoded_state']),
                      R={t: bool(st[t]['trajectory_success']) for t in (1, 2)})
    return out


def summary(tab):
    s = lcore.cell_summary(tab); v = list(tab.values())
    s['R1'] = float(np.mean([x['R'][1] for x in v])); s['R2'] = float(np.mean([x['R'][2] for x in v])); s['world_agree_U'] = float(np.mean([x['predU'] == x['obs'] for x in v]))
    return s


def dedupe(sims):
    """Design rule 10: cells with identical latent trajectories (m and rho of the locked simulation) are counted once (first kept)."""
    seen = {}; groups = defaultdict(list)
    for k, s in sims.items():
        h = hash((json.dumps(s['m']), json.dumps(s['rho']), s['path'] if 'path' in s else k.rsplit('/', 1)[1])); seen.setdefault(h, k); groups[seen[h]].append(k)
    return {k for k in seen.values()}, {k: v for k, v in groups.items() if len(v) > 1}


# ---------------------------------------------------------------- decision rules (pure functions; self-tested)
def n1(r):
    return 'holds' if r >= .90 else 'opposing' if r <= .50 else 'mixed'


def n2(r):
    return 'H-transfer' if r >= .80 else 'H-no-transfer' if r <= .30 else 'mixed'


def editor_rule(R1, R2, Dm):
    return bool(R1 is not None and R2 is not None and Dm is not None and R1 >= .90 and R2 <= .20 and Dm >= .80)


def freeze_rule(obs, keep):
    """obs: {F1_plus, F1_alt, Fempty_alt, Fnot1_plus} observed R_2N; keep: {F1_plus, F1_alt, Fnot1_plus} -> bool (pre-check kept)."""
    tests = dict(F1_plus=lambda: obs['F1_plus'] <= .20, F1_alt=lambda: obs['F1_alt'] >= obs['Fempty_alt'] - .10, Fnot1_plus=lambda: obs['Fnot1_plus'] <= .10)
    res = {k: (tests[k]() if keep.get(k) else None) for k in tests}; kept = [v for v in res.values() if v is not None]
    return dict(conditions=res, holds=None if not kept else all(kept), evaluable=bool(kept))


def prediction_rule(agree, ci_lo, cat_acc):
    return bool(agree >= .85 and ci_lo > 0 and cat_acc >= .80)


def q24(n1v, n4, n5):
    if n1v != 'holds': return 'H-template-bound'
    return 'H-natural' if n4 is True and n5 is True else 'mixed'


def combine(vs):
    vs = list(vs); return vs[0] if vs and all(v == vs[0] for v in vs) else 'mixed (per backbone)'


def d_separation(cells):
    """G5 second part: editor cells (plus and minus paths): CE correct iff D >= 0.5, state-supervised correct iff D <= 0.20."""
    ok = [(c['D'] >= .5) if c['family'] == 'CE' else (c['D'] <= .20) for c in cells if c['D'] is not None]
    return dict(n=len(ok), frac=float(np.mean(ok)) if ok else None, holds=bool(ok) and float(np.mean(ok)) >= .90)


# ---------------------------------------------------------------- loading
def load_unit(unit, bb):
    import lib8
    sims = json.load(gzip.open(ROOT / f'results/simulate8_{unit if unit != "L" else "G"}_{bb}.json.gz', 'rt'))
    meta = read(ROOT / f'results/simulate8_{unit if unit != "L" else "G"}_{bb}_summary.json')['cells']; cells = {}
    for key, sim in sims.items():
        d, name, path = key.split('/'); recs = lib8.chain_records(bb, d, 'natural', name, f'{path}_from_start'); n = len(sim['states'][0])
        tab = world_tab(recs, sim, n); cells[key] = dict(meta[key], tab=tab, **summary(tab))
    return sims, cells


def pooled_pred(cells, keys):
    sel = {k: cells[k]['tab'] for k in keys}; wid, lat, nai = [], [], []
    for k, tab in sel.items():
        d = cells[k]['domain']
        for w, x in tab.items(): wid.append(f'{d}/{w}'); lat.append(x['pred'] == x['obs']); nai.append(x['naive'] == x['obs'])
    pl = lcore.pooled(sel); pl['latent_minus_naive'] = lcore.boot_diff_ci(wid, np.array(lat, float), np.array(nai, float))
    pl['U'] = float(np.mean([x['predU'] == x['obs'] for t in sel.values() for x in t.values()]))
    pl['category_accuracy'] = float(np.mean([cells[k]['cat_match'] for k in keys])); pl['n_cells'] = len(keys); return pl


def obs(cells, d, name, path):
    c = cells.get(f'{d}/{name}/{path}'); return None if c is None else c['obs_rate']


def editors_median(cells, d, prefix):
    cs = [c for k, c in cells.items() if k.startswith(f'{d}/{prefix}') and k.endswith('/plus')]
    if not cs: return None
    return dict(n=len(cs), R1=float(np.median([c['R1'] for c in cs])), R2=float(np.median([c['R2'] for c in cs])),
                D=float(np.median([c['D'] for c in cs if c['D'] is not None])) if any(c['D'] is not None for c in cs) else None, R2N=float(np.median([c['obs_rate'] for c in cs])))


# ---------------------------------------------------------------- units
def unit_n(p):
    out = dict(per_backbone={})
    for bb in UNITS['N']:
        sims, cells = load_unit('N', bb); keep, ident = dedupe(sims); d = 'month-nat'
        pre = p['prechecks'][f'dev8_N_{bb}']['N4/' + bb + '/' + d]
        r = dict(identical_groups=ident)
        r['N1'] = dict(R2N=obs(cells, d, 'nat_F_empty', 'plus'), verdict=n1(obs(cells, d, 'nat_F_empty', 'plus')))
        r['N2'] = dict(R2N=obs(cells, d, 'syn_F_empty', 'plus'), verdict=n2(obs(cells, d, 'syn_F_empty', 'plus')), descriptive=p['N2_descriptive'][bb])
        em = editors_median(cells, d, 'C1nat_'); r['N3'] = dict(em or {}, holds=editor_rule(em['R1'], em['R2'], em['D']) if em else None)
        fo = dict(F1_plus=obs(cells, d, 'nat_F_{1}', 'plus'), F1_alt=obs(cells, d, 'nat_F_{1}', 'alt'), Fempty_alt=obs(cells, d, 'nat_F_empty', 'alt'), Fnot1_plus=obs(cells, d, 'nat_F_not1', 'plus'))
        r['N4'] = dict(observed=fo, **freeze_rule(fo, {k: (v or {}).get('keep') for k, v in pre.items()}))
        ks = [k for k in keep if cells[k]['family'] != 'ref']; pl = pooled_pred(cells, ks)
        r['N5'] = dict(pl, holds=prediction_rule(pl['latent'], pl['latent_minus_naive']['ci95'][0], pl['category_accuracy']))
        r['Q24'] = q24(r['N1']['verdict'], r['N4']['holds'], r['N5']['holds']); r['reencode'] = obs(cells, d, 'reencode', 'plus')
        r['cells'] = {k: {kk: v for kk, v in c.items() if kk != 'tab'} for k, c in cells.items()}; out['per_backbone'][bb] = r
    out['Q24'] = combine(v['Q24'] for v in out['per_backbone'].values()); return out


def s_by_plane(bb, d, split):
    import lib8
    X = lib8.slot_matrix(bb, d, split); nxt = [lib8.S.advance(d, s, 'plus') for s in lib8.S.states(d)]
    return {k: float(((X[:, nxt] - X) @ B).norm(dim=-1).mean()) for k, B in lib8.planes(bb, d)}


def unit_g(p, bb='t5_9b', closed_only=False):
    sims, cells = load_unit('G' if not closed_only else 'L', bb); keep, ident = dedupe(sims); gp = read(ROOT / f'results/g_prep_{bb}.json'); r = dict(identical_groups=ident, domains={})
    for d in ('weekday', 'month'):
        if not gp['domains'][d].get('gate'): r['domains'][d] = dict(skipped='reconstruction gate'); continue
        x = r['domains'][d] = {}; rp = gp['domains'][d]['rstar_pred']; pre = p['prechecks'][f'dev8_G_{bb}']
        hi = obs(cells, d, 'F_empty' if rp == 16 else f'RRR{rp}', 'plus'); lo = obs(cells, d, f'RRR{rp - 2}', 'plus'); g2 = pre.get(f'G2/{bb}/{d}', {})
        tests = dict(hi=None if not (g2.get('hi') or {}).get('keep') or hi is None else hi >= .95, lo=None if not (g2.get('lo') or {}).get('keep') or lo is None else lo <= .50)
        kept = [v for v in tests.values() if v is not None]; x['G2'] = dict(rstar_pred=rp, hi=hi, lo=lo, tests=tests, holds=None if not kept else all(kept))
        fo = dict(F1_plus=obs(cells, d, 'F_{1}', 'plus'), F1_alt=obs(cells, d, 'F_{1}', 'alt'), Fempty_alt=obs(cells, d, 'F_empty', 'alt'), Fnot1_plus=obs(cells, d, 'F_not1', 'plus'))
        x['G3'] = dict(observed=fo, **freeze_rule(fo, {k: (v or {}).get('keep') for k, v in pre[f'G3/{bb}/{d}'].items()}))
        s = s_by_plane(bb, d, 'confirm7'); x['G4'] = dict(s=s, holds=min(s, key=s.get) == 1)
        grid = sorted(int(k.split('/')[1][3:]) for k in cells if k.startswith(f'{d}/RRR') and k.endswith('/plus'))
        x['rstar_observed'] = next((q for q in grid if obs(cells, d, f'RRR{q}', 'plus') >= .95), None)
        x['reencode'] = obs(cells, d, 'reencode', 'plus')
        if not closed_only:
            c1 = editors_median(cells, d, 'C1_'); x['G1'] = dict(c1 or {}, holds=editor_rule(c1['R1'], c1['R2'], c1['D']) if c1 else None)
            c3 = editors_median(cells, d, 'C3U4_'); x['G6'] = dict(c3 or {}, holds=None if not c3 else c3['R2N'] >= .95)
    ks = [k for k in keep if cells[k]['family'] != 'ref']; pl = pooled_pred(cells, ks)
    r['prediction'] = dict(pl, holds=prediction_rule(pl['latent'], pl['latent_minus_naive']['ci95'][0], pl['category_accuracy']))
    if not closed_only:
        ed = [dict(D=c['D'], family=c['family']) for k, c in cells.items() if k.split('/')[1].startswith(('C1_', 'C3U4_')) and not k.endswith('/alt')]
        sep = d_separation(ed); r['G5'] = dict(prediction=r['prediction'], D_separation=sep, holds=r['prediction']['holds'] and sep['holds'])
        doms = [v for v in r['domains'].values() if 'skipped' not in v]
        for g in ('G1', 'G2', 'G3', 'G4', 'G6'): r[g] = dict(holds=bool(doms) and all(v[g]['holds'] is True for v in doms), per_domain={d: v[g]['holds'] for d, v in r['domains'].items() if 'skipped' not in v})
        fails = [g for g in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6') if not r[g]['holds']]
        r['Q25'] = 'replicated on 9B-9B' if not fails else dict(not_holding=fails)
    r['cells'] = {k: {kk: v for kk, v in c.items() if kk != 'tab'} for k, c in cells.items()}
    return r


def main():
    require_slurm()
    if '--self-test' in sys.argv: import selftest8; return selftest8.main()
    p = read(ROOT / 'protocol.json'); assert p.get('locked') is True
    out = dict(N=unit_n(p), G=unit_g(p, 't5_9b'), ladder={bb: unit_g(p, bb, closed_only=True) for bb in UNITS['L']})
    dump(ROOT / 'results/predictions.json', out)
    print(json.dumps(dict(Q24=out['N']['Q24'], per_bb={bb: v['Q24'] for bb, v in out['N']['per_backbone'].items()}, Q25=out['G']['Q25']), default=str), flush=True)


if __name__ == '__main__':
    main()
