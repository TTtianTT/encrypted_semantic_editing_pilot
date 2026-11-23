"""Analysis (CPU, after all post-lock chains; PLAN 6.4, 7.2, 8, 9.2, 10.2, 13). Verdicts follow protocol.json (predictions and the
operational rules). The latent predictions are the locked simulation files (results/simulate_<bb>.json.gz); the argmax recorded inside
the post-lock chains is compared with them (consistency). Outputs: results/predictions.json, results/chains.csv, figs/*.png and *.svg.
--smoke: run every unit on the dev smoke shards (local/smoke) with the pre-lock summaries (no verdict is meaningful)."""
import gzip
import time
from collections import defaultdict
import lib5
from lib5 import *
import lcore

FIGS = ROOT / 'figs'
SM = False


# ---------------------------------------------------------------- loading
def load_sims(bbs, sdir):
    out = {}
    for bb in bbs:
        f = sdir / f'simulate_{bb}.json.gz'
        if f.exists():
            with gzip.open(f, 'rt') as g: out.update(json.load(g))
    return out


CH = {}


def load_chains(dirs):
    CH.clear()
    for D in dirs:
        for f in sorted(Path(D).glob('chain_*.jsonl')):
            for r in rows(f): CH.setdefault((r['backbone'], r['domain'], r['method'], r['path']), []).append(r)


def recs(bb, d, method, path):
    return CH.get((bb, d, method, path if path.endswith(('_from_start', 'g50_plus')) else f'{path}_from_start'), [])


def steps_of(rs):
    return max(r['step'] for r in rs) if rs else 0


def R_at(bb, d, method, path, k):
    rs = recs(bb, d, method, path)
    if not rs or steps_of(rs) < k: return None
    return chain_rate(bb, d, 'natural', method, path if path.endswith('_from_start') else f'{path}_from_start', k, recs=rs)


def rv(x): return None if x is None else x['rate']


def merged(bb, d, method, path, sims, unit='L'):
    """Observed records with the locked latent readout merged in (field argmax_locked); consistency counts mismatches."""
    rs = recs(bb, d, method, path); sim = sims.get(f'{unit}/{bb}/{d}/{method}/{path}')
    if not rs or sim is None: return None, None
    idx = {w: i for i, w in enumerate(sim['world_ids'])}; out = []; mm = 0
    for r in rs:
        i = idx[r['world_id']]; t = r['step'] - 1
        if t >= len(sim['states'][i]): continue
        q = dict(r, argmax_locked=sim['argmax']['full'][i][t]); assert sim['states'][i][t] == r['state']
        if 'argmax_full' in r and r['argmax_full'] != q['argmax_locked']: mm += 1
        out.append(q)
    return out, mm


# ---------------------------------------------------------------- L
def is_editor(method): return not method.startswith(('F_', 'RRR', 'FF'))


