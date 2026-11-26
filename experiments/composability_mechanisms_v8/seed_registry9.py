"""v9 seed registry (CPU, before the lock; PLAN v7 design rule 3, PLAN v9 section 1). Historical editors: v8's registry (v1-v7 entries plus
v8's own, composability_mechanisms_v7/seed_registry.json). v9 editors found on disk: S (C1, C3-U4 seeds 45-49), B2 (LoReFT-C1, LoReFT-C3U4),
B3 (Full-C1, MLP-C1), B4 (U8, U16, Urand; CE only), DO (decoder-only CE slot and slot C3-U4 editors per model and domain). The procedure
string carries the objective, backbone, domain, editor family and unroll set, so families never share a data-order hash. Asserts: no v9
editor repeats a historical data order; no two v9 editors of different paths share one. Output: seed_registry.json."""
import hashlib
import re
from symutil import *

V8D = EXP / 'composability_mechanisms_v7'; V1D = EXP / 'symmetry_composability_v1'
TRAIN = lambda d: (V8D / 'data/month-nat/worlds.jsonl') if d == 'month-nat' else (V1D / f'data/{d}/worlds.jsonl')
OBJ = {'C1': 'CE single', 'C3U4': 'CE+L2 unrolled|S=(1, 2, 3, 4)', 'LoReFTC1': 'CE single|loreft', 'LoReFTC3U4': 'CE+L2 unrolled|S=(1, 2, 3, 4)|loreft',
       'FullC1': 'CE single|full', 'MLPC1': 'CE single|mlp', 'U8': 'CE unrolled|S=1..8', 'U16': 'CE unrolled|S=1..16', 'Urand': 'CE unrolled|S=1..2N'}


def entry(fam, bb, d, seed, path):
    p = f'{fam}|{bb}|{d}'; return dict(round='v9', procedure=p, backbone=bb, domain=d, seed=int(seed), path=str(Path(path).relative_to(REPO)),
                                       data_order_hash=hashlib.sha256(json.dumps([p, int(seed), sha(TRAIN(d))]).encode()).hexdigest())


def new9():
    E = []
    for f in sorted((ROOT / 'local').glob('n9_*_s*_u*.pt')):
        m = re.match(r'n9_(bart|t5)_(\w+?)_(weekday|month)_s(\d+)_u\d+', f.stem); E.append(entry(OBJ[m[2]], m[1], m[3], m[4], f))
    for f in sorted((ROOT / 'local').glob('do_*_C*_s*.pt')):
        m = re.match(r'do_(gemma|qwen)_(C1|C3U4)_([\w-]+)_s(\d+)', f.stem); E.append(entry(f'decoder-only slot {OBJ[m[2]]}', m[1], m[3], m[4], f))
    return E


def main():
    require_slurm(); old = read(V8D / 'seed_registry.json'); hist = old['historical'] + old['v8']; new = new9(); oh = {}
    for e in hist: oh.setdefault(e['data_order_hash'], []).append(e['path'])
    clash = [dict(new=e['path'], old=oh[e['data_order_hash']]) for e in new if e['data_order_hash'] in oh]
    nd = {}
    for e in new: nd.setdefault(e['data_order_hash'], set()).add(re.sub(r'_u\d+$', '', Path(e['path']).stem))
    within = [sorted(v) for v in nd.values() if len(v) > 1]
    dump(ROOT / 'seed_registry.json', dict(rule='PLAN v7 design rule 3; procedure excludes the number of updates (prefix runs)', historical_sha256=sha(V8D / 'seed_registry.json'),
                                         n_historical=len(hist), v9=new, n_v9=len(new), clashes=clash, within_v9=within, pass_=not clash and not within))
    print('historical', len(hist), 'v9', len(new), 'clashes', len(clash), 'within', len(within), flush=True)


if __name__ == '__main__':
    main()
