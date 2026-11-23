"""P (CPU, exploratory, before the lock). P0 input manifest (hashes of v1-v3 fits, editors, caches, shard archives);
P1 per-plane (rho_k, delta_k, eps_k) of v3's T5Gemma RRR operators vs v3 unit-block harmonics and R_2N;
P3 text-level dedupe audit of v1 confirm and v2 confirm2/confirm, re-run of the locked v1/v2 analyses without duplicated worlds,
NOTE_DEDUPE drafts (appendix C); P4 per-plane criterion vs unit-block criterion for predicting one-way R_2N >= 0.90.
Results: results/patch/. Nothing here changes any v4 prediction, threshold or definition."""
import csv
import subprocess
import time
from collections import defaultdict
from lib4 import *
from d_make_data import history_text_files, texts_of

OUT = 'results/patch'


# ---------------------------------------------------------------- P0
def manifest():
    E = []
    add = lambda key, p: E.append((key, p))
    for f in ('backend.py', 'semantics.py', 'evaluator.py', 'common.py', 'config.json', 'model_manifest.json'):
        add(f'four_domain/{f}', SOURCE / f)
    add('operator_residual_v2/core.py', V2 / 'core.py'); add('cwr/fit.py', CWR / 'fit.py'); add('cwr/shared.py', CWR / 'shared.py')
    for f in ('config.json', 'model.safetensors', 'tokenizer.json', 'vocab.json', 'merges.txt'): add(f'model/bart-base/{f}', REPO / 'models/bart-base' / f)
    add('model/bart_metadata.json', REPO / 'models/bart_metadata.json')
    for f in sorted(V1.glob('*.py')) + [V1 / 'protocol.json', V1 / 'protocol_lock.json', V1 / 'results/e1_predictions.json', V1 / 'results/e1_shards.tar.gz']:
        add(f'v1/{f.name}', f)
    for f in sorted((V1 / 'data').glob('*/*.jsonl')): add(f'v1/data/{f.parent.name}/{f.name}', f)
    for f in sorted((V1 / 'local').glob('e1_*.pt')):
        if 'latest' in f.name: continue
        add(f'v1/local/{f.name}', f)
    for f in sorted(V2DIR.glob('*.py')) + [V2DIR / 'protocol.json', V2DIR / 'protocol_lock.json', V2DIR / 'results/predictions.json',
                                           V2DIR / 'results/shards_laneA.tar.gz', V2DIR / 'results/shards_laneB.tar.gz', V2DIR / 'results/algebra.json']:
        add(f'v2/{f.name}', f)
    for f in sorted((V2DIR / 'data').glob('*/*.jsonl')): add(f'v2/data/{f.parent.name}/{f.name}', f)
    for f in sorted((V2DIR / 'local').glob('*.pt')): add(f'v2/local/{f.name}', f)
    for f in sorted(V3DIR.glob('*.py')) + [V3DIR / n for n in ('protocol.json', 'protocol_lock.json', 'ERRATUM_01.md', 'data/slot_positions.json')] + \
            sorted((V3DIR / 'results').glob('*.json')) + sorted((V3DIR / 'results').glob('*.tar.gz')) + [V3DIR / 'results/chains.csv']:
        add(f'v3/{f.relative_to(V3DIR)}', f)
    for f in sorted((V3DIR / 'data').glob('*/*.jsonl')): add(f'v3/data/{f.parent.name}/{f.name}', f)
    for f in sorted((V3DIR / 'local').glob('*.pt')): add(f'v3/local/{f.name}', f)
    return E


def model_checks():
    mm = read(SOURCE / 'model_manifest.json'); out = {}
    out['bart_revision'] = read(REPO / 'models/bart_metadata.json')['sha'] == 'aadd2ab0ae0c8268c7c9693540e9904811f36177'
    t5 = mm['t5gemma']; out['t5_revision'] = t5['revision'] == '6a196a58ce2786cd139a1217a85d1f7b9984e330'
    out['t5_files_sha_match'] = all(sha(Path(t5['directory']) / n) == r['sha256'] for n, r in t5['files'].items())
    out['bart_files_sha_match'] = all(sha(Path(mm['bart']['directory']) / n) == r['sha256'] for n, r in mm['bart']['files'].items())
    return out


