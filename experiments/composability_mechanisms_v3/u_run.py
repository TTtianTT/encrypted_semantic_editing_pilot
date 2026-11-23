"""U (BART, after the lock; section 8). --stage train: C1-U4 (weekday, month, compass; S in 1..4), C1-UN (weekday, month; S in 1..N),
C3-U4 (month; CE + normalised L2, lambda = 1; S in 1..4); rank-16 v1 editor structure, plus and minus trained jointly, random init,
seeds 42-44, 1200 updates (appendix A.4). Admission: dev one-way plus R_4 >= 0.90, else one retrain with 2400 updates, else 'cannot learn'.
Idempotent: an editor already saved is not retrained. --stage eval: confirm4 plus / minus / alternating 2N chains; probe readout of the
step-1 and step-2 states (v3 M3 probe); M1, M2; per-plane eps_k. References on confirm4: v1 C1 (2N chains) and P2's long C3 (month)."""
import time
from lib4 import *
from v_chains import PATHS

VARIANTS = {'C1U4': dict(doms=['weekday', 'month', 'compass'], S=lambda N: range(1, 5), l2=0.0),
            'C1UN': dict(doms=['weekday', 'month'], S=lambda N: range(1, N + 1), l2=0.0),
            'C3U4': dict(doms=['month'], S=lambda N: range(1, 5), l2=1.0)}


def cells():
    return [(v, d, s) for v, c in VARIANTS.items() for d in c['doms'] for s in SEEDS]


def train(eng, bb='bart', split_dev='dev', updates=(1200, 2400), only=None, out_dir='local', res_dir='results'):
    res = {}
    for v, d, s in (only or cells()):
        cfg = VARIANTS[v]; N = len(S.states(d)); st = None
        for upd in updates:
            f = ROOT / f'{out_dir}/u_{v}_{d}_s{s}_u{upd}.pt'
            if f.exists():
                c = load(f); r4 = c['dev_R4']
            else:
                ed, hist, scale = train_unrolled(eng, bb, d, s, list(cfg['S'](N)), updates=upd, l2_weight=cfg['l2'])
                r4 = dev_chain(eng, bb, d, 'natural', {op: ed[op] for op in ('plus', 'minus')}, ['plus'] * 4, split=split_dev)[-1]
                save(f, dict(editor={k: v_.cpu() for k, v_ in ed.state_dict().items()}, seed=s, dev_R4=r4, l2_scale=scale))
                write(f'{res_dir}/u_train_{v}_{d}_s{s}_u{upd}.jsonl', hist)
            res[f'{v}/{d}/s{s}/u{upd}'] = dict(dev_R4=r4, admitted=r4['rate'] >= .90); st = upd
            print('U train', v, d, s, upd, r4['rate'], flush=True)
            if r4['rate'] >= .90: break
        res[f'{v}/{d}/s{s}'] = dict(updates=st, admitted=res[f'{v}/{d}/s{s}/u{st}']['admitted'],
                                    status='ok' if res[f'{v}/{d}/s{s}/u{st}']['admitted'] else 'cannot learn')
    return res


def evaluate(eng, tr, split=CONFIRM, bb='bart', max_steps=None, m4=False, out_dir='local', doms=('weekday', 'month', 'compass')):
    res = {}
    for d in doms:
        N = len(S.states(d)); info, predict = probe(bb, d); res[f'{d}/probe'] = info
        eds = {}
        for v, c in VARIANTS.items():
            if d not in c['doms']: continue
            for s in SEEDS:
                st = tr.get(f'{v}/{d}/s{s}')
                if st is None: continue                                   # (smoke test: subset of cells)
                if st['admitted']: eds[f'{v}_s{s}'] = ROOT / f"{out_dir}/u_{v}_{d}_s{s}_u{st['updates']}.pt"
                else: res[f'{d}/{v}_s{s}'] = dict(status='cannot learn')
        for s in SEEDS:
            eds[f'C1v1_s{s}'] = V1 / f'local/e1_C1_{d}_s{s}_0600.pt'
            if d == 'month' and (ROOT / f'local/p2_a_C3_6000_month_s{s}.pt').exists(): eds[f'P2C3_s{s}'] = ROOT / f'local/p2_a_C3_6000_month_s{s}.pt'
        for name, path in eds.items():
            ed = load_editor(eng, path); ops = {op: ed[op] for op in ('plus', 'minus')}
            for pn, oplist in PATHS(N).items(): run_chain(eng, bb, d, 'natural', name, ops, pn, 'world_start', oplist[:max_steps], split=split)
            wm = write_metrics(eng, bb, d, 'natural', ed['plus'], predict, split=split, m4=m4, T2=ed['plus']); wm.pop('writes')
            sd = {k: v_.cpu() for k, v_ in ed.state_dict().items()}
            wm['eps'] = {str(k): v_['eps'] for k, v_ in op_plane_errors('editor', sd, 'plus', bb, d).items()}
            wm['algebra'] = harmonics_of(*editor_factors('editor', sd, 'plus'), N)
            res[f'{d}/{name}'] = wm
            print('U eval', d, name, 'M1', round(wm['M1']['mean'], 3), 'M3', {k: round(x, 3) for k, x in wm['M3'].items() if k != 'n'}, flush=True)
    return res


def main():
    require_slurm(); p = verify_protocol4(); stage = sys.argv[sys.argv.index('--stage') + 1]; t0 = time.time(); eng = engine4('bart')
    if stage == 'train':
        res = train(eng); res['seconds'] = time.time() - t0; dump('results/u_train.json', res); return
    res = evaluate(eng, read(ROOT / 'results/u_train.json')); res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump('results/u_eval.json', res)


if __name__ == '__main__':
    main()
