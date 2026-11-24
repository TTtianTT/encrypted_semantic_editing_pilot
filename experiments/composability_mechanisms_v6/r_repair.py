"""R: repairs (Q20; PLAN v7 B6, appendix A.5). --backbone bart|t5 --mode precheck|run|r4|smoke.
Cases: data/r_cases.json (frozen by p_posthoc7.py; v6 confirm6 latents of R-A: F_empty alternating chains on held-out templates; R-B: BART
month under-trained C3-family editors, 'stopped at the previous state'; matched successful control steps). The latent at the case step is
recomputed with the same operators and dynamics as v6 (verified: the fitted-readout argmax at that step equals the recorded one, else stop).
precheck (before the lock; no decoding of repaired latents): per group the median change ||h' - h|| / R_w of PROJ and PUSH on the slot
  (>= 0.02, else the repair is a no-op and its predictions become exploratory).
run (after the lock): each repair once on the case-step latent, then one decode, exact match against the gold state of that step: SNAP,
  PROJ, PUSH (all cases), CTX (editors that change non-slot positions: the trained full-sequence C3-family editors of R-B; the slot-only
  S-RRR operator of R-A leaves the context unchanged), and SNAP+CTX (positive control, = reencode). Controls: the same repairs on matched
  successful steps.
r4 (after the lock): the same on replication cases drawn from this experiment's confirm7 U chains with the same rules: every T5Gemma
  F_empty alternating 'slot right, decode wrong' first failure; at most 300 first failures of the new C3 seeds (45-47) whose decoded state is
  the previous gold state (rng 3101), with matched controls.
smoke (before the lock): run mode on the first failures of the dev chains (results/devchains_<bb>.json.gz), dev split, code path only.
Output: results/r_<mode>_<bb>.json."""
import gzip
import re
import random
import time
from collections import defaultdict, Counter
from lib7 import *
from cells7 import v6_registry, editor_ops, u_cells, PATHS

REPAIRS = ('SNAP', 'PROJ', 'PUSH', 'CTX', 'SNAP+CTX')


def ops_for(eng, bb, c, split):
    d = c['domain']; pos = slots(bb, d, split)
    if c['method'] == 'F_empty' and d.endswith('-mt'):
        gates = read(V6DIR / f'results/gates_{bb}.json'); return m_base_ops(bb, d, gates, pos), False
    if split in ('confirm6',):
        reg = {e['name']: e['path'] for e in v6_registry() if e['domain'] == d}; return editor_ops(eng, reg[c['method']]), True
    for fam, dd, name, ops in u_cells(eng, bb, split, domains=[d]):
        if name == c['method']: return (ops() if callable(ops) else ops), c['method'].startswith(('C3', 'P2'))
    raise KeyError(c['method'])


@torch.no_grad()
def latents(eng, bb, d, ops, oplist, split, want):
    """Run the chain on every world; return {(world index, step): (h_row, m_row)} for the wanted (world index, step) pairs and the argmax."""
    ws = worlds5(d, split); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; state = [w['start_state'] for w in ws]
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots(bb, d, split).to(DEV); out = {}; T = max(t for _, t in want)
    for step, op in enumerate(oplist[:T], 1):
        prev = torch.tensor(state, device=DEV); state = [S.advance(d, s, op) for s in state]; h = apply_op(ops[op], h, m, prev)
        for (i, t) in want:
            if t == step: out[i, t] = (h[i].clone(), m[i].clone(), state[i])
    return out


@torch.no_grad()
def run_group(eng, bb, cases, split, mode):
    """cases of one cell (same backbone, domain, method, path). Returns per case the repair outcomes (run) or change sizes (precheck)."""
    c0 = cases[0]; d = c0['domain']; N = len(S.states(d)); ops, ctx_ok = ops_for(eng, bb, c0, split); oplist = PATHS(N)[c0['path']]
    ws = worlds5(d, split); idx = {w['world_id']: i for i, w in enumerate(ws)}; want = {(idx[c['world_id']], c['step']) for c in cases}
    lat = latents(eng, bb, d, ops, oplist, split, want); man = manifold(bb, d, split); P = planes(bb, d); lam = vote_lams(bb, d)['full'].double()
    pos = slots(bb, d, split); res = []; t = tmpl(d)
    for c in cases:
        i = idx[c['world_id']]; h, m, g = lat[i, c['step']]; assert g == c['gold'], (c['case_id'], g, c['gold'])
        sub = {k: v[i:i + 1].to(DEV) for k, v in man.items() if k != 'rank'}; p = pos[i:i + 1].to(DEV); hs = h[p[0]][None]
        am, _ = margin_raw(hs, sub['Cw'], P, lam); assert int(am[0]) == c['argmax_full'], ('latent mismatch with the recorded readout', c['case_id'])
        r = dict(case_id=c['case_id'], group=c['group'], role=c['role'], world=f"{d}/{c['world_id']}")
        gg = torch.tensor([g], device=DEV)
        for k in ('PROJ', 'PUSH'): r[f'change_{k}'] = float((repair_slot(k, hs, sub, gg) - hs.double()).norm() / sub['R'][0])
        if mode != 'precheck':
            cg = cache5(bb, d, split, g); clean = (cg['h'][i:i + 1].to(DEV), cg['m'][i:i + 1].to(DEV))
            for k in REPAIRS:
                if k == 'CTX' and not ctx_ok: continue
                h2, m2 = repair(k, h[None], m[None], p, sub, gg, clean); o = dec(eng, h2, m2)[0]
                r[k] = bool(Ev.score(o['text'], S.gold(ws[i], g, t), ws[i], o['ended'])['success'])
        res.append(r)
    return res


