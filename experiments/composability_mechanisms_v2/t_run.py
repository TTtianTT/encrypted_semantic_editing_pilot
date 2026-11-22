"""T (T5Gemma, after the lock). --stage fit | chains_rrr | train_c1 | eval_c1 | surgery."""
import time
from lib3 import *

RANKS = {'weekday': [4, 5, 6, 7, 16, 32], 'month': [9, 10, 11, 12, 16, 32], 'compass': [2, 3, 4, 16]}


def paths3(N, long_=False):
    out = dict(plus_from_start=['plus'] * (2 * N), minus_from_start=['minus'] * (2 * N), alt_from_start=['plus', 'minus'] * N)
    if long_: out['longplus'] = ['plus'] * (10 * N)
    return out


def fit_specs(p):
    out = []
    for d in p['gates']['t5']['T_rrr_domains']:
        N = len(S.states(d)); out.append((d, 'natural', RANKS[d])); out.append((d, 'scrmax', sorted({N - 1, 16, 32})))
    return out


def main():
    require_slurm(); p = verify_protocol3(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine3('t5'); res = {}
    if stage == 'fit':
        for d, mp, ranks in fit_specs(p):
            fits, info = fit_rrr3('t5', d, mp, ranks); save(f'local/t5_rrr_{d}_{mp}.pt', fits)
            res[f'{d}/{mp}'] = dict(ranks=ranks, ridge=info, dev16=dev_single(eng, 't5', d, mp, {op: RRRop(fits[op, 16]) for op in ('plus', 'minus')}))
            print('T fit', d, mp, res[f'{d}/{mp}']['dev16']['rate'], flush=True)
        dump('results/t_fit.json', res); return
    if stage == 'chains_rrr':
        for d, mp, ranks in fit_specs(p):
            fits = load(ROOT / f'local/t5_rrr_{d}_{mp}.pt'); N = len(S.states(d))
            for r in ranks:
                ops = {op: RRRop(fits[op, r]) for op in ('plus', 'minus')}
                for pn, oplist in paths3(N, long_=(r == 16)).items(): run_chain(eng, 't5', d, mp, f'RRR{r}', ops, pn, 'world_start', oplist)
                run_singles(eng, 't5', d, mp, f'RRR{r}', ops); print('T chains', d, mp, r, round(time.time() - t0), flush=True)
        for d in p['gates']['t5']['T_domains']:
            N = len(S.states(d))
            for pn, oplist in paths3(N).items(): run_chain(eng, 't5', d, 'natural', 'reencode', None, pn, 'world_start', oplist)
            run_singles(eng, 't5', d, 'natural', 'reencode', None)
        dump('results/t_chains_rrr_complete.json', dict(seconds=time.time() - t0, resources=eng.resources())); return
    if stage == 'train_c1':
        for d in p['gates']['t5']['T_domains']:
            for s in SEEDS:
                ed, hist, scale = train_editor(eng, 't5', d, 'natural', 'C1', s)
                save(f'local/t5_C1_{d}_s{s}.pt', dict(editor={k: v.cpu() for k, v in ed.state_dict().items()}, seed=s)); write(f'results/t_train_C1_{d}_s{s}.jsonl', hist)
                res[f'{d}/s{s}'] = dict(dev=dev_single(eng, 't5', d, 'natural', {op: ed[op] for op in ('plus', 'minus')}), final_loss=hist[-1]['loss'])
                print('T train', d, s, res[f'{d}/s{s}']['dev']['rate'], flush=True)
        dump('results/t_train_c1.json', res); return
    if stage == 'eval_c1':
        for d in p['gates']['t5']['T_domains']:
            N = len(S.states(d)); info, predict = probe('t5', d); res[f'{d}/probe'] = info
            for s in SEEDS:
                ed = load_editor(eng, ROOT / f'local/t5_C1_{d}_s{s}.pt'); ops = {op: ed[op] for op in ('plus', 'minus')}
                for pn, oplist in paths3(N).items(): run_chain(eng, 't5', d, 'natural', f'C1_s{s}', ops, pn, 'world_start', oplist)
                run_singles(eng, 't5', d, 'natural', f'C1_s{s}', ops)
                wm = write_metrics(eng, 't5', d, 'natural', ed['plus'], predict, m4=True); wm.pop('writes')
                res[f'{d}/C1_s{s}'] = wm; print('T eval C1', d, s, 'M1', round(wm['M1']['mean'], 3), 'M3', wm['M3'], flush=True)
        dump('results/t_eval_c1.json', res | dict(seconds=time.time() - t0, resources=eng.resources())); return
    if stage == 'surgery':
        for d in p['gates']['t5']['T_rrr_domains']:
            cal = p['calib']['t5'][d]; P = planes('t5', d); pos = slots('t5', d, 'confirm3'); X = slot_matrix('t5', d, 'train'); ks = [k for k, _ in P]; N = len(S.states(d))
            fits = load(ROOT / f'local/t5_rrr_{d}_natural.pt'); T = {op: RRRop(fits[op, 16]) for op in ('plus', 'minus')}
            def pe(K):
                B = torch.cat([B for k, B in P if k in K], 1); return {op: PlaneEd(*fit_plane_editor(X, B, d, op), B, pos) for op in ('plus', 'minus')}
            conds = {'F_empty': T, 'F_{1}': {op: Freeze(T[op], bvec(P, {1}), pos) for op in T},
                     'F_not1': {op: Freeze(T[op], bvec(P, set(ks) - {1}), pos) for op in T}, 'E_all': pe(set(ks))}
            K = cal['Kstar']['K']
            if sorted(K) != sorted(ks): conds['E_Kstar'] = pe(set(K))
            model = dict(P=P, lams={m: torch.tensor(v['lam'], dtype=torch.float64) for m, v in cal['models'].items()})
            for name, ops in conds.items():
                for pn, oplist in paths3(N).items(): run_chain(eng, 't5', d, 'natural', name, ops, pn, 'world_start', oplist, model=model)
                print('T surgery', d, name, round(time.time() - t0), flush=True)
        dump('results/t_surgery_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
