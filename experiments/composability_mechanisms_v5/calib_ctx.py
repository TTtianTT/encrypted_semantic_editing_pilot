"""Context-readout calibration (GPU, BART, weekday and month, train + dev only, before the lock; PLAN B6, appendix A.3).
Q_ctx: top N - 1 principal components of the state-demeaned context representations of the train worlds (every non-pad non-slot
position, pooled over states) -> local/ctx_bart_<d>.pt. lam_ctx: maximum likelihood on dev context-substitution probes with the slot
weights fixed at the locked vote model (v4 protocol 'full' lams, the v5 vote_models): for every dev world, state x and shift m = 1..N-1,
(a) context swap: slot of E(x), every other position of E(x + m); (b) complement: slot of E(x + m), context of E(x). Each probe is decoded
and its state parsed; unparsable probes are dropped. Writes results/calib_ctx_bart.json."""
import time
from lib6 import *


@torch.no_grad()
def probes(eng, d):
    bb = 'bart'; ws = worlds5(d, 'dev'); n = len(ws); N = len(S.states(d)); pos = slots(bb, d, 'dev')
    C = {s: cache5(bb, d, 'dev', s) for s in S.states(d)}; meta = []
    for x in S.states(d):
        for ms in range(1, N):
            for kind in ('ctx_swap', 'slot_swap'):
                for w in range(n): meta.append((w, x, (x + ms) % N, kind))
    ys = []; Hs = []; bs = 256
    for lo in range(0, len(meta), bs):
        part = meta[lo:lo + bs]; ar = torch.arange(len(part)); pp = pos[[w for w, *_ in part]]
        base = torch.stack([C[x2 if k == 'ctx_swap' else x]['h'][w] for w, x, x2, k in part]); slot_src = torch.stack([C[x if k == 'ctx_swap' else x2]['h'][w] for w, x, x2, k in part])
        h = base.clone(); h[ar, pp] = slot_src[ar, pp]; m = torch.stack([C[x]['m'][w] for w, x, *_ in part])
        for o, (w, x, x2, k) in zip(dec(eng, h.cuda(), m.cuda()), part): ys.append(Ev.parse_state(o['text'], d)[0])
        Hs.append(h)
    return meta, ys, torch.cat(Hs)


def main():
    require_slurm(); t0 = time.time(); eng = engine5('bart'); res = dict(backbone='bart', domains={})
    for d in C_DOMAINS:
        N = len(S.states(d)); Q, expl = ctx_basis('bart', d); save(f'local/ctx_bart_{d}.pt', dict(Q=Q, explained=expl))
        meta, ys, H = probes(eng, d); ok = [i for i, y in enumerate(ys) if y is not None]
        P = planes('bart', d); Cw = slot_matrix('bart', d, 'dev'); pos = slots('bart', d, 'dev'); c = ctx_model_data('bart', d, 'dev', Q)
        widx = torch.tensor([meta[i][0] for i in ok]); Hk = H[ok]; ar = torch.arange(len(ok))
        Dslot = plane_dists(Hk[ar, pos[widx]].double(), Cw[widx], P); Dctx = torch.cat([ctx_dists(Hk[lo:lo + 512], c, widx[lo:lo + 512]) for lo in range(0, len(ok), 512)])
        y = torch.tensor([ys[i] for i in ok]); lam_full = vote_lams('bart', d)['full']
        fit = fit_lam_ctx(Dslot, Dctx, y, lam_full)
        acc_slot = float((vote_scores(Dslot, lam_full).argmax(-1) == y).double().mean())
        acc_ctx = float((vote_scores(Dslot, lam_full) - fit['lam_ctx'] * Dctx).argmax(-1).eq(y).double().mean())
        outc = {}
        for (w, x, x2, k), yy in zip(meta, ys):
            o = outc.setdefault(k, dict(n=0, unparsable=0, slot_state=0, context_state=0, other=0)); o['n'] += 1
            sl, cx = (x, x2) if k == 'ctx_swap' else (x2, x)
            o['unparsable' if yy is None else 'slot_state' if yy == sl else 'context_state' if yy == cx else 'other'] += 1
        res['domains'][d] = dict(N=N, ctx_dim=N - 1, explained_variance=expl, probes=len(ys), parsable=len(ok), outcomes=outc, probe_accuracy_slot_only=acc_slot,
                                 probe_accuracy_slot_ctx=acc_ctx, lam_slot_full=lam_full.tolist(), ctx_sha256=sha(ROOT / f'local/ctx_bart_{d}.pt'), **fit)
        print(d, {k: v for k, v in res['domains'][d].items() if k not in ('explained_variance', 'lam_slot_full')}, flush=True)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump('results/calib_ctx_bart.json', res)


if __name__ == '__main__':
    main()
