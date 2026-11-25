"""AMENDMENT_01 (2026-11-26, lead: exploratory parts must not be dropped). Completes unit D's edge layers if the locked d_run.py skipped any
under its time guard (out['skipped']): each skipped layer is measured with the locked d_run.measure (same procedures, closed form only) and
merged into results/d_run.json; the record of what d_run.py skipped is kept (completed_by_amendment). No-op if nothing was skipped."""
import time
import d_run as R
from dlib import *


def main():
    require_slurm(); assert R.lock_ok(); t0 = time.time(); f = ROOT / 'results/d_run.json'; out = read(f); todo = list(out.get('skipped') or [])
    if not todo: print('d_edge: nothing skipped', flush=True); return
    eng = DEngine(); L = {sp: load(ROOT / f'local/d_latents_{sp}.pt') for sp in ('train', 'confirm7')}
    ws = R.worlds5(R.D, 'confirm7'); pos = L['confirm7']['pos']; assert [w['world_id'] for w in ws] == L['confirm7']['world_ids']
    for l in todo:
        R.measure(eng, l, L['train'], L['confirm7'], ws, pos, [], out); out.setdefault('completed_by_amendment', []).append(l); dump(f, out)
    out['amendment_seconds'] = time.time() - t0; dump(f, out); print('d_edge completed', todo, flush=True)


if __name__ == '__main__':
    main()
