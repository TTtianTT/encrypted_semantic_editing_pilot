"""D audit (CPU; tokenizers only, no model). confirm7 and dev7-ho (PLAN v7 B5). Copied from v6 d_audit.py; changes: T5Gemma template-0 slot for
month (U non-inferiority set), confirm7 name positions, both multi-template splits.
Template-0 (weekday, month) and binding (bind3, name3, bind3fix) worlds, BART: gold parse, negative controls, parse_state, duplicate texts,
history key / text overlap (fresh worlds), single-token state words and slot positions (template 0: constant and equal to v5's; weekday
also equal to the v1 caches' slot).
Multi-template worlds (BART; month-mt also T5Gemma): template is held-out; per world the state words differ in exactly one token at the
v5 GT slot position of its (backbone, template); gold texts parse to their state, the distractor is never read as the slot (A.6);
negative controls; distractor != start; T5Gemma input cap.
Also: data/name_positions.json (BART token positions of the three list names, template 3) for bind3 / name3 / bind3fix train, dev (v4 X
worlds) and confirm7 (the OR editor's routing targets) and data/slot_positions.json."""
import re
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym5_semantics as S
import sym5_evaluator as Ev
from d_make_data import history_world_files, history_texts, key, ALL, V3DIR, V4DIR, V5DIR

T0B = ['weekday', 'month', 'bind3', 'name3', 'bind3fix']
USERS = {'weekday-mt': ('bart',), 'month-mt': ('bart', 't5'), 'hour-mt': ('bart',)}


def worlds(d, D=ROOT, split=None):
    return [w for w in rows(D / f'data/{d}/worlds.jsonl') if split is None or w['split'] == split]


def name_pos(tok, w, d):
    text = S.render(w, 0, 3); off = tok(text, return_offsets_mapping=True)['offset_mapping']; out = []
    for nme in S.people(w):
        cs = re.search(r'\b' + re.escape(nme) + r'\b', text).start()
        out.append(next(t for t, (a0, b0) in enumerate(off) if b0 > a0 and a0 <= cs < b0))
    return out


