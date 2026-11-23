"""Shared v4 machinery. Copied from v3 lib3.py (backbones, caches, slots, harmonic planes, vote model, surgery, chain runner,
RRR fitting, editor training, unit block, probe, write metrics) and extended with PLAN appendix A:
A.1 per-displacement accuracy A(m~), A.2 per-plane error eps_k, A.3 fundamental-first constrained RRR (FF-r),
A.4 unrolled training, A.5 token / attention L2 editors, A.6 discriminability scoring, A.7 world cluster bootstrap."""
import itertools
import random
from functools import lru_cache
import torch
import torch.nn as nn
import torch.nn.functional as Fn
from symutil import *
import sym4_semantics as S
import sym4_evaluator as Ev

V2DIR = EXP / 'composability_mechanisms_v1'            # the v2 experiment
V3DIR = EXP / 'composability_mechanisms_v2'            # the v3 experiment
BB_NAME = {'bart': 'bart', 't5': 't5gemma'}
V_DOMAINS = ['weekday', 'month', 'hour', 'compass8', 'season']
R_DOMAINS = ['weekday', 'month', 'hour', 'compass8']
U_DOMAINS = ['weekday', 'month', 'compass']
X_DOMAINS = ['bind3', 'bind3fix', 'name3']
S_DOMAINS = ['weekday', 'month']
T5_OLD = ['weekday', 'month', 'compass']                # T5Gemma train/dev caches from v3
CONFIRM = 'confirm4'
SHARD = 16
SHARDS = ROOT / 'results/shards'   # module attribute (patched only by the pre-lock smoke test)
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'


# ---------------------------------------------------------------- backbones
def engine4(bb):
    require_slurm(); source_path()
    from backend import Backend
    return Backend(BB_NAME[bb])


def mdtype(eng):
    return next(eng.model.parameters()).dtype


def dec(eng, h, m):
    return eng.decode(h.to(mdtype(eng)), m)


# ---------------------------------------------------------------- worlds, caches, slots
def tmpl(d):
    return 3 if d in S.S1B else 0


def wfile(d, split):
    if split == 'confirm3':
        return V3DIR / f'data/{d}/worlds.jsonl'
    if d in V1_DOMAINS and split in ('train', 'dev'):
        return V1 / f'data/{d}/worlds.jsonl'
    return ROOT / f'data/{d}/worlds.jsonl'


@lru_cache(None)
def _worlds(d, split):
    return tuple(w for w in rows(wfile(d, split)) if w['split'] == split)


def worlds4(d, split):
    return list(_worlds(d, split))


def cpath(bb, d, split, s):
    if split == 'confirm3':
        return V3DIR / f'local/{bb}_{d}_confirm3_t{tmpl(d)}_s{s}.pt'
    if bb == 'bart' and d in V1_DOMAINS and split in ('train', 'dev'):
        return V1 / f'local/e1_{d}_{split}_t0_s{s}.pt'
    if bb == 't5' and d in T5_OLD and split in ('train', 'dev'):
        return V3DIR / f'local/t5_{d}_{split}_t0_s{s}.pt'
    return ROOT / f'local/{bb}_{d}_{split}_t{tmpl(d)}_s{s}.pt'


@lru_cache(None)
def cache4(bb, d, split, s):
    return load(cpath(bb, d, split, s))


def slots(bb, d, split):
    """Long tensor (W,) of attribute-slot positions (template 0: constant; template 3: per world)."""
    f = V3DIR / 'data/slot_positions.json' if split == 'confirm3' else ROOT / 'data/slot_positions.json'
    tab = read(f)[bb]
    if d not in tab:   # v1 domains outside v4 (egoside, daysago): template-0 constant positions from v3's audit
        assert split in ('train', 'dev') and tmpl(d) == 0; tab = read(V3DIR / 'data/slot_positions.json')[bb]
    sp = tab[d]; ws = worlds4(d, split)
    return torch.tensor([sp['all'] if 'all' in sp else sp['per_world'][w['world_id']] for w in ws])


def slot_matrix(bb, d, split):
    """(W, N, dim) float64 canonical slot vectors c_w(x), states in natural order."""
    pos = slots(bb, d, split); ar = torch.arange(len(pos))
    return torch.stack([cache4(bb, d, split, s)['h'][ar, pos].double() for s in S.states(d)], 1)


def lock_ok():
    p = ROOT / 'protocol.json'
    return p.exists() and read(p).get('locked') is True


@torch.no_grad()
def encode_split4(eng, bb, d, split, bs=32):
    if split == CONFIRM:
        assert lock_ok(), 'confirm4 encodings only after the lock'
    ws = worlds4(d, split); ids = [w['world_id'] for w in ws]; t = tmpl(d)
    for s in S.states(d):
        f = cpath(bb, d, split, s)
        assert str(f).startswith(str(ROOT)), f'refusing to write outside this experiment: {f}'
        if f.exists() and load(f)['world_ids'] == ids: continue
        hs = []; ms = []
        for i in range(0, len(ws), bs):
            h, m = eng.encode([S.render(w, s, t) for w in ws[i:i + bs]]); hs.append(h.float().cpu()); ms.append(m.cpu())
        h = torch.cat(hs); m = torch.cat(ms); n = int(m.sum(1).max())
        assert int(m[:, n:].sum()) == 0, 'right padding expected'
        save(f, dict(h=h[:, :n].contiguous(), m=m[:, :n].contiguous(), world_ids=ids))


