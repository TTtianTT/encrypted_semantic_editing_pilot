"""BART core (GPU, after the lock). --stage g30: G3-0 sanity gate (exits non-zero on failure, stopping lane A).
--stage h: section 6.3 surgery conditions on confirm3 (4 cyclic domains), 3 paths x 2N steps, vote-model argmax recorded."""
import time
from lib3 import *


def paths3(N):
    return dict(plus_from_start=['plus'] * (2 * N), minus_from_start=['minus'] * (2 * N), alt_from_start=['plus', 'minus'] * N)


def v2fit(d, r):
    f = load(V2DIR / f'local/rrr_{d}_natural.pt')
    return {op: f[op, r] for op in ('plus', 'minus')} if ('plus', r) in f else None


def conditions(eng, p, d):
    """name -> ops dict. Locked condition set (section 6.3)."""
    P = planes('bart', d); pos = slots('bart', d, 'confirm3'); X = slot_matrix('bart', d, 'train'); ks = [k for k, _ in P]
    T = {op: RRRop(f) for op, f in v2fit(d, 16).items()}; cal = p['calib']['bart'][d]; out = {}
    def freeze(S_): return {op: Freeze(T[op], bvec(P, S_), pos) for op in T}
    def pe(K):
        B = torch.cat([B for k, B in P if k in K], 1); return {op: PlaneEd(*fit_plane_editor(X, B, d, op), B, pos) for op in ('plus', 'minus')}
    out['F_empty'] = T
    for k in ks: out[f'F_{{{k}}}'] = freeze({k})
    out['F_not1'] = freeze(set(ks) - {1})
    out['E_all'] = pe(set(ks)); out['E_{1}'] = pe({1})
    K = cal['Kstar']['K']
    if sorted(K) != sorted(ks) and sorted(K) != [1]: out['E_Kstar'] = pe(set(K))
    r = cal['Kstar']['dim']; f = v2fit(d, r)
    if f is None:
        fits, _ = fit_rrr3('bart', d, 'natural', [r]); save(f'local/bart_rrr_{d}_natural_r{r}.pt', fits); f = {op: fits[op, r] for op in ('plus', 'minus')}
    out[f'RRR{r}_dimKstar'] = {op: RRRop(f[op]) for op in ('plus', 'minus')}
    out['R16_slot'] = {op: SlotOnly(T[op], pos) for op in T}
    return out, P


def main():
    require_slurm(); p = verify_protocol3(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine3('bart')
    if stage == 'g30':
        res = dict(RRR16={}, C1={})
        for d in V1_DOMAINS:
            N = len(S.states(d)); T = {op: RRRop(f) for op, f in v2fit(d, 16).items()}
            start, L_ = (2, 7) if d == 'daysago' else ('world_start', 2 * N)
            run_chain(eng, 'bart', d, 'natural', 'RRR16', T, 'g30_plus', start, ['plus'] * L_)
            res['RRR16'][d] = chain_rate('bart', d, 'natural', 'RRR16', 'g30_plus', L_)
            for s in SEEDS:
                ed = load_editor(eng, V1 / f'local/e1_C1_{d}_s{s}_0600.pt')
                run_chain(eng, 'bart', d, 'natural', f'C1_s{s}', {op: ed[op] for op in ('plus', 'minus')}, 'g30_plus', start, ['plus'] * 2)
                res['C1'][f'{d}/s{s}'] = chain_rate('bart', d, 'natural', f'C1_s{s}', 'g30_plus', 2)
        res['pass'] = all(v['rate'] >= .95 for v in res['RRR16'].values()) and all(v['rate'] <= .20 for v in res['C1'].values())
        res['seconds'] = time.time() - t0; dump('results/g30.json', res); print('G3-0', res['pass'], flush=True)
        assert res['pass'], 'G3-0 failed: stop and debug the pipeline'
        return
    for d in CYC:
        ops, P = conditions(eng, p, d); N = len(S.states(d)); cal = p['calib']['bart'][d]
        model = dict(P=P, lams={m: torch.tensor(v['lam'], dtype=torch.float64) for m, v in cal['models'].items()})
        for name, op in ops.items():
            for pn, oplist in paths3(N).items():
                run_chain(eng, 'bart', d, 'natural', name, op, pn, 'world_start', oplist, model=model)
            print('h', d, name, round(time.time() - t0), flush=True)
    dump('results/h_complete.json', dict(seconds=time.time() - t0, resources=eng.resources(), protocol_sha256=sha(ROOT / 'protocol.json')))


if __name__ == '__main__':
    main()
