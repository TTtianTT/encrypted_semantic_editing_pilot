"""Unit DO, pre-lock GPU step (PLAN v9 section 5; appendix B.2 of PLAN v7 with the v8 layer rule, DEVIATIONS 7 of v8). --model gemma|qwen.
Data: Gemma 2 2B IT - weekday template 0 (v1 train / dev, confirm7) and month-nat (v8 train / dev / confirm8): the data it has not seen in
v8. Qwen2.5-1.5B-Instruct - weekday and month template 0 and month-nat. confirm sets are only encoded (latents), never decoded here.
1. Slot positions (the single token that differs across the state variants of a world's prompt); worlds without one are excluded for that
   model (Qwen: 8 month-nat worlds; DEVIATIONS 2) -> data/do_worlds_<model>.json.
2. Reconstruction gate per domain: greedy repeat of the clean prompts (train and dev, every state) >= 0.99.
3. Layer: Gemma - layer 10 (v8's rule, fixed); Qwen - every second layer from 2 to L - 2, S-RRR-16 fitted on month train latents, dev
   single plus step; the median of the tied best layers (lower median).
4. Latents at the layer for every domain and split (all states); planes and amplitudes from train; r*_pred (Proposition 1, 5% rule);
   S-RRR-r fits on train for r in {N-4, ..., N, 16, r*_pred, r*_pred - 2}.
5. Editors at the layer (seeds 45-47): DO4 one-step CE slot editor (rank-16 affine on the slot latent, 600 updates, batch 8, AdamW 1e-3,
   clip 1, plus / minus alternating; admission dev single >= 0.90); DO5 slot C3-U4 (path kind uniform over plus^S / minus^S / alternating,
   S uniform in 1..4, CE of every step's target sentence plus the canonical L2 of the slot latent normalised by the mean squared step,
   lambda 1, 1200 updates; admission dev plus R_4 >= 0.90); one retrain with twice the updates, else 'cannot learn'.
Output: results/do_prep_<model>.json, local/do_<model>_<d>_<split>.pt, local/do_<model>_<d>_srrr.pt, local/do_<model>_<v>_<d>_s<s>.pt."""
import random
import time
from lib9 import worlds5, fit_srrr_X, next_idx, gram_planes, cbar_of, slot_pair, rstar_pred, BOOT_SEED
from dlib import *

DOMS = {'gemma': ['weekday', S.NAT], 'qwen': ['weekday', 'month', S.NAT], 'olmo': ['weekday', 'month', S.NAT], 'phi': ['weekday', 'month', S.NAT],
        'smol': ['weekday', 'month', S.NAT], 'mistral': ['weekday', 'month', S.NAT]}
CONF = lambda d: 'confirm8' if d == S.NAT else 'confirm7'


def ren(w, s): return S.render(w, s, 0)


def gate(eng, d, W, pos):
    ok = []
    for sp in ('train', 'dev'):
        for s in S.states(d):
            for lo in range(0, len(W[sp]), 64):
                ws = W[sp][lo:lo + 64]; ok += [success(o, w, s, d) for o, w in zip(eng.generate([ren(w, s) for w in ws]), ws)]
    return rate(ok)


def latents(eng, d, ws, pos, layers):
    per = {l: [] for l in layers}
    for s in S.states(d):
        z = {l: [] for l in layers}
        for lo in range(0, len(ws), 64):
            o = eng.latents([ren(w, s) for w in ws[lo:lo + 64]], pos[lo:lo + 64], layers)
            for l in layers: z[l].append(o[l])
        for l in layers: per[l].append(torch.cat(z[l]))
    return {l: torch.stack(per[l], 1).double() for l in layers}


@torch.no_grad()
def single(eng, d, ws, pos, X, layer, step, ops=('plus', 'minus'), bs=48):
    """Dev single step: per world, state x and op, the slot latent step(op, X[i, x]) injected into the prompt of x; target x +- 1."""
    jobs = [(i, x, op) for op in ops for x in range(X.shape[1]) for i in range(len(ws))]; ok = []
    for lo in range(0, len(jobs), bs):
        part = jobs[lo:lo + bs]; v = torch.stack([step(op, X[i, x]) for i, x, op in part]).float()
        outs = eng.generate([ren(ws[i], x) for i, x, _ in part], [pos[i] for i, _, _ in part], layer, v)
        ok += [success(o, ws[i], S.advance(d, x, op), d) for o, (i, x, op) in zip(outs, part)]
    return rate(ok)


