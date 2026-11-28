"""W1 + W2 (CPU): resolve every number of claim_map.yaml from the locked results; write paper/claims.yaml and paper/generated/numbers.tex.
Numbers are read (file + JSON path) or computed by a named derivation below from locked files only; nothing is copied by hand. Each claim
records its evidence files (SHA256), the lock commit of every round it cites, and its numbers with their sources. Numbers marked pending
(v6 not merged yet) become \\TODO{v6} macros."""
import sys
import yaml
import numpy as np
from common import *

LOCK = {r: f'experiments/{d}/protocol_lock.json' for r, d in (('v1', 'symmetry_composability_v1'), ('v2', 'composability_mechanisms_v1'), ('v3', 'composability_mechanisms_v2'),
                                                             ('v4', 'composability_mechanisms_v3'), ('v5', 'composability_mechanisms_v4'), ('v6', 'composability_mechanisms_v5'), ('v7', 'composability_mechanisms_v6'),
                                                             ('v8', 'composability_mechanisms_v7'), ('v9', 'composability_mechanisms_v8'))}
P = {r: f'experiments/{d}/results/predictions.json' for r, d in (('v2', 'composability_mechanisms_v1'), ('v3', 'composability_mechanisms_v2'), ('v4', 'composability_mechanisms_v3'),
                                                                ('v5', 'composability_mechanisms_v4'))}
P['v1'] = 'experiments/symmetry_composability_v1/results/e1_predictions.json'
V5 = 'experiments/composability_mechanisms_v4'
V3ALG = 'experiments/composability_mechanisms_v2/results/algebra.json'
V3GATES = [f'experiments/composability_mechanisms_v2/results/gates_{b}.json' for b in ('bart', 't5')]
V6AUD = 'experiments/composability_mechanisms_v5/data/audit.json'
V7P = 'experiments/composability_mechanisms_v6/results/patch/p_posthoc7.json'
V7R = 'experiments/composability_mechanisms_v6/results/predictions.json'
VT = 'experiments/composability_mechanisms_v6/results/theory/t_theory.json'
E1 = 'experiments/composability_mechanisms_v7/results/e1.json'          # v8 E1 (exploratory, CPU, before the v8 lock; v7 confirm7 encodings only)
_e1 = lambda kind, op, fn: fn(v[op] for k, v in read(E1)['cells'].items() if k.split('/')[2] == kind)
P8 = 'experiments/composability_mechanisms_v7/results/predictions.json'; D8 = 'experiments/composability_mechanisms_v7/results/d_run.json'
E28 = 'experiments/composability_mechanisms_v7/results/e2_run.json'; E2B = 'experiments/composability_mechanisms_v7/results/e2b.json'; N8G = 'experiments/composability_mechanisms_v7/results/n_gate.json'
_n8 = lambda bb: read(P8)['N']['per_backbone'][bb]
_g8c = lambda k: read(P8)['G']['cells'][k]['obs_rate']
P9R = 'experiments/composability_mechanisms_v8/results/predictions.json'; P9A, P9B, P9C, P9D = (f'experiments/composability_mechanisms_v8/results/p9{x}.json' for x in 'abcd')
_b9all = lambda: [(bb, d) for bb in ('bart', 't5') for d in ('weekday', 'month')]
_b9 = lambda r: read(P9R)['B'][r[0]][r[1]]
_s9 = lambda: [v['S'] for bb in ('bart', 't5') for v in read(P9R)['B'][bb].values() if 'S' in v]
_do9 = lambda: read(P9R)['DO']['gemma']['weekday']
P5B = 'experiments/composability_mechanisms_v3/results/patch/p5_transplant_bart.json'; P5T = 'experiments/composability_mechanisms_v3/results/patch/p5_transplant_t5.json'
V3AUD = 'experiments/composability_mechanisms_v2/data/audit.json'
ROUND_DIRS = ['symmetry_composability_v1', 'composability_mechanisms_v1', 'composability_mechanisms_v2', 'composability_mechanisms_v3', 'composability_mechanisms_v4', 'composability_mechanisms_v5', 'composability_mechanisms_v6', 'composability_mechanisms_v7', 'composability_mechanisms_v8']


def _v3_sk():
    """v3 exploratory analysis _s_k_vs_entry_order: per-plane update energy s_k of the full-rank operator, per backbone / domain."""
    a = read(V3ALG)['_s_k_vs_entry_order']; return {k: v for k, v in a.items() if isinstance(v, dict) and 's_k' in v}


