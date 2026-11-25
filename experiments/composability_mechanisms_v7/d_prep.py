"""Unit D, pre-lock GPU step (exploratory; PLAN v7 C4, appendix B.2; month template 0: v1 train / dev, confirm7 = the 160 evaluation
worlds, first evaluation for this model; plan change 2026-11-25).
1. Slot positions (the month token of the user message; single-token check) for train, dev, confirm7.
2. Reconstruction gate (B.2 step 7): greedy repeat of the clean prompts, train and dev, every state; >= 0.99.
3. Slot latents after every second layer (2, 4, ..., 24) for train, dev and confirm7 (confirm7 only encoded, never decoded before the lock).
4. Layer selection (B.2 step 6): per candidate layer S-RRR-16 (fit_srrr_X on the train slot vectors) and its dev single plus step; the layer
   with the highest success, ties to the shallower; continue iff the gate passed and the chosen layer's single step >= 0.90.
5. If continuing: the CE slot editors (rank-16 affine on the slot latent, trained through the upper layers and teacher-forced generation;
   600 updates, batch 8, AdamW 1e-3, clip 1, plus and minus alternating; seeds 50-52; dev single step reported).
Output: results/d_prep.json, local/d_latents_<split>.pt, local/d_srrr_l<l>.pt, local/d_C1_s<s>.pt."""
import random
import time
from lib8 import worlds5, fit_srrr_X, next_idx, slot_pair, BOOT_SEED
from dlib import *

D = 'month'
LAYERS = list(range(2, 25, 2))
SPLITS = ('train', 'dev', 'confirm7')


def single_plus(eng, ws, pos, X, f, layer, bs=48):
    """Dev single plus step: per world and state x, the edited slot (S-RRR fit f) injected into the prompt of x; target x + 1."""
    N = X.shape[1]; L, R, b = (f[k].double() for k in ('left', 'right', 'bias')); ok = []
    jobs = [(i, x) for x in range(N) for i in range(len(ws))]
    for lo in range(0, len(jobs), bs):
        part = jobs[lo:lo + bs]; xs = torch.stack([X[i, x] for i, x in part]); v = (xs + xs @ L @ R + b).float()
        outs = eng.generate([S.render(ws[i], x, 0) for i, x in part], [pos[i] for i, _ in part], layer, v)
        ok += [success(o, ws[i], S.advance(D, x, 'plus')) for o, (i, x) in zip(outs, part)]
    return rate(ok)


def train_c1(eng, ws, pos, X, layer, seed, updates=600, batch=8, lr=1e-3, clip=1.0):
    ed = slot_pair(eng.d, seed).cuda(); opt = torch.optim.AdamW(ed.parameters(), lr=lr, weight_decay=0); rng = random.Random(seed); hist = []
    pool = [(i, x) for x in range(X.shape[1]) for i in range(len(ws))]
    for k in range(updates):
        op = ('plus', 'minus')[k % 2]; bt = [rng.choice(pool) for _ in range(batch)]; opt.zero_grad(set_to_none=True)
        hs = torch.stack([X[i, x] for i, x in bt]).float().cuda(); mod = ed[op]; v = hs + mod.b + mod.u(mod.v(hs))
        loss = eng.ce([S.render(ws[i], x, 0) for i, x in bt], [S.render(ws[i], S.advance(D, x, op), 0) for i, x in bt], [pos[i] for i, _ in bt], layer, v)
        assert torch.isfinite(loss); loss.backward(); gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), clip); opt.step()
        if k % 25 == 0 or k == updates - 1: hist.append(dict(step=k + 1, op=op, loss=float(loss), grad=float(gn)))
    return ed.eval().requires_grad_(False), hist


