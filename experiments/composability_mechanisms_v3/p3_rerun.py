"""P3 helper (run by p_diag.py as a subprocess inside the Slurm step; not an entrypoint of its own).
Re-runs the locked analysis of v1 (symmetry_composability_v1/e1_analyze.py) or v2 (composability_mechanisms_v1/analyze.py) on the
already-decoded shards with a set of confirm worlds removed, without writing anything into those experiments: dump() is redirected,
csvwrite() and figure saving are disabled, and the only edits are (a) shard records of excluded worlds are dropped, (b) the
'160 worlds' assertion is removed, (c) v1 confirm-set geometry is computed on the remaining worlds.
usage: python p3_rerun.py v1|v2 EXCLUDE_JSON OUT_JSON"""
import json
import sys
import types
from pathlib import Path

exp, excl_path, out_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
EXP = Path(__file__).resolve().parents[1]
D = EXP / ('symmetry_composability_v1' if exp == 'v1' else 'composability_mechanisms_v1')
sys.path.insert(0, str(D))
excluded = set(json.loads(excl_path.read_text())['excluded_world_ids'])
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.figure  # noqa: E402
matplotlib.figure.Figure.savefig = lambda *a, **k: None
captured = {}

src = (D / ('e1_analyze.py' if exp == 'v1' else 'analyze.py')).read_text()
if exp == 'v2':
    old = "assert len(ws) == 160, (d, mp, me, path, len(ws)); "
    assert src.count(old) == 1; src = src.replace(old, '')
mod = types.ModuleType('locked_analysis'); mod.__file__ = str(D / 'analysis_rerun.py')
exec(compile(src.replace("if __name__ == '__main__':", "if False:"), str(D / 'analysis_rerun.py'), 'exec'), mod.__dict__)
orig_load = mod.load_shards


def load_shards():
    a, b = orig_load()
    if exp == 'v1':
        for k in list(a):
            for w in list(a[k]):
                if w in excluded: del a[k][w]
        for k in list(b): b[k] = [r for r in b[k] if r['world_id'] not in excluded]
    else:
        for k in list(a):
            for w in list(a[k]):
                if w in excluded: del a[k][w]
    return a, b


mod.load_shards = load_shards
if exp == 'v2':
    # singles were stored as bare success flags; reload them with world ids so excluded worlds can be dropped
    from collections import defaultdict
    def load_shards_v2():
        ch = defaultdict(dict); sg = defaultdict(list)
        for f in sorted((D / 'results/shards').glob('*.jsonl')):
            for r in mod.rows(f):
                if r['world_id'] in excluded: continue
                if f.name.startswith('chain_'):
                    ch[r['domain'], r['map'], r['method'], r['path']].setdefault(r['world_id'], {})[r['step']] = (r['trajectory_success'], r['operation'], r['state'], r['score']['success'])
                else:
                    sg[r['domain'], r['map'], r['method'], r['template']].append(r['score']['success'])
        return ch, sg
    mod.load_shards = load_shards_v2
else:
    def R(chains, d, method, path, k):
        ws = chains[d, method, path]; return mod.rate([ws[w][k] for w in ws])
    mod.R = R
    orig_cache = mod.e1_cache
    def e1_cache(d, split, s):
        c = orig_cache(d, split, s)
        if split != 'confirm': return c
        ids = c.get('world_ids') or [w['world_id'] for w in mod.e1_worlds(d, 'confirm')]; assert len(ids) == len(c['h']); keep = [i for i, w in enumerate(ids) if w not in excluded]
        return dict(c, h=c['h'][keep], m=c['m'][keep])
    mod.e1_cache = e1_cache
mod.dump = lambda name, value: captured.__setitem__(name, value)
mod.csvwrite = lambda *a, **k: None
mod.require_slurm = lambda: None   # the parent process already asserted the Slurm step
mod.main()
import symutil as _su  # the experiment's own symutil (its directory is first on sys.path)
out_path.write_text(json.dumps(captured, indent=1, default=_su._jsonable) + '\n')
