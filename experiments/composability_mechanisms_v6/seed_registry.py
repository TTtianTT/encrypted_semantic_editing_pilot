"""Seed registry (CPU, before the lock; PLAN v7 design rule 3). Every trained editor of v1-v6 found on disk, as (training procedure, seed,
data-order hash). The training procedure is the editor family with everything that determines the batch sequence: objective, backbone,
domain (training data), batch construction and the set S of unroll lengths (unrolled editors); the number of updates is not part of it,
because a shorter run is a prefix of a longer one (v6 C3n600 = v1 C3). data-order hash = sha256 of (procedure, seed, sha256 of the train
data file). A v7 editor may not share a data-order hash with any earlier editor (lock.py asserts). Output: seed_registry.json."""
import hashlib
import re
from symutil import *

V2D = EXP / 'composability_mechanisms_v1'; V3D = EXP / 'composability_mechanisms_v2'; V4D = EXP / 'composability_mechanisms_v3'
V5D = EXP / 'composability_mechanisms_v4'; V6D = EXP / 'composability_mechanisms_v5'
TRAIN = {'weekday': V1 / 'data/weekday/worlds.jsonl', 'month': V1 / 'data/month/worlds.jsonl', 'bind3': V4D / 'data/bind3/worlds.jsonl',
         'name3': V4D / 'data/name3/worlds.jsonl', 'bind3fix': V4D / 'data/bind3fix/worlds.jsonl'}


def proc(family, bb, d, Sset=None):
    obj = {'C3': 'CE+L2 single', 'C1': 'CE single', 'L2': 'L2 single', 'C3U4': 'CE+L2 unrolled', 'C1U4': 'CE unrolled', 'SC3U4': 'slot CE+L2 unrolled'}.get(family, f'{family} unrolled L2')
    return f'{obj}|{bb}|{d}|S={Sset}' if Sset else f'{obj}|{bb}|{d}'


def data_sha(d):
    f = TRAIN.get(d) or (V5D / f'data/{d}/worlds.jsonl' if d.endswith('-mt') else None)
    return sha(f) if f and f.exists() else None


def entry(round_, family, bb, d, seed, path, Sset=None):
    p = proc(family, bb, d, Sset); ds = data_sha(d)
    return dict(round=round_, family=family, procedure=p, backbone=bb, domain=d, seed=int(seed), Sset=Sset, path=str(Path(path).relative_to(REPO)),
                data_order_hash=hashlib.sha256(json.dumps([p, int(seed), ds]).encode()).hexdigest())


def scan():
    E = []
    for f in sorted((V1 / 'local').glob('e1_C[13]_*_s*_0600.pt')):
        m = re.match(r'e1_(C[13])_(\w+)_s(\d+)_0600', f.stem); E.append(entry('v1', m[1], 'bart', m[2], m[3], f))
    for f in sorted((V3D / 'local').glob('a_C3_*_s*.pt')):
        m = re.match(r'a_C3_(l3|l10|rrrinit)_(\w+)_s(\d+)', f.stem)
        if m: E.append(entry('v3', f'C3-{m[1]}', 'bart', m[2], m[3], f))
    for f in sorted((V4D / "local").glob("p2_*_s*.pt")):
        m = re.match(r"p2_([abc])_(C3|L2)_(\d+)_(\w+)_s(\d+)", f.stem)
        if m: E.append(entry("v4", m[2], "bart", m[4], m[5], f))
    for f in sorted((V4D / "local").glob("x_Att_*_s*.pt")):
        m = re.match(r"x_Att_(\w+)_s(\d+)", f.stem)
        if m: E.append(entry("v4", "Att-L2", "bart", m[1], m[2], f))
    for f in sorted((V4D / "local").glob("u_C[13]U[4N]_*_s*.pt")):
        m = re.match(r"u_(C[13]U[4N])_(\w+?)_s(\d+)", f.stem)
        if m: E.append(entry('v4', m[1], 'bart', m[2], m[3], f, (1, 2, 3, 4)))
    for f in sorted((V5D / 'local').glob('n_*_s*_u*.pt')):
        m = re.match(r'n_(bart|t5)_(\w+?)_([\w-]+)_s(\d+)_u(\d+)', f.stem)
        if m:
            fam = {'C3n1200': 'C3', 'C3n2400': 'C3', 'C1U4n': 'C1U4', 'C3U4n': 'C3U4'}.get(m[2], m[2])
            E.append(entry('v5', fam, m[1], m[3], m[4], f, (1, 2, 3, 4) if 'U4' in m[2] else None))
    for f in sorted((V5D / 'local').glob('b_*_s*.pt')):
        m = re.match(r'b_(\w+?)_(\w+)_s(\d+)', f.stem)
        if m: E.append(entry('v5', f'{m[1]}-U', 'bart', m[2], m[3], f, (1, 2, 3, 4)))
    for f in sorted((V6D / 'local').glob('n6_*_s*_u*.pt')):
        m = re.match(r'n6_(bart|t5)_(\w+?)_([\w-]+)_s(\d+)_u(\d+)', f.stem)
        if m:
            fam = 'C3' if m[2].startswith('C3n') else m[2]
            E.append(entry('v6', fam, m[1], m[3], m[4], f, (1, 2, 3, 4) if m[2] == 'SC3U4' else None))
    for f in sorted((V6D / 'local').glob('k_*_s*_u*.pt')):
        m = re.match(r'k_(\w+?)U(\d)_([\w]+)_s(\d+)_u(\d+)', f.stem)
        if m: E.append(entry('v6', f'{m[1]}-U', 'bart', m[3], m[4], f, tuple(range(1, int(m[2]) + 1))))
    return E


def new7():
    E = []
    for f in sorted((ROOT / 'local').glob('n7_bart_C3n*_s*_u*.pt')):
        m = re.match(r'n7_bart_C3n\d+_(\w+)_s(\d+)_u\d+', f.stem); E.append(entry('v7', 'C3', 'bart', m[1], m[2], f))
    for f in sorted((ROOT / 'local').glob('k7_*_s*_u*.pt')):
        m = re.match(r'k7_(\w+?)U(\d)_(\w+)_s(\d+)_u(\d+)', f.stem); E.append(entry('v7', f'{m[1]}-U', 'bart', m[3], m[4], f, tuple(range(1, int(m[2]) + 1))))
    return E


def main():
    require_slurm(); old = scan(); new = new7(); oh = {}
    for e in old: oh.setdefault(e['data_order_hash'], []).append(e['path'])
    clash = [dict(new=e['path'], old=oh[e['data_order_hash']]) for e in new if e['data_order_hash'] in oh]
    newdup = {}
    for e in new: newdup.setdefault((e['data_order_hash'], e['path'].split('_u')[0].rsplit('_C3n', 1)[0]), []).append(e['path'])
    dump(ROOT / 'seed_registry.json', dict(rule='PLAN v7 design rule 3; procedure excludes the number of updates (prefix runs)', historical=old, v7=new,
                                         clashes=clash, n_historical=len(old), n_v7=len(new), pass_=not clash))
    print('historical', len(old), 'v7', len(new), 'clashes', len(clash), flush=True)


if __name__ == '__main__':
    main()
