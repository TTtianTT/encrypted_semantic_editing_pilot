"""E0.3 adjacent canonical-write angles on the time path +3 -> -3 (no decoding). Exploratory (exposed confirm worlds)."""
import time
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *
from e0_operators import operators, factors, apply, pad, DEV

PATH = [3, 2, 1, 0, -1, -2, -3]          # plus lowers relative date
KINK = {(2, 1), (1, 2), (-1, -2), (-2, -1)}  # length-changing transitions


def cos(a, b):
    return torch.nn.functional.cosine_similarity(a.double(), b.double(), dim=-1)


def flat(x, m):
    return (x * m[..., None]).flatten(1)


@torch.no_grad()
def main():
    require_slurm(); verify_inputs(['cache/conf/time_eval_t0', 'editor/time/', 'canonical_write_reachability_v1/local/rrr.pt'])
    t0 = time.time(); C = core(); res = {}
    cache = {}
    for s in PATH:
        p = CONF / f'local/time_eval_t0_s{s}.pt'
        q = ROOT / f'local/e0_conf_time_eval_t0_s{s}.pt'
        cache[s] = load(q if q.exists() else p)
    W = len(cache[0]['h']); pooled = {s: C.pool(cache[s]['h'].float(), cache[s]['m'].float()).double() for s in PATH}
    w = [pooled[PATH[k]] - pooled[PATH[k - 1]] for k in range(1, 7)]
    canon = []
    for k in range(1, 6):
        a, b = (PATH[k - 1], PATH[k]), (PATH[k], PATH[k + 1])
        c = cos(w[k - 1], w[k]).numpy()
        canon.append(dict(k=k, first=f'{a[0]:+d}->{a[1]:+d}', second=f'{b[0]:+d}->{b[1]:+d}', kink=bool(a in KINK or b in KINK),
                          pooled_cos=boot_mean(c)))
    # token-level cosine for the only fully aligned adjacent pair (+1->0, 0->-1)
    n = max(cache[s]['h'].shape[1] for s in (1, 0, -1))
    hp, mp = pad(cache[1]['h'].float(), cache[1]['m'].float(), n); h0, m0 = pad(cache[0]['h'].float(), cache[0]['m'].float(), n); hm, mm = pad(cache[-1]['h'].float(), cache[-1]['m'].float(), n)
    ok = ((mp == m0) & (m0 == mm)).all(1)
    tok = cos(flat(h0 - hp, m0)[ok], flat(hm - h0, m0)[ok]).numpy()
    res['canonical'] = dict(adjacent=canon, aligned_pair_token_cos=dict(**boot_mean(tok), aligned_worlds=int(ok.sum())), worlds=W)
    # editors: two consecutive plus updates from E(y_{+1}); CE_all along +3 -> -3 (6 steps)
    ops = operators(); ed = []
    h1, m1 = cache[1]['h'].float().to(DEV), cache[1]['m'].float().to(DEV)
    for name, spec in ops.items():
        if spec['domain'] != 'time' or spec['family'] not in ('C1', 'C3', 'RRR16', 'CE_all'):
            continue
        F = factors(spec)
        a = apply(F['plus'], h1, m1); b = apply(F['plus'], a, m1)
        u1, u2 = a - h1, b - a
        r = dict(name=name, family=spec['family'], seed=spec['seed'],
                 two_step_from_plus1=dict(pooled_cos=boot_mean(cos(C.pool(u1, m1), C.pool(u2, m1)).cpu().numpy()),
                                          token_cos=boot_mean(cos(flat(u1, m1), flat(u2, m1)).cpu().numpy())))
        if spec['family'] == 'CE_all':
            h, m = cache[3]['h'].float().to(DEV), cache[3]['m'].float().to(DEV); us = []
            for _ in range(6):
                z = apply(F['plus'], h, m); us.append(C.pool(z - h, m)); h = z
            r['six_step_from_plus3'] = [dict(k=k, pooled_cos=boot_mean(cos(us[k - 1], us[k]).cpu().numpy())) for k in range(1, 6)]
        ed.append(r); print(name, r['two_step_from_plus1']['pooled_cos']['mean'], flush=True)
    res['editors'] = ed
    res['ideal_open_boundary_reference'] = dict(formula='c = -(1 - exp(-delta/sigma))/2', interval=[-0.5, 0.0])
    res['g3_reference_cited_only'] = dict(values=[0.519, 0.927, 0.967, 0.969], note='different generator; not compared statistically')
    res['note'] = 'Exploratory: canonical_confirmation 160 confirm worlds were already evaluated.'
    res['seconds'] = time.time() - t0
    dump('results/e0_writes.json', res)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    ks = [c['k'] for c in canon]; mu = [c['pooled_cos']['mean'] for c in canon]
    lo = [c['pooled_cos']['mean'] - c['pooled_cos']['ci95'][0] for c in canon]; hi = [c['pooled_cos']['ci95'][1] - c['pooled_cos']['mean'] for c in canon]
    axs[0].errorbar(ks, mu, yerr=[lo, hi], fmt='o-', color='#3b6fb6', capsize=3)
    for c in canon:
        axs[0].annotate(f"{c['first']},{c['second']}" + (' *' if c['kink'] else ''), (c['k'], c['pooled_cos']['mean']), fontsize=6, xytext=(3, 6), textcoords='offset points')
    axs[0].axhspan(-.5, 0, color='#dddddd', alpha=.5, label='ideal open-boundary range'); axs[0].axhline(.5, color='#c44', lw=.7, ls='--', label='G0(b) bound')
    axs[0].set_xlabel('adjacent pair k (* = kink)'); axs[0].set_ylabel('cos(w_k, w_k+1), pooled'); axs[0].legend(fontsize=7)
    fams = ['C1', 'C3', 'RRR16', 'CE_all']; cols = ['#d08c2f', '#3b6fb6', '#555555', '#8a4fb3']
    for i, (f, col) in enumerate(zip(fams, cols)):
        v = [r['two_step_from_plus1']['pooled_cos']['mean'] for r in ed if r['family'] == f]
        axs[1].plot([i] * len(v), v, 'o', color=col)
    axs[1].axhline(canon[2]['pooled_cos']['mean'], color='#3b6fb6', ls=':', label='canonical +1->0->-1')
    axs[1].set_xticks(range(len(fams))); axs[1].set_xticklabels(fams); axs[1].set_ylabel('cos of 2 consecutive plus updates'); axs[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(ROOT / 'figs/e0_writes.png', dpi=150)


if __name__ == '__main__':
    main()
