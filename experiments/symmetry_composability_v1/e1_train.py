"""E1.4 C1 (CE) and C3 (CE + normalized canonical L2, weight 1) editors per domain; seeds 42-44; 600 updates;
canonical_objective_v1 training config. Template 0, train worlds only. Exact resume. Dev admission check for C3."""
import random
import time
import torch
from symutil import *
import sym_semantics as S
import sym_evaluator as Ev


def items(d):
    out = {op: [] for op in ('plus', 'minus')}
    for s in S.states(d):
        for op in out:
            try: S.advance(d, s, op)
            except ValueError: continue
            out[op] += [(i, s) for i in range(96)]
    return out


def token_mse(h, y, m):
    return ((h - y).square() * m[..., None]).sum((1, 2)) / (m.sum(1) * h.shape[-1])


@torch.no_grad()
def dev_single(eng, d, ed):
    ws = e1_worlds(d, 'dev'); C = {s: e1_cache(d, 'dev', s) for s in S.states(d)}; ok = []
    for s in S.states(d):
        for op in ('plus', 'minus'):
            try: y = S.advance(d, s, op)
            except ValueError: continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); out = eng.decode(ed[op](h, m), m)
            ok += [Ev.score(o['text'], S.gold(w, y, 0), w, o['ended'])['success'] for o, w in zip(out, ws)]
    return rate(ok)


def main():
    require_slurm(); p = verify_protocol(); cfg = p['training']; doms = sys.argv[sys.argv.index('--domains') + 1].split(',')
    eng = engine(); source_path(); from backend import editors
    for d in doms:
        ws = e1_worlds(d, 'train'); caches = {s: e1_cache(d, 'train', s) for s in S.states(d)}; pool_items = items(d)
        scale = {}
        with torch.no_grad():
            for op, its in pool_items.items():
                v = []
                for lo in range(0, len(its), 64):
                    part = its[lo:lo + 64]; h, m = stack_items(d, 'train', part, caches)
                    y, _ = stack_items(d, 'train', [(i, S.advance(d, s, op)) for i, s in part], caches); v.append(token_mse(h, y, m))
                scale[op] = float(torch.cat(v).mean())
        dump(f'results/e1_l2_scale_{d}.json', scale)
        for group in cfg['groups']:
            for seed in cfg['seeds']:
                done = ROOT / f'results/e1_train_{group}_{d}_s{seed}_complete.json'
                if done.exists(): continue
                ed = editors(eng.d, seed); opt = torch.optim.AdamW(ed.parameters(), lr=cfg['lr'], weight_decay=cfg['weight_decay'])
                rng = random.Random(seed); start = 0; hist = []; resume = ROOT / f'local/e1_{group}_{d}_s{seed}_latest.pt'
                if resume.exists():
                    c = load(resume); ed.load_state_dict(c['editor']); opt.load_state_dict(c['optimizer']); rng.setstate(c['random'])
                    torch.set_rng_state(c['torch_rng']); torch.cuda.set_rng_state(c['cuda_rng']); start = c['step']; hist = c['history']
                def checkpoint(step, tag=None):
                    c = dict(group=group, domain=d, seed=seed, step=step, editor={k: v.detach().cpu() for k, v in ed.state_dict().items()},
                             optimizer=opt.state_dict(), random=rng.getstate(), torch_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state(),
                             history=hist, l2_scale=scale, protocol_sha256=sha(ROOT / 'protocol.json'))
                    save(f'local/e1_{group}_{d}_s{seed}_latest.pt', c)
                    if tag: save(f'local/e1_{group}_{d}_s{seed}_{tag}.pt', c)
                if not start: checkpoint(0, '0000')
                t0 = time.time()
                for k in range(start, cfg['updates']):
                    op = ('plus', 'minus')[k % 2]; part_all = [rng.choice(pool_items[op]) for _ in range(cfg['batch'])]
                    opt.zero_grad(set_to_none=True); tot = dict(ce=0., l2_normalized=0., loss=0.)
                    for lo in range(0, cfg['batch'], cfg['microbatch']):
                        part = part_all[lo:lo + cfg['microbatch']]; h, m = stack_items(d, 'train', part, caches)
                        tgt = [(i, S.advance(d, s, op)) for i, s in part]; y, ym = stack_items(d, 'train', tgt, caches); assert torch.equal(m, ym)
                        edited = ed[op](h, m); texts = [S.render(ws[i], s, 0) for i, s in tgt]
                        ce = eng.ce(edited, m, texts)[0].mean(); l2 = torch.zeros((), device='cuda')
                        if group == 'C3': l2 = token_mse(edited, y, m).mean() / scale[op]
                        loss = ce + cfg['l2_weight'] * l2; assert torch.isfinite(loss); (loss * len(part) / cfg['batch']).backward()
                        for key_, v in (('ce', ce), ('l2_normalized', l2), ('loss', loss)): tot[key_] += float(v.detach()) * len(part) / cfg['batch']
                    gn = torch.nn.utils.clip_grad_norm_(ed.parameters(), cfg['clip']); assert torch.isfinite(gn)
                    assert all(x.grad is None for x in eng.model.parameters()), 'Backbone must be frozen'
                    opt.step(); hist.append(dict(step=k + 1, operation=op, gradient_norm=float(gn), **tot))
                    if (k + 1) % 100 == 0: checkpoint(k + 1)
                checkpoint(cfg['updates'], f"{cfg['updates']:04d}"); write(f'results/e1_train_{group}_{d}_s{seed}.jsonl', hist)
                ed.eval(); dev = dev_single(eng, d, ed)
                dump(done, dict(group=group, domain=d, seed=seed, updates=cfg['updates'], seconds=time.time() - t0, l2_scale=scale,
                                dev_single=dev, admission=(dev['rate'] >= p['admission']['threshold']) if group == 'C3' else None,
                                final_sha256=sha(ROOT / f"local/e1_{group}_{d}_s{seed}_{cfg['updates']:04d}.pt"), protocol_sha256=sha(ROOT / 'protocol.json')))
                print('train', group, d, seed, 'final loss', round(hist[-1]['loss'], 4), 'dev', dev['rate'], flush=True)
                del ed, opt


if __name__ == '__main__':
    main()
