"""Analysis (CPU, after every post-lock job; PLAN v7 B6-B9, B12). Verdicts follow protocol.json (predictions verbatim, operational rules,
pre-check demotions). Inputs: the locked simulations (results/simulate_<bb>.json.gz), the confirm7 shards (results/shards), and
results/g70_<bb>.json, r_run_<bb>.json, r_r4_<bb>.json, a_run_<bb>.json, k_run.json. Outputs: results/predictions.json,
results/paper_export.json, results/u_cells.csv. --smoke: the same code on the dev smoke products (local/smoke; verdicts meaningless)."""
import csv
import gzip
import hashlib
import re
import time
from collections import defaultdict
from lib7 import *
import lcore

SM = False


def boot_rate(world_ids, v):
    est, rm = lcore.cluster_boot(world_ids, np.asarray(v, float)[:, None]); return dict(rate=float(est[0]), ci95=np.quantile(rm[:, 0], [.025, .975]).tolist(), n=len(v))


def med(v):
    return float(np.median(v)) if len(v) else None


def shard_records(bb, d, method, path):
    D = ROOT / ('local/smoke/shards' if SM else 'results/shards')
    return [r for f in sorted(D.glob(f'chain_{bb}_{d}_natural_{method}_{path}_from_start_*.jsonl')) for r in rows(f)]


# ---------------------------------------------------------------- U
def u_unit(P):
    out = dict(families={}, mismatches=0, duplicates=[]); rec = defaultdict(lambda: defaultdict(list)); cells = {}; seen = {}
    for bb in ('bart', 't5'):
        f = ROOT / ('local/smoke' if SM else 'results') / f'simulate_{bb}.json.gz'
        if not f.exists(): continue
        with gzip.open(f, 'rt') as g: sims = json.load(g)
        summ = read(f.with_name(f'simulate_{bb}_summary.json'))['cells']; th = P['u_thresholds'][bb]
        for key, sim in sims.items():
            c = summ[key]; d, name, path = c['domain'], c['method'], c['path']; N = c['N']
            sig = hashlib.sha256(json.dumps([bb, d, path, sim['m'], sim['rho']]).encode()).hexdigest()
            if sig in seen: out['duplicates'].append([key, seen[sig]]); continue
            seen[sig] = key; rs = shard_records(bb, d, name.split('@')[0], path)
            if not rs: continue
            by = defaultdict(dict)
            for r in rs: by[r['world_id']][r['step']] = r
            if not all(w in by and 2 * N in by[w] for w in sim["world_ids"]):
                assert SM, f"shards of {key} do not cover the simulated worlds"; continue
            obs = []
            for i, w in enumerate(sim["world_ids"]):
                st = by[w]; obs.append(bool(st[2 * N]['trajectory_success']))
                out['mismatches'] += sum(int(st[t + 1].get('argmax_full', sim['argmax'][i][t]) != sim['argmax'][i][t]) for t in range(2 * N))
            preds = dict(slot=u_predict(sim, None, None), U=u_predict(sim, th['primary']['tau_m'], th['primary']['tau_r']),
                         U2=u_predict(sim, th['secondary']['tau_m'], th['secondary']['tau_r']), Um=u_predict(sim, th['primary']['tau_m'], None),
                         Ur=u_predict(sim, None, th['primary']['tau_r']))
            fam = c['family'] + ('' if c['family'] != 'NI' else f'_{bb}')
            cells[key] = dict(family=fam, backbone=bb, domain=d, method=name, path=path, obs=float(np.mean(obs)), **{f'pred_{k}': float(np.mean(v)) for k, v in preds.items()})
            for i, w in enumerate(sim['world_ids']):
                R = rec[fam]; R['w'].append(f'{bb}/{d}/{w}'); R['obs'].append(obs[i])
                for k, v in preds.items(): R[k].append(v[i])
            for k in preds: rec[fam][f'cat_{k}'].append(lcore.category(cells[key][f'pred_{k}']) == lcore.category(cells[key]['obs']))
    for fam, R in rec.items():
        a = {k: np.array([p == o for p, o in zip(R[k], R['obs'])], float) for k in ('slot', 'U', 'U2', 'Um', 'Ur')}
        pf = [o for p, o in zip(R['U'], R['obs']) if not p]
        out['families'][fam] = dict(cells=len(R['cat_U']), records=len(R['w']), agree={k: float(v.mean()) for k, v in a.items()},
                                    U_minus_slot=lcore.boot_diff_ci(R['w'], a['U'], a['slot']), U2_minus_slot=lcore.boot_diff_ci(R['w'], a['U2'], a['slot']),
                                    category={k: float(np.mean(R[f'cat_{k}'])) for k in ('slot', 'U', 'U2', 'Um', 'Ur')},
                                    U_pred_fail_precision=float(1 - np.mean(pf)) if pf else None, U_pred_fail=len(pf))
    F = out['families']; conf = P['precheck_U']['U1_U2_confirmatory']
    def holds(f): x = F.get(f); return None if x is None else x['U_minus_slot']['ci95'][0] > 0 and x['category']['U'] >= .85
    def ni(f): x = F.get(f); return None if x is None else x['U_minus_slot']['diff'] >= -.01 and x['U_minus_slot']['ci95'][0] > -.02
    out['U1'] = dict(holds=holds('F1'), kind='primary' if conf else 'exploratory (pre-check)'); out['U2'] = dict(holds=holds('F2'), kind=out['U1']['kind'])
    out['U3'] = dict(holds=None if any(ni(f) is None for f in ('NI_bart', 'NI_t5')) else ni('NI_bart') and ni('NI_t5'), per_backbone={f: ni(f) for f in ('NI_bart', 'NI_t5')})
    out['U4'] = dict(precision={f: v['U_pred_fail_precision'] for f, v in F.items()}, F3_gain=F.get('F3', {}).get('U_minus_slot'),
                     F2_secondary=dict(gain=F.get('F2', {}).get('U2_minus_slot'), category=F.get('F2', {}).get('category', {}).get('U2')))
    u1, u2, u3 = out['U1']['holds'], out['U2']['holds'], out['U3']['holds']
    out['Q21'] = dict(verdict='not evaluable' if None in (u1, u2, u3) else 'H-fix' if u1 and u2 and u3 else 'partial' if u3 and (u1 != u2) else 'H-nofix',
                      partial_family='F1' if u3 and u1 and not u2 else 'F2' if u3 and u2 and not u1 else None, confirmatory=conf)
    return out, cells