def main():
    require_slurm(); t0 = time.time(); cfg = read(SOURCE / 'config.json'); mm = read(SOURCE / 'model_manifest.json')
    tb = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    tg = AutoTokenizer.from_pretrained(mm['t5gemma']['directory'], local_files_only=True)
    wrap = lambda t: tg.apply_chat_template([dict(role='user', content=cfg['copy_instruction'] + t)], tokenize=False, add_generation_prompt=True)
    ids = {'bart': lambda t: tb(t)['input_ids'], 't5': lambda t: tg(wrap(t), add_special_tokens=False)['input_ids']}
    hist_keys = set()
    for f in history_world_files():
        if str(f).startswith(str(ROOT)): continue
        hist_keys.update(key(w) for w in rows(f) if 'people' in w)
    hist_texts, _ = history_texts()
    res = dict(domains={}); slots = {'bart': {}, 't5': {}}; ok_all = True
    v5s = read(V5DIR / 'data/slot_positions.json'); v3s = read(V3DIR / 'data/slot_positions.json')
    for d in T0B:
        t = 3 if d in S.S1B else 0; ws = worlds(d); fails = Counter(); texts = Counter(); per = {}
        for w in ws:
            seqs = {s: ids['bart'](S.render(w, s, t)) for s in S.states(d)}
            if len({len(v) for v in seqs.values()}) != 1: fails['bart_mask'] += 1; continue
            b0 = seqs[S.states(d)[0]]; diff = sorted({i for s in seqs for i in range(len(b0)) if seqs[s][i] != b0[i]})
            if len(diff) != 1: fails['bart_not_single_token'] += 1; continue
            per[w['world_id']] = diff[0]
            for s in S.states(d):
                x = S.render(w, s, t); texts[x] += 1; g = S.gold(w, s, t)
                if not Ev.score(x, g, w, True)['success']: fails['gold'] += 1
                y = S.advance(d, s, 'plus'); wrong = Ev.score(S.render(w, y, t), g, w, True)
                col = [c for c in S.COLORS if c != w['color']][0]; recol = Ev.score(S.render(dict(w, color=col), s, t), g, w, True)
                if wrong['target'] or wrong['success'] or recol['preserved'] or recol['success'] or Ev.score(x[:-12], g, w, True)['success'] or Ev.score(x, g, w, False)['success']:
                    fails['negative_control'] += 1
                if Ev.parse_state(x, d, S.people(w) if d in S.S1B else None)[0] != s: fails['parse_state'] += 1
        vals = set(per.values())
        if t == 0:
            if len(vals) != 1: fails['t0_slot_not_constant'] += 1
            slots['bart'][d] = {'all': sorted(vals)[0] if vals else None}
        else: slots['bart'][d] = {'per_world': per}
        fresh = [w for w in ws if 'origin_world_id' not in w]
        hk = len({key(w) for w in fresh} & hist_keys); ht = sum(1 for w in fresh if {S.render(w, s, t) for s in S.states(d)} & hist_texts)
        r = dict(worlds=len(ws), fresh=len(fresh), reused=len(ws) - len(fresh), failures=dict(fails), duplicate_texts=sum(1 for c in texts.values() if c > 1),
                 history_key_overlap=hk, history_text_hits_fresh=ht, slot=slots['bart'][d].get('all', 'per-world'))
        if d == "month":                                              # T5Gemma template 0 (U non-inferiority set): constant slot, equal to v5's
            pt = set()
            for w in ws:
                sq = {s: ids["t5"](S.render(w, s, 0)) for s in S.states(d)}
                if len({len(v) for v in sq.values()}) != 1: fails["t5_mask"] += 1; continue
                b0 = sq[S.states(d)[0]]; df = sorted({i for s in sq for i in range(len(b0)) if sq[s][i] != b0[i]})
                if len(df) != 1: fails["t5_not_single_token"] += 1; continue
                pt.add(df[0])
            if len(pt) != 1: fails["t5_t0_slot_not_constant"] += 1
            slots["t5"][d] = {"all": sorted(pt)[0] if pt else None}; r_t5 = slots["t5"][d] == v5s["t5"][d]
        if t == 0:
            r["slot_equals_v5"] = slots["bart"][d] == v5s["bart"][d] and (d != "month" or r_t5)
            r['slot_equals_v1_caches'] = slots['bart'][d]['all'] == v3s['bart'][d]['all']      # v1 train/dev caches use v3's template-0 table
        r['pass'] = not fails and not r['duplicate_texts'] and not hk and not ht and r.get('slot_equals_v5', True) is not False
        ok_all &= r['pass']; res['domains'][d] = r; print(d, r, flush=True)
    split = read(ROOT / 'data/templates_split.json')['split']; gt5 = read(V5DIR / 'data/audit.json')['GT']; tm = S.mt_templates()
    for d in S.MT:
        ws = worlds(d); fails = Counter(); held = set(split[d]['held_out'])
        for bb in USERS[d]: slots[bb][d] = {'per_world': {}}
        for w in ws:
            tid = w['template_id']
            if tid not in held: fails['template_not_held_out'] += 1
            if w['distractor'] == w['start_state']: fails['distractor_eq_start'] += 1
            for bb in USERS[d]:
                seqs = {s: ids[bb](S.render(w, s)) for s in S.states(d)}
                if len({len(v) for v in seqs.values()}) != 1: fails[f'{bb}_length_varies'] += 1; continue
                b0 = seqs[0]; diff = sorted({i for s in seqs for i in range(len(b0)) if seqs[s][i] != b0[i]})
                if len(diff) != 1: fails[f'{bb}_not_single_token'] += 1; continue
                if diff[0] != gt5[d][bb][str(tid)]['slot']: fails[f'{bb}_slot_ne_v5_GT'] += 1
                slots[bb][d]['per_world'][w['world_id']] = diff[0]
                if bb == 't5' and len(b0) > cfg['source_cap']['t5gemma']: fails['t5_over_cap'] += 1
            for s in S.states(d):
                g = S.gold(w, s); x = g['text']
                if not Ev.score(x, g, w, True)['success']: fails['gold'] += 1
                if Ev.parse_state(x, d, gold=g)[0] != s: fails['parse_state'] += 1
                y = S.advance(d, s, 'plus'); wr = Ev.score(S.render_mt(w, y, tid), g, w, True)
                if wr['success'] or wr['target']: fails['negative_control'] += 1
                if Ev.score(x, g, w, False)['success'] or Ev.score(x[:-3], g, w, True)['success']: fails['negative_control_trunc'] += 1
        hk = len({key(w) for w in ws} & hist_keys); ht = sum(1 for w in ws if {S.render(w, s) for s in S.states(d)} & hist_texts)
        r = dict(worlds=len(ws), failures=dict(fails), history_key_overlap=hk, history_text_hits=ht, templates=dict(Counter(str(w['template_id']) for w in ws)),
                 with_distractor_template=sum(1 for w in ws if tm[d][w['template_id']]['has_Y']))
        r['pass'] = not fails and not hk and not ht
        ok_all &= r['pass']; res['domains'][d] = r; print(d, r, flush=True)
    npos = {}
    for d in ('bind3', 'name3', 'bind3fix'):
        npos[d] = {}
        for D, sp in ((V4DIR, "train"), (V4DIR, "dev"), (ROOT, "confirm7")):
            for w in worlds(d, D, sp):
                p = name_pos(tb, w, d); npos[d][w['world_id']] = p
                if len(set(p)) != 3: fails_np = res.setdefault('name_position_failures', []); fails_np.append(w['world_id'])
                if sp == "confirm7" and not max(p) < slots['bart'][d]['per_world'][w['world_id']]: res.setdefault('name_after_slot', []).append(w['world_id'])
    ok_all &= not res.get('name_position_failures') and not res.get('name_after_slot')
    res['pass'] = bool(ok_all); res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('sym5_semantics.py', 'sym5_evaluator.py', 'd_make_data.py', 'd_audit.py')}
    dump('data/audit.json', res); dump('data/slot_positions.json', slots); dump('data/name_positions.json', npos)
    assert res['pass'], 'D audit failed'


if __name__ == '__main__':
    main()
