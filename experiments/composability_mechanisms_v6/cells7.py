"""Cell definitions shared by dev chains, calibration, pre-lock simulation and post-lock chains (PLAN v7 B7-B9; members listed in advance,
design rule 5). Families of unit U:
F1  (primary, prospective; BART weekday / month template 0): new C3 seeds 45-47, snapshots 300 / 450 / 600 / 900 / 1200.
F1s (secondary): v6's CT1 editors (v1 C3, v3 C3-l3 / C3-l10, v4 P2b, v6 C3n300 / 450 / 900; v6's identical cells removed: C3n600 = v1 C3,
     month C3n300 s42 = v1 C3 s42; DEVIATIONS of v6 #11, design rule 10).
NI  (primary, non-inferiority). BART template 0: v6's CT2 set (surgeries on RRR-16, RRR-r / FF-r for r in N-4..N-2, v3 C3-rrrinit, v4 P2a,
     P2c, C3-U4, v5 C3n1200 / 2400). T5Gemma month template 0: RRR-r r in {8, 9, 10, 11, 16}, FF-r r in {8, 9, 10}, surgeries on RRR-16,
     v5 C3-U4n (seeds 42, 43: the seeds v5 admitted).
F2  (primary): T5Gemma month-mt, held-out templates: surgeries F_empty, F{1}, F_not1, F{j} on v6's GM operator S-RRR-16.
F3  (secondary): BART weekday-mt / month-mt / hour-mt, the same conditions.
Paths: plus, minus, alternating, 2N steps (PATHS). K paths (B9): bind3 plus 100, minus 30, alternating 30; name3 / bind3fix plus 30."""
from lib7 import *

PATHS = lambda N: dict(plus=['plus'] * (2 * N), minus=['minus'] * (2 * N), alt=['plus', 'minus'] * N)
K7_PATHS = {'bind3': dict(plus=['plus'] * 100, minus=['minus'] * 30, alt=['plus', 'minus'] * 15), 'name3': dict(plus=['plus'] * 30),
            'bind3fix': dict(plus=['plus'] * 30)}
SNAPS7 = (300, 450, 600, 900, 1200); C3_SEEDS = (45, 46, 47)
V6_IDENTICAL = {('weekday', f'C3n600_s{s}') for s in SEEDS} | {('month', f'C3n600_s{s}') for s in SEEDS} | {('month', 'C3n300_s42')}
T5_NI_RRR = (8, 9, 10, 11, 16); T5_NI_FF = (8, 9, 10)


def plane_sets(bb, d):
    P = planes(bb, d); ks = [k for k, _ in P]; nf = set(ks) - {1}; out = {'{1}': {1}, 'not1': nf}
    for k in ks:
        if k >= 2 and not (len(nf) == 1 and k in nf): out[f'{{{k}}}'] = {k}
    return P, out


def freeze_conditions(bb, d, T, pos):
    P, sets = plane_sets(bb, d)
    return {'F_empty': T, **{f'F_{n}': {op: Freeze(T[op], bvec(P, Sset), pos) for op in T} for n, Sset in sets.items()}}


def editor_ops(eng, path):
    ed = load_editor(eng, path); return {op: ed[op] for op in ('plus', 'minus')}


def grid_ops7(bb, d, kind, r):
    f7 = ROOT / f'local/{bb}_R_{d}_v7.pt'
    if f7.exists():
        fits = load(f7)
        if (kind, 'plus', r) in fits: return {op: RRRop(fits[kind, op, r]) for op in ('plus', 'minus')}
    if r == 16 and kind == 'RRR': return base_ops(bb, d)
    return grid_ops(bb, d, kind, r)


def v6_registry():
    """v6's unit-C editors with v6's set (CT1 / CT2); v6's identical cells removed (rule 10)."""
    tr6 = read(V6DIR / 'results/train_new_bart_C.json'); conv = tr6['convergence']; out = []
    for e in existing_editors('bart'):
        if e['family'] != 'state' or e['domain'] not in C_DOMAINS: continue
        un = e['name'].startswith(('C3v1', 'C3l3v3', 'C3l10v3', 'P2b')); out.append(dict(domain=e['domain'], name=e['name'], path=e['path'], set='CT1' if un else 'CT2'))
    out += [dict(domain='weekday', name=f'C3v1_s{s}', path=str(V1 / f'local/e1_C3_weekday_s{s}_0600.pt'), set='CT1') for s in SEEDS]
    tr5 = read(V5DIR / 'results/train_new_bart_L.json')
    for d in C_DOMAINS:
        for v in ('C3n1200', 'C3n2400'):
            out += [dict(domain=d, name=f'{v}_s{s}', path=str(V5DIR / tr5[f'{v}/{d}/s{s}']['path']), set='CT2') for s in SEEDS if tr5[f'{v}/{d}/s{s}']['status'] == 'ok']
        for u in (300, 450, 600, 900):
            for s in SEEDS:
                st = tr6[f'C3n{u}/{d}/s{s}']
                if st['status'] == 'ok': out.append(dict(domain=d, name=f'C3n{u}_s{s}', path=str(V6DIR / st['path']), set='CT2' if conv[f'{d}/C3n{u}_s{s}']['converged'] else 'CT1'))
    return [e for e in out if (e['domain'], e['name']) not in V6_IDENTICAL]


