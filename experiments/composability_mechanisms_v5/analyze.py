"""Analysis (CPU, after all post-lock chains; PLAN B5-B7, B10). Verdicts follow protocol.json (predictions and operational rules).
The latent predictions are the locked simulation files (results/simulate_<bb>.json.gz); the argmaxes recorded inside the post-lock
chains are compared with them (consistency). Outputs: results/predictions.json, results/paper_export.json, results/chains.csv,
figs/*.png and *.svg. --smoke: every unit on the dev smoke shards (local/smoke) with the dev simulations (no verdict is meaningful)."""
import gzip
import hashlib
import json
import time
from collections import defaultdict
import lib6
from lib6 import *
import lcore

FIGS = ROOT / 'figs'
SM = False
HZ = lambda N: 3 if SM else 2 * N                   # C-unit horizon; smoke chains have 3 steps (dev check of the code path only)


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
    return CH.get((bb, d, method, path if path.endswith('_from_start') else f'{path}_from_start'), [])


def steps_of(rs):
    return max(r['step'] for r in rs) if rs else 0


def R_at(bb, d, method, path, k):
    rs = recs(bb, d, method, path)
    if not rs or steps_of(rs) < k: return None
    return chain_rate(bb, d, 'natural', method, f'{path}_from_start', k, recs=rs)


def rv(x): return None if x is None else x['rate']


def med(v):
    v = [x for x in v if x is not None]; return float(np.median(v)) if v else None


def merged(unit, bb, d, method, path, sims):
    """Observed records with the locked readouts merged in (argmax_locked_<readout>); counts mismatches with the recorded argmaxes."""
    rs = recs(bb, d, method, path); sim = sims.get(f'{unit}/{bb}/{d}/{method}/{path}')
    if not rs or sim is None: return None, 0
    idx = {w: i for i, w in enumerate(sim['world_ids'])}; out = []; mm = 0
    for r in rs:
        i = idx[r['world_id']]; t = r['step'] - 1
        if t >= len(sim['states'][i]): continue
        assert sim['states'][i][t] == r['state']; q = dict(r)
        for k, v in sim['argmax'].items():
            q[f'argmax_locked_{k}'] = v[i][t]
            if f'argmax_{k}' in r and r[f'argmax_{k}'] != v[i][t]: mm += 1
        out.append(q)
    return out, mm


def table(unit, bb, d, method, path, sims, latent='argmax_locked_full'):
    rs, mm = merged(unit, bb, d, method, path, sims); N = len(S.states(d))
    if not rs or steps_of(rs) < 2 * N: return None, mm
    return lcore.world_table(rs, 2 * N, latent), mm


