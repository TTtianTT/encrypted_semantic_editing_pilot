"""Unit D layer choice and CE editors (GPU, before the lock; plan change of 2026-11-25 by the lead, DEVIATIONS 7).
Layer rule (replaces B.2 step 6's 'ties to the shallower layer'): among the candidate layers whose dev single plus step of S-RRR-16 equals
the maximum (d_prep.py layer selection), the primary layer is the median (lower median for an even count); chosen only from the single-step
check, before any chain result. Secondary layers (exploratory, closed-form measurements only): the shallowest and the deepest tied layer.
The CE slot editors (rank-16 affine on the slot latent; 600 updates, batch 8, AdamW 1e-3, clip 1, seeds 50-52) are trained at the primary
layer only. The layer-2 editors of d_prep.py (local/d_C1_s*.pt) are kept on disk but not used.
Output: results/d_layer.json, local/d_C1_l<l>_s<s>.pt."""
import time
from d_prep import *


def main():
    require_slurm(); t0 = time.time(); prep = read(ROOT / 'results/d_prep.json'); sel = {int(k): v['rate'] for k, v in prep['layer_selection'].items()}
    best = max(sel.values()); tied = sorted(l for l, r in sel.items() if r == best); primary = tied[(len(tied) - 1) // 2]
    res = dict(rule='median of the tied layers (lower median for an even count); secondary: shallowest and deepest tied layer (DEVIATIONS 7)',
               profile=sel, tied=tied, primary=primary, secondary=[tied[0], tied[-1]] if len(tied) > 1 else [], gate=prep['gate'],
               continue_=bool(prep['gate'] and best >= .90))
    print('D layer', res, flush=True)
    if not res['continue_']: dump(ROOT / 'results/d_layer.json', res); return
    eng = DEngine(); W = {sp: worlds5(D, sp) for sp in ('train', 'dev')}; L = {sp: load(ROOT / f'local/d_latents_{sp}.pt') for sp in ('train', 'dev')}
    res['C1'] = {}
    for s in (50, 51, 52):
        ed, hist = train_c1(eng, W['train'], L['train']['pos'], L['train']['latents'][primary], primary, s)
        r = c1_single(eng, W['dev'], L['dev']['pos'], L['dev']['latents'][primary], ed, primary); f = ROOT / f'local/d_C1_l{primary}_s{s}.pt'
        save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, layer=primary, dev_single=r, updates=600))
        write(f'results/train_new/d_C1_l{primary}_s{s}.jsonl', hist); res['C1'][f's{s}'] = dict(dev_single=r, sha256=sha(f)); print('D C1', primary, s, r['rate'], flush=True)
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(ROOT / 'results/d_layer.json', res)


if __name__ == '__main__':
    main()
