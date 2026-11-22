"""Shared v3 machinery: backbones, caches, slot vectors, harmonic planes (A.1), vote model (A.2), surgery (A.3),
chain runner (A.4), RRR fitting and editor training."""
import itertools
import random
from functools import lru_cache
import torch
import torch.nn.functional as Fn
from symutil import *
import sym3_semantics as S
import sym3_evaluator as Ev

V2DIR = EXP / 'composability_mechanisms_v1'            # the v2 experiment ("composability_mechanisms_v1" directory)
BB_NAME = {'bart': 'bart', 't5': 't5gemma'}
CYC = ['weekday', 'month', 'compass', 'egoside']
T_DOMAINS = ['weekday', 'month', 'compass']
SHARD = 16
SHARDS = ROOT / 'results/shards'   # module attribute (patched only by the pre-lock smoke test)
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'


# ---------------------------------------------------------------- backbones
def engine3(bb):
    require_slurm(); source_path()
    from backend import Backend
    return Backend(BB_NAME[bb])


def mdtype(eng):
    return next(eng.model.parameters()).dtype


def dec(eng, h, m):
    return eng.decode(h.to(mdtype(eng)), m)


def logits3(eng, h, m, texts):
    return core().logits(eng, h.to(mdtype(eng)), m, texts)


# ---------------------------------------------------------------- worlds, caches, slots
def tmpl(d):
    return 3 if d in S.S1B else 0


def worlds3(d, split):
    if d in V1_DOMAINS and split in ('train', 'dev'):
        src = V1 / f'data/{d}/worlds.jsonl'
    elif d in ('pron3', 'name3', 'bind3') and split in ('train', 'dev'):
        src = V2DIR / f'data/{d}/worlds.jsonl'
    else:
        src = ROOT / f'data/{d}/worlds.jsonl'
    return [w for w in rows(src) if w['split'] == split]


def cpath(bb, d, split, s):
    if bb == 'bart' and d in V1_DOMAINS and split in ('train', 'dev'):
        return V1 / f'local/e1_{d}_{split}_t0_s{s}.pt'
    return ROOT / f'local/{bb}_{d}_{split}_t{tmpl(d)}_s{s}.pt'


@lru_cache(None)
def cache3(bb, d, split, s):
    return load(cpath(bb, d, split, s))


def slots(bb, d, split):
    """Long tensor (W,) of attribute-slot positions (template 0: constant; template 3: per world)."""
    sp = read(ROOT / 'data/slot_positions.json')[bb][d]; ws = worlds3(d, split)
    return torch.tensor([sp['all'] if 'all' in sp else sp['per_world'][w['world_id']] for w in ws])


def slot_matrix(bb, d, split):
    """(W, N, dim) float64 canonical slot vectors c_w(x), states in natural order."""
    pos = slots(bb, d, split); ar = torch.arange(len(pos))
    return torch.stack([cache3(bb, d, split, s)['h'][ar, pos].double() for s in S.states(d)], 1)


def lock_ok():
    p = ROOT / 'protocol.json'
    return p.exists() and read(p).get('locked') is True


@torch.no_grad()
def encode_split3(eng, bb, d, split, bs=32):
    if split == 'confirm3':
        assert lock_ok(), 'confirm3 encodings only after the lock'
    ws = worlds3(d, split); ids = [w['world_id'] for w in ws]; t = tmpl(d)
    for s in S.states(d):
        f = cpath(bb, d, split, s)
        if f.exists() and load(f)['world_ids'] == ids: continue
        hs = []; ms = []
        for i in range(0, len(ws), bs):
            h, m = eng.encode([S.render(w, s, t) for w in ws[i:i + bs]]); hs.append(h.float().cpu()); ms.append(m.cpu())
        h = torch.cat(hs); m = torch.cat(ms); n = int(m.sum(1).max())
        assert int(m[:, n:].sum()) == 0, 'right padding expected'
        save(f, dict(h=h[:, :n].contiguous(), m=m[:, :n].contiguous(), world_ids=ids))


# ---------------------------------------------------------------- harmonic planes (A.1)
def gram_planes(cbar):
    """cbar (N, dim) float64 -> list of (k, B_k dim x {1,2}) orthonormal across all planes (k ascending)."""
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


