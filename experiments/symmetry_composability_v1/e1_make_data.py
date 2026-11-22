"""E1.0 worlds for the five new domains: train 96 / dev 32 / confirm 160, confirm core keys disjoint from all history."""
import random
import time
from symutil import *
import sym_semantics as S

SEED = 2026112201
SPLITS = [('train', 96), ('dev', 32), ('confirm', 160)]


def history_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl'))
    fs += [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    return fs


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def main():
    require_slurm(); t0 = time.time()
    hist = set(); files = {}
    for f in history_files():
        rs = rows(f); files[str(f.relative_to(REPO))] = dict(sha256=sha(f), worlds=len(rs))
        hist.update(key(w) for w in rs)
    used = set(hist); summary = {}
    for di, d in enumerate(S.DOMAINS):
        rng = random.Random(SEED + di); out = []; seen_text = set()
        while len(out) < sum(n for _, n in SPLITS):
            people = rng.sample(S.NAMES, 3); obj = rng.choice(S.OBJECTS); col = rng.choice(S.COLORS)
            w = dict(domain=d, people=people, object=obj, color=col, quantity=rng.randrange(1, 10), status=rng.choice(S.STATUSES))
            start = rng.choice(S.states(d))
            k = key(w)
            if k in used:
                continue
            texts = {S.render(w, s, t) for s in S.states(d) for t in (0, 3)}
            if texts & seen_text:
                continue
            used.add(k); seen_text |= texts
            i = len(out); split = 'train' if i < 96 else 'dev' if i < 128 else 'confirm'
            w.update(world_id=f'{d}_{i:04d}', split=split, start_state=start); out.append(w)
        write(f'data/{d}/worlds.jsonl', out)
        write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=t, state=s, text=S.render(w, s, t))
                                          for w in out for t in (0, 3) for s in S.states(d)])
        summary[d] = {sp: sum(w['split'] == sp for w in out) for sp, _ in SPLITS}
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + domain index in sym_semantics.DOMAINS)', splits=dict(SPLITS),
                                    core_key='(people, object, color, quantity, status)', history_files=files, history_keys=len(hist),
                                    counts=summary, files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in S.DOMAINS for n in ('worlds.jsonl', 'renders.jsonl')},
                                    sym_semantics_sha256=sha(ROOT / 'sym_semantics.py'), seconds=time.time() - t0))
    print(summary, flush=True)


if __name__ == '__main__':
    main()
