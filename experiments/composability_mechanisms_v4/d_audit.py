"""D audit (CPU; tokenizers only, no model).
Template-0 and binding domains (confirm5): the v4 checks (gold parse, negative controls, parse_state, duplicate texts, history key /
text overlap, single-token state words and slot positions under BART BPE and the chat-wrapped Gemma tokenizer, T5Gemma input cap).
Multi-template domains: appendix B rules 1-7 on data/templates_mt.json; the GT gate per (backbone, template) (state word single token,
slot position constant within the template over every train / dev / confirm5 world and state); gold texts parse to the right state
and the distractor is never read as the slot (A.6); text dedupe against history over all templates; T5Gemma input cap."""
import re
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym5_semantics as S
import sym5_evaluator as Ev
from d_make_data import history_world_files, history_texts, key, ALL, all_texts

T0B = [d for d in ALL if d not in S.MT]
NUMBER_WORDS = set('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen '
                   'twenty thirty forty fifty sixty seventy eighty ninety hundred thousand first second third once twice dozen'.split())
FIELDS = ('o', 'st', 'color', 'q', 'a')


def worlds(d):
    return rows(ROOT / f'data/{d}/worlds.jsonl')


def template_rules(tm, tok):
    res = {}; ok = True
    for d, T in tm.items():
        vocab = {w.lower() for w in S.NEW_WORDS.get(S.base(d), [])} or {S.word(d, s).lower() for s in S.states(d)}
        r = dict(n=len(T), structures=Counter(t['structure'] for t in T), has_Y=sum(t['has_Y'] for t in T), violations=[])
        for t in T:
            x = t['text']
            if x.count('{X}') != 1 or ' {X}' not in x: r['violations'].append((t['id'], 'rule1'))
            nf = sum(('{' + f + '}') in x for f in FIELDS)
            if nf > 4: r['violations'].append((t['id'], 'rule5'))
            bare = re.sub(r'\{[A-Za-z]+\}', ' ', x).lower(); words = set(re.findall(r'[a-z]+', bare))
            if words & vocab: r['violations'].append((t['id'], 'rule7_state_word', sorted(words & vocab)))
            if S.base(d) == 'hour' and words & NUMBER_WORDS: r['violations'].append((t['id'], 'rule7_number_word', sorted(words & NUMBER_WORDS)))
        r['rule3'] = len(r['structures']) >= 5 and min(r['structures'].values()) >= 4
        r['rule6'] = r['has_Y'] == 12
        ws = worlds(d)[:40]; lens = []; rel = {}
        for t in T:
            L = []; P = []
            for w in ws:
                for s in S.states(d):
                    ids = tok(S.render_mt(w, s, t['id']), add_special_tokens=False)['input_ids']
                    alt = tok(S.render_mt(w, (s + 1) % len(S.states(d)), t['id']), add_special_tokens=False)['input_ids']
                    L.append(len(ids)); diff = [i for i in range(min(len(ids), len(alt))) if ids[i] != alt[i]]
                    if len(ids) == len(alt) and len(diff) == 1: P.append(diff[0] / len(ids))
            lens.append((t['id'], min(L), max(L))); rel[t['id']] = float(np.mean(P)) if P else None
        r['rule2_len_violations'] = [x for x in lens if x[1] < 8 or x[2] > 30]
        r['slot_relpos'] = rel; r['first_third'] = sum(1 for v in rel.values() if v is not None and v < 1 / 3); r['last_third'] = sum(1 for v in rel.values() if v is not None and v >= 2 / 3)
        r['rule4'] = r['first_third'] >= 10 and r['last_third'] >= 10
        r['pass'] = not r['violations'] and not r['rule2_len_violations'] and r['rule3'] and r['rule4'] and r['rule6']
        ok &= r['pass']; res[d] = r
    return res, ok