# ---------------------------------------------------------------- harmonic planes (v3 A.1)
def gram_planes(cbar):
    """cbar (N, dim) float64 (rows in cycle order) -> list of (k, B_k dim x {1,2}) orthonormal across all planes (k ascending)."""
    N = cbar.shape[0]; x = torch.arange(N, dtype=torch.float64); basis = []; out = []
    for k in range(1, N // 2 + 1):
        vecs = [(torch.cos(2 * np.pi * k * x / N)[:, None] * cbar).sum(0), (torch.sin(2 * np.pi * k * x / N)[:, None] * cbar).sum(0)]
        Bk = []
        for v in vecs:
            for b in basis + Bk: v = v - (v @ b) * b
            if v.norm() > 1e-8 * cbar.norm(): Bk.append(v / v.norm())
        basis += Bk
        if Bk: out.append((k, torch.stack(Bk, 1)))
    return out


def cbar_of(X):
    return (X - X.mean(1, keepdim=True)).mean(0)


def cycle_order(d, mp='natural'):
    """States listed along the plus cycle of map mp (natural: 0..N-1)."""
    st = S.states(d); out = [st[0]]
    while len(out) < len(st): out.append(S.advance(d, out[-1], 'plus', mp))
    return out


@lru_cache(None)
def planes(bb, d, mp='natural'):
    """Harmonic planes from train c-bar. weekday/month/compass natural: the v3 plane files (identical procedure and data)."""
    f = V3DIR / f'local/planes_{bb}_{d}.pt'
    if mp == 'natural' and f.exists(): return load(f)
    order = cycle_order(d, mp)
    return gram_planes(cbar_of(slot_matrix(bb, d, 'train'))[order])


def amplitudes(bb, d):
    X = slot_matrix(bb, d, 'train'); cb = cbar_of(X); out = {}
    nxt = [S.advance(d, s, 'plus') for s in S.states(d)]
    for k, B in planes(bb, d):
        out[k] = dict(dim=B.shape[1], a=float(((cb @ B).square().sum(1).mean()).sqrt()),
                      s=float(((X[:, nxt] - X) @ B).norm(dim=-1).mean()))
    return out


# ---------------------------------------------------------------- vote model (v3 A.2)
def plane_dists(H, Cw, P):
    diff = H[:, None, :] - Cw
    return torch.stack([(diff @ B).square().sum(-1) for _, B in P], -1)


def vote_scores(D, lam):
    return -(D * lam).sum(-1)


def fit_vote(D, y, mode, lam0, restarts=5, seed=BOOT_SEED):
    K = D.shape[-1]; g = torch.Generator().manual_seed(seed); best = None
    D = D.double(); y = torch.as_tensor(y)
    for r in range(restarts):
        jitter = torch.exp(0.5 * torch.randn(K, generator=g, dtype=torch.float64)) if r else torch.ones(K, dtype=torch.float64)
        init = lam0 * jitter
        if mode == 'equal': init = init.mean().reshape(1)
        if mode == 'fund': init = init[:1]
        th = torch.log(torch.expm1(init.clamp_min(1e-12))).clone().requires_grad_(True)
        def lam_of(t):
            l = Fn.softplus(t)
            if mode == 'equal': return l.expand(K)
            if mode == 'fund': return torch.cat([l, torch.zeros(K - 1, dtype=l.dtype)])
            return l
        opt = torch.optim.LBFGS([th], max_iter=500, line_search_fn='strong_wolfe', tolerance_grad=1e-10, tolerance_change=1e-12)
        def closure():
            opt.zero_grad(); loss = Fn.cross_entropy(vote_scores(D, lam_of(th)), y); loss.backward(); return loss
        opt.step(closure)
        with torch.no_grad():
            nll = float(Fn.cross_entropy(vote_scores(D, lam_of(th)), y)); lam = lam_of(th).detach().clone()
        if best is None or nll < best[1]: best = (lam, nll)
    return best


def omega(lam, Ed):
    v = lam * Ed; return (v / v.sum()).tolist()


# ---------------------------------------------------------------- idealized chains
def path_ops(N, kind):
    return ['plus'] * (2 * N) if kind == 'plus' else ['minus'] * (2 * N) if kind == 'minus' else ['plus', 'minus'] * N


def ideal_R(Cw, P, lam, frozen, d):
    """R-hat over worlds x all starts for plus / minus / alt (2N steps); frozen planes keep the start's coordinates."""
    N = Cw.shape[1]; out = {}
    Z = [Cw @ B for _, B in P]
    fr = [k in frozen for k, _ in P]
    for kind in ('plus', 'minus', 'alt'):
        ok_all = []
        for x0 in range(N):
            g = []; s = x0
            for op in path_ops(N, kind): s = S.advance(d, s, op); g.append(s)
            Dm = torch.stack([((Zk[:, [x0] * len(g)] if f else Zk[:, g])[:, :, None, :] - Zk[:, None]).square().sum(-1) for Zk, f in zip(Z, fr)], -1)
            yhat = vote_scores(Dm, lam).argmax(-1)
            ok_all.append((yhat == torch.tensor(g)).all(1))
        out[kind] = float(torch.cat(ok_all).double().mean())
    return out


def ideal_At(Cw, P, lam, frozen, d, kind='plus'):
    """Idealized per-step accuracy A_t (t = 1..2N), averaged over worlds x starts (for prediction curves)."""
    N = Cw.shape[1]; Z = [Cw @ B for _, B in P]; fr = [k in frozen for k, _ in P]; acc = []
    for x0 in range(N):
        g = []; s = x0
        for op in path_ops(N, kind): s = S.advance(d, s, op); g.append(s)
        Dm = torch.stack([((Zk[:, [x0] * len(g)] if f else Zk[:, g])[:, :, None, :] - Zk[:, None]).square().sum(-1) for Zk, f in zip(Z, fr)], -1)
        acc.append((vote_scores(Dm, lam).argmax(-1) == torch.tensor(g)).double())
    return torch.cat(acc).mean(0).tolist()


def category(r):
    return 'composable' if r >= .90 else 'fail' if r <= .20 else 'partial'


# ---------------------------------------------------------------- operators
class RRRop:
    def __init__(self, f):
        self.left, self.right, self.bias = (f[k].float().to(DEV) for k in ('left', 'right', 'bias'))
    def __call__(self, h, m):
        return h + (h.float() @ self.left @ self.right + self.bias) * m[..., None]


def bvec(P, ks):
    Bs = [B for k, B in P if k in ks]
    return torch.cat(Bs, 1).float().to(DEV) if Bs else None


class Freeze:
    """F_S: h' = T(h); on the slot, remove the update inside planes S (cross terms kept)."""
    def __init__(self, T, Bs, pos):
        self.T, self.Bs, self.pos = T, Bs, pos.to(DEV)
    def __call__(self, h, m):
        h1 = self.T(h, m)
        if self.Bs is None: return h1
        ar = torch.arange(len(h), device=h.device); h1 = h1.clone(); hs1 = h1[ar, self.pos]; hs0 = h[ar, self.pos]
        h1[ar, self.pos] = hs1 - ((hs1 - hs0) @ self.Bs) @ self.Bs.T
        return h1


def fit_plane_editor(X, B, d, op):
    src = list(range(X.shape[1])); dst = [S.advance(d, s, op) for s in S.states(d)]
    Z = (X[:, src] @ B).reshape(-1, B.shape[1]); Zp = (X[:, dst] @ B).reshape(-1, B.shape[1])
    Za = torch.cat([Z, torch.ones(len(Z), 1, dtype=Z.dtype)], 1); sol = torch.linalg.lstsq(Za, Zp).solution
    return sol[:-1].T.contiguous(), sol[-1]


class PlaneEd:
    def __init__(self, A, c, B, pos):
        self.A, self.c, self.B, self.pos = A.float().to(DEV), c.float().to(DEV), B.float().to(DEV), pos.to(DEV)
    def __call__(self, h, m):
        ar = torch.arange(len(h), device=h.device); h1 = h.clone(); hs = h1[ar, self.pos].float(); z = hs @ self.B
        h1[ar, self.pos] = hs + (z @ self.A.T + self.c - z) @ self.B.T
        return h1


# ---------------------------------------------------------------- chains
def files(kind, bb, d, mp, method, tag, n):
    import lib4
    return [lib4.SHARDS / f'{kind}_{bb}_{d}_{mp}_{method}_{tag}_{lo:03d}.jsonl' for lo in range(0, n, SHARD)]


def write_shards(fs, recs):
    for j, f in enumerate(fs):
        write(f, [r for r in recs if j * SHARD <= r['index'] < (j + 1) * SHARD])


@torch.no_grad()
def run_chain(eng, bb, d, mp, method, ops, name, start, oplist, split=CONFIRM, model=None, decode=True):
    """ops: {'plus','minus'} -> callable, or None for reencode. start: 'world_start' or a state.
    model: optional dict(P=planes, lams={name: lam}) to record vote-model argmax on the actual latent slot."""
    if split == CONFIRM: assert lock_ok(), 'confirm4 decoding only after the lock'
    ws = worlds4(d, split); n = len(ws); fs = files('chain', bb, d, mp, method, name, n)
    if all(f.exists() for f in fs): return
    C = {s: cache4(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); idx = torch.arange(n)
    state = [w['start_state'] for w in ws] if start == 'world_start' else [start] * n; s0 = list(state)
    stack = lambda st: (torch.stack([C[s]['h'][i] for i, s in enumerate(st)]).cuda(), torch.stack([C[s]['m'][i] for i, s in enumerate(st)]).cuda())
    h, m = stack(state); ok = [True] * n; recs = []
    if model is not None:
        pos = slots(bb, d, split).cuda(); Cw = slot_matrix(bb, d, split).cuda()
    for step, op in enumerate(oplist, 1):
        state = [S.advance(d, s, op, mp) for s in state]; ref, _ = stack(state)
        h = ref.clone() if ops is None else ops[op](h, m)
        out = dec(eng, h, m); am = {}
        if model is not None:
            Dm = plane_dists(h[idx.cuda(), pos].double(), Cw, [(k, B.cuda()) for k, B in model['P']])
            am = {f'argmax_{k}': vote_scores(Dm, lam.cuda()).argmax(-1).tolist() for k, lam in model['lams'].items()}
        for j, w in enumerate(ws):
            sc = Ev.score(out[j]['text'], S.gold(w, state[j], t), w, out[j]['ended']); ok[j] = ok[j] and sc['success']
            ps, pw = Ev.parse_state(out[j]['text'], d, S.people(w) if d in S.S1B else None)
            recs.append(dict(index=j, backbone=bb, domain=d, map=mp, method=method, path=name, world_id=w['world_id'], step=step, operation=op,
                             start=s0[j], state=state[j], success=sc['success'], target=sc['target'], preserved=sc['preserved'],
                             trajectory_success=ok[j], decoded_state=ps, decoded_word=pw, text=out[j]['text'],
                             **{k: v[j] for k, v in am.items()}))
    write_shards(fs, recs)


@torch.no_grad()
def run_singles(eng, bb, d, mp, method, ops, split=CONFIRM):
    if split == CONFIRM: assert lock_ok()
    ws = worlds4(d, split); n = len(ws); C = {s: cache4(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
    for s in S.states(d):
        for op in ('plus', 'minus'):
            try: y = S.advance(d, s, op, mp)
            except ValueError: continue
            fs = files('single', bb, d, mp, method, f's{s}_{op}', n)
            if all(f.exists() for f in fs): continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); h = C[y]['h'].cuda() if ops is None else ops[op](h, m); out = dec(eng, h, m)
            write_shards(fs, [dict(index=j, backbone=bb, domain=d, map=mp, method=method, world_id=w['world_id'], source_state=s, operation=op, target_state=y,
                                   text=out[j]['text'], score=Ev.score(out[j]['text'], S.gold(w, y, t), w, out[j]['ended'])) for j, w in enumerate(ws)])


@torch.no_grad()
def dev_single(eng, bb, d, mp, ops, split='dev', op_only=None):
    ws = worlds4(d, split); C = {s: cache4(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); ok = []
    for s in S.states(d):
        for op in ('plus', 'minus'):
            if op_only and op != op_only: continue
            try: y = S.advance(d, s, op, mp)
            except ValueError: continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); h = C[y]['h'].cuda() if ops is None else ops[op](h, m)
            ok += [Ev.score(o['text'], S.gold(w, y, t), w, o['ended'])['success'] for o, w in zip(dec(eng, h, m), ws)]
    return rate(ok)


@torch.no_grad()
def dev_chain(eng, bb, d, mp, ops, oplist, split='dev', start='world_start'):
    """In-memory trajectory success R_k (k = 1..len) on a non-confirm split (no shards)."""
    assert split != CONFIRM
    ws = worlds4(d, split); n = len(ws); C = {s: cache4(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
    state = [w['start_state'] for w in ws] if start == 'world_start' else [start] * n
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).cuda(); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).cuda()
    ok = [True] * n; R = []
    for op in oplist:
        state = [S.advance(d, s, op, mp) for s in state]; h = ops[op](h, m); out = dec(eng, h, m)
        for j, w in enumerate(ws): ok[j] = ok[j] and Ev.score(out[j]['text'], S.gold(w, state[j], t), w, out[j]['ended'])['success']
        R.append(rate(ok))
    return R


@torch.no_grad()
def reencode_rate(eng, bb, d, splits=('train', 'dev')):
    ok = []
    for split in splits:
        ws = worlds4(d, split); t = tmpl(d)
        for s in S.states(d):
            c = cache4(bb, d, split, s)
            ok += [Ev.score(o['text'], S.gold(w, s, t), w, o['ended'])['success'] for o, w in zip(dec(eng, c['h'].cuda(), c['m'].cuda()), ws)]
    return rate(ok)


# ---------------------------------------------------------------- RRR fitting (v1-v3 procedure) and FF-r (A.3)
def _F():
    if str(CWR) not in sys.path: sys.path.insert(0, str(CWR))
    import fit as F
    return F


def paired_tokens(bb, d, mp, op, idx, split='train'):
    ws = worlds4(d, split); C = {s: cache4(bb, d, split, s) for s in S.states(d)}; X = []; Y = []
    for s in S.states(d):
        try: y = S.advance(d, s, op, mp)
        except ValueError: continue
        a, b = C[s], C[y]; assert torch.equal(a['m'][idx], b['m'][idx]); v = a['m'][idx].bool()
        X.append(a['h'][idx][v]); Y.append((b['h'][idx] - a['h'][idx])[v])
    return torch.cat(X).double(), torch.cat(Y).double()


def solve_ff(st, rel, ranks, Q1):
    """FF-r (A.3) in the whitened form of the v2/v3 RRR solver (fit.solve): A = (C + lam I)^(-1/2) cross; ordinary RRR-r keeps the top-r
    right singular vectors V_r of A (B_r = B-hat V_r V_r^T); FF-r keeps orth([Q1, top r-2 right singular vectors of A (I - Q1 Q1^T)]).
    B-hat = (C + lam I)^(-1) cross. Bias as fit.solve: my - mx B."""
    c = st['cov']; lam = rel * float(c.trace() / len(c)); vals, vecs = torch.linalg.eigh(c + lam * torch.eye(len(c), dtype=torch.float64))
    assert vals.min() > 0
    invsqrt = (vecs * vals.rsqrt()) @ vecs.T; A = invsqrt @ st['cross']; Bhat = invsqrt @ A
    Q1 = Q1.double(); Aperp = A - (A @ Q1) @ Q1.T; _, _, vh = torch.linalg.svd(Aperp, full_matrices=False); out = {}
    for r in ranks:
        Q, _ = torch.linalg.qr(torch.cat([Q1, vh[:r - 2].T], 1)); left = Bhat @ Q; right = Q.T; bias = st['my'] - st['mx'] @ left @ right
        out[r] = dict(left=left.float(), right=right.float(), bias=bias.float(), rank=r, relative_ridge=rel, ridge=lam, method='FF')
    return out


def fit_rrr4(bb, d, mp, ranks, ff=False, Q1=None, ridge_grid=(1e-4, 1e-3, 1e-2, 1e-1), inner_seed=BOOT_SEED, inner_fit=80):
    """v3 fit_rrr3 procedure (ridge per rank chosen on an inner split of train worlds, refit on all train). ff=True: FF-r (A.3)."""
    F = _F(); ws = worlds4(d, 'train')
    order = list(range(len(ws))); random.Random(inner_seed).shuffle(order); fi, vi = sorted(order[:inner_fit]), sorted(order[inner_fit:])
    solve = (lambda st, rel, rs: solve_ff(st, rel, rs, Q1)) if ff else F.solve
    final = {}; info = {}
    for op in ('plus', 'minus'):
        A = paired_tokens(bb, d, mp, op, fi); Bv = paired_tokens(bb, d, mp, op, vi); st = F.sufficient(*A); sc = {}
        for rel in ridge_grid:
            for r, f in solve(st, rel, ranks).items(): sc[rel, r] = F.mse(*Bv, f)
        chosen = {r: min(ridge_grid, key=lambda rel: sc[rel, r]) for r in ranks}
        AL = paired_tokens(bb, d, mp, op, list(range(len(ws)))); sa = F.sufficient(*AL); sols = {rel: solve(sa, rel, ranks) for rel in set(chosen.values())}
        for r, rel in chosen.items():
            f = sols[rel][r]; final[op, r] = {k: f[k] for k in ('left', 'right', 'bias')} | dict(relative_ridge=rel, rank=r)
            info[f'{op}_{r}'] = rel
    return final, info


# ---------------------------------------------------------------- A.2 per-plane error
def rot_part(A):
    return complex(float(A[0, 0] + A[1, 1]) / 2, float(A[1, 0] - A[0, 1]) / 2)


def ideal_from_cbar(cb, P, op='plus'):
    """cb (N, dim) rows in cycle order. Per plane k: least squares z_{x+-1} = A* z_x in plane coordinates (A* acting on column vectors)."""
    N = cb.shape[0]; nxt = [(i + (1 if op == 'plus' else -1)) % N for i in range(N)]; out = {}
    for k, B in P:
        Z = cb @ B.double(); out[k] = torch.linalg.lstsq(Z, Z[nxt]).solution.T
    return out


def ideal_maps(bb, d, mp='natural', op='plus'):
    """Per plane k: the ideal map fitted from train c-bar (A.2 step 2), in the cycle order of map mp."""
    return ideal_from_cbar(cbar_of(slot_matrix(bb, d, 'train'))[cycle_order(d, mp)], planes(bb, d, mp), op)


def eps_from(Ak, Astar, N):
    """A.2: per-plane (rho_k, delta_k, eps_k) from the restricted operator Ak and the ideal map Astar."""
    if Ak.shape[0] == 2:
        r, rs = rot_part(Ak), rot_part(Astar); rho = abs(r) / abs(rs); delta = (np.angle(r) - np.angle(rs) + np.pi) % (2 * np.pi) - np.pi
    else:
        q = float(Ak[0, 0]) / float(Astar[0, 0]); rho = abs(q); delta = 0.0 if q > 0 else np.pi
    eps = max(abs(rho ** t * np.exp(1j * t * delta) - 1) for t in range(1, 2 * N + 1))
    return dict(rho=float(rho), delta=float(delta), eps=float(eps))


def plane_errors(U, V, P, ideal, N):
    """Column-convention linear part L = I + U V (U d x r, V r x d) restricted to each plane: A_k = I + (B_k^T U)(V B_k)."""
    out = {}
    for k, B in P:
        B = B.double(); Ak = torch.eye(B.shape[1], dtype=torch.float64) + (B.T @ U.double()) @ (V.double() @ B)
        out[k] = eps_from(Ak, ideal[k], N) | dict(dim=B.shape[1])
    return out


def op_plane_errors(kind, obj, op, bb, d, mp='natural'):
    """kind 'rrr' (fit dict) or 'editor' (state dict). Returns {k: dict(rho, delta, eps, dim)} for op (plus or minus)."""
    U, V, _ = editor_factors(kind, obj, op); N = len(S.states(d))
    return plane_errors(U, V, planes(bb, d, mp), ideal_maps(bb, d, mp, op), N)


# ---------------------------------------------------------------- editor training (v1 configuration, single step)
def token_mse(h, y, m):
    return ((h - y).square() * m[..., None]).sum((1, 2)) / (m.sum(1) * h.shape[-1])


def legal_step(d, s, op, mp):
    try: S.advance(d, s, op, mp); return True
    except ValueError: return False


def l2_scales(bb, d, mp, split='train'):
    ws = worlds4(d, split); C = {s: cache4(bb, d, split, s) for s in S.states(d)}; out = {}
    for op in ('plus', 'minus'):
        its = [(i, s) for s in S.states(d) for i in range(len(ws)) if legal_step(d, s, op, mp)]; v = []
        for lo in range(0, len(its), 64):
            part = its[lo:lo + 64]
            h = torch.stack([C[s]['h'][i] for i, s in part]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in part]).to(DEV)
            y = torch.stack([C[S.advance(d, s, op, mp)]['h'][i] for i, s in part]).to(DEV); v.append(token_mse(h, y, m))
        out[op] = float(torch.cat(v).mean())
    return out


def train_editor(eng, bb, d, mp, group, seed, updates=600, l2_weight=1.0, init_rrr=None, batch=8, micro=2, lr=1e-3, clip=1.0,
                 log_every=1, dev_every=None, dev_fn=None):
    """v3 train_editor. group: C1 (CE), C3 (CE + l2_weight * normalised L2), L2 (normalised L2 only; CE still logged every log_every)."""
    source_path(); from backend import editors
    ws = worlds4(d, 'train'); C = {s: cache4(bb, d, 'train', s) for s in S.states(d)}; t = tmpl(d); dt = mdtype(eng)
    pool = {op: [(i, s) for s in S.states(d) for i in range(len(ws)) if legal_step(d, s, op, mp)] for op in ('plus', 'minus')}
    stack = lambda its: (torch.stack([C[s]['h'][i] for i, s in its]).cuda(), torch.stack([C[s]['m'][i] for i, s in its]).cuda())
    with torch.no_grad(): scale = l2_scales(bb, d, mp)
    ed = editors(eng.d, seed)
    if init_rrr is not None:
        with torch.no_grad():
            for op in ('plus', 'minus'):
                f = init_rrr[op]; b = f['left'].double() @ f['right'].double(); u, s_, vh = torch.linalg.svd(b, full_matrices=False)
                ed[op].v.weight.copy_((u[:, :16] * s_[:16].sqrt()).T.float()); ed[op].u.weight.copy_((s_[:16].sqrt()[:, None] * vh[:16]).T.float()); ed[op].b.copy_(f['bias'])
    opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []
    for k in range(updates):
        op = ('plus', 'minus')[k % 2]; bt = [rng.choice(pool[op]) for _ in range(batch)]; opt.zero_grad(set_to_none=True); tot = dict(ce=0., l2=0., loss=0.)
        logk = (k + 1) % log_every == 0 or k == 0
        for lo in range(0, batch, micro):
            part = bt[lo:lo + micro]; h, m = stack(part); tgt = [(i, S.advance(d, s, op, mp)) for i, s in part]; y, ym = stack(tgt); assert torch.equal(m, ym)
            e = ed[op](h, m)
            if group == 'L2' and not logk: ce = torch.zeros((), device='cuda')
            elif group == 'L2':
                with torch.no_grad(): ce = eng.ce(e.to(dt), m, [S.render(ws[i], s, t) for i, s in tgt])[0].mean()
            else: ce = eng.ce(e.to(dt), m, [S.render(ws[i], s, t) for i, s in tgt])[0].mean()
            l2 = token_mse(e, y, m).mean() / scale[op] if group in ('C3', 'L2') else torch.zeros((), device='cuda')
            loss = (l2 if group == 'L2' else ce + l2_weight * l2); assert torch.isfinite(loss); (loss * len(part) / batch).backward()
            for kk, v in (('ce', ce), ('l2', l2), ('loss', loss)): tot[kk] += float(v.detach()) * len(part) / batch
        gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); assert torch.isfinite(gn)
        assert all(x.grad is None for x in eng.model.parameters()); opt.step()
        if logk:
            rec = dict(step=k + 1, op=op, grad=float(gn), **tot)
            if dev_every and dev_fn and (k + 1) % dev_every == 0: rec['dev_l2'] = dev_fn(ed)
            hist.append(rec)
    ed.eval().requires_grad_(False)
    return ed, hist, scale


@torch.no_grad()
def dev_l2(ed, bb, d, mp, scale, split='dev'):
    """Mean normalised token L2 of single steps on a split (plus and minus averaged)."""
    ws = worlds4(d, split); C = {s: cache4(bb, d, split, s) for s in S.states(d)}; out = {}
    for op in ('plus', 'minus'):
        v = []
        for s in S.states(d):
            if not legal_step(d, s, op, mp): continue
            y = S.advance(d, s, op, mp); h, m = C[s]['h'].to(DEV), C[s]['m'].to(DEV)
            v.append(token_mse(ed[op](h, m), C[y]['h'].to(DEV), m) / scale[op])
        out[op] = float(torch.cat(v).mean())
    return (out['plus'] + out['minus']) / 2


def load_editor(eng, path):
    source_path(); from backend import editors
    c = load(path); ed = editors(eng.d, c.get('seed', 42)); ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)


