"""Shared figure style and loaders (W3): only locked results and shards are read; output vector PDF with complete legends; fixed
backbone colours. Each make_*.py records its inputs (SHA256) in figs/manifest.json."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BB_COL = {'bart': '#1f77b4', 't5': '#d62728'}
BB_NAME = {'bart': 'BART-base', 't5': 'T5Gemma'}
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 8, 'legend.fontsize': 6.5, 'pdf.fonttype': 42})
FIG = PAPER / 'figs'


def chains(f):
    out = defaultdict(dict)
    with open(REPO / f) as g:
        for r in csv.DictReader(g):
            key = (r['backbone'], r['domain'], r['method'], r['path'].replace('_from_start', ''))
            out[key][int(r['t'])] = dict(A=float(r['A_t']), R=float(r['R_t']))
    return out


def curve(ch, key, field='R'):
    d = ch.get(key)
    return None if not d else ([t for t in sorted(d)], [d[t][field] for t in sorted(d)])


def seed_median(ch, bb, d, stem, path, field='R', seeds=(42, 43, 44)):
    import numpy as np
    cs = [curve(ch, (bb, d, f'{stem}_s{s}', path), field) for s in seeds]; cs = [c for c in cs if c]
    if not cs: return None
    n = min(len(c[0]) for c in cs); return cs[0][0][:n], list(np.median([c[1][:n] for c in cs], 0))


def finish(fig, name, inputs):
    fig.tight_layout(); fig.savefig(FIG / f'{name}.pdf'); plt.close(fig)
    m = FIG / 'manifest.json'; man = json.loads(m.read_text()) if m.exists() else {}
    man[name] = dict(script=f'paper/figs/make_{name}.py', inputs={f: sha(f) for f in inputs}); m.write_text(json.dumps(man, indent=1))
    print('wrote', name, flush=True)
