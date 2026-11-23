"""P2 (GPU, lane A, exploratory): C3 convergence. month and daysago (v1 train), seeds 42-44:
(a) C3 (CE + normalised canonical L2, lambda = 1), 6000 updates; (b) L2 only, 600 updates; (c) L2 only, 6000 updates.
CE and train L2 logged every 50 updates (CE logged without gradient for the L2-only variants), dev L2 every 500.
Evaluation on v3 confirm3 (already decoded in v3; no confirm4 data): month R_12 and R_24 (plus from the world start), daysago R_7 (plus from
two), DRIFT, per-plane eps_k (month). Reference: v2 RRR-16 dev/train L2. Pre-written readings (PLAN 4 P2):
under-trained if (a) or (c) reaches L2 <= 1.2 x RRR-16 and is composable; different solution if L2 converged (dev L2 change over the last
1000 updates < 2%) but not composable; CE/canonical conflict if (c) composable and (a) not."""
import time
import lib4
from lib4 import *

VARIANTS = {'a_C3_6000': dict(group='C3', updates=6000), 'b_L2_600': dict(group='L2', updates=600), 'c_L2_6000': dict(group='L2', updates=6000)}
PATHS = {'month': dict(plus_from_start=('world_start', ['plus'] * 24)), 'daysago': dict(plus_from_two=(2, ['plus'] * 7))}


def main():
    require_slurm(); t0 = time.time(); lib4.SHARDS = ROOT / 'results/patch/shards'; eng = engine4('bart'); res = {}
    for d in ('month', 'daysago'):
        N = len(S.states(d)); scale = l2_scales('bart', d, 'natural'); v2 = load(V2DIR / f'local/rrr_{d}_natural.pt')
        rrr = {op: RRRop(v2[op, 16]) for op in ('plus', 'minus')}
        res[f'{d}/RRR16'] = dict(dev_l2=dev_l2(rrr, 'bart', d, 'natural', scale), train_l2=dev_l2(rrr, 'bart', d, 'natural', scale, split='train'), l2_scale=scale)
        for name, cfg in VARIANTS.items():
            for s in SEEDS:
                f = ROOT / f'local/p2_{name}_{d}_s{s}.pt'
                ed, hist, _ = train_editor(eng, 'bart', d, 'natural', cfg['group'], s, updates=cfg['updates'], log_every=50, dev_every=500,
                                           dev_fn=lambda e: dev_l2(e, 'bart', d, 'natural', scale))
                save(f, dict(editor={k: v.cpu() for k, v in ed.state_dict().items()}, seed=s)); write(f'results/patch/p2_train_{name}_{d}_s{s}.jsonl', hist)
                ops = {op: ed[op] for op in ('plus', 'minus')}; key = f'{name}_s{s}'
                for pn, (st, oplist) in PATHS[d].items(): run_chain(eng, 'bart', d, 'natural', key, ops, pn, st, oplist, split='confirm3')
                sd = {k: v.cpu() for k, v in ed.state_dict().items()}; r = dict(final=hist[-1], dev_l2=dev_l2(ed, 'bart', d, 'natural', scale),
                                                                               train_l2=dev_l2(ed, 'bart', d, 'natural', scale, split='train'))
                dl = [h['dev_l2'] for h in hist if 'dev_l2' in h]; r['dev_l2_curve'] = dl
                r['converged'] = len(dl) >= 3 and abs(dl[-1] - dl[-3]) / dl[-3] < .02
                r['algebra'] = harmonics_of(*editor_factors('editor', sd, 'plus'), N)
                if d == 'month':
                    r['eps'] = {str(k): v['eps'] for k, v in op_plane_errors('editor', sd, 'plus', 'bart', d).items()}
                    r['R12'] = chain_rate('bart', d, 'natural', key, 'plus_from_start', 12); r['R24'] = chain_rate('bart', d, 'natural', key, 'plus_from_start', 24)
                    r['composable'] = r['R24']['rate'] >= .90
                else:
                    r['R7'] = chain_rate('bart', d, 'natural', key, 'plus_from_two', 7); r['composable'] = r['R7']['rate'] >= .90
                r['l2_within_1p2_rrr'] = r['dev_l2'] <= 1.2 * res[f'{d}/RRR16']['dev_l2']
                res[f'{d}/{key}'] = r
                print('P2', d, key, 'devL2', round(r['dev_l2'], 4), 'RRR16', round(res[f'{d}/RRR16']['dev_l2'], 4), 'comp', r['composable'],
                      'DRIFT', round(r['algebra']['DRIFT'], 3), round(time.time() - t0), flush=True)
    read_ = {}
    for d in ('month', 'daysago'):
        cell = lambda v: [res[f'{d}/{v}_s{s}'] for s in SEEDS]
        a, c = cell('a_C3_6000'), cell('c_L2_6000'); maj = lambda xs, f: sum(f(x) for x in xs) >= 2
        under = maj(a, lambda x: x['l2_within_1p2_rrr'] and x['composable']) or maj(c, lambda x: x['l2_within_1p2_rrr'] and x['composable'])
        diff = maj(a + c, lambda x: x['converged'] and not x['composable']) if not under else False
        conflict = maj(c, lambda x: x['composable']) and not maj(a, lambda x: x['composable'])
        read_[d] = dict(under_trained=under, different_solution=diff, ce_canonical_conflict=conflict, rule='majority (>= 2 of 3 seeds) per variant')
    res['reading'] = read_; res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump('results/patch/p2_c3.json', res)
    print(json.dumps(read_, indent=1), flush=True)


if __name__ == '__main__':
    main()
