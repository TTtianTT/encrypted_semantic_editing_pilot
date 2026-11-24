"""A.8 synthetic self-test (CPU; must pass before the lock).
1. S-RRR and E_all on synthetic multi-template slots (slot = shared cyclic code in three harmonic planes + a template offset and a world
   offset in the orthogonal complement): fitted on 6 training templates, applied to 3 held-out templates, they recover the rotation:
   relative error of the predicted step vs the true step < 1e-3 (S-RRR-16; relative ridge >= 1e-4 shrinks slightly) and < 1e-6 (E_all).
2. Context readout: on synthetic slot / context distances with labels drawn from softmax(-sum_k lam_k D_k - lam_ctx D_ctx), the ML fit
   recovers lam_ctx within 0.05.
3. Att2L on a two-hop synthetic pointer task (three list names, the slot holds the current name, the target is the next list name;
   v4 construction, the slot holds only the slot-coded current name; held-out = fresh sequences): held-out relative L2 <= 0.05. One layer
   cannot do the second hop: its best strategy (cancel the
   current name, average the other M - 1 list names) has relative L2 (M - 2) / (2 (M - 1)) = 0.25 for M = 3, so the plan's 'one-layer >= 0.5'
   is unattainable in principle (DEVIATIONS); tested instead: Att1 >= 0.2 (its floor is 0.25) and Tok >= 0.45 (its floor is 0.5).
4. OR on the same task (routing given): held-out relative L2 <= 0.01.
5. Unrolled L2: with S = 1 the loss (k_unrolled_loss, used by train_k) equals the single-step relative L2 exactly (Att2L and OR)."""
import time
import lib6 as L
from lib6 import *


def t_slot_ops(seed=0):
    g = torch.Generator().manual_seed(seed); dim, N, Wt = 40, 7, 30
    E, _ = torch.linalg.qr(torch.randn(dim, dim, generator=g, dtype=torch.float64)); Bs = [E[:, 2 * k:2 * k + 2] for k in range(3)]; comp = E[:, 6:]
    amp = [3.0, 1.5, 0.8]
    code = lambda s: sum(a * B @ torch.tensor([np.cos(2 * np.pi * (k + 1) * s / N), np.sin(2 * np.pi * (k + 1) * s / N)], dtype=torch.float64) for k, (a, B) in enumerate(zip(amp, Bs)))
    def worlds(tids):
        X = []
        for t in tids:
            off = comp @ torch.randn(comp.shape[1], generator=torch.Generator().manual_seed(100 + t), dtype=torch.float64) * 2
            for _ in range(Wt):
                wo = comp @ torch.randn(comp.shape[1], generator=g, dtype=torch.float64) * .3
                X.append(torch.stack([code(s) + off + wo for s in range(N)]))
        return torch.stack(X)
    Xtr, Xte = worlds(range(6)), worlds(range(6, 9)); nxt = {'plus': [(s + 1) % N for s in range(N)], 'minus': [(s - 1) % N for s in range(N)]}
    fits, _ = fit_srrr_X(Xtr, nxt, [16]); out = {}
    for op in nxt:
        f = fits[op, 16]; pred = Xte + Xte @ f['left'].double() @ f['right'].double() + f['bias'].double(); tgt = Xte[:, nxt[op]]
        out[f'srrr_{op}'] = float((pred - tgt).norm() / (tgt - Xte).norm())
    P = gram_planes(cbar_of(Xtr)); ea, B = fit_eall_X(Xtr, P, nxt)
    for op in nxt:
        A, c = ea[op]; z = Xte @ B; pred = Xte + (z @ A.T + c - z) @ B.T; tgt = Xte[:, nxt[op]]
        out[f'eall_{op}'] = float((pred - tgt).norm() / (tgt - Xte).norm())
    out['planes'] = len(P); out['pass'] = all(v < 1e-3 for k, v in out.items() if k.startswith('srrr')) and all(v < 1e-6 for k, v in out.items() if k.startswith('eall')) and len(P) == 3
    return out


def t_ctx(seed=0):
    g = torch.Generator().manual_seed(seed); n, N, K = 40000, 7, 3; lam = torch.tensor([2.0, 1.0, 0.5], dtype=torch.float64); true = 0.8
    Ds = torch.rand(n, N, K, generator=g, dtype=torch.float64) * 2; Dc = torch.rand(n, N, generator=g, dtype=torch.float64) * 2
    p = torch.softmax(-(Ds * lam).sum(-1) - true * Dc, -1); y = torch.multinomial(p, 1, generator=g)[:, 0]
    fit = fit_lam_ctx(Ds, Dc, y, lam); return dict(true=true, fitted=fit['lam_ctx'], err=abs(fit['lam_ctx'] - true), pass_=abs(fit['lam_ctx'] - true) < .05)


