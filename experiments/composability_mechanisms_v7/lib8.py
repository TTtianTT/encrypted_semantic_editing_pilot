"""Shared v8 machinery (composability_mechanisms_v7). Copied from v7 lib7.py (which extends v6 lib6.py); v8 changes: split routing
(confirm8 and dev8 here; confirm7 and dev7ho in composability_mechanisms_v6), and the v8 sections at the end of this file (engines for new
backbones, natural text, decoder-only interface, E1, E2). v6 docstring follows:
Shared v6 machinery (composability_mechanisms_v5). Copied from v5 lib5.py (backbones, caches, slots, harmonic planes, vote model,
surgery, chain runner, RRR / FF fitting, single-step and unrolled training, token / attention editors, decoupled freeze, latent
predictor, unrolled L2) and extended for PLAN v6 (paper/PLAN.md, B line): confirm6 (encoding allowed before the lock, decoding only
after), slot-centred operators for the multi-template domains (S-RRR-r, E_all; appendix A.1, A.2), the slot editor C3-U4, the context
readout (A.3), the two-layer attention editor Att2L (A.4), the oracle-routing editor OR (A.5) and unrolled L2 with S <= 8 (A.6)."""
import itertools
import random
from functools import lru_cache
import torch
import torch.nn as nn
import torch.nn.functional as Fn
from symutil import *
import sym5_semantics as S
import sym5_evaluator as Ev

V2DIR = EXP / 'composability_mechanisms_v1'            # the v2 experiment
V3DIR = EXP / 'composability_mechanisms_v2'            # the v3 experiment
V4DIR = EXP / 'composability_mechanisms_v3'            # the v4 experiment
V5DIR = EXP / 'composability_mechanisms_v4'            # the v5 experiment
V6DIR = EXP / 'composability_mechanisms_v5'            # the v6 experiment (confirm6, v6 editors, slot operators, calibrations)
V7DIR = EXP / 'composability_mechanisms_v6'            # the v7 experiment (confirm7, dev7ho, v7 editors, U calibration)
BB_NAME = {'bart': 'bart', 't5': 't5gemma'}
L_DOMAINS = dict(bart=['weekday', 'month', 'compass', 'hour', 'compass8', 'season'], t5=['weekday', 'month', 'hour', 'compass8'])
D_DOMAINS = dict(bart=['weekday', 'month', 'hour', 'compass8', 'season'], t5=['weekday', 'month', 'hour', 'compass8'])
GRID_DOMAINS = ['weekday', 'month', 'hour', 'compass8']
B_DOMAINS = ['bind3', 'name3', 'bind3fix']
MT_DOMAINS = dict(bart=['weekday-mt', 'month-mt', 'hour-mt'], t5=['month-mt'])
V4_DOMAINS = ['hour', 'compass8', 'season', 'bind3', 'bind3fix', 'name3']   # train/dev worlds and caches from v4
T5_OLD = ['weekday', 'month', 'compass']                # T5Gemma train/dev caches from v3
M_DOMAINS = MT_DOMAINS                                  # v6 unit M
C_DOMAINS = ['weekday', 'month']                        # v6 unit C (BART, template 0)
K_DOMAINS = ['bind3', 'name3', 'bind3fix']              # v6 unit K (BART, template 3)
CONFIRM = 'confirm8'
NEW_SPLITS = (CONFIRM, 'dev8')                         # v8 splits (this directory)
V7_SPLITS = ('confirm7', 'dev7ho')                     # v7 splits (composability_mechanisms_v6)
SHARD = 16
SHARDS = ROOT / 'results/shards'   # module attribute (patched only by the pre-lock smoke test)
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'


def base_of(d):
    return d[:-3] if d.endswith('-mt') else d


# ---------------------------------------------------------------- backbones
def engine5(bb):
    require_slurm(); source_path()
    from backend import Backend
    return Backend(BB_NAME[bb])


def mdtype(eng):
    return next(eng.model.parameters()).dtype


def dec(eng, h, m):
    return eng.decode(h.to(mdtype(eng)), m)


# ---------------------------------------------------------------- worlds, caches, slots
def tmpl(d):
    return 3 if d in S.S1B else 'mt' if d.endswith('-mt') else 0


def tmpl_tag(d):
    return {3: 't3', 0: 't0', 'mt': 'tmt'}[tmpl(d)]


def wfile(d, split):
    if split == 'confirm3': return V3DIR / f'data/{d}/worlds.jsonl'
    if split == 'confirm4': return V4DIR / f'data/{d}/worlds.jsonl'
    if split in NEW_SPLITS: return ROOT / f'data/{d}/worlds.jsonl'
    if split == 'confirm6': return V6DIR / f'data/{d}/worlds.jsonl'
    if split in V7_SPLITS: return V7DIR / f'data/{d}/worlds.jsonl'
    if split == 'confirm5' or d.endswith('-mt'): return V5DIR / f'data/{d}/worlds.jsonl'     # multi-template train / dev: v5
    if d in V1_DOMAINS: return V1 / f'data/{d}/worlds.jsonl'
    assert d in V4_DOMAINS, d
    return V4DIR / f'data/{d}/worlds.jsonl'


@lru_cache(None)
def _worlds(d, split):
    return tuple(w for w in rows(wfile(d, split)) if w['split'] == split)


def worlds5(d, split):
    return list(_worlds(d, split))


def cpath(bb, d, split, s):
    if split == 'confirm3': return V3DIR / f'local/{bb}_{d}_confirm3_t{tmpl(d)}_s{s}.pt'
    if split == 'confirm4': return V4DIR / f'local/{bb}_{d}_confirm4_t{tmpl(d)}_s{s}.pt'
    if split in NEW_SPLITS: return ROOT / f'local/{bb}_{d}_{split}_{tmpl_tag(d)}_s{s}.pt'
    if split == 'confirm6': return V6DIR / f'local/{bb}_{d}_{split}_{tmpl_tag(d)}_s{s}.pt'
    if split in V7_SPLITS: return V7DIR / f'local/{bb}_{d}_{split}_{tmpl_tag(d)}_s{s}.pt'
    if split == 'confirm5' or d.endswith('-mt'): return V5DIR / f'local/{bb}_{d}_{split}_{tmpl_tag(d)}_s{s}.pt'
    if bb == 'bart' and d in V1_DOMAINS: return V1 / f'local/e1_{d}_{split}_t0_s{s}.pt'
    if bb == 't5' and d in T5_OLD: return V3DIR / f'local/t5_{d}_{split}_t0_s{s}.pt'
    assert d in V4_DOMAINS, (bb, d)
    return V4DIR / f'local/{bb}_{d}_{split}_t{tmpl(d)}_s{s}.pt'


@lru_cache(None)
def cache5(bb, d, split, s):
    return load(cpath(bb, d, split, s))


def slots(bb, d, split):
    """Long tensor (W,) of attribute-slot positions (template 0: constant; template 3 and multi-template: per world)."""
    if split == 'confirm3': f = V3DIR / 'data/slot_positions.json'
    elif split in NEW_SPLITS: f = ROOT / 'data/slot_positions.json'
    elif split == 'confirm6': f = V6DIR / 'data/slot_positions.json'
    elif split in V7_SPLITS: f = V7DIR / 'data/slot_positions.json'
    elif split == 'confirm5' or d.endswith('-mt'): f = V5DIR / 'data/slot_positions.json'
    else: f = V4DIR / 'data/slot_positions.json'
    tab = read(f)[bb]
    if d not in tab:   # v1 domains outside v4 (egoside, daysago): template-0 constant positions from v3's audit
        assert split in ('train', 'dev') and tmpl(d) == 0; tab = read(V3DIR / 'data/slot_positions.json')[bb]
    sp = tab[d]; ws = worlds5(d, split)
    return torch.tensor([sp['all'] if 'all' in sp else sp['per_world'][w['world_id']] for w in ws])


def slot_matrix(bb, d, split):
    """(W, N, dim) float64 canonical slot vectors c_w(x), states in natural order."""
    pos = slots(bb, d, split); ar = torch.arange(len(pos))
    return torch.stack([cache5(bb, d, split, s)['h'][ar, pos].double() for s in S.states(d)], 1)


def lock_ok():
    p = ROOT / 'protocol.json'
    return p.exists() and read(p).get('locked') is True


