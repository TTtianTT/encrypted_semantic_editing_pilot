"""Lock (CPU; PLAN B8). Writes protocol.json: the B-line predictions, thresholds and decision rules (verbatim + operational), the
per-world latent predictions (simulate files, SHA256), GM base selection, admissions, the not-converged list, gate results and removed
combinations, the M3 pre-check, data and source hashes. Asserts: no confirm6 decoded output exists (results/shards has no chain file,
no post-lock completion file); smoke products only under local/smoke; self-test, audit and both smoke tests passed."""
import time
from lib6 import *

PREDICTIONS = {
    'G6_0': 'M 的每个保留域：基算子在训练句式的 dev 上复核单向 R_2N ≥ 0.95；C：基算子 RRR-16 在 confirm6 上单向 R_2N ≥ 0.95；K：name3 上 Tok-U 的 R_6 ≥ 0.95。不通过即停止排查。',
    'M1': '基算子的单向 plus R_2N，每个（骨干，域）。H-general：≥ 0.90；H-template：≤ 0.50。',
    'M2': 'C1：R_1、R_2、D（seed 中位数）。H-general：R_1 ≥ 0.90、R_2 ≤ 0.20、D ≥ 0.8；H-template：R_1 ≤ 0.50。',
    'M3': 'F{1}：单向 plus R_2N ≤ 0.20，交替 R_2N ≥ 0.80，且 A(1) − A(⌊N/2⌋) ≥ 0.50。H-general：全部可评格子成立。',
    'M4': '状态监督类（基算子、手术、槽位 C3-U4）的潜空间预测。H-general：逐 world 一致率 ≥ 0.85，且相对朴素判断的提升 CI 下界 > 0；类别准确率 ≥ 0.80。H-template：一致率 < 0.75。',
    'M5': 'D 探测：CE 格子 D ≥ 0.5 且 R_2N ≤ 0.20；状态监督格子 D ≤ 0.20。H-general：≥ 90% 的格子成立。',
    'Q18prime': 'M1、M3、M4 都成立为 H-general；M1 在至少 2/3 个 BART 域上符合 H-template，则为 H-template；其他为混合。若预检后 M3 没有可评格子，按 M1 与 M4 判定，并在报告中注明。',
    'CT1': '未收敛 C3 系格子：槽位+上下文预测器的类别准确率，以及逐 world 一致率相对只看槽位的提升。H-context：类别 ≥ 0.80，且提升的 CI 下界 > 0；H-slot：提升的 CI 含 0。',
    'CT2': '非劣检验集：槽位+上下文 − 只看槽位的逐 world 一致率。H-context：下降 ≤ 0.01，且 CI 下界 > −0.02。',
    'Q19': 'CT1 与 CT2 都成立为 H-context。',
    'K1': 'OR-U4 的单向 R_30（bind3，seed 中位数）。H-representable：≥ 0.90；H-unrepresentable：≤ 0.50。',
    'K2': 'max(Att2L-U4, Att2L-U8) 的单向 R_30。H-closure：≥ 0.90；H-horizon：Att2L-U4 的 R_8 ≤ 0.50，且 Att2L-U8 的 R_12 ≤ 0.50。',
    'K3': 'Att1-U8：R_8 与 R_12。H-horizon：R_8 ≥ 0.70 且 R_12 ≤ 0.50；H-closure：R_30 ≥ 0.90。',
    'K4': 'name3、bind3fix 上各编辑器的 R_30。≥ 0.95（稳定性）；对立 ≤ 0.50。',
}
OPERATIONAL = {
    'cells': 'M / C cell = (backbone, domain, operator or editor, path in {plus, minus, alt}); paths start at the world start; 2N steps. K: plus 30, '
             'minus 12, alt 12. Categories: composable >= 0.90, fail <= 0.20, otherwise partial (observed R_2N and predicted R-hat_2N alike). R_k = fraction of '
             'worlds whose decoded output is a success (multi-template: exact match after whitespace normalisation) at every step 1..k. All CIs: world cluster '
             'bootstrap, 2000 reps, seed 3101 (paired where a difference is taken).',
    'latent_prediction': 'v5 A.1 with the locked readout: per world, predicted chain success iff the argmax equals the gold state at every step t <= 2N; '
                         'cell R-hat_2N = fraction of worlds predicted successful. The predictions are the locked simulation files (results/simulate_<bb>.json.gz); '
                         'the argmaxes recorded during the post-lock chains are a consistency check only (must equal the locked simulation). Naive prediction: '
                         'decoded success at step 1.',
    'M_rule': 'Domains = gates.M_domains (GM). M1 per (backbone, domain): base (F_empty) plus R_2N; verdict H-general iff all >= 0.90, H-template iff >= 2/3 of '
              'the BART M domains <= 0.50, else neither. M2 per (backbone, domain): seed medians of C1 R_1, R_2 (plus) and D (plus path; A.2 of v5: among worlds '
              'whose step-1 decode is parsable, fraction whose step-1 latent readout differs from the decoded state); H-general iff every domain meets R_1 >= 0.90, '
              'R_2 <= 0.20, D >= 0.8; H-template iff every domain has R_1 <= 0.50; a seed that could not learn counts as R = 0 without D. M3 per (backbone, domain) '
              'that passed the locked pre-check: F{1} plus R_2N <= 0.20, alt R_2N >= 0.80 and A(1) - A(floor(N/2)) >= 0.50 (A from the plus chain, fraction of '
              'worlds correct at step t pooled by folded displacement); holds iff every evaluable cell holds; none evaluable -> not evaluable. M4 per backbone, '
              'pooled over its state-family M cells (base, every F_S, slot C3-U4): per-world agreement (predicted vs observed chain success) >= 0.85 with the '
              'latent - naive CI lower > 0, and category accuracy >= 0.80 -> holds; agreement < 0.75 -> H-template side; M4 holds iff it holds on every backbone. '
              'M5 over the M editor cells (C1: CE; slot C3-U4: state; one-way plus and minus): fraction of cells meeting their D rule >= 0.90. '
              'Q18prime: H-general iff M1 H-general, M3 holds (or not evaluable, noted) and M4 holds; H-template iff M1 H-template; else mixed. '
              'If GM removed every domain, Q18prime = not evaluable.',
    'C_rule': 'Sets fixed at the lock (cells6.c_registry + train_new_bart_C.json convergence): CT1 = v1 C3, v3 C3-l3 / C3-l10, v4 P2b (month), v1 C3 (weekday, '
              'data definition verified by the audit) and every new C3n<u> whose dev L2 > 1.2 x RRR-16 dev L2; CT2 = base surgery (F_empty, F{1}, F_not1, F{j}), '
              'RRR-r / FF-r (r = N-4..N-2), v3 C3-rrrinit, v4 P2a, P2c, C3-U4, v5 C3n1200 / C3n2400, and every new C3n<u> meeting the rule. Readouts: slot = locked '
              'vote model full lams; ctx = slot + context (appendix A.3, lam_ctx from calib_ctx). Per-world agreement pooled over (world, cell) records of the set. '
              'CT1 holds iff ctx category accuracy >= 0.80 and the paired CI of (ctx - slot) agreement has lower bound > 0; H-slot side iff that CI contains 0. CT2 '
              'holds iff (ctx - slot) agreement >= -0.01 and its CI lower bound > -0.02. Q19: H-context iff CT1 and CT2 hold; H-slot iff the CT1 CI contains 0; '
              'else mixed. lam_ctx = the exact ML estimate on the dev context-substitution probes (calib_ctx_bart.json; lib6.fit_lam_ctx: grid incl. 0, ties to the smallest); a boundary estimate lam_ctx = 0 makes the ctx readout identical to the slot readout, so CT1 is then decided by construction (reported as such).',
    'C_exploratory': 'Declared before the lock, not part of any verdict: context drift = min_y d_ctx(h_t, y) per world and step (locked simulation files, key ctx_drift). On the CT1 cells, among worlds whose slot readout predicts chain success, the AUC of the maximal drift over steps 1..2N for predicting observed chain failure (and the same on CT2); plus, per CT1 cell, the first step at which the slot readout and the decode disagree.',
    'K_rule': 'Seed medians over 42/43/44 of plus R_k on bind3 (a seed that could not learn counts as R = 0). K1: OR-U4 R_30 >= 0.90 H-representable, <= 0.50 '
              'H-unrepresentable, else mixed. K2: H-closure iff max(Att2L-U4, Att2L-U8) R_30 >= 0.90; H-horizon iff Att2L-U4 R_8 <= 0.50 and Att2L-U8 R_12 <= 0.50; '
              'else mixed. K3: H-horizon iff Att1-U8 R_8 >= 0.70 and R_12 <= 0.50; H-closure iff Att1-U8 R_30 >= 0.90; else mixed. K4: per new editor kind and '
              'domain in {name3, bind3fix} (OR-U4 only bind3fix) the seed-median R_30; stable iff all >= 0.95, unstable iff all <= 0.50, else mixed. Q17prime is '
              'reported as the (K1, K2, K3) triple with the reading of PLAN B7.',
    'oracle': 'OR-U4 (oracle routing) is a diagnostic, never a usable editor (PLAN B1 new rule 3).',
}


