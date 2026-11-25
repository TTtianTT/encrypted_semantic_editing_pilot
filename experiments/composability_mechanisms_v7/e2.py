"""E2 (exploratory; plan change 2026-11-25, PLAN.md end; BART, GPU <= 0.5 h): the binding write rank.
--stage train (before the lock): OR-U8 of v7 K7 (oracle routing, S <= 8, 8000 updates, AdamW 1e-3, batch 16, clip 1, unrolled L2; bind3
train) with the UV rank raised from 32 to 128, and a full-rank version (UV replaced by one zero-initialised d x d map); seeds 42-44 (a new
editor family, so no data-order hash repeats). Dev single step reported (not gated).
--stage run (after the lock): see run() in this file. Output: local/e2_<OR128|ORfull>_bind3_s<s>_u8000.pt, results/e2_train.json."""
import time
from lib8 import *

VARIANTS = {'OR128': 128, 'ORfull': None}
SEEDS_E2 = (42, 43, 44)


def epath(v, s):
    return ROOT / f'local/e2_{v}_bind3_s{s}_u8000.pt'


def train(eng):
    out = ROOT / 'results/e2_train.json'; res = read(out) if out.exists() else {}
    for v, rank in VARIANTS.items():
        for s in SEEDS_E2:
            key = f'{v}/s{s}'
            if key in res and epath(v, s).exists(): continue
            t0 = time.time(); ed, hist = train_k('bind3', s, 'OR', updates=8000, Sset=tuple(range(1, 9)), rank=rank)
            r = dev_single(eng, 'bart', 'bind3', 'natural', k_ops('OR', ed, slots('bart', 'bind3', 'dev'), name_positions('bind3', 'dev')))
            save(epath(v, s), dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind='OR', rank=rank, name=v, Sset=list(range(1, 9)), dev_single=r, updates=8000))
            write(f'results/train_new/e2_{v}_bind3_s{s}_u8000.jsonl', hist)
            res[key] = dict(dev_single=r, seconds=time.time() - t0, sha256=sha(epath(v, s))); dump(out, res); print('E2 train', key, round(r['rate'], 4), flush=True)
    res['_resources'] = eng.resources(); dump(out, res)


@torch.no_grad()
def chain_states(ed_ops, d, split, steps, eng=None):
    """Plus chain from the world start on a split. Returns per step the slot vectors (W, dim), gold state, previous state, and (if eng)
    the decoded trajectory success."""
    ws = worlds5(d, split); C = {s: cache5('bart', d, split, s) for s in S.states(d)}; state = [w['start_state'] for w in ws]; t = tmpl(d)
    h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).to(DEV); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).to(DEV)
    pos = slots('bart', d, split).to(DEV); ar = torch.arange(len(ws), device=DEV); ok = [True] * len(ws); out = []
    for k in range(steps):
        prev = list(state); state = [S.advance(d, s, 'plus') for s in state]; h = apply_op(ed_ops['plus'], h, m, torch.tensor(prev, device=DEV))
        rec = dict(slot=h[ar, pos].double().cpu(), gold=list(state), prev=prev)
        if eng is not None:
            o = dec(eng, h, m); ok = [a and Ev.score(o[j]['text'], S.gold(w, state[j], t), w, o[j]['ended'])['success'] for j, (a, w) in enumerate(zip(ok, ws))]
            rec['R'] = float(np.mean(ok))
        out.append(rec)
    return out