@torch.no_grad()
def encode_split5(eng, bb, d, split, bs=32):
    """PLAN B1: confirm6 may be encoded before the lock (never decoded before it)."""
    ws = worlds5(d, split); ids = [w['world_id'] for w in ws]
    for s in S.states(d):
        f = cpath(bb, d, split, s)
        assert str(f).startswith(str(ROOT)), f'refusing to write outside this experiment: {f}'
        if f.exists() and load(f)['world_ids'] == ids: continue
        hs = []; ms = []
        for i in range(0, len(ws), bs):
            h, m = eng.encode([S.render(w, s, tmpl(d)) for w in ws[i:i + bs]]); hs.append(h.float().cpu()); ms.append(m.cpu())
        n = max(int(m.sum(1).max()) for m in ms)
        hs = [Fn.pad(h, (0, 0, 0, n - h.shape[1])) if h.shape[1] < n else h[:, :n] for h in hs]; ms = [Fn.pad(m, (0, n - m.shape[1])) if m.shape[1] < n else m[:, :n] for m in ms]
        h = torch.cat(hs); m = torch.cat(ms)
        assert int(m[:, n:].sum()) == 0, 'right padding expected'
        save(f, dict(h=h.contiguous(), m=m.contiguous(), world_ids=ids))


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
    """Harmonic planes from train c-bar. Natural map: the v3 plane files (weekday/month/compass) and the v4 plane files (hour/compass8/
    season), identical procedure and data; multi-template domains: computed here from the train split pooled over training templates."""
    for f in (V3DIR / f'local/planes_{bb}_{d}.pt', V4DIR / f'local/planes_{bb}_{d}.pt', V5DIR / f'local/planes_{bb}_{d}.pt'):
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


class PlaneEd:
    def __init__(self, A, c, B, pos):
        self.A, self.c, self.B, self.pos = A.float().to(DEV), c.float().to(DEV), B.float().to(DEV), pos.to(DEV)
    def __call__(self, h, m):
        ar = torch.arange(len(h), device=h.device); h1 = h.clone(); hs = h1[ar, self.pos].float(); z = hs @ self.B
        h1[ar, self.pos] = hs + (z @ self.A.T + self.c - z) @ self.B.T
        return h1


# ---------------------------------------------------------------- chains
def files(kind, bb, d, mp, method, tag, n):
    import lib7 as lib6                                        # module attribute SHARDS (patched by smoke tests)
    return [lib6.SHARDS / f'{kind}_{bb}_{d}_{mp}_{method}_{tag}_{lo:03d}.jsonl' for lo in range(0, n, SHARD)]


def write_shards(fs, recs):
    for j, f in enumerate(fs):
        write(f, [r for r in recs if j * SHARD <= r['index'] < (j + 1) * SHARD])


@torch.no_grad()
def run_chain(eng, bb, d, mp, method, ops, name, start, oplist, split=CONFIRM, model=None, decode=True):
    """ops: {'plus','minus'} -> callable, or None for reencode. start: 'world_start' or a state.
    model: optional dict(P=planes, lams={name: lam}) to record vote-model argmax on the actual latent slot."""
    if split == CONFIRM: assert lock_ok(), 'confirm6 decoding only after the lock (PLAN B1)'
    ws = worlds5(d, split); n = len(ws); fs = files('chain', bb, d, mp, method, name, n)
    if all(f.exists() for f in fs): return
    C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); idx = torch.arange(n)
    state = [w['start_state'] for w in ws] if start == 'world_start' else [start] * n; s0 = list(state)
    stack = lambda st: (torch.stack([C[s]['h'][i] for i, s in enumerate(st)]).cuda(), torch.stack([C[s]['m'][i] for i, s in enumerate(st)]).cuda())
    h, m = stack(state); ok = [True] * n; recs = []
    if model is not None:
        pos = slots(bb, d, split).cuda(); Cw = slot_matrix(bb, d, split).cuda()
    for step, op in enumerate(oplist, 1):
        prev = torch.tensor(state, device="cuda"); state = [S.advance(d, s, op, mp) for s in state]; ref, _ = stack(state)
        h = ref.clone() if ops is None else apply_op(ops[op], h, m, prev)
        out = dec(eng, h, m); am = {}
        if model is not None:
            am = {f"argmax_{k}": v for k, v in readout(h, m, pos, Cw, model).items()}
        for j, w in enumerate(ws):
            sc = Ev.score(out[j]['text'], S.gold(w, state[j], t), w, out[j]['ended']); ok[j] = ok[j] and sc['success']
            ps, pw = Ev.parse_state(out[j]['text'], d, S.people(w) if d in S.S1B else None, gold=S.gold(w, state[j], t))
            recs.append(dict(index=j, backbone=bb, domain=d, map=mp, method=method, path=name, world_id=w['world_id'], step=step, operation=op,
                             start=s0[j], state=state[j], success=sc['success'], target=sc['target'], preserved=sc['preserved'],
                             trajectory_success=ok[j], decoded_state=ps, decoded_word=pw, text=out[j]['text'],
                             **{k: v[j] for k, v in am.items()}))
    write_shards(fs, recs)


@torch.no_grad()
def run_singles(eng, bb, d, mp, method, ops, split=CONFIRM):
    if split == CONFIRM: assert lock_ok()
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
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
    ws = worlds5(d, split); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); ok = []
    for s in S.states(d):
        for op in ('plus', 'minus'):
            if op_only and op != op_only: continue
            try: y = S.advance(d, s, op, mp)
            except ValueError: continue
            h, m = C[s]["h"].cuda(), C[s]["m"].cuda(); h = C[y]["h"].cuda() if ops is None else apply_op(ops[op], h, m, torch.full((len(ws),), s, device="cuda"))
            ok += [Ev.score(o['text'], S.gold(w, y, t), w, o['ended'])['success'] for o, w in zip(dec(eng, h, m), ws)]
    return rate(ok)


@torch.no_grad()
def dev_chain(eng, bb, d, mp, ops, oplist, split='dev', start='world_start'):
    """In-memory trajectory success R_k (k = 1..len) on a non-confirm split (no shards)."""
    assert split != CONFIRM
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
    state = [w['start_state'] for w in ws] if start == 'world_start' else [start] * n
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).cuda(); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).cuda()
    ok = [True] * n; R = []
    for op in oplist:
        prev = torch.tensor(state, device="cuda"); state = [S.advance(d, s, op, mp) for s in state]; h = apply_op(ops[op], h, m, prev); out = dec(eng, h, m)
        for j, w in enumerate(ws): ok[j] = ok[j] and Ev.score(out[j]['text'], S.gold(w, state[j], t), w, out[j]['ended'])['success']
        R.append(rate(ok))
    return R


@torch.no_grad()
def reencode_rate(eng, bb, d, splits=('train', 'dev')):
    ok = []
    for split in splits:
        ws = worlds5(d, split); t = tmpl(d)
        for s in S.states(d):
            c = cache5(bb, d, split, s)
            ok += [Ev.score(o['text'], S.gold(w, s, t), w, o['ended'])['success'] for o, w in zip(dec(eng, c['h'].cuda(), c['m'].cuda()), ws)]
    return rate(ok)


# ---------------------------------------------------------------- RRR fitting (v1-v3 procedure) and FF-r (A.3)
def _F():
    if str(CWR) not in sys.path: sys.path.insert(0, str(CWR))
    import fit as F
    return F


def paired_tokens(bb, d, mp, op, idx, split='train'):
    ws = worlds5(d, split); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; X = []; Y = []
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
    F = _F(); ws = worlds5(d, 'train')
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
    ws = worlds5(d, split); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; out = {}
    for op in ('plus', 'minus'):
        its = [(i, s) for s in S.states(d) for i in range(len(ws)) if legal_step(d, s, op, mp)]; v = []
        for lo in range(0, len(its), 64):
            part = its[lo:lo + 64]
            h = torch.stack([C[s]['h'][i] for i, s in part]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in part]).to(DEV)
            y = torch.stack([C[S.advance(d, s, op, mp)]['h'][i] for i, s in part]).to(DEV); v.append(token_mse(h, y, m))
        out[op] = float(torch.cat(v).mean())
    return out


def train_editor(eng, bb, d, mp, group, seed, updates=600, l2_weight=1.0, init_rrr=None, batch=8, micro=2, lr=1e-3, clip=1.0,
                 log_every=1, dev_every=None, dev_fn=None, snapshots=()):
    """v3 train_editor. group: C1 (CE), C3 (CE + l2_weight * normalised L2), L2 (normalised L2 only; CE still logged every log_every)."""
    source_path(); from backend import editors
    ws = worlds5(d, 'train'); C = {s: cache5(bb, d, 'train', s) for s in S.states(d)}; t = tmpl(d); dt = mdtype(eng)
    pool = {op: [(i, s) for s in S.states(d) for i in range(len(ws)) if legal_step(d, s, op, mp)] for op in ('plus', 'minus')}
    stack = lambda its: (torch.stack([C[s]['h'][i] for i, s in its]).cuda(), torch.stack([C[s]['m'][i] for i, s in its]).cuda())
    with torch.no_grad(): scale = l2_scales(bb, d, mp)
    ed = editors(eng.d, seed)
    if init_rrr is not None:
        with torch.no_grad():
            for op in ('plus', 'minus'):
                f = init_rrr[op]; b = f['left'].double() @ f['right'].double(); u, s_, vh = torch.linalg.svd(b, full_matrices=False)
                ed[op].v.weight.copy_((u[:, :16] * s_[:16].sqrt()).T.float()); ed[op].u.weight.copy_((s_[:16].sqrt()[:, None] * vh[:16]).T.float()); ed[op].b.copy_(f['bias'])
    opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []; snaps = {}
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
        if k + 1 in snapshots: snaps[k + 1] = {kk: vv.detach().cpu().clone() for kk, vv in ed.state_dict().items()}
        if logk:
            rec = dict(step=k + 1, op=op, grad=float(gn), **tot)
            if dev_every and dev_fn and (k + 1) % dev_every == 0: rec['dev_l2'] = dev_fn(ed)
            hist.append(rec)
    ed.eval().requires_grad_(False); ed.snapshots = snaps
    return ed, hist, scale


