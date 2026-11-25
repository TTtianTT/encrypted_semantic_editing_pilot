"""Unit N, pre-lock GPU step (PLAN v7 C2; train and dev of month-nat decoded, confirm8 only encoded). --backbone bart|t5.
1. Encode month-nat train, dev, confirm8 (per state; slot positions from n_audit.py).
2. Planes from natural-train slot vectors (A.1 of v3, unchanged); saved to local/planes_<bb>_month-nat.pt.
3. GN (= v6 GM, gates.py, unchanged rule): candidates S-RRR-16, S-RRR-32, E_all fitted on the natural-train slots; the first with dev
   single-step success >= 0.95 (plus and minus pooled) and dev one-way plus R_2N >= 0.95 is S-RRR_nat; none -> recorded (N1 then tests
   the selected-free S-RRR-16 and Q24 is decided by N1 as locked).
4. References on dev: full-sequence RRR-16 fitted on natural train (v4 fit_rrr4 procedure), and reencode (decode of the clean encodings).
5. N2 discriminability pre-check: S-RRR-16_syn = v6's S-RRR-16 of month-mt (local/<bb>_srrr_month-mt.pt of composability_mechanisms_v5),
   zero-shot on natural dev: single step and one-way plus R_2N; R_2N >= 0.95 or <= 0.05 -> N2 descriptive (PLAN C2).
6. Vote-model calibration on natural dev (v6 calib_mt.py procedure: plane-substitution probes decoded and parsed; full / equal / fund).
Output: results/gates_nat_<bb>.json, results/calib_nat_<bb>.json, local/<bb>_srrr_month-nat.pt, local/<bb>_eall_month-nat.pt,
local/<bb>_rrr_month-nat_full16.pt, local/planes_<bb>_month-nat.pt."""
import time
from lib8 import *

D = S.NAT


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


def evaluate(eng, bb, ops, N):
    single = dev_single(eng, bb, D, 'natural', ops); chain = dev_chain(eng, bb, D, 'natural', ops, ['plus'] * (2 * N))
    return dict(single=single, plus=dict(R1=chain[0], R_N=chain[N - 1], R_2N=chain[-1]), passes=single['rate'] >= .95 and chain[-1]['rate'] >= .95)


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine8(bb); N = len(S.states(D))
    for sp in ('train', 'dev', CONFIRM):
        encode_split5(eng, bb, D, sp, bs=32); print('encoded', bb, D, sp, flush=True)
    enc = {}
    for sp in ('train', 'dev', CONFIRM):
        pos = slots(bb, D, sp); c0 = cache5(bb, D, sp, 0)
        assert bool(c0['m'][torch.arange(len(pos)), pos].all()), (sp, 'slot on padding')
        enc[sp] = {f'{bb}_{D}_{sp}_s{s}': sha(cpath(bb, D, sp, s)) for s in S.states(D)}
    P = planes(bb, D); save(ROOT / f'local/planes_{bb}_{D}.pt', P)
    res = dict(backbone=bb, encoded_sha256=enc, planes=[dict(k=k, dim=b.shape[1]) for k, b in P], planes_sha256=sha(ROOT / f'local/planes_{bb}_{D}.pt'))

    pos = slots(bb, D, 'dev')
    fits, info = fit_srrr(bb, D, (16, 32)); save(ROOT / f'local/{bb}_srrr_{D}.pt', fits)
    ea, B = fit_eall(bb, D); save(ROOT / f'local/{bb}_eall_{D}.pt', dict(fits=ea, B=B))
    full, finfo = fit_rrr4(bb, D, 'natural', [16]); save(ROOT / f'local/{bb}_rrr_{D}_full16.pt', full)
    syn = load(V6DIR / f'local/{bb}_srrr_month-mt.pt')
    cand = {'SRRR16': {op: SlotRRRop(fits[op, 16], pos) for op in ('plus', 'minus')}, 'SRRR32': {op: SlotRRRop(fits[op, 32], pos) for op in ('plus', 'minus')},
            'Eall': {op: PlaneEd(ea[op][0], ea[op][1], B, pos) for op in ('plus', 'minus')}}
    refs = {'RRR16full_ref': {op: RRRop(full[op, 16]) for op in ('plus', 'minus')}, 'SRRR16syn': {op: SlotRRRop(syn[op, 16], pos) for op in ('plus', 'minus')}}
    GN = {}
    for name, ops in (cand | refs).items():
        GN[name] = evaluate(eng, bb, ops, N); print('GN', bb, name, round(GN[name]['single']['rate'], 4), round(GN[name]['plus']['R_2N']['rate'], 4), flush=True)
    base = next((n for n in ('SRRR16', 'SRRR32', 'Eall') if GN[n]['passes']), None)
    r2 = GN['SRRR16syn']['plus']['R_2N']['rate']
    res |= dict(GN=dict(candidates=GN, base=base, ridge=info, full_ridge=finfo, srrr_sha256=sha(ROOT / f'local/{bb}_srrr_{D}.pt'),
                        eall_sha256=sha(ROOT / f'local/{bb}_eall_{D}.pt'), full16_sha256=sha(ROOT / f'local/{bb}_rrr_{D}_full16.pt'),
                        syn_source=str(V6DIR / f'local/{bb}_srrr_month-mt.pt'), syn_sha256=sha(V6DIR / f'local/{bb}_srrr_month-mt.pt')),
                N2_precheck=dict(dev_R2N=r2, descriptive=bool(r2 >= .95 or r2 <= .05)),
                reencode_dev=reencode_rate(eng, bb, D, splits=('dev',)))
    dump(ROOT / f'results/gates_nat_{bb}.json', res | dict(resources=eng.resources(), seconds=time.time() - t0))

    Cw = slot_matrix(bb, D, 'dev'); H, meta, ys, _ = probes(eng, bb, D, P)
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
    cal = dict(backbone=bb, domains={D: dict(N=N, planes=[dict(k=k, dim=B.shape[1]) for k, B in P], models=models, probes=len(ys), parsable=len(ok),
                                            probe_outcomes=by_type, lambda0=lam0.tolist(), mean_step_dist=Ed.tolist(), planes_sha256=sha(ROOT / f'local/planes_{bb}_{D}.pt'))})
    print('calib', bb, 'omega', [round(v, 3) for v in models['full']['omega']], 'acc', {m: round(v['probe_accuracy'], 3) for m, v in models.items()}, flush=True)
    dump(ROOT / f'results/calib_nat_{bb}.json', cal | dict(resources=eng.resources(), seconds=time.time() - t0))


if __name__ == '__main__':
    main()
