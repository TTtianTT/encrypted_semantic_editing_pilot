"""Analysis (CPU): G3-0, H (HS1-HS6, HV1, Q5), B' (Q2'), N (Q6), T (T0-T6), A (H-weight / H-conflict / A3); tables and figures.
Every unit is evaluated independently; a unit whose results are missing is reported as 'not run'."""
import math
import time
from collections import Counter, defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from lib3 import *
import lib3

PATHS = ('plus_from_start', 'minus_from_start', 'alt_from_start')


def recs(bb, d, mp, me, path):
    by = defaultdict(dict)
    for r in chain_records(bb, d, mp, me, path): by[r['world_id']][r['step']] = r
    return by


def R(bb, d, mp, me, path, k):
    by = recs(bb, d, mp, me, path)
    if not by: return None
    return rate([by[w][k]['trajectory_success'] for w in by])


def A(bb, d, mp, me, path):
    by = recs(bb, d, mp, me, path); T = max(max(v) for v in by.values())
    return [float(np.mean([by[w][t]['success'] for w in by])) for t in range(1, T + 1)]


def single(bb, d, mp, me):
    ok = [r['score']['success'] for f in sorted(lib3.SHARDS.glob(f'single_{bb}_{d}_{mp}_{me}_s*.jsonl')) for r in rows(f)]
    return rate(ok) if ok else None


def cat(x): return None if x is None else category(x['rate'] if isinstance(x, dict) else x)


def safe(fn, *a):
    try: return fn(*a)
    except Exception as e: return dict(status='not run', error=f'{type(e).__name__}: {e}')