def p0():
    files = []; missing = []
    for key, p in manifest():
        if not Path(p).exists(): missing.append(str(p)); continue
        files.append(dict(key=key, path=str(Path(p).relative_to(REPO)), sha256=sha(p), bytes=Path(p).stat().st_size))
    checks = model_checks(); checks['required_present'] = not missing
    dump('inputs_manifest.json', dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), checks=checks, missing=missing, n_files=len(files), files=files))
    assert all(checks.values()), checks
    return dict(n_files=len(files), bytes=sum(f['bytes'] for f in files), checks=checks)


# ---------------------------------------------------------------- shared readers
def csv_rows(p):
    with open(p) as f: return list(csv.DictReader(f))


@lru_cache(None)
def v3_chains():
    out = {}
    for r in csv_rows(V3DIR / 'results/chains.csv'):
        out[r['backbone'], r['domain'], r['map'], r['method'], r['path'], int(r['t'])] = float(r['R_t'])
    return out


@lru_cache(None)
def v2_chains():
    out = {}
    for r in csv_rows(V2DIR / 'results/chains.csv'):
        out[r['domain'], r['map'], r['method'], r['path'], int(r['k'])] = float(r['R_k'])
    return out


def auc(score, label):
    pos = [s for s, l in zip(score, label) if l]; neg = [s for s, l in zip(score, label) if not l]
    if not pos or not neg: return None
    return float(np.mean([(p > n) + .5 * (p == n) for p in pos for n in neg]))


# ---------------------------------------------------------------- P1 / P4
def operators():
    """(name, backbone, domain, map, kind, obj, R_2N, unit-block harmonics) for every v2/v3 operator in scope."""
    ops = []
    alg2 = read(V2DIR / 'results/algebra.json'); alg3 = read(V3DIR / 'results/algebra.json'); a3 = read(V3DIR / 'results/a_eval.json')
    for d in ('weekday', 'month', 'compass', 'egoside'):
        N = len(S.states(d))
        for mp in ('natural', 'scrmax'):
            f = V2DIR / f'local/rrr_{d}_{mp}.pt'
            if not f.exists(): continue
            fits = load(f)
            for (op, r) in sorted(k for k in fits if isinstance(k, tuple) and k[0] == 'plus'):
                R = v2_chains().get((d, mp, f'RRR{r}', 'plus_from_start', 2 * N)); h = alg2.get(f'{d}/{mp}/RRR{r}', {}).get('plus', {}).get('harmonics_present')
                if R is None: continue
                ops.append((f'bart/{d}/{mp}/RRR{r}', 'bart', d, mp, 'rrr', fits['plus', r], R, h))
    for d in ('weekday', 'month', 'compass'):
        N = len(S.states(d))
        for mp in ('natural', 'scrmax'):
            f = V3DIR / f'local/t5_rrr_{d}_{mp}.pt'
            if not f.exists(): continue
            fits = load(f)
            for (op, r) in sorted(k for k in fits if isinstance(k, tuple) and k[0] == 'plus'):
                R = v3_chains().get(('t5', d, mp, f'RRR{r}', 'plus_from_start', 2 * N)); h = alg3.get(f't5/{d}/{mp}/RRR{r}', {}).get('harmonics_present')
                if R is None: continue
                ops.append((f't5/{d}/{mp}/RRR{r}', 't5', d, mp, 'rrr', fits['plus', r], R, h))
    for s in SEEDS:
        for name, path in ((f'C3_l1_v1_s{s}', V1 / f'local/e1_C3_month_s{s}_0600.pt'), (f'C3_l3_s{s}', V3DIR / f'local/a_C3_l3_month_s{s}.pt'),
                           (f'C3_l10_s{s}', V3DIR / f'local/a_C3_l10_month_s{s}.pt'), (f'C3_rrrinit_s{s}', V3DIR / f'local/a_C3_rrrinit_month_s{s}.pt')):
            sd = load(path)['editor']; R = v3_chains()[('bart', 'month', 'natural', name, 'plus_from_start', 24)]
            ops.append((f'bart/month/natural/{name}', 'bart', 'month', 'natural', 'editor', sd, R, a3[f'month/{name}']['algebra']['plus']['harmonics_present']))
    return ops