# ---------------------------------------------------------------- A.4 unrolled training
def path_seq(kind, S_):
    return ['plus'] * S_ if kind == 'plus' else ['minus'] * S_ if kind == 'minus' else [('plus', 'minus')[i % 2] for i in range(S_)]


def unrolled_loss(ed, ce_fn, l2_fn, h0, m, ops_seq, texts_seq, targets_seq=None, l2_weight=0.0):
    """(1/S) sum_s CE(decoder(h_s), text(x_s)) [+ l2_weight (1/S) sum_s L2(h_s, E(x_s))]; gradient through the whole chain."""
    h = h0; ce = 0.; l2 = 0.; S_ = len(ops_seq)
    for s, op in enumerate(ops_seq):
        h = ed[op](h, m); ce = ce + ce_fn(h, m, texts_seq[s])
        if l2_weight: l2 = l2 + l2_fn(h, targets_seq[s], m, op)
    ce = ce / S_; l2 = l2 / S_ if l2_weight else torch.zeros((), device=h0.device)
    return ce + l2_weight * l2, ce, l2


def train_unrolled(eng, bb, d, seed, Sset, updates=1200, l2_weight=0.0, batch=8, micro=2, lr=1e-3, clip=1.0, mp='natural'):
    """A.4: per update draw path kind uniformly from plus^S / minus^S / alternating and S uniformly from Sset; batch of 8 (world, start)
    from train; plus and minus editors trained jointly; frozen encoder/decoder."""
    source_path(); from backend import editors
    ws = worlds4(d, 'train'); C = {s: cache4(bb, d, 'train', s) for s in S.states(d)}; t = tmpl(d); dt = mdtype(eng)
    pool = [(i, s) for s in S.states(d) for i in range(len(ws))]
    stack = lambda its: (torch.stack([C[s]['h'][i] for i, s in its]).cuda(), torch.stack([C[s]['m'][i] for i, s in its]).cuda())
    with torch.no_grad(): scale = l2_scales(bb, d, mp)
    ce_fn = lambda h, m, texts: eng.ce(h.to(dt), m, texts)[0].mean()
    l2_fn = lambda h, y, m, op: token_mse(h, y, m).mean() / scale[op]
    ed = editors(eng.d, seed); opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []
    for k in range(updates):
        kind = rng.choice(('plus', 'minus', 'alt')); S_ = rng.choice(list(Sset)); ops_seq = path_seq(kind, S_)
        bt = [rng.choice(pool) for _ in range(batch)]; opt.zero_grad(set_to_none=True); tot = dict(ce=0., l2=0., loss=0.)
        for lo in range(0, batch, micro):
            part = bt[lo:lo + micro]; h, m = stack(part); states = [s for _, s in part]; texts = []; tg = []
            for op in ops_seq:
                states = [S.advance(d, s, op, mp) for s in states]; texts.append([S.render(ws[i], s, t) for (i, _), s in zip(part, states)])
                if l2_weight: y, _ = stack([(i, s) for (i, _), s in zip(part, states)]); tg.append(y)
            loss, ce, l2 = unrolled_loss(ed, ce_fn, l2_fn, h, m, ops_seq, texts, tg, l2_weight)
            assert torch.isfinite(loss); (loss * len(part) / batch).backward()
            for kk, v in (('ce', ce), ('l2', l2), ('loss', loss)): tot[kk] += float(v.detach()) * len(part) / batch
        gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); assert torch.isfinite(gn)
        assert all(x.grad is None for x in eng.model.parameters()); opt.step()
        hist.append(dict(step=k + 1, kind=kind, S=S_, grad=float(gn), **tot))
    ed.eval().requires_grad_(False)
    return ed, hist, scale


