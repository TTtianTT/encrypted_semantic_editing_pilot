"""A: the alternating path on held-out templates (Q22; PLAN v7 B8, appendix A.6, A.7). --backbone bart|t5 --mode precheck|run|smoke.
P = v6's GM operator S-RRR-16 (slot only), M = v6's minus operator; P^-1 by the Woodbury identity (SlotRRRinv).
precheck (before the lock): cond(I_r + R L) < 1e3 and P^-1(P(h)) = h (relative error < 1e-5) on dev7-ho slot vectors, per (backbone, domain).
run (after the lock), confirm7, held-out templates: A2 first-order errors on clean inputs (cycle-sum ratio, alternating contrast; per world,
  median over worlds); A3 one-way minus with P^-1 as the minus operator and A3b alternating (P, P^-1), decoded, 2N steps, R_2N; the training-
  template dev repetition of A2 (exploratory). A1 (rho on the F_empty chains) is computed by analyze.py from the locked simulation.
smoke: run mode on dev7-ho (code path only). Output: results/a_<mode>_<bb>.json (+ shards for A3 / A3b in run mode)."""
import time
from lib7 import *


def P_ops(bb, d, split):
    gates = read(V6DIR / f'results/gates_{bb}.json'); pos = slots(bb, d, split); T = m_base_ops(bb, d, gates, pos); return T, SlotRRRinv(T['plus'])


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; mode = sys.argv[sys.argv.index('--mode') + 1]; t0 = time.time(); out = dict(mode=mode, backbone=bb, cells={})
    if mode == 'run': assert lock_ok()
    eng = engine5(bb) if mode != 'precheck' else None
    for d in M_DOMAINS[bb]:
        split = 'dev7ho' if mode in ('precheck', 'smoke') else CONFIRM; T, inv = P_ops(bb, d, split); man = manifold(bb, d, split); r = dict(cond=inv.cond)
        hs = man['Cw'].reshape(-1, man['Cw'].shape[-1]).to(DEV); back = inv.slot(slot_map(T['plus'], hs))
        r['inverse_rel_err'] = float((back - hs.double()).norm() / hs.double().norm()); r['precheck_pass'] = r['cond'] < 1e3 and r['inverse_rel_err'] < 1e-5
        if mode != 'precheck':
            e = first_order_errors(man, T['plus'], T['minus'], d)
            r['A2'] = dict(cycle_sum_ratio_median=float(e['cycle_sum_ratio'].median()), alt_contrast_median=float(e['alt_contrast'].median()),
                           eP_rel_median=float(e['eP_norm'].median()), eM_rel_median=float(e['eM_norm'].median()), worlds=len(e['cycle_sum_ratio']))
            N = len(S.states(d)); ops = {'plus': T['plus'], 'minus': inv}
            if mode == 'run':
                for name, path, ol in (('Pinv', 'minus', ['minus'] * (2 * N)), ('PPinv', 'alt', ['plus', 'minus'] * N)):
                    run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol, model=vote_model(bb, d))
                    r[f'A3_{name}'] = chain_rate(bb, d, 'natural', name, f'{path}_from_start', 2 * N)
            else:
                from devchains import decode_chain
                for name, ol in (('Pinv', ['minus'] * (2 * N)), ('PPinv', ['plus', 'minus'] * N)):
                    ok, _, _ = decode_chain(eng, bb, d, ops, ol, split); r[f'A3_{name}'] = rate(ok)
            if mode == 'run':                                                     # exploratory: A2 on the training-template dev
                Td, _ = P_ops(bb, d, 'dev'); md = manifold(bb, d, 'dev'); e2 = first_order_errors(md, Td['plus'], Td['minus'], d)
                r['A2_train_template_dev'] = dict(cycle_sum_ratio_median=float(e2['cycle_sum_ratio'].median()), alt_contrast_median=float(e2['alt_contrast'].median()),
                                                  eP_rel_median=float(e2['eP_norm'].median()), eM_rel_median=float(e2['eM_norm'].median()))
        out['cells'][f'{bb}/{d}'] = r; print('A', mode, bb, d, {k: v for k, v in r.items() if not isinstance(v, dict)}, flush=True)
    out['seconds'] = time.time() - t0
    if eng is not None: out['resources'] = eng.resources()
    dump(ROOT / ('local/smoke' if mode == 'smoke' else 'results') / f'a_{mode}_{bb}.json', out)


if __name__ == '__main__':
    main()
