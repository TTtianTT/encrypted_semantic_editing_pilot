"""Cell definitions shared by the pre-lock simulation and the post-lock chains (identical operators and editors on both sides).
L (PLAN 6.1): freeze surgery on the base operator, the RRR / FF rank grid, existing and new trained editors.
N (PLAN 10.1): base operator, F{1}, F{not 1}, new C1 and C3-U4 editors on the multi-template domains.
D (PLAN 7.1): oracle decoupled freeze D_S for S = {1}, not-1 and every {j}, j >= 2 (the standard F_S chains are the L chains).
B (PLAN 9.1): Tok-U, Att1-U, Att2-U (seeds 42-44), references v4 Att-L2 and RRR-32, and reencode."""
from lib5 import *

PATHS = lambda N: dict(plus=['plus'] * (2 * N), minus=['minus'] * (2 * N), alt=['plus', 'minus'] * N)
B_PATHS = dict(plus=['plus'] * 30, minus=['minus'] * 6, alt=['plus', 'minus'] * 3)


def plane_sets(bb, d):
    P = planes(bb, d); ks = [k for k, _ in P]; nf = set(ks) - {1}; out = {'{1}': {1}, 'not1': nf}
    for k in ks:
        if k >= 2 and not (len(nf) == 1 and k in nf): out[f'{{{k}}}'] = {k}
    return P, out


def freeze_conditions(bb, d, T, pos):
    P, sets = plane_sets(bb, d)
    return {'F_empty': T, **{f'F_{n}': {op: Freeze(T[op], bvec(P, Sset), pos) for op in T} for n, Sset in sets.items()}}


def decoupled_conditions(bb, d, T, pos, split):
    P, sets = plane_sets(bb, d); Cw = slot_matrix(bb, d, split)
    return {f'D_{n}': {op: DecoupledFreeze(T[op], bvec(P, Sset), pos, Cw) for op in T} for n, Sset in sets.items()}


def editor_ops(eng, path):
    ed = load_editor(eng, path); return {op: ed[op] for op in ('plus', 'minus')}


def l_cells(eng, bb, split):
    """(domain, method, ops or thunk, family, new) for every L cell."""
    out = []
    for d in L_DOMAINS[bb]:
        T = base_ops(bb, d); pos = slots(bb, d, split)
        for name, ops in freeze_conditions(bb, d, T, pos).items(): out.append((d, name, ops, 'state', False))
        if d in GRID_DOMAINS:
            for r in grid_ranks(bb, d):
                for kind in ('RRR', 'FF'): out.append((d, f'{kind}{r}', lambda bb=bb, d=d, kind=kind, r=r: grid_ops(bb, d, kind, r), 'state', False))
    for e in existing_editors(bb):
        out.append((e['domain'], e['name'], lambda p=e['path']: editor_ops(eng, p), e['family'], False))
    tr = read(ROOT / f'results/train_new_{bb}_L.json')
    for b_, unit, v, d, seeds, fam, kind, upd in NEW_EDITORS:
        if b_ != bb or unit != 'L': continue
        for s in seeds:
            st = tr[f'{v}/{d}/s{s}']
            if st['status'] == 'ok': out.append((d, f'{v}_s{s}', lambda p=ROOT / st['path']: editor_ops(eng, p), fam, True))
    return out


def n_cells(eng, bb, gates, split):
    out = []; tr = read(ROOT / f'results/train_new_{bb}_N.json')
    for d in gates['N_domains']:
        T = base_ops(bb, d, gates); pos = slots(bb, d, split); P = planes(bb, d); ks = [k for k, _ in P]
        out += [(d, 'F_empty', T, 'state', True), (d, 'F_{1}', {op: Freeze(T[op], bvec(P, {1}), pos) for op in T}, 'state', True),
                (d, 'F_not1', {op: Freeze(T[op], bvec(P, set(ks) - {1}), pos) for op in T}, 'state', True)]
        for b_, unit, v, dd, seeds, fam, kind, upd in NEW_EDITORS:
            if b_ != bb or unit != 'N' or dd != d: continue
            for s in seeds:
                st = tr[f'{v}/{d}/s{s}']
                if st['status'] == 'ok': out.append((d, f'{v}_s{s}', lambda p=ROOT / st['path']: editor_ops(eng, p), fam, True))
    return out


def b_pair(path, dim):
    c = load(path); kind = c.get('kind', 'Att1'); ed = tokatt_pair(dim, c['seed'], kind != 'Tok', heads=2 if kind == 'Att2' else 1)
    ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)


def v4_x_pair(path, dim, att):
    c = load(path); ed = tokatt_pair(dim, c.get('seed', 42), att); ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)


def b_cells(eng):
    """(domain, method, ops) for B (BART). v4 Att-L2 references: local/x_Att_<d>_s<s>_u<upd>.pt of v4 (admitted update count)."""
    tr = read(ROOT / 'results/train_new_bart_B.json'); xt = read(V4DIR / 'results/x_train.json'); out = []
    for d in B_DOMAINS:
        for kind in ('Tok', 'Att1', 'Att2'):
            for s in SEEDS: out.append((d, f'{kind}U_s{s}', lambda p=ROOT / tr[f'{kind}/{d}/s{s}']['path']: {op: e for op, e in b_pair(p, eng.d).items()}))
        for s in SEEDS:
            upd = xt[f'{d}/Att/s{s}']['updates']
            out.append((d, f'AttL2v4_s{s}', lambda p=V4DIR / f'local/x_Att_{d}_s{s}_u{upd}.pt': {op: e for op, e in v4_x_pair(p, eng.d, True).items()}))
        f = load(V4DIR / f'local/x_rrr32_{d}.pt'); out.append((d, 'RRR32', {op: RRRop(f[op, 32]) for op in ('plus', 'minus')}))
        out.append((d, 'reencode', None))
    return out