# ---------------------------------------------------------------- A.5 token / attention L2 editors
class TokAttEditor(nn.Module):
    """Tok-L2: delta_i = b + U V h_i (rank 32). Att-L2 adds W_o sum_j alpha_ij W_v h_j, alpha = softmax_j((W_q h_i)^T (W_k h_j) / sqrt(64))
    over non-pad j of the same sentence; W_o zero-initialised (training starts as Tok-L2)."""
    def __init__(self, d, rank=32, att=False, dk=64):
        super().__init__(); self.att = att; self.dk = dk
        self.b = nn.Parameter(torch.zeros(d)); self.v = nn.Linear(d, rank, bias=False); self.u = nn.Linear(rank, d, bias=False)
        nn.init.normal_(self.v.weight, std=.01); nn.init.zeros_(self.u.weight)
        if att:
            self.q = nn.Linear(d, dk, bias=False); self.k = nn.Linear(d, dk, bias=False); self.wv = nn.Linear(d, dk, bias=False); self.o = nn.Linear(dk, d, bias=False)
            nn.init.zeros_(self.o.weight)

    def attention(self, z, m):
        sc = (self.q(z) @ self.k(z).transpose(1, 2)) / np.sqrt(self.dk)
        sc = sc.masked_fill(~m.bool()[:, None, :], float('-inf'))
        return torch.softmax(sc, -1)

    def forward(self, h, m):
        z = h.float(); delta = self.b + self.u(self.v(z))
        if self.att: delta = delta + self.o(self.attention(z, m) @ self.wv(z))
        return (z + delta * m[..., None]).to(h.dtype)