def h_unit(p, bb='bart', doms=CYC):
    out = {}; N = {d: len(S.states(d)) for d in doms}; cal = p['calib'][bb]
    R2N = {d: {} for d in doms}
    for d in doms:
        for f in sorted(lib3.SHARDS.glob(f'chain_{bb}_{d}_natural_*_plus_from_start_000.jsonl')):
            me = f.name[len(f'chain_{bb}_{d}_natural_'):-len('_plus_from_start_000.jsonl')]
            if me.startswith(('C1', 'C3', 'reencode')): continue   # other units' chains in the same domains
            R2N[d][me] = {pn: R(bb, d, 'natural', me, pn, 2 * N[d]) for pn in PATHS}
    out['R_2N'] = {d: {me: {pn: v['rate'] for pn, v in x.items()} for me, x in R2N[d].items()} for d in doms}
    hs1 = {d: R2N[d]['F_{1}']['plus_from_start']['rate'] for d in doms}
    out['HS1'] = dict(observed=hs1, pass_=all(v <= .2 for v in hs1.values()))
    two = [d for d in ('weekday', 'month') if d in doms]
    hs2 = {d: R2N[d]['F_{1}']['alt_from_start']['rate'] for d in two}
    out['HS2'] = dict(observed=hs2, frozen=all(v >= .8 for v in hs2.values()), drift=all(v <= .2 for v in hs2.values()))
    hs3 = {}
    for d in two:
        a = A(bb, d, 'natural', 'F_{1}', 'plus_from_start'); hs3[d] = dict(A_N=a[N[d] - 1], A_half=a[math.ceil(N[d] / 2) - 1])
    out['HS3'] = dict(observed=hs3, frozen=all(v['A_N'] >= .8 and v['A_half'] <= .3 for v in hs3.values()), drift=all(v['A_N'] <= .3 for v in hs3.values()))
    out['frozen_plane'] = out['HS1']['pass_'] and out['HS2']['frozen'] and out['HS3']['frozen']
    # HS4
    rows4 = {}
    for d in doms:
        obs = cat(R2N[d]['F_not1']['plus_from_start']); vote = cal[d]['derived']['F_not1']['category']['plus']
        rows4[d] = dict(observed=obs, R_2N=R2N[d]['F_not1']['plus_from_start']['rate'], fund='composable', complete='fail', vote=vote,
                        fund_vote_same=vote == 'composable')
    cnt = {h: sum(r['observed'] == r[h] for r in rows4.values()) for h in ('fund', 'complete', 'vote')}
    full = [h for h, c in cnt.items() if c == len(doms)]
    out['HS4'] = dict(per_domain=rows4, matches=cnt, winner=full[0] if len(full) == 1 else ('tie:' + '+'.join(full) if full else 'none'))
    # HS5
    cells = {}
    for d in doms:
        for k, _ in planes(bb, d):
            if k >= 2:
                obs = cat(R2N[d][f'F_{{{k}}}']['plus_from_start'])
                cells[f'{d}/F{{{k}}}'] = dict(observed=obs, R_2N=R2N[d][f'F_{{{k}}}']['plus_from_start']['rate'], vote=cal[d]['derived'][f'F_{{{k}}}']['category']['plus'])
    m5 = dict(fund=sum(c['observed'] == 'composable' for c in cells.values()), complete=sum(c['observed'] == 'fail' for c in cells.values()),
              vote=sum(c['observed'] == c['vote'] for c in cells.values()))
    need = math.ceil(7 / 9 * len(cells))
    out['HS5'] = dict(cells=cells, matches=m5, n=len(cells), pass_={h: v >= need for h, v in m5.items()}, threshold=f'>= {need}/{len(cells)}')
    # HS6
    hs6 = {}
    for d in doms:
        Ks = cal[d]['Kstar']; Nd = N[d]
        if Ks['dim'] >= Nd - 1: continue
        ok_gate = all(v['rate'] >= .9 for v in R2N[d]['E_all'].values())
        ek = 'E_Kstar' if 'E_Kstar' in R2N[d] else ('E_{1}' if Ks['K'] == [1] else 'E_all')
        rr = [m for m in R2N[d] if m.startswith(f"RRR{Ks['dim']}_dimKstar")]
        hold = all(v['rate'] >= .9 for v in R2N[d][ek].values()) and (R2N[d][rr[0]]['plus_from_start']['rate'] <= .2 if rr else False)
        hs6[d] = dict(evaluable=ok_gate, holds=hold if ok_gate else None, E_Kstar={k: v['rate'] for k, v in R2N[d][ek].items()},
                      RRR_dimK=R2N[d][rr[0]]['plus_from_start']['rate'] if rr else None, K=Ks['K'], dim=Ks['dim'])
    ev = [v for v in hs6.values() if v['evaluable']]
    out['HS6'] = dict(per_domain=hs6, pass_=(sum(v['holds'] for v in ev) >= .75 * len(ev)) if ev else None, applicable=len(hs6), evaluable=len(ev))
    # HV1
    agree = {m: [] for m in ('full', 'equal', 'fund')}
    for d in doms:
        conflict = [m for m in R2N[d] if (m.startswith('F_') and m != 'F_empty') or m in ('E_{1}', 'E_Kstar')]
        for me in conflict:
            for pn in PATHS:
                for w, steps in recs(bb, d, 'natural', me, pn).items():
                    for r in steps.values():
                        if r['decoded_state'] is None: continue
                        for m in agree: agree[m].append(r[f'argmax_{m}'] == r['decoded_state'])
    ag = {m: float(np.mean(v)) for m, v in agree.items()}
    nd = max(ag['equal'], ag['fund']) >= .95
    out['HV1'] = dict(agreement=ag, n=len(agree['full']), pass_=(ag['full'] >= .85 and ag['full'] >= ag['equal'] + .05 and ag['full'] >= ag['fund'] + .05),
                      not_discriminating=nd)
    hs45 = (out['HS4']['winner'], {h for h, v in out['HS5']['pass_'].items() if v})
    if not out['frozen_plane']:
        q5 = 'H-drift' if out['HS2']['drift'] and out['HS3']['drift'] else 'frozen-plane not established (mixed)'
    elif hs45[0] == 'vote' and 'vote' in hs45[1] and out['HV1']['pass_']: q5 = 'H-vote'
    elif hs45[0] == 'fund' and 'fund' in hs45[1] and ag['full'] <= ag['fund']: q5 = 'H-fund'
    elif hs45[0] == 'complete' and 'complete' in hs45[1]: q5 = 'H-complete'
    else: q5 = 'mixed'
    out['Q5'] = q5
    out['A_t'] = {f'{d}/{me}': A(bb, d, 'natural', me, 'plus_from_start') for d in doms for me in R2N[d]}
    out['model_A_t'] = {}
    for d in doms:
        for me in ('F_{1}', 'F_not1', 'E_Kstar', 'F_empty'):
            by = recs(bb, d, 'natural', me, 'plus_from_start')
            if by: out['model_A_t'][f'{d}/{me}'] = [float(np.mean([by[w][t]['argmax_full'] == by[w][t]['state'] for w in by])) for t in range(1, 2 * N[d] + 1)]
    return out


