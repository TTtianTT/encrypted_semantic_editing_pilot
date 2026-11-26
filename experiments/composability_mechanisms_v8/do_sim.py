"""DO cells and latent simulations (CPU, before the lock; PLAN v9 section 5). --model gemma|qwen.
Cells per (model, domain) at the model's layer (do_prep.py): S-RRR-r for every fitted r (plus); surgeries on S-RRR-16 - F_empty, F{1},
F_not1 (plus and alternating); the admitted CE slot editors C1_s45-47 and slot C3-U4_s45-47 (plus). 2N steps from the world start.
Readout (the locked latent predictor of unit D, as in v8): equal-weight plane readout, lambda_k = 1 / median one-step distance in plane k on
the train latents, candidates = the world's clean latents. A chain is predicted correct iff the readout equals the gold state at every step.
Dev: discriminability pre-check (DEVIATIONS 3) - DO1a S-RRR-(r*_pred) R_2N >= 0.95, DO1b S-RRR-(r*_pred - 2) R_2N <= 0.50, DO2 F{1} plus
<= 0.20, F{1} alt >= F_empty alt - 0.10, F_not1 plus <= 0.10, DO4 C1 R_2 <= 0.20 (seed median), DO5 C3-U4 R_2N >= 0.95 (seed median); a
condition the simulation puts on the other side is dropped. Confirm: the locked per-world predictions (readout per step).
Output: results/do_sim_<model>.json.gz (per cell: world_ids, start, states, argmax), results/do_sim_<model>_summary.json."""
import gzip
from do_prep import *
from lib9 import plane_dists, vote_scores

PATHS = lambda N: dict(plus=['plus'] * (2 * N), alt=['plus', 'minus'] * N)


def do_cells(model, d, layer):
    """{name: (step_fn, paths)} with step_fn(op, V (W, dim) double) -> V'."""
    f = load(ROOT / f'local/do_{model}_{d}_srrr.pt'); fits, P = f['fits'], f['planes']; out = {}
    for r in f['ranks']: out[f'SRRR{r}'] = (lin(fits['plus', r]), ('plus',))
    base = {op: lin(fits[op, 16]) for op in ('plus', 'minus')}; out['F_empty'] = (lambda op, v: base[op](op, v), ('plus', 'alt'))
    Bs = {'F_{1}': torch.cat([B for k, B in P if k == 1], 1).double(), 'F_not1': torch.cat([B for k, B in P if k != 1], 1).double()}
    for n, B in Bs.items(): out[n] = ((lambda B: lambda op, v: (lambda v1: v1 - ((v1 - v) @ B) @ B.T)(base[op](op, v)))(B), ('plus', 'alt'))
    rec = read(ROOT / f'results/do_prep_{model}.json')['domains'][d].get('editors', {})
    for key, r in rec.items():
        if not r['admitted']: continue
        v, s = key.split('/'); c = load(ROOT / f'local/do_{model}_{v}_{d}_{s}.pt'); ed = slot_pair(c['editor']['plus.b'].shape[0], c['seed']).cpu().double(); ed.load_state_dict(c['editor'])
        out[f'{v}_{s}'] = ((lambda ed: lambda op, x: x + ed[op].b + ed[op].u(ed[op].v(x)))(ed.eval().requires_grad_(False)), ('plus',))
    return out


def readout_fn(Xtr, Xc, P, d):
    nxt = next_idx(d, 'plus'); dp = torch.stack([((Xtr[:, nxt] - Xtr) @ B.double()).square().sum(-1).reshape(-1) for _, B in P], 1); lam = 1 / dp.median(0).values
    Pd = [(k, B.double()) for k, B in P]
    return (lambda V: vote_scores(plane_dists(V.double(), Xc, Pd), lam).argmax(-1).tolist()), lam