@torch.no_grad()
def dev_l2(ed, bb, d, mp, scale, split='dev'):
    """Mean normalised token L2 of single steps on a split (plus and minus averaged)."""
    ws = worlds5(d, split); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; out = {}
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
    ws = worlds5(d, 'train'); C = {s: cache5(bb, d, 'train', s) for s in S.states(d)}; t = tmpl(d); dt = mdtype(eng)
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
    """Tok-L2 / Tok-U: delta_i = b + U V h_i (rank 32). Att (v4 Att-L2 = Att1-U, heads = 1): adds W_o sum_j alpha_ij W_v h_j,
    alpha = softmax_j((W_q h_i)^T (W_k h_j) / sqrt(64)) over non-pad j of the same sentence. Att2-U (A.4): two heads of d_a = 64, outputs
    concatenated and mapped by W_o (d x 128). W_o zero-initialised (training starts as Tok). heads = 1 is numerically v4's Att-L2."""
    def __init__(self, d, rank=32, att=False, dk=64, heads=1):
        super().__init__(); self.att = att; self.dk = dk; self.heads = heads
        self.b = nn.Parameter(torch.zeros(d)); self.v = nn.Linear(d, rank, bias=False); self.u = nn.Linear(rank, d, bias=False)
        nn.init.normal_(self.v.weight, std=.01); nn.init.zeros_(self.u.weight)
        if att:
            self.q = nn.Linear(d, dk * heads, bias=False); self.k = nn.Linear(d, dk * heads, bias=False); self.wv = nn.Linear(d, dk * heads, bias=False)
            self.o = nn.Linear(dk * heads, d, bias=False); nn.init.zeros_(self.o.weight)

    def _split(self, x):
        B, L_, _ = x.shape; return x.view(B, L_, self.heads, self.dk).transpose(1, 2)            # (B, H, L, dk)

    def attention(self, z, m):
        """(B, L, L) for one head (v4 shape), (B, H, L, L) for several."""
        sc = (self._split(self.q(z)) @ self._split(self.k(z)).transpose(-1, -2)) / np.sqrt(self.dk)
        a = torch.softmax(sc.masked_fill(~m.bool()[:, None, None, :], float('-inf')), -1)
        return a[:, 0] if self.heads == 1 else a

    def forward(self, h, m):
        z = h.float(); delta = self.b + self.u(self.v(z))
        if self.att:
            a = self.attention(z, m); a = a[:, None] if self.heads == 1 else a; B, L_, _ = z.shape
            delta = delta + self.o((a @ self._split(self.wv(z))).transpose(1, 2).reshape(B, L_, self.heads * self.dk))
        return (z + delta * m[..., None]).to(h.dtype)


def tokatt_pair(d, seed, att, rank=32, heads=1):
    torch.manual_seed(seed)
    return nn.ModuleDict({op: TokAttEditor(d, rank, att, heads=heads) for op in ('plus', 'minus')}).to(DEV).float()


def rel_l2(e, y, x, m):
    """A.5 relative L2: mean_i ||h_i + delta_i - E(target)_i||^2 / mean_i ||E(target)_i - E(source)_i||^2 over non-pad positions."""
    v = m[..., None].float()
    return ((e - y).square() * v).sum() / ((y - x).square() * v).sum()


def train_l2_editor(bb, d, op, seed, att, updates=4000, batch=16, lr=1e-3, clip=1.0, mp='natural', H=None):
    """A.5: train one operator (plus or minus) of a Tok-L2 / Att-L2 editor on train canonical pairs. H: optional {s: (h, m)} override (selftest)."""
    if H is None:
        ws = worlds5(d, 'train'); H = {s: (cache5(bb, d, 'train', s)['h'], cache5(bb, d, 'train', s)['m']) for s in S.states(d)}
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
    ws = worlds5(d, split); n = len(ws); st = S.states(d); t = tmpl(d); pos = slots(bb, d, split).to(DEV); ar = torch.arange(n, device=DEV)
    H = {s: cache5(bb, d, split, s)['h'].to(DEV) for s in st}; M = cache5(bb, d, split, st[0])['m'].to(DEV); v = M[..., None]
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
LOCKED6 = ['symutil.py', 'sym5_semantics.py', 'sym5_evaluator.py', 'lib6.py', 'lcore.py', 'cells6.py', 'g60.py', 'm_chains.py', 'c_chains.py', 'k_chains.py',
           'analyze.py', 'job_gpu.slurm', 'job_cpu.slurm', 'data/templates_mt.json']


def verify_protocol6():
    p = read(ROOT / 'protocol.json'); assert p.get('locked') is True, 'protocol not locked'
    for k, v in p['sources'].items(): assert sha(ROOT / k) == v, f'locked source changed: {k}'
    for k, v in p['data'].items(): assert sha(REPO / k) == v, f'locked data changed: {k}'
    return p


def chain_records(bb, d, mp, method, path):
    out = []
    import lib7 as lib6                                        # module attribute SHARDS (patched by smoke tests)
    for f in sorted(lib6.SHARDS.glob(f'chain_{bb}_{d}_{mp}_{method}_{path}_*.jsonl')): out += rows(f)
    return out


def chain_rate(bb, d, mp, method, path, k, recs=None):
    rs = recs if recs is not None else chain_records(bb, d, mp, method, path); ws = {r['world_id'] for r in rs}
    ok = {r['world_id']: r['trajectory_success'] for r in rs if r['step'] == k}; assert len(ok) == len(ws), (bb, d, mp, method, path, k)
    return rate(list(ok.values()))


# ---------------------------------------------------------------- v5 inputs (PLAN 3): base operators, locked vote models, editor registry
def base_fit(bb, d, gates=None):
    """(fit dict {(op, r): ...}, rank) of the base operator. BART: v4 RRR-16 (compass: v3's RRR-16, the v2 fit file); T5Gemma: v4 GB rank
    (hour 32, else 16). Multi-template domains: this experiment's GB rank (gates = results/gates_{bb}.json content)."""
    if d.endswith('-mt'): return load(V5DIR / f'local/{bb}_rrr_{d}_natural_base.pt'), 16     # v5 full-sequence RRR (reference only)
    if bb == 'bart' and d == 'compass': return load(V2DIR / 'local/rrr_compass_natural.pt'), 16
    return load(V4DIR / f'local/{bb}_rrr_{d}_natural_base.pt'), read(V4DIR / 'protocol.json')['gates'][bb]['GB'][d]['base_rank']


def base_ops(bb, d, gates=None):
    f, r = base_fit(bb, d, gates)
    return {op: RRRop(f[op, r]) for op in ('plus', 'minus')}


def vote_lams(bb, d):
    """Locked vote-model weights {full, equal, fund}: v3 calib (compass), v4 protocol (weekday, month, hour, compass8, season),
    this experiment's calib_mt (multi-template; locked with this protocol)."""
    if d == 'compass': m = read(V3DIR / f'results/calib_{bb}.json')['domains']['compass']['models']
    elif d.endswith('-mt'): m = read(V6DIR / f'results/calib_mt_{bb}.json')['domains'][d]['models']      # v6 locked multi-template calibration
    else: m = read(V4DIR / 'protocol.json')['calib'][bb][d]['models']
    return {k: torch.tensor(v['lam'], dtype=torch.float64) for k, v in m.items()}


def vote_model(bb, d):
    return dict(P=planes(bb, d), lams=vote_lams(bb, d))


def grid_ranks(bb, d):
    N = len(S.states(d))
    return [N - 4, N - 3, N - 2] if bb == 'bart' else [N - 2, N - 1, N, N + 1, N + 2] + ([13] if d in ('month', 'hour') else [])