# ---------------------------------------------------------------- R
def r_unit(P):
    out = dict(groups={})
    def load_mode(mode):
        mode = "smoke" if SM and mode == "run" else mode; rs = []
        for bb in ('bart', 't5'):
            f = ROOT / ('local/smoke' if SM else 'results') / f'r_{mode}_{bb}.json'
            if f.exists(): rs += read(f)['cases']
        return rs
    def rates(rs, k):
        v = [r for r in rs if k in r]; return boot_rate([r['world'] for r in v], [r[k] for r in v]) if v else None
    for mode in ('run', 'r4'):
        rs = load_mode(mode)
        for g in sorted({r['group'] for r in rs}):
            for role in ('case', 'control'):
                x = [r for r in rs if r['group'] == g and r['role'] == role]
                if x: out['groups'][f'{mode}/{g}/{role}'] = {k: rates(x, k) for k in ('SNAP', 'PROJ', 'PUSH', 'CTX', 'SNAP+CTX')}
    G = out['groups']; pre = P['precheck_R']
    def r0(g): x = G.get(f'run/{g}/case', {}); return (x.get('SNAP') or {}).get('rate', 0) >= .90 if g.startswith('R-A') else (x.get('SNAP+CTX') or {}).get('rate', 0) >= .95
    out['R0'] = {g.split('/')[1]: r0(g.split('/')[1]) for g in G if g.startswith('run/') and g.endswith('/case')}
    def r1rule(x):
        pj, pu = x['PROJ']['rate'], x['PUSH']['rate']
        return 'H-offhull' if pj >= .7 and pu <= .4 else 'H-inspan' if pu >= .7 and pj <= .4 else 'either' if pj >= .7 and pu >= .7 else 'neither' if pj <= .4 and pu <= .4 else 'mixed'
    def r2rule(x):
        pj, pu, cx = x['PROJ']['rate'], x['PUSH']['rate'], (x.get('CTX') or {}).get('rate', 0)
        return ('H-inspan' if pu >= .7 and pj <= .4 and cx <= .4 else 'H-context' if cx >= .7 and pu <= .4 else 'H-offhull' if pj >= .7 and pu <= .4 else 'mixed')
    xa = G.get('run/R-A-t5/case')
    out['R1'] = dict(verdict=r1rule(xa) if xa and out['R0'].get('R-A-t5') else 'not interpretable' if xa else 'not evaluable', precheck=pre.get('R-A-t5'),
                     kind='primary' if all((pre.get('R-A-t5') or {}).values()) else 'exploratory (no-op repair)')
    rb = [r for r in load_mode('run') if r['group'].startswith('R-B') and r['role'] == 'case' and out['R0'].get(r['group'])]
    pooled = {k: rates(rb, k) for k in ('SNAP', 'PROJ', 'PUSH', 'CTX', 'SNAP+CTX')} if rb else None
    out['R2'] = dict(verdict=r2rule(pooled) if pooled else 'not evaluable', pooled=pooled, families_interpretable=sorted({r['group'] for r in rb}),
                     per_family={g.split('/')[1]: r2rule(v) for g, v in G.items() if g.startswith('run/R-B') and g.endswith('/case')})
    ctl = [r for r in load_mode('run') if r['role'] == 'control']; c3 = {k: rates(ctl, k) for k in ('PROJ', 'PUSH', 'CTX')}
    out['R3'] = dict(rates=c3, holds=all(v is None or v['rate'] >= .97 for v in c3.values()))
    a4 = G.get('r4/R4-A-t5/case'); b4 = [r for r in load_mode('r4') if r['group'] == 'R4-B' and r['role'] == 'case']; pb4 = {k: rates(b4, k) for k in ('SNAP', 'PROJ', 'PUSH', 'CTX', 'SNAP+CTX')} if b4 else None
    out['R4'] = dict(A=dict(verdict=r1rule(a4) if a4 else None), B=dict(verdict=r2rule(pb4) if pb4 else None, pooled=pb4))
    out['R4']['A']['status'] = None if not a4 else 'confirmed' if out['R4']['A']['verdict'] == out['R1']['verdict'] else 'unstable'
    out['R4']['B']['status'] = None if not pb4 else 'confirmed' if out['R4']['B']['verdict'] == out['R2']['verdict'] else 'unstable'
    out['Q20'] = dict(R1=out['R1']['verdict'], R2=out['R2']['verdict'], R4=dict(A=out['R4']['A']['status'], B=out['R4']['B']['status']))
    return out