@lru_cache(None)
def planes(bb, d):
    return gram_planes(cbar_of(slot_matrix(bb, d, 'train')))


def amplitudes(bb, d):
    X = slot_matrix(bb, d, 'train'); cb = cbar_of(X); N = X.shape[1]; out = {}
    nxt = [S.advance(d, s, 'plus') for s in S.states(d)]
    for k, B in planes(bb, d):
        out[k] = dict(dim=B.shape[1], a=float(((cb @ B).square().sum(1).mean()).sqrt()),
                      s=float(((X[:, nxt] - X) @ B).norm(dim=-1).mean()))
    return out


# ---------------------------------------------------------------- vote model (A.2)
def plane_dists(H, Cw, P):
    """H (n, dim) slot vectors, Cw (n, N, dim) candidate canonical slots -> (n, N, K) per-plane squared distances."""
    diff = H[:, None, :] - Cw
    return torch.stack([(diff @ B).square().sum(-1) for _, B in P], -1)


def vote_scores(D, lam):
    return -(D * lam).sum(-1)


def fit_vote(D, y, mode, lam0, restarts=5, seed=BOOT_SEED):
    """Max likelihood lambda = softplus(theta). mode: full | equal | fund. Returns (lam (K,), nll)."""
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


# ---------------------------------------------------------------- idealized chains (A.2)
def path_ops(N, kind):
    return ['plus'] * (2 * N) if kind == 'plus' else ['minus'] * (2 * N) if kind == 'minus' else ['plus', 'minus'] * N


def ideal_R(Cw, P, lam, frozen, d):
    """R-hat over worlds x all starts for plus / minus / alt (2N steps). frozen: set of plane indices k.
    Computed exactly in plane coordinates (planes are mutually orthonormal): frozen planes keep the start's coordinates."""
    N = Cw.shape[1]; out = {}
    Z = [Cw @ B for _, B in P]                                             # each (W, N, dim_k)
    fr = [k in frozen for k, _ in P]
    for kind in ('plus', 'minus', 'alt'):
        ok_all = []
        for x0 in range(N):
            g = []; s = x0
            for op in path_ops(N, kind): s = S.advance(d, s, op); g.append(s)
            Dm = torch.stack([((Zk[:, [x0] * len(g)] if f else Zk[:, g])[:, :, None, :] - Zk[:, None]).square().sum(-1) for Zk, f in zip(Z, fr)], -1)
            yhat = vote_scores(Dm, lam).argmax(-1)                          # (W, T)
            ok_all.append((yhat == torch.tensor(g)).all(1))
        out[kind] = float(torch.cat(ok_all).double().mean())
    return out


def category(r):
    return 'composable' if r >= .90 else 'fail' if r <= .20 else 'partial'


def kstar(Cw, P, lam, d):
    ks = [k for k, _ in P]; dims = {k: B.shape[1] for k, B in P}; cands = []
    for n in range(1, len(ks) + 1):
        for K in itertools.combinations(ks, n):
            r = ideal_R(Cw, P, lam, set(ks) - set(K), d)
            if min(r.values()) >= .95: cands.append((sum(dims[k] for k in K), -min(r.values()), K, r))
    cands.sort()
    return dict(K=list(cands[0][2]), dim=cands[0][0], R_hat=cands[0][3]) if cands else dict(K=ks, dim=sum(dims.values()), R_hat=None)


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


class SlotOnly:
    def __init__(self, T, pos):
        self.T, self.pos = T, pos.to(DEV)
    def __call__(self, h, m):
        ar = torch.arange(len(h), device=h.device); h1 = h.clone(); h1[ar, self.pos] = self.T(h, m)[ar, self.pos]; return h1


def fit_plane_editor(X, B, d, op):
    """Least squares z' = A z + c on train slot coordinates for pairs (x, op(x)). X (W,N,dim) float64, B (dim, r)."""
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


# ---------------------------------------------------------------- chains (A.4)
def files(kind, bb, d, mp, method, tag, n):
    import lib3
    return [lib3.SHARDS / f'{kind}_{bb}_{d}_{mp}_{method}_{tag}_{lo:03d}.jsonl' for lo in range(0, n, SHARD)]


