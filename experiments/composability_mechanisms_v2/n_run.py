"""N (BART, after the lock): CE-only C1 on scrambled maps. --stage train: 12 editors (weekday/month/compass sigma_max, weekday skip2;
seeds 42-44), admission dev single >= 0.90 else one retrain at 2400 updates. --stage eval: confirm3 chains, M1-M3, A.5 M4 classes."""
import time
from lib3 import *

MAPS_N = [('weekday', 'scrmax'), ('month', 'scrmax'), ('compass', 'scrmax'), ('weekday', 'skip2')]
NATURAL_STEPS = {(0, 1), (2, 3), (3, 4)}   # weekday sigma_max transitions that coincide with natural steps


@torch.no_grad()
def natural_step_cos(eng, Wr, s, split='confirm3', d='weekday', mp='scrmax'):
    nat = load_editor(eng, V1 / f'local/e1_C1_weekday_s{s}_0600.pt')['plus']
    Hc = {x: cache3('bart', d, split, x)['h'].to(DEV) for x in S.states(d)}; Mc = cache3('bart', d, split, 0)['m'].to(DEV)
    cs = {x: float(cosrows(Wr[x].to(DEV), (nat(Hc[x], Mc) - Hc[x]) * Mc[..., None]).mean()) for x in Wr}
    g = {x: S.advance(d, x, 'plus', mp) for x in Wr}
    return dict(natural_step=float(np.mean([cs[x] for x in cs if (x, g[x]) in NATURAL_STEPS])),
                other=float(np.mean([cs[x] for x in cs if (x, g[x]) not in NATURAL_STEPS])), per_source={str(k): v for k, v in cs.items()})


def main():
    require_slurm(); p = verify_protocol3(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine3('bart'); res = {}
    if stage == 'train':
        for d, mp in MAPS_N:
            for s in SEEDS:
                for upd in (600, 2400):
                    ed, hist, scale = train_editor(eng, 'bart', d, mp, 'C1', s, updates=upd)
                    dv = dev_single(eng, 'bart', d, mp, {op: ed[op] for op in ('plus', 'minus')})
                    save(f'local/n_C1_{d}_{mp}_s{s}_u{upd}.pt', dict(editor={k: v.cpu() for k, v in ed.state_dict().items()}, seed=s))
                    write(f'results/n_train_{d}_{mp}_s{s}_u{upd}.jsonl', hist)
                    res[f'{d}/{mp}/s{s}/u{upd}'] = dict(dev=dv, final_loss=hist[-1]['loss'], admitted=dv['rate'] >= .90)
                    print('N train', d, mp, s, upd, dv['rate'], flush=True)
                    if dv['rate'] >= .90: break
                res[f'{d}/{mp}/s{s}'] = dict(updates=upd, admitted=dv['rate'] >= .90, status='ok' if dv['rate'] >= .90 else 'cannot learn')
        res['seconds'] = time.time() - t0; dump('results/n_train.json', res); return
    tr = read(ROOT / 'results/n_train.json')
    for d, mp in MAPS_N:
        N = len(S.states(d)); info, predict = probe('bart', d); res[f'{d}/probe'] = info
        for s in SEEDS:
            st = tr[f'{d}/{mp}/s{s}']
            if not st['admitted']: res[f'{d}/{mp}/s{s}'] = dict(status='cannot learn'); continue
            ed = load_editor(eng, ROOT / f"local/n_C1_{d}_{mp}_s{s}_u{st['updates']}.pt"); ops = {op: ed[op] for op in ('plus', 'minus')}
            for pn, oplist in dict(plus_from_start=['plus'] * (2 * N), minus_from_start=['minus'] * (2 * N), alt_from_start=['plus', 'minus'] * N).items():
                run_chain(eng, 'bart', d, mp, f'C1_s{s}', ops, pn, 'world_start', oplist)
            run_singles(eng, 'bart', d, mp, f'C1_s{s}', ops)
            wm = write_metrics(eng, 'bart', d, mp, ed['plus'], predict, m4='keep'); Wr = wm.pop('writes')
            r = dict(wm, R2=chain_rate('bart', d, mp, f'C1_s{s}', 'plus_from_start', 2), R1=chain_rate('bart', d, mp, f'C1_s{s}', 'plus_from_start', 1))
            if d == 'weekday' and mp == 'scrmax':   # exploratory: natural-step transitions vs others, cosine with the natural-map C1 write
                r['cos_with_natural_C1'] = natural_step_cos(eng, Wr, s)
            res[f'{d}/{mp}/s{s}'] = r
            print('N eval', d, mp, s, 'M1', round(r['M1']['mean'], 3), 'R2', r['R2']['rate'], 'M3', {k: round(v, 3) for k, v in r['M3'].items() if k != 'n'}, flush=True)
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump('results/n_eval.json', res)


if __name__ == '__main__':
    main()
