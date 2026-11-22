"""D: confirm2 (160 new worlds for each v1 domain) and the S1b binding domains (96/32/160). Core keys disjoint from
every v1 split and every historical world file."""
import random
import time
from symutil import *
import sym2_semantics as S

SEED = 2026112301
ALL = V1_DOMAINS + S1B_DOMAINS


def history_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    fs += [V1 / f'data/{d}/worlds.jsonl' for d in V1_DOMAINS]
    return fs


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def main():
    require_slurm(); t0 = time.time(); hist = set(); files = {}
    for f in history_files():
        rs = rows(f); files[str(f.relative_to(REPO))] = dict(sha256=sha(f), worlds=len(rs)); hist.update(key(w) for w in rs)
    used = set(hist); counts = {}
    for di, d in enumerate(ALL):
        rng = random.Random(SEED + di); out = []; seen = set()
        n_total = 160 if d in V1_DOMAINS else 288
        while len(out) < n_total:
            w = dict(domain=d, people=rng.sample(S.NAMES, 3), object=rng.choice(S.OBJECTS), color=rng.choice(S.COLORS),
                     quantity=rng.randrange(1, 10), status=rng.choice(S.STATUSES))
            start = rng.choice(S.states(d)); k = key(w)
            if k in used: continue
            texts = {S.render(w, s, t) for s in S.states(d) for t in (0, 3)}
            if texts & seen: continue
            used.add(k); seen |= texts; i = len(out)
            if d in V1_DOMAINS:
                w.update(world_id=f'{d}_c2_{i:04d}', split='confirm2')
            else:
                w.update(world_id=f'{d}_{i:04d}', split='train' if i < 96 else 'dev' if i < 128 else 'confirm')
            w['start_state'] = start; out.append(w)
        write(f'data/{d}/worlds.jsonl', out)
        write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=t, state=s, text=S.render(w, s, t))
                                          for w in out for t in (0, 3) for s in S.states(d)])
        counts[d] = {sp: sum(w['split'] == sp for w in out) for sp in sorted({w['split'] for w in out})}
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + index in V1_DOMAINS + S1B_DOMAINS)', counts=counts,
                                    core_key='(people, object, color, quantity, status)', history_files=files, history_keys=len(hist),
                                    files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in ALL for n in ('worlds.jsonl', 'renders.jsonl')},
                                    sym2_semantics_sha256=sha(ROOT / 'sym2_semantics.py'), seconds=time.time() - t0))
    print(counts, flush=True)


if __name__ == '__main__':
    main()
