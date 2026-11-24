"""Pre-lock latent-space predictions (GPU, no decoding; PLAN B5, B6, v5 appendix A.1). --backbone bart|t5 [--split dev --out <dir>].
M (both backbones): every M cell x path (plus / minus / alternating, 2N steps from the world start) run on the confirm6 encodings of
the held-out templates exactly as in the chains; the locked vote models (this experiment's calib_mt: full / equal / fundamental-only)
read the slot at every step. C (BART): every C cell x path; readouts: the slot vote model (v5 locked lams: full / equal / fund) and the
slot + context score ('ctx', appendix A.3). Written: results/simulate_<bb>.json.gz (per world, per step: gold state and every argmax) and
results/simulate_<bb>_summary.json (per cell: predicted R-hat_2N and category for every readout, A_t, A-hat(m~) on plus; the M3
pre-check: a domain's F{1} is excluded at the lock if its own prediction falls on the other side of any M3 threshold)."""
import gzip
import time
from lib6 import *
import lcore
from cells6 import PATHS, m_cells, c_cells


def pred_summary(sim, N, path):
    st = np.array(sim['states']); out = {}
    for key, am in sim['argmax'].items():
        ok = np.array(am) == st; R = float(ok.all(1).mean()); At = ok.mean(0).tolist()
        o = dict(R_hat_2N=R, category=lcore.category(R), A_t=At)
        if path == 'plus':
            disp = {}
            for t in range(st.shape[1]): disp.setdefault(min((t + 1) % N, N - (t + 1) % N), []).append(At[t])
            o['A_hat'] = {str(k): float(np.mean(v)) for k, v in sorted(disp.items())}
        out[key] = o
    return out


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; split = sys.argv[sys.argv.index('--split') + 1] if '--split' in sys.argv else CONFIRM
    outdir = Path(sys.argv[sys.argv.index('--out') + 1]).resolve() if '--out' in sys.argv else ROOT / 'results'; t0 = time.time(); eng = engine5(bb)
    gates = read(ROOT / f'results/gates_{bb}.json'); sims = {}; summ = {}
    units = [('M', [(d, n, o, f, None) for d, n, o, f in m_cells(eng, bb, gates, split)])]
    if bb == 'bart': units.append(('C', [(d, n, o, 'state', st) for d, n, o, st in c_cells(eng, split)]))
    for unit, cells in units:
        models = {}
        for d, name, ops, fam, cset in cells:
            ops = ops() if callable(ops) else ops; N = len(S.states(d))
            if d not in models: models[d] = ctx_model(bb, d, split) if unit == 'C' else vote_model(bb, d)
            for path, oplist in PATHS(N).items():
                key = f'{unit}/{bb}/{d}/{name}/{path}'; sim = simulate_chain(bb, d, ops, oplist, models[d], split=split); sims[key] = sim
                ps = pred_summary(sim, N, path)
                summ[key] = dict(unit=unit, backbone=bb, domain=d, method=name, path=path, family=fam, set=cset, N=N, readouts=ps,
                                 R_hat_2N=ps['full']['R_hat_2N'], category=ps['full']['category'])
            print('sim', unit, bb, d, name, {p: round(summ[f'{unit}/{bb}/{d}/{name}/{p}']['R_hat_2N'], 3) for p in PATHS(N)},
                  {p: round(summ[f'{unit}/{bb}/{d}/{name}/{p}']['readouts']['ctx']['R_hat_2N'], 3) for p in PATHS(N)} if unit == 'C' else '', flush=True)
    m3 = {}
    for d in gates['M_domains']:
        N = len(S.states(d)); pl = summ[f'M/{bb}/{d}/F_{{1}}/plus']; al = summ[f'M/{bb}/{d}/F_{{1}}/alt']
        dA = pl['readouts']['full']['A_hat']['1'] - pl['readouts']['full']['A_hat'][str(N // 2)]
        side = dict(plus_R2N_le_020=pl['R_hat_2N'] <= .20, alt_R2N_ge_080=al['R_hat_2N'] >= .80, A1_minus_Ahalf_ge_050=dA >= .50)
        m3[f'{bb}/{d}'] = dict(pred_plus_R2N=pl['R_hat_2N'], pred_alt_R2N=al['R_hat_2N'], pred_A1_minus_Ahalf=dA, sides=side, included=all(side.values()))
    out = dict(backbone=bb, split=split, cells=summ, M3_precheck=m3, seconds=time.time() - t0, resources=eng.resources())
    f = outdir / f'simulate_{bb}.json.gz'; f.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(f, 'wt') as g: json.dump(sims, g)
    out['simulate_sha256'] = sha(f); dump(outdir / f'simulate_{bb}_summary.json', out)


if __name__ == '__main__':
    main()
