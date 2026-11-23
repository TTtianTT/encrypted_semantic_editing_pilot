"""Pre-lock smoke test (GPU; dev only; outputs in local/smoke; not a locked source). --backbone bart|t5.
Runs the post-lock code paths on dev worlds with short chains: run_chain with the vote-model readout for a sample of L cells (freeze,
grid, existing and new editors), D_S cells, N cells (incl. reencode), BART B cells and the bind3 attention mass, v1 C1 (G5-0 path);
lcore on the smoke shards. Consistency check (the basis of the locked predictions): simulate_chain's per-step argmax equals the argmax
recorded inside run_chain for the same cells (dev). No confirm5 data are decoded."""
import shutil
import time
import lib5
from lib5 import *
import lcore
from cells import PATHS, l_cells, n_cells, decoupled_conditions, b_cells

SM = ROOT / 'local/smoke'
K = 3


def run_and_compare(eng, bb, d, name, ops, log, steps=K):
    ops = ops() if callable(ops) else ops; model = vote_model(bb, d); N = len(S.states(d)); bad = 0
    for path, oplist in PATHS(N).items():
        run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist[:steps], split='dev', model=model)
        sim = simulate_chain(bb, d, ops, oplist[:steps], model, split='dev')
        recs = chain_records(bb, d, 'natural', name, f'{path}_from_start'); idx = {w: i for i, w in enumerate(sim['world_ids'])}
        for r in recs:
            i = idx[r['world_id']]
            if r['argmax_full'] != sim['argmax']['full'][i][r['step'] - 1] or r['state'] != sim['states'][i][r['step'] - 1]: bad += 1
        tab = lcore.world_table([dict(r) for r in recs], steps); s = lcore.cell_summary(tab)
        log.setdefault('cells', {})[f'{d}/{name}/{path}'] = dict(obs=s['obs_rate'], pred=s['pred_rate'], D=s['D'], mismatch=bad)
    return bad


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time()
    lib5.SHARDS = SM / f'shards_{bb}'
    if lib5.SHARDS.exists(): shutil.rmtree(lib5.SHARDS)
    eng = engine5(bb); gates = read(ROOT / f'results/gates_{bb}.json'); log = {}; mism = 0
    L = l_cells(eng, bb, 'dev'); pick = []
    for d in L_DOMAINS[bb]:
        cs = [c for c in L if c[0] == d]; pick += [c for c in cs if c[1] in ('F_{1}', 'F_not1')][:2] + [c for c in cs if c[1].startswith(('RRR', 'FF'))][:2]
    pick += [c for c in L if c[3] == 'CE'][:2] + [c for c in L if c[3] == 'state' and c[1][0] == 'C'][:2] + [c for c in L if c[4]][:3]
    for d, name, ops, fam, new in pick: mism += run_and_compare(eng, bb, d, name, ops, log)
    d = 'hour'; D = decoupled_conditions(bb, d, base_ops(bb, d), slots(bb, d, 'dev'), 'dev')
    for name in list(D)[:2]: mism += run_and_compare(eng, bb, d, name, D[name], log)
    Ncells = n_cells(eng, bb, gates, 'dev')
    for d_, name, ops, fam, new in Ncells[:5]: mism += run_and_compare(eng, bb, d_, name, ops, log)
    for d_ in gates['N_domains']:
        run_chain(eng, bb, d_, 'natural', 'reencode', None, 'plus_from_start', 'world_start', ['plus'] * 2, split='dev')
        log.setdefault('reencode_dev_R2', {})[d_] = chain_rate(bb, d_, 'natural', 'reencode', 'plus_from_start', 2)['rate']
    if bb == 'bart':
        import b_run
        for d_, name, ops in b_cells(eng):
            if not name.endswith('_s42') and name not in ('RRR32', 'reencode'): continue
            ops = ops() if callable(ops) else ops
            run_chain(eng, bb, d_, 'natural', name, ops, 'plus_from_start', 'world_start', ['plus'] * 2, split='dev')
            log.setdefault('B_dev_R2', {})[f'{d_}/{name}'] = chain_rate(bb, d_, 'natural', name, 'plus_from_start', 2)['rate']
            if d_ == 'bind3' and name.startswith(('Att1U', 'Att2U')): log.setdefault('B_attention', {})[name] = b_run.attention_mass(eng, ops, d_, split='dev')
        for d_ in ('weekday', 'month'):
            ed = load_editor(eng, V1 / f'local/e1_C1_{d_}_s42_0600.pt')
            run_chain(eng, bb, d_, 'natural', 'C1v1_s42', {op: ed[op] for op in ('plus', 'minus')}, 'g50_plus', 'world_start', ['plus', 'plus'], split='dev')
            log.setdefault('G50_C1_dev_R2', {})[d_] = chain_rate(bb, d_, 'natural', 'C1v1_s42', 'g50_plus', 2)['rate']
    log['argmax_mismatches'] = mism; log['pass'] = mism == 0
    log['sources'] = {f: sha(ROOT / f) for f in LOCKED5 + ['simulate.py', 'lock.py', 'train_new.py', 'gates.py', 'calib_mt.py', 'smoke.py']}
    log['seconds'] = time.time() - t0; log['resources'] = eng.resources(); dump(f'results/smoke_{bb}.json', log)
    print(json.dumps({k: v for k, v in log.items() if k not in ('sources', 'cells')}, indent=1, default=str), flush=True)
    assert log['pass'], 'smoke test failed'


if __name__ == '__main__':
    main()
