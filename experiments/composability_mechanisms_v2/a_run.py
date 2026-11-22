"""A (BART, after the core units): C3 anchoring strength on month and daysago. --stage train: lambda in {3, 10} and RRR-16-initialised
C3 (lambda = 1), seeds 42-44 (18 editors). --stage eval: confirm3 chains for these plus v1 C3 (lambda = 1); DRIFT, adjacent-write
cosine, unit-block harmonics (A3), vote-model argmax on month chains (exploratory)."""
import time
from lib3 import *

VARIANTS = {'C3_l3': dict(l2_weight=3.0), 'C3_l10': dict(l2_weight=10.0), 'C3_rrrinit': dict(l2_weight=1.0, init=True)}


def paths(d):
    if d == 'daysago':
        return dict(plus_from_two=(2, ['plus'] * 7), minus_from_nine=(9, ['minus'] * 7), alt_from_five=(5, ['plus', 'minus'] * 5))
    N = len(S.states(d))
    return dict(plus_from_start=('world_start', ['plus'] * (2 * N)), minus_from_start=('world_start', ['minus'] * (2 * N)), alt_from_start=('world_start', ['plus', 'minus'] * N))


@torch.no_grad()
def adjacent_cos(ed, d, split='confirm3'):
    H = {x: cache3('bart', d, split, x)['h'].to(DEV) for x in S.states(d)}; M = cache3('bart', d, split, S.states(d)[0])['m'].to(DEV); C = core()
    ws = worlds3(d, split)
    x0 = [w['start_state'] if legal_step(d, w['start_state'], 'plus', 'natural') and legal_step(d, S.advance(d, w['start_state'], 'plus'), 'plus', 'natural') else S.states(d)[0] for w in ws]
    h = torch.stack([H[x][i] for i, x in enumerate(x0)]); h1 = ed['plus'](h, M); h2 = ed['plus'](h1, M)
    return boot_mean(cosrows(C.pool(h1 - h, M), C.pool(h2 - h1, M)).cpu().numpy())


def main():
    require_slurm(); p = verify_protocol3(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine3('bart'); res = {}
    if stage == 'train':
        for d in ('month', 'daysago'):
            v2 = load(V2DIR / f'local/rrr_{d}_natural.pt'); init = {op: v2[op, 16] for op in ('plus', 'minus')}
            for name, cfg in VARIANTS.items():
                for s in SEEDS:
                    ed, hist, scale = train_editor(eng, 'bart', d, 'natural', 'C3', s, l2_weight=cfg['l2_weight'], init_rrr=init if cfg.get('init') else None)
                    save(f'local/a_{name}_{d}_s{s}.pt', dict(editor={k: v.cpu() for k, v in ed.state_dict().items()}, seed=s)); write(f'results/a_train_{name}_{d}_s{s}.jsonl', hist)
                    res[f'{d}/{name}/s{s}'] = dict(dev=dev_single(eng, 'bart', d, 'natural', {op: ed[op] for op in ('plus', 'minus')}), final_loss=hist[-1]['loss'])
                    print('A train', d, name, s, res[f'{d}/{name}/s{s}']['dev']['rate'], flush=True)
        dump('results/a_train.json', res); return
    for d in ('month', 'daysago'):
        N = len(S.states(d)); eds = {}
        for s in SEEDS:
            eds[f'C3_l1_v1_s{s}'] = V1 / f'local/e1_C3_{d}_s{s}_0600.pt'
            for name in VARIANTS: eds[f'{name}_s{s}'] = ROOT / f'local/a_{name}_{d}_s{s}.pt'
        cal = p['calib']['bart'].get(d); model = dict(P=planes('bart', d), lams={m: torch.tensor(v['lam'], dtype=torch.float64) for m, v in cal['models'].items()}) if cal else None
        for name, path in eds.items():
            ed = load_editor(eng, path); ops = {op: ed[op] for op in ('plus', 'minus')}
            for pn, (st, oplist) in paths(d).items(): run_chain(eng, 'bart', d, 'natural', name, ops, pn, st, oplist, model=model)
            sd = {k: v.cpu() for k, v in ed.state_dict().items()}
            alg = {op: harmonics_of(*editor_factors('editor', sd, op), N) for op in ('plus', 'minus')}
            res[f'{d}/{name}'] = dict(algebra=alg, adjacent_write_cos=adjacent_cos(ed, d))
            print('A eval', d, name, 'DRIFT', round(alg['plus']['DRIFT'], 3), 'harm', alg['plus']['harmonics_present'], flush=True)
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump('results/a_eval.json', res)


if __name__ == '__main__':
    main()
