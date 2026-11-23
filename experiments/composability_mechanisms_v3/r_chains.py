"""R (GPU, after the lock; section 7): ordinary RRR-r and FF-r (all positions) for every R domain kept after G4-0 and every grid rank;
plus / minus / alternating, 2N steps from the world start on confirm4."""
import time
from lib4 import *
from v_chains import PATHS


def run(eng, p, bb, doms, split=CONFIRM, max_steps=None):
    for d in doms:
        N = len(S.states(d)); f = load(ROOT / f'local/{bb}_R_{d}.pt'); ranks = sorted({r for (_, _, r) in f})
        for meth in ('RRR', 'FF'):
            for r in ranks:
                ops = {op: RRRop(f[meth, op, r]) for op in ('plus', 'minus')}
                for pn, oplist in PATHS(N).items(): run_chain(eng, bb, d, 'natural', f'{meth}{r}', ops, pn, 'world_start', oplist[:max_steps], split=split)
                print('R', bb, d, meth, r, flush=True)


def main():
    require_slurm(); p = verify_protocol4(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine4(bb)
    post = read(ROOT / f'results/g40_{bb}.json')['V_domains_post']; doms = [d for d in p['gates'][bb]['R_domains'] if d in post]
    run(eng, p, bb, doms); dump(f'results/r_{bb}_complete.json', dict(domains=doms, seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