# ---------------------------------------------------------------- M
def m_unit(p, sims, bbs):
    out = dict(M1={}, M2={}, M3={}, M4={}, M5=dict(cells={}), exploratory=dict(SC3U4={}, reference={}, distractor={}), mismatches=0)
    for bb in bbs:
        g = p['gates'][bb]; tabs = {}
        for d in g['M_domains']:
            N = len(S.states(d)); out['M1'][f'{bb}/{d}'] = rv(R_at(bb, d, 'F_empty', 'plus', 2 * N))
            r1, r2, Ds = [], [], []
            for s in SEEDS:
                st = p['train_new'][bb]['M'].get(f'C1n/{d}/s{s}')
                if not st or st['status'] != 'ok': r1.append(0.); r2.append(0.); continue
                r1.append(rv(R_at(bb, d, f'C1n_s{s}', 'plus', 1))); r2.append(rv(R_at(bb, d, f'C1n_s{s}', 'plus', 2)))
                t, mm = table('M', bb, d, f'C1n_s{s}', 'plus', sims); out['mismatches'] += mm
                if t: Ds.append(lcore.cell_summary(t)['D'])
            R1, R2, Dm = med(r1), med(r2), med(Ds)
            cls = None if None in (R1, R2) else 'H-general' if R1 >= .90 and R2 <= .20 and Dm is not None and Dm >= .8 else 'H-template' if R1 <= .50 else 'neither'
            out['M2'][f'{bb}/{d}'] = dict(R1=R1, R2=R2, D=Dm, cls=cls)
            pc = p['M3_precheck'].get(f'{bb}/{d}', {})
            if pc.get('included'):
                pl = recs(bb, d, 'F_{1}', 'plus'); A = A_by_disp(pl, N) if pl and steps_of(pl) >= 2 * N else None
                rp, ra = rv(R_at(bb, d, 'F_{1}', 'plus', 2 * N)), rv(R_at(bb, d, 'F_{1}', 'alt', 2 * N)); dA = None if A is None else A[1] - A[N // 2]
                out['M3'][f'{bb}/{d}'] = dict(plus=rp, alt=ra, A1_minus_Ahalf=dA, holds=None if None in (rp, ra, dA) else rp <= .20 and ra >= .80 and dA >= .50)
            else: out['M3'][f'{bb}/{d}'] = dict(excluded_at_lock=True, precheck=pc)
            for key, c in p['simulate'][bb]['cells'].items():
                if c['unit'] != 'M' or c['domain'] != d: continue
                t, mm = table('M', bb, d, c['method'], c['path'], sims); out['mismatches'] += mm
                if t is None: continue
                s_ = lcore.cell_summary(t)
                if c['family'] == 'state': tabs[key] = t
                if c['method'].startswith(('C1n', 'SC3U4')) and c['path'] in ('plus', 'minus'):
                    ok = (s_['D'] is not None and s_['D'] >= .5 and s_['obs_rate'] <= .20) if c['family'] == 'CE' else (s_['D'] is not None and s_['D'] <= .20)
                    out['M5']['cells'][key] = dict(family=c['family'], D=s_['D'], R2N=s_['obs_rate'], holds=ok)
                if c['method'].startswith('SC3U4'): out['exploratory']['SC3U4'][key] = s_['obs_rate']
                if c['method'] in ('RRR16full', 'F_empty'): out['exploratory']['reference'][key] = s_['obs_rate']
            ws = {w['world_id']: w for w in worlds5(d, 'dev' if SM else CONFIRM)}; tm = S.mt_templates()[d]; byY = defaultdict(list); keep = []
            for r in recs(bb, d, 'F_empty', 'plus'):
                w = ws[r['world_id']]
                if r['step'] == 2 * N: byY[tm[w['template_id']]['has_Y']].append(r['trajectory_success'])
                if tm[w['template_id']]['has_Y']: keep.append(S.word(d, w['distractor']) in r['text'])
            out['exploratory']['distractor'][f'{bb}/{d}'] = dict(R2N_with_Y=med([np.mean(byY[True])]) if byY[True] else None, R2N_without_Y=med([np.mean(byY[False])]) if byY[False] else None,
                                                                 distractor_retention=float(np.mean(keep)) if keep else None,
                                                                 per_template={str(t): float(np.mean([r['trajectory_success'] for r in recs(bb, d, 'F_empty', 'plus') if r['step'] == 2 * N and ws[r['world_id']]['template_id'] == t]))
                                                                               for t in sorted({w['template_id'] for w in ws.values()})})
        if tabs:
            pl = lcore.pooled(tabs, boot=lcore.boot_diff_ci); cat = float(np.mean([lcore.cell_summary(t)['cat_match'] for t in tabs.values()]))
            ci = pl.get('latent_minus_naive', {}).get('ci95', [None])[0]
            out['M4'][bb] = dict(cells=len(tabs), agreement=pl['latent'], naive=pl['naive'], majority_reference=pl['majority_reference'], latent_minus_naive=pl.get('latent_minus_naive'),
                                 category_accuracy=cat, holds=pl['latent'] >= .85 and ci is not None and ci > 0 and cat >= .80, template_side=pl['latent'] < .75)
    m1 = [v for v in out['M1'].values() if v is not None]; bart = [v for k, v in out['M1'].items() if k.startswith('bart/') and v is not None]
    out['M1']['verdict'] = 'H-general' if m1 and all(v >= .90 for v in m1) else 'H-template' if bart and sum(v <= .50 for v in bart) >= 2 / 3 * len(bart) else 'neither'
    cls = [v['cls'] for v in out['M2'].values()]
    out['M2']['verdict'] = 'H-general' if cls and all(c == 'H-general' for c in cls) else 'H-template' if cls and all(c == 'H-template' for c in cls) else 'neither'
    m3 = [v['holds'] for v in out['M3'].values() if isinstance(v, dict) and 'holds' in v]
    out['M3_holds'] = None if not m3 or None in m3 else all(m3)
    m4 = [v['holds'] for v in out['M4'].values()]; out['M4_holds'] = bool(m4) and all(m4)
    m5 = [v['holds'] for v in out['M5']['cells'].values()]; out['M5']['frac'] = float(np.mean(m5)) if m5 else None; out['M5']['holds'] = bool(m5) and np.mean(m5) >= .90
    if not any(p['gates'][bb]['M_domains'] for bb in bbs): out['Q18prime'] = dict(verdict='not evaluable', reason='GM removed every domain')
    else:
        g_ = out['M1']['verdict'] == 'H-general' and out['M3_holds'] is not False and out['M4_holds']
        out['Q18prime'] = dict(verdict='H-general' if g_ else 'H-template' if out['M1']['verdict'] == 'H-template' else 'mixed', M3_not_evaluable=out['M3_holds'] is None)
    return out


# ---------------------------------------------------------------- C
def c_unit(p, sims):
    out = dict(cells={}, mismatches=0); recs_set = defaultdict(lambda: dict(w=[], slot=[], ctx=[], cat_slot=[], cat_ctx=[]))
    for key, c in p['simulate']['bart']['cells'].items():
        if c['unit'] != 'C': continue
        rs, mm = merged('C', 'bart', c['domain'], c['method'], c['path'], sims); out['mismatches'] += mm; N = len(S.states(c['domain']))
        if not rs or steps_of(rs) < HZ(N): continue
        ts = lcore.world_table(rs, HZ(N), 'argmax_locked_full'); tc = lcore.world_table(rs, HZ(N), 'argmax_locked_ctx')
        ss, sc = lcore.cell_summary(ts), lcore.cell_summary(tc); r = recs_set[c['set']]
        for w in ts: r['w'].append(w); r['slot'].append(float(ts[w]['pred'] == ts[w]['obs'])); r['ctx'].append(float(tc[w]['pred'] == tc[w]['obs']))
        r['cat_slot'].append(ss['cat_match']); r['cat_ctx'].append(sc['cat_match'])
        out['cells'][key] = dict(set=c['set'], obs=ss['obs_rate'], pred_slot=ss['pred_rate'], pred_ctx=sc['pred_rate'], cat_slot=ss['cat_match'], cat_ctx=sc['cat_match'],
                                 agree_slot=ss['world_agree'], agree_ctx=sc['world_agree'], naive=ss['naive_rate'])
    for s_, r in recs_set.items():
        ci = lcore.boot_diff_ci(r['w'], np.array(r['ctx']), np.array(r['slot']))
        out[s_] = dict(cells=len(r['cat_slot']), records=len(r['w']), agree_slot=float(np.mean(r['slot'])), agree_ctx=float(np.mean(r['ctx'])), ctx_minus_slot=ci,
                       category_slot=float(np.mean(r['cat_slot'])), category_ctx=float(np.mean(r['cat_ctx'])))
    t1, t2 = out.get('CT1'), out.get('CT2')
    if t1: t1['holds'] = t1['category_ctx'] >= .80 and t1['ctx_minus_slot']['ci95'][0] > 0; t1['slot_side'] = t1['ctx_minus_slot']['ci95'][0] <= 0 <= t1['ctx_minus_slot']['ci95'][1]
    if t2: t2['holds'] = t2['ctx_minus_slot']['diff'] >= -.01 and t2['ctx_minus_slot']['ci95'][0] > -.02
    out['Q19'] = dict(verdict='not evaluable' if not (t1 and t2) else 'H-context' if t1['holds'] and t2['holds'] else 'H-slot' if t1['slot_side'] else 'mixed')
    newc = defaultdict(list)
    for key, c in out['cells'].items():
        _, _, d, m, path = key.split('/')
        if m.startswith('C3n') and path == 'plus': newc[f"{d}/{m.split('_')[0]}"].append(c['obs'])
    out['exploratory'] = dict(new_C3_plus_R2N_by_updates={k: med(v) for k, v in sorted(newc.items())})
    first = defaultdict(lambda: dict(slot_first=0, ctx_first=0, same_step=0, neither=0))
    for key, c in out['cells'].items():
        if c['set'] != 'CT1': continue
        _, _, d, m, path = key.split('/'); rs, _ = merged('C', 'bart', d, m, path, sims); by = defaultdict(dict)
        for r in rs: by[r['world_id']][r['step']] = r
        for w, st in by.items():
            if st[max(st)]['trajectory_success']: continue
            fs = next((t for t in sorted(st) if st[t]['argmax_locked_full'] != st[t]['state']), None); fc = next((t for t in sorted(st) if st[t]['argmax_locked_ctx'] != st[t]['state']), None)
            k = 'neither' if fs is None and fc is None else 'slot_first' if fc is None or (fs is not None and fs < fc) else 'ctx_first' if fs is None or fc < fs else 'same_step'
            first[f'{d}/{path}'][k] += 1
    out['exploratory']['first_wrong_readout_in_failed_worlds'] = dict(first)
    drift = defaultdict(lambda: ([], []))                      # declared exploratory: max context drift vs failure among slot-predicted successes
    for key, c in out['cells'].items():
        _, _, d, m, path = key.split('/'); sim = sims.get(f'C/bart/{d}/{m}/{path}')
        if not sim or 'ctx_drift' not in sim: continue
        rs, _ = merged('C', 'bart', d, m, path, sims); N = len(S.states(d)); t = lcore.world_table(rs, HZ(N), 'argmax_locked_full'); idx = {w: i for i, w in enumerate(sim['world_ids'])}
        for w, x in t.items():
            if x['pred']: drift[c['set']][0].append(max(sim['ctx_drift'][idx[w]][:HZ(N)])); drift[c['set']][1].append(not x['obs'])
    def auc(s, y):
        s, y = np.array(s), np.array(y, bool)
        if y.all() or not y.any(): return None
        r = np.argsort(np.argsort(s)) + 1.0; return float((r[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum()))
    out['exploratory']['ctx_drift_auc_failure_among_slot_predicted_success'] = {k: dict(n=len(v[0]), failures=int(np.sum(v[1])), auc=auc(*v)) for k, v in drift.items()}
    groups = defaultdict(list)                                 # DEVIATIONS #11: identical latent trajectories incl. the continuous drift (same editor weights)
    for key in out['cells']:
        _, _, d, m, path = key.split('/'); sim = sims.get(f'C/bart/{d}/{m}/{path}')
        if sim: groups[hashlib.sha256(json.dumps([d, path, sim['states'], sim['argmax'], sim.get('ctx_drift')], sort_keys=True).encode()).hexdigest()].append(key)
    out['exploratory']['identical_cells'] = sorted(sorted(v) for v in groups.values() if len(v) > 1)
    return out


# ---------------------------------------------------------------- K
def k_unit(p):
    out = dict(table={}); trK = p['train_new']['bart']['K']
    def R(d, name, k):
        vals = []
        for s in SEEDS:
            st = trK.get(f'{name}/{d}/s{s}')
            if st is not None and st['status'] != 'ok': vals.append(0.); continue
            vals.append(rv(R_at('bart', d, f'{name}_s{s}', 'plus', k)))
        return med(vals)
    for d in K_DOMAINS:
        for name in ('ORU4', 'Att2LU4', 'Att2LU8', 'Att1U8', 'TokU', 'Att1U', 'Att2U'):
            if name == 'ORU4' and d == 'name3': continue
            out['table'][f'{d}/{name}'] = {f'R{k}': R(d, name, k) for k in (1, 4, 6, 8, 12, 30)} | dict(
                minus12=med([rv(R_at('bart', d, f'{name}_s{s}', 'minus', 12)) for s in SEEDS]), alt12=med([rv(R_at('bart', d, f'{name}_s{s}', 'alt', 12)) for s in SEEDS]))
        out['table'][f'{d}/reencode'] = {f'R{k}': rv(R_at('bart', d, 'reencode', 'plus', k)) for k in (1, 6, 30)}
    T = out['table']; v = lambda k, f: T.get(k, {}).get(f)
    k1 = v('bind3/ORU4', 'R30'); out['K1'] = dict(R30=k1, verdict=None if k1 is None else 'H-representable' if k1 >= .90 else 'H-unrepresentable' if k1 <= .50 else 'mixed')
    mx = max([x for x in (v('bind3/Att2LU4', 'R30'), v('bind3/Att2LU8', 'R30')) if x is not None], default=None)
    hz = v('bind3/Att2LU4', 'R8') is not None and v('bind3/Att2LU4', 'R8') <= .50 and v('bind3/Att2LU8', 'R12') is not None and v('bind3/Att2LU8', 'R12') <= .50
    out['K2'] = dict(max_R30=mx, Att2LU4_R8=v('bind3/Att2LU4', 'R8'), Att2LU8_R12=v('bind3/Att2LU8', 'R12'), verdict=None if mx is None else 'H-closure' if mx >= .90 else 'H-horizon' if hz else 'mixed')
    a8, a12, a30 = v('bind3/Att1U8', 'R8'), v('bind3/Att1U8', 'R12'), v('bind3/Att1U8', 'R30')
    out['K3'] = dict(R8=a8, R12=a12, R30=a30, verdict=None if a8 is None else 'H-closure' if a30 >= .90 else 'H-horizon' if a8 >= .70 and a12 <= .50 else 'mixed')
    k4 = {f'{d}/{n}': v(f'{d}/{n}', 'R30') for d in ('name3', 'bind3fix') for n in ('ORU4', 'Att2LU4', 'Att2LU8', 'Att1U8') if not (n == 'ORU4' and d == 'name3')}
    vals = [x for x in k4.values() if x is not None]
    out['K4'] = dict(R30=k4, verdict=None if not vals else 'stable' if all(x >= .95 for x in vals) else 'unstable' if all(x <= .50 for x in vals) else 'mixed')
    out['Q17prime'] = dict(verdict=f"K1 {out['K1']['verdict']}; K2 {out['K2']['verdict']}; K3 {out['K3']['verdict']}", oracle_note='OR-U4 is a diagnostic (oracle routing), not a usable editor')
    f = ROOT / 'results/k_bart_complete.json'; out['attention_bind3'] = read(f)['attention_bind3'] if f.exists() else None
    return out


# ---------------------------------------------------------------- tables, export, figures
def tables(sims):
    out = []
    for (bb, d, m, path), rs in sorted(CH.items()):
        by = defaultdict(list)
        for r in rs: by[r['step']].append(r)
        unit = 'K' if d in K_DOMAINS else 'M' if d.endswith('-mt') else 'C'; sim = sims.get(f'{unit}/{bb}/{d}/{m}/{path.replace("_from_start", "")}')
        idx = {w: i for i, w in enumerate(sim['world_ids'])} if sim else {}
        for t in sorted(by):
            g = by[t]; lat = ctx = None
            if sim and t <= len(sim['states'][0]):
                lat = float(np.mean([sim['argmax']['full'][idx[r['world_id']]][t - 1] == r['state'] for r in g]))
                if 'ctx' in sim['argmax']: ctx = float(np.mean([sim['argmax']['ctx'][idx[r['world_id']]][t - 1] == r['state'] for r in g]))
            out.append(dict(backbone=bb, domain=d, method=m, path=path, t=t, n=len(g), A_t=float(np.mean([r['success'] for r in g])),
                            R_t=float(np.mean([r['trajectory_success'] for r in g])), latent_readout_correct=lat, ctx_readout_correct=ctx))
    return out


def export(p, M, C, K, lock):
    """results/paper_export.json: one entry per prediction (A-line W1 format)."""
    pr = p['predictions']; E = []
    add = lambda pid, q, obs, ci=None, n=None, verdict=None, kind='confirmatory': E.append(dict(id=f'v6/{pid}', plan='v6', experiment='composability_mechanisms_v5',
                                                                                               prediction=pr.get(pid), quantity=q, observed=obs, ci95=ci, n_evaluable=n, verdict=verdict,
                                                                                               kind=kind, lock_commit=lock, source='experiments/composability_mechanisms_v5/results/predictions.json'))
    add('M1', 'base plus R_2N per (backbone, domain)', {k: v for k, v in M['M1'].items() if k != 'verdict'}, n=len(M['M1']) - 1, verdict=M['M1']['verdict'])
    add('M2', 'C1 seed medians R_1, R_2, D', {k: v for k, v in M['M2'].items() if k != 'verdict'}, n=len(M['M2']) - 1, verdict=M['M2']['verdict'])
    add('M3', 'F{1} plus / alt R_2N, A(1) - A(N/2)', M['M3'], n=sum(1 for v in M['M3'].values() if 'holds' in v), verdict=M['M3_holds'])
    for bb, v in M['M4'].items(): add('M4', f'{bb}: per-world agreement / category accuracy', dict(agreement=v['agreement'], naive=v['naive'], category=v['category_accuracy']),
                                       ci=(v['latent_minus_naive'] or {}).get('ci95'), n=v['cells'], verdict=v['holds'])
    add('M5', 'fraction of M editor cells meeting the D rule', M['M5']['frac'], n=len(M['M5']['cells']), verdict=M['M5']['holds'])
    add('Q18prime', 'verdict', M['Q18prime']['verdict'], verdict=M['Q18prime']['verdict'])
    for s_ in ('CT1', 'CT2'):
        if s_ in C: add(s_, 'ctx - slot per-world agreement; ctx category accuracy', dict(agree_slot=C[s_]['agree_slot'], agree_ctx=C[s_]['agree_ctx'], category_ctx=C[s_]['category_ctx'],
                                                                                         diff=C[s_]['ctx_minus_slot']['diff']), ci=C[s_]['ctx_minus_slot']['ci95'], n=C[s_]['cells'], verdict=C[s_]['holds'])
    add('Q19', 'verdict', C['Q19']['verdict'], verdict=C['Q19']['verdict'])
    for kk in ('K1', 'K2', 'K3', 'K4'): add(kk, kk, {k: v for k, v in K[kk].items() if k != 'verdict'}, verdict=K[kk]['verdict'])
    return E


def save_fig(fig, name):
    fig.tight_layout(); fig.savefig(FIGS / f'{name}.png', dpi=140); fig.savefig(FIGS / f'{name}.svg'); import matplotlib.pyplot as plt; plt.close(fig)


def Rcurve(bb, d, m, path, field='trajectory_success'):
    rs = recs(bb, d, m, path)
    if not rs: return None
    by = defaultdict(list)
    for r in rs: by[r['step']].append(r[field])
    return [float(np.mean(by[t])) for t in sorted(by)]


def figures(p, M, C, K, bbs):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    FIGS.mkdir(exist_ok=True); md = [(bb, d) for bb in bbs for d in p['gates'][bb]['M_domains']]
    if md:
        fig, axs = plt.subplots(2, len(md), figsize=(4.5 * len(md), 7), squeeze=False)
        for j, (bb, d) in enumerate(md):
            for meth, c in (('F_empty', '#2ca02c'), ('F_{1}', '#1f77b4'), ('F_not1', '#d62728'), ('RRR16full', '#7f7f7f')):
                y = Rcurve(bb, d, meth, 'plus', 'success')
                if y: axs[0][j].plot(range(1, len(y) + 1), y, c=c, label=meth)
            axs[0][j].set_title(f'{bb} {d} (held-out templates): A_t, plus'); axs[0][j].set_xlabel('step t'); axs[0][j].set_ylim(-.02, 1.02); axs[0][j].legend(fontsize=7)
            for meth, c in (('C1n', '#9467bd'), ('SC3U4', '#ff7f0e')):
                cur = [y for y in (Rcurve(bb, d, f'{meth}_s{s}', 'plus') for s in SEEDS) if y]
                if cur: axs[1][j].plot(range(1, len(cur[0]) + 1), np.median(np.array(cur), 0), c=c, label=f'{meth} (seed median)')
            axs[1][j].set_title(f'{bb} {d}: R_t, plus'); axs[1][j].set_xlabel('step t'); axs[1][j].set_ylim(-.02, 1.02); axs[1][j].legend(fontsize=7)
        save_fig(fig, 'm_curves')
    if 'bart' in bbs and C['cells']:
        fig, axs = plt.subplots(1, 2, figsize=(11, 5))
        for ax, (field, title) in zip(axs, (('pred_slot', 'slot readout'), ('pred_ctx', 'slot + context readout'))):
            for s_, c in (('CT1', '#d62728'), ('CT2', '#1f77b4')):
                pts = [(v['obs'], v[field]) for v in C['cells'].values() if v['set'] == s_]
                if pts: ax.scatter(*zip(*pts), s=14, c=c, alpha=.7, label=f'{s_} ({"not converged" if s_ == "CT1" else "non-inferiority set"})')
            ax.plot([0, 1], [0, 1], 'k:', lw=.8); ax.set_xlabel('observed R_2N'); ax.set_ylabel('predicted R-hat_2N'); ax.set_title(f'C (BART): {title}'); ax.legend(fontsize=7)
        save_fig(fig, 'c_scatter')
    if 'bart' in bbs:
        fig, axs = plt.subplots(1, 3, figsize=(15, 4))
        cols = dict(ORU4='#000000', Att2LU4='#2ca02c', Att2LU8='#17becf', Att1U8='#d62728', TokU='#1f77b4', Att1U='#ff9896', Att2U='#ff7f0e')
        for ax, d in zip(axs, K_DOMAINS):
            for m, c in cols.items():
                cur = [y for y in (Rcurve('bart', d, f'{m}_s{s}', 'plus') for s in SEEDS) if y]
                if cur: ax.plot(range(1, len(cur[0]) + 1), np.median(np.array(cur), 0), c=c, ls='--' if m == 'ORU4' else '-', label=f'{m}{" (oracle, diagnostic)" if m == "ORU4" else ""} (seed median)')
            ax.set_title(f'K {d}: one-way plus R_k'); ax.set_xlabel('k'); ax.set_ylim(-.02, 1.02); ax.legend(fontsize=6)
        save_fig(fig, 'k_Rk')


def main():
    global SM, FIGS
    require_slurm(); SM = '--smoke' in sys.argv; t0 = time.time()
    if SM:
        import lock
        try: p = lock.sections()
        except FileNotFoundError: raise
        bbs = ['bart', 't5']; sims = load_sims(bbs, ROOT / 'local/smoke'); load_chains([ROOT / f'local/smoke/shards_{b}' for b in bbs]); FIGS = ROOT / 'local/smoke/figs'
        p['simulate'] = {b: read(ROOT / f'local/smoke/simulate_{b}_summary.json') for b in bbs}; p['predictions'] = lock.PREDICTIONS
        p['M3_precheck'] = {k: v for b in bbs for k, v in p['simulate'][b]['M3_precheck'].items()}
    else:
        p = verify_protocol6(); bbs = ['bart', 't5']; sims = load_sims(bbs, ROOT / 'results'); load_chains([lib6.SHARDS])
        for bb in bbs: assert read(ROOT / f'results/g60_{bb}.json')['pass']
    M = m_unit(p, sims, bbs); C = c_unit(p, sims); K = k_unit(p)
    lockc = read(ROOT / 'protocol_lock.json')['lock_commit'] if (ROOT / 'protocol_lock.json').exists() and not SM else None
    out = dict(M=M, C=C, K=K, verdicts=dict(Q18prime=M['Q18prime']['verdict'], M1=M['M1']['verdict'], M2=M['M2']['verdict'], M3=M['M3_holds'], M4=M['M4_holds'], M5=M['M5']['holds'],
                                            Q19=C['Q19']['verdict'], CT1=C.get('CT1', {}).get('holds'), CT2=C.get('CT2', {}).get('holds'),
                                            K1=K['K1']['verdict'], K2=K['K2']['verdict'], K3=K['K3']['verdict'], K4=K['K4']['verdict']),
               consistency=dict(argmax_mismatches=M['mismatches'] + C['mismatches']), protocol_sha256=None if SM else sha(ROOT / 'protocol.json'),
               lock=lockc, g60={bb: read(ROOT / f'results/g60_{bb}.json') for bb in bbs} if not SM else None, seconds=time.time() - t0)
    dst = ROOT / ('local/smoke' if SM else 'results'); dump(dst / 'predictions.json', out); dump(dst / 'paper_export.json', export(p, M, C, K, lockc))
    csvwrite(dst / 'chains.csv', tables(sims)); figures(p, M, C, K, bbs)
    print(json.dumps(out['verdicts'], indent=1, default=str), 'mismatches', out['consistency'], flush=True)


if __name__ == '__main__':
    main()