def write_shards(fs, recs):
    for j, f in enumerate(fs):
        write(f, [r for r in recs if j * SHARD <= r['index'] < (j + 1) * SHARD])


@torch.no_grad()
def run_chain(eng, bb, d, mp, method, ops, name, start, oplist, split='confirm3', model=None):
    """ops: {'plus','minus'} -> callable, or None for reencode. start: 'world_start' or a state.
    model: optional dict(P=planes, lams={name: lam}) to record vote-model argmax on the actual latent slot."""
    ws = worlds3(d, split); n = len(ws); fs = files('chain', bb, d, mp, method, name, n)
    if all(f.exists() for f in fs): return
    C = {s: cache3(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); idx = torch.arange(n)
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
def run_singles(eng, bb, d, mp, method, ops, split='confirm3'):
    ws = worlds3(d, split); n = len(ws); C = {s: cache3(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
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
def dev_single(eng, bb, d, mp, ops, split='dev'):
    ws = worlds3(d, split); C = {s: cache3(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); ok = []
    for s in S.states(d):
        for op in ('plus', 'minus'):
            try: y = S.advance(d, s, op, mp)
            except ValueError: continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); h = C[y]['h'].cuda() if ops is None else ops[op](h, m)
            ok += [Ev.score(o['text'], S.gold(w, y, t), w, o['ended'])['success'] for o, w in zip(dec(eng, h, m), ws)]
    return rate(ok)


@torch.no_grad()
def reencode_rate(eng, bb, d, splits=('train', 'dev')):
    ok = []
    for split in splits:
        ws = worlds3(d, split); t = tmpl(d)
        for s in S.states(d):
            c = cache3(bb, d, split, s)
            ok += [Ev.score(o['text'], S.gold(w, s, t), w, o['ended'])['success'] for o, w in zip(dec(eng, c['h'].cuda(), c['m'].cuda()), ws)]
    return rate(ok)


# ---------------------------------------------------------------- RRR fitting (v1/v2 procedure)
def fit_rrr3(bb, d, mp, ranks, ridge_grid=(1e-4, 1e-3, 1e-2, 1e-1), inner_seed=BOOT_SEED, inner_fit=80):
    if str(CWR) not in sys.path: sys.path.insert(0, str(CWR))
    import fit as F
    ws = worlds3(d, 'train'); C = {s: cache3(bb, d, 'train', s) for s in S.states(d)}
    order = list(range(len(ws))); random.Random(inner_seed).shuffle(order); fi, vi = sorted(order[:inner_fit]), sorted(order[inner_fit:])
    def paired(idx, op):
        X = []; Y = []
        for s in S.states(d):
            try: y = S.advance(d, s, op, mp)
            except ValueError: continue
            a, b = C[s], C[y]; assert torch.equal(a['m'][idx], b['m'][idx]); v = a['m'][idx].bool()
            X.append(a['h'][idx][v]); Y.append((b['h'][idx] - a['h'][idx])[v])
        return torch.cat(X).double(), torch.cat(Y).double()
    final = {}; info = {}
    for op in ('plus', 'minus'):
        A = paired(fi, op); Bv = paired(vi, op); st = F.sufficient(*A); sc = {}
        for rel in ridge_grid:
            for r, f in F.solve(st, rel, ranks).items(): sc[rel, r] = F.mse(*Bv, f)
        chosen = {r: min(ridge_grid, key=lambda rel: sc[rel, r]) for r in ranks}
        AL = paired(list(range(len(ws))), op); sa = F.sufficient(*AL); sols = {rel: F.solve(sa, rel, ranks) for rel in set(chosen.values())}
        for r, rel in chosen.items():
            f = sols[rel][r]; final[op, r] = {k: f[k] for k in ('left', 'right', 'bias')} | dict(relative_ridge=rel, rank=r)
            info[f'{op}_{r}'] = rel
    return final, info


# ---------------------------------------------------------------- editor training (v1 configuration)
def token_mse(h, y, m):
    return ((h - y).square() * m[..., None]).sum((1, 2)) / (m.sum(1) * h.shape[-1])


def train_editor(eng, bb, d, mp, group, seed, updates=600, l2_weight=1.0, init_rrr=None, batch=8, micro=2, lr=1e-3, clip=1.0):
    source_path(); from backend import editors
    ws = worlds3(d, 'train'); C = {s: cache3(bb, d, 'train', s) for s in S.states(d)}; t = tmpl(d); dt = mdtype(eng)
    pool = {op: [(i, s) for s in S.states(d) for i in range(len(ws)) if _legal(d, s, op, mp)] for op in ('plus', 'minus')}
    stack = lambda its: (torch.stack([C[s]['h'][i] for i, s in its]).cuda(), torch.stack([C[s]['m'][i] for i, s in its]).cuda())
    scale = {}
    with torch.no_grad():
        for op, its in pool.items():
            v = []
            for lo in range(0, len(its), 64):
                part = its[lo:lo + 64]; h, m = stack(part); y, _ = stack([(i, S.advance(d, s, op, mp)) for i, s in part]); v.append(token_mse(h, y, m))
            scale[op] = float(torch.cat(v).mean())
    ed = editors(eng.d, seed)
    if init_rrr is not None:
        with torch.no_grad():
            for op in ('plus', 'minus'):
                f = init_rrr[op]; b = f['left'].double() @ f['right'].double(); u, s_, vh = torch.linalg.svd(b, full_matrices=False)
                ed[op].v.weight.copy_((u[:, :16] * s_[:16].sqrt()).T.float()); ed[op].u.weight.copy_((s_[:16].sqrt()[:, None] * vh[:16]).T.float()); ed[op].b.copy_(f['bias'])
    opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []
    for k in range(updates):
        op = ('plus', 'minus')[k % 2]; bt = [rng.choice(pool[op]) for _ in range(batch)]; opt.zero_grad(set_to_none=True); tot = dict(ce=0., l2=0., loss=0.)
        for lo in range(0, batch, micro):
            part = bt[lo:lo + micro]; h, m = stack(part); tgt = [(i, S.advance(d, s, op, mp)) for i, s in part]; y, ym = stack(tgt); assert torch.equal(m, ym)
            e = ed[op](h, m); ce = eng.ce(e.to(dt), m, [S.render(ws[i], s, t) for i, s in tgt])[0].mean(); l2 = torch.zeros((), device='cuda')
            if group == 'C3': l2 = token_mse(e, y, m).mean() / scale[op]
            loss = ce + l2_weight * l2; assert torch.isfinite(loss); (loss * len(part) / batch).backward()
            for kk, v in (('ce', ce), ('l2', l2), ('loss', loss)): tot[kk] += float(v.detach()) * len(part) / batch
        gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); assert torch.isfinite(gn)
        assert all(x.grad is None for x in eng.model.parameters()); opt.step(); hist.append(dict(step=k + 1, op=op, grad=float(gn), **tot))
    ed.eval().requires_grad_(False)
    return ed, hist, scale


def _legal(d, s, op, mp):
    try: S.advance(d, s, op, mp); return True
    except ValueError: return False


def load_editor(eng, path):
    source_path(); from backend import editors
    c = load(path); ed = editors(eng.d, c.get('seed', 42)); ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)


# ---------------------------------------------------------------- unit block (v2 algebra.unit_block, copied)
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


# ---------------------------------------------------------------- probe (v2 s3, torch multinomial logistic regression)
def logreg(X, y, C, K, iters=300):
    W = torch.zeros(X.shape[1], K, dtype=torch.float64, device=X.device, requires_grad=True); b = torch.zeros(K, dtype=torch.float64, device=X.device, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], max_iter=iters, line_search_fn='strong_wolfe', tolerance_grad=1e-9)
    def closure():
        opt.zero_grad(); loss = Fn.cross_entropy(X @ W + b, y) + (W ** 2).sum() / (2 * C * len(X)); loss.backward(); return loss
    opt.step(closure)
    return W.detach(), b.detach()


