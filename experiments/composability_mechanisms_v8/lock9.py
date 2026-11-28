"""v9 lock (CPU; PLAN v9 section 6). Writes protocol.json: predictions (verbatim from PLAN v9 sections 3-5), operational rules, pre-check
decisions (DEVIATIONS 3) and the demotions they imply, the B4 rule (DEVIATIONS 5), seed registry, layer choices, admissions, the chosen
second decoder-only model, simulation hashes, data and source hashes. Asserts: no confirm decoded output exists; no post-lock result exists;
self-tests (CPU and the decoder-only identity check), seed registry and smoke tests passed."""
import time
from symutil import *

PREDICTIONS = {
    'B1a': '全局均值差。H-cancel：R_1 ≤ 0.20（在一圈上取平均时，状态分量互相抵消）；对立 H-shift：R_1 ≥ 0.80。',
    'B1b': '单对均值差。R_1(起点 = x₀) ≥ 0.80，且其他起点的平均 R_1 ≤ 0.20；全体 R_2 ≤ 0.20。对立：其他起点的平均 R_1 ≥ 0.50。',
    'B1c': '按读出索引的均值差。H-state-aware：单向 R_2N ≥ 0.90；对立：≤ 0.50。',
    'B2': 'LoReFT。H-objective：LoReFT-C1 的 R_1 ≥ 0.90、R_2 ≤ 0.20、D ≥ 0.80；LoReFT-C3U4 的 R_2N ≥ 0.95。对立 H-param：LoReFT-C1 的 R_2N ≥ 0.90。',
    'B3': '容量。H-objective：满秩线性与 MLP 都满足 R_2 ≤ 0.20 且 D ≥ 0.80。对立 H-capacity：R_2N ≥ 0.90。',
    'B4': '展开视野。H-counter：U8、U16 的 R_{S_max+2} ≤ 0.50，Urand 的 R_4N ≤ 0.50。对立 H-state：任一编辑器的 R_4N ≥ 0.90。（判定只用通过准入的编辑器；DEVIATIONS 5）',
    'B5': '解析旋转。H-sufficient：单向 R_2N ≥ 0.95；对立：≤ 0.50。',
    'B6': '解码后重编码（参照，不是预测）：报告 R_2N 与每步墙钟时间。',
    'S': '每个格子；判定只用 5 个新 seed：C1 的 R_1 ≥ 0.90 且 R_2 ≤ 0.20 的 seed ≥ 4/5；C3-U4 的单向 R_2N ≥ 0.95 的 seed ≥ 4/5。报告全部 8 个 seed 的最小值与最大值。',
    'DO1a': '（主）S-RRR-(r*_pred) 的单向 R_2N ≥ 0.95。', 'DO1b': '（次）S-RRR-(r*_pred − 2) 的单向 R_2N ≤ 0.50。',
    'DO2': '（主）冻结特征（相对阈值，带预检）：F{1} 单向 ≤ 0.20；F{1} 交替 ≥ F∅ 交替 − 0.10；F¬1 ≤ 0.10。', 'DO3': '（主）谱：s_1 在全部平面中最小。',
    'DO4': '（主）一步 CE 槽位编辑器（seed 45–47）：R_1 ≥ 0.90、R_2 ≤ 0.20、D ≥ 0.80。', 'DO5': '（主）槽位 C3-U4（seed 45–47）：单向 R_2N ≥ 0.95。',
    'DO6': '（主）潜空间预测器：一致率 ≥ 0.85，相对朴素判断的提升 CI 下界 > 0，类别准确率 ≥ 0.80。',
    'DO': 'DO1a 与 DO2–DO6 都成立，记为该组合"复现"。两个模型都复现，论文的标题与摘要才可以写 decoder-only。',
    'G9_0': '锁定后的健全性闸门：基算子 RRR-16 与 S-RRR_nat 在所用 confirm 集上的单向 R_2N ≥ 0.95；不通过即停止排查。',
}
OPERATIONAL = {
    'general': 'Paths start at the world start; 2N steps (plus, minus, alternating), B4 4N. R_k = fraction of worlds whose decoded output is a success at every step '
               '1..k. Template 0 on confirm7 (= confirm6; text reused, first evaluation for every v9 editor and the second decoder-only model), month-nat on confirm8. '
               'R values of single-path predictions on the plus path. Seed medians over the admitted seeds of a cell; an editor that could not learn counts as R = 0 '
               'in S and B2 / B3 medians (admission rule), and B4 is judged on admitted editors only (DEVIATIONS 5). D = among worlds with a parsable step-1 decode, '
               'the share whose locked step-1 readout (sim9 / do_sim) differs from the decoded state.',
    'precheck': 'DEVIATIONS 3: latent simulation on dev only; a condition the simulated slot readout puts on the other side of its threshold is dropped (exploratory); '
                'B5 descriptive if the simulated R_2N >= 0.95; R_1 of CE editors and D not pre-checked.',
    'B_rules': 'B1a: H-cancel R_1 <= 0.20, H-shift >= 0.80, else mixed. B1b: holds iff its kept conditions hold; opposing iff other-start mean R_1 >= 0.50. B1c: >= 0.90 '
               'H-state-aware, <= 0.50 opposing. B2: H-objective iff LoReFT-C1 medians R_1 >= 0.90, R_2 <= 0.20 (if kept), D >= 0.80 and LoReFT-C3U4 median R_2N >= 0.95 '
               '(if kept); H-param iff LoReFT-C1 median R_2N >= 0.90; else mixed. B3: H-objective iff Full-C1 and MLP-C1 both have median R_2 <= 0.20 (if kept) and '
               'D >= 0.80; H-capacity iff either has median R_2N >= 0.90. B4: per variant the admitted seeds; variants with < 2 admitted descriptive; H-state iff an '
               'admitted editor has R_4N >= 0.90; H-counter iff every non-descriptive variant has median R_{S_max+2} (U8, U16) resp. R_4N (Urand) <= 0.50. '
               'B5: >= 0.95 H-sufficient, <= 0.50 opposing (descriptive if so pre-checked). S: per (backbone, domain) the new seeds 45-49.',
    'DO_rules': 'Per (model, domain) at the model\'s layer; readout = equal-weight plane readout (lambda_k = 1 / median one-step distance on train latents). DO1a, DO2 '
                '(kept conditions), DO3 (argmin of the confirm one-step change s_k is the fundamental), DO4 (C1 medians), DO5 (C3-U4 median R_2N), DO6 (agreement, CI '
                'lower bound of latent - naive > 0, category accuracy over cells >= 0.80). A combination replicates iff DO1a and DO2-DO6 hold; combinations whose '
                'reconstruction gate failed are not evaluated.',
    'paper': 'PLAN v9 section 7 maps every outcome to the paper.',
}
LOCKED9 = ['symutil.py', 'sym5_semantics.py', 'sym5_evaluator.py', 'lib9.py', 'lcore.py', 'dlib.py', 'cells9.py', 'sim9.py', 'chains9.py', 'analyze9.py', 'do_prep.py',
           'do_sim.py', 'do_run.py', 'selftest9.py', 'job_gpu.slurm', 'job_cpu.slurm']