# ---------------------------------------------------------------- A
def a_unit(P, ucells):
    out = dict(A1={}, A2={}, A3={}, A3b={}); pre = P['precheck_A']
    for bb in ('bart', 't5'):
        f = ROOT / ('local/smoke' if SM else 'results') / f'simulate_{bb}.json.gz'
        if not f.exists(): continue
        with gzip.open(f, 'rt') as g: sims = json.load(g)
        for d in M_DOMAINS[bb]:
            kp, ka = f'U/{bb}/{d}/F_empty/plus', f'U/{bb}/{d}/F_empty/alt'
            if kp not in sims: continue
            N = len(S.states(d)); rp = np.array(sims[kp]['rho']); ra = np.array(sims[ka]['rho'])
            r1 = float(np.median(ra[:, -1]) / max(np.median(rp[:, -1]), 1e-12)); r2 = float(np.median(rp[:, N - 1]) / max(np.median(rp[:, 0]), 1e-12))
            out['A1'][f'{bb}/{d}'] = dict(alt_over_plus_2N=r1, plus_N_over_1=r2, holds=r1 >= 2 and r2 <= 1.5, in_precheck=f'{bb}/{d}' in pre['A1_combos'],
                                          rho_median=dict(plus_t1=float(np.median(rp[:, 0])), plus_tN=float(np.median(rp[:, N - 1])), plus_t2N=float(np.median(rp[:, -1])), alt_t2N=float(np.median(ra[:, -1]))))
        fa = ROOT / ('local/smoke' if SM else 'results') / f'a_{"smoke" if SM else "run"}_{bb}.json'
        if fa.exists():
            for k, v in read(fa)['cells'].items():
                if 'A2' in v: out['A2'][k] = dict(v['A2'], holds=v['A2']['cycle_sum_ratio_median'] <= .25 and v['A2']['alt_contrast_median'] >= .5, train_template_dev=v.get('A2_train_template_dev'))
                if 'A3_Pinv' in v: out['A3'][k] = dict(R2N=v['A3_Pinv'], holds=v['A3_Pinv']['rate'] >= .95, in_precheck=k in pre['A3_combos'])
                if 'A3_PPinv' in v: out['A3b'][k] = dict(R2N=v['A3_PPinv'], holds=v['A3_PPinv']['rate'] >= .95)
    ev = [v['holds'] for v in out['A1'].values() if v['in_precheck']]
    a1 = None if not pre['A1_confirmatory'] else sum(ev) >= 3; a2 = sum(v['holds'] for v in out['A2'].values()) >= 3 if out['A2'] else None
    a3 = all(v['holds'] for v in out['A3'].values() if v['in_precheck']) if out['A3'] else None
    out['summary'] = dict(A1=a1, A1_kind='primary' if pre['A1_confirmatory'] else 'exploratory (pre-check)', A2=a2, A3=a3,
                          A3b=all(v['holds'] for v in out['A3b'].values()) if out['A3b'] else None)
    out['Q22'] = dict(verdict='H-cycle' if a1 and a2 and a3 else 'only A3' if a3 and not a1 and not a2 else 'parts: ' + ', '.join(k for k in ('A1', 'A2', 'A3') if out['summary'][k]) if any(out['summary'][k] for k in ('A1', 'A2', 'A3')) else 'H-other')
    return out


