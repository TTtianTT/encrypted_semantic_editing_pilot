"""G5-0 sanity gate (GPU, after the lock; PLAN 5.4). --backbone bart|t5. For every L domain the base operator's one-way plus chain
(2N steps) on confirm5 (this is the L cell F_empty / plus, written once and reused by l_chains); BART also v1's C1 on weekday and month,
2 steps (R_2 <= 0.20). Fail -> stop and investigate."""
import time
from lib5 import *
from cells import PATHS


def main():
    require_slurm(); p = verify_protocol5(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); res = dict(base={}, C1={})
    for d in L_DOMAINS[bb]:
        N = len(S.states(d)); run_chain(eng, bb, d, 'natural', 'F_empty', base_ops(bb, d), 'plus_from_start', 'world_start', PATHS(N)['plus'], model=vote_model(bb, d))
        res['base'][d] = chain_rate(bb, d, 'natural', 'F_empty', 'plus_from_start', 2 * N); print('G5-0 base', bb, d, res['base'][d]['rate'], flush=True)
    if bb == 'bart':
        for d in ('weekday', 'month'):
            for s in SEEDS:
                ed = load_editor(eng, V1 / f'local/e1_C1_{d}_s{s}_0600.pt')
                run_chain(eng, bb, d, 'natural', f'C1v1_s{s}', {op: ed[op] for op in ('plus', 'minus')}, 'g50_plus', 'world_start', ['plus', 'plus'])
                res['C1'][f'{d}/s{s}'] = chain_rate(bb, d, 'natural', f'C1v1_s{s}', 'g50_plus', 2)
    res['pass'] = all(v['rate'] >= .95 for v in res['base'].values()) and all(v['rate'] <= .20 for v in res['C1'].values())
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/g50_{bb}.json', res)
    assert res['pass'], 'G5-0 failed: stop and investigate'


if __name__ == '__main__':
    main()
