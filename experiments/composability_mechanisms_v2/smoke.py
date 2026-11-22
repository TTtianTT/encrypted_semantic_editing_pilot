"""Pre-lock smoke test (GPU; dev data only; not a locked source). Exercises the post-lock code paths of h_chains, b_run (pron3 only),
n_run, a_run, t_run, algebra and analyze on dev worlds, writing shards to local/smoke_shards. No confirm3 data are encoded or decoded;
no bind3 / bind3fix editor is fitted."""
import shutil
import time
from lib3 import *
import lib3
import h_chains, b_run, n_run, a_run, t_run, algebra, analyze


def fake_protocol():
    gb, gt = read(ROOT / 'results/gates_bart.json'), read(ROOT / 'results/gates_t5.json')
    cb, ct = read(ROOT / 'results/calib_bart.json'), read(ROOT / 'results/calib_t5.json')
    cal = lambda c: {d: dict(models=v['models'], derived=v['derived'], Kstar=v['Kstar'], planes=v['planes']) for d, v in c['domains'].items()}
    return dict(gates=dict(bart=dict(B_domains=gb['B_domains'], B4p_delta=gb['B4p_delta']), t5=dict(T_domains=gt['T_domains'], T_rrr_domains=gt['T_rrr_domains'])),
                calib=dict(bart=cal(cb), t5=cal(ct)), amplitudes=dict(bart=gb['amplitudes'], t5=gt['amplitudes']))