def existing_editors(bb):
    """Trained editors reused by L (PLAN 6.1). family: 'state' (training objective contains canonical L2) or 'CE'."""
    E = []
    add = lambda name, d, path, family, note: E.append(dict(name=name, domain=d, path=str(path), family=family, note=note, new=False))
    if bb == 'bart':
        for s in SEEDS:
            add(f'C3v1_s{s}', 'month', V1 / f'local/e1_C3_month_s{s}_0600.pt', 'state', 'v1 C3')
            for v in ('l3', 'l10', 'rrrinit'): add(f'C3{v}v3_s{s}', 'month', V3DIR / f'local/a_C3_{v}_month_s{s}.pt', 'state', f'v3 C3 {v}')
            for v in ('a_C3_6000', 'b_L2_600', 'c_L2_6000'): add(f'P2{v.split("_")[0]}_s{s}', 'month', V4DIR / f'local/p2_{v}_month_s{s}.pt', 'state', f'v4 P2 {v}')
            for d in ('weekday', 'month', 'compass'): add(f'C1v1_s{s}', d, V1 / f'local/e1_C1_{d}_s{s}_0600.pt', 'CE', 'v1 C1')
        ut = read(V4DIR / 'results/u_train.json')
        for v, doms in (('C3U4', ('month',)), ('C1U4', ('weekday', 'month', 'compass')), ('C1UN', ('weekday', 'month'))):
            for d in doms:
                for s in SEEDS:
                    st = ut[f'{v}/{d}/s{s}']
                    if st['status'] == 'ok':
                        add(f'{v}v4_s{s}', d, V4DIR / f"local/u_{v}_{d}_s{s}_u{st['updates']}.pt", 'state' if v.startswith('C3') else 'CE', f"v4 {v} ({st['updates']} updates)")
    else:
        for s in SEEDS:
            for d in ('weekday', 'month'): add(f'C1v3_s{s}', d, V3DIR / f'local/t5_C1_{d}_s{s}.pt', 'CE', 'v3 T5Gemma C1')
    return E


# new editors trained before the lock (PLAN 6.1, 9.1, 10.1): (backbone, unit, variant, domain, seeds, family, kind, updates)
NEW_EDITORS = [
    ('bart', 'L', 'C3n1200', 'weekday', SEEDS, 'state', 'single', 1200), ('bart', 'L', 'C3n1200', 'month', SEEDS, 'state', 'single', 1200),
    ('bart', 'L', 'C3n2400', 'weekday', SEEDS, 'state', 'single', 2400), ('bart', 'L', 'C3n2400', 'month', SEEDS, 'state', 'single', 2400),
    ('bart', 'L', 'C3U4n', 'hour', SEEDS, 'state', 'unrolled', 1200), ('bart', 'L', 'C1n', 'hour', SEEDS, 'CE', 'single', 600),
    ('t5', 'L', 'C3U4n', 'month', (42, 43), 'state', 'unrolled', 1200), ('t5', 'L', 'C1U4n', 'month', (42, 43), 'CE', 'unrolled', 1200),
] + [('bart', 'N', 'C1n', d, SEEDS, 'CE', 'single', 600) for d in ('weekday-mt', 'month-mt', 'hour-mt')] \
  + [('bart', 'N', 'C3U4n', d, SEEDS, 'state', 'unrolled', 1200) for d in ('weekday-mt', 'month-mt', 'hour-mt')] \
  + [('t5', 'N', 'C1n', 'month-mt', SEEDS, 'CE', 'single', 600)]


def new_editor_path(bb, v, d, s, upd):
    return V5DIR / f'local/n_{bb}_{v}_{d}_s{s}_u{upd}.pt'


# ---------------------------------------------------------------- A.3 oracle decoupled freeze, A.1 latent predictor
def apply_op(T, h, m, prev):
    """Operators with needs_state (D_S) also receive the gold previous state g_{t-1} (LongTensor (W,))."""
    return T(h, m, prev) if getattr(T, 'needs_state', False) else T(h, m)


class DecoupledFreeze:
    """D_S (A.3): (1) on the slot replace the plane-S component of h_{t-1} by the correct one, P_S c_w(g_{t-1}); (2) apply T;
    (3) on the output slot set the plane-S component back to the frozen value P_S h_{t-1,s}. Other planes evolve as if plane S were
    correct; the readout still sees plane S at its frozen value. Oracle diagnostic (uses the gold state). Computed in h's dtype."""
    needs_state = True

    def __init__(self, T, Bs, pos, Cw):
        self.T, self.Bs, self.pos, self.Cw = T, Bs.to(DEV), pos.to(DEV), Cw.to(DEV)

    def __call__(self, h, m, prev):
        ar = torch.arange(len(h), device=h.device); B = self.Bs.to(h.dtype); hs0 = h[ar, self.pos]
        hin = h.clone(); hin[ar, self.pos] = hs0 - (hs0 @ B) @ B.T + (self.Cw[ar, prev].to(h.dtype) @ B) @ B.T
        h2 = self.T(hin, m); out = h2.clone(); hs2 = h2[ar, self.pos]
        out[ar, self.pos] = hs2 - (hs2 @ B) @ B.T + (hs0 @ B) @ B.T
        return out


@torch.no_grad()
def simulate_chain(bb, d, ops, oplist, model, split=CONFIRM, start='world_start'):
    """A.1 latent-space predictor: the chain dynamics of run_chain without decoding; per world and step the gold state and the argmax
    of each locked vote model on the slot. Returns dict(world_ids, start, states (W x K), argmax {model: W x K})."""
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}
    state = [w['start_state'] for w in ws] if start == 'world_start' else [start] * n; s0 = list(state)
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots(bb, d, split).to(DEV); Cw = slot_matrix(bb, d, split).to(DEV)
    states = []; am = {}; drift = []
    for op in oplist:
        prev = torch.tensor(state, device=DEV); state = [S.advance(d, s, op) for s in state]; h = apply_op(ops[op], h, m, prev); states.append(state)
        for k, v in readout(h, m, pos, Cw, model).items(): am.setdefault(k, []).append(v)
        if model.get("ctx") is not None: drift.append([round(float(x), 6) for x in ctx_dists(h, model["ctx"]).min(-1).values])
    T_ = lambda L: [list(x) for x in zip(*L)]
    out = dict(world_ids=[w["world_id"] for w in ws], start=s0, states=T_(states), argmax={k: T_(v) for k, v in am.items()})
    if drift: out["ctx_drift"] = T_(drift)          # exploratory (protocol): min_y d_ctx(h_t, y) per world and step
    return out


def sim_records(sim, latent='argmax_full'):
    """Simulation output -> chain-like records for lcore.world_table (decoded fields from the observed shards are merged later)."""
    out = []
    for i, w in enumerate(sim['world_ids']):
        for t, g in enumerate(sim['states'][i], 1): out.append(dict(world_id=w, step=t, state=g, **{f'argmax_{k}': v[i][t - 1] for k, v in sim['argmax'].items()}))
    return out


# ---------------------------------------------------------------- A.4 unrolled L2 training of token / attention editors (B unit)
def unrolled_l2_loss(ed, h, m, seq, ys, xs):
    """A.4: (1/S) sum_s rel_l2(h_s, E(x_s)) along the unrolled chain h_s = T_{op_s}(h_{s-1}); xs[s] = E(x_{s-1}) (relative-L2 denominator)."""
    loss = 0.
    for op, y, x in zip(seq, ys, xs): h = ed[op](h, m); loss = loss + rel_l2(h, y, x, m)
    return loss / len(seq)


def train_unrolled_l2(bb, d, seed, kind, updates=4000, Sset=(1, 2, 3, 4), batch=16, lr=1e-3, clip=1.0, H=None, adv=None):
    """kind: 'Tok' (Tok-U), 'Att1' (Att1-U), 'Att2' (Att2-U). Per update: path type uniform over plus^S / minus^S / alternating, S
    uniform over Sset, batch 16 (world, start) from train; loss (1/S) sum_s rel_l2(h_s, E(x_s)) with the step's canonical source E(x_{s-1})
    in the denominator; gradient through the whole unrolled chain; AdamW 1e-3, clip 1. H / adv override the data (self-test)."""
    if H is None: H = {s: (cache5(bb, d, 'train', s)['h'], cache5(bb, d, 'train', s)['m']) for s in S.states(d)}
    adv = adv or (lambda s, op: S.advance(d, s, op))
    W = len(next(iter(H.values()))[0]); pool = [(i, s) for s in H for i in range(W)]; dim = next(iter(H.values()))[0].shape[-1]
    ed = tokatt_pair(dim, seed, kind != 'Tok', heads=2 if kind == 'Att2' else 1); opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0)
    rng = random.Random(seed); hist = []
    get = lambda its: torch.stack([H[s][0][i] for i, s in its]).to(DEV).float()
    for k in range(updates):
        pk = rng.choice(('plus', 'minus', 'alt')); S_ = rng.choice(list(Sset)); seq = path_seq(pk, S_); bt = [rng.choice(pool) for _ in range(batch)]
        m = torch.stack([H[s][1][i] for i, s in bt]).to(DEV); h = get(bt); xs, ys = [], []; cur = list(bt)
        opt.zero_grad(set_to_none=True)
        for op in seq: nxt = [(i, adv(s, op)) for i, s in cur]; xs.append(get(cur)); ys.append(get(nxt)); cur = nxt
        loss = unrolled_l2_loss(ed, h, m, seq, ys, xs)
        assert torch.isfinite(loss); loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); opt.step()
        if (k + 1) % 50 == 0 or k == 0: hist.append(dict(step=k + 1, path=pk, S=S_, loss=float(loss), grad=float(gn)))
    ed.eval().requires_grad_(False)
    return ed, hist