def b_unit(p):
    out = {}; doms = p['gates']['bart']['B_domains']
    r6 = {d: {me: R('bart', d, 'natural', me, 'plus_from_start', 6) for me in ('RRR16', 'RRR32')} for d in doms}
    out['B1p'] = dict(observed={d: r6[d]['RRR16'] for d in ('pron3', 'name3')}, pass_=all(r6[d]['RRR16']['rate'] >= .95 for d in ('pron3', 'name3')))
    mx = lambda d: max(r6[d]['RRR16']['rate'], r6[d]['RRR32']['rate'])
    b2, b2b = mx('bind3'), mx('bind3fix'); out['B2p'] = dict(observed=b2, R16=r6['bind3']['RRR16'], R32=r6['bind3']['RRR32'])
    out['B2bp'] = dict(observed=b2b, R16=r6['bind3fix']['RRR16'], R32=r6['bind3fix']['RRR32'])
    b3 = {f'{d}/s{s}': R('bart', d, 'natural', f'C1_s{s}', 'plus_from_start', 2) for d in doms for s in SEEDS}
    out['B3p'] = dict(observed={k: v['rate'] for k, v in b3.items()}, pass_=all(v['rate'] <= .2 for v in b3.values()))
    dl = p['gates']['bart']['B4p_delta']; out['B4p'] = dict(delta=dl, verdict='H-bind' if dl <= -.3 else 'H-geom' if abs(dl) < .1 else 'neither', prospective=False)
    if not out['B1p']['pass_']: q = 'not decidable (pipeline)'
    elif b2 <= .5 and b2b >= .95: q = 'H-bind'
    elif b2 >= .95 and b2b >= .95: q = 'H-geom'
    elif b2 <= .5 and b2b <= .5: q = 'H-list'
    else: q = 'mixed'
    out['Q2p'] = q
    kinds = Counter()
    for w, steps in recs('bart', 'bind3', 'natural', 'RRR16', 'plus_from_start').items():
        bad = [t for t in sorted(steps) if not steps[t]['success']]
        if not bad: continue
        r = steps[bad[0]]; wd = r['decoded_word']; ppl = [x.lower() for x in next(x for x in worlds3('bind3', 'confirm3') if x['world_id'] == w)['people']]
        prev = steps[bad[0] - 1]['state'] if bad[0] > 1 else r['start']
        kinds['unparsable' if wd is None else 'source_name' if wd == ppl[prev] else 'other_listed' if wd in ppl else
              'pronoun' if wd in ('me', 'you', 'them') else 'outside_name'] += 1
    out['bind3_first_failure_output'] = dict(kinds)
    out['extra'] = {f'{d}/{me}': dict(R30=(R('bart', d, 'natural', me, 'plus_from_start', 30) or {}).get('rate'), single=(single('bart', d, 'natural', me) or {}).get('rate'))
                    for d in doms for me in ('RRR16', 'RRR32', 'reencode', 'C1_s42', 'C1_s43', 'C1_s44')}
    return out


