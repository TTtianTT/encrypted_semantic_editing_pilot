"""Descriptive 95% CIs for the report (CPU, after the analysis; AMENDMENT_01, no verdict depends on it). For every chain rate R_t in
results/chains.csv at the steps the predictions use (1, 2, 8, 12, 2N, 30), the Wilson score interval on n worlds. Output:
results/report_ci.json, keyed '<backbone>/<domain>/<method>/<path>/R<t>'."""
import csv
import math
from symutil import *
import sym5_semantics as S


def wilson(k, n, z=1.959964):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def main():
    require_slurm(); out = {}
    with open(ROOT / 'results/chains.csv') as f:
        for r in csv.DictReader(f):
            d = r['domain']; t = int(r['t']); n = int(r['n']); N = len(S.states(d)) if d not in ('bind3', 'bind3fix', 'name3') else None
            if t not in {1, 2, 8, 12, 30} | ({2 * N} if N else set()): continue
            R = float(r['R_t']); k = round(R * n)
            out[f"{r['backbone']}/{d}/{r['method']}/{r['path'].replace('_from_start', '')}/R{t}"] = dict(rate=R, n=n, k=k, wilson95=wilson(k, n))
    dump(ROOT / 'results/report_ci.json', out); print('rates', len(out), flush=True)


if __name__ == '__main__':
    main()