def p1_p4():
    p1 = {}; p4 = []
    for name, bb, d, mp, kind, obj, R, harm in operators():
        e = op_plane_errors(kind, obj, 'plus', bb, d, mp); N = len(S.states(d))
        row = dict(name=name, backbone=bb, domain=d, map=mp, R_2N=R, composable=R >= .90, harmonics_unit_block=harm,
                   eps={str(k): v['eps'] for k, v in e.items()}, rho={str(k): v['rho'] for k, v in e.items()}, delta={str(k): v['delta'] for k, v in e.items()},
                   crit_all_planes=all(v['eps'] <= .5 for v in e.values()), crit_k1_unit=(harm is not None and 1 in harm), max_eps=max(v['eps'] for v in e.values()))
        p4.append(row)
        if bb == 't5' and d in ('weekday', 'month'): p1[name] = row
    lab = [r['composable'] for r in p4]; summ = {}
    for subset, rs in (('all', p4), ('rrr', [r for r in p4 if '/C3_' not in r['name']]), ('C3', [r for r in p4 if '/C3_' in r['name']]),
                       ('bart', [r for r in p4 if r['backbone'] == 'bart']), ('t5', [r for r in p4 if r['backbone'] == 't5'])):
        l = [r['composable'] for r in rs]
        summ[subset] = dict(n=len(rs), composable=sum(l),
                            accuracy_all_planes=float(np.mean([r['crit_all_planes'] == r['composable'] for r in rs])) if rs else None,
                            accuracy_k1_unit=float(np.mean([r['crit_k1_unit'] == r['composable'] for r in rs])) if rs else None,
                            auc_all_planes_binary=auc([r['crit_all_planes'] for r in rs], l), auc_k1_unit_binary=auc([r['crit_k1_unit'] for r in rs], l),
                            auc_neg_max_eps=auc([-r['max_eps'] for r in rs], l), auc_neg_eps1=auc([-r['eps']['1'] for r in rs], l))
    return p1, dict(summary=summ, operators=p4, note='eps_k per A.2 for the plus operator; planes from train c-bar in the cycle order of the map; '
                                                       'cross-plane coupling and non-normal parts are not included. Labels: one-way plus R_2N >= 0.90 on the v2/v3 confirm sets.')


# ---------------------------------------------------------------- P3
def pre_v1_texts():
    seen = set()
    for f in history_text_files():
        if any(str(f).startswith(str(x)) for x in (V1, V2DIR, V3DIR)): continue
        for r in rows(f): seen.update(texts_of(r))
    return seen


def renders(exp_dir, d):
    f = exp_dir / f'data/{d}/renders.jsonl'
    return rows(f) if f.exists() else []