def main():
    require_slurm(); t0 = time.time(); lib3.SHARDS = ROOT / 'local/smoke_shards'; analyze.lib3.SHARDS = lib3.SHARDS
    if lib3.SHARDS.exists(): shutil.rmtree(lib3.SHARDS)
    p = fake_protocol(); log = {}
    dev_slots = lambda bb, d, split: lib3.slots(bb, d, 'dev')
    eng = engine3('bart')
    # H on weekday (full condition set, 3 paths x 2N) + month conditions (3 steps)
    h_chains.slots = dev_slots
    for d, steps in (('weekday', None), ('month', 3)):
        ops, P = h_chains.conditions(eng, p, d); N = len(S.states(d)); cal = p['calib']['bart'][d]
        model = dict(P=P, lams={m: torch.tensor(v['lam'], dtype=torch.float64) for m, v in cal['models'].items()})
        for name, op in ops.items():
            for pn, oplist in h_chains.paths3(N).items():
                run_chain(eng, 'bart', d, 'natural', name, op, pn, 'world_start', oplist if steps is None else oplist[:steps], split='dev', model=model)
        log[f'H_{d}'] = sorted(ops)
    hu = analyze.h_unit(p, 'bart', ['weekday']); log['h_unit'] = dict(Q5=hu['Q5'], HS4=hu['HS4']['winner'], HV1=hu['HV1'])
    # g30-like
    ed = load_editor(eng, V1 / 'local/e1_C1_weekday_s42_0600.pt'); run_chain(eng, 'bart', 'weekday', 'natural', 'C1_s42', {op: ed[op] for op in ('plus', 'minus')}, 'g30_plus', 'world_start', ['plus'] * 2, split='dev')
    log['g30_rate'] = chain_rate('bart', 'weekday', 'natural', 'C1_s42', 'g30_plus', 2)
    # B' (pron3 only)
    fits, info = fit_rrr3('bart', 'pron3', 'natural', [16, 32]); ed, hist, _ = train_editor(eng, 'bart', 'pron3', 'natural', 'C1', 42, updates=4)
    for name, ops in {'RRR16': {op: RRRop(fits[op, 16]) for op in ('plus', 'minus')}, 'C1_s42': {op: ed[op] for op in ('plus', 'minus')}, 'reencode': None}.items():
        for pn, oplist in b_run.PATHS.items(): run_chain(eng, 'bart', 'pron3', 'natural', name, ops, pn, 'world_start', oplist[:4], split='dev')
        run_singles(eng, 'bart', 'pron3', 'natural', name, ops, split='dev')
    log['B'] = dict(R4=chain_rate('bart', 'pron3', 'natural', 'RRR16', 'plus_from_start', 4), single=analyze.single('bart', 'pron3', 'natural', 'RRR16'))
    # N
    ed, hist, _ = train_editor(eng, 'bart', 'weekday', 'scrmax', 'C1', 42, updates=4); info, predict = probe('bart', 'weekday')
    wm = write_metrics(eng, 'bart', 'weekday', 'scrmax', ed['plus'], predict, split='dev', m4='keep'); Wr = wm.pop('writes')
    log['N'] = dict(probe=info, M1=wm['M1']['mean'], M3=wm['M3'], M4=wm['M4'], natcos=n_run.natural_step_cos(eng, Wr, 42, split='dev'))
    # A
    v2 = load(V2DIR / 'local/rrr_month_natural.pt'); ed, hist, _ = train_editor(eng, 'bart', 'month', 'natural', 'C3', 42, updates=4, l2_weight=10.0,
                                                                             init_rrr={op: v2[op, 16] for op in ('plus', 'minus')})
    sd = {k: v.cpu() for k, v in ed.state_dict().items()}
    log['A'] = dict(alg=harmonics_of(*editor_factors('editor', sd, 'plus'), 12), adj=a_run.adjacent_cos(ed, 'month', split='dev'))
    res_alg = {}; algebra.fit_blocks(V2DIR / 'local/rrr_month_natural.pt', 12, 'bart/month/natural', res_alg); log['algebra_keys'] = len(res_alg)
    del eng; torch.cuda.empty_cache()
    # T5Gemma
    e5 = engine3('t5'); d = 'weekday'; N = 7
    fits, info = fit_rrr3('t5', d, 'natural', [4, 16]); ops = {op: RRRop(fits[op, 16]) for op in ('plus', 'minus')}
    for pn, oplist in t_run.paths3(N, long_=True).items(): run_chain(e5, 't5', d, 'natural', 'RRR16', ops, pn, 'world_start', oplist[:3], split='dev')
    run_singles(e5, 't5', d, 'natural', 'RRR16', ops, split='dev')
    ed, hist, _ = train_editor(e5, 't5', d, 'natural', 'C1', 42, updates=4); info, predict = probe('t5', d)
    wm = write_metrics(e5, 't5', d, 'natural', ed['plus'], predict, split='dev', m4=True); wm.pop('writes')
    cal = p['calib']['t5'][d]; P = planes('t5', d); pos = lib3.slots('t5', d, 'dev'); X = slot_matrix('t5', d, 'train'); ks = [k for k, _ in P]
    B = torch.cat([b for k, b in P], 1); conds = {'F_empty': ops, 'F_{1}': {op: Freeze(ops[op], bvec(P, {1}), pos) for op in ops},
                                                 'F_not1': {op: Freeze(ops[op], bvec(P, set(ks) - {1}), pos) for op in ops},
                                                 'E_all': {op: PlaneEd(*fit_plane_editor(X, B, d, op), B, pos) for op in ('plus', 'minus')}}
    model = dict(P=P, lams={m: torch.tensor(v['lam'], dtype=torch.float64) for m, v in cal['models'].items()})
    for name, o in conds.items():
        for pn, oplist in t_run.paths3(N).items(): run_chain(e5, 't5', d, 'natural', name, o, pn, 'world_start', oplist, split='dev', model=model)
    ht = analyze.h_unit_t5(p, [d]); log['T5'] = dict(M1=wm['M1']['mean'], M3=wm['M3'], M4=wm.get('M4'), HS1=ht['HS1'], HV1=ht['HV1'], HS4=ht['HS4']['winner'])
    crow = analyze.tables(); log['tables_rows'] = len(crow)
    log['seconds'] = time.time() - t0; dump('results/smoke.json', log); print(json.dumps(log, indent=1, default=str)[:3000], flush=True)
    # tables() wrote results/chains.csv and singles.csv from smoke shards: remove them (they are not results)
    for f in ('results/chains.csv', 'results/singles.csv'):
        (ROOT / f).unlink(missing_ok=True)


if __name__ == '__main__':
    main()
