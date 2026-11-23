"""Encode canonical states (GPU). --backbone bart|t5 --stage pre|confirm4.
pre: BART hour/compass8/season and bind3/bind3fix/name3 train+dev; T5Gemma hour/compass8/season train+dev
(weekday/month/compass train+dev caches come from v1 (BART) and v3 (T5Gemma)).
confirm4 (after the lock only): BART: V domains kept by GB + compass + X domains; T5Gemma: V domains kept by GB + S domains."""
import time
from lib4 import *


def arg(k): return sys.argv[sys.argv.index(k) + 1]


def main():
    require_slurm(); bb = arg('--backbone'); stage = arg('--stage'); t0 = time.time(); eng = engine4(bb); done = []
    if stage == 'pre':
        doms = ['hour', 'compass8', 'season'] + (X_DOMAINS if bb == 'bart' else [])
        todo = [(d, sp) for d in doms for sp in ('train', 'dev')]
    else:
        p = verify_protocol4(); g = p['gates'][bb]
        doms = list(dict.fromkeys(g['V_domains'] + (['compass'] + X_DOMAINS if bb == 'bart' else S_DOMAINS)))
        todo = [(d, CONFIRM) for d in doms]
    for d, sp in todo:
        encode_split4(eng, bb, d, sp, bs=32); done.append(f'{d}/{sp}'); print('encoded', bb, d, sp, flush=True)
    dump(f'results/d_encode_{bb}_{stage}_complete.json', dict(done=done, resources=eng.resources(), seconds=time.time() - t0,
         files={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted((ROOT / 'local').glob(f'{bb}_*.pt'))
                if (CONFIRM in p.name) == (stage == CONFIRM) and p.name.count('_') >= 4 and '_t' in p.name}))


if __name__ == '__main__':
    main()
