"""v9 synthetic self-tests (CPU, before the lock; PLAN v9 appendix A.6 items 1-4; item 5, the decoder-only identity check, runs in
do_selftest.py on GPU). Output: results/selftest9.json (pass iff every check holds).
1. Ideal harmonic codes (planes k = 1..3 in a random orthonormal basis, elliptical with axis ratio 0.6, world offsets): the global mean
   difference B1a has no state component at the slot; the readout-indexed shift B1c maps every E_w(x) to E_w(x + 1) and E_w(x - 1)
   exactly; the analytic rotation B5 does the same.
2. LoReFT: after 300 steps of the training optimiser (AdamW, weight decay 0) on a random objective, and in every trained LoReFT editor,
   the rows of R stay orthonormal (max |R R^T - I| < 1e-4). (With AdamW's default weight decay the parametrisation breaks; training uses 0.)
3. The random-horizon sampler (rng.choice over 1..2N with the training seed) is uniform within 1% over 200 000 draws.
4. The learned-baseline logistic regression recovers a known rule (y = 1 iff the first feature > 0) with >= 0.95 grouped-CV accuracy."""
import random
from cells9 import *


def ideal(W=6, N=7, dim=24, L=5, pos=2, seed=0):
    g = torch.Generator().manual_seed(seed); Q = torch.linalg.qr(torch.randn(dim, dim, generator=g, dtype=torch.float64))[0]
    planes = [(k, Q[:, 2 * (k - 1):2 * k]) for k in (1, 2, 3)]; mu = torch.randn(W, dim, generator=g, dtype=torch.float64)
    Cw = torch.zeros(W, N, dim, dtype=torch.float64)
    for x in range(N):
        for k, B in planes:
            th = torch.tensor(2 * np.pi * k * x / N, dtype=torch.float64); Cw[:, x] += (torch.stack([th.cos() * (1.5 / k), th.sin() * (0.9 / k)]) @ B.T)
    Cw += mu[:, None]; base = torch.randn(W, L, dim, generator=g, dtype=torch.float64)
    H = {x: (lambda h: (h.__setitem__((slice(None), pos), Cw[:, x]), h)[1])(base.clone()) for x in range(N)}
    return Cw, mu, planes, H, torch.full((W,), pos, dtype=torch.long), torch.ones(W, L)


def main():
    require_slurm(); chk = {}; N = 7
    Cw, mu, P, H, pos, m = ideal(N=N); d = 'weekday'
    Ds = {y: (H[(y + 1) % N] - H[y]).mean(0) for y in range(N)}; Dg = sum(Ds.values()) / N
    chk['B1a_no_state_component'] = float(Dg[2].abs().max()) < 1e-10
    model = dict(P=P, lams=dict(full=torch.ones(3, dtype=torch.float64)))
    rs = {op: ReadoutShift({y: v.float() for y, v in Ds.items()}, d, op, pos, Cw, model) for op in ('plus', 'minus')}
    err = max(float((rs[op](H[x].float().to(DEV), m.to(DEV)).double().cpu() - H[S.advance(d, x, op)]).abs().max()) for op in rs for x in range(N))
    chk['B1c_exact'] = err < 1e-4
    man = dict(Cw=Cw, mu=mu); rot = {op: Rotation(man, P, N, op, pos) for op in ('plus', 'minus')}
    err = max(float((rot[op](H[x].to(DEV), m.to(DEV)).double().cpu()[:, 2] - H[S.advance(d, x, op)][:, 2]).abs().max()) for op in rot for x in range(N))
    chk['B5_exact'] = err < 1e-8
    torch.manual_seed(1); e = LoReFTEditor(32); opt = torch.optim.AdamW(e.parameters(), lr=1e-3, weight_decay=0); x = torch.randn(4, 5, 32); y = torch.randn(4, 5, 32)
    for _ in range(300): opt.zero_grad(); ((e(x, torch.ones(4, 5)) - y) ** 2).mean().backward(); opt.step()     # the training optimiser (weight decay 0)
    R = e.R.weight.detach(); chk['loreft_orthogonal'] = float((R @ R.T - torch.eye(16)).abs().max()) < 1e-4
    dev = []                                                                                                    # every trained LoReFT editor
    for f in sorted((ROOT / 'local').glob('n9_*_LoReFT*_s*.pt')):
        c = load(f); dim = c['editor']['plus.W.weight'].shape[1]; ed = make_editors('loreft', dim, c['seed']).cpu(); ed.load_state_dict(c['editor'])
        dev += [float((ed[op].R.weight.detach() @ ed[op].R.weight.detach().T - torch.eye(16)).abs().max()) for op in ('plus', 'minus')]
    chk['loreft_trained_orthogonal'] = bool(dev) and max(dev) < 1e-4
    rng = random.Random(45); Sset = list(range(1, 2 * 12 + 1)); cnt = np.bincount([rng.choice(Sset) for _ in range(200000)], minlength=25)[1:]
    chk['urand_uniform'] = float(np.abs(cnt / cnt.sum() - 1 / len(Sset)).max()) < .01
    g = np.random.default_rng(0); X = torch.tensor(g.normal(size=(2000, 4))); yv = (X[:, 0] > 0).long(); grp = np.arange(2000) // 10; fold = grp % 5; pred = np.zeros(2000, bool)
    for k in range(5):
        tr, te = fold != k, fold == k; W_, b = logreg(X[tr], yv[tr], 1.0, 2); pred[te] = ((X[te] @ W_ + b).argmax(-1) == 1).numpy()
    chk['logreg_recovers_rule'] = float((pred == yv.numpy().astype(bool)).mean()) >= .95
    res = dict(checks=chk, pass_=all(chk.values())); dump(ROOT / 'results/selftest9.json', res); print(json.dumps(res), flush=True)


if __name__ == '__main__':
    main()
