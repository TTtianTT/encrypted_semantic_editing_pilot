"""E2 (exploratory; plan change 2026-11-25, PLAN.md end; BART, GPU <= 0.5 h): the binding write rank.
--stage train (before the lock): OR-U8 of v7 K7 (oracle routing, S <= 8, 8000 updates, AdamW 1e-3, batch 16, clip 1, unrolled L2; bind3
train) with the UV rank raised from 32 to 128, and a full-rank version (UV replaced by one zero-initialised d x d map); seeds 42-44 (a new
editor family, so no data-order hash repeats). Dev single step reported (not gated).
--stage run (after the lock): see e2_run in this file. Output: local/e2_<OR128|ORfull>_bind3_s<s>_u8000.pt, results/e2_train.json."""
import time
from lib8 import *

VARIANTS = {'OR128': 128, 'ORfull': None}
SEEDS_E2 = (42, 43, 44)


def epath(v, s):
    return ROOT / f'local/e2_{v}_bind3_s{s}_u8000.pt'


def train(eng):
    out = ROOT / 'results/e2_train.json'; res = read(out) if out.exists() else {}
    for v, rank in VARIANTS.items():
        for s in SEEDS_E2:
            key = f'{v}/s{s}'
            if key in res and epath(v, s).exists(): continue
            t0 = time.time(); ed, hist = train_k('bind3', s, 'OR', updates=8000, Sset=tuple(range(1, 9)), rank=rank)
            r = dev_single(eng, 'bart', 'bind3', 'natural', k_ops('OR', ed, slots('bart', 'bind3', 'dev'), name_positions('bind3', 'dev')))
            save(epath(v, s), dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind='OR', rank=rank, name=v, Sset=list(range(1, 9)), dev_single=r, updates=8000))
            write(f'results/train_new/e2_{v}_bind3_s{s}_u8000.jsonl', hist)
            res[key] = dict(dev_single=r, seconds=time.time() - t0, sha256=sha(epath(v, s))); dump(out, res); print('E2 train', key, round(r['rate'], 4), flush=True)
    res['_resources'] = eng.resources(); dump(out, res)


def main():
    require_slurm(); stage = sys.argv[sys.argv.index('--stage') + 1]; eng = engine8('bart')
    if stage == 'train': return train(eng)
    raise SystemExit('run stage: written after the lock')


if __name__ == '__main__':
    main()
