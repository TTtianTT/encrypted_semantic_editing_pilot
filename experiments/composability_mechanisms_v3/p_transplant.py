"""P5 (GPU, exploratory): same-world transplant classification on v3 confirm3. --bb bart: v1 C1 (5 domains x seeds 42-44);
--bb t5: v3 T5Gemma C1 (weekday, month, compass x seeds 42-44). The plus write of source state s, added to another state s' of the same
world, is decoded and classified: relative (decodes plus(s') with full success) / absolute (decodes plus(s)) / null (decodes s') /
other / unparsable. Also M1 and M2 (v2 definitions). Question: under the natural map, is 'relative' the majority only in weekday/month?"""
import time
from lib4 import *


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--bb') + 1]; t0 = time.time(); eng = engine4(bb); res = {}
    doms = V1_DOMAINS if bb == 'bart' else ['weekday', 'month', 'compass']
    for d in doms:
        for s in SEEDS:
            path = V1 / f'local/e1_C1_{d}_s{s}_0600.pt' if bb == 'bart' else V3DIR / f'local/t5_C1_{d}_s{s}.pt'
            ed = load_editor(eng, path); wm = write_metrics(eng, bb, d, 'natural', ed['plus'], None, split='confirm3', m4=True); wm.pop('writes')
            res[f'{d}/C1_s{s}'] = wm
            print('P5', bb, d, s, {k: round(v, 3) for k, v in wm['M4'].items() if k != 'n'}, round(time.time() - t0), flush=True)
        cls = ('relative', 'absolute', 'null', 'other', 'unparsable')
        med = {c: float(np.median([res[f'{d}/C1_s{s}']['M4'].get(c, 0.) for s in SEEDS])) for c in cls}
        res[f'{d}/median'] = dict(classes=med, majority=max(med, key=med.get), relative_is_majority=med['relative'] > .5)
    res['relative_majority_domains'] = [d for d in doms if res[f'{d}/median']['relative_is_majority']]
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump(f'results/patch/p5_transplant_{bb}.json', res)


if __name__ == '__main__':
    main()
