"""Analysis (CPU, after all units): G4-0, V0-V4 and Q9, R1, U1/U2/U1b and Q11, X1/X2, S1 by the locked rules (protocol.json
'predictions' and 'operational'); chains.csv (per-step A_t and cumulative R_t), exploratory tables, figures."""
import time
from collections import defaultdict, Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import lib4
from lib4 import *

CH = {}


def load_chains():
    CH.clear()
    for f in sorted(lib4.SHARDS.glob('chain_*.jsonl')):
        for r in rows(f): CH.setdefault((r['backbone'], r['domain'], r['map'], r['method'], r['path']), []).append(r)
    return CH


def recs(bb, d, method, path, mp='natural'):
    return CH.get((bb, d, mp, method, path), [])


def R_at(bb, d, method, path, k, mp='natural'):
    rs = recs(bb, d, method, path, mp)
    return chain_rate(bb, d, mp, method, path, k, recs=rs) if rs else None


def rv(x): return None if x is None else x['rate']


def tables():
    out = []
    for (bb, d, mp, me, path), rs in sorted(CH.items()):
        by = defaultdict(list)
        for r in rs: by[r['step']].append(r)
        for t in sorted(by):
            out.append(dict(backbone=bb, domain=d, map=mp, method=me, path=path, t=t, n=len(by[t]), A_t=float(np.mean([r['success'] for r in by[t]])),
                            R_t=float(np.mean([r['trajectory_success'] for r in by[t]]))))
    return out


def cell_verdict(cls, n_allow_miss=1):
    """cls: {cell: 'H-ms' | 'H-fund/H-flat' | 'none'}; a hypothesis wins if all but at most one cell match it."""
    if not cls: return 'not evaluable'
    c = Counter(cls.values()); n = len(cls)
    for h in ('H-ms', 'H-fund/H-flat'):
        if c[h] >= n - n_allow_miss: return h
    return 'mixed'


