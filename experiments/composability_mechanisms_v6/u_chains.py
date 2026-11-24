"""U chains (GPU, after the lock; PLAN v7 B7): every unit-U cell (cells7.u_cells) on confirm7, every path, decoded (shards; the recorded
argmax of the locked vote model is checked against the locked simulation in analyze.py). --backbone bart|t5. Idempotent per (cell, path)."""
import time
from lib7 import *
from cells7 import u_cells, PATHS


def main():
    require_slurm(); p = verify_protocol6(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); done = []
    for fam, d, name, ops in u_cells(eng, bb, CONFIRM):
        ops = ops() if callable(ops) else ops; N = len(S.states(d)); model = vote_model(bb, d)
        for path, ol in PATHS(N).items():
            run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol, model=model); done.append(f'{d}/{name}/{path}')
        print('U', bb, fam, d, name, flush=True)
    dump(f'results/u_{bb}_complete.json', dict(done=done, seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
