"""V (GPU, after the lock; section 6): slot surgery on the base operator for every V domain kept after G4-0: F{empty}, F{1}, F{not 1} and
every single-plane freeze F{j}, j >= 2 (N = 4: F{not 1} is F{2}, run once); plus / minus / alternating, 2N steps from the world start,
decoded at every step; the vote-model argmax (fitted / equal / fundamental-only) on the actual latent slot recorded at every step."""
import time
from lib4 import *
from g40 import base_ops, vote_model

PATHS = lambda N: dict(plus_from_start=['plus'] * (2 * N), minus_from_start=['minus'] * (2 * N), alt_from_start=['plus', 'minus'] * N)


def conditions(p, bb, d, pos):
    T, _ = base_ops(p, bb, d); P = planes(bb, d); ks = [k for k, _ in P]
    fr = lambda Sset: {op: Freeze(T[op], bvec(P, Sset), pos) for op in T}
    out = {'F_empty': T, 'F_{1}': fr({1})}
    nf = set(ks) - {1}
    out['F_not1'] = fr(nf)
    for k in ks:
        if k >= 2 and not (len(nf) == 1 and k in nf): out[f'F_{{{k}}}'] = fr({k})
    return out


def run(eng, p, bb, doms, split=CONFIRM, max_steps=None):
    for d in doms:
        N = len(S.states(d)); pos = slots(bb, d, split); model = vote_model(p, bb, d)
        for name, ops in conditions(p, bb, d, pos).items():
            for pn, oplist in PATHS(N).items():
                run_chain(eng, bb, d, 'natural', name, ops, pn, 'world_start', oplist[:max_steps], split=split, model=model)
            print('V', bb, d, name, flush=True)


def main():
    require_slurm(); p = verify_protocol4(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine4(bb)
    doms = read(ROOT / f'results/g40_{bb}.json')['V_domains_post']; run(eng, p, bb, doms)
    dump(f'results/v_{bb}_complete.json', dict(domains=doms, seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
