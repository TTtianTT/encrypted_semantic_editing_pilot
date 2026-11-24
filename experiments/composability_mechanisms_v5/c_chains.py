"""C chains (GPU, BART, after the lock; PLAN B6). Every C cell (cells6.c_cells) on confirm6 of weekday and month: plus / minus /
alternating, 2N steps from the world start, decoded at every step; the slot vote-model argmaxes and the slot + context argmax ('ctx')
on the actual latent are recorded (consistency check against the locked simulation)."""
import time
from lib6 import *
from cells6 import PATHS, c_cells


def main():
    require_slurm(); p = verify_protocol6(); t0 = time.time(); eng = engine5('bart'); models = {d: ctx_model('bart', d, CONFIRM) for d in C_DOMAINS}
    for d, name, ops, cset in c_cells(eng, CONFIRM):
        ops = ops() if callable(ops) else ops; N = len(S.states(d))
        for path, oplist in PATHS(N).items(): run_chain(eng, 'bart', d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist, model=models[d])
        print('C', d, name, cset, flush=True)
    dump('results/c_bart_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
