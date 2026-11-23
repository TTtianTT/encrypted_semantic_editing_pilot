"""Template split and assignment (CPU; after GT (data/audit.json) and GR (results/gates_mt_<bb>.json); PLAN 5.2).
Templates kept for a domain = GT and GR pass on every backbone that uses the domain (month-mt: BART and T5Gemma; weekday-mt, hour-mt:
BART). Seeded stratified split: templates with the distractor {Y} and without it are each split 2 : 1 into training and held-out
templates (n_train = round(2 n / 3) per stratum). Fewer than 8 held-out templates -> the domain leaves N.
Assignment: every train / dev world draws one training template, every confirm5 world one held-out template (seeded).
Writes data/<d>/worlds.jsonl (template_id filled), data/<d>/renders.jsonl, data/templates_split.json and data/slot_positions.json
(template-0 / binding domains from the audit; multi-template per world from the GT slot position of its (backbone, template))."""
import random
from symutil import *
import sym5_semantics as S

SEED = 2026112402
USERS = {'weekday-mt': ('bart',), 'month-mt': ('bart', 't5'), 'hour-mt': ('bart',)}


def main():
    require_slurm(); audit = read(ROOT / 'data/audit.json'); gr = {bb: read(ROOT / f'results/gates_mt_{bb}.json')['GR'] for bb in ('bart', 't5')}
    tm = read(ROOT / 'data/templates_mt.json')['templates']; slots = read(ROOT / 'data/slot_positions_t0b.json'); split = {}; counts = {}
    for di, d in enumerate(S.MT):
        bbs = USERS[d]; T = tm[d]
        keep = [t['id'] for t in T if all(t['id'] in audit['domains'][d]['GT_pass'][bb] and gr[bb][d].get(str(t['id']), {}).get('pass_') for bb in bbs)]
        removed = {t['id']: {bb: dict(GT=t['id'] in audit['domains'][d]['GT_pass'][bb], GR=gr[bb][d].get(str(t['id']), {}).get('rate')) for bb in bbs}
                   for t in T if t['id'] not in keep}
        rng = random.Random(SEED + di); train, held = [], []
        for has_y in (True, False):
            st = [i for i in keep if T[i]['has_Y'] == has_y]; rng.shuffle(st); k = round(2 * len(st) / 3)
            train += sorted(st[:k]); held += sorted(st[k:])
        ok = len(held) >= 8
        split[d] = dict(kept=keep, removed=removed, train=sorted(train), held_out=sorted(held), in_N=ok,
                        held_out_with_Y=[i for i in held if T[i]['has_Y']], train_with_Y=[i for i in train if T[i]['has_Y']])
        ws = rows(ROOT / f'data/{d}/worlds.jsonl'); rng = random.Random(SEED + 100 + di)
        for w in ws: w['template_id'] = rng.choice(sorted(train) if w['split'] in ('train', 'dev') else sorted(held)) if ok else None
        write(f'data/{d}/worlds.jsonl', ws)
        if ok:
            write(f'data/{d}/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], template=w['template_id'], state=s, text=S.render(w, s))
                                              for w in ws for s in S.states(d)])
            for bb in bbs:
                gt = audit['GT'][d][bb]; slots[bb][d] = {'per_world': {w['world_id']: gt[str(w['template_id'])]['slot'] for w in ws}}
        counts[d] = dict(templates=dict(kept=len(keep), train=len(train), held_out=len(held)), worlds={sp: sum(w['split'] == sp for w in ws) for sp in ('train', 'dev', 'confirm5')})
        print(d, split[d]['in_N'], counts[d], flush=True)
    dump('data/slot_positions.json', slots)
    dump('data/templates_split.json', dict(seed=SEED, rule='stratified by has_Y, 2:1 (round(2n/3) train), >= 8 held-out', users=USERS, split=split, counts=counts,
                                           templates_mt_sha256=sha(ROOT / 'data/templates_mt.json'),
                                           files={f'{d}/{n}': sha(ROOT / f'data/{d}/{n}') for d in S.MT for n in ('worlds.jsonl', 'renders.jsonl') if (ROOT / f'data/{d}/{n}').exists()}))


if __name__ == '__main__':
    main()
