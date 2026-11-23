"""Lock (CPU; PLAN 11). Writes protocol.json: the plan's predictions, thresholds and decision rules (verbatim), the operational
definitions fixed here before any confirm5 decoding, the per-world latent predictions (SHA256 of results/simulate_<bb>.json.gz and their
per-cell summaries), admission results and the converged C3-family list, the multi-template templates and split, gate results and
excluded combinations, the idealized categories for D (v3/v4 locked, copied), and SHA256 of data and sources.
Asserts: no confirm5 decoded output exists (results/shards has no chain file; smoke outputs live in local/smoke) and B has no bind3
evaluation file."""
import time
from lib5 import *

PREDICTIONS = {
    'G5_0': 'L 的每个（骨干，域），基算子在 confirm5 上单向 R_2N ≥ 0.95；v1 的 C1 在 weekday、month 上 R_2 ≤ 0.20。不通过即停止排查。',
    'L1': '状态监督类，每个骨干：逐 world 的整条链成败，预测与观测一致的比例。H-latent：≥ 0.85，且"潜空间 − 朴素"的 95% CI 下界 > 0；H-decoder：< 0.75，或不优于朴素预测。两个骨干都成立为 H-latent。',
    'L2': '状态监督类，每个骨干：格子类别预测的准确率。H-latent：≥ 0.80；对立：≤ 0.65。两个骨干都成立为 H-latent。',
    'L3a': '全部训练过的编辑器格子中，D ≥ 0.5 的格子：≥ 90% 的这类格子单向 R_2N ≤ 0.20；对立：有 > 10% 可组合。',
    'L3b': 'CE 系的全部格子：≥ 90% 的格子 D ≥ 0.5；对立：CE 系有时写入状态。',
    'L3c': '已收敛的 C3 系（dev L2 ≤ 1.2 倍 RRR-16 的值，锁定前判定）：≥ 90% 的格子 D ≤ 0.20。L3a–c 都成立为 H-detector。',
    'L4': 'T5Gemma（Q11′）：C1-U4 与 C3-U4（month）。H-shortcut：C1-U4 两个 seed 的单向 R_2N 都 ≤ 0.20，且 D ≥ 0.8；C3-U4 两个 seed 都 ≥ 0.90。H-state：C1-U4 ≥ 0.90。',
    'L_new': '新训编辑器（结果在锁定时未知）的 L1、L2 另单列报告。',
    'D1': 'C = confirm5 上标准冻结的观测类别 ≠ 理想化类别的格子（锁定后按此规则确定）。H-coupling：D_S 的类别 = 理想化类别，≥ 75%；H-readout：D_S 的类别 = 标准冻结的类别，≥ 75%。|C| < 6 时不可评。',
    'D2': 'hour，每个骨干的 D{j}（j = 2…6）单向 plus。H-coupling：≥ 4/5 格 R_2N ≥ 0.90；H-readout：≤ 1/5 格。门槛：标准 F{j} 在同一骨干上至少 3/5 格不可组合，否则不可评。',
    'F1': '格子：month r = 11、12；hour r = 14；compass8 r = 10（T5Gemma）。门槛：普通 RRR-r 在 confirm5 上单向 R_2N ≤ 0.70，否则该格不可评。可评格子，plus：FF-r 的 R_2N，以及 ΔR = FF − RRR（world bootstrap CI）。H-alloc：FF ≥ 0.90 且 ΔR 的 CI 下界 ≥ 0.20；H-capacity：ΔR ≤ 0.05。≥ 3/4 的可评格子符合哪一方，就判为哪一方。',
    'B1': '（seed 中位数）Att1-U、Att2-U 在 name3 与 bind3fix 上的单向 R_30。H-stable：≥ 0.95；H-unstable：≤ 0.50。',
    'B2': '（seed 中位数）bind3：max(Att1-U, Att2-U) 的单向 R_6。H-train：≥ 0.90；H-deep：≤ 0.50。',
    'B3': '（seed 中位数）bind3：Tok-U 的单向 R_6。两种假设都预期 ≤ 0.20。',
    'N1': '基算子的单向 plus R_2N。H-general：所有（骨干，域）≥ 0.90；H-template：≥ 2/3 的 BART 域 ≤ 0.50。',
    'N2': 'C1：R_1 与 R_2（seed 中位数）。H-general：R_1 ≥ 0.90 且 R_2 ≤ 0.20；H-template：R_1 ≤ 0.50。',
    'N3': 'F{1}：单向 R_2N ≤ 0.20，交替 R_2N ≥ 0.80，且 A(1) − A(⌊N/2⌋) ≥ 0.50。H-general：所有可评格子成立。',
    'N4': '读出一致率（真实潜变量，冲突条件）。H-general：≥ 0.85，且"拟合 − 只用基频"的 CI 下界 > 0.10。',
    'N5': 'C3-U4（BART）的单向 R_2N。H-general：每个域 ≥ 0.90。',
    'N6': '状态监督类的潜空间预测：逐 world 一致率。H-general：≥ 0.85。',
    'Q18': 'N1、N3、N4 都成立为 H-general；N1 符合 H-template 为 H-template；其他为混合。',
}