def _v3_amp():
    """v3 pre-lock gate files: per-plane amplitude a_k and one-step change s_k of the canonical slot code, per backbone / domain."""
    return {f'{b}/{d}': v for f in V3GATES for b in [f.split('_')[-1][:-5]] for d, v in read(f)['amplitudes'].items()}


def _v6_tmpl(d, k):
    """v6 confirm6: number of held-out templates of a multi-template domain with at least k worlds after deduplication."""
    return sum(1 for n in read(V6AUD)['domains'][d]['templates'].values() if n >= k)


def _p2_rb(field):
    """v7 P2: BART month under-trained state editors (v1 C3, v3 C3-l3 / C3-l10, v4 P2b, v6 C3n900), one-way paths."""
    return [v[field] for k, v in read(V7P)['P2'].items() if k.startswith('v6C/bart/month/') and k.split('/')[3] in ('C3v1', 'C3l3v3', 'C3l10v3', 'P2b', 'C3n900') and k.rsplit('/', 1)[1] in ('plus', 'minus')]


def _k7_surv():
    """v7 K: Att2L-U8 seeds whose bind3 one-way R_30 >= 0.90 on confirm7."""
    return [int(s) for s, v in read(V7R)['K']['table']['bind3/Att2LU8/R30'].items() if v >= .90]


def _k7_cont(s):
    return read(V7R)['K']['exploratory'][f'contraction/Att2LU8_s{s}']


def _ce_slot_stays(key):
    s = read(f"{V5}/results/simulate_{key.split('/')[1]}.json.gz")[key]
    return sum(1 for i in range(len(s['start'])) if s['argmax']['full'][i][0] == s['start'][i])


