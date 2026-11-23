"""N chains (GPU, after the lock; PLAN 10). --backbone bart|t5. Every N cell (cells.n_cells: base operator, F{1}, F{not 1}, C1 and
C3-U4 editors) and reencode on confirm5 of the held-out templates: plus / minus / alternating, 2N steps, decoded at every step (A.6 exact
match and template parser), vote-model argmax recorded."""
import time
from lib5 import *
from cells import PATHS, n_cells


def main():
    require_slurm(); p = verify_protocol5(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    gates = read(ROOT / f'results/gates_{bb}.json')
    for d, name, ops, fam, new in n_cells(eng, bb, gates, CONFIRM) + [(d, 'reencode', None, 'reencode', True) for d in gates['N_domains']]:
        ops = ops() if callable(ops) else ops; N = len(S.states(d)); model = vote_model(bb, d)
        for path, oplist in PATHS(N).items(): run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist, model=model)
        print('N', bb, d, name, flush=True)
    dump(f'results/n_{bb}_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
