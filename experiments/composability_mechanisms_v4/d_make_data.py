"""D (CPU): v5 worlds and the multi-template sentence templates (PLAN 5.1, 5.2, appendix B).

Templates: 36 skeletons written by Claude Code before any model run, expanded per domain with the domain's slot phrase
(weekday 'on {X}', month 'in {X}', hour 'at {X} o'clock'; capitalised variants at sentence start; {Y} the same-domain distractor) and
written to data/templates_mt.json (finalised here; later only removed by the GR / GT gates, never edited).
Worlds:
- confirm5 (template 0): weekday, month, compass, hour, compass8, season, 160 each (the same worlds serve both backbones);
- B (template 3): bind3, name3 160 fresh each; bind3fix: every remaining fresh (object, color, quantity) combination plus v4's 71
  confirm4 bind3fix worlds (never trained on; DEVIATIONS pre-lock), train / dev reused from v4 (X unit);
- multi-template: weekday-mt, month-mt, hour-mt train 192, dev 48, confirm5 160, each with a distractor state != start; template_id is
  assigned after the gates (d_assign.py).
Every fresh world's rendered texts (all states; multi-template: all 36 templates) are disjoint from every rendered text of the
repository's experiments (v1-v4 and the earlier four-domain / canonical / manifold / operator-residual files) and from all other new
worlds; core keys are disjoint from history."""
import random
import time
from symutil import *
import sym5_semantics as S

SEED = 2026112401
V2DIR = EXP / 'composability_mechanisms_v1'; V3DIR = EXP / 'composability_mechanisms_v2'; V4DIR = EXP / 'composability_mechanisms_v3'
T0 = ['weekday', 'month', 'compass', 'hour', 'compass8', 'season']
PLAN = {**{d: [('confirm5', 160)] for d in T0}, 'bind3': [('confirm5', 160)], 'name3': [('confirm5', 160)], 'bind3fix': [('confirm5', 160)],
        **{d: [('train', 192), ('dev', 48), ('confirm5', 160)] for d in S.MT}}
ALL = list(PLAN)

# ---------------------------------------------------------------- appendix B: 36 skeletons (structure, text); {Y}-skeletons marked
SKELETONS = [
    ('declarative', '{ATC}, the {o} event begins downtown.'),
    ('declarative', 'The {o} event finally begins {AT}.'),
    ('declarative', 'The {color} {o} arrives {AT}, not {AT_Y}.'),
    ('declarative', 'We will open the {o} {AT} and close the shop early.'),
    ('declarative', '{ATC}, {a} checks the {o} carefully.'),
    ('declarative', 'The workshop on the {o} now starts {AT} instead of {AT_Y}.'),
    ('declarative', 'There are {q} copies of the {o} ready {AT}.'),
    ('declarative', 'The {o} sale was expected {AT_Y} but now happens {AT}.'),
    ('reported', '{a} said that the {o} event starts {AT}.'),
    ('reported', '{a} said that {AT}, the {o} will be {st}.'),
    ('reported', '{ATC}, {a} said that the {color} {o} was missing.'),
    ('reported', '{a} said that the {o} moved from {BARE_Y} to {BARE}.'),
    ('reported', '{a} said that the {q} tickets for the {o} are valid {AT}.'),
    ('reported', '{a} said that the {o} is {st} {AT}, not {AT_Y}.'),
    ('reported', '{a} said that {AT} the {o} costs {q} dollars.'),
    ('relative', 'The {o} that {a} ordered arrives {AT}.'),
    ('relative', 'The {o}, which was {st}, returns {AT}.'),
    ('relative', '{ATC}, the {o} that was {color} is shown again.'),
    ('relative', 'The person who found the {o} {AT_Y} returns it {AT}.'),
    ('relative', 'The {o} that we saw {AT_Y} is back {AT}.'),
    ('relative', 'The class which uses the {o} meets {AT} rather than {AT_Y}.'),
    ('relative', '{ATC}, the {o} which {a} fixed is ready.'),
    ('passive', 'The {o} is delivered {AT} by {a}.'),
    ('passive', '{ATC}, the {o} was repaired by {a}.'),
    ('passive', 'The {color} {o} will be collected {AT}.'),
    ('passive', 'The {o} was moved by {a} from {BARE_Y} to {BARE}.'),
    ('passive', '{ATC}, {q} boxes were sent with the {o}.'),
    ('passive', 'The {o} is checked {AT}, and it was approved {AT_Y}.'),
    ('passive', '{ATC}, the {o} is cleaned and then marked {st}.'),
    ('enumeration', '{ATC}, bring the {o}, the {color} pen, and {q} cups.'),
    ('enumeration', 'We need the {o}, a map, and a pencil {AT}.'),
    ('enumeration', 'The list has the {o}, the {color} bag, and the report due {AT}.'),
    ('enumeration', '{ATC} or {AT_Y}, pack the {o}, the tape, and the labels.'),
    ('enumeration', '{a} packed the {o}, {q} pens, and a note {AT}.'),
    ('enumeration', 'For the trip {AT}, take the {o}, water, and a hat.'),
    ('enumeration', 'Check the {o}, the {color} lid, and the label {AT}, then again {AT_Y}.'),
]
PHRASE = {'weekday-mt': dict(AT='on {X}', ATC='On {X}', BARE='{X}'), 'month-mt': dict(AT='in {X}', ATC='In {X}', BARE='{X}'),
          'hour-mt': dict(AT='at {X}', ATC='At {X}', BARE='{X}')}      # 'o\'clock' dropped for rule 4 (DEVIATIONS)