def u_cells(eng, bb, split, domains=None):
    """[(family, domain, method, ops-or-thunk)] for unit U on a split. Template-0 domains use template-0 splits ('dev', CONFIRM); multi-template
    domains use 'dev' (training templates), 'dev7ho' or CONFIRM (held-out templates)."""
    out = []; mt = split in ('dev7ho',) or domains is not None and all(d.endswith('-mt') for d in domains)
    if bb == 'bart':
        if split != 'dev7ho':
            for d in C_DOMAINS:
                if domains and d not in domains: continue
                pos = slots('bart', d, split); T = base_ops('bart', d)
                for name, ops in freeze_conditions('bart', d, T, pos).items(): out.append(('NI', d, name, ops))
                for r in grid_ranks('bart', d):
                    for kind in ('RRR', 'FF'): out.append(('NI', d, f'{kind}{r}', lambda d=d, kind=kind, r=r: grid_ops('bart', d, kind, r)))
                for e in v6_registry():
                    if e['domain'] == d: out.append(('NI' if e['set'] == 'CT2' else 'F1s', d, e['name'], lambda p=e['path']: editor_ops(eng, p)))
                for s in C3_SEEDS:
                    for u in SNAPS7: out.append(('F1', d, f'C3n{u}s7_s{s}', lambda p=new7_path('bart', f'C3n{u}', d, s, u): editor_ops(eng, p)))
        mts = M_DOMAINS['bart']; fam = 'F3'
    else:
        if split != 'dev7ho' and (not domains or 'month' in domains):
            d = 'month'; pos = slots('t5', d, split); T = base_ops('t5', d)
            for name, ops in freeze_conditions('t5', d, T, pos).items(): out.append(('NI', d, name, ops))
            for r in T5_NI_RRR: out.append(('NI', d, f'RRR{r}', lambda r=r: grid_ops7('t5', 'month', 'RRR', r)))
            for r in T5_NI_FF: out.append(('NI', d, f'FF{r}', lambda r=r: grid_ops7('t5', 'month', 'FF', r)))
            tr5 = read(V5DIR / 'results/train_new_t5_L.json')
            for s in SEEDS:
                st = tr5.get(f'C3U4n/month/s{s}')
                if st and st['status'] == 'ok': out.append(('NI', d, f'C3U4n_s{s}', lambda p=V5DIR / st['path']: editor_ops(eng, p)))
        mts = M_DOMAINS['t5']; fam = 'F2'
    gates = read(V6DIR / f'results/gates_{bb}.json')
    for d in mts:
        if domains and d not in domains: continue
        pos = slots(bb, d, split); T = m_base_ops(bb, d, gates, pos)
        for name, ops in freeze_conditions(bb, d, T, pos).items(): out.append((fam, d, name, ops))
    if split == 'dev7ho' or mt: out = [c for c in out if c[1].endswith('-mt')]
    return out


def k_cells7(eng, split):
    """(domain, method, kind, ops-or-thunk) for unit K: v7 editors (seeds 45-49; OR-U8 42-44) and v6's (seeds 42-44) Att2L-U8 / U4, Att1-U8."""
    tr7 = read(ROOT / 'results/train_new_bart_K.json'); tr6 = read(V6DIR / 'results/train_new_bart_K.json'); out = []
    for d in K_DOMAINS:
        pos = slots('bart', d, split); npos = name_positions(d, split)
        for name in ('Att2LU8', 'Att2LU4', 'Att1U8', 'ORU8'):
            for s in (42, 43, 44, 45, 46, 47, 48, 49):
                st = tr7.get(f'{name}/{d}/s{s}') if (s >= 45 or name == 'ORU8') else tr6.get(f'{name}/{d}/s{s}')
                if not st or st['status'] != 'ok': continue
                base = ROOT if (s >= 45 or name == 'ORU8') else V6DIR
                out.append((d, f'{name}_s{s}', name, lambda p=base / st['path'], pos=pos, npos=npos: (lambda kd: k_ops(kd[0], kd[1], pos, npos))(k_load(p, eng.d))))
    return out