def tokatt_pair(d, seed, att, rank=32):
    torch.manual_seed(seed)
    return nn.ModuleDict({op: TokAttEditor(d, rank, att) for op in ('plus', 'minus')}).to(DEV).float()


def rel_l2(e, y, x, m):
    """A.5 relative L2: mean_i ||h_i + delta_i - E(target)_i||^2 / mean_i ||E(target)_i - E(source)_i||^2 over non-pad positions."""
    v = m[..., None].float()
    return ((e - y).square() * v).sum() / ((y - x).square() * v).sum()


def train_l2_editor(bb, d, op, seed, att, updates=4000, batch=16, lr=1e-3, clip=1.0, mp='natural', H=None):
    """A.5: train one operator (plus or minus) of a Tok-L2 / Att-L2 editor on train canonical pairs. H: optional {s: (h, m)} override (selftest)."""
    if H is None:
        ws = worlds4(d, 'train'); H = {s: (cache4(bb, d, 'train', s)['h'], cache4(bb, d, 'train', s)['m']) for s in S.states(d)}
    W = len(next(iter(H.values()))[0]); pool = [(i, s) for s in H for i in range(W)]
    dim = next(iter(H.values()))[0].shape[-1]; ed = tokatt_pair(dim, seed, att); opt = torch.optim.AdamW(ed[op].parameters(), lr=lr, weight_decay=0)
    rng = random.Random(seed); hist = []
    for k in range(updates):
        bt = [rng.choice(pool) for _ in range(batch)]; tg = [(i, S.advance(d, s, op, mp) if d else (s + 1) % len(H)) for i, s in bt]
        x = torch.stack([H[s][0][i] for i, s in bt]).to(DEV).float(); m = torch.stack([H[s][1][i] for i, s in bt]).to(DEV)
        y = torch.stack([H[s][0][i] for i, s in tg]).to(DEV).float(); assert torch.equal(m, torch.stack([H[s][1][i] for i, s in tg]).to(DEV))
        opt.zero_grad(set_to_none=True); loss = rel_l2(ed[op](x, m), y, x, m); assert torch.isfinite(loss); loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(ed[op].parameters(), clip); opt.step()
        if (k + 1) % 50 == 0 or k == 0: hist.append(dict(step=k + 1, loss=float(loss), grad=float(gn)))
    ed.eval().requires_grad_(False)
    return ed, hist


