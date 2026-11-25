"""Pre-lock latent predictions on the confirmation worlds (GPU job for the editors, which load on CUDA; encodings only, no decoding; PLAN v7 B10 as extended by C5).
--unit N|G --backbone bart|t5|t5_9b|t5_bb|t5_ll. Unit N: confirm8 (month-nat); unit G and ladder: confirm7 (weekday, month template 0).
For every cell (cells8.py) and path: simulate_chain7 (slot readout of the backbone's calibrated vote model, margin m, off-manifold rho per
world and step) and the per-world predictions of the slot-only predictor (the v7-selected primary predictor, v7 Q21 = H-nofix) and of U with
the dev-calibrated thresholds (results/dev8_<unit>_<bb>_summary.json). lock8.py records the SHA256 of the outputs.
Output: results/simulate8_<unit>_<bb>.json.gz, results/simulate8_<unit>_<bb>_summary.json."""
import gzip
import time
from types import SimpleNamespace
from cells8 import *


def main():
    require_slurm(); unit = sys.argv[sys.argv.index('--unit') + 1]; bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time()
    split = CONFIRM if unit == 'N' else 'confirm7'; d0 = S.NAT if unit == 'N' else 'month'
    eng = SimpleNamespace(d=cache5(bb, d0, split, 0)['h'].shape[-1])                 # editors need only the width; nothing is decoded
    cal = read(ROOT / f'results/dev8_{unit}_{bb}_summary.json')['U']['best']; th = (cal['tau_m'], cal['tau_r'])
    cells = n_cells(eng, bb, split) if unit == 'N' else g_cells(eng, bb, split); sims = {}; summ = {}; mans = {}; models = {}
    for fam, d, name, ops in cells:
        ops = ops() if callable(ops) else ops; N = len(S.states(d))
        if d not in mans: mans[d] = manifold(bb, d, split); models[d] = vote_model(bb, d)
        for path, oplist in PATHS(N).items():
            key = f'{d}/{name}/{path}'; sim = simulate_chain7(bb, d, ops, oplist, models[d], split=split, man=mans[d])
            sim['pred'] = dict(slot=u_predict(sim, None, None), U=u_predict(sim, *th)); sims[key] = sim
            summ[key] = dict(family=fam, domain=d, method=name, path=path, N=N, worlds=len(sim['world_ids']), pred_slot=float(np.mean(sim['pred']['slot'])), pred_U=float(np.mean(sim['pred']['U'])))
            print('sim8', unit, bb, key, fam, round(summ[key]['pred_slot'], 3), round(summ[key]['pred_U'], 3), flush=True)
    f = ROOT / f'results/simulate8_{unit}_{bb}.json.gz'
    with gzip.open(f, 'wt') as g: json.dump(sims, g)
    dump(ROOT / f'results/simulate8_{unit}_{bb}_summary.json', dict(unit=unit, backbone=bb, split=split, thresholds=dict(tau_m=th[0], tau_r=th[1]), cells=summ,
                                                                    simulate_sha256=sha(f), seconds=time.time() - t0))


if __name__ == '__main__':
    main()
