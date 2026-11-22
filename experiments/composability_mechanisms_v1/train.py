"""S1b C1 (CE) and C3 (CE + normalized canonical L2, weight 1) editors; seeds 42-44; v1 training configuration. Template 0, train only."""
import random
import time
import torch
from symutil import *
import sym2_semantics as S
import sym2_evaluator as Ev


def token_mse(h, y, m):
    return ((h - y).square() * m[..., None]).sum((1, 2)) / (m.sum(1) * h.shape[-1])


def stack(items, caches):
    return (torch.stack([caches[s]['h'][i] for i, s in items]).cuda(), torch.stack([caches[s]['m'][i] for i, s in items]).cuda())


@torch.no_grad()
def dev_single(eng, d, ed):
    ws = worlds2(d, 'dev'); C = {s: cache2(d, 'dev', s) for s in S.states(d)}; ok = []
    for s in S.states(d):
        for op in ('plus', 'minus'):
            y = S.advance(d, s, op); h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); out = eng.decode(ed[op](h, m), m)
            ok += [Ev.score(o['text'], S.gold(w, y, 0), w, o['ended'])['success'] for o, w in zip(out, ws)]
    return rate(ok)


def main():
    require_slurm(); p = verify_protocol2(); cfg = p['training']; eng = engine(); source_path(); from backend import editors
    for d in S1B_DOMAINS:
        ws = worlds2(d, 'train'); caches = {s: cache2(d, 'train', s) for s in S.states(d)}
        pool = {op: [(i, s) for s in S.states(d) for i in range(len(ws))] for op in ('plus', 'minus')}
        scale = {}
        with torch.no_grad():
            for op, its in pool.items():
                h, m = stack(its, caches); y, _ = stack([(i, S.advance(d, s, op)) for i, s in its], caches); scale[op] = float(token_mse(h, y, m).mean())
        for group in cfg['groups']:
            for seed in cfg['seeds']:
                done = ROOT / f'results/train_{group}_{d}_s{seed}_complete.json'
                if done.exists(): continue
                ed = editors(eng.d, seed); opt = torch.optim.AdamW(ed.parameters(), lr=cfg['lr'], weight_decay=cfg['weight_decay']); rng = random.Random(seed); hist = []
                t0 = time.time()
                for k in range(cfg['updates']):
                    op = ('plus', 'minus')[k % 2]; batch = [rng.choice(pool[op]) for _ in range(cfg['batch'])]
                    opt.zero_grad(set_to_none=True); tot = dict(ce=0., l2_normalized=0., loss=0.)
                    for lo in range(0, cfg['batch'], cfg['microbatch']):
                        part = batch[lo:lo + cfg['microbatch']]; h, m = stack(part, caches); tgt = [(i, S.advance(d, s, op)) for i, s in part]
                        y, ym = stack(tgt, caches); assert torch.equal(m, ym); edited = ed[op](h, m)
                        ce = eng.ce(edited, m, [S.render(ws[i], s, 0) for i, s in tgt])[0].mean(); l2 = torch.zeros((), device='cuda')
                        if group == 'C3': l2 = token_mse(edited, y, m).mean() / scale[op]
                        loss = ce + cfg['l2_weight'] * l2; assert torch.isfinite(loss); (loss * len(part) / cfg['batch']).backward()
                        for kk, v in (('ce', ce), ('l2_normalized', l2), ('loss', loss)): tot[kk] += float(v.detach()) * len(part) / cfg['batch']
                    gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), cfg['clip']); assert torch.isfinite(gn)
                    assert all(x.grad is None for x in eng.model.parameters()); opt.step(); hist.append(dict(step=k + 1, operation=op, gradient_norm=float(gn), **tot))
                save(f'local/ed_{group}_{d}_s{seed}_0600.pt', dict(group=group, domain=d, seed=seed, editor={k_: v.detach().cpu() for k_, v in ed.state_dict().items()}, l2_scale=scale))
                write(f'results/train_{group}_{d}_s{seed}.jsonl', hist); ed.eval(); dev = dev_single(eng, d, ed)
                dump(done, dict(group=group, domain=d, seed=seed, updates=cfg['updates'], l2_scale=scale, dev_single=dev, seconds=time.time() - t0,
                                final_sha256=sha(ROOT / f'local/ed_{group}_{d}_s{seed}_0600.pt'), protocol_sha256=sha(ROOT / 'protocol.json')))
                print('train', group, d, seed, round(hist[-1]['loss'], 4), 'dev', dev['rate'], flush=True); del ed, opt


if __name__ == '__main__':
    main()