# ---------------------------------------------------------------- A.1 A(m~), A.6 discriminability, A.7 cluster bootstrap
def disp_fold(g, x0, N):
    m_ = (g - x0) % N; return min(m_, N - m_)


def A_by_disp(recs, N, order=None):
    """recs: chain records of one (method, path) over 2N steps. A_t = fraction of worlds correct at step t (non-cumulative);
    A(m~) = mean of A_t over t in [1, 2N] with folded displacement m~ (positions along `order`, default natural)."""
    pos = (lambda x: order.index(x)) if order else (lambda x: x)
    by_t = {}
    for r in recs:
        if r['step'] <= 2 * N: by_t.setdefault(r['step'], []).append(r)
    out = {}
    for t, rs in by_t.items():
        At = float(np.mean([r['success'] for r in rs])); ms = {disp_fold(pos(r['state']), pos(r['start']), N) for r in rs}
        # displacement is identical for all worlds on a fixed path from each world's own start (one-way: t mod N; alt: 1 or 0)
        assert len(ms) == 1, ms
        out.setdefault(ms.pop(), []).append(At)
    return {m: float(np.mean(v)) for m, v in sorted(out.items())}


def disc_score(pred_H, pred_H2, observed, min_cells):
    """A.6: cells where the two hypotheses predict differently; H beats H2 if |C| >= min_cells, match_H >= 0.75, match_H2 <= 0.50."""
    C = [c for c in pred_H if pred_H[c] != pred_H2[c]]
    if len(C) < min_cells: return dict(cells=C, n=len(C), verdict='not evaluable')
    obs = [c for c in C if observed.get(c) is not None]
    mh = float(np.mean([observed[c] == pred_H[c] for c in obs])) if obs else None; mh2 = float(np.mean([observed[c] == pred_H2[c] for c in obs])) if obs else None
    v = 'H wins' if mh is not None and mh >= .75 and mh2 <= .50 else 'H2 wins' if mh2 is not None and mh2 >= .75 and mh <= .50 else 'no winner'
    return dict(cells=C, n=len(C), match_H=mh, match_H2=mh2, verdict=v)


