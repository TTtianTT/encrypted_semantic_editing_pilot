"""L: lock the protocol (CPU) before any confirm4 encoding/decoding, before any bind3 editor evaluation and before any U / X training.
sections() is shared with the pre-lock smoke test so that the smoke test runs on exactly the locked derived quantities."""
import time
from lib4 import *

PREDICTIONS = {
    'G4_0': '每个保留的（骨干，V 的域），基算子在 confirm4 上单向 R_2N ≥ 0.95；v1 的 C1 在 weekday、month、compass 上 R_2 ≤ 0.20。新域不通过，该域退出；旧域不通过，停止并排查管线。',
    'V0': '新域，两个骨干：s_1 最小（全部新域）；a_1 在 N ≥ 7 的新域中最大。全部成立为通过。',
    'V1': 'F{1}：N ≥ 7 的域 × 两个骨干（至多 8 格）。H-ms：单向 plus R_2N ≤ 0.20，且交替 R_2N ≥ 0.80；H-fund：单向与交替都 ≤ 0.20；H-flat：单向与交替都 ≤ 0.20。除至多 1 格外都符合某一假设，即判为该假设。',
    'V2a': 'F{1} 的 plus：A(1) − A(⌊N/2⌋)（附录 A.1），同上 8 格。H-ms ≥ 0.50；H-fund ≤ 0.10（A(1) 约为 0）；H-flat ≤ 0.10（处处约为 0）。判定同 V1。',
    'V2b': 'F¬1 的 plus：A(⌊N/2⌋) − A(1)，同上 8 格。H-ms ≥ 0.25；H-fund ≤ 0.10（处处约为 1）；H-flat ≤ 0.10（处处约为 0）。判定同 V1。',
    'V3': '单平面冻结 F{j}（j ≥ 2）的类别：plus 与 minus × 五个域 × 两个骨干。H-ms：锁定的派生类别；H-fund："可组合"；H-flat："失败"。按附录 A.6，H-ms 分别与 H-fund、H-flat 比较；每个比较至少 4 个可计分格子，否则不可评。',
    'V4': '冲突条件（S 非空的 F_S）下逐 world、逐步的一致率（真实潜变量，只计可解析输出），每个骨干。H-ms：拟合 ≥ 0.85；拟合 − 等权的 95% CI 下界 > 0；拟合 − 只用基频的 CI 下界 > 0.10。H-fund：只用基频 ≥ 拟合。拟合 − 等权的 CI 含 0 时判为 H-equal。',
    'Q9': 'V1、V2a、V2b 都符合 H-ms，V3 胜过两个对手（或不可评），且 V4 在两个骨干上都成立：判为 H-ms。V1–V3 同上，但 V4 中拟合 − 等权的 CI 在至少一个骨干上含 0：判为 H-equal。V1、V2a、V2b 符合 H-fund 或 H-flat：判为相应假设。其他情况如实报告为混合。',
    'R1': '可计分格子，plus：FF-r 的 R_2N，以及 ΔR = R_2N(FF-r) − R_2N(RRR-r)。H-alloc：FF-r ≥ 0.90，且 ΔR ≥ 0.20；H-capacity：ΔR ≤ 0.05。≥ 75% 的可计分格子符合哪一方，就判为哪一方；否则为混合。可计分格子少于 3 格时，R1 在锁定时标为不可评。',
    'U1': 'C1-U4 的单向 plus R_2N（每个域取 seed 中位数）。H-state：≥ 0.90（至少 2/3 个域）；H-shortcut：≤ 0.20（至少 2/3 个域）。',
    'U2': 'C1-U4 在第 1 步状态上的探针读出。H-state：读出目标 ≥ 0.80；H-shortcut：读出源 ≥ 0.80。',
    'U1b': 'C1-UN：同 U1。',
    'Q11': 'U1 与 U2 同向才下结论，否则为混合。',
    'X1': 'name3、bind3fix：Att-L2 的单向 R_6（seed 中位数）。H-arch ≥ 0.95；H-deep ≥ 0.95。X1 是正对照，两种假设的预期相同。X1 不通过时，X2 不可评。',
    'X2': 'bind3：Att-L2 与 Tok-L2 的单向 R_6（seed 中位数）。H-arch：Att-L2 ≥ 0.90，且 Tok-L2 ≤ 0.20；H-deep：Att-L2 ≤ 0.50。',
    'S1': 'T5Gemma，weekday 与 month，自然映射与 σ_max，RRR-32，单向 plus 走 10N 步。门槛：两种映射在 RRR-32 上的 R_2N 都 ≥ 0.95，否则该域不可评。R_10N(自然) − R_10N(σ_max)：H-slot 两个域都 ≤ 0.05；H-longsym 至少一个域 ≥ 0.20。',
}
OPERATIONAL = {
    'categories': 'composable >= 0.90; fail <= 0.20; otherwise partial (observed R_2N and derived R-hat_2N alike)',
    'paths': 'V, R, U: plus / minus / alternating (plus first), 2N steps from the world start; X: plus 30, minus 6, alternating 6 from the world start; S: plus 10N',
    'V1_V2_cells': 'cells = (backbone, domain) with N >= 7 among the domains kept after G4-0; H-fund and H-flat make the same V1/V2 predictions, so a V1/V2 '
                   'match for either is reported as "H-fund/H-flat" and V3 separates them',
    'V2_A': 'A(m~) per appendix A.1 from the per-step success A_t (non-cumulative) over t = 1..2N of the one-way plus path; season (N = 4): floor(N/2) = 2',
    'V3_season': 'for N = 4 F{2} is F{not 1}; its chain is the F{not 1} chain',
    'V4_records': 'F{1}, F{not 1} and every F{j} (j >= 2) on all three paths and all V domains of the backbone; per (world, step) with a parsable decoded state; '
                  'agreement = argmax of the model == decoded state; cluster bootstrap over worlds (A.7); a model "wins" a comparison by the CI rule only',
    'V4_verdict': 'per backbone: "H-ms holds" iff fitted >= 0.85 and CI(fit - equal) lower > 0 and CI(fit - fund) lower > 0.10; "H-fund" iff fund >= fit; '
                  '"H-equal" iff CI(fit - equal) contains 0; otherwise "neither"',
    'Q9_V3': 'V3 "beats both or not evaluable": for each of the two comparisons (H-ms vs H-fund, H-ms vs H-flat) the A.6 result is "H wins" or "not evaluable"',
    'R1_obs': 'plus path R_2N on confirm4 of FF-r and RRR-r in the locked scorable cells',
    'U_cannot_learn': 'a (variant, domain, seed) that fails admission after the 2400-update retrain is "cannot learn": it enters the U1/U1b seed median with R_2N = 0 '
                      'and is excluded from U2 (no admitted editor to probe); the probe readout is the v3 M3 probe (train canonical slots)',
    'U2_pool': 'median over admitted C1-U4 (domain, seed) cells of the step-1 readout fractions',
    'U1b_domains': 'C1-UN has two domains; "at least 2/3 of the domains" means both',
    'X_median': 'seed median of one-way plus trajectory success R_6 on confirm4',
    'S1_not_evaluable': 'a domain failing the gate is not evaluable; H-slot needs every domain evaluable and <= 0.05; H-longsym needs >= 0.20 in at least one '
                        'evaluable domain; otherwise mixed (or not decidable if no domain is evaluable)',
}


