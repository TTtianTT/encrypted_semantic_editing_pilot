"""v8 cell definitions shared by the dev pre-checks, U calibration, post-lock chains and analysis (PLAN v7 C2, C3, B.3; members listed in
advance, design rule 5). Paths: plus, minus, alternating, 2N steps.
N (bb in bart, t5; month-nat; splits dev / confirm8):
  - surgeries F_empty, F{1}, F_not1, F{j} on S-RRR_nat (the GN-selected operator, results/gates_nat_<bb>.json);
  - S-RRR-16_syn zero-shot (F_empty only; N2); reference: full-sequence RRR-16 fitted on natural train;
  - C1_nat (CE, seeds 50-52, admitted ones); BART: slot C3-U4_nat (seeds 50-52, exploratory).
G (t5_9b) and ladder (t5_bb, t5_ll; closed form only), weekday and month template 0, splits dev / confirm7:
  - RRR-r for r in {N-4, ..., N, 16} and r*_pred, r*_pred - 2; FF-r for the rank-deficient r; surgeries on RRR-16;
  - G only: C1 (seeds 50-52) and C3-U4 (seeds 50-52), admitted ones.
family: 'state' (closed form or objective with a state target), 'CE' (decoder-trained), 'ref' (reference, not in N5 / G5)."""
from lib8 import *

PATHS = lambda N: dict(plus=['plus'] * (2 * N), minus=['minus'] * (2 * N), alt=['plus', 'minus'] * N)
SEEDS8 = (50, 51, 52)
G_DOMAINS = ['weekday', 'month']


def plane_sets(bb, d):
    P = planes(bb, d); ks = [k for k, _ in P]; nf = set(ks) - {1}; out = {'{1}': {1}, 'not1': nf}
    for k in ks:
        if k >= 2 and not (len(nf) == 1 and k in nf): out[f'{{{k}}}'] = {k}
    return P, out


def freeze_conditions(bb, d, T, pos, prefix=''):
    P, sets = plane_sets(bb, d)
    return {f'{prefix}F_empty': T, **{f'{prefix}F_{n}': {op: Freeze(T[op], bvec(P, Sset), pos) for op in T} for n, Sset in sets.items()}}


def path8(bb, v, d, s, upd):
    return ROOT / f'local/n8_{bb}_{v}_{d}_s{s}_u{upd}.pt'


def admitted(bb, part):
    f = ROOT / f'results/train8_{bb}_{part}.json'
    if not f.exists(): return {}
    return {k: v for k, v in read(f).items() if not k.startswith('_') and isinstance(v, dict) and v.get('admitted')}


def editor_ops(eng, path):
    ed = load_editor(eng, path); return {op: ed[op] for op in ('plus', 'minus')}


def n_cells(eng, bb, split):
    """[(family, domain, method, ops-or-thunk)] for unit N."""
    d = S.NAT; pos = slots(bb, d, split); g = read(ROOT / f'results/gates_nat_{bb}.json')['GN']; base = g['base'] or 'SRRR16'; out = []
    if base == 'Eall':
        f = load(ROOT / f'local/{bb}_eall_{d}.pt'); T = {op: PlaneEd(f['fits'][op][0], f['fits'][op][1], f['B'], pos) for op in ('plus', 'minus')}
    else:
        f = load(ROOT / f'local/{bb}_srrr_{d}.pt'); r = int(base[4:]); T = {op: SlotRRRop(f[op, r], pos) for op in ('plus', 'minus')}
    for name, ops in freeze_conditions(bb, d, T, pos, 'nat_').items(): out.append(('state', d, name, ops))
    syn = load(V6DIR / f'local/{bb}_srrr_month-mt.pt'); out.append(('state', d, 'syn_F_empty', {op: SlotRRRop(syn[op, 16], pos) for op in ('plus', 'minus')}))
    full = load(ROOT / f'local/{bb}_rrr_{d}_full16.pt'); out.append(('ref', d, 'RRR16full', {op: RRRop(full[op, 16]) for op in ('plus', 'minus')}))
    for key, st in admitted(bb, 'N').items():
        v, _, s = key.split('/'); p = path8(bb, v, d, int(s[1:]), st['updates'])
        if v == 'C1': out.append(('CE', d, f'C1nat_{s}', lambda p=p: editor_ops(eng, p)))
        elif v == 'SC3U4': out.append(('state', d, f'SC3U4nat_{s}', lambda p=p, pos=pos: slot_ops_from(p, eng.d, pos)))
    return out


def g_ranks(bb, d):
    r = read(ROOT / f'results/g_prep_{bb}.json')['domains'][d]; return r['ranks'], r['ff_ranks'], r['rstar_pred']


def g_cells(eng, bb, split, domains=G_DOMAINS):
    """[(family, domain, method, ops-or-thunk)] for unit G (t5_9b) and the ladder (t5_bb, t5_ll: closed form only)."""
    gp = read(ROOT / f'results/g_prep_{bb}.json'); out = []
    for d in domains:
        if not gp['domains'][d].get('gate'): continue
        fits = load(ROOT / f'local/{bb}_R_{d}_v8.pt'); ranks, ffr, _ = g_ranks(bb, d); pos = slots(bb, d, split)
        T = {op: RRRop(fits['RRR', op, 16]) for op in ('plus', 'minus')}
        for name, ops in freeze_conditions(bb, d, T, pos).items(): out.append(('state', d, name, ops))
        for r in ranks:
            if r != 16: out.append(('state', d, f'RRR{r}', {op: RRRop(fits['RRR', op, r]) for op in ('plus', 'minus')}))
        for r in ffr: out.append(('state', d, f'FF{r}', {op: RRRop(fits['FF', op, r]) for op in ('plus', 'minus')}))
        if bb == 't5_9b':
            for key, st in admitted(bb, 'G').items():
                v, dd, s = key.split('/')
                if dd == d: out.append(('CE' if v == 'C1' else 'state', d, f'{v}_{s}', lambda p=path8(bb, v, d, int(s[1:]), st['updates']): editor_ops(eng, p)))
    return out
