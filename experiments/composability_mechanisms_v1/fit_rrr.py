"""Closed-form RRR for every (domain, map, rank) in the locked fit list; ridge per rank chosen on the train-internal 80/16 split
(token MSE), refit on all 96 train worlds (v1 e1_fit_rrr procedure). Dev single-step check for rank 16."""
import random
import time
import torch
from symutil import *
import sym2_semantics as S
import sym2_evaluator as Ev
sys.path.insert(0, str(CWR))
import fit as F


def paired(d, mapping, idx, caches):
    out = {}
    for op in ('plus', 'minus'):
        X = []; Y = []
        for s in S.states(d):
            try: y = S.advance(d, s, op, mapping)
            except ValueError: continue
            a, b = caches[s], caches[y]; assert torch.equal(a['m'][idx], b['m'][idx])
            v = a['m'][idx].bool(); X.append(a['h'][idx][v]); Y.append((b['h'][idx] - a['h'][idx])[v])
        out[op] = (torch.cat(X).double(), torch.cat(Y).double())
    return out


@torch.no_grad()
def dev_single(eng, d, mapping, fits):
    ws = worlds2(d, 'dev'); C = {s: cache2(d, 'dev', s) for s in S.states(d)}; ok = []
    for s in S.states(d):
        for op in ('plus', 'minus'):
            try: y = S.advance(d, s, op, mapping)
            except ValueError: continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); out = eng.decode(RRRop(fits[op, 16])(h, m), m)
            ok += [Ev.score(o['text'], S.gold(w, y, 0), w, o['ended'])['success'] for o, w in zip(out, ws)]
    return rate(ok)


def main():
    require_slurm(); p = verify_protocol2(); S.load_maps(ROOT / 'protocol.json'); cfg = p['rrr']; eng = engine(); summary = {}
    for spec in p['fits']:
        d, mapping, ranks = spec['domain'], spec['map'], spec['ranks']; tag = f'{d}_{mapping}'
        if (ROOT / f'results/fit_{tag}_complete.json').exists(): continue
        t0 = time.time(); ws = worlds2(d, 'train'); caches = {s: cache2(d, 'train', s) for s in S.states(d)}
        order = list(range(len(ws))); random.Random(cfg['inner_split_seed']).shuffle(order)
        fi, vi = sorted(order[:cfg['inner_fit']]), sorted(order[cfg['inner_fit']:])
        A = paired(d, mapping, fi, caches); B = paired(d, mapping, vi, caches); ALL = paired(d, mapping, list(range(len(ws))), caches)
        final = {}; sel = []
        for op in ('plus', 'minus'):
            st = F.sufficient(*A[op]); sc = {}
            for rel in cfg['ridge_grid']:
                for r, f in F.solve(st, rel, ranks).items():
                    sc[rel, r] = F.mse(*B[op], f); sel.append(dict(domain=d, map=mapping, op=op, rank=r, relative_ridge=rel, val_token_mse=sc[rel, r]))
            chosen = {r: min(cfg['ridge_grid'], key=lambda rel: sc[rel, r]) for r in ranks}
            sa = F.sufficient(*ALL[op]); sols = {rel: F.solve(sa, rel, ranks) for rel in set(chosen.values())}
            for r, rel in chosen.items():
                f = sols[rel][r]; f.update(op=op, domain=d, map=mapping, val_token_mse=sc[rel, r], fit_token_mse=F.mse(*ALL[op], f)); final[op, r] = f
        save(f'local/rrr_{tag}.pt', final); csvwrite(f'results/fit_selection_{tag}.csv', sel)
        info = dict(domain=d, map=mapping, ranks=ranks, chosen_ridge={f'{op}_{r}': final[op, r]['relative_ridge'] for op, r in final},
                    fit_token_mse={f'{op}_{r}': final[op, r]['fit_token_mse'] for op, r in final},
                    dev_single_RRR16=dev_single(eng, d, mapping, final) if 16 in ranks else None,
                    fit_sha256=sha(ROOT / f'local/rrr_{tag}.pt'), seconds=time.time() - t0)
        if mapping == 'natural' and d in V1_DOMAINS:  # determinism check against v1
            v1 = load(V1 / f'local/e1_rrr_{d}.pt')
            info['max_abs_diff_vs_v1_RRR16'] = max(float((final[op, 16]['left'] @ final[op, 16]['right'] - v1[op, 16]['left'] @ v1[op, 16]['right']).abs().max()) for op in ('plus', 'minus'))
        dump(f'results/fit_{tag}_complete.json', info); summary[tag] = info.get('dev_single_RRR16'); print('fit', tag, summary[tag], flush=True)


if __name__ == '__main__':
    main()
