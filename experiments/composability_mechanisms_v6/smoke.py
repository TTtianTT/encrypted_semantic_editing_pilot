"""Pre-lock smoke test (GPU; dev splits only; PLAN v7 B1, B10). --backbone bart|t5. Runs every post-lock code path on dev data, with all
products under local/smoke: (1) U chains on dev for a subset of cells (F_empty and the first editor cell of every domain, all paths), with
the recorded argmax checked against the dev simulation (local/smoke/simulate_<bb>.json.gz, written by simulate.py --split dev); (2)
r_repair, a_cycle and (BART) k_chains in smoke mode; (3) local/smoke/protocol_preview.json (lock.sections) for analyze.py --smoke.
Output: results/smoke_<bb>.json (pass = every step ran and the dev argmax mismatches are 0)."""
import gzip
import time
import lib7
from lib7 import *
from cells7 import u_cells, PATHS


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); res = dict(steps={})
    sm = ROOT / 'local/smoke'; lib7.SHARDS = sm / 'shards'; lib7.SHARDS.mkdir(parents=True, exist_ok=True)
    eng = engine5(bb); pick = {}; mm = 0
    with gzip.open(sm / f'simulate_{bb}.json.gz', 'rt') as g: sims = json.load(g)
    for fam, d, name, ops in u_cells(eng, bb, 'dev'):
        if name != 'F_empty' and d in pick: continue
        pick.setdefault(d, name); ops = ops() if callable(ops) else ops; N = len(S.states(d))
        for path, ol in PATHS(N).items():
            run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', ol, split='dev', model=vote_model(bb, d))
            sim = sims.get(f'U/{bb}/{d}/{name}/{path}'); recs = [r for f in sorted(lib7.SHARDS.glob(f'chain_{bb}_{d}_natural_{name}_{path}_from_start_*.jsonl')) for r in rows(f)]
            idx = {w: i for i, w in enumerate(sim['world_ids'])}
            mm += sum(int(r['argmax_full'] != sim['argmax'][idx[r['world_id']]][r['step'] - 1]) for r in recs)
    res['steps']['u_dev_chains'] = dict(cells=len(pick), argmax_mismatches=mm); del eng; torch.cuda.empty_cache()
    for mod, args in (('r_repair', ['--backbone', bb, '--mode', 'smoke']), ('a_cycle', ['--backbone', bb, '--mode', 'smoke'])) + ((('k_chains', ['--mode', 'smoke']),) if bb == 'bart' else ()):
        sys.argv = [mod] + args; __import__(mod).main(); res['steps'][mod] = 'ok'; torch.cuda.empty_cache()
    import lock
    try: dump(sm / 'protocol_preview.json', dict(predictions=lock.PREDICTIONS, operational=lock.OPERATIONAL, **lock.sections()))
    except FileNotFoundError as e: res['steps']['protocol_preview'] = f'pending: {e.filename}'
    res['pass'] = mm == 0; res['seconds'] = time.time() - t0; dump(ROOT / f'results/smoke_{bb}.json', res); print(json.dumps(res), flush=True)
    assert res['pass']


if __name__ == '__main__':
    main()
