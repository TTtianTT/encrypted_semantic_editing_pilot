"""P0 (CPU, exploratory, before the lock): P0-0 input hashing; X1 per-step accuracy A_t and offsets from v2 shards;
X2 month r=12 alternating anomaly; X3 month sigma_max rank non-monotonicity."""
import time
from collections import Counter, defaultdict
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *
import sym3_semantics as S
import sym3_evaluator as Ev

V2DIR = EXP / 'composability_mechanisms_v1'
SRC = '.four-domain-worktree/experiments/four_domain_state_coverage_v1'


def manifest():
    E = []
    add = lambda key, p, src: E.append((key, p, src))
    for f in ('backend.py', 'semantics.py', 'evaluator.py', 'common.py', 'config.json', 'model_manifest.json', 'train.py'):
        add(f'four_domain/{f}', REPO / SRC / f, 'four_domain_state_coverage_v1')
    add('operator_residual_v2/core.py', V2 / 'core.py', 'operator_residual_v2'); add('cwr/fit.py', CWR / 'fit.py', 'canonical_write_reachability_v1')
    add('cwr/shared.py', CWR / 'shared.py', 'canonical_write_reachability_v1')
    for f in ('sym_semantics.py', 'sym_evaluator.py', 'symutil.py', 'protocol.json', 'protocol_lock.json'):
        add(f'v1/{f}', V1 / f, 'symmetry_composability_v1')
    for d in V1_DOMAINS:
        add(f'v1/data/{d}', V1 / f'data/{d}/worlds.jsonl', 'symmetry_composability_v1')
        for split in ('train', 'dev'):
            for s in S.states(d): add(f'v1/cache/{d}_{split}_s{s}', V1 / f'local/e1_{d}_{split}_t0_s{s}.pt', 'symmetry_composability_v1')
        for g in ('C1', 'C3'):
            for seed in SEEDS: add(f'v1/editor/{d}/{g}/s{seed}', V1 / f'local/e1_{g}_{d}_s{seed}_0600.pt', 'symmetry_composability_v1')
    for f in ('protocol.json', 'protocol_lock.json', 'sym2_semantics.py', 'sym2_evaluator.py', 'symutil.py', 'fit_rrr.py', 'train.py', 'eval_chains.py',
              'algebra.py', 's2_modes.py', 's3_mechanism.py', 'results/algebra.json', 'results/shards_laneA.tar.gz', 'results/shards_laneB.tar.gz', 'AMENDMENT_01.md'):
        add(f'v2/{f}', V2DIR / f, 'composability_mechanisms_v1')
    for p in sorted((V2DIR / 'local').glob('rrr_*.pt')): add(f'v2/fit/{p.name}', p, 'composability_mechanisms_v1')
    for p in sorted((V2DIR / 'local').glob('c_*_confirm2_t0_*.pt')): add(f'v2/cache/{p.name}', p, 'composability_mechanisms_v1')
    for d in V1_DOMAINS + ['pron3', 'name3', 'bind3']: add(f'v2/data/{d}', V2DIR / f'data/{d}/worlds.jsonl', 'composability_mechanisms_v1')
    hist = [SOURCE / f'data/{d}/worlds.jsonl' for d in ('time', 'person', 'space', 'emotion')] + sorted((CONF / 'data').glob('*.jsonl')) + \
           sorted((MAN / 'data').glob('*.jsonl')) + [V2 / 'train_worlds.jsonl', V2 / 'eval_worlds.jsonl']
    for p in hist: add(f'history/{p.parent.name}/{p.name}', p, p.parent.name)
    for f in ('config.json', 'model.safetensors', 'tokenizer.json', 'vocab.json', 'merges.txt'): add(f'model/bart-base/{f}', REPO / 'models/bart-base' / f, 'models')
    add('model/bart_metadata.json', REPO / 'models/bart_metadata.json', 'models')
    return E


def model_checks():
    mm = read(SOURCE / 'model_manifest.json'); out = {}
    out['bart_revision'] = read(REPO / 'models/bart_metadata.json')['sha'] == 'aadd2ab0ae0c8268c7c9693540e9904811f36177'
    t5 = mm['t5gemma']; out['t5_revision'] = t5['revision'] == '6a196a58ce2786cd139a1217a85d1f7b9984e330'
    out['t5_files_sha_match'] = all(sha(Path(t5['directory']) / n) == r['sha256'] for n, r in t5['files'].items())
    out['bart_files_sha_match'] = all(sha(Path(mm['bart']['directory']) / n) == r['sha256'] for n, r in mm['bart']['files'].items())
    return out