@torch.no_grad()
def c1_single(eng, ws, pos, X, ed, layer, bs=48):
    ok = []; jobs = [(i, x, op) for op in ('plus', 'minus') for x in range(X.shape[1]) for i in range(len(ws))]
    for lo in range(0, len(jobs), bs):
        part = jobs[lo:lo + bs]; hs = torch.stack([X[i, x] for i, x, _ in part]).float().cuda()
        v = torch.stack([hs[j] + ed[op].b + ed[op].u(ed[op].v(hs[j])) for j, (_, _, op) in enumerate(part)])
        outs = eng.generate([S.render(ws[i], x, 0) for i, x, _ in part], [pos[i] for i, _, _ in part], layer, v)
        ok += [success(o, ws[i], S.advance(D, x, op)) for o, (i, x, op) in zip(outs, part)]
    return rate(ok)


def main():
    require_slurm(); t0 = time.time(); eng = DEngine(); res = dict(revision=eng.revision, layers=LAYERS)
    W = {sp: worlds5(D, sp) for sp in SPLITS}; pos = {}
    for sp in SPLITS:
        pos[sp] = [slot_position(eng, w) for w in W[sp]]; res.setdefault('slot_not_single', {})[sp] = sum(p is None for p in pos[sp])
    assert all(v == 0 for v in res['slot_not_single'].values()), res['slot_not_single']
    ok = []
    for sp in ('train', 'dev'):
        for s in S.states(D):
            for lo in range(0, len(W[sp]), 64):
                ws = W[sp][lo:lo + 64]; ok += [success(o, w, s) for o, w in zip(eng.generate([S.render(w, s, 0) for w in ws]), ws)]
    res['reconstruction'] = rate(ok); res['gate'] = res['reconstruction']['rate'] >= .99; print('D gate', res['reconstruction'], flush=True)
    lat = {}
    for sp in SPLITS:
        per = {l: [] for l in LAYERS}
        for s in S.states(D):
            z = {l: [] for l in LAYERS}
            for lo in range(0, len(W[sp]), 64):
                ws = W[sp][lo:lo + 64]; o = eng.latents([S.render(w, s, 0) for w in ws], pos[sp][lo:lo + 64], LAYERS)
                for l in LAYERS: z[l].append(o[l])
            for l in LAYERS: per[l].append(torch.cat(z[l]))
        lat[sp] = {l: torch.stack(per[l], 1).double() for l in LAYERS}                      # (W, N, d)
        save(ROOT / f'local/d_latents_{sp}.pt', dict(latents=lat[sp], pos=pos[sp], world_ids=[w['world_id'] for w in W[sp]]))
    res['latents_sha256'] = {sp: sha(ROOT / f'local/d_latents_{sp}.pt') for sp in SPLITS}
    nxt = {op: next_idx(D, op) for op in ('plus', 'minus')}; sel = {}
    for l in LAYERS:
        f, info = fit_srrr_X(lat['train'][l], nxt, [16]); save(ROOT / f'local/d_srrr_l{l}.pt', f)
        sel[l] = single_plus(eng, W['dev'], pos['dev'], lat['dev'][l], f['plus', 16], l); print('D layer', l, sel[l]['rate'], flush=True)
    best = max(LAYERS, key=lambda l: (sel[l]['rate'], -l))
    res |= dict(layer_selection={str(l): v for l, v in sel.items()}, layer=best, continue_=bool(res['gate'] and sel[best]['rate'] >= .90))
    dump(ROOT / 'results/d_prep.json', res | dict(resources=eng.resources(), seconds=time.time() - t0))
    if not res['continue_']: return
    res['C1'] = {}
    for s in (50, 51, 52):
        ed, hist = train_c1(eng, W['train'], pos['train'], lat['train'][best], best, s); r = c1_single(eng, W['dev'], pos['dev'], lat['dev'][best], ed, best)
        save(ROOT / f'local/d_C1_s{s}.pt', dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, layer=best, dev_single=r, updates=600))
        write(f'results/train_new/d_C1_s{s}.jsonl', hist); res['C1'][f's{s}'] = dict(dev_single=r, sha256=sha(ROOT / f'local/d_C1_s{s}.pt'))
        print('D C1', s, r['rate'], flush=True); dump(ROOT / 'results/d_prep.json', res | dict(resources=eng.resources(), seconds=time.time() - t0))


if __name__ == '__main__':
    main()
