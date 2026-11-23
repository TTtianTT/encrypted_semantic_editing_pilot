"""D audit (CPU): the v3 checks (gold parse, negative controls, parse_state, duplicate texts, split/history key overlap, single-token
state words and slot positions under BART BPE and the chat-wrapped Gemma tokenizer, T5Gemma input cap) for every v4 domain and split,
plus (8) text-level dedupe of all new worlds against every historical rendered text (bind3fix train/dev reuse: DEVIATIONS #2) and
(9) template-0 slot positions constant within a domain under both backbones (template 3: recorded per world)."""
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym4_semantics as S
import sym4_evaluator as Ev
from lib4 import worlds4, tmpl
from d_make_data import history_world_files, history_texts, key, ALL

SPLITS = ('train', 'dev', 'confirm4')


def main():
    require_slurm(); t0 = time.time(); cfg = read(SOURCE / 'config.json'); mm = read(SOURCE / 'model_manifest.json')
    tb = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    tg = AutoTokenizer.from_pretrained(mm['t5gemma']['directory'], local_files_only=True)
    wrap = lambda t: tg.apply_chat_template([dict(role='user', content=cfg['copy_instruction'] + t)], tokenize=False, add_generation_prompt=True)
    ids = {'bart': lambda t: tb(t)['input_ids'], 't5': lambda t: tg(wrap(t), add_special_tokens=False)['input_ids']}
    hist_keys = {key(w) for f in history_world_files() for w in rows(f) if 'people' in w}
    hist_texts, _ = history_texts()
    res = dict(domains={}); table = []; slots = {'bart': {}, 't5': {}}; ok_all = True; new_texts = Counter()
    for d in ALL:
        t = tmpl(d); ws = [w for sp in SPLITS for w in worlds4(d, sp)]; new = rows(ROOT / f'data/{d}/worlds.jsonl')
        fails = Counter(); texts = Counter(); per = {'bart': {}, 't5': {}}; lens_t5 = []
        for w in ws:
            for bb in ('bart', 't5'):
                seqs = {s: ids[bb](S.render(w, s, t)) for s in S.states(d)}
                if len({len(v) for v in seqs.values()}) != 1: fails[f'{bb}_mask'] += 1; continue
                base = seqs[S.states(d)[0]]; diff = sorted({i for s in seqs for i in range(len(base)) if seqs[s][i] != base[i]})
                if len(diff) != 1: fails[f'{bb}_not_single_token'] += 1; continue
                per[bb][w['world_id']] = diff[0]
                if bb == 't5': lens_t5.append(len(base))
            for s in S.states(d):
                x = S.render(w, s, t); texts[x] += 1
                if not Ev.score(x, S.gold(w, s, t), w, True)['success']: fails['gold'] += 1
                y = S.advance(d, s, 'plus')
                wrong = Ev.score(S.render(w, y, t), S.gold(w, s, t), w, True)
                col = [c for c in S.COLORS if c != w['color']][0]; recol = Ev.score(S.render(dict(w, color=col), s, t), S.gold(w, s, t), w, True)
                trunc = Ev.score(x[:-12], S.gold(w, s, t), w, True); unended = Ev.score(x, S.gold(w, s, t), w, False)
                if wrong['target'] or wrong['success'] or recol['preserved'] or recol['success'] or trunc['success'] or unended['success']: fails['negative_control'] += 1
                ps, _ = Ev.parse_state(x, d, S.people(w) if d in S.S1B else None)
                if ps != s: fails['parse_state'] += 1
        for bb in ('bart', 't5'):
            vals = set(per[bb].values())
            if t == 0:
                if len(vals) != 1: fails[f'{bb}_t0_slot_not_constant'] += 1
                slots[bb][d] = {'all': sorted(vals)[0] if vals else None}
            else:
                slots[bb][d] = {'per_world': per[bb]}
        dup = sum(1 for c in texts.values() if c > 1)
        nsp = sorted({w['split'] for w in new}); keys = {sp: {key(w) for w in new if w['split'] == sp} for sp in nsp}
        overlap = {f'{a}&{b}': len(keys[a] & keys[b]) for i, a in enumerate(nsp) for b in nsp[i + 1:]}
        fresh = [w for w in new if 'origin_world_id' not in w]; reused = [w for w in new if 'origin_world_id' in w]
        hist_key_overlap = len({key(w) for w in fresh} & hist_keys)
        hist_text_hits = sum(1 for w in fresh if any(S.render(w, s, t) in hist_texts for s in S.states(d)))
        c4_vs_reuse = len({S.render(w, s, t) for w in new if w['split'] == 'confirm4' for s in S.states(d)} &
                          {S.render(w, s, t) for w in reused for s in S.states(d)})
        for w in new:
            for s in S.states(d): new_texts[S.render(w, s, t)] += 1
        if d == 'bind3fix':
            k3 = {sp: {(w['object'], w['color'], w['quantity']) for w in new if w['split'] == sp} for sp in nsp}
            overlap.update({f'oqc:{a}&{b}': len(k3[a] & k3[b]) for i, a in enumerate(nsp) for b in nsp[i + 1:]})
        too_long = sum(1 for L in lens_t5 if L > cfg['source_cap']['t5gemma'])
        for s in S.states(d):
            c = Counter(len(ids['bart'](S.render(w, s, t))) for w in ws); g = Counter(len(ids['t5'](S.render(w, s, t))) for w in ws)
            table.append(dict(domain=d, template=t, state=s, word=S.word(d, s, ws[0]), bart_min=min(c), bart_max=max(c), t5_min=min(g), t5_max=max(g)))
        r = dict(worlds={sp: len(worlds4(d, sp)) for sp in SPLITS}, new_worlds={sp: sum(w['split'] == sp for w in new) for sp in nsp},
                 reused_worlds=len(reused), failures=dict(fails), duplicate_texts=dup, split_key_overlap=overlap, history_key_overlap=hist_key_overlap,
                 history_text_hits_fresh_worlds=hist_text_hits, confirm4_vs_reused_text_overlap=c4_vs_reuse,
                 t5_max_len=max(lens_t5) if lens_t5 else None, t5_over_cap=too_long,
                 slot_bart=slots['bart'][d].get('all', 'per-world'), slot_t5=slots['t5'][d].get('all', 'per-world'), sample=S.render(ws[0], S.states(d)[0], t))
        r['pass'] = (not fails and not dup and not any(overlap.values()) and not hist_key_overlap and not hist_text_hits and not c4_vs_reuse and not too_long)
        ok_all &= r['pass']; res['domains'][d] = r; print(d, {k: v for k, v in r.items() if k != 'sample'}, flush=True)
    res['cross_domain_duplicate_new_texts'] = sum(1 for c in new_texts.values() if c > 1)
    v3s = read(EXP / 'composability_mechanisms_v2/data/slot_positions.json')
    res['t0_slots_match_v3'] = {bb: all(slots[bb][d]['all'] == v3s[bb][d]['all'] for d in ('weekday', 'month', 'compass')) for bb in ('bart', 't5')}
    res['pass'] = ok_all and all(res['t0_slots_match_v3'].values()) and not res['cross_domain_duplicate_new_texts']; res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('sym4_semantics.py', 'sym4_evaluator.py', 'd_make_data.py', 'd_audit.py', 'lib4.py')}
    dump('data/audit.json', res); dump('data/slot_positions.json', slots); csvwrite('data/token_counts.csv', table)
    assert res['pass'], 'D audit failed'


if __name__ == '__main__':
    main()