def expand(d):
    ph = PHRASE[d]; sub = {**ph, **{f'{k}_Y': v.replace('{X}', '{Y}') for k, v in ph.items()}}
    out = []
    for i, (st, sk) in enumerate(SKELETONS):
        txt = sk
        for k in sorted(sub, key=len, reverse=True): txt = txt.replace('{' + k + '}', sub[k])
        out.append(dict(id=i, skeleton=i, structure=st, text=txt, has_Y='{Y}' in txt))
    return out


def key(w):
    return (tuple(w['people']), w['object'], w['color'], int(w['quantity']), w['status'])


def history_world_files():
    fs = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')]
    fs += sorted((CONF / 'data').glob('*.jsonl')) + sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    for D in (V1, V2DIR, V3DIR, V4DIR): fs += sorted((D / 'data').glob('*/worlds.jsonl'))
    return [f for f in fs if f.exists()]


def history_text_files():
    fs = []
    for D in (V1, V2DIR, V3DIR, V4DIR): fs += sorted((D / 'data').glob('*/renders.jsonl'))
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


def all_texts(w, d):
    if d in S.MT:
        return {S.render_mt(w, s, i) for s in S.states(d) for i in range(len(SKELETONS))}
    t = 3 if d in S.S1B else 0
    return {S.render(w, s, t) for s in S.states(d)}


def main():
    require_slurm(); t0 = time.time()
    tm = {d: expand(d) for d in S.MT}
    dump('data/templates_mt.json', dict(rules='PLAN appendix B; skeletons x domain slot phrase (d_make_data.py)', phrase=PHRASE, templates=tm))
    S.mt_templates.cache_clear()
    hist_keys = set(); wfiles = {}
    for f in history_world_files():
        rs = rows(f); wfiles[str(f.relative_to(REPO))] = dict(sha256=sha(f), worlds=len(rs)); hist_keys.update(key(w) for w in rs if 'people' in w)
    seen, tfiles = history_texts(); n_hist = len(seen); used = set(hist_keys); counts = {}
    for di, d in enumerate(ALL):
        rng = random.Random(SEED + di); out = []; plan = PLAN[d]; t = 3 if d in S.S1B else 0
        if d == 'bind3fix':
            v3 = rows(V3DIR / 'data/bind3fix/worlds.jsonl'); v4 = rows(V4DIR / 'data/bind3fix/worlds.jsonl')
            usedc = {(w['object'], w['color'], int(w['quantity'])) for w in v3 + v4}
            combos = [(o, c, q) for o in S.OBJECTS for c in S.COLORS for q in range(1, 10) if (o, c, q) not in usedc]; rng.shuffle(combos)
            for o, c, q in combos:
                sts = list(S.STATUSES); rng.shuffle(sts)
                cand = [w for w in (dict(domain=d, people=list(S.FIX3), object=o, color=c, quantity=q, status=s_) for s_ in sts) if key(w) not in used]
                if not cand: continue
                w = cand[0]; tx = all_texts(w, d)
                if tx & seen: continue
                seen |= tx; used.add(key(w)); w.update(world_id=f'{d}_c5_{len(out):04d}', split='confirm5', start_state=rng.choice(S.states(d))); out.append(w)
            n_fresh = len(out)
            for w in [w for w in v4 if w['split'] == 'confirm4']:
                out.append(dict({k: v for k, v in w.items() if k not in ('world_id', 'split')}, world_id=f'{d}_c5_{len(out):04d}', split='confirm5', origin_world_id=w['world_id']))
            counts[d + '_fresh'] = n_fresh
        else:
            total = sum(n for _, n in plan); bounds = np.cumsum([n for _, n in plan]); tries = 0
            while len(out) < total:
                tries += 1; assert tries < 10 ** 6, f'{d}: cannot find enough fresh worlds'
                w = dict(domain=d, people=rng.sample(S.NAMES, 3), object=rng.choice(S.OBJECTS), color=rng.choice(S.COLORS),
                         quantity=rng.randrange(1, 10), status=rng.choice(S.STATUSES))
                start = rng.choice(S.states(d))
                if d in S.MT: w['distractor'] = rng.choice([s for s in S.states(d) if s != start])
                if key(w) in used: continue
                tx = all_texts(w, d)
                if tx & seen: continue
                used.add(key(w)); i = len(out); split = plan[int(np.searchsorted(bounds, i, side="right"))][0]
                if d not in S.MT: seen |= tx       # multi-template: texts of templates with few fields repeat across worlds by design (DEVIATIONS)
                w.update(world_id=f'{d}_c5_{i:04d}' if split == 'confirm5' else f'{d}_v5_{i:04d}', split=split, start_state=start)
                if d in S.MT: w['template_id'] = None
                out.append(w)
        write(f'data/{d}/worlds.jsonl', out)
        if d not in S.MT:
            write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=t, state=s, text=S.render(w, s, t)) for w in out for s in S.states(d)])
        counts[d] = {sp: sum(w['split'] == sp for w in out) for sp in ('train', 'dev', 'confirm5')}
        print(d, counts[d], flush=True)
    dump('data/manifest.json', dict(seed=SEED, seed_rule='random.Random(seed + index in ALL)', all=ALL, plan=PLAN, counts=counts,
                                    templates_mt_sha256=sha(ROOT / 'data/templates_mt.json'), core_key='(people, object, color, quantity, status)',
                                    text_rule='all renders (all states) of a fresh world disjoint from every historical text; template-0 and binding worlds also disjoint from every other new world; multi-template worlds: all 36 templates x all states disjoint from history and core keys unique (identical sentences across multi-template worlds arise from templates with few fields)',
                                    history_world_files=wfiles, history_text_files=tfiles, history_keys=len(hist_keys), history_texts=n_hist,
                                    files={f'{d}/worlds.jsonl': sha(ROOT / f'data/{d}/worlds.jsonl') for d in ALL}, seconds=time.time() - t0))


if __name__ == '__main__':
    main()
