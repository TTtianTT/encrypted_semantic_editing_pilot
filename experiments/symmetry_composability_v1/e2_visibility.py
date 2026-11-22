"""E2 (GPU, no training): is the next-step visibility of the S_perp residual a curvature effect (H-curv) or an
off-manifold effect of the CE edit? Same residuals, randoms and KL definition as operator_residual_v2."""
import time
import torch
from symutil import *


@torch.no_grad()
def subspace_fraction(eng, C, S, worlds, m, comps):
    """Energy fraction of each residual inside the world's canonical time subspace (token level).

    Subspace per world = span{ pool(E_s) - mean_s pool(E_s), s=-3..3 } + span{ E_s[t] - E_0[t] : s in {-1,+1}, valid t }
    (only -1, 0, +1 share state 0's token positions; other states change length)."""
    L = m.shape[1]; H = {}; M = {}
    for s in range(-3, 4):
        h, mm = eng.encode([S.render(w, s, 0) for w in worlds]); H[s] = h[:, :max(L, int(mm.sum(1).max()))]; M[s] = mm[:, :H[s].shape[1]]
    out = {k: [] for k in comps}; dims = []
    for j in range(len(worlds)):
        P = torch.stack([C.pool(H[s][j:j + 1], M[s][j:j + 1])[0] for s in range(-3, 4)]).double(); P = P - P.mean(0)
        vec = [P]
        for s in (-1, 1):
            assert torch.equal(M[s][j, :L].long(), m[j].long()), 'state +-1 must share state 0 token positions'
            v = m[j].bool(); vec.append((H[s][j, :L][v] - H[0][j, :L][v]).double())
        A = torch.cat(vec); u, sv, _ = torch.linalg.svd(A.T, full_matrices=False); Q = u[:, sv > sv.max() * 1e-6]; dims.append(Q.shape[1])
        v = m[j].bool()
        for k, e in comps.items():
            x = e[j][v].double(); out[k].append(float((x @ Q).square().sum() / x.square().sum()))
    return out, dims


@torch.no_grad()
def main():
    require_slurm(); verify_inputs(['ces/', 'operator_residual_v2/', 'canonical_write_reachability_v1/local/rrr.pt', 'four_domain/'])
    t0 = time.time(); C = core(); Ssem, _ = semantics(); prot = read(V2 / 'protocol.json')
    eng, load_editor = C.engine()
    fit = {k: v.cuda() for k, v in load(CWR / 'local/rrr.pt')['iid_only', 'plus', 16].items() if torch.is_tensor(v)}
    summary = {}
    for seed in SEEDS:
        if (ROOT / f'results/e2/s{seed}.jsonl').exists():
            continue
        ed = load_editor(eng, C.task(seed)['checkpoint']); ed.requires_grad_(False)
        rs = C.selections(seed); bad, good, m = C.patch_pair_batch(rs); worlds = [r['world'] for r in rs]
        s = C.old_basis(seed).cuda(); q = C.basis(ed['plus'].v.weight.cpu()).cuda(); e = (bad - good) * m[..., None]
        es = C.project(e, s) * m[..., None]; er = C.project(es, q) * m[..., None]; ep = es - er
        assert float(ed['plus'].v(ep).abs().max()) < 1e-5
        comps = dict(S=es, S_R=er, S_perp=ep)
        randoms = {}
        for g in comps:
            for rseed in prot['random_seeds']:
                rq = C.random_basis(768, 4, rseed + seed * 100, q.cpu() if g != 'S' else None, g == 'S_perp').cuda()
                randoms[g, rseed] = C.matched_random(e, rq, m, comps[g].flatten(1).norm(dim=1))
        # contexts
        h1, m1 = eng.encode([Ssem.render(w, -1, 0) for w in worlds]); L = m.shape[1]
        h1, m1 = h1[:, :L], m1[:, :L]; assert torch.equal(m1.long(), m.long()), 'today/yesterday must share the mask'
        contexts = [('pre', 0, good), ('post', -1, ed['plus'](good, m)), ('transport', -1, h1),
                    ('post_RRR', -1, good + (good.float() @ fit['left'] @ fit['right'] + fit['bias']) * m[..., None])]
        out = []
        for ctx, state, base in contexts:
            texts = [Ssem.render(w, state, 0) for w in worlds]; ref, labels = C.logits(eng, base, m, texts)
            for g in comps:
                for alpha in (0.5, 1.0):
                    for rseed in [None] + prot['random_seeds']:
                        c = comps[g] if rseed is None else randoms[g, rseed]
                        changed, y = C.logits(eng, base + alpha * c, m, texts); assert torch.equal(labels, y)
                        for j, (r, met) in enumerate(zip(rs, C.distribution(ref, changed, y))):
                            met.pop('token_KL')
                            out.append(dict(seed=seed, world_id=r['world_id'], context=ctx, component=g, alpha=alpha, random_seed=rseed,
                                            perturbation_norm=float((alpha * c[j]).norm()), **met))
            # distance of each base from the canonical next/current state (off-manifold diagnostic)
            target = good if state == 0 else h1
            dist = ((base - target) * m[..., None]).flatten(1).norm(dim=1).cpu().tolist()
            for j, r in enumerate(rs):
                out.append(dict(seed=seed, world_id=r['world_id'], context=ctx, component='base_distance_to_canonical', value=dist[j]))
        frac, dims = subspace_fraction(eng, C, Ssem, worlds, m, dict(e=e, S=es, S_perp=ep))
        for j, r in enumerate(rs):
            out.append(dict(seed=seed, world_id=r['world_id'], context='geometry', component='canonical_subspace_energy_fraction',
                            subspace_dim=dims[j], **{k: v[j] for k, v in frac.items()}))
        write(f'results/e2/s{seed}.jsonl', out); summary[seed] = len(out); print('E2 seed', seed, len(out), flush=True)
        del ed
    dump('results/e2_visibility_complete.json', dict(rows=summary, resources=eng.resources(), seconds=time.time() - t0,
                                                     files={p.name: sha(p) for p in sorted((ROOT / 'results/e2').glob('*.jsonl'))}))


if __name__ == '__main__':
    main()