def l_unit(p, sims, bbs):
    tabs = defaultdict(dict); cells = {}; mism = 0; out = dict(per_backbone={}, new={}, mismatches=0)
    for bb in bbs:
        for key, c in p['simulate'][bb]['cells'].items():
            if c['unit'] != 'L': continue
            rs, mm = merged(bb, c['domain'], c['method'], c['path'], sims)
            if rs is None: continue
            mism += mm; N = c['N']; tab = lcore.world_table(rs, min(2 * N, steps_of(rs)), latent='argmax_locked')
            s = lcore.cell_summary(tab); s.update(family=c['family'], new=c['new'], locked_R_hat=c['R_hat_2N'], locked_cat=c['category'])
            cells[key] = s; tabs[bb][key] = tab
    out['mismatches'] = mism; out['cells'] = cells
    for bb in bbs:
        main = {k: t for k, t in tabs[bb].items() if cells[k]['family'] == 'state' and not cells[k]['new']}
        new = {k: t for k, t in tabs[bb].items() if cells[k]['new']}
        for name, sel, tgt in (('main', main, out['per_backbone']), ('new', new, out['new'])):
            if not sel: tgt[bb] = None; continue
            pl = lcore.pooled(sel, boot=lcore.boot_diff_ci); acc = float(np.mean([cells[k]['locked_cat'] == cells[k]['obs_cat'] for k in sel]))
            lo = pl['latent_minus_naive']['ci95'][0]
            v1 = 'H-latent' if pl['latent'] >= .85 and lo > 0 else 'H-decoder' if pl['latent'] < .75 or lo <= 0 else 'mixed'
            v2 = 'H-latent' if acc >= .80 else 'H-decoder' if acc <= .65 else 'mixed'
            tgt[bb] = dict(n_cells=len(sel), L1=dict(pl, verdict=v1), L2=dict(accuracy=acc, n=len(sel), verdict=v2))
    comb = lambda vs: 'H-latent' if vs and all(v == 'H-latent' for v in vs) else 'H-decoder' if vs and all(v == 'H-decoder' for v in vs) else 'mixed'
    pb = [v for v in out['per_backbone'].values() if v]
    out['L1'] = dict(verdict=comb([v['L1']['verdict'] for v in pb])); out['L2'] = dict(verdict=comb([v['L2']['verdict'] for v in pb]))
    a, b = out['L1']['verdict'], out['L2']['verdict']
    out['Q14'] = dict(verdict='H-latent' if a == b == 'H-latent' else 'H-decoder' if 'H-decoder' in (a, b) and 'H-latent' not in (a, b) else 'mixed')
    # L3: editor cells (backbone, editor, domain, direction)
    conv = {bb: {k for k, v in (p['simulate'][bb].get('converged_C3') or {}).items() if isinstance(v, dict) and v.get('converged')} for bb in bbs}
    ec = {}
    for key, s in cells.items():
        _, bb, d, m, path = key.split('/')
        if not is_editor(m) or path == 'alt': continue
        ec[key] = dict(D=s['D'], D_n=s['D_n'], R2N=s['obs_rate'], family=s['family'], converged=f'{d}/{m}' in conv[bb])
    fr = lambda xs: float(np.mean(xs)) if xs else None
    hiD = [c for c in ec.values() if c['D'] is not None and c['D'] >= .5]; ce = [c for c in ec.values() if c['family'] == 'CE' and c['D'] is not None]
    cv = [c for c in ec.values() if c['converged'] and c['D'] is not None]
    l3a = fr([c['R2N'] <= .20 for c in hiD]); l3b = fr([c['D'] >= .5 for c in ce]); l3c = fr([c['D'] <= .20 for c in cv])
    hold = lambda x: None if x is None else x >= .90
    out['L3'] = dict(cells=ec, L3a=dict(n=len(hiD), frac=l3a, holds=hold(l3a)), L3b=dict(n=len(ce), frac=l3b, holds=hold(l3b)), L3c=dict(n=len(cv), frac=l3c, holds=hold(l3c)))
    hs = [out['L3'][k]['holds'] for k in ('L3a', 'L3b', 'L3c')]
    out['Q14prime'] = dict(verdict='H-detector' if all(h is True for h in hs) else 'not H-detector' if any(h is False for h in hs) else 'not evaluable')
    # L4 (T5 month)
    if 't5' in bbs:
        tr = p['train_new']['t5']['L']; L4 = {}
        for v in ('C1U4n', 'C3U4n'):
            for s in (42, 43):
                key = f'L/t5/month/{v}_s{s}/plus'; ok = tr.get(f'{v}/month/s{s}', {}).get('status') == 'ok'
                L4[f'{v}_s{s}'] = dict(admitted=ok, R2N=cells[key]['obs_rate'] if ok and key in cells else 0.0, D=cells[key]['D'] if ok and key in cells else None)
        c1 = [L4[f'C1U4n_s{s}'] for s in (42, 43)]; c3 = [L4[f'C3U4n_s{s}'] for s in (42, 43)]
        sh = all(x['R2N'] <= .20 for x in c1) and all(x['D'] is not None and x['D'] >= .8 for x in c1 if x['admitted']) and all(x['R2N'] >= .90 for x in c3)
        st = all(x['R2N'] >= .90 for x in c1)
        out['L4'] = dict(cells=L4, verdict='H-shortcut' if sh else 'H-state' if st else 'mixed')
    return out


