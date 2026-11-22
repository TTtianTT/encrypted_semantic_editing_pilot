"""E0.1 encode: pooled last-layer encoder states for all 152 worlds of the four existing domains (no training)."""
import time
import torch
from symutil import *

REL = ['front', 'left', 'back', 'right']  # cyclic order under plus (heading+1), asserted below


def plan(S):
    """domain, template, state labels, list of (world -> text for state index)."""
    out = []
    for d, ts in (('time', (0,)), ('person', (0,)), ('space', (0, 1)), ('emotion', (0,))):
        for t in ts:
            out.append((d, t))
    return out


def texts_for(S, d, t, ws):
    if d != 'space':
        st = S.states(d)
        return st, [[S.render(w, s, t) for s in st] for w in ws], None
    tx = []; headings = []
    for w in ws:
        rel = {S.relation(w, h): h for h in range(4)}
        assert sorted(rel) == sorted(REL), rel
        hh = [rel[r] for r in REL]
        for i, h in enumerate(hh):  # plus = heading+1 must move to next relation in REL
            assert S.relation(w, S.advance('space', h, 'plus')) == REL[(i + 1) % 4]
        headings.append(hh); tx.append([S.render(w, h, t) for h in hh])
    return REL, tx, headings


@torch.no_grad()
def main():
    require_slurm(); verify_inputs(['four_domain/', 'model/', 'cache/conf/time_eval_t0', 'canonical_confirmation_v1/data/time_eval'])
    t0 = time.time(); S, _ = semantics(); eng = engine(); C = core(); summary = {}
    for d, t in plan(S):
        ws = worlds(d); labels, tx, hh = texts_for(S, d, t, ws)
        flat = [x for row in tx for x in row]; pooled = []; lengths = []
        for i in range(0, len(flat), 64):
            h, m = eng.encode(flat[i:i + 64]); pooled.append(C.pool(h, m).cpu()); lengths += m.sum(1).tolist()
        P = torch.cat(pooled).view(len(ws), len(labels), -1)
        save(f'local/e0_{d}_t{t}.pt', dict(pooled=P, world_ids=[w['world_id'] for w in ws], splits=[w['split'] for w in ws],
                                           states=list(labels), headings=hh, texts=tx,
                                           lengths=torch.tensor(lengths).view(len(ws), len(labels))))
        summary[f'{d}_t{t}'] = dict(worlds=len(ws), states=list(labels), texts=len(flat))
        print('encoded', d, t, P.shape, flush=True)
    # E0.3 needs canonical_confirmation confirm-world encodings for all 7 time states (template 0).
    cw = rows(CONF / 'data/time_eval.jsonl'); ids = [w['world_id'] for w in cw]; filled = []
    for s in range(-3, 4):
        p = CONF / f'local/time_eval_t0_s{s}.pt'
        ok = p.exists()
        if ok:
            c = load(p); ok = list(c.get('world_ids', ids)) == ids and len(c['h']) == len(ids)
        if not ok:
            hs = []; ms = []
            for i in range(0, len(cw), 32):
                h, m = eng.encode([S.render(w, s, 0) for w in cw[i:i + 32]]); hs.append(h.cpu()); ms.append(m.cpu())
            save(f'local/e0_conf_time_eval_t0_s{s}.pt', dict(h=torch.cat(hs), m=torch.cat(ms), world_ids=ids)); filled.append(s)
    summary['confirm_cache_filled_states'] = filled
    dump('results/e0_encode_complete.json', dict(summary=summary, resources=eng.resources(), seconds=time.time() - t0,
                                                 files={p.name: sha(p) for p in sorted((ROOT / 'local').glob('e0_*.pt'))}))


if __name__ == '__main__':
    main()
