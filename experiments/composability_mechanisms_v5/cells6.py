"""Cell definitions shared by the pre-lock simulation and the post-lock chains (identical operators and editors on both sides).
M (PLAN B5): per (backbone, domain kept by GM): base (GM operator, slot only; = F_empty), F{1}, F_not1, every F{j} (j >= 2; planes
pooled over the training templates), C1 (full sequence; family CE), slot C3-U4 (BART; family state), reference full-sequence RRR-16
(family reference), reencode.
C (PLAN B6, BART, weekday / month, template 0): set CT1 (not converged: v1 C3, v3 C3-l3 / C3-l10, v4 P2b on month; v1 C3 on weekday if
its data definition matches; new C3n<u> whose dev L2 > 1.2 x RRR-16) and set CT2 (non-inferiority: base surgery F_empty / F{1} /
F_not1 / F{j}; RRR-r and FF-r, r in N-4..N-2; v3 C3-rrrinit, v4 P2a, P2c, C3-U4, v5 C3n1200 / C3n2400 (the plan's enumeration); new
C3n<u> meeting the convergence rule).
K (PLAN B7, BART): OR-U4 (bind3, bind3fix), Att2L-U4, Att2L-U8, Att1-U8; references v5 Tok-U, Att1-U, Att2-U; reencode."""
from lib6 import *

PATHS = lambda N: dict(plus=['plus'] * (2 * N), minus=['minus'] * (2 * N), alt=['plus', 'minus'] * N)
K_PATHS = dict(plus=['plus'] * 30, minus=['minus'] * 12, alt=['plus', 'minus'] * 6)


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


def m_cells(eng, bb, gates, split):
    """(domain, method, ops or thunk, family) for every M cell."""
    out = []; tr = read(ROOT / f'results/train_new_{bb}_M.json')
    for d in gates['M_domains']:
        pos = slots(bb, d, split); T = m_base_ops(bb, d, gates, pos)
        for name, ops in freeze_conditions(bb, d, T, pos).items(): out.append((d, name, ops, 'state'))
        for v, fam in (('C1n', 'CE'), ('SC3U4', 'state')):
            for s in SEEDS:
                st = tr.get(f'{v}/{d}/s{s}')
                if not st or st['status'] != 'ok': continue
                p = ROOT / st['path']
                out.append((d, f'{v}_s{s}', (lambda p=p: editor_ops(eng, p)) if v == 'C1n' else (lambda p=p, pos=pos: slot_ops_from(p, eng.d, pos)), fam))
        out.append((d, 'RRR16full', lambda bb=bb, d=d: full_rrr16_ops(bb, d), 'reference'))
    return out


def c_registry():
    """Unit-C editors with their set (CT1 / CT2), from results/train_new_bart_C.json (convergence decided before the lock)."""
    trC = read(ROOT / 'results/train_new_bart_C.json'); conv = trC['convergence']; out = []
    audit = read(ROOT / 'data/audit.json')['domains']
    for e in existing_editors('bart'):
        if e['family'] != 'state' or e['domain'] not in C_DOMAINS: continue
        un = e['name'].startswith(('C3v1', 'C3l3v3', 'C3l10v3', 'P2b'))
        out.append(dict(domain=e['domain'], name=e['name'], path=e['path'], set='CT1' if un else 'CT2', origin='existing'))
    if audit['weekday'].get('slot_equals_v1_caches'):
        out += [dict(domain='weekday', name=f'C3v1_s{s}', path=str(V1 / f'local/e1_C3_weekday_s{s}_0600.pt'), set='CT1', origin='existing') for s in SEEDS]
    tr5 = read(V5DIR / 'results/train_new_bart_L.json')
    for d in C_DOMAINS:
        for v in ('C3n1200', 'C3n2400'):
            out += [dict(domain=d, name=f'{v}_s{s}', path=str(V5DIR / tr5[f'{v}/{d}/s{s}']['path']), set='CT2', origin='v5') for s in SEEDS if tr5[f'{v}/{d}/s{s}']['status'] == 'ok']
        for u in (300, 450, 600, 900):
            for s in SEEDS:
                st = trC[f'C3n{u}/{d}/s{s}']
                if st['status'] != 'ok': continue
                out.append(dict(domain=d, name=f'C3n{u}_s{s}', path=str(ROOT / st['path']), set='CT2' if conv[f'{d}/C3n{u}_s{s}']['converged'] else 'CT1', origin='new'))
    return out


def c_cells(eng, split):
    """(domain, method, ops or thunk, set) for every C cell (BART)."""
    out = []
    for d in C_DOMAINS:
        pos = slots('bart', d, split); T = base_ops('bart', d)
        for name, ops in freeze_conditions('bart', d, T, pos).items(): out.append((d, name, ops, 'CT2'))
        for r in grid_ranks('bart', d):
            for kind in ('RRR', 'FF'): out.append((d, f'{kind}{r}', lambda d=d, kind=kind, r=r: grid_ops('bart', d, kind, r), 'CT2'))
    for e in c_registry(): out.append((e['domain'], e['name'], lambda p=e['path']: editor_ops(eng, p), e['set']))
    return out


def k_cells(eng, split):
    """(domain, method, ops or thunk) for every K cell (BART)."""
    trK = read(ROOT / 'results/train_new_bart_K.json'); trB = read(V5DIR / 'results/train_new_bart_B.json'); out = []
    for d in K_DOMAINS:
        pos = slots('bart', d, split); npos = name_positions(d, split)
        for kind, upd, Sset, doms in K_NEW:
            if d not in doms: continue
            name = k_name(kind, upd)
            for s in SEEDS:
                st = trK[f'{name}/{d}/s{s}']
                if st['status'] != 'ok': continue
                out.append((d, f'{name}_s{s}', lambda p=ROOT / st['path'], pos=pos, npos=npos: (lambda kd: k_ops(kd[0], kd[1], pos, npos))(k_load(p, eng.d))))
        for kind in ('Tok', 'Att1', 'Att2'):
            for s in SEEDS: out.append((d, f'{kind}U_s{s}', lambda p=V5DIR / trB[f'{kind}/{d}/s{s}']['path']: k_ops('Tok', k_load5(p, eng.d))))
        out.append((d, 'reencode', None))
    return out


def k_load5(path, dim):
    c = load(path); kind = c.get('kind', 'Att1'); ed = tokatt_pair(dim, c['seed'], kind != 'Tok', heads=2 if kind == 'Att2' else 1)
    ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)
