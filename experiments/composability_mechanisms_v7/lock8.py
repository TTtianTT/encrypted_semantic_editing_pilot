"""v8 lock (CPU; PLAN v7 C5 = B10 extended to confirm8 and the new models' revisions). Writes protocol.json: the C-line predictions (verbatim),
the plan-change units E1 / E2 (verbatim readings), the operational rules, the pre-check decisions (design rule 1) and the demotions they imply,
U thresholds, gates, admissions, seed registry, model revisions, the pre-lock simulations (SHA256), data and source hashes.
Asserts: no confirm8 decoded output and no confirm7 decoded output of a v8 backbone exist; no post-lock result exists; self-test, audit,
seed registry and smoke tests passed."""
import time
from symutil import *

PREDICTIONS = {
    'N1': '（主）S-RRR_nat 的单向 plus R_2N（每个骨干）。H-natural：≥ 0.90；对立：≤ 0.50。',
    'N2': '（主）S-RRR_syn 零样本的单向 R_2N。H-transfer：≥ 0.80；H-no-transfer：≤ 0.30。dev 上已 ≥ 0.95 或 ≤ 0.05 时降为描述性。',
    'N3': '（主）C1_nat 的 R_1、R_2、D（seed 中位数）。R_1 ≥ 0.90、R_2 ≤ 0.20、D ≥ 0.80。',
    'N4': '（主）冻结特征（相对阈值）。F{1} 单向 ≤ 0.20；F{1} 交替 ≥ F∅ 交替 − 0.10；F¬1 ≤ 0.10。dev 上模型自己预测落在阈值另一侧的格子剔除。',
    'N5': '（主）潜空间预测（v7 选定的主预测器）。一致率 ≥ 0.85，相对朴素判断的提升 CI 下界 > 0，类别准确率 ≥ 0.80。',
    'Q24': 'H-natural：N1、N4、N5 都成立。H-template-bound：N1 不成立。混合：其他情形。N2、N3 单独报告。',
    'G1': 'C1 的 R_1、R_2、D：R_1 ≥ 0.90、R_2 ≤ 0.20、D ≥ 0.80。',
    'G2': '秩阈值：RRR-(r*_pred) 的单向 R_2N ≥ 0.95，RRR-(r*_pred − 2) 的单向 R_2N ≤ 0.50。',
    'G3': '冻结特征：同 N4。',
    'G4': '谱：每个域中，s_1 在全部平面里最小。',
    'G5': '潜空间预测与 D 探测：同 N5；D 在 ≥ 90% 的格子里正确区分 CE 与状态监督。',
    'G6': 'C3-U4 的 R_2N（seed 中位数）≥ 0.95。',
    'Q25': 'G1–G6 全部成立，记为"在 9B-9B 上复现"；不成立的项逐条报告，不合并成一个结论。',
    'ladder': '（探索性）T5Gemma B-B 与 L-L UL2-IT：只做闭式算子（秩阈值、冻结特征、谱与潜空间预测）；重建闸门不过的尺寸跳过；与 BART-base、2B-2B、9B-9B 合成一张表。',
    'D': '（探索性）Gemma 2 2B：继续的前提为重建 ≥ 0.99 且所选层上 S-RRR-16 的单步 ≥ 0.90（选层规则按 DEVIATIONS 7：并列层的中位数为主层，两端并列层只做闭式测量）；测量秩阈值、冻结特征、谱、潜空间读出与解码的一致率、CE 槽位编辑器的 R_1、R_2 与 D。',
    'E1': '（探索性）g_P、g_M < 1 且 g_{P⁻¹} > 1：支持"拟合出的算子在离流形方向上收缩，精确逆放大"；否则写为"未解释"。（已在锁定前完成，results/e1.json，只用 v7 已解码的 confirm7 编码与拟合，不解码。）',
    'E2': '（探索性）秩升高后衰减明显变慢、旧名字残留下降：支持写入保真度的解读；否则 §9 写为"未解释"。',
}
OPERATIONAL = {
    'general': 'Paths start at the world start; 2N steps (plus, minus, alternating plus/minus). R_k = fraction of worlds whose decoded output is a success at every '
               'step 1..k (template 0: v1-v7 scorer; month-nat: exact match with prefix + month + suffix after whitespace normalisation, output ended). '
               'Categories: composable >= 0.90, fail <= 0.20, else partial. CIs: world cluster bootstrap, 2000 reps, seed 3101 (paired for differences); world = '
               '(domain, world_id). Identical cells (same m and rho of the locked simulation) counted once (design rule 10). Unit N on confirm8 (month-nat, 240 '
               'worlds); unit G and the ladder on confirm7 = confirm6 (template 0; text reused, first evaluation for these models); D on confirm7 month.',
    'predictor': 'Primary predictor = slot readout (v7 Q21 = H-nofix): a chain is predicted correct iff the locked readout (vote model of the backbone and domain: '
                 'calib_nat_<bb>.json for month-nat, calib_g_<bb>.json for the v8 backbones) equals the gold state at every step of the locked simulation '
                 '(simulate8_<unit>_<bb>.json.gz). U with the dev-calibrated thresholds (dev8_<unit>_<bb>_summary.json) is reported alongside. Naive = step-1 '
                 'decoded success. Agreement pooled over (world, cell) records of all non-reference cells and paths (N: surgeries on S-RRR_nat, S-RRR_syn, C1_nat, '
                 'BART slot C3-U4_nat; G: rank grid, FF-r, surgeries, C1, C3-U4); category accuracy over cells (predicted rate vs observed R_2N). D = among worlds '
                 'with a parsable step-1 decode, the fraction whose step-1 readout differs from the decoded state (plus path).',
    'N_rule': 'Per backbone (bart, t5). N1 on nat_F_empty plus: holds >= 0.90, opposing <= 0.50, else mixed. N2 on syn_F_empty plus: H-transfer >= 0.80, '
              'H-no-transfer <= 0.30, else mixed; descriptive where the pre-check put dev R_2N >= 0.95 or <= 0.05. N3: medians over the admitted C1_nat seeds of '
              'R_1, R_2 (plus) and D: holds iff R_1 >= 0.90, R_2 <= 0.20, D >= 0.80. N4: the kept conditions (pre-check) on nat_F_{1} plus, nat_F_{1} alt vs '
              'nat_F_empty alt, nat_F_not1 plus; holds iff all kept hold; no kept condition -> not evaluable. N5 holds iff agreement >= 0.85, CI lower bound of '
              '(latent - naive) > 0 and category accuracy >= 0.80. Q24 per backbone: H-natural iff N1 holds, N4 holds and N5 holds; H-template-bound iff N1 does '
              'not hold (R_2N < 0.90); else mixed. Overall Q24: the common verdict if both backbones agree, else "mixed (per backbone)".',
    'G_rule': 'T5Gemma 9B-9B, weekday and month. G1 as N3 on C1 (seeds 50-52). G2 per domain: kept tests (pre-check) RRR-(r*_pred) plus R_2N >= 0.95 (r*_pred = 16 '
              '-> RRR-16) and RRR-(r*_pred - 2) plus R_2N <= 0.50. G3 as N4 per domain. G4 per domain: argmin over planes of s_k (mean one-step change of the '
              'confirm7 slot vectors inside plane k, planes from train) is the fundamental. G5: N5 rule pooled over both domains, and D separation over the editor '
              'cells (plus and minus paths): CE (C1) correct iff D >= 0.5, state-supervised (C3-U4) correct iff D <= 0.20; >= 90% correct. G6 per domain: median '
              'C3-U4 plus R_2N >= 0.95. Gk holds iff it holds in both domains. Q25: "replicated on 9B-9B" iff G1-G6 all hold, else the list of items that do not.',
    'admission': 'Editors: single-step dev single >= 0.90, unrolled dev plus R_4 >= 0.90; otherwise one retrain with twice the updates; otherwise "cannot learn" '
                 '(reported; excluded from cells, counted as failing in N3 / G1 / G6 medians with R = 0 and D = None).',
    'ladder': 'Exploratory: per size the observed r* (smallest RRR-r of the grid with plus R_2N >= 0.95), r*_pred, the G3 freeze rule, the G4 spectrum rule and the '
              'pooled predictor agreement; sizes whose reconstruction gate failed are skipped.',
    'oracle': 'OR-U8 and its E2 variants (oracle routing) are diagnostics, never usable editors (design rule 4).',
    'paper': 'PLAN v7 C6 maps every outcome (including mixed) to the paper text; title rule of the stage-2 decision 1.3.',
}
LOCKED8 = ['symutil.py', 'sym5_semantics.py', 'sym5_evaluator.py', 'lib8.py', 'lcore.py', 'cells8.py', 'chains8.py', 'analyze8.py', 'simulate8.py', 'dev8.py',
           'dlib.py', 'd_prep.py', 'd_c1.py', 'd_run.py', 'e2.py', 'e1_gain.py', 'selftest8.py', 'job_gpu.slurm', 'job_cpu.slurm']
