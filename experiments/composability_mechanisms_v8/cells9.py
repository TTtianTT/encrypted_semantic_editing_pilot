"""v9 cells (PLAN v9 sections 3-4; members listed in advance, design rule 5) and the new operators of units B1 and B5.
Splits: template 0 dev / confirm7 (weekday, month); month-nat dev / confirm8. Paths: plus, minus, alternating, 2N steps; unit B4: 4N steps.
Units and members (family 'CE' = trained through the decoder only; 'state' = closed form or objective with a state target; 'steer' = B1):
- base: RRR-16 (template 0) and S-RRR_nat (v8 GN operator, month-nat) - the G9-0 gate;
- B1 (weekday, month; both backbones): B1a global mean difference, B1b single-pair mean difference (x0 = state 0), B1c readout-indexed;
- B2: LoReFT-C1, LoReFT-C3U4 (seeds 45-47); B3: Full-C1, MLP-C1 (seeds 45-47); both backbones, weekday and month;
- B4: U8, U16, Urand (BART weekday / month), U8 (T5Gemma month); seeds 45-47;
- B5: analytic rotation (weekday, month template 0 and month-nat; both backbones);
- S: C1 and C3-U4, seeds 45-49 (BART weekday / month, T5Gemma month).
Only admitted editors enter (results/train9_<bb>_<part>.json); an editor that could not learn is reported and counted as failing."""
from lib9 import *

PATHS = lambda N: dict(plus=['plus'] * (2 * N), minus=['minus'] * (2 * N), alt=['plus', 'minus'] * N)
PATHS4 = lambda N: dict(plus=['plus'] * (4 * N), minus=['minus'] * (4 * N), alt=['plus', 'minus'] * (2 * N))
SIGN = {'plus': 1, 'minus': -1}


def mean_diffs(bb, d, x0=None):
    """Position-aligned mean differences on train (appendix A.1): {state y: (L, dim) mean_w [E_w(y + 1) - E_w(y)]} over the positions where
    the world's mask is set (template 0: same tokens across states of a world)."""
    out = {}
    for y in S.states(d):
        a, b = cache5(bb, d, 'train', y), cache5(bb, d, 'train', S.advance(d, y, 'plus')); m = a['m'].float()[..., None]
        out[y] = ((b['h'].float() - a['h'].float()) * m).sum(0) / m.sum(0).clamp_min(1)
    return out


def fit_len(D, L):
    return D[:L] if D.shape[0] >= L else Fn.pad(D, (0, 0, 0, L - D.shape[0]))


class Shift:
    """B1a / B1b: h <- h + sign * Delta at every (masked) position."""
    def __init__(self, D, sign):
        self.D, self.sign = D.to(DEV), sign
    def __call__(self, h, m):
        return (h.float() + self.sign * fit_len(self.D, h.shape[1])[None] * m[..., None].float()).to(h.dtype)


class ReadoutShift:
    """B1c: per step read y_hat with the locked slot readout (vote model, the world's clean codes) and add Delta(y_hat) for plus, or
    -Delta(y_hat - 1) for minus (the mean difference of the step that ends in y_hat - 1)."""
    def __init__(self, Ds, d, op, pos, Cw, model):
        self.Ds = {y: v.to(DEV) for y, v in Ds.items()}; self.d, self.op, self.pos, self.Cw, self.model = d, op, pos.to(DEV), Cw.to(DEV), model
    def __call__(self, h, m):
        y = readout(h, m, self.pos, self.Cw, self.model)['full']; L = h.shape[1]
        D = torch.stack([fit_len(self.Ds[yy], L) if self.op == 'plus' else -fit_len(self.Ds[S.advance(self.d, yy, 'minus')], L) for yy in y])
        return (h.float() + D * m[..., None].float()).to(h.dtype)


