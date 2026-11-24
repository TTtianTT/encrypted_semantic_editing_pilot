"""Lock (CPU; PLAN v7 B10). Writes protocol.json: the B-line predictions (verbatim), the operational rules, the U thresholds, the R case
list hash, the per-world latent predictions (simulate files, SHA256), the seed registry, gates, admissions, pre-checks and the demotions they
imply (design rule 1), data and source hashes. Asserts: no confirm7 decoded output exists; every v7 editor's data-order hash is new
(seed_registry.json); smoke products only under local/smoke; self-test, audit, P4 and both smoke tests passed."""
import time
from lib7 import *

PREDICTIONS = {
    'G7_0': 'confirm7 上的基算子单向 R_2N ≥ 0.95，范围包括：BART weekday/month 的 RRR-16、T5Gemma month 的 RRR-16，以及四个多句式组合的 S-RRR-16。name3 上 Tok-U 的 R_6 ≥ 0.95。不通过即停止排查。',
    'R0': '全部案例。正对照：R-A 的 SNAP ≥ 0.90；R-B 的 SNAP+CTX ≥ 0.95。不满足则该族不可解释，只报告数字。',
    'R1': '（主）R-A（T5Gemma）。H-offhull：PROJ ≥ 0.70 且 PUSH ≤ 0.40；H-inspan：PUSH ≥ 0.70 且 PROJ ≤ 0.40；两者都 ≥ 0.70 为"任一即可"；两者都 ≤ 0.40 为"都不是"。',
    'R2': '（主）R-B。H-inspan：PUSH ≥ 0.70，且 PROJ、CTX ≤ 0.40；H-context：CTX ≥ 0.70 且 PUSH ≤ 0.40；H-offhull：PROJ ≥ 0.70 且 PUSH ≤ 0.40；其他为混合，报告全部修复率。',
    'R3': '（主）对照步。PROJ、PUSH、CTX 修复后仍成功的比例都 ≥ 0.97（修复本身不破坏正常输入）。',
    'R4': '（主）复现案例。判定与 R1、R2 相同才算"确认"；不同则报告为"不稳定"。',
    'U1': '（主）F1。逐 world 一致率的提升（U − 只看槽位）CI 下界 > 0，且 U 的类别准确率 ≥ 0.85。',
    'U2': '（主）F2。同上。',
    'U3': '（主）NI。一致率下降 ≤ 0.01，且差值 CI 下界 > −0.02。',
    'U4': '（次）各族。U 预测失败的精确率 ≥ 0.90；F3 的提升；次版本阈值在 F2 上的结果。',
    'Q21': 'H-fix：U1、U2、U3 都成立。部分：U3 成立，且 U1、U2 只成立一个；报告是哪一族。H-nofix：其他情形。',
    'A1': '（主，只看潜变量）F∅ 链上的离流形程度 ρ。H-cycle：交替与单向 plus 在 t = 2N 时 ρ 中位数之比 ≥ 2；单向 plus 在 t = N 与 t = 1 时之比 ≤ 1.5。4 个组合中至少 3 个成立。',
    'A2': '（主，干净输入上的一阶误差，附录 A.7）一圈和比；交替对比。H-cycle：一圈和比的中位数 ≤ 0.25，且交替对比的中位数 ≥ 0.50。至少 3/4。',
    'A3': '（主）用 P⁻¹ 作 minus 算子时，单向 minus 的 R_2N。每个组合 ≥ 0.95。',
    'A3b': '（次）(P, P⁻¹) 交替的 R_2N。≥ 0.95。这几乎由构造决定，只作对照。',
    'Q22': 'H-cycle：A1、A2、A3 都成立。只有 A3 成立：写成"互逆配对有效，但累积机制未确认"。其他情形：按成立的部分报告。',
    'K5': '（主）Att2L-U8 的单向 R_100。H-closed：中位数 ≥ 0.90，且 ≥ 4/5 个 seed 不低于 0.80；H-slow-decay：中位数 ≤ 0.50。',
    'K6': '（主）三种编辑器的 R_30。支持方：Att2L-U8 中 ≥ 0.90 的 seed 至少 4/5，且 Att2L-U4 与 Att1-U8 的中位数都 ≤ 0.50；对立方：Att2L-U8 的中位数 ≤ 0.50。',
    'K7': '（主）OR-U8 的 R_30。H-representable：中位数 ≥ 0.90；H-unrepresentable：中位数 ≤ 0.50。',
    'K8': '（主）Att2L-U8（8 个 seed）删掉第 2 层注意力项后的 R_30（附录 A.8 的 c）。H-layer2-needed：中位数 ≤ 0.50；H-layer2-redundant：中位数 ≥ 0.90。',
    'K9': '（次）name3、bind3fix 上 Att2L-U8 的 R_30。不低于 0.95 的 seed ≥ 6/8。',
}
OPERATIONAL = {
    'general': 'Paths start at the world start; 2N steps (plus, minus, alternating plus/minus). R_k = fraction of worlds whose decoded output is a success at every '
               'step 1..k (template 0 / 3: v1-v6 scorer; multi-template: exact match after whitespace normalisation). Categories: composable >= 0.90, fail <= 0.20, '
               'else partial. CIs: world cluster bootstrap, 2000 reps, seed 3101 (paired for differences); world = (domain, world_id). Identical cells (same '
               'continuous latent trajectories: m and rho of the locked simulation) are detected before any CI and only the first of each group is counted '
               '(design rule 10). Primary predictions decide; secondary ones are reported separately (rule 6).',
    'U_rule': 'Predictors on the locked simulation (results/simulate_<bb>.json.gz): slot-only = readout equals gold at every step; U = readout equals gold, '
              'm >= tau_m and rho <= tau_r at every step, thresholds of results/calib_u_<bb>.json (primary for U1-U3; secondary reported in U4). Per family, pooled '
              'per-world agreement (prediction vs observed chain success at 2N) over the (world, cell) records; category accuracy over cells (predicted rate vs '
              'observed R_2N). F1 = BART template-0 new C3 seeds 45-47 (all snapshots, all paths); F2 = T5Gemma month-mt held-out-template surgeries; '
              'NI = BART template-0 v6 CT2 set and T5Gemma month template-0 set (cells7.py). U1 (F1) and U2 (F2) hold iff the paired CI of (U - slot) agreement '
              'has lower bound > 0 and U category accuracy >= 0.85. U3 holds iff on the NI set of each backbone (U - slot) >= -0.01 and its CI lower bound > -0.02. '
              'U4 (secondary): precision of a U-predicted failure per family (>= 0.90); the (U - slot) gain on F3; the secondary thresholds on F2. '
              'Q21: H-fix iff U1, U2, U3; partial iff U3 and exactly one of U1, U2; else H-nofix. If the B7 pre-check fails, U1 and U2 are exploratory and Q21 '
              'is reported descriptively.',
    'R_rule': 'Cases: data/r_cases.json (P3, frozen; v6 confirm6) and R4 replication cases drawn after the lock from this experiment\'s U chains by the same rules '
              '(r_repair.r4_cases). Each repair is applied once at the case step and decoded once; success = exact match with the gold state of that step. '
              'Rates pooled over the group\'s cases; R1 on R-A-t5 (69 cases); R2 on R-B pooled over the families that pass R0 (per family reported); R3 on all '
              'control steps (PROJ, PUSH on every control; CTX where applicable). R4: R4-A-t5 with the R1 rule, R4-B with the R2 rule; confirmed iff the verdict '
              'equals R1 resp. R2, else unstable. A repair whose pre-check median change ||h\' - h|| / R_w < 0.02 in a group is a no-op there; predictions resting '
              'on it become exploratory. CIs: world cluster bootstrap.',
    'A_rule': 'Four combinations: BART weekday-mt, month-mt, hour-mt, T5Gemma month-mt (confirm7, held-out templates); P = v6 GM S-RRR-16. A1 from the locked '
              'simulation (F_empty chains): per combination ratio median rho(alt, t = 2N) / median rho(plus, t = 2N) >= 2 and median rho(plus, t = N) / median '
              'rho(plus, t = 1) <= 1.5; holds iff >= 3 of the combinations that passed the pre-check (dev7-ho alt median rho at 2N >= 0.02) hold, and at least 3 '
              'passed (else A1 exploratory). A2 (a_cycle.py on confirm7 clean inputs): per combination median cycle-sum ratio <= 0.25 and median alternating '
              'contrast >= 0.50; holds iff >= 3/4. A3: one-way minus with P^-1 R_2N >= 0.95 on every combination whose inverse passed the A.6 pre-check '
              '(cond < 1e3, round trip < 1e-5). A3b (secondary): (P, P^-1) alternating R_2N >= 0.95. A1 and A2 are computed only after the lock.',
    'K_rule': 'bind3; decisions use the new seeds 45-49 (5 seeds; OR-U8: 42-44); all 8 seeds reported; a seed that could not learn counts as R = 0. K5: H-closed iff '
              'median R_100 >= 0.90 and >= 4/5 seeds >= 0.80; H-slow-decay iff median <= 0.50; else mixed. K6: holds iff >= 4/5 Att2L-U8 seeds have R_30 >= 0.90 '
              'and the medians of Att2L-U4 and Att1-U8 are <= 0.50; opposing iff the Att2L-U8 median <= 0.50; else mixed. K7: OR-U8 median R_30 >= 0.90 '
              'H-representable, <= 0.50 H-unrepresentable, else mixed. K8 (8 seeds, ablation c): median R_30 <= 0.50 H-layer2-needed, >= 0.90 '
              'H-layer2-redundant, else mixed; exploratory if the pre-check shows it decided by construction. K9 (secondary): name3 and bind3fix Att2L-U8 R_30 '
              '>= 0.95 in >= 6/8 seeds.',
    'oracle': 'OR-U8 (oracle routing) is a diagnostic, never a usable editor; it differs from v6 OR-U4 only in the unroll set S <= 8 and the number of updates '
              '(design rule 4).',
    'paper': 'PLAN v7 B12 maps every outcome (including mixed and neither) to the paper text.',
}
LOCKED7 = ['symutil.py', 'sym5_semantics.py', 'sym5_evaluator.py', 'lib7.py', 'lcore.py', 'cells7.py', 'g70.py', 'u_chains.py', 'r_repair.py', 'a_cycle.py',
           'k_chains.py', 'devchains.py', 'calib_u.py', 'analyze.py', 'job_gpu.slurm', 'job_cpu.slurm']


