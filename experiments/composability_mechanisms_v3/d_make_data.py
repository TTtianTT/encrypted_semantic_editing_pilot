"""D (CPU): v4 worlds. confirm4 = 160 new worlds for weekday, month, compass, hour, compass8, season (template 0) and bind3, name3
(template 3); new domains also get train 96 / dev 32; X-unit train 480 / dev 64 for bind3 and name3 (template 3).
Every new world's rendered texts (all states) are disjoint from every rendered text in the repository's experiments
(symmetry_composability_v1, composability_mechanisms_v1, composability_mechanisms_v2, four_domain_state_coverage_v1, and the
canonical/manifold/operator-residual world files) and from all other new worlds; core keys are also disjoint from history.
bind3fix (DEVIATIONS #2): with the v3 fixed participant list only (object, color, quantity) varies, 360 combinations, of which v3
used 288. confirm4 = every remaining fresh combination; X-unit train/dev reuse the 288 v3 bind3fix worlds (train 224, dev 64)."""
import random
import time
from symutil import *
import sym4_semantics as S

SEED = 2026112330
V3DIR = EXP / 'composability_mechanisms_v2'; V2DIR = EXP / 'composability_mechanisms_v1'
PLAN = {'weekday': [('confirm4', 160)], 'month': [('confirm4', 160)], 'compass': [('confirm4', 160)],
        'hour': [('train', 96), ('dev', 32), ('confirm4', 160)], 'compass8': [('train', 96), ('dev', 32), ('confirm4', 160)],
        'season': [('train', 96), ('dev', 32), ('confirm4', 160)],
        'bind3': [('train', 480), ('dev', 64), ('confirm4', 160)], 'name3': [('train', 480), ('dev', 64), ('confirm4', 160)],
        'bind3fix': [('confirm4', 160)]}
ALL = list(PLAN)


def tmpl(d): return 3 if d in S.S1B else 0


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def history_world_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    fs += sorted((V1 / 'data').glob('*/worlds.jsonl')) + sorted((V2DIR / 'data').glob('*/worlds.jsonl')) + sorted((V3DIR / 'data').glob('*/worlds.jsonl'))
    return [f for f in fs if f.exists()]


