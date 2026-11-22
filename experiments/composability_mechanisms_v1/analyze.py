"""Analysis (CPU): G2-0, A1-A5, B1-B4, R1-R5, M1-M7 by the locked rules; tables and figures."""
import time
from collections import defaultdict
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *
import sym2_semantics as S

CYC = ['weekday', 'month', 'compass', 'egoside']


def load_shards():
    ch = defaultdict(dict); sg = defaultdict(list)
    for f in sorted((ROOT / 'results/shards').glob('*.jsonl')):
        for r in rows(f):
            if f.name.startswith('chain_'):
                ch[r['domain'], r['map'], r['method'], r['path']].setdefault(r['world_id'], {})[r['step']] = (r['trajectory_success'], r['operation'], r['state'], r['score']['success'])
            else:
                sg[r['domain'], r['map'], r['method'], r['template']].append(r['score']['success'])
    return ch, sg


def plus_path(d): return 'plus_from_path_start' if d == 'daysago' else 'plus_from_start'
def N_of(d): return len(S.states(d))
def two_n(d): return 7 if d == 'daysago' else 2 * N_of(d)


def main():
    require_slurm(); p = verify_protocol2(); S.load_maps(ROOT / 'protocol.json'); t0 = time.time()
    ch, sg = load_shards(); alg = read(ROOT / 'results/algebra.json'); s3 = read(ROOT / 'results/s3_mechanism.json'); s2m = read(ROOT / 'results/s2_modes.json')
    geo1b = read(ROOT / 'results/s1b_geometry.json'); P = p['predictions']; maps = p['s1a']['maps']
    def R(d, mp, me, path, k):
        ws = ch[d, mp, me, path]; assert len(ws) == 160, (d, mp, me, path, len(ws)); return rate([ws[w][k][0] for w in ws])
    def single(d, mp, me, t=0): return rate(sg[d, mp, me, t])
    out = {}
    # tables
    crow = []
    for (d, mp, me, path), ws in sorted(ch.items()):
        K = max(max(v) for v in ws.values())
        for k in range(1, K + 1):
            r = rate([ws[w][k][0] for w in ws]); crow.append(dict(domain=d, map=mp, method=me, path=path, k=k, R_k=r['rate'], lo=r['ci95'][0], hi=r['ci95'][1]))
    csvwrite('results/chains.csv', crow)
    csvwrite('results/singles.csv', [dict(domain=d, map=mp, method=me, template=t, **single(d, mp, me, t)) for (d, mp, me, t) in sorted(sg)])
    # G2-0
    g_r = {d: R(d, 'natural', 'RRR16', plus_path(d), two_n(d)) for d in V1_DOMAINS}
    g_c = {f'{d}/C1_s{s}': R(d, 'natural', f'C1_s{s}', plus_path(d), 2) for d in V1_DOMAINS for s in p['training']['seeds']}
    out['G2_0'] = dict(RRR16_R2N=g_r, C1_R2=g_c, pass_=all(v['rate'] >= .95 for v in g_r.values()) and all(v['rate'] <= .20 for v in g_c.values()))
    # S1a
    eiso = {(d, 'natural'): p['s1a']['natural_E_iso'][d] for d in V1_DOMAINS}
    for d in V1_DOMAINS:
        for mp, m in maps[d].items(): eiso[d, mp] = m['E_iso']
    r2n = {f'{d}/{mp}': R(d, mp, 'RRR16', plus_path(d), two_n(d)) for (d, mp) in eiso}
    a1 = r2n['egoside/scrmax']['rate']
    out['A1'] = dict(observed=r2n['egoside/scrmax'], verdict='H-slot' if a1 >= .95 else 'H-sym-N' if a1 <= .5 else 'neither')
    scr = {k: v for k, v in r2n.items() if not k.endswith('natural')}
    ks = list(r2n); rho = spearmanr([eiso[tuple(k.split('/'))] for k in ks], [r2n[k]['rate'] for k in ks])[0]
    rho = None if rho != rho else float(rho)
    a2 = 'H-slot' if all(v['rate'] >= .95 for v in scr.values()) else 'H-sym-N' if (rho is not None and rho <= -.5 and min(v['rate'] for v in scr.values()) < .95) else 'neither'
    out['A2'] = dict(observed={k: dict(R_2N=v['rate'], ci95=v['ci95'], E_iso=eiso[tuple(k.split('/'))]) for k, v in r2n.items()}, spearman_rho=rho, verdict=a2)
    diff = {d: R(d, 'natural', 'RRR16', 'plus_from_start', 10 * N_of(d))['rate'] - R(d, 'scrmax', 'RRR16', 'plus_from_start', 10 * N_of(d))['rate'] for d in CYC}
    out['A3'] = dict(observed=diff, verdict='H-slot' if all(v <= .05 for v in diff.values()) else 'H-sym-N' if sum(v >= .2 for v in diff.values()) >= 2 else 'neither')
    other_bad = any(r2n[f'{d}/scrmax']['rate'] <= .5 for d in V1_DOMAINS if d != 'egoside')
    out['Q1'] = dict(verdict='H-slot' if all(out[k]['verdict'] == 'H-slot' for k in ('A1', 'A2', 'A3')) else
                     'H-sym-N' if out['A1']['verdict'] == 'H-sym-N' and other_bad else 'partial')
    a4 = {f'{d}/{mp}': alg[f'{d}/{mp}/RRR16']['plus']['max_phase_dev_deg'] for d in CYC for mp in ('natural', 'scrmax')}
    out['A4'] = dict(observed=a4, pass_=all(v is not None and v < 2 for v in a4.values()))
    a5 = {d: alg[f'{d}/scrmax/RRR16']['plus']['kappa_u'] / alg[f'{d}/natural/RRR16']['plus']['kappa_u'] for d in CYC}
    out['A5'] = dict(observed=a5, kappa_u={f'{d}/{mp}': alg[f'{d}/{mp}/RRR16']['plus']['kappa_u'] for d in V1_DOMAINS for mp in maps[d].keys() | {'natural'}},
                     G={f'{d}/{mp}': alg[f'{d}/{mp}/RRR16']['plus']['G'] for d in V1_DOMAINS for mp in maps[d].keys() | {'natural'}}, pass_=all(v > 1 for v in a5.values()))
    # S1b
    r6 = {d: R(d, 'natural', 'RRR16', 'plus_from_start', 6) for d in S1B_DOMAINS}
    out['B1'] = dict(observed={d: r6[d] for d in ('pron3', 'name3')}, pass_=all(r6[d]['rate'] >= .95 for d in ('pron3', 'name3')))
    b2 = r6['bind3']['rate']; out['B2'] = dict(observed=r6['bind3'], verdict='H-bind' if b2 <= .5 else 'H-geom' if b2 >= .95 else 'neither')
    b3 = {f'{d}/C1_s{s}': R(d, 'natural', f'C1_s{s}', 'plus_from_start', 2) for d in S1B_DOMAINS for s in p['training']['seeds']}
    out['B3'] = dict(observed=b3, pass_=all(v['rate'] <= .2 for v in b3.values()))
    dl = geo1b['B4_pre_lock']['delta']; out['B4'] = dict(observed=geo1b['B4_pre_lock'], verdict='H-bind' if dl <= -.3 else 'H-geom' if abs(dl) < .1 else 'neither', prospective=False)
    out['Q2'] = dict(verdict=out['B2']['verdict'] if out['B2']['verdict'] != 'neither' else 'neither')
    out['S1b_extra'] = {f'{d}/{me}': dict(R30=R(d, 'natural', me, 'plus_from_start', 30)['rate'], R6=R(d, 'natural', me, 'plus_from_start', 6)['rate'],
                                          single_t0=single(d, 'natural', me, 0)['rate'], single_t3=(single(d, 'natural', me, 3)['rate'] if sg.get((d, 'natural', me, 3)) else None))
                        for d in S1B_DOMAINS for me in ['RRR16', 'RRR32', 'reencode'] + [f'{g}_s{s}' for g in ('C1', 'C3') for s in p['training']['seeds']]}
    # S2
    grid = p['s2']['grids']; rk = {}
    for d in V1_DOMAINS:
        for mp in (['natural', 'scrmax'] if d in p['s2']['scrmax_grid_domains'] else ['natural']):
            rk[d, mp] = {r: dict(single=single(d, mp, f'RRR{r}')['rate'], R_N=R(d, mp, f'RRR{r}', plus_path(d), N_of(d) if d != 'daysago' else 7)['rate'],
                                 R_2N=R(d, mp, f'RRR{r}', plus_path(d), two_n(d))['rate'],
                                 alt=R(d, mp, f'RRR{r}', 'alternating_from_path_4th' if d == 'daysago' else 'alternating_from_0', 10 if d == 'daysago' else 2 * N_of(d))['rate'],
                                 harmonics=alg[f'{d}/{mp}/RRR{r}']['plus']['harmonics_present'])
                         for r in sorted(set(grid[d]) | {16, 32})}
    def rstar(tab):
        rs = sorted(tab); ok = [r for r in rs if all(tab[q]['R_2N'] >= .95 for q in rs if q >= r)]; return min(ok) if ok else None
    r1 = {}
    for d in CYC:
        tab = {r: v for r, v in rk[d, 'natural'].items() if r in grid[d]}; rs_ = rstar(tab); N = N_of(d)
        below = [r for r in tab if rs_ is not None and r < rs_]; sharp = (tab[max(below)]['R_2N'] <= .2) if below else True
        r1[d] = dict(r_star=rs_, N_minus_1=N - 1, sharp=sharp, pass_=rs_ is not None and N - 2 <= rs_ <= N and sharp)
    out['R1'] = dict(observed=r1, pass_=all(v['pass_'] for v in r1.values()))
    out['R2'] = dict(observed=dict(month_r8=rk['month', 'natural'][8]['single'], weekday_r4=rk['weekday', 'natural'][4]['single']),
                     pass_=rk['month', 'natural'][8]['single'] >= .95 and rk['weekday', 'natural'][4]['single'] >= .95)
    r3 = {d: rk[d, 'natural'][N_of(d) - 2]['single'] - rk[d, 'scrmax'][N_of(d) - 2]['single'] for d in ('weekday', 'month')}
    out['R3'] = dict(observed=r3, r_star_scrmax={d: rstar({r: v for r, v in rk[d, 'scrmax'].items() if r in grid[d]}) for d in ('weekday', 'month')},
                     pass_=all(v >= .2 for v in r3.values()))
    out['R4'] = {f'{d}/{mp}': {r: v['harmonics'] for r, v in tab.items()} for (d, mp), tab in rk.items()}
    fail = {}
    for r in grid['daysago']:
        for path in ('plus_from_path_start', 'minus_from_path_end'):
            ws = ch['daysago', 'natural', f'RRR{r}', path]; c = defaultdict(int)
            for w, steps in ws.items():
                for k in sorted(steps):
                    if not steps[k][3]:
                        prev = steps[k - 1][2] if k > 1 else ('start'); c[f'{prev}->{steps[k][2]}'] += 1; break
            fail[f'RRR{r}/{path}'] = dict(c)
    out['R5'] = fail
    out['S2_table'] = {f'{d}/{mp}': tab for (d, mp), tab in rk.items()}
    # S3
    cells = {k: v for k, v in s3.items() if '/C1_s' in k}
    med = lambda f: float(np.median([f(v) for v in cells.values()]))
    m1, m2 = med(lambda v: v['M1']['mean']), med(lambda v: v['M2']['median'])
    m3s, m3t = med(lambda v: v['M3']['source']), med(lambda v: v['M3']['target']); m4 = med(lambda v: v['M4_same_world']['rate'])
    probe_ok = all(s3[f'{d}/probe']['dev_accuracy'] >= .99 for d in V1_DOMAINS)
    out['M1'] = dict(median=m1, verdict='H-instr' if m1 >= .9 else 'H-approx' if m1 <= .6 else 'neither')
    out['M2'] = dict(median=m2, verdict='H-instr' if abs(m2) <= .2 else 'H-approx' if m2 >= .5 else 'neither')
    out['M3'] = dict(median_source=m3s, median_target=m3t, probe_dev_accuracy={d: s3[f'{d}/probe']['dev_accuracy'] for d in V1_DOMAINS},
                     verdict=('H-instr' if m3s >= .8 and m3t <= .2 else 'H-approx' if m3t >= .8 else 'neither') if probe_ok else 'not decidable (probe)')
    out['M4'] = dict(median=m4, cross_world_median=med(lambda v: v['M4_cross_world']['rate']), verdict='H-instr' if m4 >= .8 else 'H-approx' if m4 <= .2 else 'neither')
    vs = [out[k]['verdict'] for k in ('M1', 'M2', 'M3', 'M4')]
    out['Q4'] = dict(votes=vs, verdict='H-instr' if vs.count('H-instr') > vs.count('H-approx') and vs.count('H-instr') >= 3 else
                     'H-approx' if vs.count('H-approx') > vs.count('H-instr') and vs.count('H-approx') >= 3 else 'mixed')
    out['S3_cells'] = {k: dict(M1=v['M1']['mean'], M2=v['M2']['median'], M3=v['M3'], M4=v['M4_same_world']['rate'], M4x=v['M4_cross_world']['rate'],
                               M6={a: b['rate'] for a, b in v['M6'].items()}) for k, v in s3.items() if '/' in k and not k.endswith('probe')}
    out['lock'] = read(ROOT / 'protocol_lock.json'); out['protocol_sha256'] = sha(ROOT / 'protocol.json'); out['seconds'] = time.time() - t0
    dump('results/predictions.json', out)
    # ---------------- figures
    col = {'natural': '#222222', 'scrmax': '#c4473a', 'scrmed': '#d08c2f'}
    fig, axs = plt.subplots(1, 5, figsize=(20, 3.6))
    for ax, d in zip(axs, V1_DOMAINS):
        for mp in ['natural'] + list(maps[d]):
            ys = [r['R_k'] for r in crow if r['domain'] == d and r['map'] == mp and r['method'] == 'RRR16' and r['path'] == plus_path(d)]
            ax.plot(range(1, len(ys) + 1), ys, color=col[mp], label=f"{mp} (E_iso {eiso[d, mp]:.3f})")
        ax.set_ylim(-.02, 1.02); ax.set_title(f'{d}: RRR-16 one-way', fontsize=9); ax.legend(fontsize=7)
    fig.supxlabel('step k'); fig.tight_layout(); fig.savefig(ROOT / 'figs/s1a_Rk.png', dpi=140)
    fig, axs = plt.subplots(2, 5, figsize=(20, 7))
    for j, d in enumerate(V1_DOMAINS):
        for mp in (['natural', 'scrmax'] if (d, 'scrmax') in rk else ['natural']):
            rs = sorted(r for r in rk[d, mp] if r in grid[d])
            axs[0, j].plot(rs, [rk[d, mp][r]['single'] for r in rs], 'o-', color=col[mp], label=mp)
            axs[1, j].plot(rs, [rk[d, mp][r]['R_2N'] for r in rs], 'o-', color=col[mp], label=mp)
        for i in (0, 1):
            if d != 'daysago': axs[i, j].axvline(N_of(d) - 1, color='#999999', ls=':', lw=1)
            axs[i, j].set_ylim(-.02, 1.02); axs[i, j].set_xlabel('rank')
        axs[0, j].set_title(f'{d}: single-step', fontsize=9); axs[1, j].set_title(f'{d}: one-way R_2N (dotted: N-1)', fontsize=9); axs[0, j].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/s2_rank.png', dpi=140)
    fig, axs = plt.subplots(1, 4, figsize=(16, 3.6))
    for ax, d in zip(axs, CYC):
        ks = [k for k in s2m if k.startswith(d + '/')]
        for k in ks:
            fr = s2m[k]['error_fraction_by_step']; lab = sorted(fr[0])
            ax.bar([f"{k.split('/')[1]}:{l}" for l in lab], [np.mean([f[l] for f in fr]) for l in lab])
        ax.tick_params(axis='x', rotation=90, labelsize=6); ax.set_title(f'{d}: slot error by harmonic', fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/s2_modes.png', dpi=140)
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8)); cl = sorted(out['S3_cells'])
    axs[0].bar(range(len(cl)), [out['S3_cells'][k]['M3']['source'] for k in cl], color='#c4473a', label='probe = source')
    axs[0].bar(range(len(cl)), [out['S3_cells'][k]['M3']['target'] for k in cl], bottom=[out['S3_cells'][k]['M3']['source'] for k in cl], color='#3b6fb6', label='probe = target')
    axs[1].bar(range(len(cl)), [out['S3_cells'][k]['M4'] for k in cl], color='#555555')
    for ax, t in zip(axs, ('M3 probe readout after one step', 'M4 same-world write transplant success')):
        ax.set_xticks(range(len(cl))); ax.set_xticklabels(cl, rotation=90, fontsize=6); ax.set_title(t, fontsize=9); ax.set_ylim(0, 1.02)
    axs[0].legend(fontsize=7); fig.tight_layout(); fig.savefig(ROOT / 'figs/s3_mechanism.png', dpi=140)
    fig, axs = plt.subplots(1, 4, figsize=(16, 3.6))
    for ax, d in zip(axs, S1B_DOMAINS):
        for me, c_ in (('RRR16', '#222222'), ('C1_s42', '#d08c2f'), ('C3_s42', '#3b6fb6')):
            ys = [r['R_k'] for r in crow if r['domain'] == d and r['method'] == me and r['path'] == 'plus_from_start']
            ax.plot(range(1, len(ys) + 1), ys, color=c_, label=me)
        ax.set_ylim(-.02, 1.02); ax.set_title(f'{d}: one-way plus', fontsize=9); ax.legend(fontsize=7)
    r2 = geo1b['B4_pre_lock']['dev_R2']; axs[3].bar(list(r2), list(r2.values()), color='#555555'); axs[3].set_title('slot linear predictability (dev R^2)', fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/s1b.png', dpi=140)
    print(json.dumps({k: (v.get('verdict', v.get('pass_')) if isinstance(v, dict) else None) for k, v in out.items() if k[0] in 'GABRMQ'}), flush=True)


if __name__ == '__main__':
    main()