def grid_ops(bb, d, kind, r):
    """RRR-r / FF-r operators of the rank grid: v4 fits (local/<bb>_R_<d>.pt of v4) or ranks fitted here (local/<bb>_R_<d>_v5.pt)."""
    f5 = V5DIR / f'local/{bb}_R_{d}_v5.pt'
    for f in ([f5] if f5.exists() else []) + [V4DIR / f'local/{bb}_R_{d}.pt']:
        fits = load(f)
        if (kind, 'plus', r) in fits: return {op: RRRop(fits[kind, op, r]) for op in ('plus', 'minus')}
    raise KeyError((bb, d, kind, r))


# ================================================================ v6 (PLAN B line)
# ---------------------------------------------------------------- readout (slot vote model; optional context term, A.3)
def readout(h, m, pos, Cw, model):
    """Per-world argmax of every readout in `model` on the latent h (W, L, dim): the slot vote models {name: lam} and, if model has 'ctx'
    (ctx_model), the slot + context score S(y) = -sum_k lam_k d_k(slot, y) - lam_ctx d_ctx(h, y) as 'ctx' (slot part = lams['full'])."""
    ar = torch.arange(len(h), device=h.device); P = [(k, B.to(h.device)) for k, B in model['P']]
    Dm = plane_dists(h[ar, pos].double(), Cw.to(h.device), P); out = {}
    for k, lam in model['lams'].items(): out[k] = vote_scores(Dm, lam.to(h.device)).argmax(-1).tolist()
    if model.get('ctx') is not None:
        c = model['ctx']; sc = vote_scores(Dm, model['lams']['full'].to(h.device)) - float(c['lam_ctx']) * ctx_dists(h, c)
        out['ctx'] = sc.argmax(-1).tolist()
    return out


# ---------------------------------------------------------------- A.1 slot RRR, A.2 E_all (slot-centred operators)
def next_idx(d, op):
    return [S.advance(d, s, op) for s in S.states(d)]


def fit_srrr_X(Xw, nxt, ranks, ridge_grid=(1e-4, 1e-3, 1e-2, 1e-1), inner_seed=BOOT_SEED, inner_frac=80 / 192):
    """A.1 on slot vectors Xw (W, N, dim) float64 of the training templates' train worlds; nxt: {op: target index per state}. Procedure of
    lib5.fit_rrr4 (fit.solve): relative ridge per rank chosen on an inner split of the train worlds, refit on all train, rank r, bias."""
    F = _F(); W = Xw.shape[0]; order = list(range(W)); random.Random(inner_seed).shuffle(order); k = int(round(inner_frac * W))
    fi, vi = sorted(order[:k]), sorted(order[k:]); final = {}; info = {}
    pairs = lambda idx, op: (Xw[idx].reshape(-1, Xw.shape[-1]), (Xw[idx][:, nxt[op]] - Xw[idx]).reshape(-1, Xw.shape[-1]))
    for op in nxt:
        A = pairs(fi, op); Bv = pairs(vi, op); st = F.sufficient(*A); sc = {}
        for rel in ridge_grid:
            for r, f in F.solve(st, rel, ranks).items(): sc[rel, r] = F.mse(*Bv, f)
        chosen = {r: min(ridge_grid, key=lambda rel: sc[rel, r]) for r in ranks}
        sa = F.sufficient(*pairs(list(range(W)), op)); sols = {rel: F.solve(sa, rel, ranks) for rel in set(chosen.values())}
        for r, rel in chosen.items():
            f = sols[rel][r]; final[op, r] = {kk: f[kk] for kk in ('left', 'right', 'bias')} | dict(relative_ridge=rel, rank=r); info[f'{op}_{r}'] = rel
    return final, info


def fit_srrr(bb, d, ranks=(16, 32)):
    return fit_srrr_X(slot_matrix(bb, d, 'train'), {op: next_idx(d, op) for op in ('plus', 'minus')}, list(ranks))


class SlotRRRop:
    """S-RRR-r: RRR applied to the slot token only (other positions unchanged)."""
    def __init__(self, f, pos):
        self.left, self.right, self.bias = (f[k].float().to(DEV) for k in ('left', 'right', 'bias')); self.pos = pos.to(DEV)
    def __call__(self, h, m):
        ar = torch.arange(len(h), device=h.device); out = h.clone(); hs = h[ar, self.pos].float()
        out[ar, self.pos] = (hs + hs @ self.left @ self.right + self.bias).to(h.dtype); return out


def fit_eall_X(Xw, P, nxt):
    """A.2: joint least squares (with bias) on the slot coordinates in the span of all harmonic planes (dim N - 1)."""
    B = torch.cat([b for _, b in P], 1).double()
    return {op: fit_plane_editor(Xw, B, None, op, dst=nxt[op]) for op in nxt}, B


def fit_plane_editor(X, B, d, op, dst=None):
    src = list(range(X.shape[1])); dst = dst if dst is not None else [S.advance(d, s, op) for s in S.states(d)]
    Z = (X[:, src] @ B).reshape(-1, B.shape[1]); Zp = (X[:, dst] @ B).reshape(-1, B.shape[1])
    Za = torch.cat([Z, torch.ones(len(Z), 1, dtype=Z.dtype)], 1); sol = torch.linalg.lstsq(Za, Zp).solution
    return sol[:-1].T.contiguous(), sol[-1]


def fit_eall(bb, d):
    return fit_eall_X(slot_matrix(bb, d, 'train'), planes(bb, d), {op: next_idx(d, op) for op in ('plus', 'minus')})


def m_base_ops(bb, d, gates, pos):
    """The GM-selected base operator of a multi-template domain (S-RRR-16 / S-RRR-32 / E_all), acting on the slot at positions pos."""
    b = gates['GM'][d]['base']
    if b in ('SRRR16', 'SRRR32'):
        f = load(V6DIR / f'local/{bb}_srrr_{d}.pt'); r = int(b[4:]); return {op: SlotRRRop(f[op, r], pos) for op in ('plus', 'minus')}
    assert b == 'Eall'; f = load(V6DIR / f'local/{bb}_eall_{d}.pt')
    return {op: PlaneEd(f['fits'][op][0], f['fits'][op][1], f['B'], pos) for op in ('plus', 'minus')}


def full_rrr16_ops(bb, d):
    """Reference: v5's full-sequence RRR-16 of the multi-template domain (fitted on the training templates)."""
    f = load(V5DIR / f'local/{bb}_rrr_{d}_natural_base.pt'); return {op: RRRop(f[op, 16]) for op in ('plus', 'minus')}


# ---------------------------------------------------------------- slot editor (M: slot C3-U4)
class SlotEditor(nn.Module):
    """Rank-16 editor (backend Editor parametrisation) applied to the slot token only: h_slot + b + U V h_slot."""
    def __init__(self, d, rank=16):
        super().__init__(); self.b = nn.Parameter(torch.zeros(d)); self.v = nn.Linear(d, rank, bias=False); self.u = nn.Linear(rank, d, bias=False)
        nn.init.normal_(self.v.weight, std=.01); nn.init.zeros_(self.u.weight)

    def forward(self, h, m, pos):
        z = h.float(); ar = torch.arange(len(h), device=h.device); hs = z[ar, pos]; out = z.clone()
        out[ar, pos] = hs + self.b + self.u(self.v(hs)); return out.to(h.dtype)


class SlotOp:
    def __init__(self, mod, pos):
        self.mod, self.pos = mod, pos.to(DEV)
    def __call__(self, h, m):
        return self.mod(h, m, self.pos)


def slot_pair(d, seed):
    torch.manual_seed(seed); return nn.ModuleDict({op: SlotEditor(d) for op in ('plus', 'minus')}).to(DEV).float()


def slot_scales(bb, d, mp='natural'):
    X = slot_matrix(bb, d, 'train'); out = {}
    for op in ('plus', 'minus'): out[op] = float((X[:, next_idx(d, op)] - X).square().mean())
    return out


