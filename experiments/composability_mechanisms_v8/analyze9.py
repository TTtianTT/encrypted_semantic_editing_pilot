"""v9 locked analysis (CPU, after the lock; PLAN v9 sections 3-5, operational rules in protocol.json). Reads the confirmation shards
(chains9.py), the locked simulations (sim9_<bb>_confirm.json.gz; step-1 readout for D), DO chains (do_run_<model>.json.gz) and DO
simulations (do_sim_<model>.json.gz), and the pre-check decisions of the protocol. Writes results/predictions.json."""
import csv
import gzip
from collections import defaultdict
from symutil import *
import lcore

BBS = ('bart', 't5')


def shard_tab(bb, d, name, path):
    import lib9
    by = defaultdict(dict)
    for r in lib9.chain_records(bb, d, 'natural', name, f'{path}_from_start'): by[r['world_id']][r['step']] = r
    return by


def R_at(by, k):
    return float(np.mean([st[k]['trajectory_success'] for st in by.values()])) if by else None


def D_of(by, sim):
    """Step-1 disagreement: among worlds with a parsable step-1 decode, the share whose locked step-1 readout differs from the decoded state."""
    ix = {w: i for i, w in enumerate(sim['world_ids'])}; v = [sim['argmax'][ix[w]][0] != st[1]['decoded_state'] for w, st in by.items() if st[1]['decoded_state'] is not None]
    return float(np.mean(v)) if v else None


def cellstats(bb, d, name, path, sim, N, extra=()):
    by = shard_tab(bb, d, name, path)
    if not by: return None
    out = dict(R1=R_at(by, 1), R2=R_at(by, 2), R2N=R_at(by, 2 * N), D=D_of(by, sim) if sim else None, worlds=len(by))
    for k in extra: out[f'R{k}'] = R_at(by, k) if max(len(s) for s in by.values()) >= k else None
    return out


def med(xs):
    xs = [x for x in xs if x is not None]; return float(np.median(xs)) if xs else None


def kept(pc, key, cond):
    x = (pc.get(key) or {}).get(cond); return True if x is None else bool(x.get('keep', not x.get('descriptive', False)))


def tri(v, hi, lo, H, O):
    return None if v is None else H if v >= hi else O if v <= lo else 'mixed'


