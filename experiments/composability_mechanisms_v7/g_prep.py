"""Units G and ladder, pre-lock GPU step (PLAN v7 C3, B.3; plan change 2026-11-25: template-0 weekday and month, the original train / dev
split, confirm7 = confirm6 reused, 'text reused, first evaluation for this model'). --backbone t5_9b|t5_bb|t5_ll.
1. Encode weekday and month train, dev (decoded) and confirm7 (encoded only, never decoded before the lock).
2. Reconstruction gate: decode of the clean train and dev encodings, every state; >= 0.99 per domain, else the backbone leaves the unit
   (9B-9B: G stops and is reported, PLAN C5; ladder sizes: skipped, PLAN C3). State words single-token: n_audit.py.
3. Planes from train slot vectors; amplitudes a_k and one-step change s_k; r*_pred (Proposition 1, planes with a_k >= 5% of the largest).
4. Closed-form fits on train (v4 fit_rrr4): RRR-r for r in {N-4, ..., N, 16} plus r*_pred and r*_pred - 2; FF-r for the rank-deficient r
   (r < N - 1). Dev check of RRR-16: single step and one-way plus R_2N (base operator; reported).
5. Vote-model calibration on dev (calib_probes / fit_calibration, the v3 procedure).
Output: results/g_prep_<bb>.json, results/calib_g_<bb>.json, local/<bb>_R_<d>_v8.pt, local/planes_<bb>_<d>.pt."""
import time
from lib8 import *

G_DOMAINS = ['weekday', 'month']
SPLITS = ('train', 'dev', 'confirm7')


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; assert bb in MODELS8; t0 = time.time(); eng = engine8(bb)
    res = dict(backbone=bb, revision=eng.revision, domains={}); cal = dict(backbone=bb, domains={})
    for d in G_DOMAINS:
        N = len(S.states(d)); r = res['domains'][d] = {}
        for sp in SPLITS:
            encode_split5(eng, bb, d, sp, bs=32); print('encoded', bb, d, sp, flush=True)
        pos = {sp: slots(bb, d, sp) for sp in SPLITS}
        for sp in SPLITS: assert bool(cache5(bb, d, sp, 0)['m'][torch.arange(len(pos[sp])), pos[sp]].all()), (d, sp, 'slot on padding')
        r['encoded_sha256'] = {f'{sp}_s{s}': sha(cpath(bb, d, sp, s)) for sp in SPLITS for s in S.states(d)}
        r['reconstruction'] = reencode_rate(eng, bb, d, splits=('train', 'dev')); r['gate'] = r['reconstruction']['rate'] >= .99
        print('gate', bb, d, r['reconstruction']['rate'], flush=True)
        if not r['gate']: continue
        P = planes(bb, d); save(ROOT / f'local/planes_{bb}_{d}.pt', P); amp = amplitudes(bb, d); rp = rstar_pred(amp)
        ranks = sorted(set(range(N - 4, N + 1)) | {16, rp, rp - 2}); deficient = [x for x in ranks if x < N - 1]
        Q1 = P[0][1]; assert P[0][0] == 1 and Q1.shape[1] == 2
        rr, ri = fit_rrr4(bb, d, 'natural', ranks); ff, fi = fit_rrr4(bb, d, 'natural', deficient, ff=True, Q1=Q1)
        fits = {('RRR', op, x): rr[op, x] for op in ('plus', 'minus') for x in ranks} | {('FF', op, x): ff[op, x] for op in ('plus', 'minus') for x in deficient}
        save(ROOT / f'local/{bb}_R_{d}_v8.pt', fits)
        ops16 = {op: RRRop(rr[op, 16]) for op in ('plus', 'minus')}
        single = dev_single(eng, bb, d, 'natural', ops16); chain = dev_chain(eng, bb, d, 'natural', ops16, ['plus'] * (2 * N))
        r |= dict(planes=[dict(k=k, dim=B.shape[1]) for k, B in P], planes_sha256=sha(ROOT / f'local/planes_{bb}_{d}.pt'), amplitudes=amp, rstar_pred=rp,
                  ranks=ranks, ff_ranks=deficient, ridge=dict(RRR=ri, FF=fi), fits_sha256=sha(ROOT / f'local/{bb}_R_{d}_v8.pt'),
                  base_dev=dict(single=single, R1=chain[0], R_N=chain[N - 1], R_2N=chain[-1]))
        print('base', bb, d, 'r*_pred', rp, 'single', round(single['rate'], 4), 'R_2N', round(chain[-1]['rate'], 4), flush=True)
        H, meta, ys, Cw = calib_probes(eng, bb, d, P)
        cal['domains'][d] = fit_calibration(bb, d, P, H, meta, ys, Cw) | dict(planes_sha256=r['planes_sha256'])
        print('calib', bb, d, {m: round(v['probe_accuracy'], 3) for m, v in cal['domains'][d]['models'].items()}, flush=True)
        dump(ROOT / f'results/g_prep_{bb}.json', res | dict(resources=eng.resources(), seconds=time.time() - t0))
    res['gate'] = all(v['gate'] for v in res['domains'].values())
    dump(ROOT / f'results/g_prep_{bb}.json', res | dict(resources=eng.resources(), seconds=time.time() - t0))
    dump(ROOT / f'results/calib_g_{bb}.json', cal | dict(seconds=time.time() - t0))


if __name__ == '__main__':
    main()
