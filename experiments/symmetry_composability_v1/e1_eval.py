"""E1.5 confirm evaluation (GPU), only after the protocol lock. Single steps and chains for every locked method.
Outputs are written as 16-world shards under results/shards/; complete groups are skipped on resume."""
import time
import torch
from symutil import *
import sym_semantics as S
import sym_evaluator as Ev

SHARD = 16


@torch.no_grad()
def encode_confirm(eng, d):
    ws = e1_worlds(d, 'confirm'); ids = [w['world_id'] for w in ws]
    for s in S.states(d):
        f = ROOT / f'local/e1_{d}_confirm_t0_s{s}.pt'
        if f.exists() and load(f)['world_ids'] == ids: continue
        hs = []; ms = []
        for i in range(0, len(ws), 32):
            h, m = eng.encode([S.render(w, s, 0) for w in ws[i:i + 32]]); hs.append(h.cpu()); ms.append(m.cpu())
        h = torch.cat(hs); m = torch.cat(ms); n = int(m.sum(1).max())
        save(f, dict(h=h[:, :n].contiguous(), m=m[:, :n].contiguous(), world_ids=ids))


def shard_files(kind, d, method, tag):
    return [ROOT / f'results/shards/{kind}_{d}_{method}_{tag}_{lo:03d}.jsonl' for lo in range(0, 160, SHARD)]


def write_shards(files, recs):
    for j, f in enumerate(files):
        write(f, [r for r in recs if j * SHARD <= r['index'] < (j + 1) * SHARD])


def latent_stats(h, m, ref):
    v = m.bool()[..., None]; n = m.sum(1)
    return dict(pooled_norm=core().pool(h, m).norm(dim=1).tolist(), token_norm=(h * v).flatten(1).norm(dim=1).tolist(),
                canonical_token_mse=(((h - ref) * v).square().sum((1, 2)) / (n * h.shape[-1])).tolist())


@torch.no_grad()
def run(eng, p, d, method):
    ws = e1_worlds(d, 'confirm'); C = {s: e1_cache(d, 'confirm', s) for s in S.states(d)}; ops = e1_method(eng, d, method)
    idx = list(range(len(ws)))
    # chains
    for name, spec in p['chains']['by_domain'][d].items():
        files = shard_files('chain', d, method, name)
        if all(f.exists() for f in files): continue
        state = [w['start_state'] for w in ws] if spec['start'] == 'world_start' else [spec['start']] * len(ws)
        h, m = stack_items(d, 'confirm', list(zip(idx, state)), C); ok = [True] * len(ws); recs = []
        for step, op in enumerate(spec['ops'], 1):
            state = [S.advance(d, s, op) for s in state]
            ref, _ = stack_items(d, 'confirm', list(zip(idx, state)), C)
            h = ref.clone() if ops is None else ops[op](h, m)
            out = eng.decode(h, m); ls = latent_stats(h, m, ref)
            for j, w in enumerate(ws):
                sc = Ev.score(out[j]['text'], S.gold(w, state[j], 0), w, out[j]['ended']); ok[j] = ok[j] and sc['success']
                recs.append(dict(index=j, domain=d, method=method, path=name, world_id=w['world_id'], step=step, operation=op, state=state[j],
                                 text=out[j]['text'], exact=out[j]['text'] == S.render(w, state[j], 0), score=sc, trajectory_success=ok[j],
                                 **{k: v[j] for k, v in ls.items()}))
        write_shards(files, recs)
    # single steps
    for s in S.states(d):
        for op in ('plus', 'minus'):
            try: y = S.advance(d, s, op)
            except ValueError: continue
            files = shard_files('single', d, method, f's{s}_{op}')
            if all(f.exists() for f in files): continue
            h, m = C[s]['h'].cuda(), C[s]['m'].cuda(); ref = C[y]['h'].cuda()
            h = ref.clone() if ops is None else ops[op](h, m); out = eng.decode(h, m); ls = latent_stats(h, m, ref)
            recs = [dict(index=j, domain=d, method=method, world_id=w['world_id'], source_state=s, operation=op, target_state=y,
                         text=out[j]['text'], exact=out[j]['text'] == S.render(w, y, 0), score=Ev.score(out[j]['text'], S.gold(w, y, 0), w, out[j]['ended']),
                         **{k: v[j] for k, v in ls.items()}) for j, w in enumerate(ws)]
            write_shards(files, recs)


def main():
    require_slurm(); p = verify_protocol(); doms = sys.argv[sys.argv.index('--domains') + 1].split(',')
    eng = engine(); t0 = time.time()
    for d in doms:
        encode_confirm(eng, d)
        for method in p['methods']:
            run(eng, p, d, method); print('eval', d, method, round(time.time() - t0), flush=True)
    dump(f"results/e1_eval_{'_'.join(doms)}_complete.json", dict(domains=doms, methods=p['methods'], resources=eng.resources(), seconds=time.time() - t0,
         protocol_sha256=sha(ROOT / 'protocol.json')))


if __name__ == '__main__':
    main()
