"""G7-0 (GPU, first job after the lock; PLAN v7 B5): on confirm7, the base operators' one-way plus R_2N >= 0.95 - BART weekday / month
RRR-16 (template 0), T5Gemma month RRR-16 (template 0), the four multi-template combinations' S-RRR-16 (held-out templates) - and, on
BART, name3 Tok-U (v5, seeds 42-44; median) R_6 >= 0.95. Failing stops the run (assert). --backbone bart|t5. The base-operator chains are
the F_empty plus cells of unit U (u_chains.py skips them afterwards)."""
import time
from lib7 import *
from cells7 import u_cells, PATHS


def main():
    require_slurm(); p = verify_protocol6(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); res = dict(base={}, K={})
    for fam, d, name, ops in u_cells(eng, bb, CONFIRM):
        if name != 'F_empty' or (bb == 't5' and d not in ('month', 'month-mt')): continue
        N = len(S.states(d)); run_chain(eng, bb, d, 'natural', name, ops, 'plus_from_start', 'world_start', PATHS(N)['plus'], model=vote_model(bb, d))
        res['base'][d] = chain_rate(bb, d, 'natural', name, 'plus_from_start', 2 * N); print('G7-0', bb, d, res['base'][d]['rate'], flush=True)
    if bb == 'bart':
        trB = read(V5DIR / 'results/train_new_bart_B.json'); d = 'name3'
        for s in SEEDS:
            c = load(V5DIR / trB[f'Tok/{d}/s{s}']['path']); ed = tokatt_pair(eng.d, c['seed'], False); ed.load_state_dict(c['editor']); ed = ed.eval().requires_grad_(False)
            run_chain(eng, bb, d, 'natural', f'TokU_s{s}', {op: ed[op] for op in ('plus', 'minus')}, 'plus_from_start', 'world_start', ['plus'] * 6)
            res['K'][f'TokU_s{s}'] = chain_rate(bb, d, 'natural', f'TokU_s{s}', 'plus_from_start', 6)
        res['K_median_R6'] = float(np.median([v['rate'] for v in res['K'].values()]))
    res['pass'] = all(v['rate'] >= .95 for v in res['base'].values()) and (bb != 'bart' or res['K_median_R6'] >= .95)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/g70_{bb}.json', res)
    assert res['pass'], 'G7-0 failed: stop and investigate'


if __name__ == '__main__':
    main()
