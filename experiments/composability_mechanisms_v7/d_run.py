"""Unit D measurements (GPU, after the lock; exploratory; PLAN v7 C4, appendix B.2). Gemma 2 2B IT, month template 0, the layer chosen in
d_prep.py; evaluation on the 160 confirm7 worlds (first evaluation for this model); every step decoded once only to score it.
- Rank threshold: S-RRR-r on the slot latent (fitted on train, r in {N-4, ..., N, 16}); one-way plus R_2N.
- Freeze signatures on S-RRR-16: F{1}, F_not1, F_empty; plus and alternating R_2N (planes from the train latents, A.1 of v3).
- Spectrum: per-plane one-step change s_k and amplitude a_k of the confirm7 slot latents.
- Latent readout vs decoding: equal-weight plane readout (lambda_k = 1 / median one-step distance on train; no decoder calibration for this
  model, recorded) at every step of every chain above; per-world agreement of 'readout = gold at every step' with the decoded success.
- CE slot editors (d_C1_s50-52): R_1, R_2, R_2N (plus) and D (step-1 readout != step-1 decoded state).
Output: results/d_run.json."""
import time
from lib8 import fit_srrr_X, next_idx, gram_planes, cbar_of, plane_dists, vote_scores, slot_pair, lock_ok, worlds5
from dlib import *

D = 'month'


def chain(eng, ws, pos, X0, step_fn, oplist, readout, bs=48):
    """X0 (W, d) start latents; step_fn(op, V) -> V'. Per world: decoded trajectory success per step, readout per step, decoded state at step 1."""
    n = len(ws); state = [w['start_state'] for w in ws]; V = X0.clone(); ok = [True] * n; R = []; reads = []; dec1 = None
    for k, op in enumerate(oplist):
        state = [S.advance(D, s, op) for s in state]; V = step_fn(op, V); reads.append(readout(V)); outs = []
        for lo in range(0, n, bs):
            outs += eng.generate([S.render(w, w['start_state'], 0) for w in ws[lo:lo + bs]], pos[lo:lo + bs], LAYER, V[lo:lo + bs].float())
        succ = [success(o, w, s) for o, w, s in zip(outs, ws, state)]; ok = [a and b for a, b in zip(ok, succ)]; R.append(float(np.mean(ok)))
        if k == 0: dec1 = [Ev.parse_state(o['text'], D)[0] for o in outs]
    gold = [[S.advance(D, s0, op) for s0 in [w['start_state'] for w in ws]] for op in oplist[:1]]
    return dict(R=R, ok=ok, reads=reads, dec1=dec1)


def main():
    require_slurm(); assert lock_ok(); t0 = time.time(); prep = read(ROOT / 'results/d_prep.json'); assert prep['continue_']
    global LAYER; LAYER = prep['layer']; eng = DEngine(); N = len(S.states(D))
    L = {sp: load(ROOT / f'local/d_latents_{sp}.pt') for sp in ('train', 'confirm7')}; Xtr = L['train']['latents'][LAYER]; Xc = L['confirm7']['latents'][LAYER]
    ws = worlds5(D, 'confirm7'); pos = L['confirm7']['pos']; assert [w['world_id'] for w in ws] == L['confirm7']['world_ids']
    P = gram_planes(cbar_of(Xtr)); nxt = {op: next_idx(D, op) for op in ('plus', 'minus')}
    dpair = torch.stack([((Xtr[:, nxt['plus']] - Xtr) @ B).square().sum(-1).reshape(-1) for _, B in P], 1); lam = 1 / dpair.median(0).values
    readout = lambda V: vote_scores(plane_dists(V.double(), Xc, P), lam).argmax(-1).tolist()
    start = torch.stack([Xc[i, w['start_state']] for i, w in enumerate(ws)])
    def lin(f): L_, R_, b = (f[k].double() for k in ('left', 'right', 'bias')); return lambda V: V + V @ L_ @ R_ + b
    ranks = list(range(N - 4, N + 1)) + [16]; fits, _ = fit_srrr_X(Xtr, nxt, ranks); out = dict(layer=LAYER, revision=eng.revision, planes=[k for k, _ in P], lambda_equal_weight=lam.tolist())
    def run(name, ops, paths):
        for pth in paths:
            ol = ['plus'] * (2 * N) if pth == 'plus' else ['plus', 'minus'] * N
            c = chain(eng, ws, pos, start, lambda op, V: ops[op](V), ol, readout)
            gold = []; st = [w['start_state'] for w in ws]
            for op in ol: st = [S.advance(D, s, op) for s in st]; gold.append(st)
            pred = [all(c['reads'][t][i] == gold[t][i] for t in range(len(ol))) for i in range(len(ws))]
            Dv = [c['reads'][0][i] != c['dec1'][i] for i in range(len(ws)) if c['dec1'][i] is not None]
            out[f'{name}/{pth}'] = dict(R1=c['R'][0], R2=c['R'][1], R2N=c['R'][-1], A=None, agree=float(np.mean([p == o for p, o in zip(pred, c['ok'])])), pred_rate=float(np.mean(pred)),
                                        D=float(np.mean(Dv)) if Dv else None)
            print('D', name, pth, round(c['R'][-1], 3), flush=True)
    for r in ranks: run(f'SRRR{r}', {op: lin(fits[op, r]) for op in ('plus', 'minus')}, ['plus'])
    Bs = {n: torch.cat([B for k, B in P if k in ks], 1) for n, ks in (('F_{1}', {1}), ('F_not1', {k for k, _ in P} - {1}))}
    base = {op: lin(fits[op, 16]) for op in ('plus', 'minus')}
    def frz(B): return {op: (lambda V, op=op: (lambda V1: V1 - ((V1 - V) @ B) @ B.T)(base[op](V))) for op in ('plus', 'minus')}
    run('F_empty', base, ['plus', 'alt'])
    for n, B in Bs.items(): run(n, frz(B), ['plus', 'alt'])
    out['spectrum'] = {k: dict(s=float(((Xc[:, nxt['plus']] - Xc) @ B).norm(dim=-1).mean()), a=float(((cbar_of(Xc) @ B).square().sum(1).mean()).sqrt())) for k, B in P}
    for s in (50, 51, 52):
        c = load(ROOT / f'local/d_C1_s{s}.pt'); ed = slot_pair(eng.d, s); ed.load_state_dict(c['editor']); ed = ed.eval().requires_grad_(False).cpu().double()
        run(f'C1_s{s}', {op: (lambda V, op=op: V + ed[op].b + ed[op].u(ed[op].v(V))) for op in ('plus', 'minus')}, ['plus'])
    out['resources'] = eng.resources(); out['seconds'] = time.time() - t0; dump(ROOT / 'results/d_run.json', out)


if __name__ == '__main__':
    main()
