"""S3 (GPU): what does the CE-only editor C1 write? v1 C1 (5 domains x seeds 42-44) on confirm2, RRR-16 and canonical writes as
controls. M1 write state-independence, M2 write direction, M3 source/target probe, M4 transplant, M5 push scaling, M6 position,
M7 wrap-around visibility (M5-M7 exploratory)."""
import time
import torch
import torch.nn.functional as Fn
from symutil import *
import sym2_semantics as S
import sym2_evaluator as Ev

ALPHAS = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
CS = [0.01, 0.1, 1.0, 10.0]


def editors_for(eng, d):
    source_path(); from backend import editors
    out = {}
    for s in SEEDS:
        ed = editors(eng.d, s); ed.load_state_dict(load(V1 / f'local/e1_C1_{d}_s{s}_0600.pt')['editor']); out[f'C1_s{s}'] = ed.eval().requires_grad_(False)['plus']
    f = load(ROOT / f'local/rrr_{d}_natural.pt'); out['RRR16'] = RRRop(f['plus', 16])
    return out


def logreg(X, y, C, K, iters=300):
    W = torch.zeros(X.shape[1], K, dtype=torch.float64, device=X.device, requires_grad=True); b = torch.zeros(K, dtype=torch.float64, device=X.device, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], max_iter=iters, line_search_fn='strong_wolfe', tolerance_grad=1e-9)
    def closure():
        opt.zero_grad(); loss = Fn.cross_entropy(X @ W + b, y) + (W ** 2).sum() / (2 * C * len(X)); loss.backward(); return loss
    opt.step(closure)
    return W.detach(), b.detach()


def probe(d):
    pos = slot_pos(d, 0); st = S.states(d)
    def data(split):
        X = torch.cat([cache2(d, split, s)['h'][:, pos].double() for s in st]); y = torch.cat([torch.full((len(cache2(d, split, s)['h']),), i) for i, s in enumerate(st)])
        w = torch.cat([torch.arange(len(cache2(d, split, s)['h'])) for s in st]); return X.cuda(), y.cuda(), w
    X, y, w = data('train'); mu, sd = X.mean(0), X.std(0).clamp_min(1e-6); Xs = (X - mu) / sd; folds = (w % 5).cuda(); cv = {}
    for C in CS:
        acc = []
        for f in range(5):
            tr = folds != f; Wt, bt = logreg(Xs[tr], y[tr], C, len(st)); acc.append(float(((Xs[~tr] @ Wt + bt).argmax(1) == y[~tr]).float().mean()))
        cv[C] = float(np.mean(acc))
    Cb = max(CS, key=lambda c: (cv[c], -c)); Wt, bt = logreg(Xs, y, Cb, len(st))
    Xd, yd, _ = data('dev'); dev_acc = float((((Xd - mu) / sd @ Wt + bt).argmax(1) == yd).float().mean())
    return dict(C=Cb, cv_accuracy={str(k): v for k, v in cv.items()}, dev_accuracy=dev_acc), (lambda Z: (((Z.double() - mu) / sd) @ Wt + bt).argmax(1).cpu().numpy())


def cos(a, b):
    return Fn.cosine_similarity(a.flatten(1).double(), b.flatten(1).double(), dim=1)


def category(text, d, w, src, nxt, nn_):
    p, g = Ev.parse(text, d, 0)
    if p is None or not g: return 'unparsable'
    v = p['value']
    return 'source' if v == src else 'next' if v == nxt else 'next_next' if nn_ is not None and v == nn_ else 'other'