DERIVED = {
    'v1_c1_r2_max': (lambda: max(v['rate'] for v in get(read(P['v1']), 'predictions/P5/observed/C1_R2').values()), [P['v1']]),
    'v2_g20_rrr16_min': (lambda: min(v['rate'] for v in get(read(P['v2']), 'G2_0/RRR16_R2N').values()), [P['v2']]),
    'v5_g50_c1_max': (lambda: max(v['rate'] for v in read(f'{V5}/results/g50_bart.json')['C1'].values()), [f'{V5}/results/g50_bart.json']),
    'v5_c1v1_r1_min': (lambda: min(v['naive_rate'] for k, v in get(read(P['v5']), 'L/cells').items() if k.split('/')[3].startswith('C1v1') and k.split('/')[4] in ('plus', 'minus')), [P['v5']]),
    'v5_g50_base_min': (lambda: min(v['rate'] for bb in ('bart', 't5') for v in read(f'{V5}/results/g50_{bb}.json')['base'].values()),
                        [f'{V5}/results/g50_bart.json', f'{V5}/results/g50_t5.json']),
    'v5_ce_slot_stays_bart': (lambda: _ce_slot_stays('L/bart/weekday/C1v1_s42/plus'), [f'{V5}/results/simulate_bart.json.gz']),
    'v5_ce_slot_stays_t5': (lambda: _ce_slot_stays('L/t5/month/C1U4n_s42/plus'), [f'{V5}/results/simulate_t5.json.gz']),
    'v4_u1_median_max': (lambda: max(get(read(P['v4']), 'U/U1/seed_median_R2N').values()), [P['v4']]),
    'v5_l4_c1u4_max': (lambda: max(v['R2N'] for k, v in get(read(P['v5']), 'L/L4/cells').items() if k.startswith('C1U4')), [P['v5']]),
    'v5_l4_c3u4_min': (lambda: min(v['R2N'] for k, v in get(read(P['v5']), 'L/L4/cells').items() if k.startswith('C3U4')), [P['v5']]),
    'v2_r1_sharp_count': (lambda: sum(1 for v in get(read(P['v2']), 'R1/observed').values() if v.get('sharp')), [P['v2']]),
    'v4_v0_s1_smallest': (lambda: sum(1 for v in get(read(P['v4']), 'V/V0/cells').values() if v['s1_smallest']), [P['v4']]),
    'v4_v0_a1_largest': (lambda: sum(1 for v in get(read(P['v4']), 'V/V0/cells').values() if v['a1_largest']), [P['v4']]),
    'v4_v0_cells': (lambda: len(get(read(P['v4']), 'V/V0/cells')), [P['v4']]),
    'v4_v0_a1_evaluable': (lambda: sum(1 for v in get(read(P['v4']), 'V/V0/cells').values() if v['a1_largest'] is not None), [P['v4']]),
    'v3_sk_s1_smallest': (lambda: sum(1 for v in _v3_sk().values() if min(v['s_k'], key=lambda k: v['s_k'][k]) == '1'), [V3ALG]),
    'v3_sk_cells': (lambda: len(_v3_sk()), [V3ALG]),
    'v34_s1_smallest_total': (lambda: DERIVED['v3_sk_s1_smallest'][0]() + DERIVED['v4_v0_s1_smallest'][0](), [V3ALG, P['v4']]),
    'v34_cells_total': (lambda: DERIVED['v3_sk_cells'][0]() + DERIVED['v4_v0_cells'][0](), [V3ALG, P['v4']]),
    'v3_a1_largest': (lambda: sum(1 for v in _v3_amp().values() if max(v, key=lambda k: v[k]['a']) == '1'), V3GATES),
    'v3_a_cells': (lambda: len(_v3_amp()), V3GATES),
    'v34_a1_largest_total': (lambda: DERIVED['v3_a1_largest'][0]() + DERIVED['v4_v0_a1_largest'][0](), V3GATES + [P['v4']]),
    'v34_a_cells_total': (lambda: DERIVED['v3_a_cells'][0]() + DERIVED['v4_v0_a1_evaluable'][0](), V3GATES + [P['v4']]),
    'v2_r1_domains': (lambda: len(get(read(P['v2']), 'R1/observed')), [P['v2']]),
    't1_p1_holds': (lambda: sum(x['holds'] for x in read(VT)['T1_1']), [VT]),
    't1_p1_cases': (lambda: len(read(VT)['T1_1']), [VT]),
    't2b_agree': (lambda: sum(v['agree'] for v in read(VT)['T2']['b'].values()), [VT]),
    't2b_n': (lambda: sum(v['n'] for v in read(VT)['T2']['b'].values()), [VT]),
    't2a_worst': (lambda: sum(v['worst_is_predicted'] for k, v in read(VT)['T2']['a'].items() if k.endswith('per_dim')), [VT]),
    't2a_ranks': (lambda: sum(v['ranks'] for k, v in read(VT)['T2']['a'].items() if k.endswith('per_dim')), [VT]),
    'v7_a1_n1_min': (lambda: min(v['plus_N_over_1'] for v in read(V7R)['A']['A1'].values()), [V7R]),
    'v7_a1_n1_max': (lambda: max(v['plus_N_over_1'] for v in read(V7R)['A']['A1'].values()), [V7R]),
    'v7_a1_alt_min': (lambda: min(v['alt_over_plus_2N'] for v in read(V7R)['A']['A1'].values()), [V7R]),
    'v7_a1_alt_max': (lambda: max(v['alt_over_plus_2N'] for v in read(V7R)['A']['A1'].values()), [V7R]),
    'v7_a2_cyc_min': (lambda: min(v['cycle_sum_ratio_median'] for v in read(V7R)['A']['A2'].values()), [V7R]),
    'v7_a2_cyc_max': (lambda: max(v['cycle_sum_ratio_median'] for v in read(V7R)['A']['A2'].values()), [V7R]),
    'v7_a2_dev_min': (lambda: min(v['train_template_dev']['cycle_sum_ratio_median'] for v in read(V7R)['A']['A2'].values()), [V7R]),
    'v7_a2_dev_max': (lambda: max(v['train_template_dev']['cycle_sum_ratio_median'] for v in read(V7R)['A']['A2'].values()), [V7R]),
    'v7_a3_max': (lambda: max(v['R2N']['rate'] for v in read(V7R)['A']['A3'].values()), [V7R]),
    'v8_e1_slot_P_min': (lambda: _e1('slot', 'P', min), [E1]),
    'v8_e1_slot_P_max': (lambda: _e1('slot', 'P', max), [E1]),
    'v8_e1_slot_M_min': (lambda: _e1('slot', 'M', min), [E1]),
    'v8_e1_slot_M_max': (lambda: _e1('slot', 'M', max), [E1]),
    'v8_e1_slot_Pinv_min': (lambda: _e1('slot', 'Pinv', min), [E1]),
    'v8_e1_slot_Pinv_max': (lambda: _e1('slot', 'Pinv', max), [E1]),
    'v8_e1_rrr_P_min': (lambda: _e1('rrr', 'P', min), [E1]),
    'v8_e1_rrr_P_max': (lambda: _e1('rrr', 'P', max), [E1]),
    'v8_e1_rrr_M_min': (lambda: _e1('rrr', 'M', min), [E1]),
    'v8_e1_rrr_M_max': (lambda: _e1('rrr', 'M', max), [E1]),
    'v8_e1_rrr_Pinv_min': (lambda: _e1('rrr', 'Pinv', min), [E1]),
    'v8_e1_rrr_Pinv_max': (lambda: _e1('rrr', 'Pinv', max), [E1]),
    'v9_b1a_r1_max': (lambda: max(_b9(r)['B1a']['R1'] for r in _b9all()), [P9R]), 'v9_b1b_x0_min': (lambda: min(_b9(r)['B1b']['R1_x0'] for r in _b9all()), [P9R]),
    'v9_b1b_other_max': (lambda: max(_b9(r)['B1b']['R1_other'] for r in _b9all()), [P9R]), 'v9_b1c_min': (lambda: min(_b9(r)['B1c']['R2N'] for r in _b9all()), [P9R]),
    'v9_lc1_r1_min': (lambda: min(_b9(r)['B2']['LoReFTC1']['median']['R1'] for r in _b9all()), [P9R]), 'v9_lc1_r2_max': (lambda: max(_b9(r)['B2']['LoReFTC1']['median']['R2'] for r in _b9all()), [P9R]),
    'v9_lc1_d_min': (lambda: min(_b9(r)['B2']['LoReFTC1']['median']['D'] for r in _b9all()), [P9R]), 'v9_lc1_r2n_max': (lambda: max(_b9(r)['B2']['LoReFTC1']['median']['R2N'] for r in _b9all()), [P9R]),
    'v9_lc3_min_kept': (lambda: min(_b9(r)['B2']['LoReFTC3U4']['median_R2N'] for r in _b9all() if r != ('t5', 'month')), [P9R]),
    'v9_lc3_t5_month': (lambda: _b9(('t5', 'month'))['B2']['LoReFTC3U4']['median_R2N'], [P9R]),
    'v9_b3_r2_max': (lambda: max(m['R2'] for r in _b9all() for m in _b9(r)['B3']['median'].values()), [P9R]), 'v9_b3_d_min': (lambda: min(m['D'] for r in _b9all() for m in _b9(r)['B3']['median'].values()), [P9R]),
    'v9_b3_r2n_max': (lambda: max(m['R2N'] for r in _b9all() for m in _b9(r)['B3']['median'].values()), [P9R]),
    'v9_b4_admitted': (lambda: sum(len(x['admitted']) for r in _b9all() for x in _b9(r)['B4']['editors'].values()), [P9R]),
    'v9_b4_trained': (lambda: sum(len(x['seeds']) for r in _b9all() for x in _b9(r)['B4']['editors'].values()), [P9R]),
    'v9_b4_u8_bart_wd': (lambda: _b9(('bart', 'weekday'))['B4']['editors']['U8']['median_admitted'], [P9R]),
    'v9_b4_r4n_max': (lambda: max((x['R4N_max_admitted'] or 0) for r in _b9all() for x in _b9(r)['B4']['editors'].values()), [P9R]),
    'v9_b5_t0_min': (lambda: min(read(P9R)['B'][bb][d]['B5']['R2N'] for bb in ('bart', 't5') for d in ('weekday', 'month')), [P9R]),
    'v9_b5_nat_min': (lambda: min(read(P9R)['B'][bb]['month-nat']['B5']['R2N'] for bb in ('bart', 't5')), [P9R]),
    'v9_s_c1_r2_max': (lambda: max([x['R2'] for r in _s9() for x in r['C1']['seeds'].values()] + [v for r in _s9() for v in r['v5_seeds']['C1_R2'].values()]), [P9R]),
    'v9_s_c3_min': (lambda: min([x['R2N'] for r in _s9() for x in r['C3U4']['seeds'].values()] + [v for r in _s9() for v in r['v5_seeds']['C3U4_R2N'].values()]), [P9R]),
    'v9_s_cells': (lambda: len(_s9()), [P9R]),
    'v9_do_r2n': (lambda: _do9()['DO1a']['R2N'], [P9R]), 'v9_do_rstar': (lambda: _do9()['DO1a']['rstar_pred'], [P9R]),
    'v9_do_f1p': (lambda: _do9()['DO2']['observed']['F1_plus'], [P9R]), 'v9_do_f1a': (lambda: _do9()['DO2']['observed']['F1_alt'], [P9R]),
    'v9_do_c1_r2': (lambda: _do9()['DO4']['R2'], [P9R]), 'v9_do_c1_d': (lambda: _do9()['DO4']['D'], [P9R]), 'v9_do_c3': (lambda: _do9()['DO5']['R2N'], [P9R]),
    'v9_do_agree': (lambda: _do9()['DO6']['agreement'], [P9R]), 'v9_do_naive': (lambda: _do9()['DO6']['naive'], [P9R]),
    'v9_b6_bart_re': (lambda: read(P9R)['B6']['bart']['month']['reencode']['seconds_per_step'], [P9R]), 'v9_b6_bart_lat': (lambda: read(P9R)['B6']['bart']['month']['latent']['seconds_per_step'], [P9R]),
    'v9_b6_t5_re': (lambda: read(P9R)['B6']['t5']['month']['reencode']['seconds_per_step'], [P9R]), 'v9_b6_t5_lat': (lambda: read(P9R)['B6']['t5']['month']['latent']['seconds_per_step'], [P9R]),
    'v9_b6_r2n_min': (lambda: min(v['reencode']['R2N'] for bb in ('bart', 't5') for v in read(P9R)['B6'][bb].values()), [P9R]),
    'v9_p9a_const_min': (lambda: min(v['constant_share_median'] for v in read(P9A).values()), [P9A]),
    'v9_p9a_cos_hi': (lambda: max(v['cos_canonical_abs_median'] for v in read(P9A).values()), [P9A]),
    'v9_p9a_null_hi': (lambda: max(v['null_cos_abs_median'] for v in read(P9A).values()), [P9A]), 'v9_p9a_null_lo': (lambda: min(v['null_cos_abs_median'] for v in read(P9A).values()), [P9A]),
    'v9_p9a_src_min': (lambda: min(v['probe']['source'] for v in read(P9A).values()), [P9A]), 'v9_p9a_tgt_max': (lambda: max(v['probe']['target'] for v in read(P9A).values()), [P9A]),
    'v9_p9b_ell_lo': (lambda: min(x['ellipticity_median'] for v in read(P9B).values() for x in v['natural'].values() if 'ellipticity_median' in x), [P9B]),
    'v9_p9b_ang_hi': (lambda: max(x['angle_dev_median_rad'] for v in read(P9B).values() for k, x in v['natural'].items() if k == '1'), [P9B]),
    'v9_p9b_scr_ang_lo': (lambda: min(v['scrmax']['1']['angle_dev_median_rad'] for v in read(P9B).values() if '1' in v.get('scrmax', {})), [P9B]),
    'v9_p9b_f1share_lo': (lambda: min(v['natural']['1']['energy_share_median'] for v in read(P9B).values()), [P9B]), 'v9_p9b_f1share_hi': (lambda: max(v['natural']['1']['energy_share_median'] for v in read(P9B).values()), [P9B]),
    'v9_p9c_v5_bart': (lambda: read(P9C)['v5_L/bart']['per_world']['latent_minus_majority']['diff'], [P9C]), 'v9_p9c_v5_t5': (lambda: read(P9C)['v5_L/t5']['per_world']['latent_minus_majority']['diff'], [P9C]),
    'v9_p9c_v5_lo': (lambda: min(read(P9C)[k]['per_world']['latent_minus_majority']['ci95'][0] for k in ('v5_L/bart', 'v5_L/t5')), [P9C]),
    'v9_p9c_nat_t5': (lambda: read(P9C)['v8_N/t5']['per_world']['latent_minus_majority']['diff'], [P9C]), 'v9_p9c_nat_t5_lo': (lambda: read(P9C)['v8_N/t5']['per_world']['latent_minus_majority']['ci95'][0], [P9C]),
    'v9_p9c_lb_lo': (lambda: min(v['learned_baseline']['accuracy'] for v in read(P9C).values() if isinstance(v, dict) and 'learned_baseline' in v), [P9C]),
    'v9_p9c_lb_hi': (lambda: max(v['learned_baseline']['accuracy'] for v in read(P9C).values() if isinstance(v, dict) and 'learned_baseline' in v), [P9C]),
    'v9_p9d_v5_min': (lambda: min(read(P9D)[k]['min'] for k in ('v5_L_CE/bart', 'v5_L_CE/t5')), [P9D]), 'v9_p9d_v8_min': (lambda: min(v['min'] for k, v in read(P9D).items() if k.startswith('v8')), [P9D]),
    'v8_n1_bart': (lambda: _n8('bart')['N1']['R2N'], [P8]), 'v8_n1_t5': (lambda: _n8('t5')['N1']['R2N'], [P8]),
    'v8_n2_bart': (lambda: _n8('bart')['N2']['R2N'], [P8]), 'v8_n2_t5': (lambda: _n8('t5')['N2']['R2N'], [P8]),
    'v8_n3_r1_min': (lambda: min(_n8(b)['N3']['R1'] for b in ('bart', 't5')), [P8]), 'v8_n3_r2_max': (lambda: max(_n8(b)['N3']['R2'] for b in ('bart', 't5')), [P8]),
    'v8_n3_d_min': (lambda: min(_n8(b)['N3']['D'] for b in ('bart', 't5')), [P8]),
    'v8_n4_f1p_bart': (lambda: _n8('bart')['N4']['observed']['F1_plus'], [P8]), 'v8_n4_f1p_t5': (lambda: _n8('t5')['N4']['observed']['F1_plus'], [P8]),
    'v8_n4_f1a_min': (lambda: min(_n8(b)['N4']['observed']['F1_alt'] for b in ('bart', 't5')), [P8]),
    'v8_n4_fn_max': (lambda: max(_n8(b)['N4']['observed']['Fnot1_plus'] for b in ('bart', 't5')), [P8]),
    'v8_n5_bart': (lambda: _n8('bart')['N5']['latent'], [P8]), 'v8_n5_t5': (lambda: _n8('t5')['N5']['latent'], [P8]),
    'v8_n5_naive_bart': (lambda: _n8('bart')['N5']['naive'], [P8]), 'v8_n5_naive_t5': (lambda: _n8('t5')['N5']['naive'], [P8]),
    'v8_n5_maj_bart': (lambda: _n8('bart')['N5']['majority_reference'], [P8]), 'v8_n5_maj_t5': (lambda: _n8('t5')['N5']['majority_reference'], [P8]),
    'v8_n_worlds': (lambda: read(N8G)['pools']['confirm8']['kept'], [N8G]),
    'v8_g1_r2_max': (lambda: max(v['G1']['R2'] for v in read(P8)['G']['domains'].values()), [P8]),
    'v8_g2_rstar_wd': (lambda: read(P8)['G']['domains']['weekday']['G2']['rstar_pred'], [P8]), 'v8_g2_rstar_mo': (lambda: read(P8)['G']['domains']['month']['G2']['rstar_pred'], [P8]),
    'v8_g2_r9_mo': (lambda: _g8c('month/RRR9/plus'), [P8]), 'v8_g2_r10_mo': (lambda: _g8c('month/RRR10/plus'), [P8]),
    'v8_g_ff9_mo': (lambda: _g8c('month/FF9/plus'), [P8]), 'v8_g_ff10_mo': (lambda: _g8c('month/FF10/plus'), [P8]),
    'v8_g6_min': (lambda: min(v['G6']['R2N'] for v in read(P8)['G']['domains'].values()), [P8]),
    'v8_g5_agree': (lambda: read(P8)['G']['G5']['prediction']['latent'], [P8]), 'v8_g5_naive': (lambda: read(P8)['G']['G5']['prediction']['naive'], [P8]),
    'v8_g5_dsep_n': (lambda: read(P8)['G']['G5']['D_separation']['n'], [P8]),
    'v8_ll_month16': (lambda: read(P8)['ladder']['t5_ll']['cells']['month/F_empty/plus']['obs_rate'], [P8]),
    'v8_bb_month_recon': (lambda: read('experiments/composability_mechanisms_v7/results/g_prep_t5_bb.json')['domains']['month']['reconstruction']['rate'], ['experiments/composability_mechanisms_v7/results/g_prep_t5_bb.json']),
    'v8_d_layer': (lambda: read(D8)['primary'], [D8]),
    'v8_d_rstar': (lambda: min(int(k[4:].split('/')[0]) for k, v in read(D8)['layer10']['cells'].items() if k.startswith('SRRR') and v['R2N'] >= .95), [D8]),
    'v8_d_f1p': (lambda: read(D8)['layer10']['cells']['F_{1}/plus']['R2N'], [D8]), 'v8_d_f1a': (lambda: read(D8)['layer10']['cells']['F_{1}/alt']['R2N'], [D8]),
    'v8_d_c1_r2_max': (lambda: max(v['R2'] for k, v in read(D8)['layer10']['cells'].items() if k.startswith('C1_')), [D8]),
    'v8_d_c1_d_min': (lambda: min(v['D'] for k, v in read(D8)['layer10']['cells'].items() if k.startswith('C1_')), [D8]),
    'v8_d_agree_min': (lambda: min(v['agree'] for k, v in read(D8)['layer10']['cells'].items() if not k.startswith('C1_')), [D8]),
    'v8_e2_r30_max': (lambda: max(v['R30'] for v in read(E28)['_summary'].values()), [E28]),
    'v8_e2_d100_r32_lo': (lambda: min(read(E28)[f'OR32/s{s}']['distance'][99] for s in (42, 43, 44)), [E28]),
    'v8_e2_d100_r32_hi': (lambda: max(read(E28)[f'OR32/s{s}']['distance'][99] for s in (42, 43, 44)), [E28]),
    'v8_e2_d100_full_lo': (lambda: min(read(E28)[f'ORfull/s{s}']['distance'][99] for s in (42, 43, 44)), [E28]),
    'v8_e2_d100_full_hi': (lambda: max(read(E28)[f'ORfull/s{s}']['distance'][99] for s in (42, 43, 44)), [E28]),
    'v8_e2b_dir_min': (lambda: min(v['direction_1-8'] for v in read(E2B)['_summary'].values()), [E2B]),
    'v7_a_combos': (lambda: len(read(V7R)['A']['A1']), [V7R]),
    'v7_k_survivors': (lambda: len(_k7_surv()), [V7R]),
    'v7_k_dist10_med': (lambda: float(np.median([_k7_cont(s)[9] for s in range(42, 50)])), [V7R]),
    'v7_k_dist30_min': (lambda: min(_k7_cont(s)[29] for s in _k7_surv()), [V7R]),
    'v7_k_dist30_max': (lambda: max(_k7_cont(s)[29] for s in _k7_surv()), [V7R]),
    'v7_k_dist100_min': (lambda: min(_k7_cont(s)[99] for s in _k7_surv()), [V7R]),
    'v7_k_dist100_max': (lambda: max(_k7_cont(s)[99] for s in _k7_surv()), [V7R]),
    'v7_k_l1next_min': (lambda: min(read(V7R)['K']['exploratory'][f'attention/Att2LU8_s{s}']['layer1']['next'] for s in _k7_surv()), [V7R]),
    'v7_k_l1next_count': (lambda: sum(1 for k, v in read(V7R)['K']['exploratory'].items() if k.startswith('attention/Att2LU8_') and v['layer1']['next'] >= .85), [V7R]),
    'v7_k_l1next_max': (lambda: max(read(V7R)['K']['exploratory'][f'attention/Att2LU8_s{s}']['layer1']['next'] for s in _k7_surv()), [V7R]),
    'v7_k5_r100_max': (lambda: max(read(V7R)['K']['table']['bind3/Att2LU8/R100'].values()), [V7R]),
    'rounds_locked': (lambda: sum(1 for f in LOCK.values() if (REPO / f).exists()), list(LOCK.values())),
    'v4_p5_t5_rel_min': (lambda: min(v['classes']['relative'] for k, v in read(P5T).items() if k.endswith('/median')), [P5T]),
    'v4_p5_bart_other_rel_max': (lambda: max(v['classes']['relative'] for k, v in read(P5B).items() if k.endswith('/median') and k.split('/')[0] not in ('weekday', 'month')), [P5B]),
    'v2_reuse_min_pct': (lambda: 100 * min(v['confirm2_worlds_with_text_in_v1_train_dev'] / v['confirm2_worlds'] for v in read(V3AUD)['v2_confirm2_text_reuse_report'].values()), [V3AUD]),
    'v2_reuse_max_pct': (lambda: 100 * max(v['confirm2_worlds_with_text_in_v1_train_dev'] / v['confirm2_worlds'] for v in read(V3AUD)['v2_confirm2_text_reuse_report'].values()), [V3AUD]),
    'gpu_total': (lambda: sum(read(f'experiments/{d}/run_ledger.json')['total_gpu_hours'] for d in ROUND_DIRS), [f'experiments/{d}/run_ledger.json' for d in ROUND_DIRS]),
    'v7_p1_precfail_min': (lambda: min(v['prec_pred_fail'] for k, v in read(V7P)['P1_by_domain'].items() if not k.endswith('/all')), [V7P]),
    'v7_p1_precfail_max': (lambda: max(v['prec_pred_fail'] for k, v in read(V7P)['P1_by_domain'].items() if not k.endswith('/all')), [V7P]),
    'v7_p1_over_total': (lambda: sum(v['over'] for k, v in read(V7P)['P1_by_domain'].items() if k.endswith('/all')), [V7P]),
    'v7_p1_under_total': (lambda: sum(v['under'] for k, v in read(V7P)['P1_by_domain'].items() if k.endswith('/all')), [V7P]),
    'v7_p2_prev_min': (lambda: 100 * min(_p2_rb('prev')), [V7P]),
    'v7_p2_prev_max': (lambda: 100 * max(_p2_rb('prev')), [V7P]),
    'v7_p2_start_min': (lambda: 100 * min(v['start'] for k, v in read(V7P)['P2'].items() if k.startswith('v6M/') and '/F_{1}/' in k and k.rsplit('/', 1)[1] in ('plus', 'minus')), [V7P]),
    'v7_p2_start_max': (lambda: 100 * max(v['start'] for k, v in read(V7P)['P2'].items() if k.startswith('v6M/') and '/F_{1}/' in k and k.rsplit('/', 1)[1] in ('plus', 'minus')), [V7P]),
    'v6_probes_total': (lambda: sum(read('experiments/composability_mechanisms_v5/results/calib_ctx_bart.json')['domains'][d]['probes'] for d in ('weekday', 'month')), ['experiments/composability_mechanisms_v5/results/calib_ctx_bart.json']),
    'v6_tmpl_used_weekday': (lambda: _v6_tmpl('weekday-mt', 10), [V6AUD]),
    'v6_tmpl_used_month': (lambda: _v6_tmpl('month-mt', 10), [V6AUD]),
    'v6_tmpl_used_hour': (lambda: _v6_tmpl('hour-mt', 10), [V6AUD]),
    'v6_tmpl_sparse': (lambda: sum(len(read(V6AUD)['domains'][d]['templates']) - _v6_tmpl(d, 10) for d in ('weekday-mt', 'month-mt', 'hour-mt')), [V6AUD]),
    'v6_tmpl_sparse_max_worlds': (lambda: max(n for d in ('weekday-mt', 'month-mt', 'hour-mt') for n in read(V6AUD)['domains'][d]['templates'].values() if n < 10), [V6AUD]),
    'v5_l3_state_cells': (lambda: sum(1 for v in get(read(P['v5']), 'L/L3/cells').values() if v['family'] != 'CE' and v['D'] is not None), [P['v5']]),
    'v5_f_rrr_max': (lambda: max(v['RRR'] for v in get(read(P['v5']), 'F/cells').values()), [P['v5']]),
    'v5_f_ff_min': (lambda: min(v['FF'] for v in get(read(P['v5']), 'F/cells').values()), [P['v5']]),
    'v2_a2_scrambled_composable': (lambda: sum(1 for k, v in get(read(P['v2']), 'A2/observed').items() if '/scr' in k and v['R_2N'] >= .90), [P['v2']]),
    'v2_a2_scrambled_total': (lambda: sum(1 for k in get(read(P['v2']), 'A2/observed') if '/scr' in k), [P['v2']]),
    'v5_d_up': (lambda: sum(1 for v in get(read(P['v5']), 'D/cells').values() if v['std'] != v['ideal'] and v['dcp_R'] > v['std_R'] + .05), [P['v5']]),
    'v5_d_c': (lambda: sum(1 for v in get(read(P['v5']), 'D/cells').values() if v['std'] != v['ideal']), [P['v5']]),
}


