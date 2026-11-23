"""Pre-lock latent-space predictions (GPU, no decoding; PLAN 6.2, 10.1, appendix A.1). --backbone bart|t5 [--split dev --out <dir>].
For every L and N cell (operator or editor x path: plus / minus / alternating, 2N steps from the world start) the chain dynamics are run
on the confirm5 encodings exactly as in run_chain, and the locked vote models (full / equal / fundamental-only) read the slot at every
step. Written: results/simulate_<bb>.json.gz (per world, per step: gold state and the three argmaxes) and results/simulate_<bb>_summary.json
(per cell: unit, family, new, predicted R-hat_2N = fraction of worlds whose full-model readout equals the gold state at every step,
predicted category, predicted per-step accuracy and A-hat(m~) for N3). Also: the converged C3-family list (dev L2 <= 1.2 x the RRR-16
dev L2, PLAN 6.4 L3c) and the N3 pre-check (PLAN 2 new rule 2: a cell whose own prediction falls on the other side of a threshold is
excluded)."""
import gzip
import time
from lib5 import *
import lcore

from cells import PATHS, l_cells, n_cells


def pred_summary(sim, N, path):
    st = np.array(sim['states']); am = np.array(sim['argmax']['full']); ok = am == st
    At = ok.mean(0).tolist(); R = float(ok.all(1).mean()); out = dict(R_hat_2N=R, category=lcore.category(R), A_t=At)
    if path == 'plus':
        disp = {}
        for t in range(st.shape[1]): disp.setdefault(min((t + 1) % N, N - (t + 1) % N), []).append(At[t])
        out['A_hat'] = {str(k): float(np.mean(v)) for k, v in sorted(disp.items())}
    return out


@torch.no_grad()
def converged_c3(eng, bb):
    """L3c: dev L2 of every trained state-family editor (single-step normalised token L2, plus and minus averaged) vs 1.2 x RRR-16's."""
    res = {}
    for e in [x for x in existing_editors(bb) if x['family'] == 'state'] + [dict(name=f'{v}_s{s}', domain=d, path=str(ROOT / read(ROOT / f'results/train_new_{bb}_L.json')[f'{v}/{d}/s{s}']['path']))
                                                                          for b_, u, v, d, seeds, fam, k, upd in NEW_EDITORS if b_ == bb and u == 'L' and fam == 'state' for s in seeds
                                                                          if read(ROOT / f'results/train_new_{bb}_L.json')[f'{v}/{d}/s{s}']['status'] == 'ok']:
        d = e['domain']; scale = l2_scales(bb, d, 'natural')
        if f'RRR16/{d}' not in res:
            f, r = base_fit(bb, d) if base_fit(bb, d)[1] == 16 else (load(V4DIR / f'local/{bb}_rrr_{d}_natural_base.pt'), 16)
            res[f'RRR16/{d}'] = dev_l2({op: RRRop(f[op, 16]) for op in ('plus', 'minus')}, bb, d, 'natural', scale)
        ed = load_editor(eng, e['path']); v = dev_l2(ed, bb, d, 'natural', scale)
        res[f"{d}/{e['name']}"] = dict(dev_l2=v, rrr16=res[f'RRR16/{d}'], ratio=v / res[f'RRR16/{d}'], converged=v <= 1.2 * res[f'RRR16/{d}'])
    return res


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; split = sys.argv[sys.argv.index('--split') + 1] if '--split' in sys.argv else CONFIRM
    outdir = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else ROOT / 'results'; t0 = time.time(); eng = engine5(bb)
    gates = read(ROOT / f'results/gates_{bb}.json'); sims = {}; summ = {}
    for unit, cells in (("L", l_cells(eng, bb, split)), ("N", n_cells(eng, bb, gates, split))):
        for d, name, ops, fam, new in cells:
            ops = ops() if callable(ops) else ops; N = len(S.states(d)); model = vote_model(bb, d)
            for path, oplist in PATHS(N).items():
                key = f'{unit}/{bb}/{d}/{name}/{path}'; sim = simulate_chain(bb, d, ops, oplist, model, split=split); sims[key] = sim
                summ[key] = dict(unit=unit, backbone=bb, domain=d, method=name, path=path, family=fam, new=new, N=N, **pred_summary(sim, N, path))
            print('sim', unit, bb, d, name, {p: round(summ[f'{unit}/{bb}/{d}/{name}/{p}']['R_hat_2N'], 3) for p in PATHS(N)}, flush=True)
    n3 = {}
    for d in gates['N_domains']:
        N = len(S.states(d)); pl = summ[f'N/{bb}/{d}/F_{{1}}/plus']; al = summ[f'N/{bb}/{d}/F_{{1}}/alt']; dA = pl['A_hat']['1'] - pl['A_hat'][str(N // 2)]
        side = dict(plus_R2N_le_020=pl['R_hat_2N'] <= .20, alt_R2N_ge_080=al['R_hat_2N'] >= .80, A1_minus_Ahalf_ge_050=dA >= .50)
        n3[f'{bb}/{d}'] = dict(pred_plus_R2N=pl['R_hat_2N'], pred_alt_R2N=al['R_hat_2N'], pred_A1_minus_Ahalf=dA, sides=side, included=all(side.values()))
    out = dict(backbone=bb, split=split, cells=summ, N3_precheck=n3, seconds=time.time() - t0)
    if split == CONFIRM: out['converged_C3'] = converged_c3(eng, bb)
    out['resources'] = eng.resources()
    f = outdir / f'simulate_{bb}.json.gz'; f.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(f, 'wt') as g: json.dump(sims, g)
    out['simulate_sha256'] = sha(f); dump(outdir / f'simulate_{bb}_summary.json', out)


if __name__ == '__main__':
    main()
