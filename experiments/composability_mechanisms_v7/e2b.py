"""E2b (AMENDMENT_02; after the lock; exploratory; CPU, no decoding): the old-name residue of the binding write, measured on chains whose
direction is random at every step, so that the previous name is not a function of the current one (E2's plus-chain probe could not tell
them apart; REPORT section 2).
Chains: per world a fixed random sequence of plus / minus (rng 3101 + world index; probability 1/2 each), applied with the editor's own
oracle-routed operators; train and dev 8 steps (the editors' horizon), confirm7 100 steps. Editors: OR-U8 with UV rank 32 (v7 K7), 128 and
full rank (E2), seeds 42-44.
Probes (linear, standardised slot vector; ridge C from {0.01, 0.1, 1, 10} chosen on dev chains; fitted on train chains):
- direction probe: the direction of the last step (plus / minus). Given the current name, the previous name is current - 1 or current + 1,
  so chance is 0.5; accuracy above 0.5 means the slot still carries where it came from (old-name residue).
- current-name probe (3 classes): control for how readable the slot still is.
- sanity: the direction probe applied to clean encodings E_w(current) (no history) must be at chance.
Reported per editor and per step range (1-8, 9-30, 31-100): mean accuracies. Reading (written before running): if higher rank lowers the
direction-probe accuracy on steps 1-8 (in-horizon) while the decay does not slow (E2), the write fidelity is not the bottleneck; if the
residue does not fall, the reading stays 'unexplained'. Output: results/e2b.json."""
import random
import time
from lib8 import *

V = {'OR32': lambda s: V7DIR / f'local/k7_ORU8_bind3_s{s}_u8000.pt', 'OR128': lambda s: ROOT / f'local/e2_OR128_bind3_s{s}_u8000.pt',
     'ORfull': lambda s: ROOT / f'local/e2_ORfull_bind3_s{s}_u8000.pt'}
SEEDS_E2 = (42, 43, 44)
D = 'bind3'


@torch.no_grad()
def random_chain(ops, split, steps):
    ws = worlds5(D, split); C = {s: cache5('bart', D, split, s) for s in S.states(D)}; state = [w['start_state'] for w in ws]
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots('bart', D, split).to(DEV); ar = torch.arange(len(ws), device=DEV); seqs = [[random.Random(3101 + i).random() < .5 for _ in range(steps)] for i in range(len(ws))]
    out = []
    for t in range(steps):
        dirs = [1 if seqs[i][t] else 0 for i in range(len(ws))]; prev = list(state); new = []
        for op in ('plus', 'minus'):
            idx = [i for i in range(len(ws)) if (op == 'plus') == bool(dirs[i])]
            if not idx: continue
            ix = torch.tensor(idx, device=DEV)
            o = ORop(ops[op].mod, ops[op].pos[ix], ops[op].npos[ix], ops[op].sign); hh = o(h[ix], m[ix], torch.tensor([prev[i] for i in idx], device=DEV)); h[ix] = hh
        state = [S.advance(D, s, 'plus' if dirs[i] else 'minus') for i, s in enumerate(prev)]
        out.append(dict(slot=h[ar, pos].double().cpu(), cur=torch.tensor(state), dir=torch.tensor(dirs)))
    return out


def fit_probe(Xtr, ytr, Xdv, ydv, K):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6; Z = lambda X: (X - mu) / sd; best = None
    for C in (0.01, 0.1, 1.0, 10.0):
        W, b = logreg(Z(Xtr), ytr, C, K); acc = float(((Z(Xdv) @ W + b).argmax(-1) == ydv).double().mean())
        if best is None or acc > best[0]: best = (acc, C, W, b)
    _, C, W, b = best; return dict(C=C, f=lambda X: (Z(X) @ W + b).argmax(-1))


def main():
    require_slurm(); assert lock_ok(); t0 = time.time(); res = {}
    man = manifold('bart', D, 'confirm7'); clean = man['Cw']
    for v, path in V.items():
        for s in SEEDS_E2:
            kind, ed = k_load(path(s), 768); ops = {sp: k_ops(kind, ed, slots('bart', D, sp), name_positions(D, sp)) for sp in ('train', 'dev', 'confirm7')}
            ch = {sp: random_chain(ops[sp], sp, 8 if sp != 'confirm7' else 100) for sp in ops}
            cat = lambda sp, k: torch.cat([c[k] for c in ch[sp]])
            pd = fit_probe(cat('train', 'slot'), cat('train', 'dir'), cat('dev', 'slot'), cat('dev', 'dir'), 2)
            pc = fit_probe(cat('train', 'slot'), cat('train', 'cur'), cat('dev', 'slot'), cat('dev', 'cur'), 3)
            acc = lambda p, y, c: float((p['f'](c['slot']) == c[y]).double().mean())
            rng = {'1-8': range(0, 8), '9-30': range(8, 30), '31-100': range(30, 100)}
            r = {f'direction_{k}': float(np.mean([acc(pd, 'dir', ch['confirm7'][t]) for t in ix])) for k, ix in rng.items()}
            r |= {f'current_{k}': float(np.mean([acc(pc, 'cur', ch['confirm7'][t]) for t in ix])) for k, ix in rng.items()}
            Xc = clean.reshape(-1, clean.shape[-1])
            r['direction_on_clean'] = float(pd['f'](Xc).double().mean())          # share predicted 'plus' on clean codes (no history): ~ 0.5 or a constant
            r['probe_C'] = dict(direction=pd['C'], current=pc['C']); res[f'{v}/s{s}'] = r
            print('E2b', v, s, {k: round(x, 3) for k, x in r.items() if isinstance(x, float)}, flush=True)
    med = lambda v, k: float(np.median([res[f'{v}/s{s}'][k] for s in SEEDS_E2]))
    res['_summary'] = {v: {k: med(v, k) for k in ('direction_1-8', 'direction_9-30', 'direction_31-100', 'current_1-8', 'current_9-30', 'current_31-100')} for v in V}
    s = res['_summary']; lower = s['OR128']['direction_1-8'] < s['OR32']['direction_1-8'] or s['ORfull']['direction_1-8'] < s['OR32']['direction_1-8']
    res['_reading'] = dict(residue_lower_in_horizon=lower, decay_slower_E2=read(ROOT / 'results/e2_run.json')['_reading']['decay_slower'],
                           text='higher rank lowers the residue but the decay does not slow: write fidelity is not the bottleneck' if lower else 'unexplained')
    res['_seconds'] = time.time() - t0; dump(ROOT / 'results/e2b.json', res); print(json.dumps(res['_summary']), res['_reading'], flush=True)


if __name__ == '__main__':
    main()
