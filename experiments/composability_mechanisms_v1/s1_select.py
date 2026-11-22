"""S1a map selection (CPU, before the lock; v1 train+dev, template 0 pooled states only).
Cyclic domains: every directed N-cycle (N <= 7) or 2000 random ones (N = 12, seed 3101); daysago: 2000 random path orders
(excluding the natural order and its reverse). sigma_max = largest E_iso; sigma_med = median (lower median; ties -> lexicographically
smallest). For Z4, sigma_med is dropped when it equals the natural cycle (either direction) or sigma_max."""
import itertools
import time
import torch
from symutil import *
import sym2_semantics as S

N_SAMPLE = 2000


def X_for(d):
    V = torch.cat([pooled2(d, sp, 0)['pooled'] for sp in ('train', 'dev')]).double().numpy()
    return reduce_worlds(V)[1]


def candidates(d, rng):
    st = S.states(d)
    if d == 'daysago':
        nat = tuple(st); out = set()
        while len(out) < N_SAMPLE:
            p = tuple(int(x) for x in rng.permutation(st))
            if p not in (nat, nat[::-1]): out.add(p)
        return sorted(out)
    rest = st[1:]
    if len(st) <= 7:
        return [(0,) + p for p in itertools.permutations(rest)]
    out = {tuple(range(len(st)))}
    while len(out) < N_SAMPLE + 1:
        out.add((0,) + tuple(int(x) for x in rng.permutation(rest)))
    return sorted(out)


def pairs_of(d, seq):
    idx = {s: i for i, s in enumerate(S.states(d))}
    if d == 'daysago':
        return [(idx[a], idx[b]) for a, b in zip(seq[:-1], seq[1:])]
    return [(idx[seq[i]], idx[seq[(i + 1) % len(seq)]]) for i in range(len(seq))]


def main():
    require_slurm(); t0 = time.time(); rng = np.random.default_rng(BOOT_SEED); out = dict(maps={}, summary={}); rows_ = []
    for d in V1_DOMAINS:
        X = X_for(d); cand = candidates(d, rng)
        nat = tuple(S.states(d)); natv = float(e_iso(X, pairs_of(d, nat)).mean())
        vals = [(float(e_iso(X, pairs_of(d, c)).mean()), c) for c in cand]
        rows_ += [dict(domain=d, seq=' '.join(map(str, c)), E_iso=v, natural=c == nat) for v, c in vals]
        pool = [(v, c) for v, c in vals if c != nat] if d != 'daysago' else vals
        smax = max(pool, key=lambda z: (z[0], [-x for x in z[1]]))
        ordered = sorted(vals, key=lambda z: z[0]); medv = ordered[(len(ordered) - 1) // 2][0]
        smed = min([z for z in vals if abs(z[0] - medv) < 1e-12], key=lambda z: z[1])
        natural_cycles = {nat, (nat[0],) + nat[1:][::-1]} if d != 'daysago' else {nat, nat[::-1]}
        keyname = 'path' if d == 'daysago' else 'cycle'
        maps = {'scrmax': {keyname: list(smax[1]), 'E_iso': smax[0]}}
        if smed[1] in natural_cycles or smed[1] == smax[1]:
            out['summary'].setdefault('omitted_scrmed', []).append(d)
        else:
            maps['scrmed'] = {keyname: list(smed[1]), 'E_iso': smed[0]}
        out['maps'][d] = maps
        out['summary'][d] = dict(natural_E_iso=natv, candidates=len(cand), scrmax=maps['scrmax'], scrmed=maps.get('scrmed'),
                                 ratio_max_over_natural=smax[0] / natv, median_E_iso=medv,
                                 quantiles=np.quantile([v for v, _ in vals], [0, .05, .5, .95, 1]).tolist())
        print(d, out['summary'][d], flush=True)
    out['rule'] = __doc__; out['seconds'] = time.time() - t0
    dump('results/s1a_selection.json', out); csvwrite('results/s1a_candidates.csv', rows_)


if __name__ == '__main__':
    main()