def sections():
    out = dict(audit=read(ROOT / 'data/audit.json'), selftest=read(ROOT / 'results/selftest.json'), manifest=read(ROOT / 'data/manifest.json'),
               seed_registry=read(ROOT / 'seed_registry.json'), prep_fits=read(ROOT / 'results/prep_fits.json'),
               train_new={p: read(ROOT / f'results/train_new_bart_{p}.json') for p in ('C', 'K')},
               calib_u={bb: read(ROOT / f'results/calib_u_{bb}.json') for bb in ('bart', 't5')},
               devchains={bb: read(ROOT / f'results/devchains_{bb}_summary.json') for bb in ('bart', 't5')},
               r_precheck={bb: read(ROOT / f'results/r_precheck_{bb}.json')['summary'] for bb in ('bart', 't5')},
               a_precheck={bb: read(ROOT / f'results/a_precheck_{bb}.json')['cells'] for bb in ('bart', 't5')},
               k_precheck=read(ROOT / 'results/k_precheck.json'), p4={bb: read(ROOT / f'results/patch/p4_{bb}.json')['pass'] for bb in ('bart', 't5')},
               simulate={bb: read(ROOT / f'results/simulate_{bb}_summary.json') for bb in ('bart', 't5')}, r_cases_sha256=sha(ROOT / 'data/r_cases.json'),
               theory_T1=read(ROOT / 'results/theory/t_theory.json')['T1_holds'])
    out['u_thresholds'] = {bb: dict(primary=v['primary'], secondary=v['secondary']) for bb, v in out['calib_u'].items()}
    gain = [out['calib_u'][bb]['precheck'] for bb in ('bart', 't5')]
    num = sum(g['U'] * g['cells'] for g in gain if g['cells']); den = sum(g['slot_only'] * g['cells'] for g in gain if g['cells']); n = sum(g['cells'] for g in gain)
    out['precheck_U'] = dict(pooled_gain=(num - den) / n if n else None, per_backbone=gain, U1_U2_confirmatory=bool(n) and (num - den) / n >= .02)
    rho = {f'{bb}/{d}': v for bb in ('bart', 't5') for d, v in out['devchains'][bb]['A_precheck_rho_alt_2N_dev7ho'].items()}
    out['precheck_A'] = dict(rho_alt_2N_dev7ho=rho, A1_combos=[k for k, v in rho.items() if v >= .02], A1_confirmatory=sum(v >= .02 for v in rho.values()) >= 3,
                             A3_combos=[k for bb in ('bart', 't5') for k, v in out['a_precheck'][bb].items() if v['precheck_pass']])
    out['precheck_R'] = {g: v for bb in ('bart', 't5') for g, v in read(ROOT / f'results/r_precheck_{bb}.json')['precheck'].items()}
    out['precheck_K'] = dict(K8_decided_by_construction=out['k_precheck']['K8_precheck']['decided_by_construction'], K8_confirmatory=not out['k_precheck']['K8_precheck']['decided_by_construction'])
    out['R0_dev_snap'] = {bb: out['devchains'][bb]['snap_all'] for bb in ('bart', 't5')}
    return out


