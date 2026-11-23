"""New editors (GPU, before the lock; train only, admission on dev only; PLAN 2 new rule 4, 6.1, 9.1, 10.1). --backbone bart|t5
--part L|N|B. Idempotent: an editor already saved is not retrained.
L / N (lib5.NEW_EDITORS): single-step editors with the v4 train_editor (C1: CE; C3: CE + normalised L2, lambda = 1); C3n1200 is the
1200-update snapshot of the C3n2400 run (same seed, same batches), so its retrain at 2400 updates is C3n2400 itself; unrolled editors
with the v4 train_unrolled (S in 1..4, 1200 updates; C3U4: lambda = 1, C1U4: CE only). Admission: single-step dev single >= 0.90;
unrolled dev in-horizon (S = 4) plus R_4 >= 0.90; else one retrain with twice the updates; else 'cannot learn' (reported).
B (BART): Tok-U, Att1-U, Att2-U (appendix A.4) on bind3, name3, bind3fix, seeds 42-44, unrolled L2, 4000 updates. Admission on name3 and
bind3fix: dev single >= 0.95, else one retrain with 8000 updates, else B stops (bind3 is reported, not gated)."""
import time
from lib5 import *


def single(eng, bb, v, d, s, upd):
    f = new_editor_path(bb, v, d, s, upd)
    if f.exists(): return load(f)['dev_single']
    group = 'C3' if v.startswith('C3') else 'C1'
    if v == 'C3n1200':        # snapshot of the 2400-update run; its retrain at 2400 updates is C3n2400 itself
        if upd == 2400: return single(eng, bb, 'C3n2400', d, s, 2400)
        g = new_editor_path(bb, 'C3n2400', d, s, 2400)
        if not g.exists(): single(eng, bb, 'C3n2400', d, s, 2400)
        return load(f)['dev_single']
    snaps = (1200,) if v == 'C3n2400' and upd == 2400 else ()
    ed, hist, scale = train_editor(eng, bb, d, 'natural', group, s, updates=upd, snapshots=snaps)
    r = dev_single(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')})
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_single=r, l2_scale=scale, updates=upd, group=group))
    write(f'results/train_new/{bb}_{v}_{d}_s{s}_u{upd}.jsonl', hist)
    if snaps:
        source_path(); from backend import editors
        e2 = editors(eng.d, s); e2.load_state_dict(ed.snapshots[1200]); e2 = e2.eval().requires_grad_(False)
        r2 = dev_single(eng, bb, d, 'natural', {op: e2[op] for op in ('plus', 'minus')})
        save(new_editor_path(bb, 'C3n1200', d, s, 1200), dict(editor=ed.snapshots[1200], seed=s, dev_single=r2, l2_scale=scale, updates=1200, group=group,
                                                              note='snapshot at 1200 of the C3n2400 run'))
    return r


def unrolled(eng, bb, v, d, s, upd):
    f = new_editor_path(bb, v, d, s, upd)
    if f.exists(): return load(f)['dev_R4']
    ed, hist, scale = train_unrolled(eng, bb, d, s, [1, 2, 3, 4], updates=upd, l2_weight=1.0 if v.startswith('C3') else 0.0)
    r4 = dev_chain(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')}, ['plus'] * 4)[-1]
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_R4=r4, l2_scale=scale, updates=upd))
    write(f'results/train_new/{bb}_{v}_{d}_s{s}_u{upd}.jsonl', hist)
    return r4


def b_editor(eng, kind, d, s, upd):
    f = ROOT / f'local/b_{kind}_{d}_s{s}_u{upd}.pt'
    if f.exists(): return load(f)['dev_single']
    ed, hist = train_unrolled_l2('bart', d, s, kind, updates=upd)
    r = dev_single(eng, 'bart', d, 'natural', {op: ed[op] for op in ('plus', 'minus')})
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind=kind, dev_single=r, updates=upd))
    write(f'results/train_new/b_{kind}_{d}_s{s}_u{upd}.jsonl', hist)
    return r


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; part = sys.argv[sys.argv.index('--part') + 1]; t0 = time.time(); eng = engine5(bb)
    out = ROOT / f'results/train_new_{bb}_{part}.json'; res = read(out) if out.exists() else {}
    if part in ('L', 'N'):
        nd = read(ROOT / f'results/gates_{bb}.json')['N_domains'] if part == 'N' else None
        for b_, unit, v, d, seeds, fam, kind, upd in NEW_EDITORS:
            if b_ != bb or unit != part or (nd is not None and d not in nd): continue
            for s in seeds:
                st = None
                for u in (upd, 2 * upd):
                    r = (single if kind == 'single' else unrolled)(eng, bb, v, d, s, u); thr = .90
                    res[f'{v}/{d}/s{s}/u{u}'] = dict(dev=r, admitted=r['rate'] >= thr); st = u
                    print('train', bb, v, d, s, u, round(r['rate'], 4), flush=True)
                    if r['rate'] >= thr: break
                ok = res[f'{v}/{d}/s{s}/u{st}']['admitted']
                res[f'{v}/{d}/s{s}'] = dict(updates=st, family=fam, kind=kind, admitted=ok, status='ok' if ok else 'cannot learn',
                                            path=str(new_editor_path(bb, 'C3n2400' if (v, st) == ('C3n1200', 2400) else v, d, s, st).relative_to(ROOT)))
                dump(out, res)
    else:
        assert bb == 'bart'; stop = False
        for d in ('name3', 'bind3fix', 'bind3'):
            for kind in ('Tok', 'Att1', 'Att2'):
                for s in SEEDS:
                    st = None
                    for u in (4000, 8000):
                        r = b_editor(eng, kind, d, s, u); res[f'{kind}/{d}/s{s}/u{u}'] = dict(dev_single=r, admitted=r['rate'] >= .95 if d != 'bind3' else None); st = u
                        print('B train', kind, d, s, u, round(r['rate'], 4), flush=True)
                        if d == 'bind3' or r['rate'] >= .95: break
                    ok = d == 'bind3' or res[f'{kind}/{d}/s{s}/u{st}']['admitted']
                    res[f'{kind}/{d}/s{s}'] = dict(updates=st, admitted=ok, path=f'local/b_{kind}_{d}_s{s}_u{st}.pt'); stop |= not ok
                    dump(out, res)
        res['B_status'] = 'stop (admission)' if stop else 'go'
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump(out, res)


if __name__ == '__main__':
    main()
