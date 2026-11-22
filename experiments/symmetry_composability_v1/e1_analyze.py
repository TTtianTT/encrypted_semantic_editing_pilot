"""E1.6 analysis (CPU): R_k / single-step tables, locked predictions P1-P7 with admission, figures."""
import time
from collections import defaultdict
import torch
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *
import sym_semantics as S

PLUS = {d: ('plus_from_two' if d == 'daysago' else 'plus_from_start') for d in S.DOMAINS}


def load_shards():
    chains = defaultdict(lambda: defaultdict(dict)); singles = defaultdict(list)
    for f in sorted((ROOT / 'results/shards').glob('*.jsonl')):
        for r in rows(f):
            if f.name.startswith('chain_'):
                chains[r['domain'], r['method'], r['path']][r['world_id']][r['step']] = r['trajectory_success']
            else:
                singles[r['domain'], r['method']].append(r)
    return chains, singles


def R(chains, d, method, path, k):
    ws = chains[d, method, path]; assert len(ws) == 160, (d, method, path, len(ws))
    return rate([ws[w][k] for w in ws])


def confirm_geometry(d):
    C = core(); P = []
    for s in S.states(d):
        c = e1_cache(d, 'confirm', s); P.append(C.pool(c['h'].float(), c['m'].float()))
    V = torch.stack(P, 1).double().numpy(); n = len(S.states(d))
    pairs, kind = ([(i, i + 1) for i in range(n - 1)], 'open') if d == 'daysago' else ([(i, (i + 1) % n) for i in range(n)], 'cyclic')
    out, _, ew = geometry_report(V, [S.word(d, s) for s in S.states(d)], pairs, kind, null=False, name=f'{d}_confirm_t0')
    return out, ew, V