def sections():
    out = dict(audit=read(ROOT / 'data/audit.json'), selftest=read(ROOT / 'results/selftest.json'), manifest=read(ROOT / 'data/manifest.json'))
    out['gates'] = {bb: read(ROOT / f'results/gates_{bb}.json') for bb in ('bart', 't5')}
    out['calib_mt'] = {bb: read(ROOT / f'results/calib_mt_{bb}.json') for bb in ('bart', 't5')}
    out['calib_ctx'] = read(ROOT / 'results/calib_ctx_bart.json')
    out['train_new'] = {'bart': {p: read(ROOT / f'results/train_new_bart_{p}.json') for p in ('M', 'C', 'K')}, 't5': {'M': read(ROOT / 'results/train_new_t5_M.json')}}
    out['simulate'] = {bb: read(ROOT / f'results/simulate_{bb}_summary.json') for bb in ('bart', 't5')}
    out['M3_precheck'] = {k: v for bb in ('bart', 't5') for k, v in out['simulate'][bb]['M3_precheck'].items()}
    out['base_selection'] = {bb: {d: g['base'] for d, g in out['gates'][bb]['GM'].items()} for bb in ('bart', 't5')}
    out['not_converged'] = {k: v for k, v in out['train_new']['bart']['C']['convergence'].items() if isinstance(v, dict) and not v['converged']}
    out['vote_models'] = {bb: {d: {k: v.tolist() for k, v in vote_lams(bb, d).items()} for d in out['gates'][bb]['M_domains'] + (C_DOMAINS if bb == 'bart' else [])}
                          for bb in ('bart', 't5')}
    import cells6
    out['C_sets'] = cells6.c_registry()
    return out


