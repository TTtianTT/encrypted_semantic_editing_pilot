"""K: robustness and mechanism of the binding result (Q23; BART; PLAN v7 B9, appendix A.8). --mode precheck|run|smoke.
Editors (cells7.k_cells7): Att2L-U8, Att2L-U4, Att1-U8 with v7 seeds 45-49 and v6 seeds 42-44; OR-U8 (diagnostic) seeds 42-44.
run (after the lock), confirm7: bind3 plus 100, minus 30, alternating 30; name3 and bind3fix plus 30 (shards). Layer-2 ablations of Att2L-U8
(a: uniform attention over non-pad positions, b: self only, c: the layer-2 term removed; no retraining) on bind3 plus 30 (all 8 seeds;
(c) is K8, (a) and (b) exploratory). Exploratory: the contraction curve d_t = ||slot_t - E_w(gold_t)|| / R_w over 100 steps; the layer-1
and layer-2 attention mass of the slot on the current / next / previous list name and elsewhere; bind4 zero-shot (skipped: the v4 X
generator has no four-name lists; recorded).
precheck (before the lock; dev worlds; design rule 1): dev R_30 on bind3 of every editor and of Att2L-U8 with ablation (c). Ablation (c)
leaves only the token-wise term b + U V h (layer 1 reaches the output only through layer 2), i.e. a token-wise editor; if every seed is at
<= 0.50 on dev while the full editor is not, K8 is decided by construction and becomes exploratory before the lock.
smoke: run mode on dev with short chains (code path only)."""
import time
from collections import defaultdict
from lib7 import *
from cells7 import k_cells7, K7_PATHS
from devchains import decode_chain


def attention_mass(mod, d, split, layer):
    ws = worlds5(d, split); pos = slots('bart', d, split); npos = name_positions(d, split); out = defaultdict(list)
    for s in S.states(d):
        c = cache5('bart', d, split, s); z0, z, a1, a2 = mod.layers(c['h'].to(DEV).float(), c['m'].to(DEV)); a = a1 if layer == 1 else a2
        for i in range(len(ws)):
            row = a[i, int(pos[i])].cpu(); lp = npos[i].tolist()
            v = dict(current=float(row[lp[s]]), next=float(row[lp[(s + 1) % 3]]), prev=float(row[lp[(s - 1) % 3]])); v['other'] = 1 - sum(v.values())
            for k, x in v.items(): out[k].append(x)
    return {k: float(np.mean(v)) for k, v in out.items()}


@torch.no_grad()
def contraction(ops, d, split, steps=100):
    ws = worlds5(d, split); C = {s: cache5('bart', d, split, s) for s in S.states(d)}; state = [w['start_state'] for w in ws]
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots('bart', d, split).to(DEV); man = manifold('bart', d, split); ar = torch.arange(len(ws), device=DEV); dt = []
    for _ in range(steps):
        prev = torch.tensor(state, device=DEV); state = [S.advance(d, s, 'plus') for s in state]; h = apply_op(ops['plus'], h, m, prev)
        g = torch.tensor(state, device=DEV); Eg = man['Cw'].to(DEV)[ar, g]; dt.append(float(((h[ar, pos].double() - Eg).norm(dim=-1) / man['R'].to(DEV)).median()))
    return dt


def ablated(ops, mode):
    return {op: Att2LAblated(ops[op], mode) for op in ('plus', 'minus')}


def main():
    require_slurm(); mode = sys.argv[sys.argv.index('--mode') + 1]; t0 = time.time(); eng = engine5('bart'); out = dict(mode=mode, cells={}, exploratory={})
    if mode == 'run': assert lock_ok()
    split = CONFIRM if mode == 'run' else 'dev'
    for d, name, kind, ops in k_cells7(eng, split):
        if mode in ('precheck', 'smoke') and d != 'bind3': continue
        ops = ops() if callable(ops) else ops
        if mode == 'run':
            for path, ol in K7_PATHS[d].items():
                run_chain(eng, 'bart', d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol)
                out['cells'][f'{d}/{name}/{path}'] = {f'R{k}': chain_rate('bart', d, 'natural', name, f'{path}_from_start', k)['rate'] for k in (1, 6, 8, 12, 30, 100) if k <= len(ol)}
            if d == 'bind3':
                out['exploratory'][f'contraction/{name}'] = contraction(ops, d, split)
                if kind == 'Att2LU8':
                    for am in ('drop', 'uniform', 'self'):
                        an = name.replace(kind, f'{kind}-abl{am}'); run_chain(eng, 'bart', d, 'natural', an, ablated(ops, am), 'plus_from_start', 'world_start', ['plus'] * 30)
                        out['cells'][f'{d}/{an}/plus'] = {f'R{k}': chain_rate('bart', d, 'natural', an, 'plus_from_start', k)['rate'] for k in (1, 8, 30)}
                    out['exploratory'][f'attention/{name}'] = {f'layer{l}': attention_mass(ops['plus'], d, split, l) for l in (1, 2)}
        else:
            L = 30 if mode == 'precheck' else 6; ok, _, _ = decode_chain(eng, 'bart', d, ops, ['plus'] * L, split); out['cells'][f'{d}/{name}/plus'] = {f'R{L}': rate(ok)['rate']}
            if kind == 'Att2LU8':
                ok, _, _ = decode_chain(eng, 'bart', d, ablated(ops, 'drop'), ['plus'] * L, split); out['cells'][f"{d}/{name.replace(kind, kind + '-abldrop')}/plus"] = {f'R{L}': rate(ok)['rate']}
        print('K', mode, d, name, {k: v for k, v in out['cells'].items() if k.startswith(f'{d}/{name}')}, flush=True)
    if mode == 'precheck':
        full = [v['R30'] for k, v in out['cells'].items() if '/Att2LU8_' in k and 'abl' not in k]; abl = [v['R30'] for k, v in out['cells'].items() if 'abldrop' in k]
        out['K8_precheck'] = dict(full_R30=full, ablated_R30=abl, decided_by_construction=bool(abl) and max(abl) <= .5 and max(full) > .5)
    out['exploratory']['bind4'] = 'skipped: the v4 X world generator has no four-name lists'
    out['seconds'] = time.time() - t0; out['resources'] = eng.resources()
    dump(ROOT / ('local/smoke' if mode == 'smoke' else 'results') / f'k_{mode}.json', out)


if __name__ == '__main__':
    main()