# ---------------------------------------------------------------- V
def v_unit(p, g40):
    out = dict(V0={}, V1={}, V2a={}, V2b={}, V3={}, V4={}, cells={})
    # V0 (train amplitudes, all new domains, both backbones)
    v0 = {}
    for bb in p['V0_amplitudes']:
        for d in ('hour', 'compass8', 'season'):
            amp = p['V0_amplitudes'][bb][d]; a = {int(k): v['a'] for k, v in amp.items()}; s_ = {int(k): v['s'] for k, v in amp.items()}; N = len(S.states(d))
            s1 = min(s_, key=s_.get) == 1; a1 = (max(a, key=a.get) == 1) if N >= 7 else None
            v0[f'{bb}/{d}'] = dict(s=s_, a=a, s1_smallest=s1, a1_largest=a1, holds=s1 and (a1 is not False))
    out['V0'] = dict(cells=v0, pass_=all(v['holds'] for v in v0.values()))
    v1c, v2a, v2b, obs3 = {}, {}, {}, {}
    for bb in ('bart', 't5'):
        for d in g40[bb]['V_domains_post']:
            N = len(S.states(d)); ks = [x['k'] for x in p['calib'][bb][d]['planes']]; nf1 = 'F_not1'
            row = {}
            for cond in ['F_empty', 'F_{1}', nf1] + [f'F_{{{k}}}' for k in ks if k >= 2]:
                name = nf1 if (cond != nf1 and cond.startswith('F_{') and cond != 'F_{1}' and len(ks) == 2) else cond
                row[cond] = {pa: rv(R_at(bb, d, name, f'{pa}_from_start', 2 * N)) for pa in ('plus', 'minus', 'alt')}
            out['cells'][f'{bb}/{d}'] = row
            A1 = A_by_disp(recs(bb, d, 'F_{1}', 'plus_from_start'), N); An = A_by_disp(recs(bb, d, nf1, 'plus_from_start'), N); h = N // 2
            out['cells'][f'{bb}/{d}']['A_F1_plus'] = A1; out['cells'][f'{bb}/{d}']['A_Fnot1_plus'] = An
            if N >= 7:
                pl, al = row['F_{1}']['plus'], row['F_{1}']['alt']
                v1c[f'{bb}/{d}'] = dict(plus=pl, alt=al, cls='H-ms' if pl <= .2 and al >= .8 else 'H-fund/H-flat' if pl <= .2 and al <= .2 else 'none')
                x = A1[1] - A1[h]; v2a[f'{bb}/{d}'] = dict(value=x, cls='H-ms' if x >= .5 else 'H-fund/H-flat' if x <= .1 else 'none')
                y = An[h] - An[1]; v2b[f'{bb}/{d}'] = dict(value=y, cls='H-ms' if y >= .25 else 'H-fund/H-flat' if y <= .1 else 'none')
            for k in ks:
                if k < 2: continue
                for pa in ('plus', 'minus'): obs3[f'{bb}/{d}/F_{{{k}}}/{pa}'] = category(row[f'F_{{{k}}}'][pa])
    for key, cells in (('V1', v1c), ('V2a', v2a), ('V2b', v2b)):
        out[key] = dict(cells=cells, n=len(cells), verdict=cell_verdict({c: v['cls'] for c, v in cells.items()}))
    pre = p['V3_precheck']; Hms = pre['cells_H_ms']
    out['V3'] = dict(observed=obs3, vs_fund=disc_score(Hms, {c: 'composable' for c in Hms}, obs3, 4), vs_flat=disc_score(Hms, {c: 'fail' for c in Hms}, obs3, 4),
                     locked=pre['verdict_at_lock'], missing_observed=[c for c in Hms if c not in obs3])
    v3ok = all(out['V3'][k]['verdict'] in ('H wins', 'not evaluable') for k in ('vs_fund', 'vs_flat'))
    # V4
    for bb in ('bart', 't5'):
        ids, a = [], []
        for d in g40[bb]['V_domains_post']:
            for (b_, d_, mp, me, pa), rs in CH.items():
                if b_ != bb or d_ != d or not me.startswith('F_') or me == 'F_empty': continue
                for r in rs:
                    if r.get('decoded_state') is None or 'argmax_full' not in r: continue
                    ids.append(r['world_id']); a.append([r['argmax_full'] == r['decoded_state'], r['argmax_equal'] == r['decoded_state'], r['argmax_fund'] == r['decoded_state']])
        if not ids: out['V4'][bb] = dict(verdict='not evaluable'); continue
        a = np.array(a, float); fe = boot_diff_ci(ids, a[:, 0], a[:, 1]); ff = boot_diff_ci(ids, a[:, 0], a[:, 2])
        fit, eq, fu = a.mean(0)
        holds = fit >= .85 and fe['ci95'][0] > 0 and ff['ci95'][0] > .10
        verdict = 'H-ms holds' if holds else 'H-fund' if fu >= fit else 'H-equal' if fe['ci95'][0] <= 0 <= fe['ci95'][1] else 'neither'
        out['V4'][bb] = dict(n=len(ids), worlds=len(set(ids)), agreement=dict(full=fit, equal=eq, fund=fu), fit_minus_equal=fe, fit_minus_fund=ff,
                             equal_ci_contains_0=fe['ci95'][0] <= 0 <= fe['ci95'][1], verdict=verdict)
    v4 = [out['V4'][bb].get('verdict') for bb in ('bart', 't5')]
    ms = all(out[k]['verdict'] == 'H-ms' for k in ('V1', 'V2a', 'V2b')) and v3ok
    if ms and all(v == 'H-ms holds' for v in v4): q9 = 'H-ms'
    elif ms and any(out['V4'][bb].get('equal_ci_contains_0') for bb in ('bart', 't5')): q9 = 'H-equal'
    elif all(out[k]['verdict'] == 'H-fund/H-flat' for k in ('V1', 'V2a', 'V2b')):
        vf, vl = out['V3']['vs_fund']['verdict'], out['V3']['vs_flat']['verdict']      # 'H2 wins' = the rival beats H-ms in A.6
        q9 = 'H-fund' if vf == 'H2 wins' and vl != 'H2 wins' else 'H-flat' if vl == 'H2 wins' and vf != 'H2 wins' else 'H-fund or H-flat (V3 does not separate)'
    else: q9 = 'mixed'
    out['Q9'] = dict(verdict=q9, V3_beats_both_or_not_evaluable=v3ok, V4=v4)
    return out


