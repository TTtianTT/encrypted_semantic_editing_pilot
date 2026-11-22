"""Algebra (CPU, after the fits): unit-block harmonics for T5Gemma RRR fits, BART S1b' fits, BART v2 natural fits (entry order),
N-unit C1 editors (exploratory); Spearman between s_k order and harmonic entry order."""
import time
from scipy.stats import spearmanr
from lib3 import *


def fit_blocks(path, N, prefix, res):
    f = load(path)
    for (op, r) in sorted(k for k in f if isinstance(k, tuple) and k[0] == 'plus'):
        res[f'{prefix}/RRR{r}'] = harmonics_of(*editor_factors('rrr', f['plus', r], 'plus'), N)


def main():
    require_slurm(); p = verify_protocol3(); t0 = time.time(); res = {}
    for d in CYC: fit_blocks(V2DIR / f'local/rrr_{d}_natural.pt', len(S.states(d)), f'bart/{d}/natural', res)
    for f in sorted((ROOT / 'local').glob('bart_rrr_*_natural_r*.pt')):
        d = f.name.split('_')[2]; fit_blocks(f, len(S.states(d)), f'bart/{d}/natural', res)
    for d in p['gates']['bart']['B_domains']:
        if (ROOT / f'local/bart_rrr_{d}_natural.pt').exists(): fit_blocks(ROOT / f'local/bart_rrr_{d}_natural.pt', 3, f'bart/{d}/natural', res)
    for f in sorted((ROOT / 'local').glob('t5_rrr_*_*.pt')):
        if f.name.endswith('_pre.pt'): continue
        _, _, d, mp = f.stem.split('_'); fit_blocks(f, len(S.states(d)), f't5/{d}/{mp}', res)
    for f in sorted((ROOT / 'local').glob('n_C1_*.pt')):
        sd = load(f)['editor']; d = f.name.split('_')[2]; res[f'bart/N/{f.stem}'] = harmonics_of(*editor_factors('editor', sd, 'plus'), len(S.states(d)))
    order = {}
    for bb, doms in (('bart', CYC), ('t5', p['gates']['t5']['T_rrr_domains'])):
        for d in doms:
            amp = p['amplitudes'][bb].get(d)
            if not amp: continue
            ranks = sorted(int(k.split('RRR')[1]) for k in res if k.startswith(f'{bb}/{d}/natural/RRR'))
            entry = {}
            for k in map(int, amp):
                hit = [r for r in ranks if k in res[f'{bb}/{d}/natural/RRR{r}']['harmonics_present']]; entry[k] = min(hit) if hit else None
            ks = [k for k in entry if entry[k] is not None]
            rho = spearmanr([amp[str(k)]['s'] for k in ks], [entry[k] for k in ks])[0] if len(ks) > 2 else None
            order[f'{bb}/{d}'] = dict(entry_rank=entry, s_k={k: amp[str(k)]['s'] for k in map(int, amp)}, spearman_s_vs_entry=None if rho is None or rho != rho else float(rho))
    res['_s_k_vs_entry_order'] = order; res['_seconds'] = time.time() - t0
    dump('results/algebra.json', res)


if __name__ == '__main__':
    main()