# ---------------------------------------------------------------- K
def k_unit(P):
    f = ROOT / ('local/smoke/k_smoke.json' if SM else 'results/k_run.json')
    if not f.exists(): return dict(note='no K results')
    kr = read(f); C = kr['cells']; tr7 = read(ROOT / 'results/train_new_bart_K.json'); out = dict(table={})
    def R(d, name, k, seeds, path='plus'):
        v = []
        for s in seeds:
            x = C.get(f'{d}/{name}_s{s}/{path}')
            st = (tr7 if s >= 45 or name == 'ORU8' else read(V6DIR / 'results/train_new_bart_K.json')).get(f'{name.split("-")[0]}/{d}/s{s}', {})
            v.append(0.0 if x is None or st.get('status', 'ok') != 'ok' else x.get(f'R{k}', 0.0))
        return v
    new, all8 = (45, 46, 47, 48, 49), (42, 43, 44, 45, 46, 47, 48, 49)
    for d in K_DOMAINS:
        for name in ('Att2LU8', 'Att2LU4', 'Att1U8', 'ORU8'):
            for k in (8, 12, 30, 100):
                out['table'][f'{d}/{name}/R{k}'] = dict(zip(map(str, all8 if name != 'ORU8' else (42, 43, 44)), R(d, name, k, all8 if name != 'ORU8' else (42, 43, 44))))
    r100 = R('bind3', 'Att2LU8', 100, new); r30 = R('bind3', 'Att2LU8', 30, new)
    out['K5'] = dict(seeds=r100, median=med(r100), verdict='H-closed' if med(r100) >= .9 and sum(x >= .8 for x in r100) >= 4 else 'H-slow-decay' if med(r100) <= .5 else 'mixed')
    u4, a1 = R('bind3', 'Att2LU4', 30, new), R('bind3', 'Att1U8', 30, new)
    out['K6'] = dict(Att2LU8=r30, Att2LU4=u4, Att1U8=a1, verdict='holds' if sum(x >= .9 for x in r30) >= 4 and med(u4) <= .5 and med(a1) <= .5 else 'opposing' if med(r30) <= .5 else 'mixed')
    o = R('bind3', 'ORU8', 30, (42, 43, 44)); out['K7'] = dict(seeds=o, median=med(o), verdict='H-representable' if med(o) >= .9 else 'H-unrepresentable' if med(o) <= .5 else 'mixed')
    ab = R('bind3', 'Att2LU8-abldrop', 30, all8)
    out['K8'] = dict(seeds=ab, median=med(ab), verdict='H-layer2-needed' if med(ab) <= .5 else 'H-layer2-redundant' if med(ab) >= .9 else 'mixed',
                     kind='primary' if P['precheck_K']['K8_confirmatory'] else 'exploratory (decided by construction; pre-check)')
    k9 = {d: R(d, 'Att2LU8', 30, all8) for d in ('name3', 'bind3fix')}; out['K9'] = dict(seeds=k9, holds={d: sum(x >= .95 for x in v) >= 6 for d, v in k9.items()})
    out['exploratory'] = dict(ablations={am: R('bind3', f'Att2LU8-abl{am}', 30, all8) for am in ('uniform', 'self')}, **kr.get('exploratory', {}))
    return out


