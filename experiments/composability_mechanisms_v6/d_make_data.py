"""D (CPU): v7 confirm7 and dev7-ho worlds (PLAN v7 B5).
- Multi-template (weekday-mt, month-mt, hour-mt; month-mt also T5Gemma): one stream of up to 208 fresh worlds on v5's 9 held-out
  templates (byte-identical copies of v5's template files), split by a seeded shuffle into dev7-ho (48; calibration and pre-checks only)
  and confirm7 (the rest, at most 160). If fewer than 208 fresh worlds exist, confirm7 keeps at least 80 and dev7-ho takes the rest up to 48
  (reported). A fixed distractor != start.
- Template 0: weekday, month: the 1080 template-0 texts per domain are exhausted by v1-v6, so v6's 160 confirm6 worlds each are relabelled
  confirm7 (origin ids kept; not fresh; never decoded with any v7 editor; DEVIATIONS #4). month is shared by T5Gemma.
- K: bind3, name3 (template 3), 160 fresh each; bind3fix: v6's 71 confirm6 worlds (= v5 confirm5 = v4 confirm4; the combination space
  is exhausted), relabelled confirm7 with origin ids; not fresh (reported).
Text-level dedupe against every historical render (PLAN v7 B1): the renders.jsonl of v1-v6 (incl. confirm6 and v5's multi-template
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

SEED = 2026112601
V2DIR = EXP / 'composability_mechanisms_v1'; V3DIR = EXP / 'composability_mechanisms_v2'; V4DIR = EXP / 'composability_mechanisms_v3'
V5DIR = EXP / 'composability_mechanisms_v4'; V6DIR = EXP / 'composability_mechanisms_v5'
PLAN7 = {'weekday-mt': 208, 'month-mt': 208, 'hour-mt': 208, 'weekday': 160, 'month': 160, 'bind3': 160, 'name3': 160, 'bind3fix': None}
DEV_HO = 48; MIN_CONFIRM = 80
REUSE = ('weekday', 'month', 'bind3fix')   # template 0 (object x colour x status x quantity = 1080 texts) and bind3fix: exhausted; DEVIATIONS #4
ALL = list(PLAN7)


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def history_world_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    for D in (V1, V2DIR, V3DIR, V4DIR, V5DIR, V6DIR): fs += sorted((D / 'data').glob('*/worlds.jsonl'))
    return [f for f in fs if f.exists()]


def history_text_files():
    fs = []
    for D in (V1, V2DIR, V3DIR, V4DIR, V5DIR, V6DIR): fs += sorted((D / 'data').glob('*/renders.jsonl'))
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
        if d in REUSE:                                                # combination space exhausted: v6's confirm6 worlds, relabelled (not fresh)
            for w in rows(V6DIR / f"data/{d}/worlds.jsonl"):
                assert w["split"] == "confirm6"
                out.append(dict({k: v for k, v in w.items() if k not in ("world_id", "split", "origin_world_id", "origin_world_id_v4")}, world_id=f"{d}_c7_{len(out):04d}",
                                split="confirm7", origin_world_id_v6=w["world_id"], origin_world_id=w.get("origin_world_id") or w["world_id"], origin_world_id_v4=w.get("origin_world_id_v4")))
            counts[d] = dict(confirm7=len(out), fresh=0, reused_from_v6_confirm6=len(out))
        else:
            tries = 0; held = list(split[d]['held_out']) if d in S.MT else None; tcount = Counter(); dead = {}; rr = 0; fails_t = Counter()
            if held: rng.shuffle(held)
            while len(out) < PLAN7[d]:
                tries += 1
                if d in S.MT:
                    live = [t for t in held if t not in dead]
                    if not live: break                                         # every held-out template exhausted: keep what was found
                    tid = live[rr % len(live)]
                else: assert tries < 10 ** 7, f'{d}: cannot find enough fresh worlds'
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
                used.add(key(w)); w['start_state'] = start; out.append(w)
            if d in S.MT:
                n = len(out); n_dev = min(DEV_HO, max(0, n - MIN_CONFIRM)); assert n - n_dev >= MIN_CONFIRM, f'{d}: only {n} fresh worlds'
                order = list(range(n)); random.Random(SEED + 100 + di).shuffle(order); dev = set(order[:n_dev]); ci = di_ = 0
                for i, w in enumerate(out):
                    if i in dev: w.update(world_id=f'{d}_d7_{di_:04d}', split='dev7ho'); di_ += 1
                    else: w.update(world_id=f'{d}_c7_{ci:04d}', split='confirm7'); ci += 1
                counts[d] = dict(found=n, confirm7=ci, dev7ho=di_, tries=tries, template_counts={str(k): tcount[k] for k in sorted(held)},
                                 template_counts_confirm7={str(k): sum(1 for w in out if w['split'] == 'confirm7' and w['template_id'] == k) for k in sorted(held)},
                                 exhausted_at={str(k): v for k, v in dead.items()})
            else:
                for i, w in enumerate(out): w.update(world_id=f'{d}_c7_{i:04d}', split='confirm7')
                counts[d] = dict(confirm7=len(out), tries=tries)
        write(f'data/{d}/worlds.jsonl', out)
        write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=w.get('template_id', 3 if d in S.S1B else 0), state=s,
                                               text=S.render(w, s, 3 if d in S.S1B else 0)) for w in out for s in S.states(d)])
        print(d, counts[d], flush=True)
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + index in ALL); dev7-ho split random.Random(seed + 100 + index)', all=ALL, plan=PLAN7,
                                    dev_ho=DEV_HO, min_confirm=MIN_CONFIRM, counts=counts,
                                    templates_mt_sha256=sha(ROOT / 'data/templates_mt.json'), templates_split_sha256=sha(ROOT / 'data/templates_split.json'),
                                    core_key='(people, object, color, quantity, status)', history_world_files=wfiles, history_text_files=tfiles,
                                    history_keys=len(hist_keys), history_texts=n_hist,
                                    files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in ALL for n in ('worlds.jsonl', 'renders.jsonl')}, seconds=time.time() - t0))


if __name__ == '__main__':
    main()