def main():
    require_slurm(); cm = yaml.safe_load((PAPER / 'claim_map.yaml').read_text()); out = []; tex = ['% generated by paper/scripts/build_claims.py from the locked results; do not edit']
    locks = {r: read(f)['lock_commit'] if (REPO / f).exists() else None for r, f in LOCK.items()}
    for c in cm['claims']:
        rounds = sorted({p.split('/')[0] for p in c.get('predictions', []) + c.get('counter_predictions', [])}); nums = []; files = set()
        for n in c.get('numbers', []):
            name = macro_name(n['macro']); src = n.get('file')
            try:
                if 'derived' in n: fn, fs = DERIVED[n['derived']]; v = fn(); files.update(fs); src = f"derived:{n['derived']}"
                else: v = get(read(n['file']), n['path']); files.add(n['file'])
                if 'scale' in n: v = v * n['scale']
                txt = n['fmt'].format(v); pend = False
            except (FileNotFoundError, KeyError):
                if not n.get('pending'): raise
                v, txt, pend = None, None, True
            nums.append(dict(macro=name, value=v, text=txt, source=src, path=n.get('path'), note=n.get('note'), pending=pend))
            tex.append(f'\\newcommand{{\\{name}}}{{\\TODO{{v6}}}}' if pend else f'\\newcommand{{\\{name}}}{{{txt}}}')
        out.append(dict(id=c['id'], zh=c['zh'], en=c['en'], nature=c['nature'], predictions=c.get('predictions', []),
                        counter_predictions=c.get('counter_predictions', []), exploratory_sources=c.get('exploratory_sources', []), figures=c.get('figures', []),
                        lock_commits={r: locks.get(r) for r in rounds}, evidence={f: sha(f) for f in sorted(files)}, numbers=nums))
    (PAPER / 'claims.yaml').write_text(yaml.safe_dump(dict(generated_by='paper/scripts/build_claims.py', lock_commits=locks, claims=out), allow_unicode=True, sort_keys=False))
    (PAPER / 'generated').mkdir(exist_ok=True); (PAPER / 'generated/numbers.tex').write_text('\n'.join(tex) + '\n')
    print('claims', len(out), 'numbers', sum(len(c['numbers']) for c in out), 'pending', sum(n['pending'] for c in out for n in c['numbers']), flush=True)


if __name__ == '__main__':
    main()
