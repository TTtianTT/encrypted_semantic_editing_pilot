"""Pre-lock gates (GPU, train + dev only). --backbone bart|t5.
GR: template-0 and binding domains reuse v4's GR on the same train + dev caches (results/gates_<bb>.json of v4); multi-template domains:
results/gates_mt_<bb>.json (per template, before the split). GT: data/audit.json (confirm5 single-token state words and slot positions;
multi-template per template). GB (multi-template domains in N): RRR-16 dev one-way plus R_2N >= 0.95 -> 16, else RRR-32 -> 32, else the
domain leaves N; harmonic planes of each multi-template domain from its train split (training templates pooled) saved here.
Rank grid (PLAN 6.1): RRR-r and FF-r for r in the grid; ranks already fitted in v4 (local/<bb>_R_<d>.pt) are reused unchanged, missing
ranks are fitted here with the same procedure (ridge chosen per rank, so the reused ranks are unaffected)."""
import time
from lib5 import *


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); res = dict(backbone=bb)
    audit = read(ROOT / 'data/audit.json'); v4g = read(V4DIR / f'results/gates_{bb}.json'); split = read(ROOT / 'data/templates_split.json')['split']
    res['GR_reused_v4'] = v4g['GR']; res['GR_mt'] = read(ROOT / f'results/gates_mt_{bb}.json')['GR']
    gt = {}
    for d in L_DOMAINS[bb] + (B_DOMAINS if bb == 'bart' else []):
        f = audit['domains'][d]['failures']; bad = {k: v for k, v in f.items() if k.startswith(bb + '_')}
        gt[d] = dict(failures=bad, pass_=not bad and audit['domains'][d]['pass'])
    res['GT_confirm5'] = gt; gb = {}
    for d in MT_DOMAINS[bb]:
        if not split[d]['in_N']: gb[d] = dict(base_rank=None, reason='fewer than 8 held-out templates'); continue
        N = len(S.states(d)); P = planes(bb, d); save(f'local/planes_{bb}_{d}.pt', P)
        fits, info = fit_rrr4(bb, d, 'natural', [16, 32]); save(f'local/{bb}_rrr_{d}_natural_base.pt', fits); r = {}
        for rank in (16, 32):
            r[rank] = dev_chain(eng, bb, d, 'natural', {op: RRRop(fits[op, rank]) for op in ('plus', 'minus')}, ['plus'] * (2 * N))[-1]
            if r[rank]['rate'] >= .95: break
        base = 16 if r[16]['rate'] >= .95 else 32 if r.get(32, {}).get('rate', 0) >= .95 else None
        gb[d] = dict(dev_R2N={str(k): v for k, v in r.items()}, ridge=info, base_rank=base, fits_sha256=sha(ROOT / f'local/{bb}_rrr_{d}_natural_base.pt'),
                     planes=[dict(k=k, dim=B.shape[1]) for k, B in P], planes_sha256=sha(ROOT / f'local/planes_{bb}_{d}.pt'))
        print('GB', bb, d, {k: v['rate'] for k, v in r.items()}, 'base', base, flush=True)
    res['GB'] = gb; res['N_domains'] = [d for d in MT_DOMAINS[bb] if gb[d].get('base_rank')]
    grid = {}
    for d in GRID_DOMAINS:
        v4f = load(V4DIR / f'local/{bb}_R_{d}.pt'); have = sorted({k[2] for k in v4f}); need = grid_ranks(bb, d); miss = [r for r in need if r not in have]
        P = planes(bb, d); Q1 = P[0][1]; assert P[0][0] == 1 and Q1.shape[1] == 2; info = {}
        if miss:
            rr, ri = fit_rrr4(bb, d, 'natural', miss); ff, fi = fit_rrr4(bb, d, 'natural', miss, ff=True, Q1=Q1)
            fits = {('RRR', op, r): rr[op, r] for op in ('plus', 'minus') for r in miss} | {('FF', op, r): ff[op, r] for op in ('plus', 'minus') for r in miss}
            save(f'local/{bb}_R_{d}_v5.pt', fits); info = dict(RRR=ri, FF=fi)
        grid[d] = dict(ranks=need, reused_from_v4=[r for r in need if r in have], fitted_here=miss, ridge_here=info,
                       v4_sha256=sha(V4DIR / f'local/{bb}_R_{d}.pt'), v5_sha256=sha(ROOT / f'local/{bb}_R_{d}_v5.pt') if miss else None)
        print('grid', bb, d, grid[d]['reused_from_v4'], 'fitted', miss, flush=True)
    res['grid'] = grid; res['resources'] = eng.resources(); res['seconds'] = time.time() - t0
    dump(f'results/gates_{bb}.json', res)


if __name__ == '__main__':
    main()
