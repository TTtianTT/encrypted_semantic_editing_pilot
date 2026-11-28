"""v9 confirmation chains (GPU, after the lock; PLAN v9 sections 3-4, 6). --backbone bart|t5 [--smoke].
Every cell of cells9.py and path, decoded every step only to score it (shards results/shards/chain_<bb>_<d>_natural_<method>_<path>_from_start
_*.jsonl): template 0 on confirm7, month-nat on confirm8 (text reused, first evaluation for the new editors). B6 (reference): the base
operator RRR-16 with decode-and-re-encode after every step (template 0, plus path, 2N steps): R_k and the wall-clock time per step, against
the latent-only chain of the same operator. --smoke (before the lock): dev split, three cells, 3-step paths, shards under local/smoke.
Output: results/chains9_<bb>_complete.json (B6 included)."""
import time
import lib9
from cells9 import *


@torch.no_grad()
def b6(eng, bb, d, split, steps):
    """Decode-and-re-encode with RRR-16: per step h <- op(h); text <- decode(h); h <- encode(text). Returns R_k per step and seconds per step
    for this pipeline and for the latent-only pipeline (op then decode, the decode only to score)."""
    ws = worlds5(d, split); n = len(ws); C = {s: cache5(bb, d, split, s) for s in S.states(d)}; t = tmpl(d); ops = base_ops(bb, d)
    st0 = [w['start_state'] for w in ws]; out = {}
    for mode in ('reencode', 'latent'):
        st = list(st0); h = torch.stack([C[s]['h'][i] for i, s in enumerate(st)]).cuda(); m = torch.stack([C[s]['m'][i] for i, s in enumerate(st)]).cuda()
        ok = [True] * n; R = []; secs = []
        for _ in range(steps):
            torch.cuda.synchronize(); t0 = time.time(); st = [S.advance(d, s, 'plus') for s in st]; h = apply_op(ops['plus'], h, m, None); o = dec(eng, h, m)
            if mode == 'reencode':
                h2, m2 = eng.encode([x['text'] for x in o]); L = max(h.shape[1], h2.shape[1])
                h = Fn.pad(h2.float(), (0, 0, 0, L - h2.shape[1])); m = Fn.pad(m2, (0, L - m2.shape[1]))
            torch.cuda.synchronize(); secs.append(time.time() - t0)
            ok = [a and Ev.score(x['text'], S.gold(w, s, t), w, x['ended'])['success'] for a, x, w, s in zip(ok, o, ws, st)]; R.append(float(np.mean(ok)))
        out[mode] = dict(R=R, R2N=R[-1], seconds_per_step=float(np.mean(secs)))
    return out


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; smoke = '--smoke' in sys.argv; t0 = time.time()
    if smoke: lib9.SHARDS = ROOT / 'local/smoke/shards'
    else: assert lock_ok(), 'confirmation chains only after the lock'
    eng = engine8(bb); cells = cells9(eng, bb, 'dev' if smoke else 'confirm'); done = []
    if smoke: cells = [c for c in cells if c[0] in ('B1', 'B5')][:2] + [c for c in cells if c[0] in ('B2', 'S')][:1]
    for unit, fam, d, name, ops, paths in cells:
        ops = ops() if callable(ops) else ops; sp = 'dev' if smoke else 'confirm8' if d == S.NAT else 'confirm7'; N = len(S.states(d))
        for path, ol in paths(N).items():
            run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol[:3] if smoke else ol, split=sp); done.append(f'{unit}/{d}/{name}/{path}')
        print('chain9', bb, unit, d, name, flush=True)
    res = dict(backbone=bb, smoke=smoke, cells=done)
    res['B6'] = {d: b6(eng, bb, d, 'dev' if smoke else 'confirm7', 3 if smoke else 2 * len(S.states(d))) for d in ('weekday', 'month')}
    res |= dict(resources=eng.resources(), seconds=time.time() - t0, pass_=True)
    dump(ROOT / ('local/smoke' if smoke else 'results') / f'chains9_{bb}_complete.json', res)


if __name__ == '__main__':
    main()
