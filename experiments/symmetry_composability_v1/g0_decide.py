"""G0 machine decision from E0.1-E0.3, plus a synthetic self-test of the geometry metrics."""
import time
from symutil import *


def synthetic(kind, W=40, S=7, d=768, noise=.002, seed=7):
    rng = np.random.default_rng(seed)
    if kind == 'cyclic':
        x = np.arange(S)[:, None]; ks = np.arange(1, 3)[None, :]
        base = np.concatenate([np.cos(2 * np.pi * x * ks / S) * [1., .5], np.sin(2 * np.pi * x * ks / S) * [1., .5]], 1)
    elif kind == 'open':
        K = np.exp(-np.abs(np.arange(S)[:, None] - np.arange(S)[None, :]) / 2.); base = np.linalg.cholesky(K)
    else:
        base = None
    V = np.zeros((W, S, d))
    for w in range(W):
        Q, _ = np.linalg.qr(rng.standard_normal((d, S + 4)))
        pts = rng.standard_normal((S, S + 4)) if base is None else np.pad(base, ((0, 0), (0, S + 4 - base.shape[1])))
        V[w] = pts @ Q.T + noise * rng.standard_normal((S, d)) + rng.standard_normal(d)
    return V


def selftest():
    out = {}
    pairs_c = [(i, (i + 1) % 7) for i in range(7)]; pairs_o = [(i, i - 1) for i in range(1, 7)]
    r, _, _ = geometry_report(synthetic('cyclic'), list(range(7)), pairs_c, 'cyclic', name='syn_cyclic')
    out['cyclic_Z7'] = dict(E_iso=r['E_iso']['mean'], below_q05=r['E_iso_below_null_q05'], R2=r['R2_G'], R2_above_q95=r['R2_G_above_null_q95'])
    r, _, _ = geometry_report(synthetic('open'), list(range(7)), pairs_o, 'open', name='syn_open')
    out['open_toeplitz7'] = dict(E_iso=r['E_iso']['mean'], below_q05=r['E_iso_below_null_q05'], R2=r['R2_G'], R2_above_q95=r['R2_G_above_null_q95'])
    r, _, _ = geometry_report(synthetic('random'), list(range(7)), pairs_o, 'open', name='syn_random')
    out['random'] = dict(E_iso=r['E_iso']['mean'], null_frac_le=r['E_iso_null']['frac_le'], R2_null_frac_ge=r['R2_G_null']['frac_ge'])
    out['pass'] = bool(out['cyclic_Z7']['E_iso'] < .05 and out['cyclic_Z7']['below_q05'] and out['cyclic_Z7']['R2_above_q95']
                       and out['open_toeplitz7']['E_iso'] < .05 and out['open_toeplitz7']['below_q05'] and out['open_toeplitz7']['R2_above_q95']
                       and .05 < out['random']['null_frac_le'] < .95)
    return out


