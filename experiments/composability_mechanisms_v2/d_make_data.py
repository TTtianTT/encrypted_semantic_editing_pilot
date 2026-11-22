"""D: confirm3 (160 new worlds per v1 domain, template 0) and S1b' (template 3): new confirm3 worlds for pron3/name3/bind3
(train/dev reuse v2 worlds), and bind3fix (96/32/160, one fixed participant list). Core keys disjoint from all history."""
import random
import time
from symutil import *
import sym3_semantics as S
from lib3 import V2DIR, tmpl

SEED = 2026112320
ALL = V1_DOMAINS + S.S1B


def history_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    fs += [V1 / f'data/{d}/worlds.jsonl' for d in V1_DOMAINS] + sorted((V2DIR / 'data').glob('*/worlds.jsonl'))
    return fs


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def main():
    require_slurm(); t0 = time.time(); hist = set(); files = {}
    for f in history_files():
        rs = rows(f); files[str(f.relative_to(REPO))] = dict(sha256=sha(f), worlds=len(rs)); hist.update(key(w) for w in rs)
    used = set(hist); counts = {}
    for di, d in enumerate(ALL):
        rng = random.Random(SEED + di); out = []; fixkeys = set()
        # texts already used anywhere for this domain (v1 all splits, v2 all splits, v2 train/dev re-rendered with template 3)
        seen = set()
        for f in (V1 / f'data/{d}/renders.jsonl', V2DIR / f'data/{d}/renders.jsonl'):
            if f.exists(): seen |= {r['text'] for r in rows(f)}
        if d in ('pron3', 'name3', 'bind3'):
            seen |= {S.render(w, s, tmpl(d)) for w in rows(V2DIR / f'data/{d}/worlds.jsonl') if w['split'] in ('train', 'dev') for s in S.states(d)}
        seen_hist = len(seen)
        plan = [('confirm3', 160)] if d != 'bind3fix' else [('train', 96), ('dev', 32), ('confirm3', 160)]
        total = sum(n for _, n in plan); bounds = np.cumsum([n for _, n in plan])
        while len(out) < total:
            w = dict(domain=d, people=list(S.FIX3) if d == 'bind3fix' else rng.sample(S.NAMES, 3), object=rng.choice(S.OBJECTS),
                     color=rng.choice(S.COLORS), quantity=rng.randrange(1, 10), status=rng.choice(S.STATUSES))
            start = rng.choice(S.states(d)); k = key(w)
            if k in used: continue
            if d == 'bind3fix':   # people fixed and status not rendered: (object, color, quantity) must be unique within the domain
                fk = (w['object'], w['color'], w['quantity'])
                if fk in fixkeys: continue
            texts = {S.render(w, s, tmpl(d)) for s in S.states(d)}
            if texts & seen: continue
            used.add(k); seen |= texts; i = len(out); split = plan[int(np.searchsorted(bounds, i, side='right'))][0]
            if d == 'bind3fix': fixkeys.add(fk)
            w.update(world_id=f'{d}_c3_{i:04d}' if split == 'confirm3' else f'{d}_{i:04d}', split=split, start_state=start); out.append(w)
        write(f'data/{d}/worlds.jsonl', out)
        alls = out if d in V1_DOMAINS or d == 'bind3fix' else [w for w in rows(V2DIR / f'data/{d}/worlds.jsonl') if w['split'] in ('train', 'dev')] + out
        write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=tmpl(d), state=s, text=S.render(w, s, tmpl(d)))
                                          for w in alls for s in S.states(d)])
        counts[d] = {sp: sum(w['split'] == sp for w in alls) for sp in sorted({w['split'] for w in alls})} | {'historical_texts_excluded': seen_hist}
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + index in V1_DOMAINS + S1B)', counts=counts, bind3fix_people=S.FIX3,
                                    bind3fix_seed=S.FIX3_SEED, maps=S.MAPS, core_key='(people, object, color, quantity, status); bind3fix additionally unique (object, color, quantity) within domain',
                                    history_files=files, history_keys=len(hist), files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in ALL for n in ('worlds.jsonl', 'renders.jsonl')},
                                    seconds=time.time() - t0))
    print(counts, S.FIX3, flush=True)


if __name__ == '__main__':
    main()