def load_v2_chains():
    """{(d, map, method, path): {world_id: {step: (success, decoded_state, state, start)}}} for v2 RRR chains."""
    prot = read(V2DIR / 'protocol.json'); W = {d: {w['world_id']: w for w in rows(V2DIR / f'data/{d}/worlds.jsonl') if w['split'] == 'confirm2'} for d in V1_DOMAINS}
    out = defaultdict(dict)
    for f in sorted((V2DIR / 'results/shards').glob('chain_*_RRR*.jsonl')):
        if f.name.split('_')[1] not in V1_DOMAINS: continue   # S1b shards are not part of X1
        for r in rows(f):
            d = r['domain']; spec = prot['chains'][d][r['map']][r['path']]
            st = W[d][r['world_id']]['start_state'] if spec['start'] == 'world_start' else spec['start']
            ps, _ = Ev.parse_state(r['text'], d)
            out[d, r['map'], r['method'], r['path']].setdefault(r['world_id'], {})[r['step']] = (r['score']['success'], ps, r['state'], st)
    return out, prot


def order_of(d, mp, prot):
    if d == 'daysago':
        return list(range(2, 10)) if mp == 'natural' else prot['s1a']['maps'][d][mp]['path']
    return list(range(len(S.states(d)))) if mp == 'natural' else prot['s1a']['maps'][d][mp]['cycle']