def vote_share(p, bb, d):
    """Exploratory 6.4: per-plane vote share lambda_k d_k(c(x), c(x+m)) / sum, with the locked lambda and the real dev distances."""
    lam = torch.tensor(p['calib'][bb][d]['models']['full']['lam'], dtype=torch.float64); P = planes(bb, d); Cw = slot_matrix(bb, d, 'dev'); N = Cw.shape[1]; out = {}
    for m_ in range(1, N // 2 + 1):
        nx = [(x + m_) % N for x in range(N)]; dk = torch.stack([((Cw[:, nx] - Cw) @ B).square().sum(-1) for _, B in P], -1)
        v = lam * dk; out[m_] = (v / v.sum(-1, keepdim=True)).mean((0, 1)).tolist()
    return dict(planes=[k for k, _ in P], share_by_displacement=out)


# ---------------------------------------------------------------- R
def r_unit(p, g40):
    pre = p['R_precheck']; cells = {}
    for c, v in pre['cells'].items():
        bb, d, r = c.split('/'); r = int(r[1:]); N = len(S.states(d))
        if d not in g40[bb]['V_domains_post']: continue
        row = {f'{m}_{pa}': rv(R_at(bb, d, f'{m}{r}', f'{pa}_from_start', 2 * N)) for m in ('RRR', 'FF') for pa in ('plus', 'minus', 'alt')}
        row['dR_plus'] = None if row['FF_plus'] is None else row['FF_plus'] - row['RRR_plus']
        row['scorable'] = c in pre['scorable_cells']; row['S_FF'] = v['S_FF']; row['RRR_missing_fundamental'] = v['RRR_missing_fundamental']
        row['FF_pred_category'] = v['FF_pred_category']
        if row['scorable'] and row['FF_plus'] is not None:
            row['cls'] = 'H-alloc' if row['FF_plus'] >= .9 and row['dR_plus'] >= .2 else 'H-capacity' if row['dR_plus'] <= .05 else 'none'
        cells[c] = row
    sc = {c: v for c, v in cells.items() if v['scorable'] and 'cls' in v}
    if not pre['evaluable']: verdict = 'not evaluable (locked: fewer than 3 scorable cells)'
    elif not sc: verdict = 'not evaluable (no scorable cell observed)'
    else:
        c = Counter(v['cls'] for v in sc.values()); n = len(sc)
        verdict = 'H-alloc' if c['H-alloc'] >= .75 * n else 'H-capacity' if c['H-capacity'] >= .75 * n else 'mixed'
    return dict(R1=dict(cells=cells, scorable=list(sc), n_scorable=len(sc), verdict=verdict))


# ---------------------------------------------------------------- U
def u_unit(p, ut, ue):
    out = {}
    def r2n(v, d, s):
        st = ut.get(f'{v}/{d}/s{s}')
        if st is None or not st['admitted']: return 0.0
        return rv(R_at('bart', d, f'{v}_s{s}', 'plus_from_start', 2 * len(S.states(d))))
    for key, v, doms in (('U1', 'C1U4', ['weekday', 'month', 'compass']), ('U1b', 'C1UN', ['weekday', 'month'])):
        med = {d: float(np.median([r2n(v, d, s) for s in SEEDS])) for d in doms}; need = 2 if len(doms) == 3 else 2
        out[key] = dict(seed_median_R2N=med, per_seed={d: [r2n(v, d, s) for s in SEEDS] for d in doms},
                        cannot_learn=[f'{d}/s{s}' for d in doms for s in SEEDS if not ut.get(f'{v}/{d}/s{s}', {}).get('admitted', False)],
                        verdict='H-state' if sum(x >= .9 for x in med.values()) >= need else 'H-shortcut' if sum(x <= .2 for x in med.values()) >= need else 'mixed')
    m3 = [ue[f'{d}/C1U4_s{s}']['M3'] for d in ('weekday', 'month', 'compass') for s in SEEDS if 'M3' in ue.get(f'{d}/C1U4_s{s}', {})]
    if m3:
        tg, src = float(np.median([x['target'] for x in m3])), float(np.median([x['source'] for x in m3]))
        out['U2'] = dict(median_target=tg, median_source=src, n_cells=len(m3), verdict='H-state' if tg >= .8 else 'H-shortcut' if src >= .8 else 'mixed')
    else: out['U2'] = dict(verdict='not evaluable (no admitted C1-U4 editor)')
    out['Q11'] = dict(verdict=out['U1']['verdict'] if out['U1']['verdict'] == out['U2']['verdict'] and out['U1']['verdict'] in ('H-state', 'H-shortcut') else 'mixed')
    ex = {}
    for d in ('weekday', 'month', 'compass'):
        N = len(S.states(d))
        for name in [f'{v}_s{s}' for v in ('C1U4', 'C1UN', 'C3U4') for s in SEEDS] + [f'C1v1_s{s}' for s in SEEDS] + [f'P2C3_s{s}' for s in SEEDS]:
            if not recs('bart', d, name, 'plus_from_start'): continue
            e = ue.get(f'{d}/{name}', {})
            ex[f'{d}/{name}'] = dict(R4=rv(R_at('bart', d, name, 'plus_from_start', 4)), R2N={pa: rv(R_at('bart', d, name, f'{pa}_from_start', 2 * N)) for pa in ('plus', 'minus', 'alt')},
                                     M1=e.get('M1', {}).get('mean'), M2=e.get('M2', {}).get('median'), M3=e.get('M3'), M3_step2=e.get('M3_step2'), eps=e.get('eps'),
                                     harmonics=e.get('algebra', {}).get('harmonics_present'), DRIFT=e.get('algebra', {}).get('DRIFT'))
    out['exploratory'] = ex
    return out


# ---------------------------------------------------------------- X
def x_unit(p, xt, xe):
    if xt.get('x_status') != 'go': return dict(X1=dict(verdict='X stopped (admission)'), X2=dict(verdict='not evaluable'), Q12=dict(verdict='not evaluable'))
    def med(d, kind):
        v = [rv(R_at('bart', d, f'{kind}_s{s}', 'plus_from_start', 6)) for s in SEEDS]
        return None if None in v else float(np.median(v))
    x1 = {d: med(d, 'Att') for d in ('name3', 'bind3fix')}
    out = dict(X1=dict(att_R6=x1, pass_=all(v is not None and v >= .95 for v in x1.values())))
    a, t = med('bind3', 'Att'), med('bind3', 'Tok')
    if not out['X1']['pass_'] or a is None or t is None: out['X2'] = dict(att_R6=a, tok_R6=t, verdict='not evaluable (X1 failed or missing)')
    else: out['X2'] = dict(att_R6=a, tok_R6=t, verdict='H-arch' if a >= .9 and t <= .2 else 'H-deep' if a <= .5 else 'mixed')
    out['Q12'] = dict(verdict=out['X2']['verdict'])
    tab = {}
    for d in X_DOMAINS:
        for name in ['RRR32', 'reencode'] + [f'{k}_s{s}' for k in ('Tok', 'Att') for s in SEEDS]:
            tab[f'{d}/{name}'] = {f'{pa}': rv(R_at('bart', d, name, f'{pa}_from_start', n)) for pa, n in (('plus', 30), ('minus', 6), ('alt', 6))}
            tab[f'{d}/{name}']['R6_plus'] = rv(R_at('bart', d, name, 'plus_from_start', 6))
    out['table'] = tab; out['attention'] = xe.get('bind3/attention'); out['bind3_dev_single'] = {k: v['rate'] for k, v in xe.items() if k.endswith('dev_single')}
    ft = {}
    for kind in ('Tok', 'Att'):
        c = Counter()
        for s in SEEDS:
            by = defaultdict(list)
            for r in recs('bart', 'bind3', f'{kind}_s{s}', 'plus_from_start'): by[r['world_id']].append(r)
            for w, rs in by.items():
                bad = next((r for r in sorted(rs, key=lambda r: r['step']) if not r['success']), None)
                if bad is None: c['no_failure'] += 1; continue
                c['listed_other' if bad['decoded_state'] is not None and bad['decoded_state'] != bad['state'] else 'right_name_context_error' if bad['decoded_state'] == bad['state']
                  else 'outside_list' if bad['decoded_word'] else 'unparsable'] += 1
        ft[kind] = dict(c)
    out['bind3_first_failure_types'] = ft
    return out


# ---------------------------------------------------------------- S
def s_unit(p):
    out = {}; ok = []
    for d in S_DOMAINS:
        N = len(S.states(d)); r = {mp: dict(R_2N=rv(R_at('t5', d, 'RRR32', 'longplus', 2 * N, mp)), R_10N=rv(R_at('t5', d, 'RRR32', 'longplus', 10 * N, mp))) for mp in ('natural', 'scrmax')}
        ev = all(v['R_2N'] is not None and v['R_2N'] >= .95 for v in r.values())
        out[d] = dict(r, evaluable=ev, diff=(r['natural']['R_10N'] - r['scrmax']['R_10N']) if ev else None)
    evd = [d for d in S_DOMAINS if out[d]['evaluable']]
    if not evd: v = 'not decidable (no evaluable domain)'
    elif any(out[d]['diff'] >= .2 for d in evd): v = 'H-longsym'
    elif len(evd) == len(S_DOMAINS) and all(out[d]['diff'] <= .05 for d in evd): v = 'H-slot'
    else: v = 'mixed'
    out['S1'] = dict(verdict=v, evaluable=evd); return out


# ---------------------------------------------------------------- figures
def figures(p, g40, V, R, U, X, shares):
    cols = {'obs_F1': '#c0392b', 'obs_Fn1': '#2471a3'}
    for bb in ('bart', 't5'):
        doms = g40[bb]['V_domains_post']
        if not doms: continue
        fig, axs = plt.subplots(1, len(doms), figsize=(4.2 * len(doms), 3.4), squeeze=False)
        for ax, d in zip(axs[0], doms):
            N = len(S.states(d)); t = range(1, 2 * N + 1)
            for cond, c, lab in (('F_{1}', cols['obs_F1'], 'F{1}'), ('F_not1', cols['obs_Fn1'], 'F¬1')):
                rs = recs(bb, d, cond, 'plus_from_start'); by = defaultdict(list)
                for r in rs: by[r['step']].append(r['success'])
                if by: ax.plot(list(t), [np.mean(by[s]) for s in t], 'o-', ms=3, color=c, label=f'{lab} observed')
                pr = p['calib'][bb][d]['ideal_At'][cond]['plus']; ax.plot(list(t), pr, '--', color=c, alpha=.6, label=f'{lab} predicted (locked)')
            for x in (N / 2, N, 2 * N): ax.axvline(x, color='#bbbbbb', ls=':', lw=.8)
            ax.set_ylim(-.03, 1.03); ax.set_title(f'{bb} {d} (N={N})', fontsize=9); ax.set_xlabel('step t')
        axs[0][0].set_ylabel('A_t (one-way plus)'); axs[0][0].legend(fontsize=6); fig.tight_layout(); fig.savefig(ROOT / f'figs/v_curves_{bb}.png', dpi=140); plt.close(fig)
    if shares:
        fig, axs = plt.subplots(2, max(len(v) for v in shares.values()), figsize=(18, 6.5), squeeze=False)
        for i, bb in enumerate(('bart', 't5')):
            for j, (d, sh) in enumerate(shares.get(bb, {}).items()):
                ax = axs[i][j]; ms = sorted(sh['share_by_displacement'], key=int)
                for kk, k in enumerate(sh['planes']): ax.plot([int(m) for m in ms], [sh['share_by_displacement'][m][kk] for m in ms], 'o-', ms=3, label=f'k={k}')
                ax.set_title(f'{bb} {d}', fontsize=9); ax.set_xlabel('displacement'); ax.set_ylim(0, 1)
            axs[i][0].set_ylabel('vote share (locked λ, dev distances)'); axs[i][0].legend(fontsize=6)
        fig.tight_layout(); fig.savefig(ROOT / 'figs/v_vote_share.png', dpi=140); plt.close(fig)
    cells = R['R1']['cells']
    if cells:
        groups = defaultdict(list)
        for c, v in cells.items(): bb, d, r = c.split('/'); groups[bb, d].append((int(r[1:]), v))
        fig, axs = plt.subplots(1, len(groups), figsize=(3.6 * len(groups), 3.2), squeeze=False)
        for ax, ((bb, d), lst) in zip(axs[0], sorted(groups.items())):
            lst.sort(); rs_ = [r for r, _ in lst]
            ax.plot(rs_, [v['RRR_plus'] for _, v in lst], 'o-', color='#555555', label='RRR-r'); ax.plot(rs_, [v['FF_plus'] for _, v in lst], 's-', color='#c0392b', label='FF-r')
            for r, v in lst:
                if v['scorable']: ax.annotate('*', (r, v['FF_plus']), fontsize=12)
            ax.set_title(f'{bb} {d}', fontsize=9); ax.set_xlabel('rank r'); ax.set_ylim(-.03, 1.03)
        axs[0][0].set_ylabel('one-way plus R_2N'); axs[0][0].legend(fontsize=7); fig.tight_layout(); fig.savefig(ROOT / 'figs/r_rank.png', dpi=140); plt.close(fig)
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.4))
    for ax, d in zip(axs, ('weekday', 'month', 'compass')):
        N = len(S.states(d)); t = range(1, 2 * N + 1)
        for v, c in (('C1v1', '#999999'), ('C1U4', '#c0392b'), ('C1UN', '#2471a3'), ('C3U4', '#27ae60')):
            ys = []
            for s in SEEDS:
                y = [rv(R_at('bart', d, f'{v}_s{s}', 'plus_from_start', k)) for k in t]
                if None not in y: ys.append(y)
            if ys: ax.plot(list(t), np.median(np.array(ys), 0), 'o-', ms=3, color=c, label=v)
        ax.axvline(4.5, color='#bbbbbb', ls=':'); ax.set_ylim(-.03, 1.03); ax.set_title(f'{d}: one-way plus R_t (seed median)', fontsize=9); ax.set_xlabel('t')
    axs[0].legend(fontsize=7); fig.tight_layout(); fig.savefig(ROOT / 'figs/u_Rt.png', dpi=140); plt.close(fig)
    if X.get('table'):
        fig, axs = plt.subplots(1, 4, figsize=(16, 3.4))
        for ax, d in zip(axs, X_DOMAINS):
            for name, c in (('RRR32', '#555555'), ('Tok', '#2471a3'), ('Att', '#c0392b')):
                names = [name] if name == 'RRR32' else [f'{name}_s{s}' for s in SEEDS]; ys = []
                for nm in names:
                    y = [rv(R_at('bart', d, nm, 'plus_from_start', k)) for k in range(1, 31)]
                    if None not in y: ys.append(y)
                if ys: ax.plot(range(1, 31), np.median(np.array(ys), 0), '-', color=c, label=name)
            ax.set_ylim(-.03, 1.03); ax.set_title(f'{d}: plus R_k', fontsize=9); ax.set_xlabel('k')
        axs[0].legend(fontsize=7)
        att = X.get('attention') or {}
        if att:
            ks = ['current', 'next', 'prev', 'other']; M = np.array([[att[n][k] for k in ks] for n in sorted(att)])
            axs[3].imshow(M, cmap='Greys', vmin=0, vmax=1); axs[3].set_xticks(range(4)); axs[3].set_xticklabels(ks, fontsize=7)
            axs[3].set_yticks(range(len(att))); axs[3].set_yticklabels(sorted(att), fontsize=7); axs[3].set_title('bind3 Att-L2: slot attention mass', fontsize=9)
        fig.tight_layout(); fig.savefig(ROOT / 'figs/x_Rk.png', dpi=140); plt.close(fig)


