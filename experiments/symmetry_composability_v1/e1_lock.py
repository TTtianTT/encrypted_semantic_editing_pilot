"""E1.3 lock protocol and predictions BEFORE any confirm decoding. Requires G1a pass and the E1.1 result (or skip record)."""
import time
from symutil import *
import sym_semantics as S

SEEDS_E = [42, 43, 44]
RANKS = [4, 8, 16, 32, 64, 128]


def chains():
    out = {}
    for d in S.DOMAINS:
        if d == 'daysago':
            out[d] = dict(plus_from_two=dict(start=2, ops=['plus'] * 7), minus_from_nine=dict(start=9, ops=['minus'] * 7),
                          alternating_from_five=dict(start=5, ops=['plus', 'minus'] * 5))
        else:
            N = len(S.states(d))
            out[d] = dict(plus_from_start=dict(start='world_start', ops=['plus'] * (2 * N)), minus_from_start=dict(start='world_start', ops=['minus'] * (2 * N)),
                          alternating_from_0=dict(start=0, ops=['plus', 'minus'] * N))
    return out


def main():
    require_slurm(); t0 = time.time()
    assert not (ROOT / 'protocol.json').exists(), 'protocol already locked; never rewrite'
    geo = read(ROOT / 'results/e1_geometry.json'); assert geo['G1a']['decision'] == 'pass', 'G1a failed: no editing evaluation'
    corpus = ROOT / 'results/e1_corpus.json'; assert corpus.exists()
    assert not list((ROOT / 'local').glob('e1_*_confirm_*')), 'confirm encodings must not exist before the lock'
    assert not (ROOT / 'results/shards').exists(), 'no confirm decoding before the lock'
    methods = [f'RRR{r}' for r in RANKS] + [f'{g}_s{s}' for g in ('C1', 'C3') for s in SEEDS_E] + ['reencode']
    data = {f'data/{d}/worlds.jsonl': None for d in S.DOMAINS}; data.update({'data/manifest.json': None, 'data/audit.json': None,
                                                                           'results/e1_geometry.json': None, 'results/e1_corpus.json': None,
                                                                           'AMENDMENT_01.md': None, 'results/g0_amended_decision.json': None})
    p = dict(
        locked=True, created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), version=1, amendment='AMENDMENT_01.md',
        domains=S.DOMAINS, groups=S.GROUP, states={d: S.states(d) for d in S.DOMAINS}, words={d: [S.word(d, s) for s in S.states(d)] for d in S.DOMAINS},
        templates=dict(fit_train=[0], evaluation=[0], geometry_primary=0, geometry_secondary=3, structural_ood=3),
        splits=dict(train=96, dev=32, confirm=160, seed=read(ROOT / 'data/manifest.json')['seed'], rule='random.Random(seed + domain index)'),
        statistical_unit='world', bootstrap=dict(reps=BOOT_N, seed=BOOT_SEED), proportion_ci='Wilson 95%',
        success='sym_evaluator.score(...)["success"]: ended, full-grammar consumption, target attribute, all non-target facts preserved',
        metrics=dict(E_iso='affine-isometry equivariance error (PLAN appendix), world mean, plus map; null = shared label permutation, all perms if <=7 states else 1000 (seed 3101)',
                     R2_G='group-averaged R^2 of mean squared-distance matrix (cyclic distance for Z_N, |i-j| for open)', SEP='PLAN appendix', Delta_opp='4-state domains',
                     R_k='fraction of 160 confirm worlds whose first k chain steps all succeed', S6='R_6^(1/6)',
                     kappa_N='per world sqrt(sum_x ||M(T+^N E_x - E_x)||^2 / sum_x ||M(T+ E_x - E_x)||^2), median over worlds',
                     e_inv='per world sqrt(sum_x ||M(T_inv T_first E_x - E_x)||^2 / sum_x ||M(E_gx - E_x)||^2)'),
        rrr=dict(ranks=RANKS, primary_rank=16, ridge_grid=[1e-4, 1e-3, 1e-2, 1e-1], inner_split_seed=BOOT_SEED, inner_fit=80, inner_val=16,
                 selection='per rank, relative ridge minimizing inner-validation token MSE; refit on all 96 train worlds; fit.py solve()'),
        training=dict(groups=['C1', 'C3'], seeds=SEEDS_E, updates=600, batch=8, microbatch=2, lr=1e-3, optimizer='AdamW', weight_decay=0, clip=1.0,
                      l2_weight=1.0, l2_scale='per domain and op: mean train canonical write token MSE', rank=16, checkpoint_used=600,
                      sampling='op alternates plus/minus by update parity; transitions sampled uniformly with random.Random(seed)'),
        methods=methods, algebra_methods=['RRR16'] + [f'{g}_s{s}' for g in ('C1', 'C3') for s in SEEDS_E],
        chains=dict(by_domain=chains(), world_start='per-world start_state field in data/{domain}/worlds.jsonl'),
        admission=dict(threshold=0.90, measure='dev single-step success over all legal transitions x 32 dev worlds',
                       applies={'P1': 'RRR16 weekday, month', 'P2': 'RRR16 weekday, month', 'P3b': 'RRR16 compass, egoside', 'P4': 'RRR16 daysago',
                                'P5': 'C3 (each seed) weekday, month', 'P6': 'RRR16 weekday, month'},
                       rule='if not admitted, the prediction is reported as not decidable; dev never selects rank or checkpoint'),
        predictions=dict(
            P1=dict(text='RRR-16 one-way plus chain from world start: R_N >= 0.80 for weekday (N=7) and month (N=12)', threshold=0.80),
            P2=dict(text='RRR-16 same chain: R_2N >= 0.70 for weekday and month', threshold=0.70),
            P3a=dict(text='E_iso(compass) < E_iso(egoside) on confirm template-0 canonical states; bootstrap CI of difference (independent world resampling) excludes 0 (upper < 0)'),
            P3b=dict(text='RRR-16 one-way plus R_8(compass) - R_8(egoside) >= 0.20 and one-sided two-proportion z test p < 0.05', min_difference=0.20, alpha=0.05),
            P4=dict(text='daysago RRR-16: plus from two R_7 >= 0.70 and alternating from five R_10 >= 0.70', threshold=0.70),
            P5=dict(text='every seed: C1 one-way plus R_2 <= 0.20 in all five domains; C3 R_N >= 0.70 for weekday and month', C1_R2_max=0.20, C3_RN_min=0.70),
            P6=dict(text='RRR-16 median kappa_N < 0.5 for weekday and month', threshold=0.5),
            P7=dict(text='Spearman rho between confirm E_iso and RRR-16 S6 across the five domains; report only (n = 5)')),
        thresholds_rule='point estimate compared with threshold; Wilson CI reported alongside',
        stop_rules=['G1a fail -> no editing evaluation', 'budget 8 GPU h -> report remaining plan; 10 GPU h -> stop', 'same job fails twice for unknown reason -> stop',
                    'any leakage -> stop'],
        lanes=dict(A=['weekday', 'month', 'daysago'], B=['compass', 'egoside']),
        g1a=geo['G1a'],
        sources={k: sha(ROOT / k) for k in LOCKED_SOURCES},
        data={k: sha(ROOT / k) for k in data},
        inputs_manifest_sha256=sha(ROOT / 'inputs_manifest.json'))
    dump('protocol.json', p)
    print('locked', sha(ROOT / 'protocol.json'), flush=True)


if __name__ == '__main__':
    main()