def main():
    require_slurm(); t0 = time.time()
    geo = read(ROOT / 'results/e0_geometry.json'); ops = read(ROOT / 'results/e0_operators.json'); wr = read(ROOT / 'results/e0_writes.json')
    st = selftest(); assert st['pass'], st
    t = geo['time_t0']; diff = geo['time_segment_minus_person']
    a = dict(time7_E_iso=t['E_iso']['mean'], time7_E_iso_null_q05=t['E_iso_null']['null_q05'], time7_E_iso_null_quantile=t['E_iso_null']['frac_le'],
             time7_E_iso_pass=bool(t['E_iso_below_null_q05']),
             time7_R2=t['R2_G'], time7_R2_null_q95=t['R2_G_null']['null_q95'], time7_R2_null_quantile=1 - t['R2_G_null']['frac_ge'],
             time7_R2_pass=bool(t['R2_G_above_null_q95']),
             segment_E_iso=geo['time_t0_segment']['E_iso'], person_E_iso=geo['person_t0']['E_iso'],
             segment_minus_person=diff, segment_lt_person_pass=bool(diff['ci95'][1] < 0))
    a['pass'] = a['time7_E_iso_pass'] and a['time7_R2_pass'] and a['segment_lt_person_pass']
    pair = next(c for c in wr['canonical']['adjacent'] if c['first'] == '+1->+0' and c['second'] == '+0->-1')
    b = dict(pooled_cos=pair['pooled_cos'], token_cos=wr['canonical']['aligned_pair_token_cos'], pass_=bool(pair['pooled_cos']['ci95'][1] < .5))
    E = lambda k: ops[k]['e_inv']['mean_both']; I = lambda k: ops[k]['ISO_mean']
    seeds = (42, 43, 44, 45, 46)
    per = [dict(seed=s, e_inv_C1=E(f'time/C1/s{s}'), e_inv_C3=E(f'time/C3/s{s}'), ISO_C1=I(f'time/C1/s{s}'), ISO_C3=I(f'time/C3/s{s}'),
                e_inv_C3_lt_C1=E(f'time/C3/s{s}') < E(f'time/C1/s{s}'), ISO_C3_lt_C1=I(f'time/C3/s{s}') < I(f'time/C1/s{s}'),
                both_directions_C3_lt_C1=all(ops[f'time/C3/s{s}']['e_inv'][d]['world_mean']['mean'] < ops[f'time/C1/s{s}']['e_inv'][d]['world_mean']['mean'] for d in ('minus_o_plus', 'plus_o_minus')))
           for s in seeds]
    rrr = E('time/RRR16')
    c = dict(per_seed=per, e_inv_RRR16=rrr, RRR16_lt_all_C1=all(rrr < p['e_inv_C1'] for p in per),
             e_inv_C3_lt_C1_all_seeds=all(p['e_inv_C3_lt_C1'] for p in per), ISO_C3_lt_C1_count=sum(p['ISO_C3_lt_C1'] for p in per))
    c['pass'] = c['e_inv_C3_lt_C1_all_seeds'] and c['RRR16_lt_all_C1'] and c['ISO_C3_lt_C1_count'] >= 4
    decision = a['pass'] and (b['pass_'] or c['pass'])
    out = dict(decision='pass' if decision else 'fail', a_geometry=a, b_curvature=b, c_group_law=c, metric_selftest=st,
               rule='(a) and ((b) or (c)); e_inv = mean of world-mean e_inv(T- o T+) and e_inv(T+ o T-)', seconds=time.time() - t0,
               inputs={k: sha(ROOT / f'results/{k}') for k in ('e0_geometry.json', 'e0_operators.json', 'e0_writes.json')})
    if '--amended' in sys.argv:  # AMENDMENT_01: (a) -> G1a (decided in E1.2); (c3) ISO dropped; rule (b) or (c1 and c2)
        c2 = c['e_inv_C3_lt_C1_all_seeds'] and c['RRR16_lt_all_C1']
        dec = b['pass_'] or c2
        dump('results/g0_amended_decision.json', dict(decision='pass' if dec else 'fail', amendment='AMENDMENT_01.md',
             amendment_sha256=sha(ROOT / 'AMENDMENT_01.md'), rule='(b) or ((c1) and (c2)); geometry gate moved to G1a in E1.2; ISO reported only',
             b_curvature_pass=b['pass_'], c_amended_pass=c2, original_decision=read(ROOT / 'results/g0_decision.json')['decision'],
             original_decision_sha256=sha(ROOT / 'results/g0_decision.json'), b_curvature=b, c_group_law=c, metric_selftest=st, inputs=out['inputs']))
        print('G0 amended', 'pass' if dec else 'fail', flush=True); return
    dump('results/g0_decision.json', out)
    print('G0', out['decision'], 'a', a['pass'], 'b', b['pass_'], 'c', c['pass'], flush=True)


if __name__ == '__main__':
    main()