def n_unit(p):
    ev = read(ROOT / 'results/n_eval.json'); tr = read(ROOT / 'results/n_train.json'); out = dict(admission={k: v for k, v in tr.items() if k.count('/') == 2})
    maps = [('weekday', 'scrmax'), ('month', 'scrmax'), ('compass', 'scrmax')]
    cells = {f'{d}/{mp}/s{s}': ev[f'{d}/{mp}/s{s}'] for d, mp in maps for s in SEEDS if 'M1' in ev.get(f'{d}/{mp}/s{s}', {})}
    m1 = float(np.median([c['M1']['mean'] for c in cells.values()])) if cells else None
    out['N1'] = dict(median_M1=m1, consistent=m1 is not None and m1 <= .6, unexplained=m1 is not None and m1 >= .9)
    r2 = {f'{d}/{mp}': float(np.median([ev[f'{d}/{mp}/s{s}']['R2']['rate'] for s in SEEDS if 'R2' in ev.get(f'{d}/{mp}/s{s}', {})] or [np.nan])) for d, mp in maps}
    n2 = 'H-state' if sum(v >= .5 for v in r2.values()) >= 2 else 'H-token' if sum(v <= .2 for v in r2.values()) >= 2 else 'neither'
    out['N2'] = dict(seed_median_R2=r2, verdict=n2)
    tgt = float(np.median([c['M3']['target'] for c in cells.values()])); src = float(np.median([c['M3']['source'] for c in cells.values()]))
    n3 = 'H-state' if tgt >= .5 else 'H-token' if src >= .8 else 'neither'
    out['N3'] = dict(median_target=tgt, median_source=src, verdict=n3)
    out['Q6'] = n2 if n2 == n3 and n2 != 'neither' else 'mixed'
    out['cells'] = {k: dict(M1=v['M1']['mean'], M2=v['M2']['median'], M3=v['M3'], R1=v['R1']['rate'], R2=v['R2']['rate'], M4=v.get('M4'),
                            cos_with_natural_C1=v.get('cos_with_natural_C1')) for k, v in ev.items() if isinstance(v, dict) and 'M1' in v}
    out['probe_dev_accuracy'] = {k: v['dev_accuracy'] for k, v in ev.items() if k.endswith('/probe')}
    return out