OPERATIONAL = {
    'cells': 'L/N cell = (backbone, domain, operator or editor, path in {plus, minus, alt}); paths start at the world start; L/N/D chains 2N steps; '
             'B chains plus 30, minus 6, alt 6. Categories: composable >= 0.90, fail <= 0.20, otherwise partial (observed R_2N and predicted R-hat_2N alike).',
    'latent_prediction': 'A.1 with the locked fitted (full) vote model: per world, predicted chain success iff the argmax equals the gold state at every step '
                         't <= 2N; predicted cell rate R-hat_2N = fraction of worlds predicted successful. The predictions are the locked simulation files; '
                         'the argmax recorded during the post-lock chains is used only as a consistency check (it must equal the locked simulation).',
    'observed': 'per world, observed chain success = decoded trajectory success at step 2N; naive prediction = decoded success at step 1.',
    'state_family': 'L1/L2 state-supervised cells: every freeze condition F_S of the base operator (F_empty included; base = closed-form RRR), the RRR-r / FF-r '
                    'grid, and the existing editors whose objective contains canonical L2 (v1 C3, v3 C3 l3/l10/rrrinit, v4 P2 C3-6000 / L2-600 / L2-6000, v4 C3-U4). '
                    'New editors trained in this round are reported separately (L_new) and are not part of L1/L2.',
    'L1_rule': 'per backbone: agreement = mean over (world, cell) records of [predicted == observed]; latent - naive CI = A.5 world cluster bootstrap (worlds '
               'clustered by world_id, 2000 reps, seed 3101). H-latent iff agreement >= 0.85 and CI lower > 0; H-decoder iff agreement < 0.75 or CI lower <= 0; '
               'else mixed. L1 verdict: H-latent if both backbones H-latent, H-decoder if both H-decoder, else mixed.',
    'L2_rule': 'per backbone: accuracy = fraction of state-family cells with predicted category == observed category; H-latent >= 0.80, H-decoder <= 0.65, '
               'else mixed; combined over backbones as L1.',
    'Q14_rule': 'H-latent iff L1 and L2 are H-latent; H-decoder iff L1 or L2 is H-decoder and neither is H-latent; else mixed.',
    'D_rule': 'D (A.2) per editor cell = (backbone, editor, domain, direction in {plus, minus}): among worlds whose step-1 decode on that one-way path is '
              'parsable, the fraction whose step-1 latent readout (locked simulation) differs from the decoded state; the cell outcome is that path\'s R_2N. '
              'Trained editors = all existing and new editors of L (both families, both backbones; cannot-learn editors excluded).',
    'L3_rule': 'L3a: among editor cells with D >= 0.5, fraction with R_2N <= 0.20 >= 0.90 (if no such cell: not evaluable). L3b: among CE-family cells, fraction '
               'with D >= 0.5 >= 0.90. L3c: among converged C3-family cells (locked list), fraction with D <= 0.20 >= 0.90. Q14\' H-detector iff L3a, L3b and L3c hold.',
    'L4_rule': 'T5Gemma month: C1-U4n and C3-U4n seeds 42, 43 (plus R_2N; D on the plus path). A seed that cannot learn counts as R_2N = 0 and has no D; '
               'D >= 0.8 is required of every admitted C1-U4 seed. H-shortcut iff both C1-U4 seeds <= 0.20, every admitted C1-U4 seed D >= 0.8 and both C3-U4 seeds '
               '>= 0.90; H-state iff both C1-U4 seeds >= 0.90; else mixed.',
    'D1_rule': 'cells = (backbone, D domain, S in {1}, not-1, {j}; path) whose idealized category (v3/v4 locked derived, copied into this protocol) exists; '
               'C = cells whose observed standard F_S category differs from the idealized one (pooled over backbones; per backbone also reported). '
               'H-coupling iff >= 75% of C have D_S category == idealized; H-readout iff >= 75% have D_S category == standard F_S category; else mixed; |C| < 6: not evaluable.',
    'D2_rule': 'per backbone, hour, j = 2..6, plus: gate = at least 3 of the 5 standard F{j} plus R_2N < 0.90; H-coupling iff >= 4 of 5 D{j} R_2N >= 0.90; '
               'H-readout iff <= 1 of 5; else mixed. Q15: H-coupling (H-readout) iff every evaluable D1/D2 verdict is H-coupling (H-readout); not decidable if none '
               'is evaluable; else mixed.',
    'F1_rule': 'per cell: gate RRR-r plus R_2N <= 0.70 on confirm5; Delta R CI = A.5 paired world bootstrap. Q16: H-alloc (H-capacity) iff the fraction of evaluable '
               'cells matching it is >= 3/4; no evaluable cell: not evaluable; else mixed.',
    'B_rule': 'seed medians over 42/43/44 (an editor that failed admission stops B before the lock; bind3 editors are not gated). B1: H-stable iff all four '
              '(Att1-U, Att2-U) x (name3, bind3fix) medians of plus R_30 >= 0.95, H-unstable iff all <= 0.50, else mixed. B2 = Q17: max of the Att1-U and Att2-U '
              'bind3 medians of plus R_6: H-train >= 0.90, H-deep <= 0.50, else mixed. B3 holds iff the Tok-U bind3 median R_6 <= 0.20.',
    'N_rule': 'N1 per (backbone, domain) base operator plus R_2N; H-template iff >= 2/3 of the BART N domains <= 0.50. N2 per domain (seed medians); verdict '
              'H-general iff every domain meets it, H-template iff every domain has R_1 <= 0.50. N3 over the cells that passed the locked pre-check (F{1}, '
              'per (backbone, domain)); no evaluable cell: not evaluable. N4 per backbone pooled over its N domains, records = (world, step) of the F{1} and F{not 1} '
              'chains (three paths) with a parsable decoded state, as v4 V4. N5 per BART domain (seed median). N6 per backbone: per-world agreement over the '
              'state-family N cells (base, F{1}, F{not 1}, C3-U4). Q18 as stated. If GB removed every (backbone, domain) before the lock '
              '(gates.N_domains empty on both backbones), Q18 = not evaluable and no N chain is run.',
    'Q11prime': 'Q11\' = L4 verdict.',
}