def sections(bbs=('bart', 't5')):
    G = {bb: read(ROOT / f'results/gates_{bb}.json') for bb in bbs}; C = {bb: read(ROOT / f'results/calib_{bb}.json') for bb in bbs}
    Pr = {bb: read(ROOT / f'results/prelock_{bb}.json') for bb in bbs}
    g = lambda x: dict(GR=x['GR'], GT=x['GT'], GB=x['GB'], V_domains=x['V_domains'], R_domains=x['R_domains'], excluded=x['excluded'],
                       new_domains_passing=x['new_domains_passing'], **({'X_ok': x['X_ok'], 'compass_ok': x['compass_ok']} if 'X_ok' in x else {}))
    cal = lambda c: {d: dict(models=v['models'], derived=v['derived'], planes=v['planes'], planes_sha256=v['planes_sha256'], ideal_At=v['ideal_At'],
                             source=v['source']) for d, v in c['domains'].items()}
    v3 = dict(cells_H_ms={k: v for bb in bbs for k, v in C[bb]['V3_cells']['H_ms'].items()},
              scorable_vs_fund=[c for bb in bbs for c in C[bb]['V3_cells']['scorable_vs_fund']],
              scorable_vs_flat=[c for bb in bbs for c in C[bb]['V3_cells']['scorable_vs_flat']], min_cells=4)
    v3['vs_fund_evaluable'] = len(v3['scorable_vs_fund']) >= 4; v3['vs_flat_evaluable'] = len(v3['scorable_vs_flat']) >= 4
    v3['verdict_at_lock'] = {k: ('evaluable' if v3[f'{k}_evaluable'] else 'not evaluable') for k in ('vs_fund', 'vs_flat')}
    rs = [c for bb in bbs for c in Pr[bb]['scorable_cells']]
    R = dict(cells={k: v for bb in bbs for k, v in Pr[bb]['cells'].items()}, scorable_cells=rs, evaluable=len(rs) >= 3, min_cells=3)
    R['verdict_at_lock'] = 'evaluable' if R['evaluable'] else 'not evaluable (fewer than 3 scorable cells)'
    return dict(gates={bb: g(G[bb]) for bb in bbs}, V0_amplitudes={bb: G[bb]['V0_amplitudes'] for bb in bbs},
                calib={bb: cal(C[bb]) for bb in bbs}, V3_precheck=v3, R_precheck=R, S_fits=Pr['t5'].get('S_fits') if 't5' in bbs else None)


