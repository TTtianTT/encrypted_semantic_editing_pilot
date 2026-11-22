"""L: lock the protocol (predictions, thresholds, decision rules, permutation tables, data and source SHA256) before any
confirm2 / S1b-confirm encoding or decoding."""
import time
from symutil import *
import sym2_semantics as S

GRID = {'weekday': [4, 5, 6, 7, 8], 'month': [8, 9, 10, 11, 12, 14, 16], 'compass': [2, 3, 4], 'egoside': [2, 3, 4], 'daysago': [6, 7, 8, 10, 12, 16]}
MODES = {'weekday': [4, 5, 16], 'month': [8, 9, 10, 16], 'compass': [2, 16], 'egoside': [2, 16]}
SEEDS_E = [42, 43, 44]


def chains(d, mp, maps):
    if d in S1B_DOMAINS:
        return dict(plus_from_start=dict(start='world_start', ops=['plus'] * 30, short_len=30), minus_from_start=dict(start='world_start', ops=['minus'] * 6, short_len=6),
                    alternating_from_0=dict(start=0, ops=['plus', 'minus'] * 3, short_len=6))
    if d == 'daysago':
        P = list(range(2, 10)) if mp == 'natural' else maps[d][mp]['path']
        return dict(plus_from_path_start=dict(start=P[0], ops=['plus'] * 7, short_len=7), minus_from_path_end=dict(start=P[-1], ops=['minus'] * 7, short_len=7),
                    alternating_from_path_4th=dict(start=P[3], ops=['plus', 'minus'] * 5, short_len=10))
    N = len(S.states(d))
    return dict(plus_from_start=dict(start='world_start', ops=['plus'] * (10 * N), short_len=2 * N), minus_from_start=dict(start='world_start', ops=['minus'] * (2 * N), short_len=2 * N),
                alternating_from_0=dict(start=0, ops=['plus', 'minus'] * N, short_len=2 * N))


def rrr(name_map, r, paths, singles=(0,)):
    return dict(name=f'RRR{r}', map=name_map, kind='RRR', rank=r, paths=paths, single_templates=list(singles))


