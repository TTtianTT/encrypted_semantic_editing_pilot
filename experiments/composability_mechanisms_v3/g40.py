"""G4-0 (GPU, after the lock): for every kept (backbone, V domain) the base operator's one-way plus R_2N on confirm4 >= 0.95 (the chain is
the V unit's F{empty} plus chain, vote-model argmax recorded); BART: v1 C1 R_2 <= 0.20 on weekday, month, compass (3 seeds).
A new domain failing leaves V (and R); weekday or month failing, or any C1 cell failing, stops the lane (non-zero exit)."""
import time
from lib4 import *


def base_ops(p, bb, d):
    r = p['gates'][bb]['GB'][d]['base_rank']; f = load(ROOT / f'local/{bb}_rrr_{d}_natural_base.pt')
    return {op: RRRop(f[op, r]) for op in ('plus', 'minus')}, r


def vote_model(p, bb, d):
    cal = p['calib'][bb][d]
    return dict(P=planes(bb, d), lams={m: torch.tensor(v['lam'], dtype=torch.float64) for m, v in cal['models'].items()})


def run(eng, p, bb, split=CONFIRM, doms=None, c1_steps=2):
    res = dict(base={}, C1={}); doms = doms or p['gates'][bb]['V_domains']
    for d in doms:
        N = len(S.states(d)); ops, r = base_ops(p, bb, d)
        run_chain(eng, bb, d, 'natural', 'F_empty', ops, 'plus_from_start', 'world_start', ['plus'] * (2 * N), split=split, model=vote_model(p, bb, d))
        res['base'][d] = dict(rank=r, R_2N=chain_rate(bb, d, 'natural', 'F_empty', 'plus_from_start', 2 * N))
    if bb == 'bart':
        for d in ('weekday', 'month', 'compass'):
            for s in SEEDS:
                ed = load_editor(eng, V1 / f'local/e1_C1_{d}_s{s}_0600.pt')
                run_chain(eng, bb, d, 'natural', f'C1v1_s{s}', {op: ed[op] for op in ('plus', 'minus')}, 'g40_plus', 'world_start', ['plus'] * c1_steps, split=split)
                res['C1'][f'{d}/s{s}'] = chain_rate(bb, d, 'natural', f'C1v1_s{s}', 'g40_plus', c1_steps)
    res['V_domains_post'] = [d for d in doms if res['base'][d]['R_2N']['rate'] >= .95]
    res['old_ok'] = all(res['base'][d]['R_2N']['rate'] >= .95 for d in doms if d in ('weekday', 'month'))
    res['C1_ok'] = all(v['rate'] <= .20 for v in res['C1'].values())
    res['pass'] = res['old_ok'] and res['C1_ok']
    return res


def main():
    require_slurm(); p = verify_protocol4(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine4(bb)
    res = run(eng, p, bb); res['seconds'] = time.time() - t0; dump(f'results/g40_{bb}.json', res)
    print('G4-0', bb, res['pass'], 'V post', res['V_domains_post'], flush=True)
    assert res['pass'], 'G4-0 failed on an old domain or C1: stop and debug the pipeline'


if __name__ == '__main__':
    main()
