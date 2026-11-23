"""D chains (GPU, after the lock; PLAN 7). --backbone bart|t5. Oracle decoupled freeze D_S (appendix A.3) on the base operator of every
D domain, S = {1}, not-1 and every {j} (j >= 2): plus / minus / alternating, 2N steps, decoded at every step, vote-model argmax recorded.
The standard F_S chains are the L chains."""
import time
from lib5 import *
from cells import PATHS, decoupled_conditions


def main():
    require_slurm(); p = verify_protocol5(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    for d in D_DOMAINS[bb]:
        N = len(S.states(d)); model = vote_model(bb, d)
        for name, ops in decoupled_conditions(bb, d, base_ops(bb, d), slots(bb, d, CONFIRM), CONFIRM).items():
            for path, oplist in PATHS(N).items(): run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist, model=model)
            print('D', bb, d, name, flush=True)
    dump(f'results/d_{bb}_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
