"""L: lock the protocol before any confirm3 encoding/decoding and before any bind3 / bind3fix editor fit or evaluation."""
import time
from lib3 import *


def main():
    require_slurm(); t0 = time.time()
    assert not (ROOT / 'protocol.json').exists(), 'already locked; never rewrite'
    assert not list((ROOT / 'local').glob('*confirm3*')), 'confirm3 encodings must not exist before the lock'
    assert not (ROOT / 'results/shards').exists(), 'no confirm3 decoding before the lock'
    assert not [f for f in (ROOT / 'local').glob('*') if any(t in f.name for t in ('bind3', 'bind3fix')) and ('rrr' in f.name or 'C1' in f.name)], 'no bind3/bind3fix editor before the lock'
    assert read(ROOT / 'data/audit.json')['pass'] and read(ROOT / 'results/selftest.json')['pass']
    gb, gt = read(ROOT / 'results/gates_bart.json'), read(ROOT / 'results/gates_t5.json')
    cb, ct = read(ROOT / 'results/calib_bart.json'), read(ROOT / 'results/calib_t5.json')
    assert (ROOT / 'results/p0_diag.json').exists() and (ROOT / 'results/x4_postdict.json').exists()
    cal = lambda c: {d: dict(models=v['models'], derived=v['derived'], Kstar=v['Kstar'], planes=v['planes'], mean_step_dist=v['mean_step_dist'],
                             planes_sha256=v['planes_sha256']) for d, v in c['domains'].items()}
    data_files = [f'data/{d}/worlds.jsonl' for d in V1_DOMAINS + S.S1B] + ['data/audit.json', 'data/slot_positions.json', 'data/manifest.json',
                  'results/gates_bart.json', 'results/gates_t5.json', 'results/calib_bart.json', 'results/calib_t5.json', 'results/selftest.json',
                  'results/p0_diag.json', 'results/x4_postdict.json', 'inputs_manifest.json', 'PLAN.md']
    p = dict(
        locked=True, created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), version=1, plan='PLAN.md (predictions, thresholds and rules copied below; PLAN text is authoritative)',
        v2_amendment='experiments/composability_mechanisms_v1/AMENDMENT_01.md',
        backbones=dict(bart='aadd2ab0ae0c8268c7c9693540e9904811f36177', t5gemma='google/t5gemma-2b-2b-ul2-it@6a196a58ce2786cd139a1217a85d1f7b9984e330 (bf16)'),
        maps=S.MAPS, bind3fix_people=S.FIX3, data_seed=read(ROOT / 'data/manifest.json')['seed'], editor_seeds=list(SEEDS),
        gates=dict(bart=dict(GR_B=gb['GR_B'], GA_B=gb['GA_B'], B_status=gb['B_status'], B_domains=gb['B_domains'], B4p=gb['B4p'], B4p_delta=gb['B4p_delta']),
                   t5=dict(GR_T=gt['GR_T'], GA_T=gt['GA_T'], T_status=gt['T_status'], T_domains=gt['T_domains'], T_rrr_domains=gt['T_rrr_domains']),
                   excluded=dict(B=[d for d in S.S1B if d not in gb['B_domains']], T=[d for d in T_DOMAINS if d not in gt['T_domains']],
                                 T_rrr=[d for d in T_DOMAINS if d not in gt['T_rrr_domains']])),
        amplitudes=dict(bart=gb['amplitudes'], t5=gt['amplitudes']),
        calib=dict(bart=cal(cb), t5=cal(ct)),
        categories='composable >= 0.90; fail <= 0.20; otherwise partial (observed and derived alike)',
        paths='plus / minus / alternating, 2N steps each, from the world start (H, T, N); B: plus 30, minus 6, alt 6 from the world start; '
              'A: month as H, daysago plus from two (7), minus from nine (7), alternating from five (10)',
        predictions=dict(
            G3_0='RRR-16 natural one-way R_2N >= 0.95 (daysago R_7) in all five domains AND v1 C1 R_2 <= 0.20 for 5 domains x 3 seeds; otherwise stop',
            HS1='F{1} one-way plus R_2N <= 0.20 in all 4 cyclic domains (shared prediction)',
            HS2='F{1} alternating R_2N: frozen-plane >= 0.80, H-drift <= 0.20 (weekday, month)',
            HS3='F{1} one-way plus: frozen-plane A_N >= 0.80 and A_ceil(N/2) <= 0.30; H-drift A_N <= 0.30 (weekday, month)',
            frozen_plane_rule='HS1 pass and HS2, HS3 match the frozen-plane expectation in both weekday and month',
            HS4='F_not1 one-way plus R_2N category per domain (4). H-fund: all >= 0.90; H-complete: all <= 0.20; H-vote: locked derived category '
                '(calib.bart.<d>.derived.F_not1.category.plus). Count matches per hypothesis; the unique hypothesis with 4/4 wins; '
                'domains where H-fund and H-vote predict the same category are flagged "not discriminating"',
            HS5='single-plane freeze F{j}, j >= 2, one-way plus R_2N category (weekday 2, month 5, compass 1, egoside 1 = 9 cells). '
                'H-fund: all composable; H-complete: all fail; H-vote: locked categories. A hypothesis passes with >= 7/9 matches',
            HS6='domains with dim(K*) < N-1: E_K* R_2N >= 0.90 on all three paths AND RRR-dim(K*) one-way R_2N <= 0.20; gate: E_all >= 0.90 on all '
                'three paths else the domain is not evaluable; pass if >= 75% of evaluable applicable domains hold',
            HV1='conflict conditions (F_S with S non-empty, E_K with K not all planes; 3 paths; 4 domains): per world and step, model argmax == '
                'parsed decoded state, parsable outputs only. Pass: full-model agreement >= 0.85 and >= each control (equal, fundamental-only) + 0.05; '
                'if a control is already >= 0.95: "not discriminating"',
            Q5='frozen-plane established if HS1-HS3 pass; H-vote if HS4 and HS5 match H-vote and HV1 passes; H-fund if HS4 and HS5 match H-fund and '
               'the fitted model is not better than fundamental-only in HV1; H-complete if HS4 and HS5 match H-complete; else mixed',
            B1p='pron3 and name3 RRR-16 one-way R_6 >= 0.95 (all hypotheses)',
            B2p='bind3 max(RRR-16, RRR-32) one-way R_6: H-bind <= 0.50, H-geom >= 0.95, H-list <= 0.50',
            B2bp='bind3fix max(RRR-16, RRR-32) one-way R_6: H-bind >= 0.95, H-geom >= 0.95, H-list <= 0.50',
            B3p='C1 R_2 <= 0.20 for every domain x seed (all hypotheses)',
            B4p='slot R2(bind3) - min(pron3, name3, bind3fix): H-bind <= -0.30, H-geom |.| < 0.10; measured before the lock (value in gates.bart.B4p_delta), not prospective',
            Q2p='B1p fail -> not decidable; else (B2p, B2bp): (<=0.50, >=0.95) H-bind; (>=0.95, >=0.95) H-geom; (<=0.50, <=0.50) H-list; else mixed',
            N_admission='dev single >= 0.90 after 600 updates, else one retrain with 2400 updates; still failing -> "cannot learn", excluded from N1-N3',
            N1='sigma_max maps: median M1 over admitted (map, seed) cells <= 0.60 (both hypotheses); M1 >= 0.90 -> "unexplained"',
            N2='per sigma_max map, seed-median C1 one-way R_2: H-state if >= 0.50 for >= 2 of 3 maps; H-token if <= 0.20 for >= 2 of 3 maps',
            N3='probe on the C1 first-step state, median over admitted sigma_max cells: H-state if target >= 0.50; H-token if source >= 0.80',
            Q6='conclude only when N2 and N3 support the same hypothesis; else mixed',
            T0='per T domain: max(RRR-16, RRR-32) natural one-way R_2N >= 0.95; otherwise T3, T5, T6 not evaluable in that domain',
            T1='C1 R_1 >= 0.90 and R_2 <= 0.20 for every domain x seed (v2 S5: B3 direction)',
            T2='C1 medians over (domain, seed): M1 >= 0.90, |M2| <= 0.20, M3 source >= 0.80 -> H-instr; M1 <= 0.60 or M2 >= 0.50 or target >= 0.80 -> H-approx; else neither',
            T3='per evaluable domain: r* = smallest grid rank with one-way R_2N >= 0.95 at it and all larger grid ranks; pass if N-2 <= r* <= N and '
               'the largest grid rank below r* has R_2N <= 0.20; T3 passes if all evaluable domains pass (v2 S5: R1)',
            T4='single-step success >= 0.95 at r = N-2 (weekday 5, month 10) (v2 S5: R2)',
            T5='weekday and month: sigma_max max(RRR-16, RRR-32) one-way R_2N >= 0.95 and RRR-16 R_10N(natural) - R_10N(sigma_max) <= 0.05 (v2 S5: A1-A3)',
            T6='on T5Gemma with its own calibration: HS1 and HS2 hold, HV1 passes, and the HS4 winner equals BART\'s HS4 winner',
            S5_original='"A1-A3, R1-R2, B3 的方向与 BART 一致" (v2 PLAN section 9), concretised as T1, T3-T5',
            A_H_weight='lambda = 10: seed-median month one-way R_24 >= 0.90 and seed-median daysago one-way R_7 >= 0.90',
            A_H_conflict='H-weight fails AND the RRR-initialised C3 drifts: its seed-median DRIFT > DRIFT of v2 RRR-16 and its seed-median one-way R '
                         '(month R_24, daysago R_7) <= 0.90 in at least one domain',
            A3='12 month C3 editors (v1 lambda=1 x3, lambda=3 x3, lambda=10 x3, RRR-init x3): count where (one-way R_12 >= 0.90) == (k=1 in the unit block); pass if >= 10/12',
            exploratory=['X1-X4', 'R16-slot', 'offset heatmaps', 's_k order vs harmonic entry order', 'B exploratory output types', 'N skip2 and natural-step writes',
                         'A DRIFT / adjacent cosine / vote-model postdiction']),
        stop_rules=['G3-0 fail', 'same job fails twice for an unknown reason', 'leakage', 'budget 14 GPU h (report at 10)'],
        sources={k: sha(ROOT / k) for k in LOCKED3},
        data={str((ROOT / k).relative_to(REPO)): sha(ROOT / k) for k in data_files})
    dump('protocol.json', p); print('locked', sha(ROOT / 'protocol.json'), flush=True)


if __name__ == '__main__':
    main()