def t_unit(p, h_bart):
    out = {}; g = p['gates']['t5']; RANKS = {'weekday': [4, 5, 6, 7, 16, 32], 'month': [9, 10, 11, 12, 16, 32], 'compass': [2, 3, 4, 16]}
    N = {d: len(S.states(d)) for d in T_DOMAINS}
    t0 = {}
    for d in g['T_rrr_domains']:
        a = R('t5', d, 'natural', 'RRR16', 'plus_from_start', 2 * N[d]); b = R('t5', d, 'natural', 'RRR32', 'plus_from_start', 2 * N[d]) if 32 in RANKS[d] else None
        t0[d] = dict(R16=a['rate'], R32=b['rate'] if b else None, pass_=max(a['rate'], b['rate'] if b else 0) >= .95)
    out['T0'] = t0; ev_d = [d for d, v in t0.items() if v['pass_']]
    c1 = {f'{d}/s{s}': dict(R1=R('t5', d, 'natural', f'C1_s{s}', 'plus_from_start', 1)['rate'], R2=R('t5', d, 'natural', f'C1_s{s}', 'plus_from_start', 2)['rate'])
          for d in g['T_domains'] for s in SEEDS}
    out['T1'] = dict(cells=c1, pass_=all(v['R1'] >= .9 and v['R2'] <= .2 for v in c1.values()))
    te = read(ROOT / 'results/t_eval_c1.json'); cl = [v for k, v in te.items() if '/C1_s' in k]
    m1 = float(np.median([c['M1']['mean'] for c in cl])); m2 = float(np.median([c['M2']['median'] for c in cl]))
    ms = float(np.median([c['M3']['source'] for c in cl])); mt = float(np.median([c['M3']['target'] for c in cl]))
    out['T2'] = dict(M1=m1, M2=m2, M3_source=ms, M3_target=mt, probe_dev_accuracy={k: v['dev_accuracy'] for k, v in te.items() if k.endswith('/probe')},
                     verdict='H-instr' if m1 >= .9 and abs(m2) <= .2 and ms >= .8 else 'H-approx' if (m1 <= .6 or m2 >= .5 or mt >= .8) else 'neither')
    t3 = {}; tab = {}
    for d in g['T_rrr_domains']:
        tab[d] = {r: dict(R_2N=R('t5', d, 'natural', f'RRR{r}', 'plus_from_start', 2 * N[d])['rate'], single=single('t5', d, 'natural', f'RRR{r}')['rate']) for r in RANKS[d]}
        if d not in ev_d: t3[d] = dict(evaluable=False); continue
        rs = sorted(tab[d]); okr = [r for r in rs if all(tab[d][q]['R_2N'] >= .95 for q in rs if q >= r)]; rst = min(okr) if okr else None
        below = [r for r in rs if rst is not None and r < rst]; sharp = tab[d][max(below)]['R_2N'] <= .2 if below else True
        t3[d] = dict(evaluable=True, r_star=rst, N_minus_1=N[d] - 1, sharp=sharp, pass_=rst is not None and N[d] - 2 <= rst <= N[d] and sharp)
    out['T3'] = dict(per_domain=t3, rank_table=tab, pass_=all(v['pass_'] for v in t3.values() if v.get('evaluable')))
    t4 = {d: tab[d][N[d] - 2]['single'] for d in ('weekday', 'month') if d in tab}
    out['T4'] = dict(observed=t4, pass_=all(v >= .95 for v in t4.values()) if t4 else None)
    t5 = {}
    for d in ('weekday', 'month'):
        if d not in ev_d: continue
        s16 = R('t5', d, 'scrmax', 'RRR16', 'plus_from_start', 2 * N[d])['rate']; s32 = R('t5', d, 'scrmax', 'RRR32', 'plus_from_start', 2 * N[d])['rate']
        dl = R('t5', d, 'natural', 'RRR16', 'longplus', 10 * N[d])['rate'] - R('t5', d, 'scrmax', 'RRR16', 'longplus', 10 * N[d])['rate']
        t5[d] = dict(scr_R2N=max(s16, s32), diff_R10N=dl, pass_=max(s16, s32) >= .95 and dl <= .05)
    out['T5'] = dict(per_domain=t5, pass_=all(v['pass_'] for v in t5.values()) if t5 else None)
    ht = safe(h_unit_t5, p, ev_d)
    out['T6_surgery'] = ht
    if isinstance(ht, dict) and 'HS1' in ht:
        out['T6'] = dict(HS1=ht['HS1']['pass_'], HS2=ht['HS2']['frozen'], HV1=ht['HV1']['pass_'], HS4_winner=ht['HS4']['winner'],
                         bart_HS4_winner=h_bart.get('HS4', {}).get('winner'))
        out['T6']['pass_'] = out['T6']['HS1'] and out['T6']['HS2'] and out['T6']['HV1'] and out['T6']['HS4_winner'] == out['T6']['bart_HS4_winner']
    return out


def h_unit_t5(p, doms):
    """Reduced H analysis for the T5Gemma surgery set (F_empty, F{1}, F_not1, E_all, E_Kstar)."""
    out = {}; N = {d: len(S.states(d)) for d in doms}; cal = p['calib']['t5']
    R2N = {d: {me: {pn: R('t5', d, 'natural', me, pn, 2 * N[d])['rate'] for pn in PATHS} for me in ('F_empty', 'F_{1}', 'F_not1', 'E_all', 'E_Kstar')
               if recs('t5', d, 'natural', me, 'plus_from_start')} for d in doms}
    out['R_2N'] = R2N
    out['HS1'] = dict(observed={d: R2N[d]['F_{1}']['plus_from_start'] for d in doms}, pass_=all(R2N[d]['F_{1}']['plus_from_start'] <= .2 for d in doms))
    two = [d for d in ('weekday', 'month') if d in doms]
    out['HS2'] = dict(observed={d: R2N[d]['F_{1}']['alt_from_start'] for d in two}, frozen=bool(two) and all(R2N[d]['F_{1}']['alt_from_start'] >= .8 for d in two))
    rows4 = {d: dict(observed=category(R2N[d]['F_not1']['plus_from_start']), vote=cal[d]['derived']['F_not1']['category']['plus']) for d in doms}
    cnt = dict(fund=sum(r['observed'] == 'composable' for r in rows4.values()), complete=sum(r['observed'] == 'fail' for r in rows4.values()),
               vote=sum(r['observed'] == r['vote'] for r in rows4.values()))
    full = [h for h, c in cnt.items() if c == len(doms)]
    out['HS4'] = dict(per_domain=rows4, matches=cnt, winner=full[0] if len(full) == 1 else ('tie:' + '+'.join(full) if full else 'none'))
    agree = {m: [] for m in ('full', 'equal', 'fund')}
    for d in doms:
        for me in ('F_{1}', 'F_not1', 'E_Kstar'):
            for pn in PATHS:
                for w, steps in recs('t5', d, 'natural', me, pn).items():
                    for r in steps.values():
                        if r['decoded_state'] is None: continue
                        for m in agree: agree[m].append(r[f'argmax_{m}'] == r['decoded_state'])
    ag = {m: float(np.mean(v)) if v else None for m, v in agree.items()}
    out['HV1'] = dict(agreement=ag, pass_=ag['full'] is not None and ag['full'] >= .85 and ag['full'] >= ag['equal'] + .05 and ag['full'] >= ag['fund'] + .05,
                      not_discriminating=max(ag['equal'] or 0, ag['fund'] or 0) >= .95)
    return out


