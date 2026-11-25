"""v8 audit (CPU; tokenizers only, no model; before the lock). Writes data/slot_positions.json.
month-nat (unit N; BART and T5Gemma 2B-2B; train, dev, confirm8): per world the 12 month variants differ in exactly one token (the slot;
B.1 step 6), the gold of every variant scores as success and parses to its state, the next state's text never scores as the gold (negative
control), the start state is not May (B.1 step 5), no text repeats across worlds, and the texts do not occur in any earlier render of this
project (checked in prep_natural.py step 8; re-checked here against the v1-v7 template-0 month texts).
New backbones (units G and ladder; T5Gemma 9B-9B, B-B, L-L; weekday and month template 0; train, dev and the reused confirm7 = confirm6):
the slot is constant and single-token, and the token ids equal those of T5Gemma 2B-2B (same tokenizer and chat template)."""
import time
from collections import Counter
from transformers import AutoTokenizer
from symutil import *
import sym5_semantics as S
import sym5_evaluator as Ev

NAT = S.NAT
G_DOMAINS = ['weekday', 'month']
G_SPLITS = ['train', 'dev', 'confirm7']
EXP = ROOT.parent
V1 = EXP / 'symmetry_composability_v1'; V7DIR = EXP / 'composability_mechanisms_v6'
MODELS8 = {'t5_9b': 't5gemma-9b-9b-ul2-it', 't5_bb': 't5gemma-b-b-ul2-it', 't5_ll': 't5gemma-l-l-ul2-it'}


def worlds_g(d, split):
    f = V7DIR / f'data/{d}/worlds.jsonl' if split == 'confirm7' else V1 / f'data/{d}/worlds.jsonl'
    return [w for w in rows(f) if w['split'] == split]


def single_diff(seqs):
    if len({len(v) for v in seqs.values()}) != 1: return None
    b0 = next(iter(seqs.values())); diff = sorted({i for v in seqs.values() for i in range(len(b0)) if v[i] != b0[i]})
    return diff[0] if len(diff) == 1 else None


def main():
    require_slurm(); t0 = time.time(); cfg = read(SOURCE / 'config.json'); mm = read(SOURCE / 'model_manifest.json'); man8 = read(ROOT / 'data/model_manifest_v8.json')
    tb = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    toks = {'t5': AutoTokenizer.from_pretrained(mm['t5gemma']['directory'], local_files_only=True)}
    for bb, name in MODELS8.items(): toks[bb] = AutoTokenizer.from_pretrained(f'/dataset1/zailong/models/{name}', local_files_only=True)
    def t5ids(tok, t):
        return tok(tok.apply_chat_template([dict(role='user', content=cfg['copy_instruction'] + t)], tokenize=False, add_generation_prompt=True), add_special_tokens=False)['input_ids']
    ids = {'bart': lambda t: tb(t)['input_ids']} | {bb: (lambda tok: lambda t: t5ids(tok, t))(tok) for bb, tok in toks.items()}
    slots = {bb: {} for bb in ids}; res = dict(month_nat={}, new_backbones={}); ok = True

    # month-nat
    ws = [w for w in rows(ROOT / f'data/{NAT}/worlds.jsonl')]; texts = Counter(); fails = Counter()
    hist = set()
    for d0 in ('month', 'month-mt'):
        for f in sorted(EXP.glob(f'*/data/{d0}/worlds.jsonl')) + [V1 / f'data/{d0}/worlds.jsonl']:
            if f.exists():
                for w in rows(f):
                    try: hist.update(S.render(w, s, 0) for s in S.states(d0))
                    except Exception: pass
    for bb in ('bart', 't5'):
        slots[bb][NAT] = {'per_world': {}}
    for w in ws:
        st = S.states(NAT)
        if w['start_state'] == 4: fails['start_may'] += 1
        for bb in ('bart', 't5'):
            p = single_diff({s: ids[bb](S.render(w, s)) for s in st})
            if p is None: fails[f'{bb}_not_single_token'] += 1
            else: slots[bb][NAT]['per_world'][w['world_id']] = p
        for s in st:
            x = S.render(w, s); texts[x] += 1; g = S.gold(w, s)
            if x in hist: fails['history_text'] += 1
            sc = Ev.score(x, g, w, True)
            if not sc['success'] or Ev.parse_state(x, NAT, gold=g)[0] != s: fails['gold'] += 1
            y = S.render(w, S.advance(NAT, s, 'plus'))
            if Ev.score(y, g, w, True)['success'] or Ev.score(x, g, w, False)['success'] or Ev.score(x[:-2], g, w, True)['success']: fails['negative_control'] += 1
    by = Counter(w['split'] for w in ws)
    res['month_nat'] = dict(worlds=dict(by), failures=dict(fails), duplicate_texts=sum(1 for c in texts.values() if c > 1), history_texts=len(hist))
    ok &= not fails and res['month_nat']['duplicate_texts'] == 0

    # new backbones: template 0, constant slot, ids equal to T5Gemma 2B-2B
    for d in G_DOMAINS:
        for bb in MODELS8:
            vals = set(); same = True; n = 0
            for sp in G_SPLITS:
                for w in worlds_g(d, sp):
                    seqs = {s: ids[bb](S.render(w, s, 0)) for s in S.states(d)}; n += 1
                    vals.add(single_diff(seqs)); same &= all(seqs[s] == ids['t5'](S.render(w, s, 0)) for s in S.states(d))
            slots[bb][d] = {'all': sorted(vals)[0] if len(vals) == 1 and None not in vals else None}
            res['new_backbones'][f'{bb}/{d}'] = dict(worlds=n, slot=slots[bb][d]['all'], constant=len(vals) == 1 and None not in vals, ids_equal_t5_2b=same,
                                                    revision=next(v['revision'] for v in man8.values() if v.get('directory', '').endswith(MODELS8[bb])))
            ok &= res['new_backbones'][f'{bb}/{d}']['constant'] and same
    dump(ROOT / 'data/slot_positions.json', slots)
    res['pass'] = bool(ok); res['seconds'] = time.time() - t0; dump(ROOT / 'results/n_audit.json', res)
    print(json.dumps({k: v for k, v in res.items()}, indent=1)[:3000], flush=True)


if __name__ == '__main__':
    main()