def train_unrolled_slot(eng, bb, d, seed, Sset=(1, 2, 3, 4), updates=1200, l2_weight=1.0, batch=8, micro=2, lr=1e-3, clip=1.0):
    """Slot C3-U4 (PLAN B5): the v4 unrolled training (path kind uniform over plus^S / minus^S / alternating, S uniform in Sset, batch 8,
    decoder CE on every step's gold text) plus l2_weight x the canonical L2 on the slot token (normalised by the mean squared slot step),
    with an editor that changes only the slot token."""
    ws = worlds5(d, 'train'); C = {s: cache5(bb, d, 'train', s) for s in S.states(d)}; t = tmpl(d); dt = mdtype(eng); P = slots(bb, d, 'train')
    pool = [(i, s) for s in S.states(d) for i in range(len(ws))]
    stack = lambda its: (torch.stack([C[s]['h'][i] for i, s in its]).cuda(), torch.stack([C[s]['m'][i] for i, s in its]).cuda())
    scale = slot_scales(bb, d); ed = slot_pair(eng.d, seed); opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []
    for k in range(updates):
        kind = rng.choice(('plus', 'minus', 'alt')); S_ = rng.choice(list(Sset)); seq = path_seq(kind, S_)
        bt = [rng.choice(pool) for _ in range(batch)]; opt.zero_grad(set_to_none=True); tot = dict(ce=0., l2=0., loss=0.)
        for lo in range(0, batch, micro):
            part = bt[lo:lo + micro]; h, m = stack(part); pos = P[[i for i, _ in part]].cuda(); ar = torch.arange(len(part), device='cuda'); states = [s for _, s in part]
            ce = 0.; l2 = 0.
            for op in seq:
                states = [S.advance(d, s, op) for s in states]; h = ed[op](h, m, pos)
                ce = ce + eng.ce(h.to(dt), m, [S.render(ws[i], s, t) for (i, _), s in zip(part, states)])[0].mean()
                y, _ = stack([(i, s) for (i, _), s in zip(part, states)])
                l2 = l2 + (h[ar, pos].float() - y[ar, pos].float()).square().mean() / scale[op]
            ce = ce / S_; l2 = l2 / S_; loss = ce + l2_weight * l2; assert torch.isfinite(loss); (loss * len(part) / batch).backward()
            for kk, v in (('ce', ce), ('l2', l2), ('loss', loss)): tot[kk] += float(v.detach()) * len(part) / batch
        gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); assert torch.isfinite(gn)
        assert all(x.grad is None for x in eng.model.parameters()); opt.step()
        hist.append(dict(step=k + 1, kind=kind, S=S_, grad=float(gn), **tot))
    ed.eval().requires_grad_(False)
    return ed, hist, scale


def slot_ops_from(path, dim, pos):
    c = load(path); ed = slot_pair(dim, c['seed']); ed.load_state_dict(c['editor']); ed = ed.eval().requires_grad_(False)
    return {op: SlotOp(ed[op], pos) for op in ('plus', 'minus')}


# ---------------------------------------------------------------- A.3 context readout
def ctx_mask(m, pos):
    cm = m.clone().float(); cm[torch.arange(len(m)), pos] = 0; return cm


@torch.no_grad()
def ctx_basis(bb, d):
    """Q_ctx (dim, N - 1): top principal components of the state-demeaned context representations (every non-pad non-slot position of
    every train world, pooled over states)."""
    N = len(S.states(d)); C = [cache5(bb, d, 'train', s) for s in S.states(d)]; pos = slots(bb, d, 'train')
    H = torch.stack([c['h'].double() for c in C], 1); m = C[0]['m']; cm = ctx_mask(m, pos)          # (W, N, L, dim)
    V = (H - H.mean(1, keepdim=True)) * cm[:, None, :, None].double()
    X = V.reshape(-1, V.shape[-1]); cov = X.T @ X / float(cm.sum() * N)
    vals, vecs = torch.linalg.eigh(cov); Q = vecs[:, -(N - 1):].flip(1).contiguous()
    return Q, (vals.flip(0)[:N - 1] / vals.sum()).tolist()


@torch.no_grad()
def ctx_model_data(bb, d, split, Q):
    """Projected canonical context of every world and state: Zc (W, N, L, r) and the context mask cm (W, L)."""
    C = [cache5(bb, d, split, s) for s in S.states(d)]; pos = slots(bb, d, split); Qf = Q.float()
    Zc = torch.stack([c['h'].float() @ Qf for c in C], 1); return dict(Q=Qf, Zc=Zc, cm=ctx_mask(C[0]['m'], pos))


def ctx_dists(h, c, idx=None):
    """d_ctx(h, y) (W, N): mean over context positions of ||Q^T (h_i - E_w(y)_i)||^2."""
    Zc = c['Zc'] if idx is None else c['Zc'][idx]; cm = c['cm'] if idx is None else c['cm'][idx]
    Zc = Zc.to(h.device); cm = cm.to(h.device); hq = h.float() @ c['Q'].to(h.device)
    dd = (hq[:, None] - Zc).square().sum(-1)                                              # (W, N, L)
    return ((dd * cm[:, None]).sum(-1) / cm.sum(-1)[:, None]).double()


def ctx_lam(bb, d):
    return read(V6DIR / 'results/calib_ctx_bart.json')['domains'][d]['lam_ctx'] if bb == 'bart' else None


def ctx_model(bb, d, split):
    """Locked slot vote model (v5/v4 lams) + the context term (Q_ctx, lam_ctx from results/calib_ctx_bart.json) for unit C."""
    f = load(V6DIR / f'local/ctx_{bb}_{d}.pt'); c = ctx_model_data(bb, d, split, f['Q']); c['lam_ctx'] = ctx_lam(bb, d)
    return dict(P=planes(bb, d), lams=vote_lams(bb, d), ctx=c)


def fit_lam_ctx(Dslot, Dctx, y, lam_slot, grid=None):
    """Exact ML fit of lam_ctx >= 0 with the slot weights fixed: softmax over y of -sum_k lam_k D_k - lam_ctx D_ctx (Dslot (n, N, K),
    Dctx (n, N)). The NLL is evaluated on {0} and a log grid (relative to 1 / std(D_ctx)); the minimiser (ties -> smallest lam_ctx)
    is refined by golden-section search between its grid neighbours. Also reported: dNLL/dlam at 0 (> 0 means the boundary 0 is the
    MLE) and the NLL at 0."""
    base = vote_scores(Dslot.double(), lam_slot.double()); Dctx = Dctx.double(); y = torch.as_tensor(y)
    nll = lambda l: float(Fn.cross_entropy(base - l * Dctx, y, reduction='sum')) / len(y)
    sc = float(1 / Dctx.std().clamp_min(1e-12)); grid = grid if grid is not None else [0.0] + [sc * 10 ** e for e in np.arange(-6, 3.01, .25)]
    vals = [nll(l) for l in grid]; i = min(range(len(grid)), key=lambda j: (vals[j], grid[j]))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    for _ in range(60):
        a, b = lo + .382 * (hi - lo), lo + .618 * (hi - lo)
        if nll(a) <= nll(b): hi = b
        else: lo = a
    lam = grid[i] if vals[i] <= nll((lo + hi) / 2) else (lo + hi) / 2
    p = torch.softmax(base, -1); grad0 = float((Dctx.gather(1, y[:, None])[:, 0] - (p * Dctx).sum(-1)).mean())
    if grad0 >= 0: lam = 0.0      # the NLL is convex in lam_ctx (linear logits): dNLL/dlam >= 0 at 0 makes 0 the exact MLE (DEVIATIONS #13)
    return dict(lam_ctx=lam, nll=nll(lam), nll_slot_only=nll(0.0), dnll_dlam_at_0=grad0, boundary_mle=lam == 0.0, grid_min_index=i)


# ---------------------------------------------------------------- A.4 two-layer attention editor, A.5 oracle routing, A.6 unrolled L2 (K)
def _masked_softmax(sc, m):
    return torch.softmax(sc.masked_fill(~m.bool()[:, None, :], float('-inf')), -1)


class Att2LEditor(nn.Module):
    """A.4: z_i = h_i + W_o1 sum_j a1_ij W_v1 h_j; delta_i = b + U V h_i + W_o2 sum_j a2_ij W_v2 z_j (a1 from W_q1 h, W_k1 h; a2 from
    W_q2 z, W_k2 z); one head of 64 per layer; W_o1, W_o2 zero-initialised; U V rank 32."""
    def __init__(self, d, rank=32, dk=64):
        super().__init__(); self.dk = dk
        self.b = nn.Parameter(torch.zeros(d)); self.v = nn.Linear(d, rank, bias=False); self.u = nn.Linear(rank, d, bias=False)
        nn.init.normal_(self.v.weight, std=.01); nn.init.zeros_(self.u.weight)
        for l in ('1', '2'):
            for n_, (a, b_) in (('q', (d, dk)), ('k', (d, dk)), ('wv', (d, dk)), ('o', (dk, d))): setattr(self, n_ + l, nn.Linear(a, b_, bias=False))
            nn.init.zeros_(getattr(self, 'o' + l).weight)

    def layers(self, h, m):
        z0 = h.float(); a1 = _masked_softmax(self.q1(z0) @ self.k1(z0).transpose(-1, -2) / np.sqrt(self.dk), m)
        z = z0 + self.o1(a1 @ self.wv1(z0)); a2 = _masked_softmax(self.q2(z) @ self.k2(z).transpose(-1, -2) / np.sqrt(self.dk), m)
        return z0, z, a1, a2

    def attention(self, h, m):
        return self.layers(h, m)[3]                                                        # layer-2 attention (B, L, L)

    def forward(self, h, m):
        z0, z, a1, a2 = self.layers(h, m); delta = self.b + self.u(self.v(z0)) + self.o2(a2 @ self.wv2(z))
        return (z0 + delta * m[..., None]).to(h.dtype)


