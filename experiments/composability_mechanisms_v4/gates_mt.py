"""GR for the multi-template domains (GPU, train + dev only, before the template split; PLAN 5.3). --backbone bart|t5.
Every (backbone, template) that passed GT (data/audit.json) is rendered on all train + dev worlds of its domain in every state, encoded and
decoded (reencode); single-step success >= 0.99 passes, otherwise the template is removed for that backbone. Templates are not edited."""
import time
from lib5 import *


@torch.no_grad()
def reencode_template(eng, d, tid, bs):
    ws = [dict(w, template_id=tid) for sp in ('train', 'dev') for w in worlds5(d, sp)]; items = [(w, s) for w in ws for s in S.states(d)]; ok = []
    for lo in range(0, len(items), bs):
        part = items[lo:lo + bs]; h, m = eng.encode([S.render(w, s) for w, s in part])
        for o, (w, s) in zip(dec(eng, h, m), part): ok.append(Ev.score(o['text'], S.gold(w, s), w, o['ended'])['success'])
    return rate(ok)


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    audit = read(ROOT / 'data/audit.json'); res = dict(backbone=bb, GR={})
    for d in MT_DOMAINS[bb]:
        res['GR'][d] = {}
        for tid in sorted(int(i) for i in audit['domains'][d]['GT_pass'][bb]):
            r = reencode_template(eng, d, tid, 64 if bb == 'bart' else 32); res['GR'][d][str(tid)] = dict(r, pass_=r['rate'] >= .99)
            print('GR', bb, d, tid, round(r['rate'], 4), flush=True)
    res['GT_failed'] = {d: audit['domains'][d]['GT_fail'][bb] for d in MT_DOMAINS[bb]}
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/gates_mt_{bb}.json', res)


if __name__ == '__main__':
    main()
