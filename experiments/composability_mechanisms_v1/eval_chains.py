"""Confirm evaluation after the lock (GPU): encode confirm2 / S1b confirm, then single steps and chains for every locked method.
16-world shards under results/shards/; complete (method, path) groups are skipped on resume."""
import time
import torch
from symutil import *
import sym2_semantics as S
import sym2_evaluator as Ev
from d_encode import encode_split

SHARD = 16


def split_of(d):
    return 'confirm2' if d in V1_DOMAINS else 'confirm'


def editor(eng, d, spec):
    kind = spec['kind']
    if kind == 'reencode':
        return None
    if kind == 'RRR':
        f = load(ROOT / f"local/rrr_{d}_{spec['map']}.pt"); return {op: RRRop(f[op, spec['rank']]) for op in ('plus', 'minus')}
    source_path(); from backend import editors
    ed = editors(eng.d, spec['seed'])
    path = (V1 / f"local/e1_{kind}_{d}_s{spec['seed']}_0600.pt") if d in V1_DOMAINS else (ROOT / f"local/ed_{kind}_{d}_s{spec['seed']}_0600.pt")
    ed.load_state_dict(load(path)['editor']); ed.eval().requires_grad_(False)
    return {op: ed[op] for op in ('plus', 'minus')}


def files(kind, d, spec, tag, n):
    return [ROOT / f"results/shards/{kind}_{d}_{spec['map']}_{spec['name']}_{tag}_{lo:03d}.jsonl" for lo in range(0, n, SHARD)]


def write_shards(fs, recs):
    for j, f in enumerate(fs):
        write(f, [r for r in recs if j * SHARD <= r['index'] < (j + 1) * SHARD])


def stats(h, m, ref, pos):
    v = m.bool()[..., None]; n = m.sum(1); C = core()
    return dict(pooled_norm=C.pool(h, m).norm(dim=1).tolist(), token_norm=(h * v).flatten(1).norm(dim=1).tolist(),
                canonical_token_mse=(((h - ref) * v).square().sum((1, 2)) / (n * h.shape[-1])).tolist(),
                slot_mse=(h[:, pos] - ref[:, pos]).square().mean(1).tolist())


@torch.no_grad()
def run(eng, p, d, spec):
    split = split_of(d); ws = worlds2(d, split); n = len(ws); C = {s: cache2(d, split, s) for s in S.states(d)}; pos = slot_pos(d, 0)
    ops = editor(eng, d, spec); mp = spec['map']; idx = list(range(n))
    def stack(states):
        return (torch.stack([C[s]['h'][i] for i, s in zip(idx, states)]).cuda(), torch.stack([C[s]['m'][i] for i, s in zip(idx, states)]).cuda())
    for name, ch in p['chains'][d][mp].items():
        steps = ch['ops'] if spec['paths'] == 'full' else ch['ops'][:ch['short_len']]
        fs = files('chain', d, spec, name, n)
        if all(f.exists() for f in fs): continue
        state = [w['start_state'] for w in ws] if ch['start'] == 'world_start' else [ch['start']] * n
        h, m = stack(state); ok = [True] * n; recs = []
        for step, op in enumerate(steps, 1):
            state = [S.advance(d, s, op, mp) for s in state]; ref, _ = stack(state)
            h = ref.clone() if ops is None else ops[op](h, m)
            out = eng.decode(h, m); st = stats(h, m, ref, pos)
            for j, w in enumerate(ws):
                sc = Ev.score(out[j]['text'], S.gold(w, state[j], 0), w, out[j]['ended']); ok[j] = ok[j] and sc['success']
                recs.append(dict(index=j, domain=d, map=mp, method=spec['name'], path=name, world_id=w['world_id'], step=step, operation=op,
                                 state=state[j], text=out[j]['text'], exact=out[j]['text'] == S.render(w, state[j], 0), score=sc,
                                 trajectory_success=ok[j], **{k: v[j] for k, v in st.items()}))
        write_shards(fs, recs)
    for t in spec.get('single_templates', [0]):
        Ct = C if t == 0 else {s: load(ROOT / f'local/c_{d}_{split}_t{t}_s{s}.pt') for s in S.states(d)}
        for s in S.states(d):
            for op in ('plus', 'minus'):
                try: y = S.advance(d, s, op, mp)
                except ValueError: continue
                fs = files('single', d, spec, f't{t}_s{s}_{op}', n)
                if all(f.exists() for f in fs): continue
                h, m = Ct[s]['h'].cuda(), Ct[s]['m'].cuda(); ref = Ct[y]['h'].cuda()
                assert torch.equal(m, Ct[y]['m'].cuda())
                h = ref.clone() if ops is None else ops[op](h, m); out = eng.decode(h, m)
                recs = [dict(index=j, domain=d, map=mp, method=spec['name'], template=t, world_id=w['world_id'], source_state=s, operation=op, target_state=y,
                             text=out[j]['text'], exact=out[j]['text'] == S.render(w, y, t), score=Ev.score(out[j]['text'], S.gold(w, y, t), w, out[j]['ended']))
                        for j, w in enumerate(ws)]
                write_shards(fs, recs)


def main():
    require_slurm(); p = verify_protocol2(); S.load_maps(ROOT / 'protocol.json'); lane = sys.argv[sys.argv.index('--lane') + 1]
    eng = engine(); t0 = time.time()
    for d in p['lanes'][lane]:
        encode_split(eng, d, split_of(d), (0, 3) if d in S1B_DOMAINS else (0,))
        for spec in p['methods'][d]:
            run(eng, p, d, spec); print('eval', d, spec['map'], spec['name'], round(time.time() - t0), flush=True)
    dump(f'results/eval_{lane}_complete.json', dict(lane=lane, domains=p['lanes'][lane], resources=eng.resources(), seconds=time.time() - t0,
                                                   protocol_sha256=sha(ROOT / 'protocol.json')))


if __name__ == '__main__':
    main()
