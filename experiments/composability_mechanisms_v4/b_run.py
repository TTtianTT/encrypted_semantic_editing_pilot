"""B chains (GPU, BART, after the lock; PLAN 9). Every B cell (cells.b_cells: Tok-U, Att1-U, Att2-U seeds 42-44; v4 Att-L2 and RRR-32;
reencode) on confirm5 of bind3, name3, bind3fix: plus 30 steps, minus 6, alternating 6, from the world start, decoded at every step.
Exploratory: attention of the slot query over the list names (current j, next j+1, previous j-1, other) for the plus operator of every
attention editor on bind3 (step 1 from every state; Att2-U: mean over heads, heads also reported)."""
import time
from lib5 import *
from cells import B_PATHS, b_cells


@torch.no_grad()
def attention_mass(eng, ed, d, split=CONFIRM):
    ws = worlds5(d, split); pos = slots('bart', d, split); out = dict(current=[], next=[], prev=[], other=[]); heads = []
    for s in S.states(d):
        c = cache5('bart', d, split, s); h = c['h'].to(DEV); m = c['m'].to(DEV); a = ed['plus'].attention(h.float(), m)
        if a.dim() == 4: heads.append(a.cpu()); a = a.mean(1)
        for i, w in enumerate(ws):
            text = S.render(w, s, 3); off = eng.tok(text, return_offsets_mapping=True)['offset_mapping']; lp = []
            for nme in S.people(w):
                cs = text.index(nme); lp.append(next(t for t, (a0, b0) in enumerate(off) if b0 > a0 and a0 <= cs < b0))
            row = a[i, int(pos[i])].cpu(); vals = dict(current=float(row[lp[s]]), next=float(row[lp[(s + 1) % 3]]), prev=float(row[lp[(s - 1) % 3]]))
            vals['other'] = 1 - sum(vals.values())
            for k, v in vals.items(): out[k].append(v)
    return {k: float(np.mean(v)) for k, v in out.items()}


def main():
    require_slurm(); p = verify_protocol5(); assert read(ROOT / 'results/train_new_bart_B.json')['B_status'] == 'go'; t0 = time.time(); eng = engine5('bart'); att = {}
    for d, name, ops in b_cells(eng):
        ops = ops() if callable(ops) else ops
        for path, oplist in B_PATHS.items(): run_chain(eng, 'bart', d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist)
        if d == 'bind3' and name.startswith(('Att1U', 'Att2U', 'AttL2v4')): att[name] = attention_mass(eng, ops, d)
        print('B', d, name, att.get(name, ''), flush=True)
    dump('results/b_complete.json', dict(attention_bind3=att, seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