# ---------------------------------------------------------------- D
def d_unit(p, bbs):
    C = []; allc = {}
    for bb in bbs:
        for d in D_DOMAINS[bb]:
            N = len(S.states(d)); ideal = p['idealized_D'][bb][d]
            for cond, v in ideal.items():
                if cond == 'F_empty' or (cond == 'F_{2}' and d == 'season'): continue
                dname = 'D_' + cond[2:]
                for path in ('plus', 'minus', 'alt'):
                    std = rv(R_at(bb, d, cond, path, 2 * N)); dec_ = rv(R_at(bb, d, dname, path, 2 * N))
                    if std is None or dec_ is None: continue
                    c = dict(backbone=bb, domain=d, S=cond[2:], path=path, ideal=v['category'][path], std=category(std), dcp=category(dec_), std_R=std, dcp_R=dec_)
                    allc[f'{bb}/{d}/{cond[2:]}/{path}'] = c
                    if c['std'] != c['ideal']: C.append(c)
    def d1(cs):
        if len(cs) < 6: return dict(n=len(cs), verdict='not evaluable')
        cp = float(np.mean([c['dcp'] == c['ideal'] for c in cs])); rd = float(np.mean([c['dcp'] == c['std'] for c in cs]))
        return dict(n=len(cs), frac_coupling=cp, frac_readout=rd, verdict='H-coupling' if cp >= .75 else 'H-readout' if rd >= .75 else 'mixed')
    out = dict(cells=allc, D1=dict(d1(C), per_backbone={bb: d1([c for c in C if c['backbone'] == bb]) for bb in bbs}), D2={})
    for bb in bbs:
        std = [rv(R_at(bb, 'hour', f'F_{{{j}}}', 'plus', 24)) for j in range(2, 7)]; dcp = [rv(R_at(bb, 'hour', f'D_{{{j}}}', 'plus', 24)) for j in range(2, 7)]
        if None in std or None in dcp: out['D2'][bb] = dict(verdict='not evaluable (missing)'); continue
        gate = sum(x < .90 for x in std) >= 3; k = sum(x >= .90 for x in dcp)
        out['D2'][bb] = dict(std=std, dcp=dcp, gate=gate, n_composable=k, verdict='not evaluable (gate)' if not gate else 'H-coupling' if k >= 4 else 'H-readout' if k <= 1 else 'mixed')
    vs = [out['D1']['verdict']] + [v['verdict'] for v in out['D2'].values()]; ev = [v for v in vs if not v.startswith('not')]
    out['Q15'] = dict(verdict='not decidable' if not ev else 'H-coupling' if all(v == 'H-coupling' for v in ev) else 'H-readout' if all(v == 'H-readout' for v in ev) else 'mixed')
    return out


# ---------------------------------------------------------------- F
F_CELLS = [('month', 11), ('month', 12), ('hour', 14), ('compass8', 10)]


def traj(bb, d, method, path, k):
    return {r['world_id']: float(r['trajectory_success']) for r in recs(bb, d, method, path) if r['step'] == k}


def f_unit():
    out = dict(cells={})
    for d, r in F_CELLS:
        N = len(S.states(d)); a = traj('t5', d, f'FF{r}', 'plus', 2 * N); b = traj('t5', d, f'RRR{r}', 'plus', 2 * N)
        if not a or not b: out['cells'][f'{d}/r{r}'] = dict(verdict='missing'); continue
        ws = sorted(set(a) & set(b)); ci = lcore.boot_diff_ci(ws, np.array([a[w] for w in ws]), np.array([b[w] for w in ws]))
        rrr, ff = float(np.mean(list(b.values()))), float(np.mean(list(a.values())))
        gate = rrr <= .70
        v = None if not gate else 'H-alloc' if ff >= .90 and ci['ci95'][0] >= .20 else 'H-capacity' if ci['diff'] <= .05 else 'neither'
        out['cells'][f'{d}/r{r}'] = dict(RRR=rrr, FF=ff, dR=ci, gate=gate, verdict=v)
    ev = [c for c in out['cells'].values() if c.get('gate')]
    if not ev: out['Q16'] = dict(verdict='not evaluable', n=0)
    else:
        fa = np.mean([c['verdict'] == 'H-alloc' for c in ev]); fc = np.mean([c['verdict'] == 'H-capacity' for c in ev])
        out['Q16'] = dict(n=len(ev), frac_alloc=float(fa), frac_capacity=float(fc), verdict='H-alloc' if fa >= .75 else 'H-capacity' if fc >= .75 else 'mixed')
    out['exploratory_bart_grid'] = {f'{d}/r{r}': dict(RRR=rv(R_at('bart', d, f'RRR{r}', 'plus', 2 * len(S.states(d)))), FF=rv(R_at('bart', d, f'FF{r}', 'plus', 2 * len(S.states(d)))))
                                    for d in GRID_DOMAINS for r in grid_ranks('bart', d)}
    out['exploratory_t5_r13'] = {d: dict(RRR=rv(R_at('t5', d, 'RRR13', 'plus', 24)), FF=rv(R_at('t5', d, 'FF13', 'plus', 24))) for d in ('month', 'hour')}
    return out


