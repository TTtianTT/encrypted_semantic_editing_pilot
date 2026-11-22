"""Shared utilities for symmetry_composability_v1. Every entrypoint calls require_slurm()."""
import csv
import hashlib
import itertools
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
EXP = REPO / 'experiments'
SOURCE = REPO / '.four-domain-worktree/experiments/four_domain_state_coverage_v1'
CES = REPO / '.causal-next-edit-worktree/experiments/causal_next_edit_stability_v1'
V2 = EXP / 'operator_residual_v2'
CWR = EXP / 'canonical_write_reachability_v1'
COBJ = EXP / 'canonical_objective_v1'
CONF = EXP / 'canonical_confirmation_v1'
MAN = EXP / 'manifold_controls_v1'
SEEDS = (42, 43, 44)
BOOT_SEED = 3101
BOOT_N = 2000


def require_slurm():
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'), 'Use sbatch + srun'


# ---------------------------------------------------------------- io
def read(p): return json.loads(Path(p).read_text())
def rows(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def _target(name):
    p = Path(name)
    p = p if p.is_absolute() else ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def dump(name, value):
    p = _target(name); q = p.with_suffix(p.suffix + '.tmp')
    q.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=_jsonable) + '\n'); q.replace(p)


def write(name, values):
    p = _target(name); q = p.with_suffix(p.suffix + '.tmp')
    with q.open('w') as f:
        for r in values:
            f.write(json.dumps(r, ensure_ascii=False, default=_jsonable) + '\n')
    q.replace(p)


def csvwrite(name, values):
    if not values:
        return
    p = _target(name)
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in values for k in r)), lineterminator='\n')
        w.writeheader(); w.writerows(values)


def _jsonable(x):
    if isinstance(x, (np.floating,)): return float(x)
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, (np.bool_,)): return bool(x)
    raise TypeError(type(x))


def save(name, value):
    import torch
    p = _target(name); q = p.with_suffix('.tmp'); torch.save(value, q); q.replace(p)


def load(p):
    import torch
    return torch.load(p, map_location='cpu', weights_only=False)


def verify_inputs(keys=None):
    """Check SHA256 of frozen inputs recorded by p0_preflight (all, or those whose key starts with a prefix)."""
    man = read(ROOT / 'inputs_manifest.json')
    bad = []
    for r in man['files']:
        if keys and not any(r['key'].startswith(k) for k in keys):
            continue
        p = REPO / r['path']
        if not p.exists() or sha(p) != r['sha256']:
            bad.append(r['path'])
    assert not bad, f'Frozen input changed or missing: {bad[:5]}'
    return man


# ---------------------------------------------------------------- frozen model / semantics
def source_path():
    if str(SOURCE) not in sys.path:
        sys.path.insert(0, str(SOURCE))


def engine():
    require_slurm(); source_path()
    from backend import Backend
    return Backend('bart')


def semantics():
    source_path()
    import semantics as s
    import evaluator as e
    return s, e


def core():
    if str(V2) not in sys.path:
        sys.path.append(str(V2))
    import core as c
    return c


def worlds(domain):
    return rows(SOURCE / f'data/{domain}/worlds.jsonl')


# ---------------------------------------------------------------- statistics
def wilson(k, n):
    if not n:
        return None
    z = 1.959963984540054; p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0., float(c - h)), min(1., float(c + h))]


def rate(values):
    v = [bool(x) for x in values]; k = sum(v); n = len(v)
    return dict(n=n, k=k, rate=k / n if n else None, ci95=wilson(k, n))


def boot_idx(n, seed=BOOT_SEED, reps=BOOT_N):
    return np.random.default_rng(seed).integers(n, size=(reps, n))


def boot_mean(values, seed=BOOT_SEED):
    x = np.asarray(values, float)
    if not len(x):
        return None
    b = x[boot_idx(len(x), seed)].mean(1)
    return dict(mean=float(x.mean()), ci95=np.quantile(b, [.025, .975]).tolist(), n=len(x))


def boot_stat(fn, n, seed=BOOT_SEED, reps=BOOT_N):
    """Bootstrap any statistic fn(index_array) over world indices."""
    idx = boot_idx(n, seed, reps)
    vals = np.array([fn(i) for i in idx], float)
    return dict(value=float(fn(np.arange(n))), ci95=np.nanquantile(vals, [.025, .975]).tolist())


def two_prop_z(k1, n1, k2, n2):
    from scipy.stats import norm
    p = (k1 + k2) / (n1 + n2); se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return dict(z=None, p_one_sided=None, p_two_sided=None)
    z = (k1 / n1 - k2 / n2) / se
    return dict(z=float(z), p_one_sided=float(norm.sf(z)), p_two_sided=float(2 * norm.sf(abs(z))))


# ---------------------------------------------------------------- geometry
def e_iso_world(P, Q):
    """Affine-isometry equivariance error for one world. P,Q: (n,d) float64 arrays, rows paired x -> gx.

    min_{R in O(d), t} sum ||R p + t - q||^2 = ||P~||^2 + ||Q~||^2 - 2 ||P~^T Q~||_*, normalised by sum ||q - p||^2.
    Computed in the span of both point sets (dimension <= 2n) via QR, identical to full space.
    """
    P = np.asarray(P, np.float64); Q = np.asarray(Q, np.float64)
    Pc = P - P.mean(0); Qc = Q - Q.mean(0)
    basis, _ = np.linalg.qr(np.concatenate([Pc, Qc]).T)  # d x <=2n
    a = Pc @ basis; b = Qc @ basis
    nuc = np.linalg.svd(a.T @ b, compute_uv=False).sum()
    resid = max(0., (a ** 2).sum() + (b ** 2).sum() - 2 * nuc)
    den = ((Q - P) ** 2).sum()
    return resid / den if den > 0 else np.nan