class OREditor(nn.Module):
    """A.5 (diagnostic): delta_i = b + U V h_i at every position; at the slot also W_o W_v h_src, src = position of the gold next (plus) /
    previous (minus) list name. Trained: W_v, W_o, U, V, b."""
    def __init__(self, d, rank=32, dk=64):
        super().__init__(); self.b = nn.Parameter(torch.zeros(d)); self.v = nn.Linear(d, rank, bias=False); self.u = nn.Linear(rank, d, bias=False)
        nn.init.normal_(self.v.weight, std=.01); nn.init.zeros_(self.u.weight); self.wv = nn.Linear(d, dk, bias=False); self.o = nn.Linear(dk, d, bias=False)
        nn.init.zeros_(self.o.weight)

    def forward(self, h, m, pos, src):
        z = h.float(); ar = torch.arange(len(h), device=h.device); delta = self.b + self.u(self.v(z))
        route = torch.zeros_like(z); route[ar, pos] = self.o(self.wv(z[ar, src])); delta = delta + route
        return (z + delta * m[..., None]).to(h.dtype)


class ORop:
    """Chain operator for OR: needs the gold input state j* (index into the participant list); src = npos[w, (j* +- 1) mod 3]."""
    needs_state = True

    def __init__(self, mod, pos, npos, sign):
        self.mod, self.pos, self.npos, self.sign = mod, pos.to(DEV), npos.to(DEV), sign

    def __call__(self, h, m, prev):
        ar = torch.arange(len(h), device=h.device); src = self.npos[ar, (prev.to(h.device) + self.sign) % 3]
        return self.mod(h, m, self.pos, src)


SIGN = {'plus': 1, 'minus': -1}


def k_pair(kind, dim, seed):
    torch.manual_seed(seed)
    if kind == 'Att2L': mk = lambda: Att2LEditor(dim)
    elif kind == 'OR': mk = lambda: OREditor(dim)
    else: return tokatt_pair(dim, seed, kind != 'Tok', heads=2 if kind == 'Att2' else 1)
    return nn.ModuleDict({op: mk() for op in ('plus', 'minus')}).to(DEV).float()


def name_positions(d, split):
    """(W, 3) token positions of the three list names (data/name_positions.json, from the BART tokenizer in d_audit.py)."""
    tab = read((ROOT if split in NEW_SPLITS else V7DIR if split in V7_SPLITS else V6DIR) / 'data/name_positions.json')[d]; return torch.tensor([tab[w['world_id']] for w in worlds5(d, split)])


def k_ops(kind, ed, pos=None, npos=None):
    if kind == 'OR': return {op: ORop(ed[op], pos, npos, SIGN[op]) for op in ('plus', 'minus')}
    return {op: ed[op] for op in ('plus', 'minus')}


def k_load(path, dim):
    c = load(path); ed = k_pair(c['kind'], dim, c['seed']); ed.load_state_dict(c['editor']); return c['kind'], ed.eval().requires_grad_(False)


def k_step(ed, kind, op, h, m, ctx=None, states=None):
    """One editor step; OR routes the slot to the list name of the gold next (plus) / previous (minus) participant of `states`."""
    if kind != 'OR': return ed[op](h, m)
    ar = torch.arange(len(h), device=h.device); src = ctx['npos'][ar, (states.to(h.device) + SIGN[op]) % 3]
    return ed[op](h, m, ctx['pos'], src)


def k_unrolled_loss(ed, kind, h, m, seq, ys, xs, ctx=None, states_seq=None):
    """A.6: (1/S) sum_s rel_l2(h_s, E(x_s)) along h_s = T_{op_s}(h_{s-1}); xs[s] = E(x_{s-1}); states_seq[s] = gold input states (OR)."""
    loss = 0.
    for k, (op, y, x) in enumerate(zip(seq, ys, xs)):
        h = k_step(ed, kind, op, h, m, ctx, states_seq[k] if states_seq is not None else None); loss = loss + rel_l2(h, y, x, m)
    return loss / len(seq)


def train_k(d, seed, kind, updates=4000, Sset=(1, 2, 3, 4), batch=16, lr=1e-3, clip=1.0, data=None):
    """A.6 / v5 A.4 unrolled L2 for the K editors (Tok, Att1, Att2, Att2L, OR): per update path type uniform over plus^S / minus^S /
    alternating, S uniform in Sset, batch 16 (world, start) from train; loss (1/S) sum_s rel_l2(h_s, E(x_s)) with E(x_{s-1}) in the
    denominator; gradient through the unrolled chain; AdamW 1e-3, clip 1. data: dict(H={s: (h, m)}, adv, pos, npos) overrides the train
    caches (self-test)."""
    if data is None:
        data = dict(H={s: (cache5('bart', d, 'train', s)['h'], cache5('bart', d, 'train', s)['m']) for s in S.states(d)}, adv=lambda s, op: S.advance(d, s, op))
        if kind == 'OR': data.update(pos=slots('bart', d, 'train'), npos=name_positions(d, 'train'))
    H, adv = data['H'], data['adv']; W = len(next(iter(H.values()))[0]); pool = [(i, s) for s in H for i in range(W)]; dim = next(iter(H.values()))[0].shape[-1]
    ed = k_pair(kind, dim, seed); opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []
    get = lambda its: torch.stack([H[s][0][i] for i, s in its]).to(DEV).float()
    for k in range(updates):
        pk = rng.choice(('plus', 'minus', 'alt')); S_ = rng.choice(list(Sset)); seq = path_seq(pk, S_); bt = [rng.choice(pool) for _ in range(batch)]
        m = torch.stack([H[s][1][i] for i, s in bt]).to(DEV); h = get(bt); cur = list(bt); idx = torch.tensor([i for i, _ in bt]); xs, ys, sts = [], [], []
        opt.zero_grad(set_to_none=True)
        for op in seq:
            nxt = [(i, adv(s, op)) for i, s in cur]; xs.append(get(cur)); ys.append(get(nxt)); sts.append(torch.tensor([s for _, s in cur])); cur = nxt
        ctx = dict(pos=data['pos'][idx].to(DEV), npos=data['npos'][idx].to(DEV)) if kind == 'OR' else None
        loss = k_unrolled_loss(ed, kind, h, m, seq, ys, xs, ctx, sts); assert torch.isfinite(loss); loss.backward()
        gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); opt.step()
        if (k + 1) % 50 == 0 or k == 0: hist.append(dict(step=k + 1, path=pk, S=S_, loss=float(loss), grad=float(gn)))
    ed.eval().requires_grad_(False)
    return ed, hist


# ---------------------------------------------------------------- v6 editor registry (all trained before the lock, PLAN B1 new rule 2)
# (unit, variant, backbone, domains, seeds, family, kind, updates)
NEW6 = [('M', 'C1n', 'bart', ['weekday-mt', 'month-mt', 'hour-mt'], SEEDS, 'CE', 'single', 600),
        ('M', 'C1n', 't5', ['month-mt'], SEEDS, 'CE', 'single', 600),
        ('M', 'SC3U4', 'bart', ['weekday-mt', 'month-mt', 'hour-mt'], SEEDS, 'state', 'slot_unrolled', 1200),
        ('C', 'C3n900', 'bart', ['weekday', 'month'], SEEDS, 'state', 'single', 900)]       # C3n300 / 450 / 600: snapshots of the 900 run
C3_SNAPS = (300, 450, 600)
K_NEW = [('OR', 4000, (1, 2, 3, 4), ['bind3', 'bind3fix']), ('Att2L', 4000, (1, 2, 3, 4), K_DOMAINS), ('Att2L', 8000, tuple(range(1, 9)), K_DOMAINS),
         ('Att1', 8000, tuple(range(1, 9)), K_DOMAINS)]


def k_name(kind, upd):
    return {('OR', 4000): 'ORU4', ('Att2L', 4000): 'Att2LU4', ('Att2L', 8000): 'Att2LU8', ('Att1', 8000): 'Att1U8'}[kind, upd]


def new6_path(bb, v, d, s, upd):
    return V6DIR / f'local/n6_{bb}_{v}_{d}_s{s}_u{upd}.pt'


# ================================================================ v7 (PLAN v7, appendix A): manifold quantities, U predictor, repairs,
# inverse pair, first-order errors, layer-2 ablations
def manifold(bb, d, split, rel_tol=1e-6, Cw=None):
    """A.1 per world: clean slot vectors Cw (W, N, dim, float64), centre mu (W, dim), orthonormal basis B (W, dim, N) of span{E_w(y) - mu}
    (directions with relative singular value < rel_tol zeroed; rank <= N - 1) and radius R (W,) = median_y ||E_w(y) - mu||."""
    Cw = slot_matrix(bb, d, split) if Cw is None else Cw.double()
    mu = Cw.mean(1); C = Cw - mu[:, None]; _, Sv, Vh = torch.linalg.svd(C, full_matrices=False)
    keep = (Sv > rel_tol * Sv[:, :1]).double(); B = Vh.transpose(1, 2) * keep[:, None, :]
    return dict(Cw=Cw, mu=mu, B=B, R=C.norm(dim=-1).median(1).values, rank=keep.sum(1))


def proj_in(man, hs):
    """Pi_w (hs - mu): in-span component (W, dim), float64."""
    x = hs.double() - man['mu'].to(hs.device); B = man['B'].to(hs.device)
    return torch.einsum('wdk,wk->wd', B, torch.einsum('wdk,wd->wk', B, x))


