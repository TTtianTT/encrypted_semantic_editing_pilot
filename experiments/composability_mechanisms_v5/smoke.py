"""Pre-lock smoke test (GPU; dev only; outputs only in local/smoke; not a locked source). --backbone bart|t5.
Runs the post-lock code paths on dev worlds with short chains: run_chain with the readouts for a sample of M cells (GM base, surgery,
C1, slot C3-U4, full-sequence RRR-16) and, on BART, C cells with the slot + context readout and K cells (every new editor kind incl. the
oracle-routing operator, references, reencode) and the G6-0 paths; lcore on the smoke shards. Consistency check (basis of the locked
predictions): simulate_chain's per-step argmax (every readout) equals the argmax recorded inside run_chain for the same cells on dev.
No confirm6 data are decoded."""
import shutil
import time
import lib6
from lib6 import *
import lcore
from cells6 import PATHS, K_PATHS, m_cells, c_cells, k_cells

SM = ROOT / 'local/smoke'
K = 3


def run_and_compare(eng, bb, d, name, ops, model, log, steps=K):
    ops = ops() if callable(ops) else ops; N = len(S.states(d)); bad = 0
    for path, oplist in PATHS(N).items():
        run_chain(eng, bb, d, 'natural', name, ops, f'{path}_from_start', 'world_start', oplist[:steps], split='dev', model=model)
        sim = simulate_chain(bb, d, ops, oplist[:steps], model, split='dev')
        recs = chain_records(bb, d, 'natural', name, f'{path}_from_start'); idx = {w: i for i, w in enumerate(sim['world_ids'])}
        for r in recs:
            i = idx[r['world_id']]
            for k, v in sim['argmax'].items():
                if r[f'argmax_{k}'] != v[i][r['step'] - 1]: bad += 1
            if r['state'] != sim['states'][i][r['step'] - 1]: bad += 1
        tab = lcore.world_table([dict(r) for r in recs], steps); s = lcore.cell_summary(tab)
        log.setdefault('cells', {})[f'{d}/{name}/{path}'] = dict(obs=s['obs_rate'], pred=s['pred_rate'], D=s['D'], mismatch=bad)
    return bad


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time()
    lib6.SHARDS = SM / f'shards_{bb}'
    if lib6.SHARDS.exists(): shutil.rmtree(lib6.SHARDS)
    eng = engine5(bb); gates = read(ROOT / f'results/gates_{bb}.json'); log = {}; mism = 0
    Mc = m_cells(eng, bb, gates, 'dev'); pick = []
    for d in gates['M_domains']:
        cs = [c for c in Mc if c[0] == d]; pick += [c for c in cs if c[1] in ('F_empty', 'F_{1}', 'F_not1')] + [c for c in cs if c[1].startswith(('C1n', 'SC3U4'))][:4] + [c for c in cs if c[1] == 'RRR16full']
    for d, name, ops, fam in pick: mism += run_and_compare(eng, bb, d, name, ops, vote_model(bb, d), log)
    for d in gates['M_domains']:
        T = m_base_ops(bb, d, gates, slots(bb, d, 'dev')); N = len(S.states(d))
        log.setdefault('G60_M_dev_R2N', {})[d] = dev_chain(eng, bb, d, 'natural', T, ['plus'] * (2 * N))[-1]['rate']
        run_chain(eng, bb, d, 'natural', 'reencode', None, 'plus_from_start', 'world_start', ['plus'] * 2, split='dev')
        log.setdefault('reencode_dev_R2', {})[d] = chain_rate(bb, d, 'natural', 'reencode', 'plus_from_start', 2)['rate']
    if bb == 'bart':
        Cc = c_cells(eng, 'dev'); pick = []
        for d in C_DOMAINS:
            cs = [c for c in Cc if c[0] == d]; pick += [c for c in cs if c[1] in ('F_empty', 'F_{1}')] + [c for c in cs if c[3] == 'CT1'][:2] + [c for c in cs if c[1].startswith('C3n')][:2]
        for d, name, ops, cset in pick: mism += run_and_compare(eng, bb, d, name, ops, ctx_model(bb, d, 'dev'), log)
        seen = set()
        for d, name, ops in k_cells(eng, 'dev'):
            kind = name.rsplit('_', 1)[0]
            if (d, kind) in seen: continue
            seen.add((d, kind)); ops = ops() if callable(ops) else ops
            run_chain(eng, bb, d, 'natural', name, ops, 'plus_from_start', 'world_start', K_PATHS['plus'][:3], split='dev')
            log.setdefault('K_dev_R3', {})[f'{d}/{name}'] = chain_rate(bb, d, 'natural', name, 'plus_from_start', 3)['rate']
        tr = read(V5DIR / 'results/train_new_bart_B.json')
        for s in SEEDS:
            from cells6 import k_load5
            ed = k_load5(V5DIR / tr[f'Tok/name3/s{s}']['path'], eng.d)
            log.setdefault('G60_K_name3_TokU_dev_R6', {})[s] = dev_chain(eng, bb, 'name3', 'natural', {op: ed[op] for op in ('plus', 'minus')}, ['plus'] * 6)[-1]['rate']
    log['argmax_mismatches'] = mism; log['pass'] = mism == 0
    log['sources'] = {f: sha(ROOT / f) for f in LOCKED6 + ['simulate.py', 'lock.py', 'train_new.py', 'gates.py', 'calib_mt.py', 'calib_ctx.py', 'smoke.py'] if (ROOT / f).exists()}
    log['seconds'] = time.time() - t0; log['resources'] = eng.resources(); dump(f'results/smoke_{bb}.json', log)
    print(json.dumps({k: v for k, v in log.items() if k not in ('sources', 'cells')}, indent=1, default=str), flush=True)
    assert log['pass'], 'smoke test failed'


if __name__ == '__main__':
    main()
