"""W1 + W2 (CPU): resolve every number of claim_map.yaml from the locked results; write paper/claims.yaml and paper/generated/numbers.tex.
Numbers are read (file + JSON path) or computed by a named derivation below from locked files only; nothing is copied by hand. Each claim
records its evidence files (SHA256), the lock commit of every round it cites, and its numbers with their sources. Numbers marked pending
(v6 not merged yet) become \\TODO{v6} macros."""
import sys
import yaml
from common import *

LOCK = {r: f'experiments/{d}/protocol_lock.json' for r, d in (('v1', 'symmetry_composability_v1'), ('v2', 'composability_mechanisms_v1'), ('v3', 'composability_mechanisms_v2'),
                                                             ('v4', 'composability_mechanisms_v3'), ('v5', 'composability_mechanisms_v4'), ('v6', 'composability_mechanisms_v5'))}
P = {r: f'experiments/{d}/results/predictions.json' for r, d in (('v2', 'composability_mechanisms_v1'), ('v3', 'composability_mechanisms_v2'), ('v4', 'composability_mechanisms_v3'),
                                                                ('v5', 'composability_mechanisms_v4'))}
P['v1'] = 'experiments/symmetry_composability_v1/results/e1_predictions.json'
V5 = 'experiments/composability_mechanisms_v4'
V3ALG = 'experiments/composability_mechanisms_v2/results/algebra.json'
V3GATES = [f'experiments/composability_mechanisms_v2/results/gates_{b}.json' for b in ('bart', 't5')]
V6AUD = 'experiments/composability_mechanisms_v5/data/audit.json'


def _v3_sk():
    """v3 exploratory analysis _s_k_vs_entry_order: per-plane update energy s_k of the full-rank operator, per backbone / domain."""
    a = read(V3ALG)['_s_k_vs_entry_order']; return {k: v for k, v in a.items() if isinstance(v, dict) and 's_k' in v}


def _v3_amp():
    """v3 pre-lock gate files: per-plane amplitude a_k and one-step change s_k of the canonical slot code, per backbone / domain."""
    return {f'{b}/{d}': v for f in V3GATES for b in [f.split('_')[-1][:-5]] for d, v in read(f)['amplitudes'].items()}


def _v6_tmpl(d, k):
    """v6 confirm6: number of held-out templates of a multi-template domain with at least k worlds after deduplication."""
    return sum(1 for n in read(V6AUD)['domains'][d]['templates'].values() if n >= k)


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
        rounds = sorted({p.split('/')[0] for p in c.get('predictions', [])}); nums = []; files = set()
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
        out.append(dict(id=c['id'], zh=c['zh'], en=c['en'], nature=c['nature'], predictions=c.get('predictions', []), figures=c.get('figures', []),
                        lock_commits={r: locks.get(r) for r in rounds}, evidence={f: sha(f) for f in sorted(files)}, numbers=nums))
    (PAPER / 'claims.yaml').write_text(yaml.safe_dump(dict(generated_by='paper/scripts/build_claims.py', lock_commits=locks, claims=out), allow_unicode=True, sort_keys=False))
    (PAPER / 'generated').mkdir(exist_ok=True); (PAPER / 'generated/numbers.tex').write_text('\n'.join(tex) + '\n')
    print('claims', len(out), 'numbers', sum(len(c['numbers']) for c in out), 'pending', sum(n['pending'] for c in out for n in c['numbers']), flush=True)


if __name__ == '__main__':
    main()
