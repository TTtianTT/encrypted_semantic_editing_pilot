"""P6 (GPU, exploratory): dynamics of v3 conditions whose idealized prediction failed. --bb bart: month F{4}, F{5}, F{6} alternating
chains and month E_K* plus chain; --bb t5: month E_K* plus chain. Latents are recomputed on v3 confirm3 (no decoding); decoded success is
read from v3's shards. Per step: per-plane phase difference and amplitude ratio of the slot relative to the target canonical slot (plane
coordinates centred on the world's mean over states), slot residual outside the harmonic span (relative to the target), and context
(non-slot, non-pad) deviation from E(target). Reported: per-step medians, values at the step before each world's first failure, and which
quantity first exceeds its threshold (phase > pi/N, amplitude ratio off by > 25%, residual or context > 2x its step-1 value)."""
import time
from lib4 import *

V3SH = V3DIR / 'results/shards'


def conditions(bb):
    cal = read(V3DIR / 'protocol.json')['calib'][bb]['month']; P = planes(bb, 'month'); pos = slots(bb, 'month', 'confirm3')
    X = slot_matrix(bb, 'month', 'train'); out = {}
    f = load(V2DIR / 'local/rrr_month_natural.pt') if bb == 'bart' else load(V3DIR / 'local/t5_rrr_month_natural.pt')
    T = {op: RRRop(f[op, 16]) for op in ('plus', 'minus')}
    if bb == 'bart':
        for k in (4, 5, 6): out[f'F_{{{k}}}', 'alt_from_start'] = {op: Freeze(T[op], bvec(P, {k}), pos) for op in T}
    K = cal['Kstar']['K']; B = torch.cat([b for k, b in P if k in K], 1)
    out['E_Kstar', 'plus_from_start'] = {op: PlaneEd(*fit_plane_editor(X, B, 'month', op), B, pos) for op in ('plus', 'minus')}
    return out, P, pos, K


def v3_success(bb, cond, path):
    ok = {}
    for f in sorted(V3SH.glob(f'chain_{bb}_month_natural_{cond}_{path}_*.jsonl')):
        for r in rows(f): ok.setdefault(r['world_id'], {})[r['step']] = r['success']
    return ok


@torch.no_grad()
def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--bb') + 1]; t0 = time.time(); eng = engine4(bb); res = {}
    d = 'month'; N = 12; ws = worlds4(d, 'confirm3'); n = len(ws); C = {s: cache4(bb, d, 'confirm3', s) for s in S.states(d)}
    conds, P, pos, K = conditions(bb); pos = pos.to(DEV); ar = torch.arange(n, device=DEV); Cw = slot_matrix(bb, d, 'confirm3').to(DEV)
    Bs = [(k, B.to(DEV)) for k, B in P]; Ball = torch.cat([B for _, B in Bs], 1); mu = Cw.mean(1)                     # (n, dim)
    for (cond, path), ops in conds.items():
        oplist = ['plus'] * 24 if path == 'plus_from_start' else ['plus', 'minus'] * 12; succ = v3_success(bb, cond, path)
        state = [w['start_state'] for w in ws]; h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
        nonslot = m.clone(); nonslot[ar, pos] = 0; src0 = h.clone(); steps = []
        for t, op in enumerate(oplist, 1):
            state = [S.advance(d, s, op) for s in state]; h = ops[op](h, m); ref = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV)
            hs = h[ar, pos].double(); tg = Cw[ar, torch.tensor(state, device=DEV)]
            rec = {}
            for k, B in Bs:
                z = (hs - mu) @ B.double(); zt = (tg - mu) @ B.double()
                if B.shape[1] == 2:
                    ph = torch.atan2(z[:, 1], z[:, 0]) - torch.atan2(zt[:, 1], zt[:, 0]); ph = (ph + np.pi) % (2 * np.pi) - np.pi
                    rec[f'phase_{k}'] = ph.abs().cpu().numpy(); rec[f'amp_{k}'] = (z.norm(dim=1) / zt.norm(dim=1)).cpu().numpy()
                else:
                    rec[f'phase_{k}'] = (np.pi * (torch.sign(z[:, 0]) != torch.sign(zt[:, 0])).double()).cpu().numpy(); rec[f'amp_{k}'] = (z[:, 0].abs() / zt[:, 0].abs()).cpu().numpy()
            dv = hs - tg; resid = dv - (dv @ Ball.double()) @ Ball.double().T
            rec['residual'] = (resid.norm(dim=1) / (tg - mu).norm(dim=1)).cpu().numpy()
            cd = ((h - ref).float().square().sum(-1) * nonslot).sum(1) / nonslot.sum(1); cs = ((ref - src0).float().square().sum(-1) * nonslot).sum(1) / nonslot.sum(1)
            rec['context'] = cd.cpu().numpy(); rec['context_rel_to_src_gap'] = (cd / cs.clamp_min(1e-12)).cpu().numpy()
            steps.append(rec)
        keys = list(steps[0]); per_step = {k: [float(np.median(s_[k])) for s_ in steps] for k in keys}
        fail_t = {i: next((t for t in range(1, len(oplist) + 1) if not succ.get(w['world_id'], {}).get(t, True)), None) for i, w in enumerate(ws)}
        thr = {k: (np.pi / N if k.startswith('phase') else None) for k in keys}
        # E_K*: planes outside K* are left unedited by construction; they are reported per step but excluded from 'first to exceed'
        cand = [k for k in keys if not (cond == 'E_Kstar' and k.split('_')[0] in ('phase', 'amp') and k.split('_')[-1].isdigit() and int(k.split('_')[-1]) not in K)]
        first = {}; before_fail = {k: [] for k in keys}
        for i in range(n):
            tf = fail_t[i]
            if tf is None: continue
            for k in keys:
                if tf >= 2: before_fail[k].append(float(steps[tf - 2][k][i]))
            hits = {}
            for k in cand:
                for t in range(1, tf + 1):
                    v = steps[t - 1][k][i]; base = steps[0][k][i]
                    bad = (v > thr[k]) if k.startswith('phase') else (abs(v - 1) > .25) if k.startswith('amp') else (v > 2 * base and t > 1)
                    if bad: hits[k] = t; break
            if hits:
                tmin = min(hits.values()); first.setdefault('|'.join(sorted(k for k, t in hits.items() if t == tmin)), []).append(tf - tmin)
        res[f'{cond}/{path}'] = dict(per_step_median=per_step, n_failing=sum(v is not None for v in fail_t.values()),
                                     failure_step_hist={str(t): sum(1 for v in fail_t.values() if v == t) for t in sorted({v for v in fail_t.values() if v})},
                                     median_before_failure={k: float(np.median(v)) if v else None for k, v in before_fail.items()},
                                     excluded_from_first=[k for k in keys if k not in cand], first_to_exceed={k: dict(worlds=len(v), median_lead_steps=float(np.median(v))) for k, v in sorted(first.items(), key=lambda x: -len(x[1]))})
        print('P6', bb, cond, path, 'failing', res[f'{cond}/{path}']['n_failing'], list(res[f'{cond}/{path}']['first_to_exceed'].items())[:3], flush=True)
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump(f'results/patch/p6_dyn_{bb}.json', res)


if __name__ == '__main__':
    main()