def cluster_boot(world_ids, values, reps=BOOT_N, seed=BOOT_SEED):
    """A.7: resample worlds with replacement; values (n_records, k) columns; returns mean of each column and the
    per-replicate pooled means (reps, k). Pooled = all records of the drawn worlds (multiplicity counted)."""
    values = np.asarray(values, float); ids = sorted(set(world_ids)); ix = {w: i for i, w in enumerate(ids)}
    g = np.array([ix[w] for w in world_ids]); W = len(ids)
    sums = np.zeros((W, values.shape[1])); cnt = np.bincount(g, minlength=W).astype(float)
    np.add.at(sums, g, values)
    draw = np.random.default_rng(seed).integers(W, size=(reps, W))
    counts = np.stack([np.bincount(r, minlength=W) for r in draw]).astype(float)        # (reps, W)
    reps_mean = (counts @ sums) / (counts @ cnt)[:, None]
    return values.mean(0), reps_mean


def boot_diff_ci(world_ids, a, b, **kw):
    est, rm = cluster_boot(world_ids, np.stack([a, b], 1), **kw); d = rm[:, 0] - rm[:, 1]
    return dict(diff=float(est[0] - est[1]), ci95=np.quantile(d, [.025, .975]).tolist(), a=float(est[0]), b=float(est[1]))


# ---------------------------------------------------------------- unit block (v2), probe, write metrics (v3)
def unit_block(AQ, N, unit=0.9):
    ev, V = torch.linalg.eig(AQ.cpu())
    keep = ev.abs() >= unit; lam = ev[keep]; Vu = V[:, keep]; Vu = Vu / Vu.norm(dim=0, keepdim=True)
    sv = torch.linalg.svdvals(Vu) if Vu.shape[1] else torch.tensor([1.])
    ph = torch.rad2deg(torch.angle(lam)).numpy(); step = 360. / N
    j = np.round(ph / step).astype(int) % N; dev = np.abs(((ph - j * step) + 180) % 360 - 180)
    harm = sorted({int(min(a, N - a)) for a, dv in zip(j, dev) if dv < 2})
    return dict(n_unit=int(keep.sum()), kappa_u=float(sv.max() / sv.min()), max_phase_dev_deg=float(dev.max()) if len(dev) else None, harmonics_present=harm)


def harmonics_of(U, V, b, N):
    st, _, AQ = operator_stats(U.double().cpu(), V.double().cpu(), b.double().cpu())
    return dict(unit_block(AQ, N), DRIFT=st['DRIFT'], ISO=st['ISO'])


def logreg(X, y, C, K, iters=300):
    W = torch.zeros(X.shape[1], K, dtype=torch.float64, device=X.device, requires_grad=True); b = torch.zeros(K, dtype=torch.float64, device=X.device, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], max_iter=iters, line_search_fn='strong_wolfe', tolerance_grad=1e-9)
    def closure():
        opt.zero_grad(); loss = Fn.cross_entropy(X @ W + b, y) + (W ** 2).sum() / (2 * C * len(X)); loss.backward(); return loss
    opt.step(closure)
    return W.detach(), b.detach()