def main():
    global SM
    require_slurm(); SM = '--smoke' in sys.argv; t0 = time.time()
    P = read(ROOT / 'protocol.json') if not SM else read(ROOT / 'local/smoke/protocol_preview.json')
    g70 = {bb: read(ROOT / f'results/g70_{bb}.json') for bb in ('bart', 't5')} if not SM else None
    U, ucells = u_unit(P); R = r_unit(P); A = a_unit(P, ucells); K = k_unit(P)
    out = dict(G7_0=g70, U=U, R=R, A=A, K=K, verdicts=dict(Q20=R['Q20'], Q21=U['Q21'], Q22=A['Q22'], K5=K.get('K5', {}).get('verdict'), K6=K.get('K6', {}).get('verdict'),
                                                       K7=K.get('K7', {}).get('verdict'), K8=K.get('K8', {}).get('verdict')),
               lock=read(ROOT / 'protocol_lock.json')['lock_commit'] if (ROOT / 'protocol_lock.json').exists() and not SM else None, seconds=time.time() - t0)
    dst = ROOT / ('local/smoke' if SM else 'results'); dump(dst / 'predictions.json', out)
    with open(dst / 'u_cells.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['key', 'family', 'backbone', 'domain', 'method', 'path', 'obs', 'pred_slot', 'pred_U', 'pred_U2', 'pred_Um', 'pred_Ur'])
        w.writeheader(); [w.writerow(dict(key=k, **v)) for k, v in ucells.items()]
    exp = []
    add = lambda pid, obs, verdict, kind='primary', ci=None: exp.append(dict(id=f'v7/{pid}', plan='v7', experiment='composability_mechanisms_v6', prediction=P['predictions'].get(pid),
                                                                       observed=obs, ci95=ci, verdict=verdict, kind=kind, lock_commit=out['lock']))
    add('G7_0', {bb: v['pass'] for bb, v in (g70 or {}).items()}, all(v['pass'] for v in (g70 or {}).values()) if g70 else None)
    for u in ('U1', 'U2'): f = U['families'].get('F1' if u == 'U1' else 'F2', {}); add(u, f.get('agree'), U[u]['holds'], U[u]['kind'], (f.get('U_minus_slot') or {}).get('ci95'))
    add('U3', U['U3']['per_backbone'], U['U3']['holds']); add('U4', U['U4'], None, 'secondary'); add('Q21', None, U['Q21']['verdict'])
    add('R0', R['R0'], all(R['R0'].values()) if R['R0'] else None); add('R1', R['groups'].get('run/R-A-t5/case'), R['R1']['verdict']); add('R2', R['R2']['pooled'], R['R2']['verdict'])
    add('R3', R['R3']['rates'], R['R3']['holds']); add('R4', R['R4'], R['R4']['A'].get('status'))
    add('A1', A['A1'], A['summary']['A1'], A['summary']['A1_kind']); add('A2', A['A2'], A['summary']['A2']); add('A3', A['A3'], A['summary']['A3']); add('A3b', A['A3b'], A['summary']['A3b'], 'secondary')
    add('Q22', None, A['Q22']['verdict'])
    for k in ('K5', 'K6', 'K7', 'K8'): add(k, K.get(k), K.get(k, {}).get('verdict'), K.get(k, {}).get('kind', 'primary'))
    add('K9', K.get('K9'), K.get('K9', {}).get('holds'), 'secondary')
    dump(dst / 'paper_export.json', exp); print(json.dumps(out['verdicts'], default=str, indent=1), 'mismatches', U['mismatches'], 'duplicates', len(U['duplicates']), flush=True)


if __name__ == '__main__':
    main()