def main():
    require_slurm(); t0 = time.time(); res = {}
    files = []; missing = []
    for key, p, src in manifest():
        if not Path(p).exists(): missing.append(str(p)); continue
        files.append(dict(key=key, path=str(Path(p).relative_to(REPO)) if str(p).startswith(str(REPO)) else str(p), sha256=sha(p), bytes=Path(p).stat().st_size, source=src))
    checks = model_checks(); checks['required_present'] = not missing
    checks['v2_local_shards_files'] = len(list((V2DIR / 'results/shards').glob('*.jsonl')))
    dump('inputs_manifest.json', dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), checks=checks, missing=missing, n_files=len(files), files=files))
    assert all(v for v in checks.values() if isinstance(v, bool)), checks
    # X1
    ch, prot = load_v2_chains(); x1 = {}
    for (d, mp, me, path), ws in sorted(ch.items()):
        order = order_of(d, mp, prot); N = len(order); T = max(max(v) for v in ws.values()); A = []; Rt = []; off = []
        for t in range(1, T + 1):
            A.append(float(np.mean([ws[w][t][0] for w in ws]))); Rt.append(float(np.mean([all(ws[w][k][0] for k in range(1, t + 1)) for w in ws])))
            c = Counter()
            for w in ws:
                _, ps, _, st = ws[w][t]
                c['unparsable' if ps is None or ps not in order else str((order.index(ps) - order.index(st)) % N if d != 'daysago' else order.index(ps) - order.index(st))] += 1
            off.append(dict(c))
        x1[f'{d}/{mp}/{me}/{path}'] = dict(A_t=A, R_t=Rt, offsets=off)
    res['X1'] = x1
    # verification of PLAN 1.1(3)
    wk = ch['weekday', 'natural', 'RRR4', 'plus_from_start']; mo = ch['month', 'natural', 'RRR8', 'plus_from_start']
    cnt = lambda ws, t, f: sum(f(*ws[w][t]) for w in ws)
    v = dict(weekday_r4_A_t=[round(a, 2) for a in x1['weekday/natural/RRR4/plus_from_start']['A_t']],
             weekday_r4_t3_outputs_start=cnt(wk, 3, lambda ok, ps, s, st: ps == st), weekday_r4_t4_outputs_start=cnt(wk, 4, lambda ok, ps, s, st: ps == st),
             month_r8_A6=x1['month/natural/RRR8/plus_from_start']['A_t'][5], month_r8_t6_outputs_start=cnt(mo, 6, lambda ok, ps, s, st: ps == st),
             month_r8_A12=x1['month/natural/RRR8/plus_from_start']['A_t'][11], month_r8_A24=x1['month/natural/RRR8/plus_from_start']['A_t'][23],
             month_r8_t7_nearest_alias=cnt(mo, 7, lambda ok, ps, s, st: ps == (st + 1) % 12),
             month_r8_t9_split=[cnt(mo, 9, lambda ok, ps, s, st: ps == (st + 9) % 12), cnt(mo, 9, lambda ok, ps, s, st: ps == (st + 3) % 12)])
    alt = {}
    for d, r in (('weekday', 5), ('month', 10), ('month', 9), ('weekday', 4), ('month', 8), ('egoside', 2), ('egoside', 3), ('compass', 2)):
        k = f'{d}/natural/RRR{r}/alternating_from_0'; Rt = x1[k]['R_t']
        alt[f'{d}_r{r}'] = dict(R_2N=Rt[-1], survives_steps=next((i for i, x in enumerate(Rt) if x < 1.0), len(Rt)))
    v['alternating'] = alt; res['X1_check_plan_1_1_3'] = v
    # X2: month natural alternating anomaly
    x2 = {}
    for r in (11, 12, 14, 16):
        f = load(V2DIR / 'local/rrr_month_natural.pt'); F = {op: editor_factors('rrr', f[op, r], op) for op in ('plus', 'minus')}
        M = torch.cat([F['plus'][0], F['plus'][1].T, F['minus'][0], F['minus'][1].T], 1)
        q, sv, _ = torch.linalg.svd(M, full_matrices=False); Q = q[:, sv > sv.max() * 1e-12]; I = torch.eye(Q.shape[1], dtype=torch.float64)
        Ap = I + (Q.T @ F['plus'][0]) @ (F['plus'][1] @ Q); Am = I + (Q.T @ F['minus'][0]) @ (F['minus'][1] @ Q); L = Am @ Ap
        P = I.clone(); norms = []
        for _ in range(12): P = P @ L; norms.append(float(torch.linalg.matrix_norm(P, 2)))
        Afull_m = lambda x: x + F['minus'][0] @ (F['minus'][1] @ x)
        c = Afull_m(F['plus'][2]) + F['minus'][2]
        ws = ch['month', 'natural', f'RRR{r}', 'alternating_from_0']; kinds = Counter()
        rs = {}
        for fpath in sorted((V2DIR / 'results/shards').glob(f'chain_month_natural_RRR{r}_alternating_from_0_*.jsonl')):
            for rec in rows(fpath): rs.setdefault(rec['world_id'], {})[rec['step']] = (rec['score'], Ev.parse_state(rec['text'], 'month')[0], rec['state'])
        for w, steps in rs.items():
            bad = [k for k in sorted(steps) if not steps[k][0]['success']]
            if not bad: kinds['no_failure'] += 1; continue
            sc, ps, st = steps[bad[0]]   # classify by the parsed month word, not the grammar-dependent 'target' flag
            kinds['wrong_month' if ps is not None and ps != st else 'unparsable_month' if ps is None else
                  'fact_clause' if not sc['preserved'] else 'grammar_or_end'] += 1
        x2[f'r{r}'] = dict(spectral_radius=float(torch.linalg.eigvals(L).abs().max()), max_power_norm_k_le_12=max(norms), power_norms=norms,
                           translation_norm=float(c.norm()), first_failure_type=dict(kinds), R_24=x1[f'month/natural/RRR{r}/alternating_from_0']['R_t'][-1])
    res['X2'] = x2
    # X3: month sigma_max
    alg = read(V2DIR / 'results/algebra.json'); x3 = {}
    for r in (8, 9, 10, 11, 12, 14, 16):
        k = f'month/scrmax/RRR{r}/plus_from_start'
        x3[f'r{r}'] = dict(harmonics_sigma_order=alg[f'month/scrmax/RRR{r}']['plus']['harmonics_present'], A_t=x1[k]['A_t'], R_2N=x1[k]['R_t'][23],
                           offsets_t1_6=x1[k]['offsets'][:6])
    res['X3'] = x3; res['note'] = 'Exploratory; v2 confirm2 shards (already evaluated). Offsets are (decoded - start) mod N in the map order.'
    res['seconds'] = time.time() - t0; dump('results/p0_diag.json', res)
    # figures
    fig, axs = plt.subplots(1, 2, figsize=(13, 3.6))
    for ax, d, rs_ in ((axs[0], 'weekday', (4, 5, 6)), (axs[1], 'month', (8, 9, 10, 11))):
        N = len(S.states(d))
        for r in rs_: ax.plot(range(1, 2 * N + 1), x1[f'{d}/natural/RRR{r}/plus_from_start']['A_t'][:2 * N], 'o-', ms=3, label=f'r={r}')
        for x in (N, 2 * N): ax.axvline(x, color='#999999', ls=':')
        ax.set_title(f'{d} natural RRR, one-way plus: per-step accuracy A_t', fontsize=9); ax.set_xlabel('t'); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/p0_At.png', dpi=140)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4))
    for ax, (d, r) in zip(axs, (('weekday', 4), ('month', 8))):
        N = len(S.states(d)); off = x1[f'{d}/natural/RRR{r}/plus_from_start']['offsets'][:2 * N]
        Mx = np.array([[o.get(str(j), 0) for j in range(N)] for o in off]).T
        ax.imshow(Mx, aspect='auto', origin='lower', cmap='Greys'); ax.set_xlabel('t (1..2N)'); ax.set_ylabel('decoded - start (mod N)')
        ax.set_xticks(range(2 * N)); ax.set_xticklabels(range(1, 2 * N + 1), fontsize=6); ax.set_title(f'{d} r={r}: offset counts', fontsize=9)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/p0_offsets.png', dpi=140)
    print(json.dumps(v, indent=1), flush=True)


if __name__ == '__main__':
    main()
