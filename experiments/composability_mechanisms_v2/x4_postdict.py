"""X4 (GPU, exploratory, before the lock): BART vote model (calib_bart) postdicts v2 rank-deficient chains. Latents recomputed
deterministically from v2 fits on v2 confirm2 caches (no decoding); compared with the decoded states in v2 shards."""
import time
from lib3 import *


@torch.no_grad()
def main():
    require_slurm(); t0 = time.time(); cal = read(ROOT / 'results/calib_bart.json'); res = {}
    v2w = {d: [w for w in rows(V2DIR / f'data/{d}/worlds.jsonl') if w['split'] == 'confirm2'] for d in ('weekday', 'month')}
    for d, ranks in (('weekday', (4, 5)), ('month', (8, 9, 10))):
        ws = v2w[d]; n = len(ws); N = len(S.states(d)); pos = read(ROOT / 'data/slot_positions.json')['bart'][d]['all']
        C = {s: load(V2DIR / f'local/c_{d}_confirm2_t0_s{s}.pt') for s in S.states(d)}
        Cw = torch.stack([C[s]['h'][:, pos].double() for s in S.states(d)], 1).cuda(); P = [(k, B.cuda()) for k, B in planes('bart', d)]
        lams = {m: torch.tensor(v['lam'], dtype=torch.float64).cuda() for m, v in cal['domains'][d]['models'].items()}
        fits = load(V2DIR / f'local/rrr_{d}_natural.pt')
        for r in ranks:
            shard = {}
            for f in sorted((V2DIR / 'results/shards').glob(f'chain_{d}_natural_RRR{r}_plus_from_start_*.jsonl')):
                for rec in rows(f): shard[rec['world_id'], rec['step']] = Ev.parse_state(rec['text'], d)[0]
            T = RRRop(fits['plus', r]); state = [w['start_state'] for w in ws]
            h = torch.stack([C[s]['h'][i] for i, s in enumerate(state)]).cuda(); m = torch.stack([C[s]['m'][i] for i, s in enumerate(state)]).cuda()
            agree = {k: [] for k in lams}; steps = {k: [] for k in lams}
            for t in range(1, 2 * N + 1):
                h = T(h, m); Dm = plane_dists(h[:, pos].double(), Cw, P); per = {k: [] for k in lams}
                for k, lam in lams.items():
                    am = vote_scores(Dm, lam).argmax(-1).tolist()
                    for j, w in enumerate(ws):
                        obs = shard[w['world_id'], t]
                        if obs is None: continue
                        per[k].append(am[j] == obs); agree[k].append(am[j] == obs)
                    steps[k].append(float(np.mean(per[k])) if per[k] else None)
            res[f'{d}/RRR{r}'] = {k: dict(agreement=float(np.mean(v)), n=len(v), by_step=steps[k]) for k, v in agree.items()}
            print(d, r, {k: round(float(np.mean(v)), 3) for k, v in agree.items()}, flush=True)
    res['note'] = 'Exploratory postdiction; v2 confirm2 data were already evaluated; does not affect any locked quantity.'
    res['seconds'] = time.time() - t0; dump('results/x4_postdict.json', res)


if __name__ == '__main__':
    main()
