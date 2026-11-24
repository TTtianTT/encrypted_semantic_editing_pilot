"""D (CPU): v6 confirm6 worlds (PLAN B4).
- M: weekday-mt, month-mt, hour-mt, 160 fresh worlds each (BART; month-mt also T5Gemma), each rendered with one of v5's 9 held-out templates
  (data/templates_mt.json and data/templates_split.json are byte-identical copies of v5's), a fixed distractor != start.
- C: weekday, month (template 0), 160 fresh each.
- K: bind3, name3 (template 3), 160 fresh each; bind3fix: v5's 71 confirm5 worlds (= v4's confirm4 worlds; the combination space is
  exhausted, v5 DEVIATIONS #3), relabelled confirm6 with origin_world_id; not fresh (reported).
Text-level dedupe against every historical render (PLAN B1): the renders.jsonl of v1-v5 (incl. confirm5 and v5's multi-template
train / dev / confirm5 renders) and the earlier four-domain / canonical / manifold / operator-residual files; every new world's renders
(all states) are also disjoint from every other new world's; core keys disjoint from history and unique. Multi-template worlds: the
held-out templates are filled round-robin (seeded order); for the current template, world fields are drawn until the template's renders
of the world (all states) are fresh; a template with no fresh combination in 20000 consecutive draws is exhausted and skipped
(reported). (v5's GR-gate renders - v5 train / dev worlds re-rendered under every template for the reconstruction gate, never written
as data, never trained or calibrated on - are not counted as history; DEVIATIONS.)"""
import random
import shutil
import time
from collections import Counter
from symutil import *
import sym5_semantics as S

SEED = 2026112501
V2DIR = EXP / 'composability_mechanisms_v1'; V3DIR = EXP / 'composability_mechanisms_v2'; V4DIR = EXP / 'composability_mechanisms_v3'
V5DIR = EXP / 'composability_mechanisms_v4'
PLAN6 = {'weekday-mt': 160, 'month-mt': 160, 'hour-mt': 160, 'weekday': 160, 'month': 160, 'bind3': 160, 'name3': 160, 'bind3fix': None}
ALL = list(PLAN6)


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def history_world_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    for D in (V1, V2DIR, V3DIR, V4DIR, V5DIR): fs += sorted((D / 'data').glob('*/worlds.jsonl'))
    return [f for f in fs if f.exists()]


def history_text_files():
    fs = []
    for D in (V1, V2DIR, V3DIR, V4DIR, V5DIR): fs += sorted((D / 'data').glob('*/renders.jsonl'))
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
    for d in ('pron3', 'name3', 'bind3'):
        for w in rows(V2DIR / f'data/{d}/worlds.jsonl'):
            for t in (0, 3): seen.update(S.render(w, s, t) for s in S.states(d))
    return seen, files


def t0b_texts(w, d):
    return {S.render(w, s, 3 if d in S.S1B else 0) for s in S.states(d)}


def main():
    require_slurm(); t0 = time.time(); (ROOT / 'data').mkdir(exist_ok=True)
    for f in ('templates_mt.json', 'templates_split.json'):
        shutil.copyfile(V5DIR / 'data' / f, ROOT / 'data' / f); assert sha(ROOT / 'data' / f) == sha(V5DIR / 'data' / f)
    S.mt_templates.cache_clear(); split = read(ROOT / 'data/templates_split.json')['split']
    hist_keys = set(); wfiles = {}
    for f in history_world_files():
        rs = rows(f); wfiles[str(f.relative_to(REPO))] = dict(sha256=sha(f), worlds=len(rs)); hist_keys.update(key(w) for w in rs if 'people' in w)
    seen, tfiles = history_texts(); n_hist = len(seen); used = set(hist_keys); counts = {}
    for di, d in enumerate(ALL):
        rng = random.Random(SEED + di); out = []
        if d == 'bind3fix':
            for w in rows(V5DIR / 'data/bind3fix/worlds.jsonl'):
                assert w['split'] == 'confirm5'
                out.append(dict({k: v for k, v in w.items() if k not in ('world_id', 'split', 'origin_world_id')}, world_id=f'{d}_c6_{len(out):04d}', split='confirm6',
                                origin_world_id=w['world_id'], origin_world_id_v4=w.get('origin_world_id')))
            counts[d] = dict(confirm6=len(out), fresh=0, reused_from_v5_confirm5=len(out))
        else:
            tries = 0; held = list(split[d]['held_out']) if d in S.MT else None; tcount = Counter(); dead = {}; rr = 0; fails_t = Counter()
            if held: rng.shuffle(held)
            while len(out) < PLAN6[d]:
                tries += 1; assert tries < 10 ** 7, f'{d}: cannot find enough fresh worlds'
                if d in S.MT:
                    live = [t for t in held if t not in dead]; assert live, f'{d}: every held-out template exhausted'
                    tid = live[rr % len(live)]
                w = dict(domain=d, people=rng.sample(S.NAMES, 3), object=rng.choice(S.OBJECTS), color=rng.choice(S.COLORS),
                         quantity=rng.randrange(1, 10), status=rng.choice(S.STATUSES))
                start = rng.choice(S.states(d))
                if d in S.MT: w['distractor'] = rng.choice([s for s in S.states(d) if s != start])
                if key(w) in used: continue
                if d in S.MT:
                    tx = {S.render_mt(w, s, tid) for s in S.states(d)}
                    if tx & seen:
                        fails_t[tid] += 1
                        if fails_t[tid] >= 20000: dead[tid] = len(out)          # no fresh combination found in 20000 draws: template exhausted
                        continue
                    w['template_id'] = tid; tcount[tid] += 1; fails_t[tid] = 0; rr += 1
                else: tx = t0b_texts(w, d)
                if tx & seen: continue
                seen |= tx
                used.add(key(w)); w.update(world_id=f'{d}_c6_{len(out):04d}', split='confirm6', start_state=start); out.append(w)
            counts[d] = dict(confirm6=len(out), tries=tries)
            if d in S.MT: counts[d].update(template_counts={str(k): tcount[k] for k in sorted(held)}, exhausted_at={str(k): v for k, v in dead.items()})
        write(f'data/{d}/worlds.jsonl', out)
        write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=w.get('template_id', 3 if d in S.S1B else 0), state=s,
                                               text=S.render(w, s, 3 if d in S.S1B else 0)) for w in out for s in S.states(d)])
        print(d, counts[d], flush=True)
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + index in ALL)', all=ALL, plan=PLAN6, counts=counts,
                                    templates_mt_sha256=sha(ROOT / 'data/templates_mt.json'), templates_split_sha256=sha(ROOT / 'data/templates_split.json'),
                                    core_key='(people, object, color, quantity, status)', history_world_files=wfiles, history_text_files=tfiles,
                                    history_keys=len(hist_keys), history_texts=n_hist,
                                    files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in ALL for n in ('worlds.jsonl', 'renders.jsonl')}, seconds=time.time() - t0))


if __name__ == '__main__':
    main()
