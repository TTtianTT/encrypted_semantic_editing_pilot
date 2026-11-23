"""S (GPU, T5Gemma, after the lock; section 10): RRR-32 under the natural map and sigma_max (v2 tables), weekday and month,
one-way plus 10N steps from the world start on confirm4."""
import time
from lib4 import *


def run(eng, split=CONFIRM, max_steps=None):
    for d in S_DOMAINS:
        N = len(S.states(d))
        for mp in ('natural', 'scrmax'):
            f = load(ROOT / f'local/t5_S_{d}_{mp}.pt'); ops = {op: RRRop(f[op, 32]) for op in ('plus', 'minus')}
            run_chain(eng, 't5', d, mp, 'RRR32', ops, 'longplus', 'world_start', (['plus'] * (10 * N))[:max_steps], split=split)
            print('S', d, mp, flush=True)


def main():
    require_slurm(); p = verify_protocol4(); t0 = time.time(); eng = engine4('t5'); run(eng)
    dump('results/s_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
