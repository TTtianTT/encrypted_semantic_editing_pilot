"""v9 editors (GPU, before the lock; train worlds only, admission on dev only; PLAN v9 sections 3-4). --backbone bart|t5 --part S|B2|B3|B4.
Idempotent (an editor already saved is not retrained). Admission (v6 B4 rule, kept by v8 C1 and v9 section 1): single-step editors dev single
>= 0.90; unrolled editors dev in-horizon plus R_{S_max} >= 0.90; otherwise one retrain with twice the updates; otherwise 'cannot learn'.
S  (section 4): C1 (CE, 600 updates) and C3-U4 (CE + L2, lambda 1, S in 1..4, 1200 updates) with seeds 45-49; BART weekday and month,
   T5Gemma 2B-2B month.
B2 (LoReFT, appendix A.2): LoReFT-C1 (C1 training) and LoReFT-C3U4 (C3-U4 training); seeds 45-47; both backbones, weekday and month.
B3 (capacity): full-rank residual linear and MLP residual, one-step CE (C1 training); seeds 45-47; both backbones, weekday and month.
B4 (horizon, CE only, no L2, rank-16 backend editor, 1200 updates): U8 (S <= 8), U16 (S <= 16), Urand (S uniform in 1..2N; appendix A.3);
   BART weekday and month; T5Gemma month U8 only; seeds 45-47.
Output: local/n9_<bb>_<v>_<d>_s<s>_u<upd>.pt, results/train9_<bb>_<part>.json, results/train_new/*.jsonl."""
import time
from lib9 import *


def path9(bb, v, d, s, upd):
    return ROOT / f'local/n9_{bb}_{v}_{d}_s{s}_u{upd}.pt'


def single(eng, bb, v, kind, d, s, upd):
    f = path9(bb, v, d, s, upd)
    if f.exists(): return load(f)['dev']
    ed, hist, scale = train_editor(eng, bb, d, 'natural', 'C1', s, updates=upd, kind=kind)
    r = dev_single(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')})
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind=kind, variant=v, dev=r, dev_kind='single', l2_scale=scale, updates=upd, group='C1'))
    write(f'results/train_new/n9_{bb}_{v}_{d}_s{s}_u{upd}.jsonl', hist); return r


def unrolled(eng, bb, v, kind, d, s, upd, Sset, l2):
    f = path9(bb, v, d, s, upd)
    if f.exists(): return load(f)['dev']
    ed, hist, scale = train_unrolled(eng, bb, d, s, list(Sset), updates=upd, l2_weight=l2, kind=kind)
    r = dev_chain(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')}, ['plus'] * max(Sset))[-1]
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind=kind, variant=v, dev=r, dev_kind=f'R_{max(Sset)}', Sset=list(Sset), l2_weight=l2,
                 l2_scale=scale, updates=upd))
    write(f'results/train_new/n9_{bb}_{v}_{d}_s{s}_u{upd}.jsonl', hist); return r


def jobs(bb, part):
    doms = ['weekday', 'month'] if not (part == 'S' and bb == 't5') else ['month']
    N = lambda d: len(S.states(d)); out = []
    for d in doms:
        if part == 'S':
            out += [('C1', 'rank16', d, s, 600, None, 0) for s in range(45, 50)] + [('C3U4', 'rank16', d, s, 1200, range(1, 5), 1.0) for s in range(45, 50)]
        elif part == 'B2':
            out += [('LoReFTC1', 'loreft', d, s, 600, None, 0) for s in (45, 46, 47)] + [('LoReFTC3U4', 'loreft', d, s, 1200, range(1, 5), 1.0) for s in (45, 46, 47)]
        elif part == 'B3':
            out += [(v, k, d, s, 600, None, 0) for v, k in (('FullC1', 'full'), ('MLPC1', 'mlp')) for s in (45, 46, 47)]
        elif part == 'B4':
            if bb == 't5' and d != 'month': continue
            vs = [('U8', range(1, 9))] + ([] if bb == 't5' else [('U16', range(1, 17)), ('Urand', range(1, 2 * N(d) + 1))])
            out += [(v, 'rank16', d, s, 1200, Ss, 0.0) for v, Ss in vs for s in (45, 46, 47)]
    return out


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; part = sys.argv[sys.argv.index('--part') + 1]; t0 = time.time(); eng = engine8(bb)
    out = ROOT / f'results/train9_{bb}_{part}.json'; res = read(out) if out.exists() else {}
    for v, kind, d, s, upd, Sset, l2 in jobs(bb, part):
        key = f'{v}/{d}/s{s}'
        if key in res: continue
        fn = (lambda u: single(eng, bb, v, kind, d, s, u)) if Sset is None else (lambda u: unrolled(eng, bb, v, kind, d, s, u, Sset, l2))
        t1 = time.time(); r = fn(upd); rec = dict(updates=upd, dev=r, admitted=r['rate'] >= .90, kind=kind)
        if not rec['admitted']:
            r2 = fn(2 * upd); rec = dict(updates=2 * upd, dev=r2, first=r, admitted=r2['rate'] >= .90, kind=kind, note=None if r2['rate'] >= .90 else 'cannot learn')
        rec['seconds'] = time.time() - t1; rec['path'] = str(path9(bb, v, d, s, rec['updates']).relative_to(ROOT)); res[key] = rec; dump(out, res)
        print('train9', bb, part, key, rec['updates'], round(rec['dev']['rate'], 4), rec['admitted'], round(rec['seconds']), flush=True)
    res['_resources'] = eng.resources(); res['_seconds'] = res.get('_seconds', 0) + time.time() - t0; dump(out, res)


if __name__ == '__main__':
    main()