# ---------------------------------------------------------------- B
def b_unit():
    med = lambda d, kind, k: (lambda v: None if None in v else float(np.median(v)))([rv(R_at('bart', d, f'{kind}U_s{s}', 'plus', k)) for s in SEEDS])
    b1 = {f'{k}/{d}': med(d, k, 30) for k in ('Att1', 'Att2') for d in ('name3', 'bind3fix')}; out = dict(B1=dict(R30=b1))
    vals = list(b1.values())
    out['B1']['verdict'] = 'not evaluable' if None in vals else 'H-stable' if all(v >= .95 for v in vals) else 'H-unstable' if all(v <= .50 for v in vals) else 'mixed'
    a1, a2 = med('bind3', 'Att1', 6), med('bind3', 'Att2', 6); mx = None if a1 is None or a2 is None else max(a1, a2)
    out['B2'] = dict(Att1U=a1, Att2U=a2, max=mx, verdict='not evaluable' if mx is None else 'H-train' if mx >= .90 else 'H-deep' if mx <= .50 else 'mixed')
    t = med('bind3', 'Tok', 6); out['B3'] = dict(TokU=t, holds=None if t is None else t <= .20); out['Q17'] = dict(verdict=out['B2']['verdict'])
    out['table'] = {f'{d}/{m}': {f'R{k}': rv(R_at('bart', d, m, 'plus', k)) for k in (1, 6, 30)} | dict(minus6=rv(R_at('bart', d, m, 'minus', 6)), alt6=rv(R_at('bart', d, m, 'alt', 6)))
                    for d in B_DOMAINS for m in [f'{k}U_s{s}' for k in ('Tok', 'Att1', 'Att2') for s in SEEDS] + [f'AttL2v4_s{s}' for s in SEEDS] + ['RRR32', 'reencode']}
    f = ROOT / 'results/b_complete.json'; out['attention_bind3'] = read(f)['attention_bind3'] if f.exists() else None
    return out