def history_text_files():
    fs = sorted((V1 / 'data').glob('*/renders.jsonl')) + sorted((V2DIR / 'data').glob('*/renders.jsonl')) + sorted((V3DIR / 'data').glob('*/renders.jsonl'))
    fs += sorted((SOURCE / 'data').glob('*/*.jsonl')) + sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl'))
    fs += [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    return [f for f in fs if f.exists()]


def texts_of(r):
    return [v for k, v in r.items() if k in ('text', 'source', 'target') and isinstance(v, str)]


def history_texts():
    seen = set(); files = {}
    for f in history_text_files():
        n0 = len(seen)
        for r in rows(f): seen.update(texts_of(r))
        files[str(f.relative_to(REPO))] = dict(sha256=sha(f), new_texts=len(seen) - n0)
    # v2 pron3/name3/bind3 train/dev re-rendered with template 3 (used by v3) are already in v3 renders; v2 S1b worlds re-rendered
    # with every template as a safeguard
    for d in ('pron3', 'name3', 'bind3'):
        for w in rows(V2DIR / f'data/{d}/worlds.jsonl'):
            for t in (0, 3): seen.update(S.render(w, s, t) for s in S.states(d))
    return seen, files


def main():
    require_slurm(); t0 = time.time()
    hist_keys = set(); wfiles = {}
    for f in history_world_files():
        rs = rows(f); wfiles[str(f.relative_to(REPO))] = dict(sha256=sha(f), worlds=len(rs)); hist_keys.update(key(w) for w in rs if 'people' in w)
    seen, tfiles = history_texts(); n_hist_texts = len(seen); used = set(hist_keys); counts = {}; out_all = {}
    for di, d in enumerate(ALL):
        rng = random.Random(SEED + di); out = []; plan = PLAN[d]; t = tmpl(d)
        if d == 'bind3fix':
            v3 = rows(V3DIR / 'data/bind3fix/worlds.jsonl'); used3 = {(w['object'], w['color'], int(w['quantity'])) for w in v3}
            combos = [(o, c, q) for o in S.OBJECTS for c in S.COLORS for q in range(1, 10) if (o, c, q) not in used3]
            rng.shuffle(combos)
            for o, c, q in combos:
                if len(out) >= 160: break
                sts = list(S.STATUSES); rng.shuffle(sts)      # status is not rendered in template 3: pick one whose core key is unused
                cand = [dict(domain=d, people=list(S.FIX3), object=o, color=c, quantity=q, status=st_) for st_ in sts]
                cand = [w for w in cand if key(w) not in used]
                if not cand: continue
                w = cand[0]; texts = {S.render(w, s, t) for s in S.states(d)}
                if texts & seen: continue
                seen |= texts; used.add(key(w))
                w.update(world_id=f'{d}_c4_{len(out):04d}', split='confirm4', start_state=rng.choice(S.states(d))); out.append(w)
            # X-unit train/dev: the 288 v3 bind3fix worlds (texts already rendered in v3; not text-fresh, see DEVIATIONS #2)
            tr = [w for w in v3 if w['split'] == 'train'] + [w for w in v3 if w['split'] == 'confirm3'][:128]
            dv = [w for w in v3 if w['split'] == 'dev'] + [w for w in v3 if w['split'] == 'confirm3'][128:]
            assert len(tr) == 224 and len(dv) == 64
            reuse = []
            for split, ws in (('train', tr), ('dev', dv)):
                for w in ws:
                    reuse.append(dict({k: v for k, v in w.items() if k not in ('world_id', 'split')}, world_id=f'{d}_v4_{len(reuse):04d}', split=split,
                                      origin_world_id=w['world_id']))
            out = reuse + out
        else:
            total = sum(n for _, n in plan); bounds = np.cumsum([n for _, n in plan]); tries = 0
            while len(out) < total:
                tries += 1; assert tries < 10 ** 6, f'{d}: cannot find enough fresh worlds'
                w = dict(domain=d, people=rng.sample(S.NAMES, 3), object=rng.choice(S.OBJECTS), color=rng.choice(S.COLORS),
                         quantity=rng.randrange(1, 10), status=rng.choice(S.STATUSES))
                start = rng.choice(S.states(d)); k = key(w)
                if k in used: continue
                texts = {S.render(w, s, t) for s in S.states(d)}
                if texts & seen: continue
                used.add(k); seen |= texts; i = len(out); split = plan[int(np.searchsorted(bounds, i, side='right'))][0]
                w.update(world_id=f'{d}_c4_{i:04d}' if split == 'confirm4' else f'{d}_v4_{i:04d}', split=split, start_state=start); out.append(w)
        write(f'data/{d}/worlds.jsonl', out); out_all[d] = out
        write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=t, state=s, text=S.render(w, s, t))
                                          for w in out for s in S.states(d)])
        counts[d] = {sp: sum(w['split'] == sp for w in out) for sp in ('train', 'dev', 'confirm4')}
        print(d, counts[d], flush=True)
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + index in ALL)', all=ALL, plan=PLAN, counts=counts, bind3fix_people=S.FIX3,
                                    bind3fix_seed=S.FIX3_SEED, maps=S.MAPS, core_key='(people, object, color, quantity, status)',
                                    text_rule='all state renders of a new world disjoint from every historical text and every other new world',
                                    history_world_files=wfiles, history_text_files=tfiles, history_keys=len(hist_keys), history_texts=n_hist_texts,
                                    files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in ALL for n in ('worlds.jsonl', 'renders.jsonl')},
                                    seconds=time.time() - t0))


if __name__ == '__main__':
    main()
