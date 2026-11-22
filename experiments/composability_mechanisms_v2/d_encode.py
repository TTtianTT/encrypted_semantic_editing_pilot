"""Encode canonical states. --backbone bart|t5 --stage pre|confirm3.
pre: BART S1b' (template 3) train/dev; T5Gemma weekday/month/compass (template 0) train/dev.
confirm3 (after the lock): BART five v1 domains + S1b' retained domains; T5Gemma retained T domains."""
import time
from lib3 import *


def arg(k): return sys.argv[sys.argv.index(k) + 1]


def main():
    require_slurm(); bb = arg('--backbone'); stage = arg('--stage'); t0 = time.time(); eng = engine3(bb); done = []
    if stage == 'pre':
        todo = [(d, sp) for d in (S.S1B if bb == 'bart' else T_DOMAINS) for sp in ('train', 'dev')]
    else:
        p = read(ROOT / 'protocol.json'); assert p['locked']
        doms = (V1_DOMAINS + p['gates']['bart']['B_domains']) if bb == 'bart' else p['gates']['t5']['T_domains']
        todo = [(d, 'confirm3') for d in doms]
    for d, sp in todo:
        encode_split3(eng, bb, d, sp, bs=32); done.append(f'{d}/{sp}'); print('encoded', bb, d, sp, flush=True)
    dump(f'results/d_encode_{bb}_{stage}_complete.json', dict(done=done, resources=eng.resources(), seconds=time.time() - t0,
         files={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted((ROOT / 'local').glob(f'{bb}_*.pt'))
                if ('confirm3' in p.name) == (stage == 'confirm3')}))


if __name__ == '__main__':
    main()
