"""Section 6.2 calibration (GPU, dev only, before the lock): plane-substitution probes, vote model (full / equal / fundamental-only),
derived predictions R-hat for every section 6.3 condition, and K*. --backbone bart|t5."""
import time
from lib3 import *


def conditions(P):
    ks = [k for k, _ in P]; cond = {'F_empty': set(), **{f'F_{{{k}}}': {k} for k in ks}}
    cond['F_not1'] = set(ks) - {1}
    cond['E_all'] = set(); cond['E_{1}'] = set(ks) - {1}
    return cond


@torch.no_grad()
def probes(eng, bb, d, P):
    ws = worlds3(d, 'dev'); n = len(ws); N = len(S.states(d)); Cw = slot_matrix(bb, d, 'dev'); pos = slots(bb, d, 'dev')
    C = {s: cache3(bb, d, 'dev', s) for s in S.states(d)}; dim = Cw.shape[-1]; Pall = {k: B for k, B in P}
    recs = []; H = []; meta = []
    for x in S.states(d):
        for k, B in P:
            Pk = B @ B.T; Pc = torch.eye(dim, dtype=torch.float64) - Pk
            for kind, Proj in (('single', Pk), ('complement', Pc)):
                for mshift in range(1, N):
                    y_true = (x + mshift) % N
                    slot = Cw[:, x] + (Cw[:, y_true] - Cw[:, x]) @ Proj
                    for w in range(n): meta.append((w, x, k, kind, mshift)); H.append(slot[w])
    H = torch.stack(H); out_y = []; bs = 256 if bb == 'bart' else 128
    for lo in range(0, len(H), bs):
        part = meta[lo:lo + bs]; hs = H[lo:lo + bs]
        h = torch.stack([C[x]['h'][w] for w, x, *_ in part]).cuda(); m = torch.stack([C[x]['m'][w] for w, x, *_ in part]).cuda()
        ar = torch.arange(len(part)); pp = pos[[w for w, *_ in part]]
        h[ar, pp] = hs.float().cuda()
        for o, (w, *_r) in zip(dec(eng, h, m), part): out_y.append(Ev.parse_state(o['text'], d)[0])
    return H, meta, out_y, Cw


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine3(bb)
    doms = CYC if bb == 'bart' else read(ROOT / 'results/gates_t5.json')['T_domains']; res = dict(backbone=bb, domains={})
    for d in doms:
        P = planes(bb, d); save(f'local/planes_{bb}_{d}.pt', P); N = len(S.states(d))
        H, meta, ys, Cw = probes(eng, bb, d, P)
        ok = [i for i, y in enumerate(ys) if y is not None]; y = torch.tensor([ys[i] for i in ok])
        Cand = torch.stack([Cw[meta[i][0]] for i in ok]); Dm = plane_dists(H[ok], Cand, P)
        nxt = [(s + 1) % N for s in range(N)]
        dpair = torch.stack([((Cw[:, nxt] - Cw) @ B).square().sum(-1).reshape(-1) for _, B in P], 1)     # dev d_k(c(x), c(x+1))
        lam0 = 1 / dpair.median(0).values; Ed = dpair.mean(0)
        models = {}
        for mode in ('full', 'equal', 'fund'):
            lam, nll = fit_vote(Dm, y, mode, lam0)
            models[mode] = dict(lam=lam.tolist(), nll=nll, probe_accuracy=float((vote_scores(Dm, lam).argmax(-1) == y).double().mean()), omega=omega(lam, Ed))
        lam = torch.tensor(models['full']['lam'], dtype=torch.float64)
        cond = conditions(P); derived = {}
        for name, frozen in cond.items():
            r = ideal_R(Cw, P, lam, frozen, d); derived[name] = dict(frozen=sorted(frozen), R_hat=r, category={k: category(v) for k, v in r.items()})
        ks = kstar(Cw, P, lam, d)
        derived['E_Kstar'] = dict(K=ks['K'], frozen=sorted(set(k for k, _ in P) - set(ks['K'])), R_hat=ks['R_hat'],
                                  category={k: category(v) for k, v in ks['R_hat'].items()} if ks['R_hat'] else None)
        by_type = {}
        for (w, x, k, kind, ms), yy in zip(meta, ys):
            key = f'{kind}_k{k}'; c = by_type.setdefault(key, dict(n=0, unparsable=0, source=0, moved=0, other=0))
            c['n'] += 1; c['unparsable' if yy is None else 'source' if yy == x else 'moved' if yy == (x + ms) % N else 'other'] += 1
        res['domains'][d] = dict(N=N, planes=[dict(k=k, dim=B.shape[1]) for k, B in P], probes=len(ys), parsable=len(ok), probe_outcomes=by_type,
                                 lambda0=lam0.tolist(), mean_step_dist=Ed.tolist(), models=models, derived=derived, Kstar=ks,
                                 planes_sha256=sha(ROOT / f'local/planes_{bb}_{d}.pt'))
        print(d, 'omega', [round(v, 3) for v in models['full']['omega']], 'acc', {m: round(v['probe_accuracy'], 3) for m, v in models.items()},
              'K*', ks['K'], flush=True)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0
    dump(f'results/calib_{bb}.json', res)


if __name__ == '__main__':
    main()