def dedupe_sets():
    """Per confirm world: which historical text pools contain one of its renders (any template, any state). Excluded = any pool."""
    pre = pre_v1_texts(); out = {}
    v1_tr = {r['text'] for d in V1_DOMAINS for r in renders(V1, d) if r['split'] in ('train', 'dev')}
    v1_cf = {r['text'] for d in V1_DOMAINS for r in renders(V1, d) if r['split'] == 'confirm'}
    v2_s1b_tr = {r['text'] for d in ('pron3', 'name3', 'bind3') for r in renders(V2DIR, d) if r['split'] in ('train', 'dev')}
    specs = dict(v1=(V1, {d: 'confirm' for d in V1_DOMAINS}, [('v1 train/dev', v1_tr), ('pre-v1', pre)]),
                 v2=(V2DIR, {**{d: 'confirm2' for d in V1_DOMAINS}, **{d: 'confirm' for d in ('pron3', 'name3', 'bind3')}},
                     [('v1 train/dev', v1_tr), ('v1 confirm', v1_cf), ('v2 S1b train/dev', v2_s1b_tr), ('pre-v1', pre)]))
    for exp, (D, splits, pools) in specs.items():
        tab = []; ex = []
        for d, sp in splits.items():
            hit = {name: set() for name, _ in pools}; hit0 = {name: set() for name, _ in pools}; allw = set()
            for r in renders(D, d):
                if r['split'] != sp: continue
                allw.add(r['world_id'])
                for name, pool in pools:
                    if r['text'] in pool:
                        hit[name].add(r['world_id'])
                        if r['template'] == 0: hit0[name].add(r['world_id'])
            dup = set().union(*hit.values()); ex += sorted(dup)
            tab.append(dict(domain=d, split=sp, worlds=len(allw), duplicated=len(dup), rate=len(dup) / len(allw) if allw else None,
                            by_source={k: len(v) for k, v in hit.items()}, template0_by_source={k: len(v) for k, v in hit0.items()}))
        out[exp] = dict(table=tab, excluded_world_ids=ex, sources=[n for n, _ in pools],
                        history=' + '.join(n for n, _ in pools) + ' (pre-v1 = four_domain_state_coverage_v1, canonical_confirmation_v1, manifold_controls_v1, operator_residual_v2)')
    return out


def rnd(x):
    if isinstance(x, dict) and 'rate' in x: return round(x['rate'], 4)
    if isinstance(x, dict): return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, float): return round(x, 4)
    return x


def verdicts(pred, exp):
    """Flatten {name: verdict-ish} and a few headline numbers for the comparison table."""
    out = {}
    if exp == 'v1':
        P = pred['predictions']
        for k, v in P.items():
            num = None; o = v.get('observed', {})
            if k in ('P1', 'P2'): num = {d: round(x['rate'], 4) for d, x in o.items()}
            elif k == 'P3a': num = dict(diff=round(o['diff']['diff'], 4), ci95=[round(x, 4) for x in o['diff']['ci95']])
            elif k == 'P3b': num = dict(diff=round(o['difference'], 4), p=o['test']['p_one_sided'])
            elif k == 'P4': num = {a: round(b['rate'], 4) for a, b in o.items()}
            elif k == 'P5': num = dict(C1_R2_max=round(max(x['rate'] for x in o['C1_R2'].values()), 4), C3_RN_min=round(min(x['rate'] for x in o['C3_RN'].values()), 4))
            elif k == 'P6': num = {d: round(x['median'], 4) for d, x in o.items()}
            elif k == 'P7': num = dict(rho=round(o['spearman_rho'], 4))
            out[k] = (v.get('verdict', v.get('decision')), num)
        return out
    for k, v in pred.items():
        if not isinstance(v, dict) or k[0] not in 'GABRMQ': continue
        verdict = v.get('verdict', v.get('pass_')); num = None; o = v.get('observed')
        if k == 'G2_0': num = dict(RRR16_min=round(min(x['rate'] for x in v['RRR16_R2N'].values()), 4), C1_R2_max=round(max(x['rate'] for x in v['C1_R2'].values()), 4))
        elif k in ('A1', 'A3', 'B1', 'B2', 'R2', 'R3'): num = rnd(o)
        elif k == 'A2': num = dict(rho=v['spearman_rho'], min_scr=round(min(x['R_2N'] for kk, x in o.items() if not kk.endswith('natural')), 4))
        elif k == 'B3': num = round(max(x['rate'] for x in o.values()), 4)
        elif k == 'R1': num = {d: x['r_star'] for d, x in o.items()}
        out[k] = (verdict, num)
    return out