def gt_gate(d, T, ids):
    """GT per (backbone, template): every world and state renders with the slot as one differing token at a constant position."""
    out = {}
    for bb in ('bart', 't5'):
        out[bb] = {}
        for t in T:
            pos = set(); bad = Counter()
            for w in worlds(d):
                seqs = {s: ids[bb](S.render_mt(w, s, t['id'])) for s in S.states(d)}
                if len({len(v) for v in seqs.values()}) != 1: bad['length_varies'] += 1; continue
                b0 = seqs[0]; diff = sorted({i for s in seqs for i in range(len(b0)) if seqs[s][i] != b0[i]})
                if len(diff) != 1: bad['not_single_token'] += 1; continue
                pos.add(diff[0])
            out[bb][t['id']] = dict(pass_=not bad and len(pos) == 1, slot=sorted(pos)[0] if len(pos) == 1 else None, positions=sorted(pos)[:5], failures=dict(bad))
    return out


def main():
    require_slurm(); t0 = time.time(); cfg = read(SOURCE / 'config.json'); mm = read(SOURCE / 'model_manifest.json')
    tb = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    tg = AutoTokenizer.from_pretrained(mm['t5gemma']['directory'], local_files_only=True)
    wrap = lambda t: tg.apply_chat_template([dict(role='user', content=cfg['copy_instruction'] + t)], tokenize=False, add_generation_prompt=True)
    ids = {'bart': lambda t: tb(t)['input_ids'], 't5': lambda t: tg(wrap(t), add_special_tokens=False)['input_ids']}
    hist_keys = {key(w) for f in history_world_files() for w in rows(f) if 'people' in w}
    hist_texts, _ = history_texts()
    res = dict(domains={}); slots = {'bart': {}, 't5': {}}; ok_all = True; new_texts = Counter()
    # ---------------- template-0 and binding domains (confirm5)
    v4s = read(EXP / 'composability_mechanisms_v3/data/slot_positions.json')
    for d in T0B:
        t = 3 if d in S.S1B else 0; ws = worlds(d); fails = Counter(); texts = Counter(); per = {'bart': {}, 't5': {}}; lens_t5 = []
        for w in ws:
            for bb in ('bart', 't5'):
                seqs = {s: ids[bb](S.render(w, s, t)) for s in S.states(d)}
                if len({len(v) for v in seqs.values()}) != 1: fails[f'{bb}_mask'] += 1; continue
                b0 = seqs[S.states(d)[0]]; diff = sorted({i for s in seqs for i in range(len(b0)) if seqs[s][i] != b0[i]})
                if len(diff) != 1: fails[f'{bb}_not_single_token'] += 1; continue
                per[bb][w['world_id']] = diff[0]
                if bb == 't5': lens_t5.append(len(b0))
            for s in S.states(d):
                x = S.render(w, s, t); texts[x] += 1; g = S.gold(w, s, t)
                if not Ev.score(x, g, w, True)['success']: fails['gold'] += 1
                y = S.advance(d, s, 'plus'); wrong = Ev.score(S.render(w, y, t), g, w, True)
                col = [c for c in S.COLORS if c != w['color']][0]; recol = Ev.score(S.render(dict(w, color=col), s, t), g, w, True)
                if wrong['target'] or wrong['success'] or recol['preserved'] or recol['success'] or Ev.score(x[:-12], g, w, True)['success'] or Ev.score(x, g, w, False)['success']:
                    fails['negative_control'] += 1
                if Ev.parse_state(x, d, S.people(w) if d in S.S1B else None)[0] != s: fails['parse_state'] += 1
        for bb in ('bart', 't5'):
            vals = set(per[bb].values())
            if t == 0:
                if len(vals) != 1: fails[f'{bb}_t0_slot_not_constant'] += 1
                slots[bb][d] = {'all': sorted(vals)[0] if vals else None}
            else: slots[bb][d] = {'per_world': per[bb]}
        fresh = [w for w in ws if 'origin_world_id' not in w]; reused = [w for w in ws if 'origin_world_id' in w]
        hk = len({key(w) for w in fresh} & hist_keys); ht = sum(1 for w in fresh if all_texts(w, d) & hist_texts)
        for w in ws:
            for x in all_texts(w, d): new_texts[x] += 1
        r = dict(worlds=len(ws), fresh=len(fresh), reused_from_v4_confirm4=len(reused), failures=dict(fails), duplicate_texts=sum(1 for c in texts.values() if c > 1),
                 history_key_overlap=hk, history_text_hits_fresh=ht, t5_over_cap=sum(1 for L in lens_t5 if L > cfg['source_cap']['t5gemma']),
                 slot_bart=slots['bart'][d].get('all', 'per-world'), slot_t5=slots['t5'][d].get('all', 'per-world'),
                 t0_slot_matches_v4=(slots['bart'][d] == v4s['bart'].get(d) and slots['t5'][d] == v4s['t5'].get(d)) if t == 0 else None)
        r['pass'] = not fails and not r['duplicate_texts'] and not hk and not ht and not r['t5_over_cap'] and r['t0_slot_matches_v4'] is not False
        ok_all &= r['pass']; res['domains'][d] = r; print(d, r, flush=True)
    # ---------------- multi-template domains
    tm = read(ROOT / 'data/templates_mt.json')['templates']
    rules, rules_ok = template_rules(tm, tb); res['template_rules'] = rules; res['template_rules_pass'] = rules_ok
    print('template rules', {d: (r['pass'], r['first_third'], r['last_third'], r['violations'][:3], r['rule2_len_violations'][:3]) for d, r in rules.items()}, flush=True)
    res['GT'] = {}
    for d in S.MT:
        ws = worlds(d); fails = Counter(); gt = gt_gate(d, tm[d], ids); res['GT'][d] = gt
        for w in ws:
            for t in tm[d]:
                for s in S.states(d):
                    g = S.gold(dict(w, template_id=t['id']), s); x = g['text']
                    if not Ev.score(x, g, w, True)['success']: fails['gold'] += 1
                    if Ev.parse_state(x, d, gold=g)[0] != s: fails['parse_state'] += 1
                    y = S.advance(d, s, 'plus'); wr = Ev.score(S.render_mt(w, y, t['id']), g, w, True)
                    if wr['success'] or wr['target']: fails['negative_control'] += 1
                    if Ev.score(x, g, w, False)['success'] or Ev.score(x[:-3], g, w, True)['success']: fails['negative_control_trunc'] += 1
        lens_t5 = [len(ids['t5'](S.render_mt(w, 0, t['id']))) for w in ws[:20] for t in tm[d]]
        fresh_hits = sum(1 for w in ws if all_texts(w, d) & hist_texts); hk = len({key(w) for w in ws} & hist_keys)
        sp = Counter(w['split'] for w in ws); dist_ok = all(w['distractor'] != w['start_state'] for w in ws)
        r = dict(worlds=dict(sp), failures=dict(fails), history_key_overlap=hk, history_text_hits=fresh_hits, distractor_ne_start=dist_ok,
                 t5_max_len=max(lens_t5), t5_over_cap=sum(1 for L in lens_t5 if L > cfg['source_cap']['t5gemma']),
                 GT_pass={bb: [i for i, v in gt[bb].items() if v['pass_']] for bb in gt}, GT_fail={bb: {i: v['failures'] for i, v in gt[bb].items() if not v['pass_']} for bb in gt})
        r['pass'] = not fails and not hk and not fresh_hits and dist_ok and not r['t5_over_cap']
        ok_all &= r['pass']; res['domains'][d] = r; print(d, {k: v for k, v in r.items() if k != 'GT_pass'}, flush=True)
    res['cross_domain_duplicate_new_texts'] = sum(1 for c in new_texts.values() if c > 1)
    res['pass'] = bool(ok_all and rules_ok and not res['cross_domain_duplicate_new_texts']); res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('sym5_semantics.py', 'sym5_evaluator.py', 'd_make_data.py', 'd_audit.py')}
    res['templates_mt_sha256'] = sha(ROOT / 'data/templates_mt.json')
    dump('data/audit.json', res); dump('data/slot_positions_t0b.json', slots)
    assert res['pass'], 'D audit failed'


if __name__ == '__main__':
    main()
