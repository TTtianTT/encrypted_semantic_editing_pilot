"""v9 encoding (GPU, before the lock; confirm encoded, never decoded): T5Gemma 2B-2B weekday template 0 on confirm7, which v7 did not
encode (v7 encoded T5Gemma month only). Slot position: 22 for every template-0 weekday world of the T5Gemma tokenizer and chat template
(v8 n_audit.json: constant slot 22 and token ids identical to 2B-2B on train, dev and confirm7); asserted here on the encoded masks and by
the single differing token across states. Output: local/t5_weekday_confirm7_t0_s<s>.pt, data/slot_positions.json, results/enc9.json."""
from lib9 import *


def main():
    require_slurm(); eng = engine8('t5'); d, sp = 'weekday', 'confirm7'; ws = worlds5(d, sp)
    tab = read(ROOT / 'data/slot_positions.json') if (ROOT / 'data/slot_positions.json').exists() else {}; tab.setdefault('t5', {})[d] = {'all': 22}; dump(ROOT / 'data/slot_positions.json', tab)
    ids = {s: [eng.tok(eng.tok.apply_chat_template([dict(role='user', content=eng.cfg['copy_instruction'] + S.render(w, s, 0))], tokenize=False, add_generation_prompt=True), add_special_tokens=False)['input_ids'] for w in ws] for s in S.states(d)}
    diff = {i for j in range(len(ws)) for s in S.states(d) for i in range(len(ids[0][j])) if ids[s][j][i] != ids[0][j][i]}
    assert diff == {22}, diff
    encode_split5(eng, 't5', d, sp, bs=32); m = cache5('t5', d, sp, 0)['m']; assert bool(m[:, 22].all())
    dump(ROOT / 'results/enc9.json', dict(worlds=len(ws), slot=22, differing_positions=sorted(diff), files={s: sha(cpath('t5', d, sp, s)) for s in S.states(d)}))


if __name__ == '__main__':
    main()