def pointer2(n_seq, seed, d=128, c_var=.75, e_var=.25):
    """Two-hop pointer task on v4's construction (v4 selftest.pointer_data): length 8, position markers everywhere, list names at positions
    1-3 (list subspace; names in one sequence share a random component, name_i = c + e_i, so token-wise prediction fails), filler noise at
    0, 4, 6, 7. Unlike v4, the slot (position 5) holds only the slot-coded current name name_j (no position marker): the editor must find
    the current name in the list, then take the next one. Target slot: slot-coded name_{j+1} (plus) / name_{j-1} (minus)."""
    g = torch.Generator().manual_seed(seed); E, _ = torch.linalg.qr(torch.randn(d, d, generator=torch.Generator().manual_seed(1234), dtype=torch.float64))
    Lsub, SN, POS, FIL = E[:, :16], E[:, 16:32], E[:, 32:40], E[:, 43:]
    c = torch.randn(n_seq, 1, 16, generator=g, dtype=torch.float64) * np.sqrt(c_var / 16); e = torch.randn(n_seq, 3, 16, generator=g, dtype=torch.float64) * np.sqrt(e_var / 16)
    names = c + e; base = torch.zeros(n_seq, 8, d, dtype=torch.float64) + POS.T[None]
    for p in (0, 4, 6, 7): base[:, p] += torch.randn(n_seq, FIL.shape[1], generator=g, dtype=torch.float64) * .2 @ FIL.T
    for i in range(3): base[:, 1 + i] += names[:, i] @ Lsub.T
    H = {}
    for j in range(3):
        h = base.clone(); h[:, 5] += names[:, j] @ SN.T; H[j] = (h.float(), torch.ones(n_seq, 8, dtype=torch.long))
    return dict(H=H, adv=lambda s, op: (s + SIGN[op]) % 3, pos=torch.full((n_seq,), 5), npos=torch.tensor([1, 2, 3]).repeat(n_seq, 1))


@torch.no_grad()
def heldout_rel(ed, kind, data):
    tot = []; pos = data['pos'].to(DEV); npos = data['npos'].to(DEV)
    for j in range(3):
        for op in ('plus', 'minus'):
            h, m = (x.to(DEV) for x in data['H'][j]); y = data['H'][data['adv'](j, op)][0].to(DEV)
            e = k_step(ed, kind, op, h.float(), m, dict(pos=pos, npos=npos), torch.full((len(h),), j)); tot.append(float(rel_l2(e, y, h.float(), m)))
    return float(np.mean(tot))


def t_k(updates=20000, lr=3e-3, batch=64):
    """Same optimiser for every editor (AdamW lr 3e-3, batch 64, 20000 single-step updates): the plan setting (lr 1e-3, batch 16) leaves Att2L on
    the one-layer plateau of this task (DEVIATIONS); the test checks that the architecture can learn the second hop."""
    tr = pointer2(2000, 11); te = pointer2(500, 12); out = dict(optimiser=dict(updates=updates, lr=lr, batch=batch))
    for kind in ("Att2L", "Att1", "Tok", "OR"):
        ed, hist = train_k(None, 42, kind, updates=updates, Sset=(1,), lr=lr, batch=batch, data=tr); out[kind] = dict(heldout_rel_l2=heldout_rel(ed, kind, te), train_last=hist[-1]["loss"])
    out['pass'] = out['Att2L']['heldout_rel_l2'] <= .05 and out['Att1']['heldout_rel_l2'] >= .2 and out['Tok']['heldout_rel_l2'] >= .45 and out['OR']['heldout_rel_l2'] <= .01
    return out


def t_unrolled_s1():
    data = pointer2(8, 3); out = {}
    for kind in ('Att2L', 'OR'):
        ed = k_pair(kind, 128, 5)
        with torch.no_grad():
            for p in ed.parameters(): p.add_(0.05 * torch.randn_like(p))
            h, m = (x.to(DEV) for x in data['H'][0]); y = data['H'][1][0].to(DEV); ctx = dict(pos=data['pos'].to(DEV), npos=data['npos'].to(DEV)); st = torch.zeros(8, dtype=torch.long)
            a = k_unrolled_loss(ed, kind, h.float(), m, ['plus'], [y], [h.float()], ctx, [st]); b = rel_l2(k_step(ed, kind, 'plus', h.float(), m, ctx, st), y, h.float(), m)
        out[kind] = float((a - b).abs())
    out['pass'] = all(v == 0.0 for v in out.values()); return out


def main():
    require_slurm(); t0 = time.time(); torch.manual_seed(0); res = {}
    res['A8_1_slot_ops'] = t_slot_ops(); print(1, res['A8_1_slot_ops'], flush=True)
    res['A8_2_ctx'] = t_ctx(); print(2, res['A8_2_ctx'], flush=True)
    res['A8_3_4_K'] = t_k(); print('3-4', res['A8_3_4_K'], flush=True)
    res['A8_5_unrolled'] = t_unrolled_s1(); print(5, res['A8_5_unrolled'], flush=True)
    res['pass'] = all(v.get('pass', v.get('pass_')) for v in res.values() if isinstance(v, dict)); res['seconds'] = time.time() - t0
    res['sources'] = {f: sha(ROOT / f) for f in ('lib6.py', 'selftest.py')}; dump('results/selftest.json', res); assert res['pass'], 'selftest failed'


if __name__ == '__main__':
    main()