def probe(bb, d, CS=(0.01, 0.1, 1.0, 10.0)):
    with torch.enable_grad():
        def data(split):
            X = slot_matrix(bb, d, split); W, N, dim = X.shape
            return X.reshape(-1, dim).to(DEV), torch.arange(N).repeat(W).to(DEV), torch.arange(W).repeat_interleave(N)
        X, y, w = data('train'); mu, sd = X.mean(0), X.std(0).clamp_min(1e-6); Xs = (X - mu) / sd; folds = (w % 5).to(DEV); cv = {}; K = len(S.states(d))
        for C in CS:
            acc = []
            for f in range(5):
                tr = folds != f; Wt, bt = logreg(Xs[tr], y[tr], C, K); acc.append(float(((Xs[~tr] @ Wt + bt).argmax(1) == y[~tr]).float().mean()))
            cv[C] = float(np.mean(acc))
        Cb = max(CS, key=lambda c: (cv[c], -c)); Wt, bt = logreg(Xs, y, Cb, K)
        Xd, yd, _ = data('dev'); dev_acc = float((((Xd - mu) / sd @ Wt + bt).argmax(1) == yd).float().mean())
    st = S.states(d)
    return dict(C=Cb, cv_accuracy={str(k): v for k, v in cv.items()}, dev_accuracy=dev_acc), (lambda Z: [st[i] for i in (((Z.double().to(DEV) - mu) / sd) @ Wt + bt).argmax(1).tolist()])


def cosrows(a, b):
    return Fn.cosine_similarity(a.flatten(1).double(), b.flatten(1).double(), dim=1)


@torch.no_grad()
def write_metrics(eng, bb, d, mp, T, predict, split=CONFIRM, m4=True, T2=None):
    """M1-M3 (v2 definitions; M3 on the first-step state) and the transplant classes for a plus operator T under mapping mp.
    T2 (optional): the second-step probe readout on T2(T(h)) (U unit). M4 classes: relative / absolute / null / other / unparsable
    (PLAN 4 P5: five classes; v3's natural_successor class is folded into other and also reported separately)."""
    if split == CONFIRM: assert lock_ok()
    ws = worlds4(d, split); n = len(ws); st = S.states(d); t = tmpl(d); pos = slots(bb, d, split).to(DEV); ar = torch.arange(n, device=DEV)
    H = {s: cache4(bb, d, split, s)['h'].to(DEV) for s in st}; M = cache4(bb, d, split, st[0])['m'].to(DEV); v = M[..., None]
    legal = [s for s in st if legal_step(d, s, 'plus', mp)]; g = {s: S.advance(d, s, 'plus', mp) for s in legal}
    Wr = {s: (T(H[s], M) - H[s]) * v for s in legal}; Wc = {s: (H[g[s]] - H[s]) * v for s in legal}
    pc = torch.stack([cosrows(Wr[a], Wr[b]) for i, a in enumerate(legal) for b in legal[i + 1:]], 1).mean(1).cpu().numpy()
    cw = torch.stack([cosrows(Wr[s], Wc[s]) for s in legal], 1).mean(1).cpu().numpy()
    out = dict(M1=boot_mean(pc), M2=dict(median=float(np.median(cw)), ci95=boot_stat(lambda i: np.median(cw[i]), n)['ci95'], mean=float(cw.mean())))
    if predict is not None:
        src = tgt = oth = 0
        for s in legal:
            pr = predict((H[s] + Wr[s])[ar, pos]); src += sum(p == s for p in pr); tgt += sum(p == g[s] for p in pr); oth += sum(p not in (s, g[s]) for p in pr)
        tot = src + tgt + oth; out['M3'] = dict(source=src / tot, target=tgt / tot, other=oth / tot, n=tot)
    if T2 is not None and predict is not None:
        c = dict(source=0, step1=0, step2=0, other=0)
        for s in legal:
            s2 = g[s]
            if not legal_step(d, s2, 'plus', mp): continue
            h2 = T2(H[s] + Wr[s], M); pr = predict(h2[ar, pos]); g2 = S.advance(d, s2, 'plus', mp)
            for p in pr: c['step2' if p == g2 else 'step1' if p == s2 else 'source' if p == s else 'other'] += 1
        tt = sum(c.values()); out['M3_step2'] = {k: x / tt for k, x in c.items()} | dict(n=tt)
    if m4:
        from collections import Counter
        c = Counter(); nat = Counter()
        for s in legal:
            for s2 in legal:
                if s2 == s: continue
                for o, w in zip(dec(eng, H[s2] + Wr[s], M), ws):
                    ps, _ = Ev.parse_state(o['text'], d, S.people(w) if d in S.S1B else None)
                    ns = S.advance(d, s2, 'plus') if legal_step(d, s2, 'plus', 'natural') else None
                    if ps == g[s2] and Ev.score(o['text'], S.gold(w, g[s2], t), w, o['ended'])['success']: c['relative'] += 1
                    elif ps == g[s]: c['absolute'] += 1
                    elif ps == s2: c['null'] += 1
                    elif ps is None: c['unparsable'] += 1
                    else:
                        c['other'] += 1
                        if ps == ns and ns != g[s2]: nat['natural_successor_within_other'] += 1
        tot = sum(c.values()); out['M4'] = {k: x / tot for k, x in c.items()} | dict(n=tot) | {k: x / tot for k, x in nat.items()}
    out['writes'] = {s: Wr[s].cpu() for s in legal} if m4 == 'keep' else None
    return out


# ---------------------------------------------------------------- protocol / shards
LOCKED4 = ['symutil.py', 'sym4_semantics.py', 'sym4_evaluator.py', 'lib4.py', 'd_encode.py', 'g40.py', 'v_chains.py', 'r_chains.py', 'u_run.py',
           'x_run.py', 's_long.py', 'analyze.py', 'job_gpu.slurm', 'job_cpu.slurm']


def verify_protocol4():
    p = read(ROOT / 'protocol.json'); assert p.get('locked') is True, 'protocol not locked'
    for k, v in p['sources'].items(): assert sha(ROOT / k) == v, f'locked source changed: {k}'
    for k, v in p['data'].items(): assert sha(REPO / k) == v, f'locked data changed: {k}'
    return p


def chain_records(bb, d, mp, method, path):
    out = []
    import lib4
    for f in sorted(lib4.SHARDS.glob(f'chain_{bb}_{d}_{mp}_{method}_{path}_*.jsonl')): out += rows(f)
    return out


def chain_rate(bb, d, mp, method, path, k, recs=None):
    rs = recs if recs is not None else chain_records(bb, d, mp, method, path); ws = {r['world_id'] for r in rs}
    ok = {r['world_id']: r['trajectory_success'] for r in rs if r['step'] == k}; assert len(ok) == len(ws), (bb, d, mp, method, path, k)
    return rate(list(ok.values()))
