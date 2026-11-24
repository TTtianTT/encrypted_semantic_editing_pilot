"""New editors (GPU, before the lock; train only, admission on dev only; PLAN B1 new rule 2, B4, B5, B6, B7). --backbone bart|t5
--part M|C|K. Idempotent (an editor already saved is not retrained). Admission (PLAN B4): single-step editors dev single >= 0.90;
unrolled editors dev in-horizon (plus R_4) >= 0.90; K editors dev single >= 0.95 on name3 and bind3fix (bind3 not gated); otherwise one
retrain with twice the updates; otherwise 'cannot learn' (reported).
M: full-sequence C1 (600 updates; both backbones) and the slot C3-U4 (S <= 4, 1200 updates, BART) on the domains kept by GM.
C (BART): C3 (lambda = 1) on weekday and month, one 1800-update run per seed with snapshots at 300, 450, 600, 900, 1200 (identical to
separate runs of those lengths: same seed, same batch sequence); C3n<u> = the snapshot at u (retrain = the snapshot at 2u). Convergence
(PLAN B6): dev L2 (single step, normalised token L2, plus and minus averaged) vs 1.2 x the RRR-16 base operator's dev L2, for every unit-C
editor (existing and new); decided here, before the lock.
K (BART): OR-U4 (bind3, bind3fix; the oracle routing is not defined for name3, whose slot names are not list names), Att2L-U4,
Att2L-U8, Att1-U8 on bind3, name3, bind3fix, seeds 42-44."""
import time
from lib6 import *

SNAPS = (300, 450, 600, 900, 1200)


def c1(eng, bb, d, s, upd):
    f = new6_path(bb, 'C1n', d, s, upd)
    if f.exists(): return load(f)['dev_single']
    ed, hist, scale = train_editor(eng, bb, d, 'natural', 'C1', s, updates=upd)
    r = dev_single(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')})
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_single=r, l2_scale=scale, updates=upd, group='C1'))
    write(f'results/train_new/{bb}_C1n_{d}_s{s}_u{upd}.jsonl', hist); return r


def sc3u4(eng, bb, d, s, upd):
    f = new6_path(bb, 'SC3U4', d, s, upd)
    if f.exists(): return load(f)['dev_R4']
    ed, hist, scale = train_unrolled_slot(eng, bb, d, s, (1, 2, 3, 4), updates=upd)
    ops = {op: SlotOp(ed[op], slots(bb, d, 'dev')) for op in ('plus', 'minus')}
    r4 = dev_chain(eng, bb, d, 'natural', ops, ['plus'] * 4)[-1]
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_R4=r4, slot_scale=scale, updates=upd, kind='SC3U4'))
    write(f'results/train_new/{bb}_SC3U4_{d}_s{s}_u{upd}.jsonl', hist); return r4


def c3_run(eng, d, s):
    """One 1800-update C3 run; snapshots saved as C3n<u>."""
    if all(new6_path('bart', f'C3n{u}', d, s, u).exists() for u in SNAPS + (1800,)): return
    source_path(); from backend import editors
    ed, hist, scale = train_editor(eng, 'bart', d, 'natural', 'C3', s, updates=1800, snapshots=SNAPS)
    write(f'results/train_new/bart_C3n_{d}_s{s}_u1800.jsonl', hist)
    for u in SNAPS + (1800,):
        sd = ed.snapshots[u] if u in ed.snapshots else {k: x.cpu() for k, x in ed.state_dict().items()}
        e2 = editors(eng.d, s); e2.load_state_dict(sd); e2 = e2.eval().requires_grad_(False)
        r = dev_single(eng, 'bart', d, 'natural', {op: e2[op] for op in ('plus', 'minus')})
        save(new6_path('bart', f'C3n{u}', d, s, u), dict(editor=sd, seed=s, dev_single=r, l2_scale=scale, updates=u, group='C3', note='snapshot of one 1800-update run'))


def k_editor(eng, kind, name, d, s, upd, Sset):
    f = ROOT / f'local/k_{name}_{d}_s{s}_u{upd}.pt'
    if f.exists(): return load(f)['dev_single']
    ed, hist = train_k(d, s, kind, updates=upd, Sset=Sset)
    ops = k_ops(kind, ed, slots('bart', d, 'dev'), name_positions(d, 'dev') if kind == 'OR' else None)
    r = dev_single(eng, 'bart', d, 'natural', ops)
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind=kind, name=name, Sset=list(Sset), dev_single=r, updates=upd))
    write(f'results/train_new/k_{name}_{d}_s{s}_u{upd}.jsonl', hist); return r


