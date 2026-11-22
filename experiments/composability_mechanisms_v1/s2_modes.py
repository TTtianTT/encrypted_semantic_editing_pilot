"""S2 (GPU): harmonic decomposition of the slot error along the one-way plus chain (natural cyclic maps, ranks < N-1, plus
RRR-16 as baseline), and oracle patching of the harmonics missing from the operator's unit block (exploratory)."""
import time
import torch
from symutil import *
import sym2_semantics as S
import sym2_evaluator as Ev
from algebra import unit_block


def planes(d):
    """Harmonic planes P_k (k = 1..floor(N/2)) at the template-0 slot, from train canonical encodings (natural state order)."""
    pos = slot_pos(d, 0); st = S.states(d); N = len(st)
    H = torch.stack([cache2(d, 'train', s)['h'][:, pos].double() for s in st], 1)   # (W, N, dim)
    cbar = (H - H.mean(1, keepdim=True)).mean(0)                                     # (N, dim)
    x = torch.arange(N, dtype=torch.float64); basis = []; P = {}
    for k in range(1, N // 2 + 1):
        vecs = [(torch.cos(2 * np.pi * k * x / N)[:, None] * cbar).sum(0), (torch.sin(2 * np.pi * k * x / N)[:, None] * cbar).sum(0)]
        Bk = []
        for v in vecs:
            for b in basis + Bk: v = v - (v @ b) * b
            if v.norm() > 1e-8 * cbar.norm(): Bk.append(v / v.norm())
        basis += Bk; P[k] = torch.stack(Bk, 1) if Bk else None
    return P


def frac(e, P):
    tot = e.square().sum(1); out = {}; acc = torch.zeros_like(tot)
    for k, B in P.items():
        if B is None: continue
        f = (e @ B).square().sum(1); out[k] = (f / tot); acc += f
    out['outside'] = 1 - acc / tot
    return {str(k): float(v.mean()) for k, v in out.items()}


@torch.no_grad()
def main():
    require_slurm(); p = verify_protocol2(); S.load_maps(ROOT / 'protocol.json'); t0 = time.time(); eng = engine(); res = {}
    for d, ranks in p['s2']['modes'].items():
        P = planes(d); pos = slot_pos(d, 0); N = len(S.states(d)); ws = worlds2(d, 'confirm2'); n = len(ws)
        C = {s: cache2(d, 'confirm2', s) for s in S.states(d)}; fits = load(ROOT / f'local/rrr_{d}_natural.pt')
        Pd = {k: B.float().cuda() for k, B in P.items() if B is not None}
        for r in ranks:
            F = {op: RRRop(fits[op, r]) for op in ('plus', 'minus')}
            _, _, AQ = operator_stats(*editor_factors('rrr', fits['plus', r], 'plus'))
            present = unit_block(AQ, N)['harmonics_present']; missing = [k for k in Pd if k not in present]
            out = dict(rank=r, harmonics_present=present, harmonics_missing=missing, steps=[])
            for patch in ([False, True] if missing else [False]):
                state = [w['start_state'] for w in ws]
                h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).cuda(); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).cuda()
                ok = np.ones(n, bool); Rk = []; fr = []
                for step in range(1, 2 * N + 1):
                    state = [S.advance(d, s, 'plus') for s in state]; ref = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).cuda()
                    h = F['plus'](h, m)
                    if not patch: fr.append(frac((h[:, pos] - ref[:, pos]).double(), {k: B.double() for k, B in Pd.items()}))
                    if patch:
                        Bm = torch.cat([Pd[k] for k in missing], 1); hs = h[:, pos]
                        h[:, pos] = hs - (hs @ Bm) @ Bm.T + (ref[:, pos] @ Bm) @ Bm.T
                    dec = eng.decode(h, m)
                    ok &= np.array([Ev.score(o['text'], S.gold(w, s, 0), w, o['ended'])['success'] for o, w, s in zip(dec, ws, state)])
                    Rk.append(float(ok.mean()))
                out['patched_R_k' if patch else 'R_k'] = Rk
                if not patch: out['error_fraction_by_step'] = fr
            res[f'{d}/RRR{r}'] = out; print(d, r, 'present', present, 'R_2N', out['R_k'][-1], 'patched', out.get('patched_R_k', [None])[-1], flush=True)
    res['_note'] = 'Exploratory. Planes from train canonical slot vectors (natural order); errors at the template-0 attribute slot.'
    res['_seconds'] = time.time() - t0; res['_resources'] = eng.resources()
    dump('results/s2_modes.json', res)


if __name__ == '__main__':
    main()
