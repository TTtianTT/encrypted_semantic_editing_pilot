"""Multi-template calibration (GPU, dev of the training templates only, before the lock; PLAN B5: re-calibration with the v3 procedure). --backbone bart|t5.
The v3 procedure (v4 calib.py): plane-substitution probes on dev decoded and parsed (A.6 template parser), vote model full / equal /
fundamental-only by maximum likelihood. Planes: v5's local/planes_<bb>_<d>.pt (train, training templates pooled). Domains: those kept by GM (gates.py)."""
import time
from lib6 import *


@torch.no_grad()
def probes(eng, bb, d, P):
    ws = worlds5(d, 'dev'); n = len(ws); N = len(S.states(d)); Cw = slot_matrix(bb, d, 'dev'); pos = slots(bb, d, 'dev')
    C = {s: cache5(bb, d, 'dev', s) for s in S.states(d)}; dim = Cw.shape[-1]; H = []; meta = []
    for x in S.states(d):
        for k, B in P:
            Pk = B @ B.T; Pc = torch.eye(dim, dtype=torch.float64) - Pk
            for kind, Proj in (('single', Pk), ('complement', Pc)):
                for mshift in range(1, N):
                    y_true = (x + mshift) % N; slot = Cw[:, x] + (Cw[:, y_true] - Cw[:, x]) @ Proj
                    for w in range(n): meta.append((w, x, k, kind, mshift)); H.append(slot[w])
    H = torch.stack(H); out_y = []; bs = 256 if bb == 'bart' else 128
    for lo in range(0, len(H), bs):
        part = meta[lo:lo + bs]; hs = H[lo:lo + bs]
        h = torch.stack([C[x]['h'][w] for w, x, *_ in part]).cuda(); m = torch.stack([C[x]['m'][w] for w, x, *_ in part]).cuda()
        ar = torch.arange(len(part)); pp = pos[[w for w, *_ in part]]; h[ar, pp] = hs.float().cuda()
        for o, (w, x, *_) in zip(dec(eng, h, m), part): out_y.append(Ev.parse_state(o['text'], d, gold=S.gold(ws[w], x))[0])
    return H, meta, out_y, Cw


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    gates = read(ROOT / f'results/gates_{bb}.json'); res = dict(backbone=bb, domains={})
    for d in gates['M_domains']:
        P = planes(bb, d); N = len(S.states(d)); Cw = slot_matrix(bb, d, 'dev')
        H, meta, ys, _ = probes(eng, bb, d, P)
        ok = [i for i, y in enumerate(ys) if y is not None]; y = torch.tensor([ys[i] for i in ok])
        Cand = torch.stack([Cw[meta[i][0]] for i in ok]); Dm = plane_dists(H[ok], Cand, P)
        nxt = [(s + 1) % N for s in range(N)]
        dpair = torch.stack([((Cw[:, nxt] - Cw) @ B).square().sum(-1).reshape(-1) for _, B in P], 1)
        lam0 = 1 / dpair.median(0).values; Ed = dpair.mean(0); models = {}
        for mode in ('full', 'equal', 'fund'):
            lam, nll = fit_vote(Dm, y, mode, lam0)
            models[mode] = dict(lam=lam.tolist(), nll=nll, probe_accuracy=float((vote_scores(Dm, lam).argmax(-1) == y).double().mean()), omega=omega(lam, Ed))
        by_type = {}
        for (w, x, k, kind, ms), yy in zip(meta, ys):
            c = by_type.setdefault(f'{kind}_k{k}', dict(n=0, unparsable=0, source=0, moved=0, other=0))
            c['n'] += 1; c['unparsable' if yy is None else 'source' if yy == x else 'moved' if yy == (x + ms) % N else 'other'] += 1
        res['domains'][d] = dict(N=N, planes=[dict(k=k, dim=B.shape[1]) for k, B in P], models=models, probes=len(ys), parsable=len(ok), probe_outcomes=by_type,
                                 lambda0=lam0.tolist(), mean_step_dist=Ed.tolist(), planes_sha256=sha(V5DIR / f'local/planes_{bb}_{d}.pt'))
        print(d, 'omega', [round(v, 3) for v in models['full']['omega']], 'acc', {m: round(v['probe_accuracy'], 3) for m, v in models.items()}, flush=True)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/calib_mt_{bb}.json', res)


if __name__ == '__main__':
    main()