def main():
    require_slurm(); t0 = time.time(); man = read(ROOT / 'data/model_manifest_v9.json'); do2 = read(ROOT / 'results/do_gate2.json')['chosen']; models = ['gemma'] + ([do2] if do2 else [])
    sh = ROOT / 'results/shards'; assert not sh.exists() or not any(sh.glob('chain_*')), 'confirm decoded output exists before the lock'
    for pat in ('chains9_*_complete.json', 'do_run_*', 'predictions.json'): assert not list((ROOT / 'results').glob(pat)), pat
    sec = dict(selftest=read(ROOT / 'results/selftest9.json'), seed_registry=read(ROOT / 'seed_registry.json'), manifest=man, do_gate2=read(ROOT / 'results/do_gate2.json'),
               train9={f'{bb}_{p}': read(ROOT / f'results/train9_{bb}_{p}.json') for bb in ('bart', 't5') for p in ('S', 'B2', 'B3', 'B4')},
               do_prep={m: read(ROOT / f'results/do_prep_{m}.json') for m in models}, do_selftest={m: read(ROOT / f'results/do_selftest_{m}.json') for m in models},
               sim9={bb: {k: v for k, v in read(ROOT / f'results/sim9_{bb}_summary.json').items() if k in ('precheck', 'sha256')} for bb in ('bart', 't5')},
               do_sim={m: {k: v for k, v in read(ROOT / f'results/do_sim_{m}_summary.json').items() if k in ('precheck', 'sha256', 'lambda', 'layer')} for m in models},
               smoke={**{f'chains9_{bb}': read(ROOT / f'local/smoke/chains9_{bb}_complete.json')['pass_'] for bb in ('bart', 't5')},
                      **{f'do_run_{m}': read(ROOT / f'local/smoke/do_run_{m}_complete.json')['pass_'] for m in models}},
               p9={p: str((ROOT / f'results/p9{p}.json').relative_to(REPO)) for p in 'abcde'})
    assert sec['selftest']['pass_'] and sec['seed_registry']['pass_'] and all(sec['smoke'].values()) and all(v['pass_'] for v in sec['do_selftest'].values())
    pre = {bb: sec['sim9'][bb]['precheck'] for bb in ('bart', 't5')}; dem = []
    for bb, pc in pre.items():
        for k, conds in pc.items():
            for c, x in conds.items():
                if x.get('keep') is False: dem.append(f'{bb}/{k}/{c}: dropped (dev simulation {x["pred"]:.3f})')
                if x.get('descriptive'): dem.append(f'{bb}/{k}/{c}: descriptive (dev simulation {x["pred"]:.3f})')
    for m in models:
        for d, pc in sec['do_sim'][m]['precheck'].items():
            for c, x in pc.items():
                if x.get('keep') is False: dem.append(f'DO/{m}/{d}/{c}: dropped (dev simulation {x["pred"]})')
    data = {str(f.relative_to(REPO)): sha(f) for f in sorted((ROOT / 'data').rglob('*')) if f.is_file()}
    for f in sorted((ROOT / 'results').glob('sim9_*.json.gz')) + sorted((ROOT / 'results').glob('do_sim_*.json.gz')) + sorted((ROOT / 'local').glob('*.pt')): data[str(f.relative_to(REPO))] = sha(f)
    p = dict(experiment='composability_mechanisms_v8 (v9)', plan='PLAN.md', plan_sha256=sha(ROOT / 'PLAN.md'), predictions=PREDICTIONS, operational=OPERATIONAL, prechecks=pre,
             do2_model=do2, demotions=dem, **sec, sources={f: sha(ROOT / f) for f in LOCKED9}, data=data, locked=True, locked_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    dump('protocol.json', p); print('locked; protocol sha256', sha(ROOT / 'protocol.json'), json.dumps(dict(do2=do2, demotions=dem)), flush=True)


if __name__ == '__main__':
    main()