@torch.no_grad()
def chain_rate(eng, d, ws, pos, X, layer, step, oplist, bs=48):
    st = [w['start_state'] for w in ws]; V = torch.stack([X[i, s] for i, s in enumerate(st)]); ok = [True] * len(ws)
    for op in oplist:
        st = [S.advance(d, s, op) for s in st]; V = torch.stack([step(op, v) for v in V]); outs = []
        for lo in range(0, len(ws), bs): outs += eng.generate([ren(w, w['start_state']) for w in ws[lo:lo + bs]], pos[lo:lo + bs], layer, V[lo:lo + bs].float())
        ok = [a and success(o, w, s, d) for a, o, w, s in zip(ok, outs, ws, st)]
    return rate(ok)


def lin(f):
    L, R, b = (f[k].double() for k in ('left', 'right', 'bias')); return lambda op, v: v + v @ L @ R + b


def train_editor(eng, d, ws, pos, X, layer, seed, unrolled, updates):
    ed = slot_pair(eng.d, seed).cuda(); opt = torch.optim.AdamW(ed.parameters(), lr=1e-3, weight_decay=0); rng = random.Random(seed); hist = []
    pool = [(i, x) for x in range(X.shape[1]) for i in range(len(ws))]; Xc = X.float().cuda()
    scale = {op: float((X[:, next_idx(d, op)] - X).square().mean()) for op in ('plus', 'minus')}
    for k in range(updates):
        if unrolled: pk = rng.choice(('plus', 'minus', 'alt')); S_ = rng.choice([1, 2, 3, 4]); seq = path_seq(pk, S_)
        else: seq = [('plus', 'minus')[k % 2]]
        bt = [rng.choice(pool) for _ in range(8)]; opt.zero_grad(set_to_none=True); st = [x for _, x in bt]; v = torch.stack([Xc[i, x] for i, x in bt]); ce = 0.; l2 = 0.
        for op in seq:
            st = [S.advance(d, s, op) for s in st]; mod = ed[op]; v = v + mod.b + mod.u(mod.v(v))
            ce = ce + eng.ce([ren(ws[i], x) for i, x in bt], [ren(ws[i], s) for (i, _), s in zip(bt, st)], [pos[i] for i, _ in bt], layer, v)
            if unrolled: l2 = l2 + (v - torch.stack([Xc[i, s] for (i, _), s in zip(bt, st)])).square().mean() / scale[op]
        loss = (ce + l2) / len(seq); assert torch.isfinite(loss); loss.backward(); gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), 1.0); opt.step()
        if k % 25 == 0 or k == updates - 1: hist.append(dict(step=k + 1, loss=float(loss), grad=float(gn), S=len(seq)))
    ed = ed.eval().requires_grad_(False)
    return ed, hist


def path_seq(kind, S_):
    return ['plus'] * S_ if kind == 'plus' else ['minus'] * S_ if kind == 'minus' else [('plus', 'minus')[i % 2] for i in range(S_)]