def e_iso(V, pairs):
    """V: (W, S, d) world x state-index x dim. pairs: list of (i, j) state-index pairs i -> g(i)=j. Returns per-world array."""
    src = [i for i, _ in pairs]; dst = [j for _, j in pairs]
    return np.array([e_iso_world(V[w, src], V[w, dst]) for w in range(V.shape[0])])


def mean_sqdist(V):
    """D-bar(x,x') = mean over worlds of ||v_w(x) - v_w(x')||^2."""
    diff = V[:, :, None, :] - V[:, None, :, :]
    return (diff ** 2).sum(-1).mean(0)


def orbit_key(kind, n):
    if kind == 'cyclic':
        return lambda i, j: min(abs(i - j), n - abs(i - j))
    if kind == 'open':
        return lambda i, j: abs(i - j)
    raise ValueError(kind)


def group_r2(D, key):
    n = len(D); prs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    vals = np.array([D[i, j] for i, j in prs]); keys = [key(i, j) for i, j in prs]
    groups = {}
    for k, v in zip(keys, vals):
        groups.setdefault(k, []).append(v)
    proj = np.array([np.mean(groups[k]) for k in keys])
    tot = ((vals - vals.mean()) ** 2).sum()
    if tot == 0 or len(groups) == len(prs):
        return np.nan
    return float(1 - ((vals - proj) ** 2).sum() / tot)


def sep(V):
    C = V - V.mean(1, keepdims=True)
    cbar = C.mean(0, keepdims=True)
    return float(1 - ((C - cbar) ** 2).sum() / (C ** 2).sum())


def delta_opp(D):
    n = len(D); assert n == 4
    allm = np.mean([D[i, j] for i in range(n) for j in range(i + 1, n)])
    return float((D[0, 2] - D[1, 3]) / allm)


def permutations_for(n, k=1000, seed=BOOT_SEED):
    if n <= 7:
        return [list(p) for p in itertools.permutations(range(n))]
    rng = np.random.default_rng(seed)
    return [list(range(n))] + [rng.permutation(n).tolist() for _ in range(k)]


def conj_pairs(pairs, perm):
    """Replace g by pi o g o pi^{-1}: pairs (x, gx) -> (pi x, pi gx)."""
    return [(perm[i], perm[j]) for i, j in pairs]


def quantile_of(obs, null):
    null = np.asarray(null, float)
    return dict(observed=float(obs), null_q05=float(np.quantile(null, .05)), null_q95=float(np.quantile(null, .95)),
                frac_le=float((null <= obs + 1e-12).mean()), frac_ge=float((null >= obs - 1e-12).mean()), null_n=len(null))


# ---------------------------------------------------------------- operator algebra
def core_matrix(U, V):
    """A = I + U V (column convention). U: d x r, V: r x d. Return Q (d x k) orth basis of [U, V^T] and A_Q = Q^T A Q."""
    import torch
    U = U.double(); V = V.double()
    M = torch.cat([U, V.T], 1)
    q, s, _ = torch.linalg.svd(M, full_matrices=False)
    keep = s > s.max() * max(M.shape) * torch.finfo(torch.float64).eps
    Q = q[:, keep]
    AQ = torch.eye(Q.shape[1], dtype=torch.float64) + (Q.T @ U) @ (V @ Q)
    return Q, AQ


def operator_stats(U, V, b, kmax=50):
    import torch
    Q, AQ = core_matrix(U, V)
    sv = torch.linalg.svdvals(AQ)
    ev = torch.linalg.eigvals(AQ)
    nn = float(torch.linalg.norm(AQ @ AQ.T - AQ.T @ AQ) / torch.linalg.norm(AQ) ** 2)
    b = b.double(); Uq, _, _ = torch.linalg.svd(U.double(), full_matrices=False)
    r = int(torch.linalg.matrix_rank(U.double()))
    Pu = Uq[:, :r]
    drift = float(torch.linalg.norm(b - Pu @ (Pu.T @ b)) / torch.linalg.norm(b)) if float(torch.linalg.norm(b)) > 0 else None
    growth = []; P = torch.eye(AQ.shape[0], dtype=torch.float64)
    for k in range(1, kmax + 1):
        P = P @ AQ; growth.append(float(torch.linalg.matrix_norm(P, 2)))
    return dict(dim=int(Q.shape[1]), ISO=float(((sv - 1) ** 2).mean().sqrt()), sv_min=float(sv.min()), sv_max=float(sv.max()),
                spectral_radius=float(ev.abs().max()), NN=nn, DRIFT=drift,
                eig_modulus=ev.abs().tolist(), eig_phase=torch.angle(ev).tolist(), singular_values=sv.tolist(),
                power_norm=growth), Q, AQ


def editor_factors(kind, obj, op):
    """Return (U d x r, V r x d, b d) in column convention."""
    if kind == 'editor':
        sd = obj
        return sd[f'{op}.u.weight'].double(), sd[f'{op}.v.weight'].double(), sd[f'{op}.b'].double()
    if kind == 'rrr':
        f = obj
        return f['right'].T.double(), f['left'].T.double(), f['bias'].double()
    raise ValueError(kind)