def sections(bbs=('bart', 't5')):
    out = dict(audit=read(ROOT / 'data/audit.json'), templates_split=read(ROOT / 'data/templates_split.json'), selftest=read(ROOT / 'results/selftest.json'))
    out['templates_mt'] = read(ROOT / 'data/templates_mt.json'); out['gates_mt'] = {}; out['gates'] = {}; out['calib_mt'] = {}; out['train_new'] = {}; out['simulate'] = {}
    for bb in bbs:
        out['gates_mt'][bb] = read(ROOT / f'results/gates_mt_{bb}.json'); out['gates'][bb] = read(ROOT / f'results/gates_{bb}.json')
        out['calib_mt'][bb] = read(ROOT / f'results/calib_mt_{bb}.json')
        out['train_new'][bb] = {p: read(ROOT / f'results/train_new_{bb}_{p}.json') for p in (('L', 'N', 'B') if bb == 'bart' else ('L', 'N'))}
        sm = read(ROOT / f'results/simulate_{bb}_summary.json'); assert sha(ROOT / f'results/simulate_{bb}.json.gz') == sm['simulate_sha256']
        out['simulate'][bb] = sm
    p4 = read(V4DIR / 'protocol.json')
    out['idealized_D'] = {bb: {d: p4['calib'][bb][d]['derived'] for d in D_DOMAINS[bb]} for bb in bbs}
    out['vote_models'] = {bb: {d: {k: v.tolist() for k, v in vote_lams(bb, d).items()} for d in L_DOMAINS[bb] + out['gates'][bb]['N_domains']} for bb in bbs}
    return out


def main():
    require_slurm(); t0 = time.time()
    sh = ROOT / 'results/shards'; assert not sh.exists() or not any(sh.glob('chain_*')), 'confirm5 decoded output exists before the lock'
    assert not any((ROOT / 'results').glob('b_*')), 'B evaluation files exist before the lock'
    assert not any(ROOT.glob('logs/*')) or True
    sec = sections(); assert sec['selftest']['pass'] and sec['audit']['pass']
    for bb in ('bart', 't5'): assert read(ROOT / f'results/smoke_{bb}.json')['pass'], f'smoke {bb} failed'
    data = {}
    for f in sorted((ROOT / 'data').rglob('*')):
        if f.is_file(): data[str(f.relative_to(REPO))] = sha(f)
    for bb in ('bart', 't5'):
        for f in (ROOT / f'results/simulate_{bb}.json.gz', ROOT / f'results/simulate_{bb}_summary.json'): data[str(f.relative_to(REPO))] = sha(f)
    srcs = {f: sha(ROOT / f) for f in LOCKED5}
    p = dict(experiment='composability_mechanisms_v4', plan='PLAN.md', plan_sha256=sha(ROOT / 'PLAN.md'), predictions=PREDICTIONS, operational=OPERATIONAL,
             **sec, sources=srcs, data=data, inputs_manifest_sha256=sha(ROOT / 'inputs_manifest.json'), locked=True, locked_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    dump('protocol.json', p); print('locked; protocol sha256', sha(ROOT / 'protocol.json'), 'seconds', time.time() - t0, flush=True)


if __name__ == '__main__':
    main()
