"""Encode confirm6 (GPU, before the lock; PLAN B1: confirm6 may be encoded, never decoded, before the lock). --backbone bart|t5.
BART: confirm6 of weekday-mt, month-mt, hour-mt (held-out templates), weekday, month (template 0), bind3, name3, bind3fix (template 3).
T5Gemma: confirm6 of month-mt. (train / dev caches: v5 multi-template, v1 / v4 template-0 and binding caches.)"""
import time
from lib6 import *


def todo(bb):
    return [(d, CONFIRM) for d in (M_DOMAINS['bart'] + C_DOMAINS + K_DOMAINS if bb == 'bart' else M_DOMAINS['t5'])]


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); done = []
    for d, sp in todo(bb):
        encode_split5(eng, bb, d, sp, bs=32); done.append(f'{d}/{sp}'); print('encoded', bb, d, sp, flush=True)
    files = {}
    for d, sp in todo(bb):
        for s in S.states(d):
            p = cpath(bb, d, sp, s); files[p.name] = dict(sha256=sha(p), bytes=p.stat().st_size)
        pos = slots(bb, d, sp); m = cache5(bb, d, sp, S.states(d)[0])['m']; assert bool(m[torch.arange(len(pos)), pos].all()), (d, 'slot on padding')
    dump(f'results/d_encode_{bb}_complete.json', dict(done=done, files=files, resources=eng.resources(), seconds=time.time() - t0))


if __name__ == '__main__':
    main()