class Rotation:
    """B5 (appendix A.4): on the slot only, in every harmonic plane k (train planes): whiten the world's clean 2-D coordinates, rotate by
    sign * 2 pi k / N in the world's own orientation (the sign that maps its clean state x to x + 1), de-whiten; components outside the
    planes unchanged. One-dimensional (Nyquist) planes: z -> -z. Uses the world's clean codes (diagnostic, like the readout)."""
    def __init__(self, man, P, N, op, pos):
        self.pos = pos.to(DEV); self.sign = SIGN[op]; C = (man['Cw'] - man['mu'][:, None]).double(); self.mu = man['mu'].double().to(DEV); self.parts = []
        for k, B in P:
            B = B.double(); Z = C @ B                                                                  # (W, N, dim_k)
            if B.shape[1] == 1: self.parts.append((B.to(DEV), None, None, None)); continue
            Sig = Z.transpose(1, 2) @ Z / N; ev, V = torch.linalg.eigh(Sig); sq = V @ torch.diag_embed(ev.clamp_min(1e-12).sqrt()) @ V.transpose(1, 2)
            isq = V @ torch.diag_embed(ev.clamp_min(1e-12).rsqrt()) @ V.transpose(1, 2); Zw = Z @ isq.transpose(1, 2)
            th = torch.atan2(Zw[..., 1], Zw[..., 0]); dth = torch.remainder(th.roll(-1, 1) - th + np.pi, 2 * np.pi) - np.pi
            orient = torch.where((dth * (2 * np.pi * k / N)).sum(1) >= 0, 1.0, -1.0).double()                # per world
            self.parts.append((B.to(DEV), sq.to(DEV), isq.to(DEV), (orient * 2 * np.pi * k / N).to(DEV)))
    def __call__(self, h, m):
        ar = torch.arange(len(h), device=h.device); hs = h[ar, self.pos].double(); c = hs - self.mu; new = hs.clone()
        for B, sq, isq, ang in self.parts:
            z = c @ B
            if sq is None: new = new + (-2 * z) @ B.T; continue
            a = self.sign * ang; R = torch.stack([torch.stack([a.cos(), -a.sin()], -1), torch.stack([a.sin(), a.cos()], -1)], -2)
            zw = (isq @ z[..., None]); z2 = (sq @ (R @ zw))[..., 0]; new = new + (z2 - z) @ B.T
        out = h.clone(); out[ar, self.pos] = new.to(h.dtype); return out


def admitted(bb, part):
    f = ROOT / f'results/train9_{bb}_{part}.json'
    return {k: v for k, v in (read(f).items() if f.exists() else []) if not k.startswith('_') and isinstance(v, dict) and v.get('admitted')}


def all_trained(bb, part):
    f = ROOT / f'results/train9_{bb}_{part}.json'
    return {k: v for k, v in (read(f).items() if f.exists() else []) if not k.startswith('_') and isinstance(v, dict)}


def editor_ops9(eng, path):
    ed = load_editor9(eng, path); return {op: ed[op] for op in ('plus', 'minus')}


CE_VARIANTS = ('C1', 'LoReFTC1', 'FullC1', 'MLPC1', 'U8', 'U16', 'Urand')
T0 = ['weekday', 'month']


def cells9(eng, bb, split):
    """[(unit, family, domain, method, ops-or-thunk, paths)] for one backbone and split kind ('dev' or 'confirm')."""
    sp = lambda d: ('dev' if split == 'dev' else 'confirm8' if d == S.NAT else 'confirm7'); out = []
    for d in T0:
        out.append(('base', 'state', d, 'RRR16', lambda d=d: base_ops(bb, d), PATHS))
    g = read(V8DIR / f'results/gates_nat_{bb}.json')['GN']; f = load(V8DIR / f'local/{bb}_srrr_{S.NAT}.pt'); r = int((g['base'] or 'SRRR16')[4:])
    out.append(('base', 'state', S.NAT, 'SRRRnat', lambda: {op: SlotRRRop(f[op, r], slots(bb, S.NAT, sp(S.NAT))) for op in ('plus', 'minus')}, PATHS))
    for d in T0:
        Ds = mean_diffs(bb, d); Dg = sum(Ds.values()) / len(Ds); D0 = Ds[S.states(d)[0]]; pos = slots(bb, d, sp(d))
        out.append(('B1', 'steer', d, 'B1a', {op: Shift(Dg, SIGN[op]) for op in ('plus', 'minus')}, PATHS))
        out.append(('B1', 'steer', d, 'B1b', {op: Shift(D0, SIGN[op]) for op in ('plus', 'minus')}, PATHS))
        out.append(('B1', 'steer', d, 'B1c', lambda d=d, Ds=Ds, pos=pos: {op: ReadoutShift(Ds, d, op, pos, slot_matrix(bb, d, sp(d)), vote_model(bb, d)) for op in ('plus', 'minus')}, PATHS))
    for part, unit in (('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'), ('S', 'S')):
        for key, st in admitted(bb, part).items():
            v, d, s = key.split('/'); fam = 'CE' if v in CE_VARIANTS else 'state'
            out.append((unit, fam, d, f'{v}_{s}', lambda p=ROOT / st['path']: editor_ops9(eng, p), PATHS4 if unit == 'B4' else PATHS))
    for d in T0 + [S.NAT]:
        N = len(S.states(d))
        out.append(('B5', 'state', d, 'Rot', lambda d=d, N=N: (lambda man, pos: {op: Rotation(man, planes(bb, d), N, op, pos) for op in ('plus', 'minus')})(manifold(bb, d, sp(d)), slots(bb, d, sp(d))), PATHS))
    return out