def main():
    require_slurm(); t0 = time.time()
    assert not (ROOT / 'protocol.json').exists(), 'already locked; never rewrite'
    assert not list((ROOT / 'local').glob('c_*confirm*')), 'confirm encodings must not exist before the lock'
    assert not (ROOT / 'results/shards').exists(), 'no confirm decoding before the lock'
    assert read(ROOT / 'data/audit.json')['pass']
    sel = read(ROOT / 'results/s1a_selection.json'); maps = sel['maps']
    fits = []; methods = {}; ch = {}
    for d in V1_DOMAINS:
        mps = ['natural'] + [m for m in ('scrmax', 'scrmed') if m in maps[d]]; ch[d] = {mp: chains(d, mp, maps) for mp in mps}; methods[d] = []
        for mp in mps:
            ranks = {16, 32}
            if mp == 'natural' or (mp == 'scrmax' and d in ('weekday', 'month')): ranks |= set(GRID[d])
            fits.append(dict(domain=d, map=mp, ranks=sorted(ranks)))
            methods[d] += [rrr(mp, 16, 'full'), rrr(mp, 32, 'full')]
            methods[d] += [rrr(mp, r, 'short') for r in sorted(ranks - {16, 32})]
        methods[d] += [dict(name=f'C1_s{s}', map='natural', kind='C1', seed=s, paths='short', single_templates=[0]) for s in SEEDS_E]
        methods[d] += [dict(name='reencode', map='natural', kind='reencode', paths='full', single_templates=[0])]
    for d in S1B_DOMAINS:
        ch[d] = {'natural': chains(d, 'natural', maps)}; fits.append(dict(domain=d, map='natural', ranks=[16, 32]))
        methods[d] = [rrr('natural', 16, 'full', (0, 3)), rrr('natural', 32, 'full', (0, 3))]
        methods[d] += [dict(name=f'{g}_s{s}', map='natural', kind=g, seed=s, paths='full', single_templates=[0]) for g in ('C1', 'C3') for s in SEEDS_E]
        methods[d] += [dict(name='reencode', map='natural', kind='reencode', paths='full', single_templates=[0, 3])]
    data_files = [f'data/{d}/worlds.jsonl' for d in V1_DOMAINS + S1B_DOMAINS] + ['data/audit.json', 'data/slot_positions.json', 'data/manifest.json',
                  'results/s1a_selection.json', 'results/s1b_geometry.json', 'inputs_manifest.json', 'PLAN.md']
    p = dict(
        locked=True, created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), version=1, plan='PLAN.md',
        domains=dict(v1=V1_DOMAINS, s1b=S1B_DOMAINS), confirm=dict(v1='confirm2 (160 new worlds per domain)', s1b='confirm (160)'),
        s1a=dict(maps=maps, natural_E_iso={d: sel['summary'][d]['natural_E_iso'] for d in V1_DOMAINS}, selection_rule=sel['rule'],
                 omitted_scrmed=sel['summary'].get('omitted_scrmed', [])),
        rrr=dict(ridge_grid=[1e-4, 1e-3, 1e-2, 1e-1], inner_split_seed=BOOT_SEED, inner_fit=80, inner_val=16, primary_rank=16, template=0),
        fits=fits, s2=dict(grids=GRID, scrmax_grid_domains=['weekday', 'month'], modes=MODES),
        training=dict(groups=['C1', 'C3'], seeds=SEEDS_E, updates=600, batch=8, microbatch=2, lr=1e-3, optimizer='AdamW', weight_decay=0, clip=1.0,
                      l2_weight=1.0, l2_scale='per domain and op: mean train canonical write token MSE', rank=16),
        chains=ch, methods=methods, lanes=dict(A=['weekday', 'month', 'daysago'], B=['compass', 'egoside', 'pron3', 'name3', 'bind3']),
        success='sym2_evaluator.score(...)["success"]', statistical_unit='world', proportion_ci='Wilson 95%', bootstrap=dict(reps=BOOT_N, seed=BOOT_SEED),
        definitions=dict(one_way_R2N='R at step 2N of plus_from_start (cyclic); R_7 of plus_from_path_start (daysago)',
                         R10N='R at step 10N of plus_from_start (cyclic)', R6_s1b='R at step 6 of plus_from_start (S1b)',
                         kappa_u='appendix A, |lambda| >= 0.9, plus operator A_Q', G='max_{k<=10N} ||A_Q^k||_2',
                         single='success over all legal single transitions (template 0) x 160 worlds',
                         probe='torch multinomial logistic regression, standardized slot vectors, C in {0.01,0.1,1,10} by 5-fold world CV (accuracy); see DEVIATIONS #1',
                         writes='W(x) = M * (T(E(x)) - E(x)), plus operator, token level'),
        predictions=dict(
            G2_0=dict(rule='natural RRR-16 one-way R_2N >= 0.95 in all five v1 domains AND C1 R_2 <= 0.20 for every domain x seed; otherwise stop'),
            A1=dict(quantity='egoside scrmax RRR-16 one-way R_2N', H_symN='<= 0.50', H_slot='>= 0.95'),
            A2=dict(quantity='RRR-16 one-way R_2N for every scrmax/scrmed map', H_slot='all >= 0.95',
                    H_symN='Spearman rho(E_iso, R_2N) over all maps incl. natural <= -0.5 AND min R_2N < 0.95'),
            A3=dict(quantity='R_10N(natural) - R_10N(scrmax), RRR-16, four cyclic domains', H_slot='all <= 0.05', H_symN='>= 0.20 in at least 2 of 4'),
            Q1=dict(rule='H-slot if A1, A2, A3 all H-slot; H-sym-N if A1 H-sym-N and at least one other domain scrmax RRR-16 R_2N <= 0.50; else partial'),
            A4=dict(quantity='max phase deviation of |lambda|>=0.9 eigenvalues, RRR-16 plus, natural and scrmax, cyclic domains', expected='< 2 deg (both hypotheses)'),
            A5=dict(quantity='kappa_u(scrmax)/kappa_u(natural), RRR-16 plus, cyclic domains', expected='> 1 (both hypotheses)'),
            B1=dict(quantity='pron3 and name3 RRR-16 one-way R_6', expected='>= 0.95 (both hypotheses)'),
            B2=dict(quantity='bind3 RRR-16 one-way R_6', H_bind='<= 0.50', H_geom='>= 0.95'),
            B3=dict(quantity='C1 R_2 for pron3, name3, bind3, every seed', expected='<= 0.20 (both hypotheses)'),
            B4=dict(quantity='slot-predictability dev R2(bind3) - min(pron3, name3)', H_bind='<= -0.30', H_geom='|.| < 0.10',
                    note='measured before the lock on train+dev (as the plan specifies); value recorded below; not prospective',
                    pre_lock_value=read(ROOT / 'results/s1b_geometry.json')['B4_pre_lock']),
            Q2=dict(rule='H-bind if B2 meets H-bind; H-geom if B2 meets H-geom; else neither'),
            R1=dict(rule='for each natural cyclic domain (weekday N=7, month 12, compass 4, egoside 4): r* = smallest grid rank with one-way R_2N >= 0.95 at it and all '
                         'larger grid ranks; pass if N-2 <= r* <= N and the largest grid rank below r* (if any) has R_2N <= 0.20; R1 passes if all four pass'),
            R2=dict(rule='natural single-step success >= 0.95 at month rank 8 and weekday rank 4'),
            R3=dict(rule='single(natural) - single(scrmax) >= 0.20 at r = N-2 for weekday (5) and month (10); r*(scrmax) also reported'),
            R4=dict(rule='exploratory: harmonics present in the unit block at each rank'),
            R5=dict(rule='exploratory: first-failure transitions for daysago low ranks (boundary entry?)'),
            M1=dict(quantity='mean pairwise cosine of C1 writes across source states (world mean)', H_instr='>= 0.90', H_approx='<= 0.60'),
            M2=dict(quantity='cosine(C1 write, canonical write), per-world mean over sources, median over worlds', H_instr='|.| <= 0.20', H_approx='>= 0.50'),
            M3=dict(quantity='probe readout on C1 first-step slot', H_instr='source >= 0.80 and target <= 0.20', H_approx='target >= 0.80',
                    admissible_if='probe dev accuracy on canonical encodings >= 0.99'),
            M4=dict(quantity='same-world write transplant success', H_instr='>= 0.80', H_approx='<= 0.20'),
            M_aggregation='each M statistic is computed per (domain, C1 seed) cell (15 cells); the hypothesis test uses the median over cells; all cells reported',
            Q4=dict(rule='the hypothesis met by the majority of M1-M4 (ties -> mixed)'),
            M5_M7='exploratory'),
        stop_rules=['G2-0 fail -> stop and debug the pipeline', '8 GPU h -> report; 10 GPU h -> stop', 'same job fails twice for unknown reason -> stop', 'leakage -> stop'],
        sources={k: sha(ROOT / k) for k in LOCKED_SOURCES},
        data={str((ROOT / k).relative_to(REPO)): sha(ROOT / k) for k in data_files})
    dump('protocol.json', p)
    print('locked', sha(ROOT / 'protocol.json'), flush=True)


if __name__ == '__main__':
    main()
