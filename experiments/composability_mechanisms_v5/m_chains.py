"""M chains (GPU, after the lock; PLAN B5). --backbone bart|t5. Every M cell (cells6.m_cells: the cells simulated before the lock) and
reencode on confirm6 of the held-out templates: plus / minus / alternating, 2N steps from the world start, decoded at every step (exact
match, template parser); the locked vote-model argmaxes on the actual latent slot are recorded (consistency check)."""
import time
from lib6 import *
from cells6 import PATHS, m_cells


def main():
    require_slurm(); p = verify_protocol6(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    gates = read(ROOT / f'results/gates_{bb}.json')
    for d, name, ops, fam in m_cells(eng, bb, gates, CONFIRM) + [(d, 'reencode', None, 'reencode') for d in gates['M_domains']]:
        ops = ops() if callable(ops) else ops; N = len(S.states(d)); model = vote_model(bb, d)
        for path, oplist in PATHS(N).items(): run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist, model=model)
        print('M', bb, d, name, flush=True)
    dump(f'results/m_{bb}_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
