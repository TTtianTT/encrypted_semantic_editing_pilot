"""E1.2 / E1.5 encode: canonical last-layer encoder states for the new domains.

Default (E1.2): train and dev only. `--split confirm` is allowed only after the protocol lock (checked).
Token-level caches (template 0) for RRR fitting / training / evaluation; pooled states for templates 0 and 3.
"""
import time
import torch
from symutil import *
import sym_semantics as S


def lock_ok():
    p = ROOT / 'protocol.json'
    return p.exists() and read(p).get('locked') is True


@torch.no_grad()
def main():
    require_slurm(); verify_inputs(['model/'])
    splits = ['confirm'] if '--split' in sys.argv and sys.argv[sys.argv.index('--split') + 1] == 'confirm' else ['train', 'dev']
    if 'confirm' in splits:
        assert lock_ok(), 'confirm encodings only after protocol lock'
    t0 = time.time(); eng = engine(); C = core(); done = {}
    for d in S.DOMAINS:
        ws_all = rows(ROOT / f'data/{d}/worlds.jsonl')
        for split in splits:
            ws = [w for w in ws_all if w['split'] == split]; ids = [w['world_id'] for w in ws]
            for t in (0, 3):
                if split == 'confirm' and t == 3:
                    continue
                pooled = []
                for s in S.states(d):
                    hs = []; ms = []
                    for i in range(0, len(ws), 32):
                        h, m = eng.encode([S.render(w, s, t) for w in ws[i:i + 32]]); hs.append(h.cpu()); ms.append(m.cpu())
                    h = torch.cat(hs); m = torch.cat(ms); n = int(m.sum(1).max()); h, m = h[:, :n].contiguous(), m[:, :n].contiguous()
                    pooled.append(C.pool(h, m))
                    if t == 0:
                        save(f'local/e1_{d}_{split}_t{t}_s{s}.pt', dict(h=h, m=m, world_ids=ids))
                save(f'local/e1_pooled_{d}_{split}_t{t}.pt', dict(pooled=torch.stack(pooled, 1), world_ids=ids, states=S.states(d)))
                done[f'{d}_{split}_t{t}'] = len(ws); print('encoded', d, split, t, flush=True)
    tag = 'confirm' if 'confirm' in splits else 'train_dev'
    dump(f'results/e1_encode_{tag}_complete.json', dict(done=done, resources=eng.resources(), seconds=time.time() - t0,
         files={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted((ROOT / 'local').glob('e1_*.pt'))
                if ('confirm' in p.name) == (tag == 'confirm')}))


if __name__ == '__main__':
    main()
