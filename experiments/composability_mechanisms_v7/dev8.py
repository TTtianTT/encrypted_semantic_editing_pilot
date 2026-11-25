"""v8 dev chains and pre-checks (GPU, before the lock; dev decoded, confirm never). --unit N|G --backbone bart|t5|t5_9b|t5_bb|t5_ll.
For every cell of the unit (cells8.py) and path (plus, minus, alternating; 2N steps): simulate_chain7 on dev (readout, margin m, off-manifold
rho per world and step, vote model of the backbone and domain) and the decoded chain (trajectory success per world).
Then, on CPU in the same job:
- U threshold calibration (v7 calib_u.py procedure; A.4 grid; ties to the most permissive pair) on these dev cells; the v7-selected primary
  predictor is the slot readout (v7 Q21 = H-nofix), U is reported alongside (PLAN C1);
- discriminability pre-check (design rule 1; PLAN C2): N4 / G3 per backbone and domain from the latent (slot-readout) prediction on dev:
  F{1} plus <= 0.20, F{1} alt >= F_empty alt - 0.10, F_not1 plus <= 0.10; a condition the latent model itself puts on the wrong side is
  dropped (exploratory). G2 (rank threshold) the same: RRR-(r*_pred) plus >= 0.95 and RRR-(r*_pred - 2) plus <= 0.50 predicted on dev.
Output: results/dev8_<unit>_<bb>.json.gz (cells), results/dev8_<unit>_<bb>_summary.json."""
import gzip
import time
from cells8 import *


@torch.no_grad()
def decode_obs(eng, bb, d, ops, oplist, split):
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
    state = [w['start_state'] for w in ws]; ok = [True] * n; step1 = None                  # whole split at once: slot operators hold per-world positions
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    for k, op in enumerate(oplist):
        prev = torch.tensor(state, device=DEV); state = [S.advance(d, s, op) for s in state]; h = apply_op(ops[op], h, m, prev); outs = dec(eng, h, m)
        succ = [Ev.score(outs[j]['text'], S.gold(w, state[j], t), w, outs[j]['ended'])['success'] for j, w in enumerate(ws)]
        if k == 0: step1 = [Ev.parse_state(outs[j]['text'], d, gold=S.gold(w, state[j], t))[0] if d == S.NAT else Ev.parse_state(outs[j]['text'], d)[0] for j, w in enumerate(ws)]
        ok = [a and b for a, b in zip(ok, succ)]
    return ok, step1


def _perm(tm, tr):
    return (0 if tm is None else 1 + TAU_M.index(tm), 0 if tr is None else 1 + sorted([x for x in TAU_R if x is not None], reverse=True).index(tr))


def agreement(cells, tm, tr):
    ok = [p == o for sim, obs in cells for p, o in zip(u_predict(sim, tm, tr), obs)]; return float(np.mean(ok)) if ok else None


def calibrate_u(cells):
    table = [dict(tau_m=tm, tau_r=tr, agreement=agreement(cells, tm, tr)) for tm in TAU_M for tr in TAU_R]
    return dict(max(table, key=lambda x: (x['agreement'], tuple(-v for v in _perm(x['tau_m'], x['tau_r']))))), table


def prechecks(summ, unit, bb):
    pred = lambda d, meth, path: summ.get(f'{d}/{meth}/{path}', {}).get('pred_slot')
    out = {}
    for d in sorted({v['domain'] for v in summ.values()}):
        pre = 'nat_' if unit == 'N' else ''
        f1p, f1a, fea, fnp = pred(d, pre + 'F_{1}', 'plus'), pred(d, pre + 'F_{1}', 'alt'), pred(d, pre + 'F_empty', 'alt'), pred(d, pre + 'F_not1', 'plus')
        c = dict(F1_plus=None if f1p is None else dict(pred=f1p, keep=f1p <= .20), F1_alt=None if f1a is None or fea is None else dict(pred=f1a, ref=fea, keep=f1a >= fea - .10),
                 Fnot1_plus=None if fnp is None else dict(pred=fnp, keep=fnp <= .10))
        out[f'{"N4" if unit == "N" else "G3"}/{bb}/{d}'] = c
        if unit == 'G':
            _, _, rp = g_ranks(bb, d); a, b = pred(d, f'RRR{rp}' if rp != 16 else 'F_empty', 'plus'), pred(d, f'RRR{rp - 2}', 'plus')
            out[f'G2/{bb}/{d}'] = dict(rstar_pred=rp, hi=None if a is None else dict(pred=a, keep=a >= .95), lo=None if b is None else dict(pred=b, keep=b <= .50))
    return out


def main():
    require_slurm(); unit = sys.argv[sys.argv.index('--unit') + 1]; bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine8(bb)
    cells = n_cells(eng, bb, 'dev') if unit == 'N' else g_cells(eng, bb, 'dev'); out = {}; summ = {}; mans = {}; models = {}
    for fam, d, name, ops in cells:
        ops = ops() if callable(ops) else ops; N = len(S.states(d))
        if d not in mans: mans[d] = manifold(bb, d, 'dev'); models[d] = vote_model(bb, d)
        for path, oplist in PATHS(N).items():
            sim = simulate_chain7(bb, d, ops, oplist, models[d], split='dev', man=mans[d]); obs, step1 = decode_obs(eng, bb, d, ops, oplist, 'dev')
            key = f'{d}/{name}/{path}'; out[key] = dict(family=fam, domain=d, method=name, path=path, sim=sim, obs=obs, step1_decoded=step1)
            summ[key] = dict(family=fam, domain=d, method=name, path=path, obs=float(np.mean(obs)), pred_slot=float(np.mean(u_predict(sim, None, None))))
            print('dev8', unit, bb, key, fam, round(summ[key]['obs'], 3), round(summ[key]['pred_slot'], 3), flush=True)
    f = ROOT / f'results/dev8_{unit}_{bb}.json.gz'
    with gzip.open(f, 'wt') as g: json.dump(out, g)
    cal = [(v['sim'], v['obs']) for v in out.values() if v['family'] != 'ref']; best, table = calibrate_u(cal)
    res = dict(unit=unit, backbone=bb, cells=summ, U=dict(best=best, table=table, slot_only=agreement(cal, None, None), calibration_cells=len(cal)),
               prechecks=prechecks(summ, unit, bb), sha256=sha(f), resources=eng.resources(), seconds=time.time() - t0)
    dump(ROOT / f'results/dev8_{unit}_{bb}_summary.json', res); print(json.dumps(dict(U=res['U']['best'], slot=res['U']['slot_only'], pre=res['prechecks']))[:2000], flush=True)


if __name__ == '__main__':
    main()
