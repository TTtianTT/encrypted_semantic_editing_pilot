"""v9 latent simulations (GPU job because editors load on CUDA; no model, no decoding; before the lock). --backbone bart|t5.
For every cell of cells9.py and path: simulate_chain7 (slot readout of the backbone's locked vote model, margin m, off-manifold rho per world
and step) on dev (discriminability pre-check, DEVIATIONS 3) and on the confirmation splits (locked per-world predictions; the readout at
step 1 also gives D after the lock). Pre-check (dev, slot-only readout; a chain is predicted correct iff the readout equals the gold state at
every step up to k): B1a R_1 <= 0.20; B1b R_1 from x0 >= 0.80, from other starts <= 0.20, R_2 <= 0.20; B1c R_2N >= 0.90; B2 LoReFT-C1 R_2
<= 0.20, LoReFT-C3U4 R_2N >= 0.95; B3 R_2 <= 0.20; B4 U8 / U16 R_{S_max+2} <= 0.50, Urand R_4N <= 0.50; S C1 R_2 <= 0.20, C3-U4 R_2N >=
0.95 (seed medians, plus path); a condition predicted on the other side is dropped (exploratory). B5: descriptive if the simulated R_2N is
already >= 0.95 (the readout is exact by construction). R_1 of CE editors and D are not pre-checked.
Output: results/sim9_<bb>_<split>.json.gz, results/sim9_<bb>_summary.json."""
import gzip
import time
from types import SimpleNamespace
from cells9 import *

HZ = {'U8': 8, 'U16': 16}


def pred_rate(sim, k=None, starts=None, exclude=False):
    p = u_predict(sim, None, None, steps=k); sel = [i for i, s in enumerate(sim['start']) if starts is None or ((s in starts) != exclude)]
    return float(np.mean([p[i] for i in sel])) if sel else None


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); summ = {}
    for split in ('dev', 'confirm'):
        dim = cache5(bb, 'month', 'dev', 0)['h'].shape[-1]; eng = SimpleNamespace(d=dim); sims = {}; mans = {}; models = {}
        for unit, fam, d, name, ops, paths in cells9(eng, bb, split):
            ops = ops() if callable(ops) else ops; sp = 'dev' if split == 'dev' else 'confirm8' if d == S.NAT else 'confirm7'; N = len(S.states(d))
            if d not in mans: mans[d] = manifold(bb, d, sp); models[d] = vote_model(bb, d)
            for path, ol in paths(N).items():
                sim = simulate_chain7(bb, d, ops, ol, models[d], split=sp, man=mans[d]); key = f'{unit}/{d}/{name}/{path}'; sims[key] = sim
                if path == 'plus':
                    v = name.split('_')[0]; x0 = S.states(d)[0]
                    summ.setdefault(split, {})[f'{unit}/{d}/{name}'] = dict(unit=unit, family=fam, domain=d, method=name, N=N,
                        R1=pred_rate(sim, 1), R2=pred_rate(sim, 2), R2N=pred_rate(sim, 2 * N), R4N=pred_rate(sim, 4 * N) if len(ol) >= 4 * N else None,
                        Rhz=pred_rate(sim, HZ[v] + 2) if v in HZ else None, R1_x0=pred_rate(sim, 1, {x0}), R1_other=pred_rate(sim, 1, {x0}, exclude=True))
            print('sim9', bb, split, unit, d, name, flush=True)
        f = ROOT / f'results/sim9_{bb}_{split}.json.gz'
        with gzip.open(f, 'wt') as g: json.dump(sims, g)
        summ.setdefault('sha256', {})[split] = sha(f)
    summ['precheck'] = precheck(summ['dev']); summ['seconds'] = time.time() - t0
    dump(ROOT / f'results/sim9_{bb}_summary.json', summ); print(json.dumps(summ['precheck'])[:3000], flush=True)


def precheck(dev):
    med = lambda unit, d, v, k: (lambda xs: float(np.median(xs)) if xs else None)([c[k] for c in dev.values() if c['unit'] == unit and c['domain'] == d and c['method'].split('_')[0] == v and c[k] is not None])
    out = {}
    for d in sorted({c['domain'] for c in dev.values()}):
        c = lambda name: dev.get(f'B1/{d}/{name}')
        if c('B1a'): out[f'B1a/{d}'] = dict(R1=dict(pred=c('B1a')['R1'], keep=c('B1a')['R1'] <= .20))
        if c('B1b'): out[f'B1b/{d}'] = dict(R1_x0=dict(pred=c('B1b')['R1_x0'], keep=c('B1b')['R1_x0'] >= .80), R1_other=dict(pred=c('B1b')['R1_other'], keep=c('B1b')['R1_other'] <= .20),
                                            R2=dict(pred=c('B1b')['R2'], keep=c('B1b')['R2'] <= .20))
        if c('B1c'): out[f'B1c/{d}'] = dict(R2N=dict(pred=c('B1c')['R2N'], keep=c('B1c')['R2N'] >= .90))
        for unit, v, k, rule in (('B2', 'LoReFTC1', 'R2', lambda x: x <= .20), ('B2', 'LoReFTC3U4', 'R2N', lambda x: x >= .95), ('B3', 'FullC1', 'R2', lambda x: x <= .20),
                                 ('B3', 'MLPC1', 'R2', lambda x: x <= .20), ('B4', 'U8', 'Rhz', lambda x: x <= .50), ('B4', 'U16', 'Rhz', lambda x: x <= .50),
                                 ('B4', 'Urand', 'R4N', lambda x: x <= .50), ('S', 'C1', 'R2', lambda x: x <= .20), ('S', 'C3U4', 'R2N', lambda x: x >= .95)):
            m = med(unit, d, v, k)
            if m is not None: out[f'{v}/{d}'] = {k: dict(pred=m, keep=bool(rule(m)))}
        r = dev.get(f'B5/{d}/Rot')
        if r: out[f'B5/{d}'] = dict(R2N=dict(pred=r['R2N'], descriptive=r['R2N'] >= .95))
    return out


if __name__ == '__main__':
    main()