def probe(bb, d, CS=(0.01, 0.1, 1.0, 10.0)):
    """Train on canonical train slot vectors (labels = state), C by 5-fold world CV; returns info and predict(slot (n,dim))."""
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
def write_metrics(eng, bb, d, mp, T, predict, split='confirm3', m4=True):
    """M1-M3 (v2 definitions) and the A.5 transplant classification for a plus operator T under mapping mp."""
    ws = worlds3(d, split); n = len(ws); st = S.states(d); N = len(st); t = tmpl(d); pos = slots(bb, d, split).to(DEV); ar = torch.arange(n, device=DEV)
    H = {s: cache3(bb, d, split, s)['h'].to(DEV) for s in st}; M = cache3(bb, d, split, st[0])['m'].to(DEV); v = M[..., None]
    legal = [s for s in st if _legal(d, s, 'plus', mp)]; g = {s: S.advance(d, s, 'plus', mp) for s in legal}
    Wr = {s: (T(H[s], M) - H[s]) * v for s in legal}; Wc = {s: (H[g[s]] - H[s]) * v for s in legal}
    pc = torch.stack([cosrows(Wr[a], Wr[b]) for i, a in enumerate(legal) for b in legal[i + 1:]], 1).mean(1).cpu().numpy()
    cw = torch.stack([cosrows(Wr[s], Wc[s]) for s in legal], 1).mean(1).cpu().numpy()
    src = tgt = oth = 0
    for s in legal:
        pr = predict((H[s] + Wr[s])[ar, pos]); src += sum(p == s for p in pr); tgt += sum(p == g[s] for p in pr); oth += sum(p not in (s, g[s]) for p in pr)
    tot = src + tgt + oth
    out = dict(M1=boot_mean(pc), M2=dict(median=float(np.median(cw)), ci95=boot_stat(lambda i: np.median(cw[i]), n)['ci95'], mean=float(cw.mean())),
               M3=dict(source=src / tot, target=tgt / tot, other=oth / tot, n=tot))
    if m4:
        from collections import Counter
        c = Counter()
        for s in legal:
            for s2 in legal:
                if s2 == s: continue
                for o, w in zip(dec(eng, H[s2] + Wr[s], M), ws):
                    ps, _ = Ev.parse_state(o['text'], d, S.people(w) if d in S.S1B else None)
                    nat = S.advance(d, s2, 'plus') if _legal(d, s2, 'plus', 'natural') else None
                    if ps == g[s2] and Ev.score(o['text'], S.gold(w, g[s2], t), w, o['ended'])['success']: c['relative'] += 1
                    elif ps == g[s]: c['absolute'] += 1
                    elif ps == s2: c['null'] += 1
                    elif ps is not None and ps == nat and nat != g[s2]: c['natural_successor'] += 1
                    elif ps is None: c['unparsable'] += 1
                    else: c['other'] += 1
        tot = sum(c.values()); out['M4'] = {k: x / tot for k, x in c.items()} | dict(n=tot)
    out['writes'] = {s: Wr[s].cpu() for s in legal} if m4 == 'keep' else None
    return out