def unit_b(p, bb):
    import gzip as gz
    sims = json.load(gz.open(ROOT / f'results/sim9_{bb}_confirm.json.gz', 'rt')); pc = p['prechecks'][bb]; out = {}
    S_ = lambda unit, d, name, path='plus': sims.get(f'{unit}/{d}/{name}/{path}')
    train = {part: p['train9'].get(f'{bb}_{part}', {}) for part in ('S', 'B2', 'B3', 'B4')}
    for d in ('weekday', 'month', 'month-nat'):
        N = 7 if d == 'weekday' else 12; r = {}
        g = cellstats(bb, d, 'RRR16' if d != 'month-nat' else 'SRRRnat', 'plus', None, N); r['G9_0'] = dict(R2N=g and g['R2N'], holds=bool(g and g['R2N'] >= .95))
        rot = cellstats(bb, d, 'Rot', 'plus', None, N)
        if rot: r['B5'] = dict(R2N=rot['R2N'], verdict=tri(rot['R2N'], .95, .50, 'H-sufficient', 'opposing'), descriptive=not kept(pc, f'B5/{d}', 'R2N'))
        if d == 'month-nat': out[d] = r; continue
        by = shard_tab(bb, d, 'B1a', 'plus'); r['B1a'] = dict(R1=R_at(by, 1), verdict=tri(R_at(by, 1), .80, .20, 'H-shift', 'H-cancel'), exploratory=not kept(pc, f'B1a/{d}', 'R1'))
        by = shard_tab(bb, d, 'B1b', 'plus'); x0 = 0
        r1x0 = float(np.mean([st[1]['trajectory_success'] for st in by.values() if st[1]['start'] == x0])) if by else None
        r1o = float(np.mean([st[1]['trajectory_success'] for st in by.values() if st[1]['start'] != x0])) if by else None
        conds = dict(R1_x0=(r1x0 is not None and r1x0 >= .80) if kept(pc, f'B1b/{d}', 'R1_x0') else None, R1_other=(r1o is not None and r1o <= .20) if kept(pc, f'B1b/{d}', 'R1_other') else None,
                     R2=(R_at(by, 2) <= .20) if kept(pc, f'B1b/{d}', 'R2') else None)
        kc = [v for v in conds.values() if v is not None]
        r['B1b'] = dict(R1_x0=r1x0, R1_other=r1o, R2=R_at(by, 2), conditions=conds, holds=None if not kc else all(kc), opposing=r1o is not None and r1o >= .50)
        c = cellstats(bb, d, 'B1c', 'plus', None, N); r['B1c'] = dict(R2N=c and c['R2N'], verdict=tri(c and c['R2N'], .90, .50, 'H-state-aware', 'opposing'), exploratory=not kept(pc, f'B1c/{d}', 'R2N'))
        def fam(unit, v, part, extra=()):
            res = {}
            for key, st in train[part].items():
                if not isinstance(st, dict) or key.startswith('_'): continue
                vv, dd, s = key.split('/')
                if vv != v or dd != d: continue
                res[s] = cellstats(bb, d, f'{v}_{s}', 'plus', S_(unit, d, f'{v}_{s}'), N, extra) if st.get('admitted') else dict(cannot_learn=True, R1=0.0, R2=0.0, R2N=0.0, D=None, **{f'R{k}': 0.0 for k in extra})
            return res
        lc1, lc3 = fam('B2', 'LoReFTC1', 'B2'), fam('B2', 'LoReFTC3U4', 'B2')
        m1 = {k: med([x.get(k) for x in lc1.values()]) for k in ('R1', 'R2', 'R2N', 'D')}; m3 = med([x.get('R2N') for x in lc3.values()])
        c1ok = m1['R1'] is not None and m1['R1'] >= .90 and (m1['R2'] <= .20 if kept(pc, f'LoReFTC1/{d}', 'R2') else True) and m1['D'] is not None and m1['D'] >= .80
        c3ok = (m3 is not None and m3 >= .95) if kept(pc, f'LoReFTC3U4/{d}', 'R2N') else None
        r['B2'] = dict(LoReFTC1=dict(seeds=lc1, median=m1), LoReFTC3U4=dict(seeds=lc3, median_R2N=m3), verdict='H-objective' if c1ok and c3ok is not False else 'H-param' if (m1['R2N'] or 0) >= .90 else 'mixed')
        b3 = {v: fam('B3', v, 'B3') for v in ('FullC1', 'MLPC1')}; mm = {v: {k: med([x.get(k) for x in s.values()]) for k in ('R2', 'R2N', 'D')} for v, s in b3.items()}
        obj = all((m['R2'] <= .20 if kept(pc, f'{v}/{d}', 'R2') else True) and m['D'] is not None and m['D'] >= .80 for v, m in mm.items())
        r['B3'] = dict(seeds=b3, median=mm, verdict='H-objective' if obj else 'H-capacity' if any((m['R2N'] or 0) >= .90 for m in mm.values()) else 'mixed')
        b4 = {}
        for v, hz in (('U8', 10), ('U16', 18), ('Urand', None)):
            ss = fam('B4', v, 'B4', extra=(hz, 4 * N) if hz else (4 * N,))
            if not ss: continue
            k = f'R{hz}' if hz else f'R{4 * N}'
            b4[v] = dict(seeds=ss, stat=k, admitted=[s for s, x in ss.items() if not x.get('cannot_learn')],
                         median_admitted=med([x.get(k) for x in ss.values() if not x.get('cannot_learn')]), median_all=med([x.get(k) for x in ss.values()]),
                         R4N_max=max([x.get(f'R{4 * N}') or 0 for x in ss.values()]))
        for x in b4.values():                                        # DEVIATIONS 5: admitted editors only; < 2 admitted -> descriptive
            x['descriptive'] = len(x['admitted']) < 2; x['cannot_learn_rate'] = 1 - len(x['admitted']) / len(x['seeds'])
            x['R4N_max_admitted'] = max([x['seeds'][s].get(f'R{4 * N}') or 0 for s in x['admitted']], default=None)
        dec = [x for x in b4.values() if not x['descriptive']]
        verdict = 'descriptive' if not dec else 'H-state' if any((x['R4N_max_admitted'] or 0) >= .90 for x in dec) else 'H-counter' if all(x['median_admitted'] <= .50 for x in dec) else 'mixed'
        r['B4'] = dict(editors=b4, verdict=verdict, rule='admitted editors only; variants with fewer than 2 admitted editors descriptive (DEVIATIONS 5)')
        if d in ('weekday', 'month') and (bb == 'bart' or d == 'month'):
            c1, c3 = fam('S', 'C1', 'S'), fam('S', 'C3U4', 'S')
            n1 = sum(1 for x in c1.values() if x['R1'] >= .90 and x['R2'] <= .20); n3 = sum(1 for x in c3.values() if x['R2N'] >= .95)
            r['S'] = dict(C1=dict(seeds=c1, passing=n1, holds=n1 >= 4), C3U4=dict(seeds=c3, passing=n3, holds=n3 >= 4), v5_seeds=v5_seeds(bb, d))
        out[d] = r
    return out


