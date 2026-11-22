"""D audit (CPU): gold 100%; equal BART masks for all states of a world (covers every map); key disjointness;
token table; negative controls; single attribute-slot position per domain/template (recorded for S2/S3)."""
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym2_semantics as S
import sym2_evaluator as Ev
from d_make_data import history_files, key, ALL


def main():
    require_slurm(); t0 = time.time()
    tok = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    ids = lambda t: tok(t)['input_ids']
    hist = {key(w) for f in history_files() for w in rows(f)}
    res = dict(domains={}); table = []; slots = {}; ok_all = True
    for d in ALL:
        ws = rows(ROOT / f'data/{d}/worlds.jsonl'); gold_fail = []; mask_fail = []; neg_fail = []; slot_fail = []; texts = Counter(); pos = {0: set(), 3: set()}
        for w in ws:
            for t in (0, 3):
                seqs = {s: ids(S.render(w, s, t)) for s in S.states(d)}
                if len({len(v) for v in seqs.values()}) != 1:
                    mask_fail.append((w['world_id'], t)); continue
                diff = sorted({i for s in seqs for i in range(len(seqs[s])) if seqs[s][i] != seqs[S.states(d)[0]][i]})
                if len(diff) != 1: slot_fail.append((w['world_id'], t, diff))
                else: pos[t].add(diff[0])
                for s in S.states(d):
                    x = S.render(w, s, t); texts[x] += 1
                    if not Ev.score(x, S.gold(w, s, t), w, True)['success']: gold_fail.append((w['world_id'], t, s))
                    try: y = S.advance(d, s, 'plus')
                    except ValueError: continue
                    wrong = Ev.score(S.render(w, y, t), S.gold(w, s, t), w, True)
                    col = [c for c in S.COLORS if c != w['color']][0]
                    recol = Ev.score(S.render(dict(w, color=col), s, t), S.gold(w, s, t), w, True)
                    trunc = Ev.score(x[:-12], S.gold(w, s, t), w, True); unended = Ev.score(x, S.gold(w, s, t), w, False)
                    if wrong['target'] or wrong['success'] or recol['preserved'] or recol['success'] or trunc['success'] or unended['success']:
                        neg_fail.append((w['world_id'], t, s))
        # template 0 must have one constant slot position (S2/S3 use it); template 3 starts with a name whose BPE length varies
        # (no leading space), so its single slot position may vary by world and is recorded as a set.
        if len(pos[0]) != 1: slot_fail.append(('non-constant template-0 slot position', sorted(pos[0])))
        slots[d] = {'0': sorted(pos[0])[0] if len(pos[0]) == 1 else None, '3': None, '3_positions': sorted(pos[3])}
        dup = [x for x, c in texts.items() if c > 1]
        splits = sorted({w['split'] for w in ws}); keys = {sp: {key(w) for w in ws if w['split'] == sp} for sp in splits}
        overlap = {f'{a}&{b}': len(keys[a] & keys[b]) for i, a in enumerate(splits) for b in splits[i + 1:]}
        hist_overlap = {sp: len(keys[sp] & hist) for sp in splits}
        for t in (0, 3):
            for s in S.states(d):
                c = Counter(len(ids(S.render(w, s, t))) for w in ws)
                table.append(dict(domain=d, template=t, state=s, word=S.word(d, s, ws[0]), min_tokens=min(c), max_tokens=max(c), slot=slots[d][str(t)]))
        r = dict(worlds=len(ws), splits={sp: len([w for w in ws if w['split'] == sp]) for sp in splits}, gold_failures=len(gold_fail),
                 mask_failures=len(mask_fail), slot_failures=len(slot_fail), negative_control_failures=len(neg_fail), duplicate_texts=len(dup),
                 split_key_overlap=overlap, history_overlap=hist_overlap, slot_positions=slots[d],
                 examples=dict(gold=gold_fail[:3], mask=mask_fail[:3], slot=slot_fail[:3], neg=neg_fail[:3]),
                 sample={f't{t}': S.render(ws[0], S.states(d)[0], t) for t in (0, 3)})
        r['pass'] = not (gold_fail or mask_fail or slot_fail or neg_fail or dup or any(overlap.values()) or any(hist_overlap.values()))
        ok_all &= r['pass']; res['domains'][d] = r
        print(d, {k: v for k, v in r.items() if k not in ('examples', 'sample')}, flush=True)
    res['pass'] = ok_all; res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('sym2_semantics.py', 'sym2_evaluator.py', 'd_make_data.py', 'd_audit.py')}
    dump('data/audit.json', res); dump('data/slot_positions.json', slots); csvwrite('data/token_counts.csv', table)
    assert ok_all, 'D audit failed; fix templates first'


if __name__ == '__main__':
    main()
