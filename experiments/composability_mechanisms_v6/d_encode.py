"""Encode confirm7 and dev7-ho (GPU, before the lock; PLAN v7 B1: confirm7 may be encoded, never decoded, before the lock).
--backbone bart|t5. BART: weekday-mt, month-mt, hour-mt (confirm7 and dev7-ho, held-out templates), weekday, month (confirm7, template 0),
bind3, name3, bind3fix (confirm7, template 3). T5Gemma: month-mt (confirm7, dev7-ho), month (confirm7, template 0; U non-inferiority set)."""
import time
from lib7 import *


def todo(bb):
    if bb == 'bart': return [(d, sp) for d in M_DOMAINS['bart'] for sp in (CONFIRM, 'dev7ho')] + [(d, CONFIRM) for d in C_DOMAINS + K_DOMAINS]
    return [('month-mt', CONFIRM), ('month-mt', 'dev7ho'), ('month', CONFIRM)]


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