def run(eng):
    """After the lock (exploratory). bind3 confirm7, plus 100 steps, for OR-U8 rank 32 (v7 K7, reference), rank 128 and full rank, seeds
    42-44: R_30, R_100; per step the median distance ||slot - E_w(gold)|| / R_w; old-name residue: a linear probe fitted on train chains
    (the editor's own plus chains, steps 1-8, slot vector -> previous state's list index; ridge C chosen on dev chains from {0.01, 0.1, 1, 10})
    read on the confirm7 chain at every step (accuracy; chance 1/3), with the same probe trained for the current state as a control."""
    assert lock_ok(); man = manifold('bart', 'bind3', 'confirm7'); R_w = man['R']; ar = torch.arange(len(R_w)); res = {}
    eds = {f'OR32/s{s}': V7DIR / f'local/k7_ORU8_bind3_s{s}_u8000.pt' for s in SEEDS_E2} | {f'{v}/s{s}': epath(v, s) for v in VARIANTS for s in SEEDS_E2}
    for key, p in eds.items():
        kind, ed = k_load(p, eng.d); ops = {sp: k_ops(kind, ed, slots('bart', 'bind3', sp), name_positions('bind3', sp)) for sp in ('train', 'dev', 'confirm7')}
        fit = {}
        for sp in ('train', 'dev'):
            ch = chain_states(ops[sp], 'bind3', sp, 8); fit[sp] = (torch.cat([c['slot'] for c in ch]), torch.tensor([x for c in ch for x in c['prev']]), torch.tensor([x for c in ch for x in c['gold']]))
        mu, sd = fit['train'][0].mean(0), fit['train'][0].std(0) + 1e-6; Z = lambda X: (X - mu) / sd; probes = {}
        for tgt, col in (('prev', 1), ('gold', 2)):
            best = max((0.01, 0.1, 1.0, 10.0), key=lambda C: float(((Z(fit['dev'][0]) @ logreg(Z(fit['train'][0]), fit['train'][col], C, 3)[0] + logreg(Z(fit['train'][0]), fit['train'][col], C, 3)[1]).argmax(-1) == fit['dev'][col]).double().mean()))
            probes[tgt] = (best,) + logreg(Z(fit['train'][0]), fit['train'][col], best, 3)
        ch = chain_states(ops['confirm7'], 'bind3', 'confirm7', 100, eng)
        dist, prev_acc, gold_acc = [], [], []
        for c in ch:
            g = torch.tensor(c['gold']); dist.append(float(((c['slot'] - man['Cw'][ar, g]).norm(dim=-1) / R_w).median()))
            for tgt, acc in (('prev', prev_acc), ('gold', gold_acc)):
                _, W, b = probes[tgt]; y = torch.tensor(c[tgt]); acc.append(float(((Z(c['slot']) @ W + b).argmax(-1) == y).double().mean()))
        res[key] = dict(R30=ch[29]['R'], R100=ch[99]['R'], R=[c['R'] for c in ch], distance=dist, old_name_probe=prev_acc, current_name_probe=gold_acc,
                        probe_C={t: probes[t][0] for t in probes}); print('E2 run', key, round(ch[29]['R'], 3), round(ch[99]['R'], 3), flush=True)
    med = lambda v, k: float(np.median([res[f'{v}/s{s}'][k] for s in SEEDS_E2]))
    res['_summary'] = {v: dict(R30=med(v, 'R30'), R100=med(v, 'R100')) for v in ('OR32', 'OR128', 'ORfull')}
    r = res['_summary']; slower = r['OR128']['R100'] > r['OR32']['R100'] or r['ORfull']['R100'] > r['OR32']['R100']
    res_old = {v: float(np.median([np.mean(res[f'{v}/s{s}']['old_name_probe'][9:]) for s in SEEDS_E2])) for v in ('OR32', 'OR128', 'ORfull')}
    res['_reading'] = dict(decay_slower=slower, old_name_residue=res_old, residue_lower=min(res_old['OR128'], res_old['ORfull']) < res_old['OR32'],
                           text='supports the write-fidelity reading' if slower and min(res_old['OR128'], res_old['ORfull']) < res_old['OR32'] else 'unexplained')
    res['_resources'] = eng.resources(); dump(ROOT / 'results/e2_run.json', res)


def main():
    require_slurm(); stage = sys.argv[sys.argv.index("--stage") + 1]; eng = engine8("bart")
    if stage == "train": return train(eng)
    assert stage == "run"; return run(eng)


if __name__ == '__main__':
    main()