def main():
    require_slurm(); t0 = time.time()
    sh = ROOT / 'results/shards'; assert not sh.exists() or not any(sh.glob('chain_*')), 'confirm6 decoded output exists before the lock'
    assert not any((ROOT / 'results').glob(p) for p in ('m_*_complete.json', 'c_*_complete.json', 'k_*_complete.json', 'g60_*.json')) or True
    for p in ('m_*_complete.json', 'c_*_complete.json', 'k_*_complete.json', 'g60_*.json'): assert not list((ROOT / 'results').glob(p)), p
    assert not list(ROOT.glob('results/**/smoke*/**/chain_*')), 'smoke products outside local/smoke'
    sec = sections(); assert sec['selftest']['pass'] and sec['audit']['pass']
    for bb in ('bart', 't5'): assert read(ROOT / f'results/smoke_{bb}.json')['pass'], f'smoke {bb} failed'
    data = {}
    for f in sorted((ROOT / 'data').rglob('*')):
        if f.is_file(): data[str(f.relative_to(REPO))] = sha(f)
    for bb in ('bart', 't5'):
        for f in (ROOT / f'results/simulate_{bb}.json.gz', ROOT / f'results/simulate_{bb}_summary.json'): data[str(f.relative_to(REPO))] = sha(f)
    srcs = {f: sha(ROOT / f) for f in LOCKED6}
    p = dict(experiment='composability_mechanisms_v5', plan='PLAN.md', plan_sha256=sha(ROOT / 'PLAN.md'), predictions=PREDICTIONS, operational=OPERATIONAL,
             **sec, sources=srcs, data=data, inputs_manifest_sha256=sha(ROOT / 'inputs_manifest.json'), locked=True, locked_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    dump('protocol.json', p); print('locked; protocol sha256', sha(ROOT / 'protocol.json'), 'seconds', time.time() - t0, flush=True)


if __name__ == '__main__':
    main()
