"""Pre-lock closed-form fits (GPU, before the lock; deterministic, train worlds only; PLAN v7 B7 NI): T5Gemma month RRR-r for r in
{8, 9, 10, 11, 16} and FF-r for r in {8, 9, 10} where no earlier fit exists (v4 / v5 grids hold r in 10..14 and the v4 base RRR-16), with
v4's fit_rrr4 procedure (ridge per rank on an inner train split). Output: local/t5_R_month_v7.pt, results/prep_fits.json."""
import time
from lib7 import *
from cells7 import T5_NI_RRR, T5_NI_FF


def have(bb, d, kind, r):
    if kind == 'RRR' and r == 16: return True
    for f in (V5DIR / f'local/{bb}_R_{d}_v5.pt', V4DIR / f'local/{bb}_R_{d}.pt'):
        if f.exists() and (kind, 'plus', r) in load(f): return True
    return False


def main():
    require_slurm(); t0 = time.time(); bb, d = 't5', 'month'
    miss = {k: [r for r in rs if not have(bb, d, k, r)] for k, rs in (('RRR', T5_NI_RRR), ('FF', T5_NI_FF))}
    P = planes(bb, d); Q1 = P[0][1]; assert P[0][0] == 1 and Q1.shape[1] == 2; fits = {}; info = {}
    if miss['RRR']:
        rr, ri = fit_rrr4(bb, d, 'natural', miss['RRR']); fits |= {('RRR', op, r): rr[op, r] for op in ('plus', 'minus') for r in miss['RRR']}; info['RRR'] = ri
    if miss['FF']:
        ff, fi = fit_rrr4(bb, d, 'natural', miss['FF'], ff=True, Q1=Q1); fits |= {('FF', op, r): ff[op, r] for op in ('plus', 'minus') for r in miss['FF']}; info['FF'] = fi
    save(ROOT / f'local/{bb}_R_{d}_v7.pt', fits)
    dump('results/prep_fits.json', dict(missing=miss, ridge=info, sha256=sha(ROOT / f'local/{bb}_R_{d}_v7.pt'), seconds=time.time() - t0))
    print('fitted', miss, flush=True)


if __name__ == '__main__':
    main()