# ---------------------------------------------------------------- protocol / shards
LOCKED3 = ['symutil.py', 'sym3_semantics.py', 'sym3_evaluator.py', 'lib3.py', 'd_encode.py', 'h_chains.py', 'b_run.py', 'n_run.py', 't_run.py',
           'a_run.py', 'algebra.py', 'analyze.py', 'job_gpu.slurm', 'job_cpu.slurm']


def verify_protocol3():
    p = read(ROOT / 'protocol.json'); assert p.get('locked') is True, 'protocol not locked'
    for k, v in p['sources'].items(): assert sha(ROOT / k) == v, f'locked source changed: {k}'
    for k, v in p['data'].items(): assert sha(REPO / k) == v, f'locked data changed: {k}'
    return p


def chain_records(bb, d, mp, method, path):
    out = []
    import lib3
    for f in sorted(lib3.SHARDS.glob(f'chain_{bb}_{d}_{mp}_{method}_{path}_*.jsonl')): out += rows(f)
    return out


def chain_rate(bb, d, mp, method, path, k):
    rs = chain_records(bb, d, mp, method, path); ws = {r['world_id'] for r in rs}
    ok = {r['world_id']: r['trajectory_success'] for r in rs if r['step'] == k}; assert len(ok) == len(ws)
    return rate(list(ok.values()))
