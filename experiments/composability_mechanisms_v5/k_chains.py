"""K chains (GPU, BART, after the lock; PLAN B7). Every K cell (cells6.k_cells) on confirm6 of bind3, name3, bind3fix: plus 30 steps,
minus 12, alternating 12, from the world start, decoded at every step. Exploratory: on bind3, the slot's attention mass over the list
names (current j, next j+1, previous j-1, other) for the plus operator at step 1 from every state: layer 2 of Att2L, the single layer
of Att1-U8 and of v5's Att1-U / Att2-U (heads averaged)."""
import re
import time
from lib6 import *
from cells6 import K_PATHS, k_cells


@torch.no_grad()
def attention_mass(eng, op_mod, d):
    ws = worlds5(d, CONFIRM); pos = slots('bart', d, CONFIRM); npos = name_positions(d, CONFIRM); out = dict(current=[], next=[], prev=[], other=[])
    for s in S.states(d):
        c = cache5('bart', d, CONFIRM, s); a = op_mod.attention(c['h'].to(DEV).float(), c['m'].to(DEV))
        if a.dim() == 4: a = a.mean(1)
        for i in range(len(ws)):
            row = a[i, int(pos[i])].cpu(); lp = npos[i].tolist()
            v = dict(current=float(row[lp[s]]), next=float(row[lp[(s + 1) % 3]]), prev=float(row[lp[(s - 1) % 3]])); v['other'] = 1 - sum(v.values())
            for k, x in v.items(): out[k].append(x)
    return {k: float(np.mean(v)) for k, v in out.items()}


def main():
    require_slurm(); p = verify_protocol6(); t0 = time.time(); eng = engine5('bart'); att = {}
    for d, name, ops in k_cells(eng, CONFIRM):
        ops = ops() if callable(ops) else ops
        for path, oplist in K_PATHS.items(): run_chain(eng, 'bart', d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist)
        if d == 'bind3' and name.startswith(('Att2LU4', 'Att2LU8', 'Att1U8', 'Att1U_', 'Att2U_')): att[name] = attention_mass(eng, ops['plus'], d)
        print('K', d, name, att.get(name, ''), flush=True)
    dump('results/k_bart_complete.json', dict(attention_bind3=att, seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
