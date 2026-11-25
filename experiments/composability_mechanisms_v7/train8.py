"""v8 editors (GPU, before the lock; train worlds only, admission on dev only; PLAN v7 C2, C3; admission rule of v6 B4 kept by C1):
single-step editors dev single >= 0.90; unrolled editors dev in-horizon (plus R_4) >= 0.90; otherwise one retrain with twice the updates;
otherwise 'cannot learn' (reported). Idempotent (an editor already saved is not retrained). Seeds 50-52 (new for v8; every v8 procedure is
new - new domain month-nat or new backbone - so no data-order hash can repeat; seed_registry8.py checks).
--part N --backbone bart|t5: full-sequence C1_nat (CE, 600 updates) on month-nat; BART also the slot C3-U4_nat (S <= 4, 1200 updates;
exploratory).
--part G --backbone t5_9b: C1 (600 updates) and C3-U4 (lambda = 1, S <= 4, 1200 updates) on weekday and month, template 0.
Output: local/n8_<bb>_<v>_<d>_s<s>_u<upd>.pt, results/train8_<bb>_<part>.json, results/train_new/<...>.jsonl."""
import time
from lib8 import *

SEEDS8 = (50, 51, 52)


def path8(bb, v, d, s, upd):
    return ROOT / f'local/n8_{bb}_{v}_{d}_s{s}_u{upd}.pt'


def c1(eng, bb, d, s, upd):
    f = path8(bb, 'C1', d, s, upd)
    if f.exists(): return load(f)['dev_single']
    ed, hist, scale = train_editor(eng, bb, d, 'natural', 'C1', s, updates=upd)
    r = dev_single(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')})
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_single=r, l2_scale=scale, updates=upd, group='C1'))
    write(f'results/train_new/{bb}_C1_{d}_s{s}_u{upd}.jsonl', hist); return r


def c3u4(eng, bb, d, s, upd):
    f = path8(bb, 'C3U4', d, s, upd)
    if f.exists(): return load(f)['dev_R4']
    ed, hist, scale = train_unrolled(eng, bb, d, s, [1, 2, 3, 4], updates=upd, l2_weight=1.0)
    r4 = dev_chain(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')}, ['plus'] * 4)[-1]
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_R4=r4, l2_scale=scale, updates=upd))
    write(f'results/train_new/{bb}_C3U4_{d}_s{s}_u{upd}.jsonl', hist); return r4


def sc3u4(eng, bb, d, s, upd):
    f = path8(bb, 'SC3U4', d, s, upd)
    if f.exists(): return load(f)['dev_R4']
    ed, hist, scale = train_unrolled_slot(eng, bb, d, s, (1, 2, 3, 4), updates=upd)
    r4 = dev_chain(eng, bb, d, 'natural', {op: SlotOp(ed[op], slots(bb, d, 'dev')) for op in ('plus', 'minus')}, ['plus'] * 4)[-1]
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, dev_R4=r4, slot_scale=scale, updates=upd, kind='SC3U4'))
    write(f'results/train_new/{bb}_SC3U4_{d}_s{s}_u{upd}.jsonl', hist); return r4


def admit(fn, eng, bb, d, s, upd):
    r = fn(eng, bb, d, s, upd)
    if r['rate'] >= .90: return dict(updates=upd, dev=r, admitted=True)
    r2 = fn(eng, bb, d, s, 2 * upd)
    return dict(updates=2 * upd, dev=r2, first=r, admitted=r2['rate'] >= .90, note=None if r2['rate'] >= .90 else 'cannot learn')


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; part = sys.argv[sys.argv.index('--part') + 1]; t0 = time.time(); eng = engine8(bb)
    out = ROOT / f'results/train8_{bb}_{part}.json'; res = read(out) if out.exists() else {}
    if part == 'N':
        jobs = [('C1', c1, S.NAT, 600)] + ([('SC3U4', sc3u4, S.NAT, 1200)] if bb == 'bart' else [])
    else:
        assert part == 'G' and bb == 't5_9b'
        g = read(ROOT / 'results/g_prep_t5_9b.json')
        if not g.get('gate'): dump(out, dict(skipped='9B-9B reconstruction gate failed (g_prep_t5_9b.json); G stops (PLAN C5)')); return
        jobs = [(v, fn, d, u) for d in ('weekday', 'month') for v, fn, u in (('C1', c1, 600), ('C3U4', c3u4, 1200))]
    for v, fn, d, upd in jobs:
        for s in SEEDS8:
            key = f'{v}/{d}/s{s}'
            if key in res: continue
            res[key] = admit(fn, eng, bb, d, s, upd); print('train8', bb, key, res[key]['updates'], round(res[key]['dev']['rate'], 4), res[key]['admitted'], flush=True)
            dump(out, res)
    res['_resources'] = eng.resources(); res['_seconds'] = res.get('_seconds', 0) + time.time() - t0; dump(out, res)


if __name__ == '__main__':
    main()
