"""v8 seed registry (CPU, before the lock; PLAN v7 design rule 3). The historical editors (v1-v7) are v7's registry
(composability_mechanisms_v6/seed_registry.json); the v8 editors found on disk are added with the same procedure / data-order hash rule.
v8 procedures: C1 / C3-U4 / slot C3-U4 on month-nat (bart, t5) and on weekday / month for T5Gemma 9B-9B (a new backbone); E2's OR-U8 with
UV rank 128 and full rank (bind3); D's CE slot editor on Gemma 2 2B (month). A v8 editor may not share a data-order hash with any earlier
editor or with another v8 editor of a different path. Output: seed_registry.json (this directory)."""
import hashlib
import re
from symutil import *

V7D = EXP / 'composability_mechanisms_v6'
TRAIN = {'month-nat': ROOT / 'data/month-nat/worlds.jsonl', 'weekday': V1 / 'data/weekday/worlds.jsonl', 'month': V1 / 'data/month/worlds.jsonl',
         'bind3': EXP / 'composability_mechanisms_v3/data/bind3/worlds.jsonl'}


def entry(family, bb, d, seed, path, extra=''):
    obj = {'C1': 'CE single', 'C3U4': 'CE+L2 unrolled|S=(1, 2, 3, 4)', 'SC3U4': 'slot CE+L2 unrolled|S=(1, 2, 3, 4)'}.get(family, family)
    p = f'{obj}|{bb}|{d}{extra}'; ds = sha(TRAIN[d])
    return dict(round='v8', family=family, procedure=p, backbone=bb, domain=d, seed=int(seed), path=str(Path(path).relative_to(REPO)),
                data_order_hash=hashlib.sha256(json.dumps([p, int(seed), ds]).encode()).hexdigest())


def new8():
    E = []
    for f in sorted((ROOT / 'local').glob('n8_*_s*_u*.pt')):
        m = re.match(r'n8_(bart|t5_9b|t5)_(C1|C3U4|SC3U4)_([\w-]+)_s(\d+)_u\d+', f.stem); E.append(entry(m[2], m[1], m[3], m[4], f))
    for f in sorted((ROOT / 'local').glob('e2_*_bind3_s*_u8000.pt')):
        m = re.match(r'e2_(OR128|ORfull)_bind3_s(\d+)', f.stem); E.append(entry(f'OR-U unrolled L2|S={tuple(range(1, 9))}|{m[1]}', 'bart', 'bind3', m[2], f))
    for f in sorted((ROOT / 'local').glob('d_C1_s*.pt')):
        m = re.match(r'd_C1_s(\d+)', f.stem); E.append(entry('CE slot (decoder-only, layer-l latent)', 'gemma2_2b', 'month', m[1], f))
    return E


def main():
    require_slurm(); old = read(V7D / 'seed_registry.json'); hist = old['historical'] + old['v7']; new = new8()
    oh = {}
    for e in hist: oh.setdefault(e['data_order_hash'], []).append(e['path'])
    clash = [dict(new=e['path'], old=oh[e['data_order_hash']]) for e in new if e['data_order_hash'] in oh]
    nd = {}
    for e in new: nd.setdefault(e['data_order_hash'], set()).add(re.sub(r'_u\d+$', '', Path(e['path']).stem))
    within = [sorted(v) for v in nd.values() if len(v) > 1]
    dump(ROOT / 'seed_registry.json', dict(rule='PLAN v7 design rule 3; procedure excludes the number of updates (prefix runs)', historical_source=str(V7D / 'seed_registry.json'),
                                         historical_sha256=sha(V7D / 'seed_registry.json'), n_historical=len(hist), v8=new, n_v8=len(new), clashes=clash, within_v8=within,
                                         pass_=not clash and not within))
    print('historical', len(hist), 'v8', len(new), 'clashes', len(clash), 'within', len(within), flush=True)


if __name__ == '__main__':
    main()