@torch.no_grad()
def simulate(step, X, ws, d, oplist, rd):
    st = [w['start_state'] for w in ws]; s0 = list(st); V = torch.stack([X[i, s] for i, s in enumerate(st)]).double(); states, am = [], []
    for op in oplist:
        st = [S.advance(d, s, op) for s in st]; V = step(op, V); states.append(list(st)); am.append(rd(V))
    T_ = lambda L: [list(x) for x in zip(*L)]
    return dict(world_ids=[w['world_id'] for w in ws], start=s0, states=T_(states), argmax=T_(am))


def pred(sim, k=None):
    return float(np.mean([all(a == g for a, g in zip(sim['argmax'][i][:k], sim['states'][i][:k])) for i in range(len(sim['world_ids']))]))


def main():
    require_slurm(); model = sys.argv[sys.argv.index('--model') + 1]; prep = read(ROOT / f'results/do_prep_{model}.json'); layer = prep['layer']; sims = {}; summ = dict(model=model, layer=layer, cells={}, precheck={})
    keep = read(ROOT / f'data/do_worlds_{model}.json')
    for d, r in prep['domains'].items():
        if r.get('skipped'): continue
        Xtr = load(ROOT / f'local/do_{model}_{d}_train.pt')['latents']; P = load(ROOT / f'local/do_{model}_{d}_srrr.pt')['planes']; N = len(S.states(d)); cells = do_cells(model, d, layer)
        for split in ('dev', CONF(d)):
            L = load(ROOT / f'local/do_{model}_{d}_{split}.pt'); X = L['latents']; ids = L['world_ids']; wmap = {w['world_id']: w for w in worlds5(d, split)}; ws = [wmap[i] for i in ids]
            rd, lam = readout_fn(Xtr, X, P, d); summ.setdefault('lambda', {})[d] = lam.tolist()
            for name, (step, paths) in cells.items():
                for path in paths:
                    sim = simulate(step, X, ws, d, PATHS(N)[path], rd); key = f'{split}/{d}/{name}/{path}'; sims[key] = sim
                    summ['cells'][key] = dict(R1=pred(sim, 1), R2=pred(sim, 2), R2N=pred(sim))
        dv = lambda name, path, k='R2N': summ['cells'].get(f'dev/{d}/{name}/{path}', {}).get(k); rp = r['rstar_pred']
        med = lambda v, k, path='plus': (lambda xs: float(np.median(xs)) if xs else None)([c[k] for kk, c in summ['cells'].items() if kk.startswith(f'dev/{d}/{v}_') and kk.endswith(f'/{path}')])
        pc = dict(DO1a=dict(pred=dv(f'SRRR{rp}', 'plus'), keep=(dv(f'SRRR{rp}', 'plus') or 0) >= .95), DO1b=dict(pred=dv(f'SRRR{rp - 2}', 'plus'), keep=(dv(f'SRRR{rp - 2}', 'plus') or 1) <= .50),
                  DO2_F1_plus=dict(pred=dv('F_{1}', 'plus'), keep=dv('F_{1}', 'plus') <= .20), DO2_F1_alt=dict(pred=dv('F_{1}', 'alt'), ref=dv('F_empty', 'alt'), keep=dv('F_{1}', 'alt') >= dv('F_empty', 'alt') - .10),
                  DO2_Fnot1_plus=dict(pred=dv('F_not1', 'plus'), keep=dv('F_not1', 'plus') <= .10))
        m4, m5 = med('C1', 'R2'), med('C3U4', 'R2N')
        pc['DO4_R2'] = dict(pred=m4, keep=m4 is not None and m4 <= .20); pc['DO5'] = dict(pred=m5, keep=m5 is not None and m5 >= .95); summ['precheck'][d] = pc
        print('DO sim', model, d, json.dumps(pc), flush=True)
    f = ROOT / f'results/do_sim_{model}.json.gz'
    with gzip.open(f, 'wt') as g: json.dump(sims, g)
    summ['sha256'] = sha(f); dump(ROOT / f'results/do_sim_{model}_summary.json', summ)


if __name__ == '__main__':
    main()
