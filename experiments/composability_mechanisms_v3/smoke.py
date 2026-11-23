"""Pre-lock smoke test (GPU; dev data only; not a locked source). --backbone bart|t5. Runs the code paths of every post-lock job on dev
worlds with the pre-lock derived quantities (lock.sections), writing only to local/smoke/: g40.run, v_chains.run, r_chains.run,
u_run.train/evaluate (a few updates), x_run.train/evaluate/attention_mass (name3 only, a few updates; nothing for bind3), s_long.run,
and the analysis units and figures. Also the A.8.3 real-decoder check: the S = 1 unrolled loss equals v3's single-step CE.
No confirm4 data are encoded or decoded."""
import shutil
import time
import lib4
from lib4 import *
import lock, g40, v_chains, r_chains, s_long, u_run, x_run, analyze

SM = ROOT / 'local/smoke'


def ce_identity(eng):
    """A.8.3 on the real decoder: S = 1 unrolled loss == v3 train_editor's single-step CE, same batch, same editor."""
    source_path(); from backend import editors
    d = 'weekday'; ws = worlds4(d, 'train'); C = {s: cache4('bart', d, 'train', s) for s in S.states(d)}; dt = mdtype(eng)
    ed = editors(eng.d, 42)
    with torch.no_grad():
        for op in ed: ed[op].u.weight.normal_(std=.05)
    its = [(i, s) for i, s in zip(range(8), [0, 3, 6, 1, 2, 5, 4, 0])]
    h = torch.stack([C[s]['h'][i] for i, s in its]).cuda(); m = torch.stack([C[s]['m'][i] for i, s in its]).cuda(); diffs = []
    for op in ('plus', 'minus'):
        texts = [S.render(ws[i], S.advance(d, s, op), 0) for i, s in its]
        with torch.no_grad():
            ref = eng.ce(ed[op](h, m).to(dt), m, texts)[0].mean()
            got, _, _ = unrolled_loss(ed, lambda hh, mm, tt: eng.ce(hh.to(dt), mm, tt)[0].mean(), None, h, m, [op], [texts])
        diffs.append(abs(float(ref - got)))
    return dict(max_abs_diff=max(diffs), pass_=max(diffs) < 1e-6)


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time()
    lib4.SHARDS = SM / f'shards_{bb}'; analyze.lib4.SHARDS = lib4.SHARDS
    if lib4.SHARDS.exists(): shutil.rmtree(lib4.SHARDS)
    (SM / 'figs').mkdir(parents=True, exist_ok=True)
    p = lock.sections(bbs=(bb,)); eng = engine4(bb); log = {}
    g = g40.run(eng, p, bb, split='dev'); log['g40'] = dict(base={d: v['R_2N']['rate'] for d, v in g['base'].items()}, C1={k: v['rate'] for k, v in g['C1'].items()},
                                                            V_post=g['V_domains_post'], pass_=g['pass'])
    G = {bb: g, ('t5' if bb == 'bart' else 'bart'): dict(V_domains_post=[])}
    v_chains.run(eng, p, bb, g['V_domains_post'], split='dev'); log['V_domains'] = g['V_domains_post']
    rd = [d for d in p['gates'][bb]['R_domains'] if d in g['V_domains_post']][:1]
    r_chains.run(eng, p, bb, rd, split='dev', max_steps=None if bb == 'bart' else 3); log['R_domains'] = rd
    if bb == 'bart':
        log['A8_3_ce_identity'] = ce_identity(eng)
        tr = u_run.train(eng, only=[('C1U4', 'weekday', 42), ('C1UN', 'weekday', 42), ('C3U4', 'month', 42)], updates=(4,), out_dir='local/smoke', res_dir='local/smoke')
        ue = u_run.evaluate(eng, tr, split='dev', out_dir='local/smoke', doms=('weekday', 'month')); log['U_train'] = {k: v for k, v in tr.items() if '/u' not in k}
        xt = x_run.train(eng, doms=['name3'], updates=(4,), out_dir='local/smoke', seeds=(42,)); log['X_train'] = xt
        xe = x_run.evaluate(eng, xt, split='dev', doms=['name3'], out_dir='local/smoke', seeds=(42,))
        att = x_run.load_pair(ROOT / 'local/smoke/x_Att_name3_s42_u4.pt', eng.d); log['X_attention_name3'] = x_run.attention_mass(eng, att, 'name3', 'dev')
    else:
        s_long.run(eng, split='dev', max_steps=3); ue = xt = xe = None
    # analysis units on the smoke shards
    analyze.load_chains(); crow = analyze.tables(); log['tables_rows'] = len(crow)
    V = analyze.v_unit(p, G); R = analyze.r_unit(p, G)
    log['V'] = dict(Q9=V['Q9'], V1=V['V1']['verdict'], V2a=V['V2a']['verdict'], V2b=V['V2b']['verdict'], V3={k: V['V3'][k]['verdict'] for k in ('vs_fund', 'vs_flat')},
                    V4={b: V['V4'][b].get('verdict') for b in V['V4']}, V0=V['V0']['pass_'])
    log['R'] = dict(verdict=R['R1']['verdict'], cells=len(R['R1']['cells']))
    shares = {bb: {d: analyze.vote_share(p, bb, d) for d in g['V_domains_post'][:2]}}
    if bb == 'bart':
        U = analyze.u_unit(p, tr, ue); log['U'] = dict(U1=U['U1']['verdict'], U2=U['U2']['verdict'], Q11=U['Q11']['verdict'])
        saved = analyze.SEEDS; analyze.SEEDS = (42,)
        X = analyze.x_unit(p, dict(xt, x_status='go'), xe); analyze.SEEDS = saved; log['X'] = {k: v.get('verdict', v.get('pass_')) for k, v in X.items() if k in ('X1', 'X2', 'Q12')}
        Sx = dict(S1=dict(verdict='n/a (bart)'))
    else:
        U, X = dict(R1={}), dict(); Sx = analyze.s_unit(p); log['S'] = Sx['S1']
    root = analyze.ROOT; analyze.ROOT = SM
    try: analyze.figures(p, G, V, R, U if bb == 'bart' else {}, X, shares)
    finally: analyze.ROOT = root
    log['figures'] = sorted(f.name for f in (SM / 'figs').glob('*.png'))
    ok_g = all(v >= .95 for v in log['g40']['base'].values()) and (bb == 't5' or all(v <= .20 for v in log['g40']['C1'].values()))
    log['pass'] = bool(ok_g and (bb == 't5' or log['A8_3_ce_identity']['pass_']))
    log['sources'] = {f: sha(ROOT / f) for f in LOCKED4 + ['lock.py', 'smoke.py', 'gates.py', 'calib.py', 'prelock_fits.py']}
    log['seconds'] = time.time() - t0; log['resources'] = eng.resources()
    dump(f'results/smoke_{bb}.json', log); print(json.dumps({k: v for k, v in log.items() if k != 'sources'}, indent=1, default=str)[:5000], flush=True)
    assert log['pass'], 'smoke test failed'


if __name__ == '__main__':
    main()
