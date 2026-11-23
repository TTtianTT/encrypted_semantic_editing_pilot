"""Section 6.2 calibration (GPU, dev only, before the lock). --backbone bart|t5.
weekday/month: v3 calibration reused as is (same dev worlds, same planes; results/calib_<bb>.json of v3). hour/compass8/season: the v3
procedure (plane-substitution probes on dev, vote model full / equal / fundamental-only by maximum likelihood). For every V domain kept
by GB: derived categories R-hat_2N for F{empty}, F{1}, F{not 1}, F{j} (plus / minus / alt; idealized states on dev), idealized
per-step prediction curves A_t for F{1} and F{not 1} (plus), and the V3 discriminability pre-check (appendix A.6)."""
import time
from lib4 import *


@torch.no_grad()
def probes(eng, bb, d, P):
    ws = worlds4(d, 'dev'); n = len(ws); N = len(S.states(d)); Cw = slot_matrix(bb, d, 'dev'); pos = slots(bb, d, 'dev')
    C = {s: cache4(bb, d, 'dev', s) for s in S.states(d)}; dim = Cw.shape[-1]; H = []; meta = []
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
        for o in dec(eng, h, m): out_y.append(Ev.parse_state(o['text'], d)[0])
    return H, meta, out_y, Cw


def conditions(P):
    ks = [k for k, _ in P]; cond = {'F_empty': set(), **{f'F_{{{k}}}': {k} for k in ks}}
    cond['F_not1'] = set(ks) - {1}
    return cond


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine4(bb)
    gates = read(ROOT / f'results/gates_{bb}.json'); v3 = read(V3DIR / f'results/calib_{bb}.json')['domains']; res = dict(backbone=bb, domains={})
    for d in gates['V_domains']:
        P = planes(bb, d); save(f'local/planes_{bb}_{d}.pt', P); N = len(S.states(d)); Cw = slot_matrix(bb, d, 'dev')
        if d in ('weekday', 'month'):
            src = v3[d]; models = src['models']; extra = dict(source='v3 calibration reused (composability_mechanisms_v2/results/calib_%s.json)' % bb,
                                                               probe_outcomes=src['probe_outcomes'], lambda0=src['lambda0'], mean_step_dist=src['mean_step_dist'])
            v3P = load(V3DIR / f'local/planes_{bb}_{d}.pt'); assert all(torch.equal(a[1], b[1]) for a, b in zip(P, v3P))
        else:
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
            extra = dict(source='calibrated here (v3 procedure)', probes=len(ys), parsable=len(ok), probe_outcomes=by_type, lambda0=lam0.tolist(), mean_step_dist=Ed.tolist())
        lam = torch.tensor(models['full']['lam'], dtype=torch.float64); derived = {}
        for name, frozen in conditions(P).items():
            r = ideal_R(Cw, P, lam, frozen, d); derived[name] = dict(frozen=sorted(frozen), R_hat=r, category={k: category(v) for k, v in r.items()})
        curves = {name: {kind: ideal_At(Cw, P, lam, fr, d, kind) for kind in ('plus', 'minus', 'alt')}
                  for name, fr in (('F_{1}', {1}), ('F_not1', set(k for k, _ in P) - {1}))}
        res['domains'][d] = dict(N=N, planes=[dict(k=k, dim=B.shape[1]) for k, B in P], models=models, derived=derived, ideal_At=curves,
                                 planes_sha256=sha(ROOT / f'local/planes_{bb}_{d}.pt'), **extra)
        print(d, 'omega', [round(v, 3) for v in models['full']['omega']], {n: v['category'] for n, v in derived.items()}, flush=True)
    # V3 discriminability pre-check (cells: domain x F{j}, j >= 2 x {plus, minus})
    cells = {}
    for d, v in res['domains'].items():
        for k in [p['k'] for p in v['planes'] if p['k'] >= 2]:
            for path in ('plus', 'minus'): cells[f'{bb}/{d}/F_{{{k}}}/{path}'] = v['derived'][f'F_{{{k}}}']['category'][path]
    res['V3_cells'] = dict(H_ms=cells, scorable_vs_fund=[c for c, v in cells.items() if v != 'composable'], scorable_vs_flat=[c for c, v in cells.items() if v != 'fail'])
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0
    dump(f'results/calib_{bb}.json', res)


if __name__ == '__main__':
    main()