def main():
    require_slurm(); p = verify_protocol4(); t0 = time.time(); load_chains()
    g40 = {bb: read(ROOT / f'results/g40_{bb}.json') for bb in ('bart', 't5')}
    V = v_unit(p, g40); R = r_unit(p, g40)
    U = u_unit(p, read(ROOT / 'results/u_train.json'), read(ROOT / 'results/u_eval.json'))
    X = x_unit(p, read(ROOT / 'results/x_train.json'), read(ROOT / 'results/x_eval.json')); Sx = s_unit(p)
    shares = {bb: {d: vote_share(p, bb, d) for d in g40[bb]['V_domains_post']} for bb in ('bart', 't5')}
    alt = {f'{bb}/{d}/{c}': dict(derived=p['calib'][bb][d]['derived'][c]['category']['alt'], observed=category(V['cells'][f'{bb}/{d}'][c]['alt']))
           for bb in ('bart', 't5') for d in g40[bb]['V_domains_post'] for c in V['cells'][f'{bb}/{d}'] if c.startswith('F_') and c in p['calib'][bb][d]['derived']
           and V['cells'][f'{bb}/{d}'][c]['alt'] is not None}
    csvwrite('results/chains.csv', tables())
    out = dict(G4_0=g40, V=V, R=R, U=U, X=X, S=Sx, exploratory=dict(vote_share=shares, alt_derived_vs_observed=alt),
               verdicts=dict(Q9=V['Q9']['verdict'], Q10=R['R1']['verdict'], Q11=U['Q11']['verdict'], U1b=U['U1b']['verdict'], Q12=X['Q12']['verdict'], Q13=Sx['S1']['verdict'],
                             V0=V['V0']['pass_']),
               lock=read(ROOT / 'protocol_lock.json') if (ROOT / 'protocol_lock.json').exists() else None, protocol_sha256=sha(ROOT / 'protocol.json'), seconds=time.time() - t0)
    dump('results/predictions.json', out); figures(p, g40, V, R, U, X, shares)
    print(json.dumps(out['verdicts'], indent=1), flush=True)


if __name__ == '__main__':
    main()
