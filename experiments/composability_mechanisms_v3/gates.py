"""Pre-lock gates (GPU, train+dev only). --backbone bart|t5.
GR: reencode single-step success >= 0.99 on train+dev for every (backbone, domain, template) to be edited.
GT: single-token state words and constant template-0 slot positions under this backbone (from data/audit.json).
GB: per V domain, RRR-16 dev one-way plus R_2N >= 0.95 -> base rank 16; else RRR-32 -> 32; else the domain leaves V and R.
V0 (descriptive): a_k and s_k from train for every V domain."""
import time
from lib4 import *


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine4(bb); res = dict(backbone=bb)
    audit = read(ROOT / 'data/audit.json')
    doms = (V_DOMAINS + ['compass'] + X_DOMAINS) if bb == 'bart' else V_DOMAINS
    res['GR'] = {d: dict(**(r := reencode_rate(eng, bb, d)), pass_=r['rate'] >= .99) for d in doms}
    gt = {}
    for d in doms:
        f = audit['domains'][d]['failures']; bad = {k: v for k, v in f.items() if k.startswith(bb + '_')}
        gt[d] = dict(failures=bad, pass_=not bad and audit['domains'][d]['pass'])
    res['GT'] = gt
    ok = {d: res['GR'][d]['pass_'] and gt[d]['pass_'] for d in doms}; gb = {}
    for d in V_DOMAINS:
        if not ok[d]: gb[d] = dict(base_rank=None, reason='GR/GT'); continue
        N = len(S.states(d)); fits, info = fit_rrr4(bb, d, 'natural', [16, 32]); save(f'local/{bb}_rrr_{d}_natural_base.pt', fits); r = {}
        for rank in (16, 32):
            ops = {op: RRRop(fits[op, rank]) for op in ('plus', 'minus')}
            r[rank] = dev_chain(eng, bb, d, 'natural', ops, ['plus'] * (2 * N))[-1]
            if r[rank]['rate'] >= .95: break
        base = 16 if r[16]['rate'] >= .95 else 32 if r.get(32, {}).get('rate', 0) >= .95 else None
        gb[d] = dict(dev_R2N={str(k): v for k, v in r.items()}, ridge=info, base_rank=base, fits_sha256=sha(ROOT / f'local/{bb}_rrr_{d}_natural_base.pt'))
        print('GB', bb, d, {k: v['rate'] for k, v in r.items()}, 'base', base, flush=True)
    res['GB'] = gb
    res['V_domains'] = [d for d in V_DOMAINS if gb[d]['base_rank'] is not None]
    res['R_domains'] = [d for d in R_DOMAINS if d in res['V_domains']]
    res['excluded'] = dict(V=[d for d in V_DOMAINS if d not in res['V_domains']], other=[d for d in doms if d not in V_DOMAINS and not ok[d]])
    res['new_domains_passing'] = [d for d in ('hour', 'compass8', 'season') if d in res['V_domains']]
    if bb == 'bart': res['X_ok'] = {d: ok[d] for d in X_DOMAINS}; res['compass_ok'] = ok['compass']
    res['V0_amplitudes'] = {d: {str(k): v for k, v in amplitudes(bb, d).items()} for d in V_DOMAINS}
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0
    dump(f'results/gates_{bb}.json', res); print(json.dumps({k: v for k, v in res.items() if k in ('V_domains', 'R_domains', 'excluded', 'GR')}, indent=1, default=str), flush=True)


if __name__ == '__main__':
    main()
