"""Dev chains (GPU, before the lock; decoding dev splits only; PLAN v7 B7, B10). --backbone bart|t5. For every unit-U cell on the
calibration splits - template-0 dev, training-template dev of the multi-template domains (v5 dev worlds) and dev7-ho (held-out templates,
this experiment) - and every path, (1) the latent simulation with readout, normalised margin m and off-manifold rho per world and step
(simulate_chain7), (2) the decoded chain (exact match per step; observed = trajectory success at the last step), checked to follow the same
latent dynamics. Also the pre-checks that need dev decoding: R0 / B6 'SNAP >= 0.90 on dev failure steps' (positive control on the first
'slot right, decode wrong' failure of every dev chain) and A (B8) rho of the F_empty alternating chain at t = 2N on dev7-ho.
Output: results/devchains_<bb>.json.gz (cells: family, split, sim, obs), results/devchains_<bb>_summary.json."""
import gzip
import time
from collections import defaultdict
from lib7 import *
from cells7 import u_cells, PATHS


@torch.no_grad()
def decode_chain(eng, bb, d, ops, oplist, split, snap_at_first_fail=False, man=None):
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d)
    state = [w['start_state'] for w in ws]; h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots(bb, d, split).to(DEV); ok = [True] * n; first = [None] * n; snap = []
    if snap_at_first_fail: P = planes(bb, d); lam = vote_lams(bb, d)['full'].double()      # binding domains have no vote model
    for step, op in enumerate(oplist, 1):
        prev = torch.tensor(state, device=DEV); state = [S.advance(d, s, op) for s in state]; h = apply_op(ops[op], h, m, prev); out = dec(eng, h, m)
        succ = [Ev.score(out[j]['text'], S.gold(w, state[j], t), w, out[j]['ended'])['success'] for j, w in enumerate(ws)]
        if snap_at_first_fail:
            am, _ = margin_raw(h[torch.arange(n, device=DEV), pos], man['Cw'].to(DEV), P, lam)
            idx = [j for j in range(n) if ok[j] and not succ[j] and int(am[j]) == state[j]]
            if idx:
                ix = torch.tensor(idx, device=DEV); g = torch.tensor([state[j] for j in idx], device=DEV); h2 = h[ix].clone()
                sub = dict(Cw=man['Cw'][idx].to(DEV), mu=man['mu'][idx].to(DEV), B=man['B'][idx].to(DEV), R=man['R'][idx].to(DEV))
                h2[torch.arange(len(idx), device=DEV), pos[ix]] = repair_slot('SNAP', h2[torch.arange(len(idx), device=DEV), pos[ix]], sub, g).to(h2.dtype)
                o2 = dec(eng, h2, m[ix])
                snap += [Ev.score(o2[q]['text'], S.gold(ws[j], state[j], t), ws[j], o2[q]['ended'])['success'] for q, j in enumerate(idx)]
        for j in range(n):
            if ok[j] and not succ[j]: first[j] = step
            ok[j] = ok[j] and succ[j]
    return ok, first, snap


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); out = dict(cells={}); snaps = defaultdict(list); rho_alt = {}
    for split in ('dev', 'dev7ho'):
        mans = {}; models = {}
        for fam, d, name, ops in u_cells(eng, bb, split):
            ops = ops() if callable(ops) else ops; N = len(S.states(d))
            if d not in mans: mans[d] = manifold(bb, d, split); models[d] = vote_model(bb, d)
            for path, oplist in PATHS(N).items():
                sim = simulate_chain7(bb, d, ops, oplist, models[d], split=split, man=mans[d])
                obs, first, snap = decode_chain(eng, bb, d, ops, oplist, split, snap_at_first_fail=True, man=mans[d])
                key = f'{split}/{bb}/{d}/{name}/{path}'; out['cells'][key] = dict(family=fam, split=split, domain=d, method=name, path=path, sim=sim, obs=obs, first_fail=first)
                snaps[fam].extend(snap)
                if split == 'dev7ho' and name == 'F_empty' and path == 'alt': rho_alt[d] = float(np.median([r[-1] for r in sim['rho']]))
                print('dev', key, fam, 'obs', round(float(np.mean(obs)), 3), 'U-none', round(float(np.mean(u_predict(sim, None, None))), 3), flush=True)
    f = ROOT / f'results/devchains_{bb}.json.gz'
    with gzip.open(f, 'wt') as g: json.dump(out, g)
    summ = dict(backbone=bb, cells=len(out['cells']), snap_positive_control={k: dict(n=len(v), rate=float(np.mean(v)) if v else None) for k, v in snaps.items()},
                snap_all=dict(n=sum(len(v) for v in snaps.values()), rate=float(np.mean([x for v in snaps.values() for x in v])) if any(snaps.values()) else None),
                A_precheck_rho_alt_2N_dev7ho=rho_alt, sha256=sha(f), seconds=time.time() - t0, resources=eng.resources())
    dump(ROOT / f'results/devchains_{bb}_summary.json', summ); print(json.dumps({k: v for k, v in summ.items() if k != 'resources'}), flush=True)


if __name__ == '__main__':
    main()