@torch.no_grad()
def convergence(eng, res):
    """PLAN B6: unit-C editors' dev L2 vs 1.2 x RRR-16 (v4 base fit) dev L2 per domain."""
    out = {}
    for d in C_DOMAINS:
        scale = l2_scales('bart', d, 'natural'); f, r = base_fit('bart', d); rrr = dev_l2({op: RRRop(f[op, 16]) for op in ('plus', 'minus')}, 'bart', d, 'natural', scale)
        out[f'RRR16/{d}'] = rrr; eds = [e for e in existing_editors('bart') if e['family'] == 'state' and e['domain'] == d]
        if d == 'weekday':
            eds += [dict(name=f'C3v1_s{s}', domain=d, path=str(V1 / f'local/e1_C3_weekday_s{s}_0600.pt')) for s in SEEDS]
        for v in ('C3n1200', 'C3n2400'):
            tr = read(V5DIR / 'results/train_new_bart_L.json')
            eds += [dict(name=f'{v}_s{s}', domain=d, path=str(V5DIR / tr[f'{v}/{d}/s{s}']['path'])) for s in SEEDS if tr[f'{v}/{d}/s{s}']['status'] == 'ok']
        for u in (300, 450, 600, 900):
            for s in SEEDS:
                st = res.get(f'C3n{u}/{d}/s{s}')
                if st and st['status'] == 'ok': eds.append(dict(name=f'C3n{u}_s{s}', domain=d, path=str(ROOT / st['path'])))
        for e in eds:
            v = dev_l2(load_editor(eng, e['path']), 'bart', d, 'natural', scale)
            out[f"{d}/{e['name']}"] = dict(dev_l2=v, rrr16=rrr, ratio=v / rrr, converged=v <= 1.2 * rrr)
    return out


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; part = sys.argv[sys.argv.index('--part') + 1]; t0 = time.time(); eng = engine5(bb)
    out = ROOT / f'results/train_new_{bb}_{part}.json'; res = read(out) if out.exists() else {}
    if part == 'M':
        md = read(ROOT / f'results/gates_{bb}.json')['M_domains']
        for unit, v, b_, doms, seeds, fam, kind, upd in NEW6:
            if unit != 'M' or b_ != bb: continue
            for d in [x for x in doms if x in md]:
                for s in seeds:
                    st = None
                    for u in (upd, 2 * upd):
                        r = (c1 if v == 'C1n' else sc3u4)(eng, bb, d, s, u); res[f'{v}/{d}/s{s}/u{u}'] = dict(dev=r, admitted=r['rate'] >= .90); st = u
                        print('train', bb, v, d, s, u, round(r['rate'], 4), flush=True)
                        if r['rate'] >= .90: break
                    ok = res[f'{v}/{d}/s{s}/u{st}']['admitted']
                    res[f'{v}/{d}/s{s}'] = dict(updates=st, family=fam, kind=kind, admitted=ok, status='ok' if ok else 'cannot learn',
                                                path=str(new6_path(bb, v, d, s, st).relative_to(ROOT))); dump(out, res)
    elif part == 'C':
        assert bb == 'bart'
        for d in C_DOMAINS:
            for s in SEEDS:
                c3_run(eng, d, s)
                for u in (300, 450, 600, 900):
                    st = None
                    for uu in (u, 2 * u):
                        r = load(new6_path('bart', f'C3n{uu}', d, s, uu))['dev_single']; res[f'C3n{u}/{d}/s{s}/u{uu}'] = dict(dev=r, admitted=r['rate'] >= .90); st = uu
                        if r['rate'] >= .90: break
                    ok = res[f'C3n{u}/{d}/s{s}/u{st}']['admitted']
                    res[f'C3n{u}/{d}/s{s}'] = dict(updates=st, family='state', admitted=ok, status='ok' if ok else 'cannot learn',
                                                   path=str(new6_path('bart', f'C3n{st}', d, s, st).relative_to(ROOT)))
                    print('train C3', d, s, u, st, ok, flush=True)
                dump(out, res)
        res['convergence'] = convergence(eng, res); dump(out, res)
    else:
        assert bb == 'bart'
        for kind, upd, Sset, doms in K_NEW:
            for d in doms:
                for s in SEEDS:
                    name = k_name(kind, upd); st = None
                    for u in (upd, 2 * upd):
                        r = k_editor(eng, kind, name, d, s, u, Sset); gated = d in ('name3', 'bind3fix')
                        res[f'{name}/{d}/s{s}/u{u}'] = dict(dev_single=r, admitted=r['rate'] >= .95 if gated else None); st = u
                        print('K train', name, d, s, u, round(r['rate'], 4), flush=True)
                        if not gated or r['rate'] >= .95: break
                    ok = d == 'bind3' or res[f'{name}/{d}/s{s}/u{st}']['admitted']
                    res[f'{name}/{d}/s{s}'] = dict(kind=kind, updates=st, admitted=ok, status='ok' if ok else 'cannot learn', path=f'local/k_{name}_{d}_s{s}_u{st}.pt')
                    dump(out, res)
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump(out, res)


if __name__ == '__main__':
    main()