# ---------------------------------------------------------------- N
def n_unit(p, sims, bbs):
    out = dict(N1={}, N2={}, N3={}, N4={}, N5={}, N6={})
    for bb in bbs:
        doms = p['gates'][bb]['N_domains']; tabs = {}; recsN4 = []
        for d in doms:
            N = len(S.states(d)); out['N1'][f'{bb}/{d}'] = rv(R_at(bb, d, 'F_empty', 'plus', 2 * N))
            c1 = [(rv(R_at(bb, d, f'C1n_s{s}', 'plus', 1)), rv(R_at(bb, d, f'C1n_s{s}', 'plus', 2))) for s in SEEDS]
            c1 = [x for x in c1 if None not in x]
            if c1:
                r1, r2 = float(np.median([x[0] for x in c1])), float(np.median([x[1] for x in c1]))
                out['N2'][f'{bb}/{d}'] = dict(R1=r1, R2=r2, cls='H-general' if r1 >= .90 and r2 <= .20 else 'H-template' if r1 <= .50 else 'neither')
            pc = p['simulate'][bb]['N3_precheck'].get(f'{bb}/{d}', {})
            if pc.get('included'):
                pl = recs(bb, d, 'F_{1}', 'plus'); A = A_by_disp(pl, N) if pl and steps_of(pl) >= 2 * N else None
                rp, ra = rv(R_at(bb, d, 'F_{1}', 'plus', 2 * N)), rv(R_at(bb, d, 'F_{1}', 'alt', 2 * N))
                dA = None if A is None else A[1] - A[N // 2]
                out['N3'][f'{bb}/{d}'] = dict(plus=rp, alt=ra, A1_minus_Ahalf=dA, holds=None if None in (rp, ra, dA) else rp <= .20 and ra >= .80 and dA >= .50)
            else: out['N3'][f'{bb}/{d}'] = dict(excluded_at_lock=True)
            for m in ('F_{1}', 'F_not1'):
                for path in ('plus', 'minus', 'alt'): recsN4 += [r for r in recs(bb, d, m, path) if r.get('decoded_state') is not None]
            if bb == 'bart':
                v = [rv(R_at(bb, d, f'C3U4n_s{s}', 'plus', 2 * N)) for s in SEEDS]; v = [x for x in v if x is not None]
                out['N5'][d] = float(np.median(v)) if v else None
            for key, c in p['simulate'][bb]['cells'].items():
                if c['unit'] != 'N' or c['domain'] != d or c['family'] != 'state': continue
                rs, _ = merged(bb, d, c['method'], c['path'], sims, unit='N')
                if rs: tabs[key] = lcore.world_table(rs, min(2 * N, steps_of(rs)), latent='argmax_locked')
        if recsN4:
            w = [r['world_id'] for r in recsN4]; ag = {k: np.array([r[f'argmax_{k}'] == r['decoded_state'] for r in recsN4], float) for k in ('full', 'equal', 'fund')}
            fe = lcore.boot_diff_ci(w, ag['full'], ag['equal']); ff = lcore.boot_diff_ci(w, ag['full'], ag['fund'])
            out['N4'][bb] = dict(n=len(recsN4), agreement={k: float(v.mean()) for k, v in ag.items()}, fit_minus_equal=fe, fit_minus_fund=ff,
                                 holds=float(ag['full'].mean()) >= .85 and ff['ci95'][0] > .10)
        if tabs: pl = lcore.pooled(tabs); out['N6'][bb] = dict(agreement=pl['latent'], naive=pl['naive'], holds=pl['latent'] >= .85)
    n1 = [v for v in out['N1'].values() if v is not None]; bart = [v for k, v in out['N1'].items() if k.startswith('bart/') and v is not None]
    out['N1']['verdict'] = 'H-general' if n1 and all(v >= .90 for v in n1) else 'H-template' if bart and sum(v <= .50 for v in bart) >= 2 / 3 * len(bart) else 'neither'
    n3 = [v['holds'] for v in out['N3'].values() if isinstance(v, dict) and 'holds' in v]
    out['N3_holds'] = None if not n3 or None in n3 else all(n3)
    n4 = [v['holds'] for v in out['N4'].values()]; out['N4_holds'] = bool(n4) and all(n4)
    g = out['N1']['verdict'] == 'H-general' and out['N3_holds'] is True and out['N4_holds']
    out['Q18'] = dict(verdict='H-general' if g else 'H-template' if out['N1']['verdict'] == 'H-template' else 'mixed')
    if not any(p['gates'][bb]['N_domains'] for bb in bbs):   # PLAN 5.3 GB: every domain left N before the lock
        out['N1']['verdict'] = None
        out['Q18'] = dict(verdict='not evaluable', reason='GB: no (backbone, multi-template domain) reached dev one-way plus R_2N >= 0.95 with RRR-16 or RRR-32',
                          GB={bb: {d: {r: v['rate'] for r, v in g_['dev_R2N'].items()} for d, g_ in p['gates'][bb]['GB'].items() if 'dev_R2N' in g_} for bb in bbs})
    return out


# ---------------------------------------------------------------- chains.csv and figures
def tables(sims):
    out = []
    for (bb, d, m, path), rs in sorted(CH.items()):
        by = defaultdict(list)
        for r in rs: by[r['step']].append(r)
        unit = 'B' if d in B_DOMAINS else 'N' if d.endswith('-mt') else 'L'; sim = sims.get(f'{unit}/{bb}/{d}/{m}/{path.replace("_from_start", "")}')
        idx = {w: i for i, w in enumerate(sim['world_ids'])} if sim else {}
        for t in sorted(by):
            g = by[t]; lat = None
            if sim and t <= len(sim['states'][0]): lat = float(np.mean([sim['argmax']['full'][idx[r['world_id']]][t - 1] == r['state'] for r in g]))
            out.append(dict(backbone=bb, domain=d, method=m, path=path, t=t, n=len(g), A_t=float(np.mean([r['success'] for r in g])),
                            R_t=float(np.mean([r['trajectory_success'] for r in g])), latent_readout_correct=lat))
    return out


def save(fig, name):
    fig.tight_layout(); fig.savefig(FIGS / f'{name}.png', dpi=140); fig.savefig(FIGS / f'{name}.svg'); import matplotlib.pyplot as plt; plt.close(fig)


def figures(p, L, D, B, N, bbs):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    FIGS.mkdir(exist_ok=True); col = dict(freeze='#1f77b4', grid='#2ca02c', C3='#d62728', CE='#9467bd')
    kind = lambda m, fam: 'freeze' if m.startswith('F_') else 'grid' if m.startswith(('RRR', 'FF')) else 'CE' if fam == 'CE' else 'C3'
    fig, axs = plt.subplots(1, len(bbs), figsize=(5.5 * len(bbs), 5), squeeze=False)
    for ax, bb in zip(axs[0], bbs):
        seen = set()
        for key, c in L['cells'].items():
            if key.split('/')[1] != bb: continue
            k = kind(key.split('/')[3], c['family']); lab = k if k not in seen else None; seen.add(k)
            ax.scatter(c['obs_rate'], c['pred_rate'], s=12, c=col[k], alpha=.7, label=lab, marker='o' if not c['new'] else 'x')
        nv = [(c['obs_rate'], c['naive_rate']) for key, c in L['cells'].items() if key.split('/')[1] == bb]
        if nv: ax.scatter(*zip(*nv), s=6, c='grey', alpha=.35, marker='.', label='naive (step-1 success)')
        ax.plot([0, 1], [0, 1], 'k:', lw=.8); ax.set_xlabel('observed chain success rate (R_2N)'); ax.set_ylabel('predicted (latent) / naive'); ax.set_title(f'{bb}: latent prediction per cell (x = new editor)')
        ax.legend(fontsize=7)
    save(fig, 'l_scatter')
    fig, ax = plt.subplots(figsize=(6, 5))
    for c in L['L3']['cells'].values():
        if c['D'] is None: continue
        ax.scatter(c['D'], c['R2N'], c=col['CE'] if c['family'] == 'CE' else col['C3'], marker='o' if c['family'] == 'CE' else 's', s=18, alpha=.7)
    ax.scatter([], [], c=col['CE'], marker='o', label='CE family'); ax.scatter([], [], c=col['C3'], marker='s', label='C3 (state) family')
    ax.axvline(.5, ls=':', c='k'); ax.set_xlabel('step-1 disagreement D'); ax.set_ylabel('one-way R_2N'); ax.legend(fontsize=8); ax.set_title('L3: D vs composability (editor x domain x direction)')
    save(fig, 'l_D_vs_R2N')
    doms = [d for d in ('hour', 'month')]; fig, axs = plt.subplots(len(bbs), len(doms), figsize=(6 * len(doms), 4 * len(bbs)), squeeze=False)
    for i, bb in enumerate(bbs):
        for j, d in enumerate(doms):
            ax = axs[i][j]; N = len(S.states(d))
            for cond, ls in (('{1}', '-'), ('not1', '--'), ('{4}', '-.')):
                for meth, c in ((f'F_{cond}', '#1f77b4'), (f'D_{cond}', '#d62728')):
                    rs = recs(bb, d, meth, 'plus')
                    if not rs: continue
                    by = defaultdict(list)
                    for r in rs: by[r['step']].append(r['success'])
                    ax.plot(sorted(by), [np.mean(by[t]) for t in sorted(by)], ls=ls, c=c, label=f'{meth} observed')
                ia = p['idealized_D'][bb][d].get(f'F_{cond}', {}).get('category', {}).get('plus')
                if ia: ax.text(2 * N, .02 + .06 * ['{1}', 'not1', '{4}'].index(cond), f'ideal F_{cond}: {ia}', ha='right', fontsize=7)
            ax.set_title(f'{bb} {d}: standard F_S (blue) vs decoupled D_S (red), plus'); ax.set_xlabel('step t'); ax.set_ylabel('A_t'); ax.legend(fontsize=6)
    save(fig, 'd_curves')
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    for ax, d in zip(axs, B_DOMAINS):
        for m, c in (('TokU', '#1f77b4'), ('Att1U', '#d62728'), ('Att2U', '#ff7f0e'), ('AttL2v4', '#7f7f7f')):
            curves = []
            for s in SEEDS:
                rs = recs('bart', d, f'{m}_s{s}', 'plus')
                if rs:
                    by = defaultdict(list)
                    for r in rs: by[r['step']].append(r['trajectory_success'])
                    curves.append([np.mean(by[t]) for t in sorted(by)])
            if curves: ax.plot(range(1, len(curves[0]) + 1), np.median(np.array(curves), 0), c=c, label=f'{m} (seed median)')
        ax.set_title(f'B {d}: one-way plus R_k'); ax.set_xlabel('k'); ax.set_ylim(-.02, 1.02); ax.legend(fontsize=7)
    save(fig, 'b_Rk')
    nd = [(bb, d) for bb in bbs for d in p['gates'][bb]['N_domains']]
    if nd:
        fig, axs = plt.subplots(2, len(nd), figsize=(4.5 * len(nd), 7), squeeze=False)
        for j, (bb, d) in enumerate(nd):
            for meth, c in (('F_{1}', '#1f77b4'), ('F_not1', '#d62728')):
                rs = recs(bb, d, meth, 'plus')
                if rs:
                    by = defaultdict(list)
                    for r in rs: by[r['step']].append(r['success'])
                    axs[0][j].plot(sorted(by), [np.mean(by[t]) for t in sorted(by)], c=c, label=meth)
            axs[0][j].set_title(f'{bb} {d} (held-out templates): A_t'); axs[0][j].legend(fontsize=7)
            for meth, c in (('C1n', '#9467bd'), ('C3U4n', '#2ca02c')):
                cur = []
                for s in SEEDS:
                    rs = recs(bb, d, f'{meth}_s{s}', 'plus')
                    if rs:
                        by = defaultdict(list)
                        for r in rs: by[r['step']].append(r['trajectory_success'])
                        cur.append([np.mean(by[t]) for t in sorted(by)])
                if cur: axs[1][j].plot(range(1, len(cur[0]) + 1), np.median(np.array(cur), 0), c=c, label=f'{meth} (seed median)')
            axs[1][j].set_title(f'{bb} {d}: R_t'); axs[1][j].legend(fontsize=7)
        save(fig, 'n_curves')


def main():
    global SM, FIGS
    require_slurm(); SM = '--smoke' in sys.argv; t0 = time.time()
    if SM:
        import lock; p = lock.sections(bbs=tuple(b for b in ('bart', 't5') if (ROOT / f'results/simulate_{b}_summary.json').exists())); bbs = list(p['simulate'])
        sims = load_sims(bbs, ROOT / 'local/smoke'); load_chains([ROOT / f'local/smoke/shards_{b}' for b in bbs]); FIGS = ROOT / 'local/smoke/figs'
        p['simulate'] = {b: read(ROOT / f'local/smoke/simulate_{b}_summary.json') for b in bbs}
    else:
        p = verify_protocol5(); bbs = ['bart', 't5']; sims = load_sims(bbs, ROOT / 'results'); load_chains([lib5.SHARDS])
        for bb in bbs: assert read(ROOT / f'results/g50_{bb}.json')['pass']
    L = l_unit(p, sims, bbs); D = d_unit(p, bbs); F = f_unit() if 't5' in bbs else {}; B = b_unit() if 'bart' in bbs else {}; N = n_unit(p, sims, bbs)
    out = dict(L=L | dict(cells=L['cells']), D=D, F=F, B=B, N=N,
               verdicts=dict(Q14=L['Q14']['verdict'], L1=L['L1']['verdict'], L2=L['L2']['verdict'], Q14prime=L['Q14prime']['verdict'], Q11prime=L.get('L4', {}).get('verdict'),
                             Q15=D['Q15']['verdict'], Q16=F.get('Q16', {}).get('verdict'), Q17=B.get('Q17', {}).get('verdict'), B1=B.get('B1', {}).get('verdict'),
                             Q18=N['Q18']['verdict']),
               consistency=dict(argmax_mismatches=L['mismatches']), protocol_sha256=sha(ROOT / 'protocol.json') if not SM else None,
               lock=read(ROOT / 'protocol_lock.json') if (ROOT / 'protocol_lock.json').exists() and not SM else None, seconds=time.time() - t0)
    dst = ROOT / ('local/smoke' if SM else 'results'); dump(dst / 'predictions.json', out); csvwrite(dst / 'chains.csv', tables(sims))
    figures(p, L, D, B, N, bbs); print(json.dumps(out['verdicts'], indent=1), 'mismatches', L['mismatches'], flush=True)


if __name__ == '__main__':
    main()
