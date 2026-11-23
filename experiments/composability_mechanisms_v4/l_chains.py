"""L chains (GPU, after the lock; PLAN 6.3). --backbone bart|t5. Every L cell (cells.l_cells: the cells simulated before the lock):
plus / minus / alternating, 2N steps from the world start, decoded at every step; the locked vote-model argmaxes on the actual latent slot
are recorded at every step (consistency check against the locked simulation)."""
import time
from lib5 import *
from cells import PATHS, l_cells


def main():
    require_slurm(); p = verify_protocol5(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); n = 0
    for d, name, ops, fam, new in l_cells(eng, bb, CONFIRM):
        ops = ops() if callable(ops) else ops; N = len(S.states(d)); model = vote_model(bb, d)
        for path, oplist in PATHS(N).items(): run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist, model=model)
        n += 1; print('L', bb, d, name, flush=True)
    dump(f'results/l_{bb}_complete.json', dict(cells=n, seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
