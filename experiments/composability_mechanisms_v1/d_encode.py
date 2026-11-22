"""Encode canonical states. Default: S1b train/dev (template 0 token caches + pooled t0/t3) before the lock.
encode_split() is also used by eval_chains after the lock for confirm2 / S1b confirm (asserts the lock)."""
import time
import torch
from symutil import *
import sym2_semantics as S


@torch.no_grad()
def encode_split(eng, d, split, templates=(0,), token=True):
    if split in ('confirm', 'confirm2'):
        assert (ROOT / 'protocol.json').exists() and read(ROOT / 'protocol.json').get('locked') is True, 'confirm encodings only after the lock'
    C = core(); ws = worlds2(d, split); ids = [w['world_id'] for w in ws]
    for t in templates:
        pooled = []
        for s in S.states(d):
            f = ROOT / (f'local/c_{d}_{split}_t0_s{s}.pt' if t == 0 else f'local/c_{d}_{split}_t{t}_s{s}.pt')
            if f.exists() and load(f)['world_ids'] == ids:
                c = load(f); pooled.append(C.pool(c['h'].float(), c['m'].float())); continue
            hs = []; ms = []
            for i in range(0, len(ws), 32):
                h, m = eng.encode([S.render(w, s, t) for w in ws[i:i + 32]]); hs.append(h.cpu()); ms.append(m.cpu())
            h = torch.cat(hs); m = torch.cat(ms); n = int(m.sum(1).max()); h, m = h[:, :n].contiguous(), m[:, :n].contiguous()
            pooled.append(C.pool(h, m))
            if token: save(f, dict(h=h, m=m, world_ids=ids))
        save(f'local/c_pooled_{d}_{split}_t{t}.pt', dict(pooled=torch.stack(pooled, 1), world_ids=ids, states=S.states(d)))


def main():
    require_slurm(); verify_inputs(['model/']); t0 = time.time(); eng = engine()
    for d in S1B_DOMAINS:
        for split in ('train', 'dev'):
            encode_split(eng, d, split, (0, 3)); print('encoded', d, split, flush=True)
    dump('results/d_encode_train_dev_complete.json', dict(resources=eng.resources(), seconds=time.time() - t0,
         files={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted((ROOT / 'local').glob('c_*.pt'))}))


if __name__ == '__main__':
    main()
