"""E1.4 closed-form RRR per domain and op (template 0, train only); ridge chosen per rank on the train-internal 80/16
split by token MSE, then refit on all 96 train worlds. Dev single-step admission check for RRR-16."""
import random
import time
import torch
from symutil import *
import sym_semantics as S
sys.path.insert(0, str(CWR))
import fit as F   # canonical_write_reachability_v1/fit.py: sufficient, solve, mse


def paired(d, idx, caches):
    xs = {}; 
    for op in ('plus', 'minus'):
        X = []; Y = []
        for s in S.states(d):
            try: y = S.advance(d, s, op)
            except ValueError: continue
            a, b = caches[s], caches[y]; assert torch.equal(a['m'][idx], b['m'][idx]), 'masks must align'
            v = a['m'][idx].bool(); X.append(a['h'][idx][v]); Y.append((b['h'][idx] - a['h'][idx])[v])
        xs[op] = (torch.cat(X).double(), torch.cat(Y).double())
    return xs


@torch.no_grad()
def dev_single(eng, d, ops, label):
    ws = e1_worlds(d, 'dev'); C = {s: e1_cache(d, 'dev', s) for s in S.states(d)}; ok = []; Ev = __import__('sym_evaluator')
    for s in S.states(d):
        for op in ('plus', 'minus'):
            try: y = S.advance(d, s, op)
            except ValueError: continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); out = eng.decode(ops[op](h, m), m)
            ok += [Ev.score(o['text'], S.gold(w, y, 0), w, o['ended'])['success'] for o, w in zip(out, ws)]
    return dict(method=label, **rate(ok))


def main():
    require_slurm(); p = verify_protocol(); doms = sys.argv[sys.argv.index('--domains') + 1].split(',')
    eng = engine(); cfg = p['rrr']
    for d in doms:
        if (ROOT / f'results/e1_rrr_{d}_complete.json').exists(): continue
        t0 = time.time(); ws = e1_worlds(d, 'train'); caches = {s: e1_cache(d, 'train', s) for s in S.states(d)}
        assert [w['world_id'] for w in ws] == caches[S.states(d)[0]]['world_ids']
        order = list(range(len(ws))); random.Random(cfg['inner_split_seed']).shuffle(order)
        fit_i, val_i = sorted(order[:cfg['inner_fit']]), sorted(order[cfg['inner_fit']:])
        A = paired(d, fit_i, caches); B = paired(d, val_i, caches); ALL = paired(d, list(range(len(ws))), caches)
        final = {}; sel = []
        for op in ('plus', 'minus'):
            st = F.sufficient(*A[op]); scores = {}
            for rel in cfg['ridge_grid']:
                for r, f in F.solve(st, rel, cfg['ranks']).items():
                    scores[rel, r] = F.mse(*B[op], f); sel.append(dict(domain=d, op=op, rank=r, relative_ridge=rel, val_token_mse=scores[rel, r]))
            chosen = {r: min(cfg['ridge_grid'], key=lambda rel: scores[rel, r]) for r in cfg['ranks']}
            sa = F.sufficient(*ALL[op]); sols = {rel: F.solve(sa, rel, cfg['ranks']) for rel in set(chosen.values())}
            for r, rel in chosen.items():
                f = sols[rel][r]; f.update(op=op, domain=d, val_token_mse=scores[rel, r], fit_token_mse=F.mse(*ALL[op], f)); final[op, r] = f
        save(f'local/e1_rrr_{d}.pt', final); csvwrite(f'results/e1_rrr_selection_{d}.csv', sel)
        dev = dev_single(eng, d, {op: RRRop(final[op, 16]) for op in ('plus', 'minus')}, 'RRR16')
        dump(f'results/e1_rrr_{d}_complete.json', dict(domain=d, inner_fit_worlds=[ws[i]['world_id'] for i in fit_i],
             inner_val_worlds=[ws[i]['world_id'] for i in val_i], chosen_ridge={f'{op}_{r}': final[op, r]['relative_ridge'] for op, r in final},
             training_tokens={op: int(ALL[op][0].shape[0]) for op in ALL}, dev_single_RRR16=dev, admission=dev['rate'] >= p['admission']['threshold'],
             fit_sha256=sha(ROOT / f'local/e1_rrr_{d}.pt'), protocol_sha256=sha(ROOT / 'protocol.json'), seconds=time.time() - t0))
        print('RRR', d, 'dev RRR16', dev['rate'], flush=True)


if __name__ == '__main__':
    main()
