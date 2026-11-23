"""X (BART, template 3, after the lock; section 9). --stage train: Tok-L2 (rank 32) and Att-L2 (Tok-L2 + one attention head) trained with
canonical relative L2 only (appendix A.5), plus and minus separately, seeds 42-44, 4000 updates, on bind3 / bind3fix / name3 train;
RRR-32 closed form. Admission: on name3 and bind3fix every editor's dev single-step success >= 0.95, else one retrain with 8000 updates,
else X stops (x_status = 'stopped'). bind3 is evaluated only here (after the lock), dev included.
--stage eval: confirm4 chains (plus 30, minus 6, alternating 6 from the world start) and single steps for Tok-L2 / Att-L2 x seeds, RRR-32
and reencode; exploratory: attention mass from the slot to the list positions on bind3, failure output types."""
import time
from lib4 import *

PATHS = dict(plus_from_start=['plus'] * 30, minus_from_start=['minus'] * 6, alt_from_start=['plus', 'minus'] * 3)
KINDS = {'Tok': False, 'Att': True}


def train_pair(bb, d, kind, seed, updates, out_dir):
    f = ROOT / f'{out_dir}/x_{kind}_{d}_s{seed}_u{updates}.pt'
    if f.exists(): return f
    sd = {}; hist = {}
    for op in ('plus', 'minus'):
        ed, h = train_l2_editor(bb, d, op, seed, KINDS[kind], updates=updates); hist[op] = h
        sd.update({k: v.cpu() for k, v in ed.state_dict().items() if k.startswith(op + '.')})
    save(f, dict(editor=sd, seed=seed, kind=kind, updates=updates, hist=hist)); return f


def load_pair(path, dim):
    c = load(path); ed = tokatt_pair(dim, c['seed'], KINDS[c['kind']]); ed.load_state_dict(c['editor']); return ed.eval().requires_grad_(False)


def train(eng, bb='bart', doms=X_DOMAINS, updates=(4000, 8000), out_dir='local', admit_split='dev', seeds=SEEDS):
    res = {}
    for d in doms:
        fits, info = fit_rrr4(bb, d, 'natural', [32]); save(f'{out_dir}/x_rrr32_{d}.pt', fits); res[f'{d}/RRR32'] = dict(ridge=info)
        for kind in KINDS:
            for s in seeds:
                for upd in updates:
                    f = train_pair(bb, d, kind, s, upd, out_dir); st = upd
                    if d == 'bind3': break                               # no admission rule on bind3; its dev is read in eval
                    ed = load_pair(f, eng.d); dv = dev_single(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')}, split=admit_split)
                    res[f'{d}/{kind}/s{s}/u{upd}'] = dict(dev_single=dv, admitted=dv['rate'] >= .95)
                    print('X train', d, kind, s, upd, dv['rate'], flush=True)
                    if dv['rate'] >= .95: break
                res[f'{d}/{kind}/s{s}'] = dict(updates=st, admitted=(d == 'bind3') or res[f'{d}/{kind}/s{s}/u{st}']['admitted'])
    adm = [res[f'{d}/{k}/s{s}']['admitted'] for d in doms if d != 'bind3' for k in KINDS for s in seeds]
    res['x_status'] = 'go' if all(adm) else 'stopped'
    return res


@torch.no_grad()
def attention_mass(eng, ed, d, split, bb='bart'):
    """bind3: attention of the slot query over list positions (p_j = current, p_{j+1} = plus target, p_{j-1}) for the plus operator."""
    ws = worlds4(d, split); pos = slots(bb, d, split); out = dict(current=[], next=[], prev=[], other=[])
    for s in S.states(d):
        c = cache4(bb, d, split, s); h = c['h'].to(DEV); m = c['m'].to(DEV); a = ed['plus'].attention(h.float(), m)
        for i, w in enumerate(ws):
            text = S.render(w, s, 3); off = eng.tok(text, return_offsets_mapping=True)['offset_mapping']
            lp = []
            for n in S.people(w):
                cs = text.index(n); lp.append(next(t for t, (a0, b0) in enumerate(off) if b0 > a0 and a0 <= cs < b0))   # first token of the list name
            row = a[i, int(pos[i])].cpu()
            j = s; vals = dict(current=float(row[lp[j]]), next=float(row[lp[(j + 1) % 3]]), prev=float(row[lp[(j - 1) % 3]]))
            vals['other'] = 1 - sum(vals.values())
            for k, v in vals.items(): out[k].append(v)
    return {k: float(np.mean(v)) for k, v in out.items()}


def evaluate(eng, tr, split=CONFIRM, bb='bart', doms=X_DOMAINS, max_steps=None, out_dir='local', seeds=SEEDS):
    res = {}
    for d in doms:
        methods = {'RRR32': {op: RRRop(load(ROOT / f'{out_dir}/x_rrr32_{d}.pt')[op, 32]) for op in ('plus', 'minus')}, 'reencode': None}
        eds = {}
        for kind in KINDS:
            for s in seeds:
                st = tr[f'{d}/{kind}/s{s}']; ed = load_pair(ROOT / f"{out_dir}/x_{kind}_{d}_s{s}_u{st['updates']}.pt", eng.d)
                eds[f'{kind}_s{s}'] = ed; methods[f'{kind}_s{s}'] = {op: ed[op] for op in ('plus', 'minus')}
        for name, ops in methods.items():
            for pn, oplist in PATHS.items(): run_chain(eng, bb, d, 'natural', name, ops, pn, 'world_start', oplist[:max_steps], split=split)
            run_singles(eng, bb, d, 'natural', name, ops, split=split)
            if d == 'bind3' and ops is not None: res[f'{d}/{name}/dev_single'] = dev_single(eng, bb, d, 'natural', ops)
            print('X eval', d, name, flush=True)
        if d == 'bind3':
            res[f'{d}/attention'] = {n: attention_mass(eng, e, d, split) for n, e in eds.items() if n.startswith('Att')}
    return res


def main():
    require_slurm(); p = verify_protocol4(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine4('bart')
    doms = [d for d in X_DOMAINS if p['gates']['bart']['X_ok'][d]]
    if stage == 'train':
        res = train(eng, doms=doms); res['seconds'] = time.time() - t0; dump('results/x_train.json', res); print('X status', res['x_status'], flush=True); return
    tr = read(ROOT / 'results/x_train.json')
    if tr['x_status'] != 'go':
        dump('results/x_eval.json', dict(status='X stopped: admission failed after the 8000-update retrain')); return
    res = evaluate(eng, tr, doms=doms); res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump('results/x_eval.json', res)


if __name__ == '__main__':
    main()
