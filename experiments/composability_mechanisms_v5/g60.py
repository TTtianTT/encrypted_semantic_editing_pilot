"""G6-0 sanity gate (GPU, after the lock; PLAN B4). --backbone bart|t5. Fail -> stop and investigate.
- M: every kept domain's GM base operator, one-way plus R_2N >= 0.95 on the dev worlds of the training templates (re-check);
- C (BART): the RRR-16 base operator on confirm6, one-way plus R_2N >= 0.95 on weekday and month (= the C cell F_empty / plus, written
  once and reused by c_chains);
- K (BART): v5's Tok-U on name3, plus R_6 >= 0.95 (seed median; = the K cell TokU_s<s> / plus, reused by k_chains)."""
import time
from lib6 import *
from cells6 import PATHS, K_PATHS, k_cells


def main():
    require_slurm(); p = verify_protocol6(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    gates = read(ROOT / f'results/gates_{bb}.json'); res = dict(M={}, C={}, K={})
    for d in gates['M_domains']:
        N = len(S.states(d)); T = m_base_ops(bb, d, gates, slots(bb, d, 'dev'))
        res['M'][d] = dev_chain(eng, bb, d, 'natural', T, ['plus'] * (2 * N))[-1]; print('G6-0 M', bb, d, res['M'][d]['rate'], flush=True)
    if bb == 'bart':
        for d in C_DOMAINS:
            N = len(S.states(d)); run_chain(eng, bb, d, 'natural', 'F_empty', base_ops(bb, d), 'plus_from_start', 'world_start', PATHS(N)['plus'], model=ctx_model(bb, d, CONFIRM))
            res['C'][d] = chain_rate(bb, d, 'natural', 'F_empty', 'plus_from_start', 2 * N); print('G6-0 C', d, res['C'][d]['rate'], flush=True)
        for d, name, ops in k_cells(eng, CONFIRM):
            if d != 'name3' or not name.startswith('TokU_'): continue
            run_chain(eng, bb, d, 'natural', name, ops() if callable(ops) else ops, 'plus_from_start', 'world_start', K_PATHS['plus'])
            res['K'][name] = chain_rate(bb, d, 'natural', name, 'plus_from_start', 6)
        res['K_median_R6'] = float(np.median([v['rate'] for v in res['K'].values()]))
    res['pass'] = all(v['rate'] >= .95 for v in res['M'].values()) and all(v['rate'] >= .95 for v in res['C'].values()) and (bb != 'bart' or res['K_median_R6'] >= .95)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/g60_{bb}.json', res)
    assert res['pass'], 'G6-0 failed: stop and investigate'


if __name__ == '__main__':
    main()
