"""D audit (CPU): v2's five checks plus (6) single-token state words and slot positions under BART BPE and the Gemma tokenizer
(chat-wrapped as Backend.wrap), template-0 slot constant within a domain; (7) T5Gemma input <= source_cap."""
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym3_semantics as S
import sym3_evaluator as Ev
from lib3 import worlds3, tmpl, T_DOMAINS
from d_make_data import history_files, key, ALL


def main():
    require_slurm(); t0 = time.time(); cfg = read(SOURCE / 'config.json'); mm = read(SOURCE / 'model_manifest.json')
    tb = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    tg = AutoTokenizer.from_pretrained(mm['t5gemma']['directory'], local_files_only=True)
    wrap = lambda t: tg.apply_chat_template([dict(role='user', content=cfg['copy_instruction'] + t)], tokenize=False, add_generation_prompt=True)
    ids = {'bart': lambda t: tb(t)['input_ids'], 't5': lambda t: tg(wrap(t), add_special_tokens=False)['input_ids']}
    hist_new = {key(w) for f in history_files() for w in rows(f)}
    res = dict(domains={}); table = []; slots = {'bart': {}, 't5': {}}; ok_all = True
    for d in ALL:
        t = tmpl(d); splits = ['train', 'dev', 'confirm3']; ws = [w for sp in splits for w in worlds3(d, sp)]
        new = [w for w in rows(ROOT / f'data/{d}/worlds.jsonl')]
        fails = Counter(); texts = Counter(); per = {'bart': {}, 't5': {}}; lens_t5 = []
        bbs = ['bart', 't5'] if (d in T_DOMAINS or t == 0) else ['bart', 't5']
        for w in ws:
            for bb in bbs:
                seqs = {s: ids[bb](S.render(w, s, t)) for s in S.states(d)}
                if len({len(v) for v in seqs.values()}) != 1: fails[f'{bb}_mask'] += 1; continue
                base = seqs[S.states(d)[0]]; diff = sorted({i for s in seqs for i in range(len(base)) if seqs[s][i] != base[i]})
                if len(diff) != 1: fails[f'{bb}_not_single_token'] += 1; continue
                per[bb][w['world_id']] = diff[0]
                if bb == 't5': lens_t5.append(len(base))
            for s in S.states(d):
                x = S.render(w, s, t); texts[x] += 1
                if not Ev.score(x, S.gold(w, s, t), w, True)['success']: fails['gold'] += 1
                try: y = S.advance(d, s, 'plus')
                except ValueError: continue
                wrong = Ev.score(S.render(w, y, t), S.gold(w, s, t), w, True)
                col = [c for c in S.COLORS if c != w['color']][0]; recol = Ev.score(S.render(dict(w, color=col), s, t), S.gold(w, s, t), w, True)
                trunc = Ev.score(x[:-12], S.gold(w, s, t), w, True); unended = Ev.score(x, S.gold(w, s, t), w, False)
                if wrong['target'] or wrong['success'] or recol['preserved'] or recol['success'] or trunc['success'] or unended['success']: fails['negative_control'] += 1
                ps, _ = Ev.parse_state(x, d, S.people(w) if d in S.S1B else None)
                if ps != s: fails['parse_state'] += 1
        for bb in bbs:
            vals = set(per[bb].values())
            if t == 0:
                if len(vals) != 1: fails[f'{bb}_t0_slot_not_constant'] += 1
                slots[bb][d] = {'all': sorted(vals)[0] if vals else None}
            else:
                slots[bb][d] = {'per_world': per[bb]}
        dup = sum(1 for c in texts.values() if c > 1)
        nsp = sorted({w['split'] for w in new}); keys = {sp: {key(w) for w in new if w['split'] == sp} for sp in nsp}
        overlap = {f'{a}&{b}': len(keys[a] & keys[b]) for i, a in enumerate(nsp) for b in nsp[i + 1:]}
        hist_overlap = {sp: len(keys[sp] & hist_new) for sp in nsp}
        if d == 'bind3fix':
            k3 = {sp: {(w['object'], w['color'], w['quantity']) for w in new if w['split'] == sp} for sp in nsp}
            overlap.update({f'oqc:{a}&{b}': len(k3[a] & k3[b]) for i, a in enumerate(nsp) for b in nsp[i + 1:]})
        too_long = sum(1 for L in lens_t5 if L > cfg['source_cap']['t5gemma'])
        for s in S.states(d):
            c = Counter(len(ids['bart'](S.render(w, s, t))) for w in ws); g = Counter(len(ids['t5'](S.render(w, s, t))) for w in ws)
            table.append(dict(domain=d, template=t, state=s, word=S.word(d, s, ws[0]), bart_min=min(c), bart_max=max(c), t5_min=min(g), t5_max=max(g)))
        r = dict(worlds=len(ws), new_worlds={sp: len([w for w in new if w['split'] == sp]) for sp in nsp}, failures=dict(fails), duplicate_texts=dup,
                 split_key_overlap=overlap, history_overlap=hist_overlap, t5_max_len=max(lens_t5) if lens_t5 else None, t5_over_cap=too_long,
                 slot_bart=slots['bart'][d].get('all', 'per-world'), slot_t5=slots['t5'][d].get('all', 'per-world'),
                 sample=S.render(ws[0], S.states(d)[0], t))
        r['pass'] = not fails and not dup and not any(overlap.values()) and not any(hist_overlap.values()) and not too_long
        ok_all &= r['pass']; res['domains'][d] = r; print(d, {k: v for k, v in r.items() if k != 'sample'}, flush=True)
    # report only: did v2 confirm2 reuse v1 texts? (v2's generator deduplicated within confirm2 only)
    v2rep = {}
    for d in V1_DOMAINS:
        v1t = {r['text'] for r in rows(V1 / f'data/{d}/renders.jsonl') if r['split'] in ('train', 'dev')}
        c2 = [r for r in rows(EXP / f'composability_mechanisms_v1/data/{d}/renders.jsonl') if r['template'] == 0]
        hit = {r['world_id'] for r in c2 if r['text'] in v1t}
        v2rep[d] = dict(confirm2_worlds_with_text_in_v1_train_dev=len(hit), confirm2_worlds=len({r['world_id'] for r in c2}))
    res['v2_confirm2_text_reuse_report'] = v2rep
    v2s = read(EXP / 'composability_mechanisms_v1/data/slot_positions.json')
    res['bart_t0_slots_match_v2'] = all(slots['bart'][d]['all'] == v2s[d]['0'] for d in V1_DOMAINS)
    res['pass'] = ok_all and res['bart_t0_slots_match_v2']; res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('sym3_semantics.py', 'sym3_evaluator.py', 'd_make_data.py', 'd_audit.py', 'lib3.py')}
    dump('data/audit.json', res); dump('data/slot_positions.json', slots); csvwrite('data/token_counts.csv', table)
    assert res['pass'], 'D audit failed'


if __name__ == '__main__':
    main()