def rho_of(man, hs):
    """A.3: ||(I - Pi_w)(hs - mu_w)|| / R_w."""
    x = hs.double() - man['mu'].to(hs.device); return (x - proj_in(man, hs)).norm(dim=-1) / man['R'].to(hs.device)


def margin_raw(hs, Cw, P, lam):
    """A.2: S(y_hat) - max_{y != y_hat} S(y) with the locked vote scores; returns (argmax, m_raw)."""
    sc = vote_scores(plane_dists(hs.double(), Cw.to(hs.device), [(k, B.to(hs.device)) for k, B in P]), lam.to(hs.device))
    top = sc.topk(2, -1); return top.indices[:, 0], top.values[:, 0] - top.values[:, 1]


def margin_scale(man, P, lam):
    """M_w = median over the clean encodings E_w(y) of m_raw (A.2)."""
    Cw = man['Cw']; W, N, _ = Cw.shape
    vals = torch.stack([margin_raw(Cw[:, y], Cw, P, lam)[1] for y in range(N)], 1); return vals.median(1).values


def latent_stats(h, pos, man, P, lam, Mw):
    """Per world at one chain step: argmax of the fitted readout, normalised margin m, off-manifold rho."""
    ar = torch.arange(len(h), device=h.device); hs = h[ar, pos.to(h.device)]
    am, mr = margin_raw(hs, man['Cw'], P, lam); return am, mr / Mw.to(h.device), rho_of(man, hs)


def simulate_chain7(bb, d, ops, oplist, model, split=CONFIRM, start='world_start', man=None):
    """simulate_chain plus, per world and step, the normalised margin m and the off-manifold rho of the fitted readout (A.2, A.3)."""
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}
    state = [w['start_state'] for w in ws] if start == 'world_start' else [start] * n; s0 = list(state)
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots(bb, d, split).to(DEV); man = man or manifold(bb, d, split); P = model['P']; lam = model['lams']['full'].double(); Mw = margin_scale(man, P, lam)
    states, am, mm, rr = [], [], [], []
    for op in oplist:
        prev = torch.tensor(state, device=DEV); state = [S.advance(d, s, op) for s in state]; h = apply_op(ops[op], h, m, prev); states.append(state)
        a, mg, r = latent_stats(h, pos, man, P, lam, Mw); am.append(a.tolist()); mm.append([round(float(x), 6) for x in mg]); rr.append([round(float(x), 6) for x in r])
    T_ = lambda L: [list(x) for x in zip(*L)]
    return dict(world_ids=[w['world_id'] for w in ws], start=s0, states=T_(states), argmax=T_(am), m=T_(mm), rho=T_(rr))


def u_predict(sim, tau_m, tau_r, steps=None):
    """U (A.2-A.4): a step is predicted correct iff readout = gold, m >= tau_m and rho <= tau_r (None = no limit); a chain iff every step."""
    out = []
    for i in range(len(sim['world_ids'])):
        ok = True
        for t in range(steps or len(sim['states'][i])):
            ok &= sim['argmax'][i][t] == sim['states'][i][t] and (tau_m is None or sim['m'][i][t] >= tau_m) and (tau_r is None or sim['rho'][i][t] <= tau_r)
        out.append(bool(ok))
    return out


TAU_M = [None, 0., .1, .2, .3, .4, .5]                 # A.4 grid ('None' = no limit)
TAU_R = [None, .05, .1, .2, .3, .5, .75, 1.]


def repair_slot(kind, hs, man, g):
    """A.5 slot repairs (float64): SNAP h <- E_w(g); PROJ h <- mu + Pi(h - mu); PUSH h <- E_w(g) + (I - Pi)(h - mu)."""
    ar = torch.arange(len(hs), device=hs.device); Eg = man['Cw'].to(hs.device)[ar, g.to(hs.device)]; x = hs.double() - man['mu'].to(hs.device)
    if kind == 'SNAP': return Eg
    if kind == 'PROJ': return man['mu'].to(hs.device) + proj_in(man, hs)
    assert kind == 'PUSH'; return Eg + (x - proj_in(man, hs))


def repair(kind, h, m, pos, man, g, clean_g):
    """A.5 on a full latent h (W, L, dim): SNAP / PROJ / PUSH change the slot only; CTX sets every non-slot position to the clean encoding of
    state g (slot unchanged); SNAP+CTX is the clean encoding of g. clean_g: (h, m) of the clean encodings at g (same worlds, same order)."""
    hg, mg = clean_g; L = min(h.shape[1], hg.shape[1]); assert not m[:, L:].any() and not mg[:, L:].any() and bool((m[:, :L] == mg[:, :L]).all())
    ar = torch.arange(len(h), device=h.device); pos = pos.to(h.device)
    if kind == 'SNAP+CTX': out = hg[:, :L].to(h.device, h.dtype).clone(); return out, m[:, :L]
    out = h[:, :L].clone()
    if kind == 'CTX': hs = out[ar, pos].clone(); out = hg[:, :L].to(h.device, h.dtype).clone(); out[ar, pos] = hs; return out, m[:, :L]
    out[ar, pos] = repair_slot(kind, h[ar, pos], man, g).to(h.dtype); return out, m[:, :L]


class SlotRRRinv:
    """A.6: inverse of the S-RRR slot map y = h (I + L R) + b (row vectors): h = (y - b)(I - L (I_r + R L)^{-1} R) (Woodbury)."""
    def __init__(self, op):
        L, R, b = op.left.double(), op.right.double(), op.bias.double(); Ir = torch.eye(L.shape[1], dtype=L.dtype, device=L.device)
        K = Ir + R @ L; self.cond = float(torch.linalg.cond(K)); self.Minv = torch.eye(L.shape[0], dtype=L.dtype, device=L.device) - L @ torch.linalg.solve(K, R)
        self.bias = b; self.pos = getattr(op, 'pos', None)            # RRRop (token-wise, no slot position): the slot map only

    def slot(self, y):
        return (y.double() - self.bias.to(y.device)) @ self.Minv.to(y.device)

    def __call__(self, h, m):
        ar = torch.arange(len(h), device=h.device); out = h.clone(); out[ar, self.pos.to(h.device)] = self.slot(h[ar, self.pos.to(h.device)]).to(h.dtype); return out


def slot_map(op, hs):
    """The slot part of an S-RRR operator (float64)."""
    dev = op.left.device; x = hs.double().to(dev)
    return (x + x @ op.left.double() @ op.right.double() + op.bias.double()).to(hs.device)


def first_order_errors(man, opP, opM, d):
    """A.7 on clean inputs: e_P(x) = (I - Pi)[P(E(x)) - E(x+1)], e_M(x+1) = (I - Pi)[M(E(x+1)) - E(x)]; per world the cycle-sum ratio
    ||sum_x e_P(x)|| / sum_x ||e_P(x)|| and the alternating contrast median_x ||e_P(x) + e_M(x+1)|| / (||e_P(x)|| + ||e_M(x+1)||)."""
    Cw = man['Cw']; W, N, _ = Cw.shape; off = lambda v: (v - man['mu']) - proj_in(man, v)
    eP = torch.stack([off(slot_map(opP, Cw[:, x])) - off(Cw[:, (x + 1) % N]) for x in range(N)], 1)
    eM = torch.stack([off(slot_map(opM, Cw[:, (x + 1) % N])) - off(Cw[:, x]) for x in range(N)], 1)
    cyc = eP.sum(1).norm(dim=-1) / eP.norm(dim=-1).sum(1).clamp_min(1e-30)
    con = ((eP + eM).norm(dim=-1) / (eP.norm(dim=-1) + eM.norm(dim=-1)).clamp_min(1e-30)).median(1).values
    return dict(cycle_sum_ratio=cyc, alt_contrast=con, eP_norm=eP.norm(dim=-1).mean(1) / man['R'], eM_norm=eM.norm(dim=-1).mean(1) / man['R'])


class Att2LAblated(nn.Module):
    """A.8 layer-2 ablations without retraining: (a) 'uniform' a2 over non-pad positions, (b) 'self' a2_ii = 1, (c) 'drop' the layer-2 term."""
    def __init__(self, mod, mode):
        super().__init__(); self.mod, self.mode = mod, mode

    def forward(self, h, m):
        e = self.mod; z0, z, a1, a2 = e.layers(h, m); base = e.b + e.u(e.v(z0))
        if self.mode == 'drop': delta = base
        else:
            L = h.shape[1]
            if self.mode == 'uniform': a = (m.float() / m.float().sum(-1, keepdim=True))[:, None, :].expand(-1, L, -1)
            else: assert self.mode == 'self'; a = torch.eye(L, device=h.device)[None].expand(len(h), -1, -1)
            delta = base + e.o2(a @ e.wv2(z))
        return (z0 + delta * m[..., None]).to(h.dtype)


def new7_path(bb, v, d, s, upd):          # v7 editors (composability_mechanisms_v6)
    return V7DIR / f'local/n7_{bb}_{v}_{d}_s{s}_u{upd}.pt'
