"""DO confirmation chains (GPU, after the lock; PLAN v9 section 5). --model gemma|qwen [--smoke].
Every cell of do_sim.do_cells and path on the confirmation latents (weekday / month template 0: confirm7; month-nat: confirm8), composed in
latent space only and decoded once per step to score it (the prompt of the world's start sentence with the slot latent replaced after the
model's layer). Per world: trajectory success at every step and the decoded state at step 1 (for D). --smoke (before the lock): dev, 3 steps,
two cells per domain, output under local/smoke.
Output: results/do_run_<model>.json.gz (per cell: world_ids, ok per step, decoded step-1 state), results/do_run_<model>_complete.json."""
import gzip
import time
from do_sim import *
from lib9 import lock_ok


@torch.no_grad()
def run_cell(eng, d, ws, pos, X, layer, step, oplist, bs=48):
    st = [w['start_state'] for w in ws]; V = torch.stack([X[i, s] for i, s in enumerate(st)]).double(); n = len(ws); ok = [True] * n; R = []; dec1 = None
    for k, op in enumerate(oplist):
        st = [S.advance(d, s, op) for s in st]; V = step(op, V); outs = []
        for lo in range(0, n, bs): outs += eng.generate([ren(w, w['start_state']) for w in ws[lo:lo + bs]], pos[lo:lo + bs], layer, V[lo:lo + bs].float())
        succ = [success(o, w, s, d) for o, w, s in zip(outs, ws, st)]; ok = [a and b for a, b in zip(ok, succ)]; R.append(list(ok))
        if k == 0: dec1 = [Ev.parse_state(o['text'], d, gold=S.gold(w, s, 0))[0] if d == S.NAT else Ev.parse_state(o['text'], d)[0] for o, w, s in zip(outs, ws, st)]
    return dict(world_ids=[w['world_id'] for w in ws], ok=[list(x) for x in zip(*R)], decoded_step1=dec1)


def main():
    require_slurm(); model = sys.argv[sys.argv.index('--model') + 1]; smoke = '--smoke' in sys.argv; t0 = time.time()
    if not smoke: assert lock_ok(), 'DO confirmation chains only after the lock'
    prep = read(ROOT / f'results/do_prep_{model}.json'); layer = prep['layer']; eng = DEngine(model=model); out = {}
    for d, r in prep['domains'].items():
        if r.get('skipped'): continue
        split = 'dev' if smoke else CONF(d); L = load(ROOT / f'local/do_{model}_{d}_{split}.pt'); X = L['latents']; pos = L['pos']
        wmap = {w['world_id']: w for w in worlds5(d, split)}; ws = [wmap[i] for i in L['world_ids']]; N = len(S.states(d)); cells = do_cells(model, d, layer)
        if smoke: cells = dict(list(cells.items())[:2])
        for name, (step, paths) in cells.items():
            for path in paths:
                ol = PATHS(N)[path][:3] if smoke else PATHS(N)[path]; out[f'{split}/{d}/{name}/{path}'] = run_cell(eng, d, ws, pos, X, layer, step, ol)
                print('DO run', model, d, name, path, round(float(np.mean([x[-1] for x in out[f'{split}/{d}/{name}/{path}']['ok']])), 3), flush=True)
    base = ROOT / ('local/smoke' if smoke else 'results'); base.mkdir(parents=True, exist_ok=True); f = base / f'do_run_{model}.json.gz'
    with gzip.open(f, 'wt') as g: json.dump(out, g)
    dump(base / f'do_run_{model}_complete.json', dict(model=model, layer=layer, smoke=smoke, cells=list(out), sha256=sha(f), resources=eng.resources(), seconds=time.time() - t0, pass_=True))


if __name__ == '__main__':
    main()