def p3():
    sets = dedupe_sets(); res = {}
    for exp in ('v1', 'v2'):
        excl = ROOT / OUT / f'dedupe_{exp}_excluded.json'; dump(excl, dict(excluded_world_ids=sets[exp]['excluded_world_ids']))
        out = ROOT / OUT / f'dedupe_{exp}_rerun.json'
        r = subprocess.run([sys.executable, str(ROOT / 'p3_rerun.py'), exp, str(excl), str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-4000:]
        cap = read(out); key = 'results/e1_predictions.json' if exp == 'v1' else 'results/predictions.json'
        orig = read((V1 / 'results/e1_predictions.json') if exp == 'v1' else (V2DIR / 'results/predictions.json'))
        vo, vd = verdicts(orig, exp), verdicts(cap[key], exp)
        comp = [dict(item=k, original=vo[k], deduplicated=vd.get(k), verdict_changed=str(vo[k][0]) != str(vd.get(k, (None,))[0])) for k in vo]
        res[exp] = dict(table=sets[exp]['table'], history=sets[exp]['history'], sources=sets[exp]['sources'], n_excluded=len(sets[exp]['excluded_world_ids']), comparison=comp,
                        stdout_tail=r.stdout[-1500:])
        note(exp, res[exp])
    return res


def note(exp, r):
    name = 'symmetry_composability_v1' if exp == 'v1' else 'composability_mechanisms_v1'
    lines = [f'# NOTE_DEDUPE（{name}）', '', f"- 日期：{time.strftime('%Y-%m-%d')}",
             f"- 检查内容：本实验各 confirm world 的渲染文本（模板 0 与模板 3，全部状态），与 {r['history']} 的渲染文本完全相同的数量（按域、按 split）。",
             f'- 重复的 world ID：见 `experiments/composability_mechanisms_v3/results/patch/dedupe_{exp}_excluded.json`（分支 `experiment/composability-mechanisms-v3`）。',
             f'- 生成：`composability_mechanisms_v3/p_diag.py` 的 P3（Slurm CPU 作业）；重算用 `p3_rerun.py` 在已解码的分片上重跑本实验锁定的分析脚本，'
             '只去掉重复 world 的记录，不重新编码或解码。', '',
             '| 域 | split | confirm world 数 | ' + ' | '.join(f'与 {n} 重复' for n in r['sources']) + ' | 任一来源重复（已去掉） | 比例 |',
             '| --- | --- | --- | ' + ' | '.join('---' for _ in r['sources']) + ' | --- | --- |']
    for t in r['table']:
        cells = ' | '.join(f"{t['by_source'][n]}（模板 0：{t['template0_by_source'][n]}）" for n in r['sources'])
        lines.append(f"| {t['domain']} | {t['split']} | {t['worlds']} | {cells} | {t['duplicated']} | {t['rate']:.3f} |")
    lines += ['', '## 去掉重复 world 后重算的关键数字', '', '| 结论或预测 | 原值 | 去重后 | 判定是否改变 |', '| --- | --- | --- | --- |']
    for c in r['comparison']:
        o, dd = c['original'], c['deduplicated'] or (None, None)
        lines.append(f"| {c['item']} | {o[0]}：{json.dumps(o[1], ensure_ascii=False)} | {dd[0]}：{json.dumps(dd[1], ensure_ascii=False)} | {'是' if c['verdict_changed'] else '否'} |")
    changed = [c['item'] for c in r['comparison'] if c['verdict_changed']]
    extra = ('P6（κ_N，由 confirm 编码上的代数分析得到）未重算，表中为原值。' if exp == 'v1' else
             'M1–M4（S3，GPU 上在 confirm2 编码上计算的汇总量）与 A4、A5（只依赖拟合）未重算，表中为原值；S2 与 S1a 的链式结果已重算。')
    lines += ['', '## 结论', '', ('全部判定不变。' if not changed else '以下判定改变：' + '、'.join(changed) + '。') + extra, '']
    (ROOT / OUT / f'NOTE_DEDUPE_{exp}.md').write_text('\n'.join(lines))


def main():
    require_slurm(); t0 = time.time(); res = {}
    res['P0'] = p0(); print('P0', res['P0'], flush=True)
    p1, p4 = p1_p4(); res['P1'] = p1; res['P4'] = p4; print('P4', json.dumps(p4['summary'], indent=1), flush=True)
    res['P3'] = p3(); print('P3', {e: [(c['item'], c['verdict_changed']) for c in v['comparison']] for e, v in res['P3'].items()}, flush=True)
    res['seconds'] = time.time() - t0; dump(f'{OUT}/p_diag.json', res)


if __name__ == '__main__':
    main()
