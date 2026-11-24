"""E1 (CPU, exploratory; plan change of 2026-11-25, PLAN.md end): do the fitted operators contract or expand off-manifold directions?
Objects: v6's GM operator S-RRR-16 plus (P), minus (M) and the exact inverse P^-1 (Woodbury) on the four (backbone, multi-template domain)
combinations, v7 confirm7 held-out-template worlds; control: the template-0 RRR-16 base operator (BART weekday / month, T5Gemma month,
confirm7). Both operators act token-wise, so the slot evolves by its own linear map A (row convention: x -> x A + b).
Gain: along the F_empty one-way plus and alternating chains (2N steps, the operators of each path), the off-manifold residual
r_t = (I - Pi_w)(h_t - mu_w) of the slot and g = ||(I - Pi_w)(r_t A)|| / ||r_t|| for A in {A_P, A_M, A_P^-1}; median over worlds and steps per
(backbone, domain, path). Spectrum: singular values of A restricted to its action subspace (the row space of the right factor R) after
removing the components in the harmonic planes, for P, M and P^-1. Reading: g_P, g_M < 1 and g_P^-1 > 1 support 'the fitted operators
contract off-manifold directions and the exact inverse expands them'; otherwise 'unexplained'. Output: results/e1.json."""
import time
from lib8 import *


def lin(op):
    """Linear part A (dim x dim, float64) of an S-RRR / RRR operator (x -> x + x L R + b) or of SlotRRRinv."""
    if isinstance(op, SlotRRRinv): return op.Minv.double().cpu()
    L, R = op.left.double().cpu(), op.right.double().cpu(); return torch.eye(L.shape[0], dtype=torch.float64) + L @ R


def offproj(man, x):
    return (x - man['mu']) - proj_in(man, x)


def gains(man, slot0, ops, path, A):
    """Iterate the slot under the path's operators; per step and world g = ||off(r A)|| / ||r|| with r the off-manifold residual."""
    h = slot0.clone(); out = {k: [] for k in A}
    for op in path:
        h = slot_map(ops[op], h); r = offproj(man, h); nr = r.norm(dim=-1)
        for k, a in A.items():
            g = r @ a; g = g - torch.einsum('wdk,wk->wd', man['B'], torch.einsum('wdk,wd->wk', man['B'], g))      # (I - Pi_w)(r A)
            out[k].append((g.norm(dim=-1) / nr.clamp_min(1e-12)))
    return {k: float(torch.stack(v).median()) for k, v in out.items()}


def spectrum(op, P, A):
    R = op.right.double().cpu(); B = torch.cat([b.double().cpu() for _, b in P], 1)
    Q = torch.linalg.qr((R.T - B @ (B.T @ R.T)))[0]; return torch.linalg.svdvals(Q.T @ A @ Q).tolist()


def main():
    require_slurm(); t0 = time.time(); out = dict(cells={}, spectra={})
    combos = [(bb, d, 'slot') for bb in ('bart', 't5') for d in M_DOMAINS[bb]] + [('bart', 'weekday', 'rrr'), ('bart', 'month', 'rrr'), ('t5', 'month', 'rrr')]
    for bb, d, kind in combos:
        split = 'confirm7'; N = len(S.states(d)); pos = slots(bb, d, split); man = manifold(bb, d, split)
        if kind == 'slot': ops = m_base_ops(bb, d, read(V6DIR / f'results/gates_{bb}.json'), pos)
        else: ops = base_ops(bb, d)
        for op in ops.values(): op.left, op.right, op.bias = op.left.cpu(), op.right.cpu(), op.bias.cpu()
        inv = SlotRRRinv(ops['plus']); A = dict(P=lin(ops['plus']), M=lin(ops['minus']), Pinv=lin(inv))
        ws = worlds5(d, split); C = man['Cw']; slot0 = torch.stack([C[i, w['start_state']] for i, w in enumerate(ws)])
        for path, ol in (('plus', ['plus'] * (2 * N)), ('alt', ['plus', 'minus'] * N)):
            out['cells'][f'{bb}/{d}/{kind}/{path}'] = gains(man, slot0, ops, ol, A)
        P = planes(bb, d)
        out['spectra'][f'{bb}/{d}/{kind}'] = {k: spectrum(ops['plus'], P, a) for k, a in A.items()}
        g = out['cells'][f'{bb}/{d}/{kind}/plus']; print('E1', bb, d, kind, {k: round(v, 3) for k, v in g.items()}, flush=True)
    sl = [v for k, v in out['cells'].items() if '/slot/' in k]
    out['reading'] = 'supports contraction of the fitted operators and expansion by the inverse' if all(v['P'] < 1 and v['M'] < 1 and v['Pinv'] > 1 for v in sl) else 'unexplained'
    out['seconds'] = time.time() - t0; dump(ROOT / 'results/e1.json', out); print(out['reading'], flush=True)


if __name__ == '__main__':
    main()