NB = ['bart', 't5']; GB = ['t5_9b', 't5_bb', 't5_ll']


def main():
    require_slurm(); t0 = time.time()
    sh = ROOT / 'results/shards'; assert not sh.exists() or not any(sh.glob('chain_*')), 'confirm decoded output exists before the lock'
    for pat in ('chains8_*_complete.json', 'predictions.json', 'd_run.json', 'e2_run.json'): assert not list((ROOT / 'results').glob(pat)), pat
    sec = dict(audit=read(ROOT / 'results/n_audit.json'), n_gate=read(ROOT / 'results/n_gate.json'), selftest=read(ROOT / 'results/selftest8.json'),
               seed_registry=read(ROOT / 'seed_registry.json'), model_manifest=read(ROOT / 'data/model_manifest_v8.json'),
               gates_nat={bb: read(ROOT / f'results/gates_nat_{bb}.json') for bb in NB}, calib_nat={bb: read(ROOT / f'results/calib_nat_{bb}.json') for bb in NB},
               g_prep={bb: read(ROOT / f'results/g_prep_{bb}.json') for bb in GB}, calib_g={bb: read(ROOT / f'results/calib_g_{bb}.json') for bb in GB if (ROOT / f'results/calib_g_{bb}.json').exists()},
               train8={f'{bb}_{p}': read(ROOT / f'results/train8_{bb}_{p}.json') for bb, p in (('bart', 'N'), ('t5', 'N'), ('t5_9b', 'G'))},
               e1=read(ROOT / 'results/e1.json')['reading'], e2_train=read(ROOT / 'results/e2_train.json'), d_prep=read(ROOT / 'results/d_prep.json'), d_layer=read(ROOT / 'results/d_layer.json'),
               dev8={f'{u}_{bb}': read(ROOT / f'results/dev8_{u}_{bb}_summary.json') for u, bbs in (('N', NB), ('G', GB)) for bb in bbs},
               simulate8={f'{u}_{bb}': read(ROOT / f'results/simulate8_{u}_{bb}_summary.json') for u, bbs in (('N', NB), ('G', GB)) for bb in bbs},
               smoke={f'{u}_{bb}': read(ROOT / f'local/smoke/chains8_{u}_{bb}_complete.json')['pass_'] for u, bb in (('N', 'bart'), ('N', 't5'), ('G', 't5_9b'))})
    assert sec['audit']['pass'] and sec['selftest']['pass_'] and sec['seed_registry']['pass_'] and all(sec['smoke'].values())
    for v in sec['dev8'].values(): v.pop('cells', None)
    pre = {f'dev8_{k}': v['prechecks'] for k, v in sec['dev8'].items()}
    n2 = {bb: sec['gates_nat'][bb]['N2_precheck']['descriptive'] for bb in NB}
    dem = [f'N2/{bb}: descriptive (dev R_2N {sec["gates_nat"][bb]["N2_precheck"]["dev_R2N"]:.3f})' for bb in NB if n2[bb]]
    for k, v in pre.items():
        for pk, conds in v.items():
            for c, x in conds.items():
                if isinstance(x, dict) and x.get('keep') is False: dem.append(f'{pk}/{c}: dropped (dev latent prediction {x["pred"]:.3f} on the wrong side)')
    data = {str(f.relative_to(REPO)): sha(f) for f in sorted((ROOT / 'data').rglob('*')) if f.is_file()}
    for u, bbs in (('N', NB), ('G', GB)):
        for bb in bbs:
            for f in (ROOT / f'results/simulate8_{u}_{bb}.json.gz', ROOT / f'results/dev8_{u}_{bb}.json.gz'): data[str(f.relative_to(REPO))] = sha(f)
    for f in sorted((ROOT / 'local').glob('*.pt')): data[str(f.relative_to(REPO))] = sha(f)
    p = dict(experiment='composability_mechanisms_v7 (v8)', plan='PLAN.md', plan_sha256=sha(ROOT / 'PLAN.md'), predictions=PREDICTIONS, operational=OPERATIONAL,
             prechecks=pre, N2_descriptive=n2, demotions=dem, u_thresholds={k: v['U']['best'] for k, v in sec['dev8'].items()}, **sec,
             revisions={k: v['revision'] for k, v in sec['model_manifest'].items()}, sources={f: sha(ROOT / f) for f in LOCKED8}, data=data, locked=True,
             locked_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    dump('protocol.json', p); print('locked; protocol sha256', sha(ROOT / 'protocol.json'), json.dumps(dict(demotions=dem, N2=n2)), flush=True)


if __name__ == '__main__':
    main()