def main():
    require_slurm(); t0 = time.time()
    sh = ROOT / 'results/shards'; assert not sh.exists() or not any(sh.glob('chain_*')), 'confirm7 decoded output exists before the lock'
    for p in ('g70_*.json', 'u_*_complete.json', 'r_run_*.json', 'r_r4_*.json', 'a_run_*.json', 'k_run.json'): assert not list((ROOT / 'results').glob(p)), p
    assert not list(ROOT.glob('results/**/smoke*/**/chain_*')), 'smoke products outside local/smoke'
    sec = sections(); assert sec['selftest']['pass'] and sec['audit']['pass'] and all(sec['p4'].values())
    assert sec['seed_registry']['pass_'] and not sec['seed_registry']['clashes'], 'a v7 editor repeats a historical data order'
    for bb in ('bart', 't5'): assert read(ROOT / f'results/smoke_{bb}.json')['pass'], f'smoke {bb} failed'
    data = {}
    for f in sorted((ROOT / 'data').rglob('*')):
        if f.is_file(): data[str(f.relative_to(REPO))] = sha(f)
    for bb in ('bart', 't5'):
        for f in (ROOT / f'results/simulate_{bb}.json.gz', ROOT / f'results/simulate_{bb}_summary.json', ROOT / f'results/devchains_{bb}.json.gz'): data[str(f.relative_to(REPO))] = sha(f)
    data[str((ROOT / 'seed_registry.json').relative_to(REPO))] = sha(ROOT / 'seed_registry.json')
    p = dict(experiment='composability_mechanisms_v6', plan='PLAN.md', plan_sha256=sha(ROOT / 'PLAN.md'), predictions=PREDICTIONS, operational=OPERATIONAL,
             **sec, sources={f: sha(ROOT / f) for f in LOCKED7}, data=data, locked=True, locked_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    dump('protocol.json', p); print('locked; protocol sha256', sha(ROOT / 'protocol.json'), json.dumps({k: sec[k] for k in ('precheck_U', 'precheck_A', 'precheck_K')}, default=str), flush=True)


if __name__ == '__main__':
    main()