@torch.no_grad()
def main():
    require_slurm(); p = verify_protocol2(); t0 = time.time(); eng = engine(); C_ = core(); res = {}
    for d in V1_DOMAINS:
        ws = worlds2(d, 'confirm2'); n = len(ws); pos = slot_pos(d, 0); st = S.states(d); N = len(st)
        Cc = {s: cache2(d, 'confirm2', s) for s in st}; H = {s: Cc[s]['h'].cuda() for s in st}; M = Cc[st[0]]['m'].cuda()
        for s in st: assert torch.equal(Cc[s]['m'].cuda(), M)
        legal = [s for s in st if (S.advance(d, s, 'plus') if not (d == 'daysago' and s == 9) else None) is not None]
        g = {s: S.advance(d, s, 'plus') for s in legal}; v = M[..., None]
        with torch.enable_grad(): pinfo, predict = probe(d)
        res[f'{d}/probe'] = pinfo
        for name, T in editors_for(eng, d).items():
            Wr = {s: (T(H[s], M) - H[s]) * v for s in legal}; Wc = {s: (H[g[s]] - H[s]) * v for s in legal}; r = dict(domain=d, method=name)
            # M1: pairwise cosine between writes of different source states, per world
            pc = torch.stack([cos(Wr[a], Wr[b]) for i, a in enumerate(legal) for b in legal[i + 1:]], 1).mean(1).cpu().numpy(); r['M1'] = boot_mean(pc)
            # M2: cosine with the canonical write; per-world mean over sources, median over worlds
            cw = torch.stack([cos(Wr[s], Wc[s]) for s in legal], 1).mean(1).cpu().numpy()
            r['M2'] = dict(median=float(np.median(cw)), ci95=boot_stat(lambda i: np.median(cw[i]), n)['ci95'], mean=float(cw.mean()))
            # M3: probe readout on the first-step state
            lab = {s: i for i, s in enumerate(st)}; src = tgt = oth = 0
            for s in legal:
                pr = predict((H[s] + Wr[s])[:, pos]); src += int((pr == lab[s]).sum()); tgt += int((pr == lab[g[s]]).sum()); oth += int(((pr != lab[s]) & (pr != lab[g[s]])).sum())
            tot = src + tgt + oth; r['M3'] = dict(source=src / tot, target=tgt / tot, other=oth / tot, n=tot)
            # M4: transplant within world (x' != x) and across worlds (w' = next world)
            ok = []; cross = []
            for s in legal:
                for s2 in legal:
                    if s2 == s: continue
                    out = eng.decode(H[s2] + Wr[s], M); ok += [Ev.score(o['text'], S.gold(w, g[s2], 0), w, o['ended'])['success'] for o, w in zip(out, ws)]
                perm = [(i + 1) % n for i in range(n)]; out = eng.decode(H[s][perm] + Wr[s], M)
                cross += [Ev.score(o['text'], S.gold(ws[perm[i]], g[s], 0), ws[perm[i]], o['ended'])['success'] for i, o in enumerate(out)]
            r['M4_same_world'] = rate(ok); r['M4_cross_world'] = rate(cross)
            # M5: push scaling
            cats = {}
            for a in ALPHAS:
                c = {}
                for s in legal:
                    nn_ = g.get(g[s]) if g[s] in g else None
                    for o, w in zip(eng.decode(H[s] + a * Wr[s], M), ws):
                        k = category(o['text'], d, w, s, g[s], nn_); c[k] = c.get(k, 0) + 1
                tot = sum(c.values()); cats[str(a)] = {k: x / tot for k, x in c.items()}
            r['M5'] = cats
            # M6: write applied only at the slot, or only elsewhere
            slot_mask = torch.zeros_like(M); slot_mask[:, pos] = 1; res6 = {}
            for where, mk in (('slot_only', slot_mask), ('non_slot_only', M * (1 - slot_mask))):
                okk = []
                for s in legal:
                    out = eng.decode(H[s] + Wr[s] * mk[..., None], M); okk += [Ev.score(o['text'], S.gold(w, g[s], 0), w, o['ended'])['success'] for o, w in zip(out, ws)]
                res6[where] = rate(okk)
            r['M6'] = res6
            # M7: wrap-around visibility of r = T(E(x)) - E(g x) at x = world start (first legal state if start has no successor)
            x = [w['start_state'] if w['start_state'] in g else legal[0] for w in ws]
            base = torch.stack([H[s][i] for i, s in enumerate(x)]); resid = (T(base, M) - torch.stack([H[g[s]][i] for i, s in enumerate(x)])) * v
            gen = torch.Generator(device='cuda').manual_seed(BOOT_SEED); rnd = torch.randn(resid.shape, generator=gen, device='cuda', dtype=resid.dtype) * v
            rnd = rnd * (resid.flatten(1).norm(dim=1) / rnd.flatten(1).norm(dim=1))[:, None, None]; vis = {}
            for k in range(N):
                z = [st[(st.index(s) + k) % N] for s in x]; Hz = torch.stack([H[s][i] for i, s in enumerate(z)]); texts = [S.render(w, s, 0) for w, s in zip(ws, z)]
                ref, lab_ = C_.logits(eng, Hz, M, texts)
                kr = [q['KL'] for q in C_.distribution(ref, C_.logits(eng, Hz + resid, M, texts)[0], lab_)]
                kn = [q['KL'] for q in C_.distribution(ref, C_.logits(eng, Hz + rnd, M, texts)[0], lab_)]
                vis[str(k)] = dict(median_KL_real=float(np.median(kr)), median_KL_random=float(np.median(kn)))
            r['M7'] = dict(by_offset=vis, residual_norm_median=float(resid.flatten(1).norm(dim=1).median()))
            res[f'{d}/{name}'] = r
            print(d, name, 'M1', round(r['M1']['mean'], 3), 'M2', round(r['M2']['median'], 3), 'M3', {k: round(v_, 3) for k, v_ in r['M3'].items() if k != 'n'},
                  'M4', r['M4_same_world']['rate'], flush=True)
    res['_seconds'] = time.time() - t0; res['_resources'] = eng.resources()
    dump('results/s3_mechanism.json', res)


if __name__ == '__main__':
    main()