def v5_seeds(bb, d):
    """v5's seeds 42-44 (one-way plus, month / weekday template 0; v5 L cells, chains.csv) for the 8-seed min / max report."""
    R = defaultdict(dict); f = EXP / 'composability_mechanisms_v4/results/chains.csv'
    with open(f) as fh:
        for row in csv.DictReader(fh):
            if row['backbone'] == bb and row['domain'] == d and row['path'].startswith('plus'): R[row['method']][int(row['t'])] = float(row['R_t'])
    c1 = 'C1v1' if bb == 'bart' else 'C1v3'; c3 = 'C3U4v4' if bb == 'bart' else 'C3U4n'; N = 7 if d == 'weekday' else 12
    pick = lambda stem, k: {m: v.get(k) for m, v in R.items() if m.startswith(stem + '_s')}
    return dict(C1_R1=pick(c1, 1), C1_R2=pick(c1, 2), C3U4_R2N=pick(c3, 2 * N))


def unit_do(p, model):
    prep = read(ROOT / f'results/do_prep_{model}.json'); runs = json.load(gzip.open(ROOT / f'results/do_run_{model}.json.gz', 'rt'))
    sims = json.load(gzip.open(ROOT / f'results/do_sim_{model}.json.gz', 'rt')); pc = read(ROOT / f'results/do_sim_{model}_summary.json')['precheck']; out = {}
    for d, r in prep['domains'].items():
        if r.get('skipped'): out[d] = dict(skipped=r['skipped']); continue
        split = 'confirm8' if d == 'month-nat' else 'confirm7'; N = 7 if d == 'weekday' else 12; cells = {}
        for key, run in runs.items():
            sp, dd, name, path = key.split('/')
            if dd != d or sp != split: continue
            sim = sims[key]; ix = {w: i for i, w in enumerate(sim['world_ids'])}; ok = run['ok']; wid = run['world_ids']
            pred = [all(a == g for a, g in zip(sim['argmax'][ix[w]], sim['states'][ix[w]])) for w in wid]; obs = [o[-1] for o in ok]
            Dv = [sim['argmax'][ix[w]][0] != dc for w, dc in zip(wid, run['decoded_step1']) if dc is not None]
            cells[f'{name}/{path}'] = dict(R1=float(np.mean([o[0] for o in ok])), R2=float(np.mean([o[1] for o in ok])), R2N=float(np.mean(obs)), D=float(np.mean(Dv)) if Dv else None,
                                         tab={w: dict(pred=pv, obs=ov, naive=o[0]) for w, pv, ov, o in zip(wid, pred, obs, ok)})
        rp = r['rstar_pred']; P = pc[d]; g = lambda name, path='plus': (cells.get(f'{name}/{path}') or {}).get('R2N')
        do1a = g(f'SRRR{rp}'); do1b = g(f'SRRR{rp - 2}')
        c2 = dict(F1_plus=(g('F_{1}') <= .20) if P['DO2_F1_plus']['keep'] else None, F1_alt=(g('F_{1}', 'alt') >= g('F_empty', 'alt') - .10) if P['DO2_F1_alt']['keep'] else None,
                  Fnot1_plus=(g('F_not1') <= .10) if P['DO2_Fnot1_plus']['keep'] else None); k2 = [v for v in c2.values() if v is not None]
        X = load(ROOT / f'local/do_{model}_{d}_{split}.pt')['latents']; Pl = load(ROOT / f'local/do_{model}_{d}_srrr.pt')['planes']; nxt = [(s + 1) % N for s in range(N)]
        s = {k: float(((X[:, nxt] - X) @ B.double()).norm(dim=-1).mean()) for k, B in Pl}
        ed = lambda v, k: med([c[k] for n, c in cells.items() if n.startswith(f'{v}_') and n.endswith('/plus')])
        do4 = dict(R1=ed('C1', 'R1'), R2=ed('C1', 'R2'), D=ed('C1', 'D')); do4['holds'] = bool(do4['R1'] is not None and do4['R1'] >= .90 and (do4['R2'] <= .20 if P['DO4_R2']['keep'] else True) and (do4['D'] or 0) >= .80)
        do5 = ed('C3U4', 'R2N')
        tabs = {n: c['tab'] for n, c in cells.items()}; wid, lat, nai = [], [], []
        for n, t in tabs.items():
            for w, x in t.items(): wid.append(f'{n}|{w}'.split('|')[1]); lat.append(x['pred'] == x['obs']); nai.append(x['naive'] == x['obs'])
        ci = lcore.boot_diff_ci(wid, np.array(lat, float), np.array(nai, float)); cat = float(np.mean([lcore.category(float(np.mean([x['pred'] for x in t.values()]))) == lcore.category(float(np.mean([x['obs'] for x in t.values()]))) for t in tabs.values()]))
        do6 = dict(agreement=float(np.mean(lat)), naive=float(np.mean(nai)), ci=ci['ci95'], category_accuracy=cat, holds=bool(np.mean(lat) >= .85 and ci['ci95'][0] > 0 and cat >= .80))
        res = dict(DO1a=dict(rstar_pred=rp, R2N=do1a, holds=bool(do1a is not None and do1a >= .95), exploratory=not P['DO1a']['keep']),
                   DO1b=dict(R2N=do1b, holds=bool(do1b is not None and do1b <= .50), secondary=True, exploratory=not P['DO1b']['keep']),
                   DO2=dict(observed=dict(F1_plus=g('F_{1}'), F1_alt=g('F_{1}', 'alt'), Fempty_alt=g('F_empty', 'alt'), Fnot1_plus=g('F_not1')), conditions=c2, holds=None if not k2 else all(k2)),
                   DO3=dict(s=s, holds=min(s, key=s.get) == 1), DO4=do4, DO5=dict(R2N=do5, holds=(do5 is not None and do5 >= .95) if P['DO5']['keep'] else None), DO6=do6,
                   cells={n: {k: v for k, v in c.items() if k != 'tab'} for n, c in cells.items()})
        prim = [res['DO1a']['holds'] if not res['DO1a']['exploratory'] else True, res['DO2']['holds'], res['DO3']['holds'], res['DO4']['holds'], res['DO5']['holds'], res['DO6']['holds']]
        res['replicates'] = all(x is not False for x in prim) and all(x is not None for x in prim[1:3]); out[d] = res
    return out


def main():
    require_slurm(); p = read(ROOT / 'protocol.json'); assert p.get('locked') is True
    do_models = ['gemma'] + [m for m in [p.get('do2_model')] if m]
    out = dict(B={bb: unit_b(p, bb) for bb in BBS}, DO={m: unit_do(p, m) for m in do_models}, B6={bb: read(ROOT / f'results/chains9_{bb}_complete.json')['B6'] for bb in BBS})
    out['G9_0'] = all(v['G9_0']['holds'] for bb in BBS for v in out['B'][bb].values())
    rep = lambda m: (lambda ev: bool(ev) and all(v.get('replicates', False) for v in ev))([v for v in out['DO'][m].values() if 'skipped' not in v])   # no evaluable combination -> not replicated
    out['DO_replicates'] = {m: rep(m) for m in do_models}; out['DO_both_replicate'] = len(do_models) == 2 and all(rep(m) for m in do_models)
    dump(ROOT / 'results/predictions.json', out); print(json.dumps(dict(G9_0=out['G9_0'], DO=out['DO_both_replicate'])), flush=True)


if __name__ == '__main__':
    main()