def main():
    require_slurm(); model = sys.argv[sys.argv.index('--model') + 1]; t0 = time.time(); eng = DEngine(model=model); res = dict(model=model, revision=eng.revision, domains={})
    W, P, keep = {}, {}, {}
    for d in DOMS[model]:
        for sp in ('train', 'dev', CONF(d)):
            ws = worlds5(d, sp); ps = [slot_position(eng, w, d) for w in ws]
            keep[f'{d}/{sp}'] = dict(kept=[w['world_id'] for w, p in zip(ws, ps) if p is not None], excluded=[w['world_id'] for w, p in zip(ws, ps) if p is None])
            W[d, sp] = [w for w, p in zip(ws, ps) if p is not None]; P[d, sp] = [p for p in ps if p is not None]
    dump(ROOT / f'data/do_worlds_{model}.json', keep); res['excluded'] = {k: len(v['excluded']) for k, v in keep.items()}
    for d in DOMS[model]:
        res['domains'][d] = dict(gate=gate(eng, d, {sp: W[d, sp] for sp in ('train', 'dev')}, None)); print('DO gate', model, d, res['domains'][d]['gate']['rate'], flush=True)
    if model == 'gemma': layer = 10; res['layer_rule'] = 'v8 rule (DEVIATIONS 7 of v8): layer 10'
    else:
        cands = list(range(2, eng.L - 1, 2)); Lt = latents(eng, 'month', W['month', 'train'], P['month', 'train'], cands); Ld = latents(eng, 'month', W['month', 'dev'], P['month', 'dev'], cands); sel = {}
        for l in cands:
            f, _ = fit_srrr_X(Lt[l], {op: next_idx('month', op) for op in ('plus', 'minus')}, [16])
            sel[l] = single(eng, 'month', W['month', 'dev'], P['month', 'dev'], Ld[l], l, lin(f['plus', 16]), ops=('plus',))['rate']; print('DO layer', l, sel[l], flush=True)
        best = max(sel.values()); tied = sorted(l for l, r in sel.items() if r == best); layer = tied[(len(tied) - 1) // 2]
        res['layer_rule'] = dict(profile=sel, tied=tied, rule='median of the tied best layers (lower median)')
    res['layer'] = layer; dump(ROOT / f'results/do_prep_{model}.json', res)
    for d in DOMS[model]:
        r = res['domains'][d]
        if r['gate']['rate'] < .99: r['skipped'] = 'reconstruction gate'; continue
        X = {sp: latents(eng, d, W[d, sp], P[d, sp], [layer])[layer] for sp in ('train', 'dev', CONF(d))}
        for sp, x in X.items(): save(ROOT / f'local/do_{model}_{d}_{sp}.pt', dict(latents=x, pos=P[d, sp], world_ids=[w['world_id'] for w in W[d, sp]], layer=layer))
        N = len(S.states(d)); Pl = gram_planes(cbar_of(X['train'])); cb = cbar_of(X['train']); nxt = next_idx(d, 'plus')
        amp = {k: dict(dim=B.shape[1], a=float(((cb @ B).square().sum(1).mean()).sqrt()), s=float(((X['train'][:, nxt] - X['train']) @ B).norm(dim=-1).mean())) for k, B in Pl}
        rp = rstar_pred(amp); ranks = sorted(set(range(N - 4, N + 1)) | {16, rp, rp - 2})
        fits, info = fit_srrr_X(X['train'], {op: next_idx(d, op) for op in ('plus', 'minus')}, ranks); save(ROOT / f'local/do_{model}_{d}_srrr.pt', dict(fits=fits, planes=Pl, ranks=ranks))
        r |= dict(amplitudes=amp, rstar_pred=rp, ranks=ranks, latents_sha256={sp: sha(ROOT / f'local/do_{model}_{d}_{sp}.pt') for sp in X},
                  base_dev_single=single(eng, d, W[d, 'dev'], P[d, 'dev'], X['dev'], layer, lin(fits['plus', 16]), ops=('plus',)))
        r['editors'] = {}
        for v, unr, upd in (('C1', False, 600), ('C3U4', True, 1200)):
            for s in (45, 46, 47):
                def run(u):
                    ed, hist = train_editor(eng, d, W[d, 'train'], P[d, 'train'], X['train'], layer, s, unr, u); edc = {op: m.cpu().double() for op, m in ed.items()}
                    step = lambda op, x: x + edc[op].b + edc[op].u(edc[op].v(x))
                    dv = single(eng, d, W[d, 'dev'], P[d, 'dev'], X['dev'], layer, step) if not unr else chain_rate(eng, d, W[d, 'dev'], P[d, 'dev'], X['dev'], layer, step, ['plus'] * 4)
                    f = ROOT / f'local/do_{model}_{v}_{d}_s{s}.pt'; save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, layer=layer, variant=v, updates=u, dev=dv))
                    write(f'results/train_new/do_{model}_{v}_{d}_s{s}_u{u}.jsonl', hist); return dv, f
                dv, f = run(upd); rec = dict(updates=upd, dev=dv, admitted=dv['rate'] >= .90)
                if not rec['admitted']: dv2, f = run(2 * upd); rec = dict(updates=2 * upd, dev=dv2, first=dv, admitted=dv2['rate'] >= .90, note=None if dv2['rate'] >= .90 else 'cannot learn')
                rec['sha256'] = sha(f); r['editors'][f'{v}/s{s}'] = rec; print('DO editor', model, d, v, s, rec['updates'], dv['rate'], rec['admitted'], flush=True)
                dump(ROOT / f'results/do_prep_{model}.json', res)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(ROOT / f'results/do_prep_{model}.json', res)


if __name__ == '__main__':
    main()
