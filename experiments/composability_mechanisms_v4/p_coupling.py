"""P0 + P2 (CPU, exploratory; PLAN 4).
P0: locate and hash the v1-v4 inputs this round reuses (fits, editors, encoding caches, plane files, calibrations, v4 shards archives)
    -> inputs_manifest.json.
P2: for each base operator (two backbones, five V domains) take the slot linear part M (column convention M = (I + L R)^T of
    h' = h (I + L R) + b) and per harmonic plane j the leak ratio l_j = ||(I - P_j) M B_j||_F / ||B_j^T M B_j||_F; Spearman correlation
    with v4's F{j} harm (1 - one-way plus R_2N, results/predictions.json of v4). Report only."""
import glob
from lib5 import *

V_DOMS = ['weekday', 'month', 'hour', 'compass8', 'season']


def manifest():
    pats = []
    for d in ('weekday', 'month', 'compass'):
        pats += [V1 / f'local/e1_{d}_{sp}_t0_s*.pt' for sp in ('train', 'dev')] + [V1 / f'local/e1_C1_{d}_s4[234]_0600.pt', V2DIR / f'local/rrr_{d}_natural.pt']
        pats += [V3DIR / f'local/t5_{d}_{sp}_t0_s*.pt' for sp in ('train', 'dev')] + [V3DIR / f'local/planes_*_{d}.pt']
    pats += [V1 / 'local/e1_C3_month_s4[234]_0600.pt', V3DIR / 'local/a_C3_*_month_s4[234].pt', V3DIR / 'local/t5_C1_*_s4[234].pt',
             V3DIR / 'results/calib_bart.json', V3DIR / 'results/calib_t5.json', V3DIR / 'protocol.json']
    for d in V4_DOMAINS:
        pats += [V4DIR / f'local/*_{d}_{sp}_t*_s*.pt' for sp in ('train', 'dev')] + [V4DIR / f'data/{d}/worlds.jsonl']
    pats += [V4DIR / 'local/*_rrr_*_natural_base.pt', V4DIR / 'local/*_R_*.pt', V4DIR / 'local/planes_*.pt', V4DIR / 'local/u_*.pt', V4DIR / 'local/x_*.pt',
             V4DIR / 'local/p2_*_month_s*.pt', V4DIR / 'protocol.json', V4DIR / 'results/u_train.json', V4DIR / 'results/x_train.json',
             V4DIR / 'results/predictions.json', V4DIR / 'results/shards_*.tar.gz', V4DIR / 'data/slot_positions.json', V3DIR / 'data/slot_positions.json']
    for d in ('weekday', 'month', 'compass'): pats.append(V1 / f'data/{d}/worlds.jsonl')
    files = sorted({f for p in pats for f in glob.glob(str(p))})
    out = {str(Path(f).relative_to(REPO)): dict(sha256=sha(f), bytes=Path(f).stat().st_size) for f in files}
    for e in existing_editors('bart') + existing_editors('t5'):
        assert str(Path(e['path']).relative_to(REPO)) in out, e['path']
    return out


def leak(bb, d):
    f, r = base_fit(bb, d); P = planes(bb, d); res = {}
    for op in ('plus', 'minus'):
        L, R = f[op, r]['left'].double(), f[op, r]['right'].double(); M = torch.eye(L.shape[0], dtype=torch.float64) + (L @ R).T
        for k, B in P:
            B = B.double(); MB = M @ B; ins = B.T @ MB
            res[f'{op}/{k}'] = float((MB - B @ ins).norm() / ins.norm())
    return dict(rank=r, leak=res)


def spearman(x, y):
    rk = lambda v: np.argsort(np.argsort(v)).astype(float)
    a, b = rk(np.asarray(x)), rk(np.asarray(y)); return float(np.corrcoef(a, b)[0, 1])


def main():
    require_slurm(); t0 = time.time() if 'time' in dir() else None
    man = manifest(); dump('inputs_manifest.json', dict(created='2026-11-24', n_files=len(man), files=man))
    print('P0 manifest', len(man), 'files', flush=True)
    V = read(V4DIR / 'results/predictions.json')['V']['cells']; out = dict(operators={}, pairs=[])
    for bb in ('bart', 't5'):
        for d in V_DOMS:
            lk = leak(bb, d); out['operators'][f'{bb}/{d}'] = lk
            for k in [k for k, _ in planes(bb, d)]:
                c = V[f'{bb}/{d}'].get(f'F_{{{k}}}') or (V[f'{bb}/{d}'].get('F_not1') if d == 'season' and k == 2 else None)
                if c is None or c.get('plus') is None: continue
                out['pairs'].append(dict(backbone=bb, domain=d, plane=k, leak_plus=lk['leak'][f'plus/{k}'], leak_minus=lk['leak'][f'minus/{k}'],
                                         harm_plus=1 - c['plus'], harm_minus=None if c.get('minus') is None else 1 - c['minus']))
            print('P2', bb, d, {k: round(v, 3) for k, v in lk['leak'].items() if k.startswith('plus')}, flush=True)
    pr = out['pairs']; out['spearman'] = {}
    for sel, name in ((lambda p: True, 'all'), (lambda p: p['plane'] >= 2, 'j>=2'), (lambda p: p['backbone'] == 'bart', 'bart'), (lambda p: p['backbone'] == 't5', 't5')):
        q = [p for p in pr if sel(p)]
        out['spearman'][name] = dict(n=len(q), plus=spearman([p['leak_plus'] for p in q], [p['harm_plus'] for p in q]),
                                     minus=spearman([p['leak_minus'] for p in q if p['harm_minus'] is not None], [p['harm_minus'] for p in q if p['harm_minus'] is not None]))
    dump('results/patch/p2_coupling.json', out); print(json.dumps(out['spearman'], indent=1), flush=True)


if __name__ == '__main__':
    import time
    main()
