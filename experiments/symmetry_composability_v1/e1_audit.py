"""E1.0 audit (CPU): gold texts score 100%; adjacent transitions share the BART attention mask; no duplicate texts;
split / history disjointness; token-count table; evaluator negative controls."""
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym_semantics as S
import sym_evaluator as Ev
from e1_make_data import history_files, key


def main():
    require_slurm(); t0 = time.time()
    tok = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    n = lambda t: len(tok(t)['input_ids'])
    hist = {key(w) for f in history_files() for w in rows(f)}
    res = dict(domains={}); table = []; ok_all = True
    for d in S.DOMAINS:
        ws = rows(ROOT / f'data/{d}/worlds.jsonl'); r = {}
        gold_fail = []; mask_fail = []; texts = Counter(); neg_fail = []
        for w in ws:
            for t in (0, 3):
                for s in S.states(d):
                    x = S.render(w, s, t); texts[x] += 1
                    sc = Ev.score(x, S.gold(w, s, t), w, True)
                    if not sc['success']:
                        gold_fail.append((w['world_id'], t, s))
                    try:
                        y = S.advance(d, s, 'plus')
                    except ValueError:
                        continue
                    if n(x) != n(S.render(w, y, t)):
                        mask_fail.append((w['world_id'], t, s, y))
                    # negative controls: wrong state, changed color, truncated output, unended output
                    wrong = Ev.score(S.render(w, y, t), S.gold(w, s, t), w, True)
                    col = [c for c in S.COLORS if c != w['color']][0]
                    w2 = dict(w, color=col); recol = Ev.score(S.render(w2, s, t), S.gold(w, s, t), w, True)
                    trunc = Ev.score(x[:-12], S.gold(w, s, t), w, True); unended = Ev.score(x, S.gold(w, s, t), w, False)
                    if wrong['target'] or wrong['success'] or recol['preserved'] or recol['success'] or trunc['success'] or unended['success']:
                        neg_fail.append((w['world_id'], t, s))
        dup = [x for x, c in texts.items() if c > 1]
        keys = {sp: {key(w) for w in ws if w['split'] == sp} for sp in ('train', 'dev', 'confirm')}
        overlap = {f'{a}&{b}': len(keys[a] & keys[b]) for a, b in (('train', 'dev'), ('train', 'confirm'), ('dev', 'confirm'))}
        confirm_hist = len(keys['confirm'] & hist)
        lengths = {}
        for t in (0, 3):
            for s in S.states(d):
                c = Counter(n(S.render(w, s, t)) for w in ws); lengths[f't{t}_s{s}'] = dict(sorted(c.items()))
                table.append(dict(domain=d, template=t, state=s, word=S.word(d, s), word_tokens=n(' ' + S.word(d, s)) - 2,
                                  min_tokens=min(c), max_tokens=max(c)))
        r = dict(worlds=len(ws), gold_success_failures=len(gold_fail), adjacent_mask_failures=len(mask_fail), duplicate_texts=len(dup),
                 split_key_overlap=overlap, confirm_history_overlap=confirm_hist, negative_control_failures=len(neg_fail),
                 examples=dict(gold=gold_fail[:5], mask=mask_fail[:5], dup=dup[:3], neg=neg_fail[:5]), lengths=lengths,
                 sample=dict(t0=S.render(ws[0], S.states(d)[0], 0), t3=S.render(ws[0], S.states(d)[0], 3)))
        r['pass'] = not gold_fail and not mask_fail and not dup and not any(overlap.values()) and confirm_hist == 0 and not neg_fail
        ok_all &= r['pass']; res['domains'][d] = r
        print(d, {k: v for k, v in r.items() if k not in ('examples', 'lengths', 'sample')}, flush=True)
    res['pass'] = ok_all; res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('sym_semantics.py', 'sym_evaluator.py', 'e1_make_data.py', 'e1_audit.py')}
    dump('data/audit.json', res); csvwrite('data/token_counts.csv', table)
    assert ok_all, 'E1.0 audit failed; fix templates before E1.1'


if __name__ == '__main__':
    main()