def a_unit(p):
    ev = read(ROOT / 'results/a_eval.json'); out = {}
    def r(d, name):
        if d == 'month': return R('bart', d, 'natural', name, 'plus_from_start', 24)['rate']
        return R('bart', d, 'natural', name, 'plus_from_two', 7)['rate']
    var = ['C3_l1_v1', 'C3_l3', 'C3_l10', 'C3_rrrinit']
    tab = {f'{d}/{v}/s{s}': dict(R=r(d, f'{v}_s{s}'), R12=R('bart', d, 'natural', f'{v}_s{s}', 'plus_from_start', 12)['rate'] if d == 'month' else None,
                                 DRIFT=ev[f'{d}/{v}_s{s}']['algebra']['plus']['DRIFT'], k1=1 in ev[f'{d}/{v}_s{s}']['algebra']['plus']['harmonics_present'],
                                 adjacent_cos=ev[f'{d}/{v}_s{s}']['adjacent_write_cos']['mean']) for d in ('month', 'daysago') for v in var for s in SEEDS}
    out['table'] = tab
    med = lambda d, v, k: float(np.median([tab[f'{d}/{v}/s{s}'][k] for s in SEEDS]))
    hw = med('month', 'C3_l10', 'R') >= .9 and med('daysago', 'C3_l10', 'R') >= .9
    rrr_drift = {d: harmonics_of(*editor_factors('rrr', load(V2DIR / f'local/rrr_{d}_natural.pt')['plus', 16], 'plus'), len(S.states(d)))['DRIFT'] for d in ('month', 'daysago')}
    hc = (not hw) and any(med(d, 'C3_rrrinit', 'DRIFT') > rrr_drift[d] and med(d, 'C3_rrrinit', 'R') <= .9 for d in ('month', 'daysago'))
    out['H_weight'] = dict(month_R24_l10=med('month', 'C3_l10', 'R'), daysago_R7_l10=med('daysago', 'C3_l10', 'R'), holds=hw)
    out['H_conflict'] = dict(holds=hc, rrrinit_DRIFT={d: med(d, 'C3_rrrinit', 'DRIFT') for d in ('month', 'daysago')}, RRR16_DRIFT=rrr_drift,
                             rrrinit_R={d: med(d, 'C3_rrrinit', 'R') for d in ('month', 'daysago')})
    out['Q8'] = 'H-weight' if hw else 'H-conflict' if hc else 'neither'
    m = [tab[f'month/{v}/s{s}'] for v in var for s in SEEDS]
    agree = sum((x['R12'] >= .9) == x['k1'] for x in m); out['A3'] = dict(agree=agree, n=len(m), pass_=agree >= 10)
    return out