def main():
    require_slurm(); p = verify_protocol(); t0 = time.time(); P = p['predictions']; thr = p['admission']['threshold']
    chains, singles = load_shards(); alg = read(ROOT / 'results/e1_algebra.json')
    # admission (dev single-step success)
    adm = {}
    for d in S.DOMAINS:
        adm[d, 'RRR16'] = read(ROOT / f'results/e1_rrr_{d}_complete.json')['dev_single_RRR16']['rate'] >= thr
        for s in p['training']['seeds']:
            adm[d, f'C3_s{s}'] = read(ROOT / f'results/e1_train_C3_{d}_s{s}_complete.json')['dev_single']['rate'] >= thr
    # tables
    chain_rows = []
    for (d, m, path), ws in sorted(chains.items()):
        K = max(max(v) for v in ws.values()); prev = 1.0
        for k in range(1, K + 1):
            r = R(chains, d, m, path, k); chain_rows.append(dict(domain=d, method=m, path=path, k=k, R_k=r['rate'], lo=r['ci95'][0], hi=r['ci95'][1],
                                                                  r_k=r['rate'] / prev if prev > 0 else None)); prev = r['rate']
    single_rows = []
    for (d, m), rs in sorted(singles.items()):
        single_rows.append(dict(domain=d, method=m, n=len(rs), success=np.mean([r['score']['success'] for r in rs]),
                                exact=np.mean([r['exact'] for r in rs]), preserved=np.mean([r['score']['preserved'] for r in rs]),
                                target=np.mean([r['score']['target'] for r in rs])))
    csvwrite('results/e1_chains.csv', chain_rows); csvwrite('results/e1_singles.csv', single_rows)
    geo = {}; ew = {}; Vs = {}
    for d in S.DOMAINS:
        geo[d], ew[d], Vs[d] = confirm_geometry(d)
    pred = {}
    def admitted(keys): return all(adm[k] for k in keys)
    # P1, P2
    for name, mult, t in (('P1', 1, P['P1']['threshold']), ('P2', 2, P['P2']['threshold'])):
        obs = {d: R(chains, d, 'RRR16', PLUS[d], mult * len(S.states(d))) for d in ('weekday', 'month')}
        pred[name] = dict(threshold=t, observed=obs, admissible=admitted([(d, 'RRR16') for d in obs]), pass_=all(o['rate'] >= t for o in obs.values()))
    # P3a, P3b
    diff = boot_diff(ew['compass'], ew['egoside'])
    pred['P3a'] = dict(observed=dict(compass=geo['compass']['E_iso'], egoside=geo['egoside']['E_iso'], diff=diff), pass_=diff['ci95'][1] < 0, admissible=True)
    a, b = R(chains, 'compass', 'RRR16', PLUS['compass'], 8), R(chains, 'egoside', 'RRR16', PLUS['egoside'], 8)
    z = two_prop_z(a['k'], a['n'], b['k'], b['n'])
    pred['P3b'] = dict(threshold=P['P3b']['min_difference'], observed=dict(compass=a, egoside=b, difference=a['rate'] - b['rate'], test=z),
                       admissible=admitted([('compass', 'RRR16'), ('egoside', 'RRR16')]),
                       pass_=(a['rate'] - b['rate'] >= P['P3b']['min_difference']) and z['p_one_sided'] is not None and z['p_one_sided'] < P['P3b']['alpha'])
    # P4
    o1 = R(chains, 'daysago', 'RRR16', 'plus_from_two', 7); o2 = R(chains, 'daysago', 'RRR16', 'alternating_from_five', 10)
    pred['P4'] = dict(threshold=P['P4']['threshold'], observed=dict(R7_plus_from_two=o1, R10_alternating=o2), admissible=adm['daysago', 'RRR16'],
                      pass_=o1['rate'] >= P['P4']['threshold'] and o2['rate'] >= P['P4']['threshold'])
    # P5
    c1 = {f'{d}/C1_s{s}': R(chains, d, f'C1_s{s}', PLUS[d], 2) for d in S.DOMAINS for s in p['training']['seeds']}
    c3 = {f'{d}/C3_s{s}': R(chains, d, f'C3_s{s}', PLUS[d], len(S.states(d))) for d in ('weekday', 'month') for s in p['training']['seeds']}
    pred['P5'] = dict(threshold=dict(C1_R2_max=P['P5']['C1_R2_max'], C3_RN_min=P['P5']['C3_RN_min']), observed=dict(C1_R2=c1, C3_RN=c3),
                      admissible=admitted([(d, f'C3_s{s}') for d in ('weekday', 'month') for s in p['training']['seeds']]),
                      pass_=all(v['rate'] <= P['P5']['C1_R2_max'] for v in c1.values()) and all(v['rate'] >= P['P5']['C3_RN_min'] for v in c3.values()))
    # P6
    kap = {d: alg[f'{d}/RRR16']['kappa_N'] for d in ('weekday', 'month')}
    pred['P6'] = dict(threshold=P['P6']['threshold'], observed={d: dict(median=v['median'], ci95=v['median_ci95']) for d, v in kap.items()},
                      admissible=admitted([(d, 'RRR16') for d in kap]), pass_=all(v['median'] < P['P6']['threshold'] for v in kap.values()))
    # P7 (report only)
    s6 = {d: R(chains, d, 'RRR16', PLUS[d], 6)['rate'] ** (1 / 6) for d in S.DOMAINS}
    rho = spearmanr([geo[d]['E_iso']['mean'] for d in S.DOMAINS], [s6[d] for d in S.DOMAINS])
    pred['P7'] = dict(observed=dict(E_iso={d: geo[d]['E_iso']['mean'] for d in S.DOMAINS}, S6=s6, spearman_rho=float(rho[0]), p=float(rho[1])),
                      decision='report only (n = 5)')
    for k, v in pred.items():
        if 'pass_' in v:
            v['verdict'] = ('pass' if v['pass_'] else 'fail') if v['admissible'] else 'not decidable (admission failed)'
    out = dict(predictions=pred, admission={f'{d}/{m}': v for (d, m), v in adm.items()}, confirm_geometry=geo,
               protocol_sha256=sha(ROOT / 'protocol.json'), lock=read(ROOT / 'protocol_lock.json') if (ROOT / 'protocol_lock.json').exists() else None,
               seconds=time.time() - t0)
    dump('results/e1_predictions.json', out)
    # figures ------------------------------------------------------------
    col = dict(RRR16='#222222', reencode='#999999', C1='#d08c2f', C3='#3b6fb6')
    fig, axs = plt.subplots(3, 5, figsize=(20, 10))
    for j, d in enumerate(S.DOMAINS):
        names = list(p['chains']['by_domain'][d])
        for i, path in enumerate(names):
            ax = axs[i, j]
            for m in p['methods']:
                fam = 'C1' if m.startswith('C1') else 'C3' if m.startswith('C3') else m
                if fam not in col: continue
                ys = [r['R_k'] for r in chain_rows if r['domain'] == d and r['method'] == m and r['path'] == path]
                ax.plot(range(1, len(ys) + 1), ys, '-', color=col[fam], lw=1.2 if fam in ('RRR16', 'reencode') else .8, label=fam)
            ax.set_ylim(-.02, 1.02); ax.set_title(f'{d} {path}', fontsize=8)
            if d != 'daysago': ax.axvline(len(S.states(d)), color='#dddddd', lw=.6)
    h, l = axs[0, 0].get_legend_handles_labels(); u = dict(zip(l, h)); axs[0, 0].legend(u.values(), u.keys(), fontsize=7)
    fig.supxlabel('step k'); fig.supylabel('R_k'); fig.tight_layout(); fig.savefig(ROOT / 'figs/e1_Rk.png', dpi=140)
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8)); ranks = p['rrr']['ranks']
    for d in S.DOMAINS:
        sr = [next(r['success'] for r in single_rows if r['domain'] == d and r['method'] == f'RRR{k}') for k in ranks]
        rn = [R(chains, d, f'RRR{k}', PLUS[d], len(S.states(d)) if d != 'daysago' else 7)['rate'] for k in ranks]
        axs[0].plot(ranks, sr, 'o-', label=d); axs[1].plot(ranks, rn, 'o-', label=d)
    for ax, t in zip(axs, ('single-step success', 'R_N (plus chain; daysago R_7)')):
        ax.set_xscale('log', base=2); ax.set_xlabel('RRR rank'); ax.set_title(t, fontsize=9); ax.set_ylim(-.02, 1.02)
    axs[0].legend(fontsize=7); fig.tight_layout(); fig.savefig(ROOT / 'figs/e1_rank.png', dpi=140)
    fig, ax = plt.subplots(figsize=(5, 4))
    for d in S.DOMAINS:
        ax.plot(geo[d]['E_iso']['mean'], s6[d], 'o'); ax.annotate(d, (geo[d]['E_iso']['mean'], s6[d]), fontsize=8, xytext=(3, 3), textcoords='offset points')
    e0 = read(ROOT / 'results/e0_geometry.json')
    for k, lab in (('time_t0_segment', 'E0 time {+1,0,-1}'), ('person_t0', 'E0 person')):
        ax.axvline(e0[k]['E_iso']['mean'], ls=':', color='#999999'); ax.annotate(lab, (e0[k]['E_iso']['mean'], .05), fontsize=7, rotation=90)
    ax.set_xlabel('E_iso (confirm, template 0)'); ax.set_ylabel('S6 = R_6^(1/6), RRR-16 plus chain'); ax.set_title(f"P7 Spearman rho = {rho[0]:.2f} (n=5)", fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/e1_eiso_vs_s6.png', dpi=140)
    fig, axs = plt.subplots(1, 5, figsize=(18, 3.5))
    for ax, d in zip(axs, S.DOMAINS):
        n = len(S.states(d)); pairs = [(i, i + 1) for i in range(n - 1)] if d == 'daysago' else [(i, (i + 1) % n) for i in range(n)]
        pca_plot(ax, Vs[d], [S.word(d, s).replace(' days ago', '') for s in S.states(d)], f"{d} confirm  E_iso={geo[d]['E_iso']['mean']:.3f}", pairs)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/e1_confirm_pca.png', dpi=140)
    print(json.dumps({k: v.get('verdict', v.get('decision')) for k, v in pred.items()}), flush=True)


if __name__ == '__main__':
    main()
