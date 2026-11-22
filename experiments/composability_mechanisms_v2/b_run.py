"""B' (BART, template 3, after the lock). --stage fit_train: RRR-16/32 and C1 x3 for each retained S1b' domain.
--stage chains: confirm3 chains (plus 30, minus 6, alt 6 from the world start) and single steps for RRR-16/32, C1 x3, reencode."""
import time
from lib3 import *

PATHS = dict(plus_from_start=['plus'] * 30, minus_from_start=['minus'] * 6, alt_from_start=['plus', 'minus'] * 3)


def main():
    require_slurm(); p = verify_protocol3(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine3('bart')
    doms = p['gates']['bart']['B_domains']; res = {}
    if stage == 'fit_train':
        for d in doms:
            fits, info = fit_rrr3('bart', d, 'natural', [16, 32]); save(f'local/bart_rrr_{d}_natural.pt', fits)
            res[f'{d}/RRR'] = dict(ridge=info, dev={r: dev_single(eng, 'bart', d, 'natural', {op: RRRop(fits[op, r]) for op in ('plus', 'minus')}) for r in (16, 32)})
            for s in SEEDS:
                ed, hist, scale = train_editor(eng, 'bart', d, 'natural', 'C1', s)
                save(f'local/b_C1_{d}_s{s}.pt', dict(editor={k: v.cpu() for k, v in ed.state_dict().items()}, seed=s, l2_scale=scale))
                write(f'results/b_train_C1_{d}_s{s}.jsonl', hist)
                res[f'{d}/C1_s{s}'] = dict(dev=dev_single(eng, 'bart', d, 'natural', {op: ed[op] for op in ('plus', 'minus')}), final_loss=hist[-1]['loss'])
            print('B fit/train', d, {k: v for k, v in res.items() if k.startswith(d)}, flush=True)
        res['seconds'] = time.time() - t0; dump('results/b_fit_train.json', res); return
    for d in doms:
        fits = load(ROOT / f'local/bart_rrr_{d}_natural.pt')
        methods = {f'RRR{r}': {op: RRRop(fits[op, r]) for op in ('plus', 'minus')} for r in (16, 32)}
        for s in SEEDS:
            ed = load_editor(eng, ROOT / f'local/b_C1_{d}_s{s}.pt'); methods[f'C1_s{s}'] = {op: ed[op] for op in ('plus', 'minus')}
        methods['reencode'] = None
        for name, ops in methods.items():
            for pn, oplist in PATHS.items(): run_chain(eng, 'bart', d, 'natural', name, ops, pn, 'world_start', oplist)
            run_singles(eng, 'bart', d, 'natural', name, ops); print('B chains', d, name, round(time.time() - t0), flush=True)
    dump('results/b_chains_complete.json', dict(seconds=time.time() - t0, resources=eng.resources()))


if __name__ == '__main__':
    main()