def tables():
    crow = []; srow = []
    for f in sorted(lib3.SHARDS.glob('chain_*_000.jsonl')):
        stem = f.name[len('chain_'):-len('_000.jsonl')]; first = rows(f)[0]
        bb, d, mp, me, path = first['backbone'], first['domain'], first['map'], first['method'], first['path']
        by = recs(bb, d, mp, me, path); T = max(max(v) for v in by.values())
        for t in range(1, T + 1):
            crow.append(dict(backbone=bb, domain=d, map=mp, method=me, path=path, t=t, A_t=float(np.mean([by[w][t]['success'] for w in by])),
                             R_t=float(np.mean([by[w][t]['trajectory_success'] for w in by]))))
    csvwrite('results/chains.csv', crow)
    agg = defaultdict(list)
    for f in sorted(lib3.SHARDS.glob('single_*.jsonl')):
        for r in rows(f): agg[r['backbone'], r['domain'], r['map'], r['method']].append(r['score']['success'])
    csvwrite('results/singles.csv', [dict(backbone=k[0], domain=k[1], map=k[2], method=k[3], **rate(v)) for k, v in sorted(agg.items())])
    return crow


def figures(res, crow):
    h = res.get('H', {})
    if 'A_t' in h:
        fig, axs = plt.subplots(1, 4, figsize=(18, 3.8))
        for ax, d in zip(axs, CYC):
            N = len(S.states(d))
            for me, c in (('F_empty', '#222222'), ('F_{1}', '#c4473a'), ('F_not1', '#3b6fb6'), ('E_Kstar', '#2a9d55')):
                if f'{d}/{me}' in h['A_t']:
                    ax.plot(range(1, 2 * N + 1), h['A_t'][f'{d}/{me}'][:2 * N], '-', color=c, label=f'{me} observed')
                if f'{d}/{me}' in h['model_A_t']:
                    ax.plot(range(1, 2 * N + 1), h['model_A_t'][f'{d}/{me}'], ':', color=c, label=f'{me} vote model')
            for x in (N, 2 * N): ax.axvline(x, color='#bbbbbb', lw=.6)
            ax.set_ylim(-.02, 1.02); ax.set_title(f'{d}: per-step accuracy A_t (one-way plus)', fontsize=9); ax.legend(fontsize=6)
        fig.tight_layout(); fig.savefig(ROOT / 'figs/h_At.png', dpi=140)
    if 'T' in res and 'T3' in res['T']:
        fig, axs = plt.subplots(1, 3, figsize=(14, 3.6)); bart = {r_['method']: r_ for r_ in crow}
        for ax, d in zip(axs, T_DOMAINS):
            tab = res['T']['T3']['rank_table'].get(d)
            if not tab: continue
            rs = sorted(map(int, tab)); ax.plot(rs, [tab[r]['R_2N'] if r in tab else tab[str(r)]['R_2N'] for r in rs], 'o-', label='T5Gemma R_2N')
            ax.plot(rs, [tab[r]['single'] if r in tab else tab[str(r)]['single'] for r in rs], 's--', label='T5Gemma single')
            ax.axvline(len(S.states(d)) - 1, color='#999999', ls=':'); ax.set_xscale('log', base=2); ax.set_ylim(-.02, 1.02); ax.set_title(d, fontsize=9); ax.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(ROOT / 'figs/t_rank.png', dpi=140)


def main():
    require_slurm(); p = verify_protocol3(); t0 = time.time(); res = dict(G3_0=read(ROOT / 'results/g30.json'))
    res['H'] = safe(h_unit, p); res['B'] = safe(b_unit, p); res['N'] = safe(n_unit, p)
    res['T'] = safe(t_unit, p, res['H'] if isinstance(res['H'], dict) else {}); res['A'] = safe(a_unit, p)
    res['algebra'] = read(ROOT / 'results/algebra.json').get('_s_k_vs_entry_order') if (ROOT / 'results/algebra.json').exists() else None
    res['lock'] = read(ROOT / 'protocol_lock.json') if (ROOT / 'protocol_lock.json').exists() else None
    crow = tables(); figures(res, crow); res['seconds'] = time.time() - t0
    dump('results/predictions.json', res)
    print(json.dumps({k: (v.get('Q5') or v.get('Q2p') or v.get('Q6') or v.get('Q8') or v.get('status')) if isinstance(v, dict) else None for k, v in res.items() if k in 'HBNTA'}), flush=True)


if __name__ == '__main__':
    main()