def r4_cases(bb):
    """Replication cases from this experiment's confirm7 U chains (shards), same rules as p_posthoc7 P3."""
    sh = ROOT / 'results/shards'; out = []; rng = random.Random(3101); recs = defaultdict(dict)
    sel = (lambda f: '_F_empty_alt_' in f.name and '-mt_' in f.name) if bb == 't5' else (lambda f: '_C3n' in f.name and 's7_s' in f.name)
    for f in sorted(sh.glob(f'chain_{bb}_*.jsonl')):
        if not sel(f): continue
        for r in rows(f): recs[r['domain'], r['method'], r['path'].replace('_from_start', '')].setdefault(r['world_id'], {})[r['step']] = r
    cand = []
    for (d, m, p), by in recs.items():
        for w, st in by.items():
            t = next((t for t in sorted(st) if not st[t]['success']), None)
            if t is None or st[t]['argmax_full'] != st[t]['state']: continue
            r = st[t]; prev = st[t - 1]['state'] if t > 1 else r['start']
            if bb == 'bart' and r['decoded_state'] != prev: continue
            cand.append(dict(source='v7U', backbone=bb, domain=d, method=m, family=re.sub(r'_s\d+$', '', m), path=p, world_id=w, step=t, start=r['start'], gold=r['state'],
                             prev_gold=prev, decoded_state=r['decoded_state'], argmax_full=r['argmax_full'], group='R4-A-t5' if bb == 't5' else 'R4-B', role='case'))
    if bb == 'bart' and len(cand) > 300: cand = rng.sample(sorted(cand, key=lambda c: (c['method'], c['path'], c['world_id'])), 300)
    ctrl = []
    for c in cand:
        by = recs[c['domain'], c['method'], c['path']]; opts = sorted((w, t) for w, st in by.items() if w != c['world_id'] for t, r in st.items() if abs(t - c['step']) <= 2 and r['success'])
        w, t = rng.choice(opts); r = by[w][t]
        ctrl.append(dict(c, world_id=w, step=t, start=r['start'], gold=r['state'], prev_gold=by[w][t - 1]['state'] if t > 1 else r['start'], decoded_state=r['decoded_state'],
                         argmax_full=r['argmax_full'], role='control'))
    allc = cand + ctrl
    for i, c in enumerate(allc): c['case_id'] = f"{c['group']}/{c['role']}/{i:04d}"
    return allc


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; mode = sys.argv[sys.argv.index('--mode') + 1]; t0 = time.time(); eng = engine5(bb)
    if mode in ('run', 'r4'): assert lock_ok(), 'R decoding only after the lock'
    if mode == 'smoke':
        with gzip.open(ROOT / f'results/devchains_{bb}.json.gz', 'rt') as g: dc = json.load(g)
        cases = []
        for k, v in list(dc['cells'].items()):
            if v['split'] != 'dev' or v['method'] not in ('F_empty',) and not v['method'].startswith('C3n'): continue
            for i, w in enumerate(v['sim']['world_ids'][:4]):
                t = v['first_fail'][i]
                if t is None or v['sim']['argmax'][i][t - 1] != v['sim']['states'][i][t - 1]: continue
                cases.append(dict(source='dev', backbone=bb, domain=v['domain'], method=v['method'], path=v['path'], world_id=w, step=t, gold=v['sim']['states'][i][t - 1],
                                  argmax_full=v['sim']['argmax'][i][t - 1], group='smoke', role='case', case_id=f'smoke/{len(cases):04d}'))
            if len(cases) >= 12: break
        split = 'dev'
    elif mode == 'r4': cases = [c for c in r4_cases(bb)]; split = CONFIRM
    else: cases = [c for c in read(ROOT / 'data/r_cases.json')['cases'] if c['backbone'] == bb]; split = 'confirm6'
    groups = defaultdict(list)
    for c in cases: groups[c['domain'], c['method'], c['path']].append(c)
    res = []
    for key, cs in sorted(groups.items()):
        res += run_group(eng, bb, cs, split, 'precheck' if mode == 'precheck' else 'run'); print('R', mode, key, len(cs), flush=True)
    summ = defaultdict(dict)
    for g in sorted({r['group'] for r in res}):
        for role in ('case', 'control'):
            rs = [r for r in res if r['group'] == g and r['role'] == role]
            if not rs: continue
            s = dict(n=len(rs), median_change_PROJ=float(np.median([r['change_PROJ'] for r in rs])), median_change_PUSH=float(np.median([r['change_PUSH'] for r in rs])))
            for k in REPAIRS:
                v = [r[k] for r in rs if k in r]
                if v: s[k] = rate(v)
            summ[g][role] = s
    out = dict(mode=mode, backbone=bb, split=split, summary=summ, cases=res, seconds=time.time() - t0, resources=eng.resources())
    if mode == 'precheck': out['precheck'] = {g: dict(PROJ=v['case']['median_change_PROJ'] >= .02, PUSH=v['case']['median_change_PUSH'] >= .02) for g, v in summ.items() if 'case' in v}
    dump(ROOT / ('local/smoke' if mode == 'smoke' else 'results') / f'r_{mode}_{bb}.json', out)
    print(json.dumps({g: {r: {k: (x['rate'] if isinstance(x, dict) else x) for k, x in v.items()} for r, v in s.items()} for g, s in summ.items()}), flush=True)


if __name__ == '__main__':
    main()