LOCK_FILES = ['data/audit.json', 'data/slot_positions.json', 'data/manifest.json', 'results/gates_bart.json', 'results/gates_t5.json',
              'results/calib_bart.json', 'results/calib_t5.json', 'results/prelock_bart.json', 'results/prelock_t5.json', 'results/selftest.json',
              'results/smoke_bart.json', 'results/smoke_t5.json', 'results/patch/p_diag.json', 'inputs_manifest.json', 'PLAN.md']


def main():
    require_slurm(); t0 = time.time()
    assert not (ROOT / 'protocol.json').exists(), 'already locked; never rewrite'
    assert not [f for f in (ROOT / 'local').glob('*.pt') if CONFIRM in f.name], 'confirm4 encodings must not exist before the lock'
    assert not (ROOT / 'results/shards').exists(), 'no confirm4 decoding before the lock'
    assert not [f for f in (ROOT / 'local').glob('*.pt') if f.name.startswith(('u_', 'x_'))], 'no U / X weights before the lock'
    assert not [f for f in (ROOT / 'results').rglob('*') if 'bind3_' in f.name and ('x_' in f.name or 'chain' in f.name or 'single' in f.name)], 'no bind3 editor evaluation before the lock'
    au = read(ROOT / 'data/audit.json'); st = read(ROOT / 'results/selftest.json')
    assert au['pass'] and st['pass']
    for f, h in {**au['sources'], **st['sources']}.items(): assert sha(ROOT / f) == h, f'audit/selftest ran on a different {f}'
    for bb in ('bart', 't5'):
        sm = read(ROOT / f'results/smoke_{bb}.json'); assert sm['pass'], f'smoke {bb} failed'
        for f, h in sm['sources'].items(): assert sha(ROOT / f) == h, f'smoke {bb} ran on a different {f}'
    for f in ('p2_c3.json', 'p5_transplant_bart.json', 'p5_transplant_t5.json', 'p6_dyn_bart.json', 'p6_dyn_t5.json', 'p_diag.json'):
        assert (ROOT / 'results/patch' / f).exists(), f'P result missing: {f}'
    sec = sections(); man = read(ROOT / 'data/manifest.json')
    p = dict(locked=True, created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), version=1,
             plan='PLAN.md (predictions, thresholds and rules copied below verbatim; PLAN text is authoritative)',
             backbones=dict(bart='aadd2ab0ae0c8268c7c9693540e9904811f36177', t5gemma='google/t5gemma-2b-2b-ul2-it@6a196a58ce2786cd139a1217a85d1f7b9984e330 (bf16)'),
             maps=S.MAPS, bind3fix_people=S.FIX3, data_seed=man['seed'], data_counts=man['counts'], editor_seeds=list(SEEDS),
             world_seeds=dict(v4=man['seed_rule'] + f' with seed {man["seed"]}', v1_train_dev='symmetry_composability_v1/data/manifest.json',
                              v3_bind3fix_reuse='composability_mechanisms_v2/data/manifest.json'),
             predictions=PREDICTIONS, operational=OPERATIONAL, **sec,
             stop_rules=['G4-0 old domain or C1 fails', 'same job fails twice for an unknown reason', 'leakage', 'budget 16 GPU h (report at 12)'],
             sources={k: sha(ROOT / k) for k in LOCKED4},
             data={str((ROOT / k).relative_to(REPO)): sha(ROOT / k) for k in LOCK_FILES + [f'data/{d}/worlds.jsonl' for d in man['all']]})
    dump('protocol.json', p); print('locked', sha(ROOT / 'protocol.json'), 'V3', p['V3_precheck']['verdict_at_lock'], 'R', p['R_precheck']['verdict_at_lock'],
                                   'R cells', p['R_precheck']['scorable_cells'], flush=True)


if __name__ == '__main__':
    main()
