"""Encode canonical states (GPU, before the lock; PLAN 2 new rule 1: confirm5 may be encoded, never decoded, before the lock).
--backbone bart|t5. BART: confirm5 of the six L domains and of bind3 / name3 / bind3fix (template 3); multi-template domains kept in N
(data/templates_split.json): train, dev, confirm5. T5Gemma: confirm5 of weekday, month, hour, compass8; month-mt train, dev, confirm5.
(Template-0 and binding train/dev caches come from v1 / v3 / v4.)"""
import time
from lib5 import *


def todo(bb):
    sp = read(ROOT / 'data/templates_split.json')['split']
    out = [(d, CONFIRM) for d in L_DOMAINS[bb] + (B_DOMAINS if bb == 'bart' else [])]
    out += [(d, s) for d in MT_DOMAINS[bb] if sp[d]['in_N'] for s in ('train', 'dev', CONFIRM)]
    return out


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb); done = []
    for d, sp in todo(bb):
        encode_split5(eng, bb, d, sp, bs=32); done.append(f'{d}/{sp}'); print('encoded', bb, d, sp, flush=True)
    files = {}
    for d, sp in todo(bb):
        for s in S.states(d):
            p = cpath(bb, d, sp, s); files[p.name] = dict(sha256=sha(p), bytes=p.stat().st_size)
    dump(f'results/d_encode_{bb}_complete.json', dict(done=done, files=files, resources=eng.resources(), seconds=time.time() - t0))


if __name__ == '__main__':
    main()
