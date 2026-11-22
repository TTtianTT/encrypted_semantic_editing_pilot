"""P0 GPU smoke: encode/decode 8 canonical time texts; apply RRR-16 plus to the +1 samples."""
import time
import torch
from symutil import *


def main():
    require_slurm(); verify_inputs(['four_domain/', 'canonical_write_reachability_v1/local/rrr.pt', 'model/'])
    t0 = time.time(); S, Ev = semantics(); eng = engine()
    ws = [w for w in worlds('time') if w['split'] == 'test'][:8]
    st = [-3, -2, -1, 0, 1, 2, 3, 1]
    h, m = eng.encode([S.render(w, s, 0) for w, s in zip(ws, st)])
    out = eng.decode(h, m)
    recon = [dict(world_id=w['world_id'], state=s, text=o['text'], score=Ev.score(o['text'], S.gold(w, s, 0), w, o['ended']))
             for w, s, o in zip(ws, st, out)]
    fit = {k: v.cuda() for k, v in load(CWR / 'local/rrr.pt')['iid_only', 'plus', 16].items() if torch.is_tensor(v)}
    ix = [i for i, s in enumerate(st) if s == 1]
    hp = h[ix] + (h[ix].float() @ fit['left'] @ fit['right'] + fit['bias']) * m[ix][..., None]
    tgt = S.advance('time', 1, 'plus'); assert tgt == 0
    out2 = eng.decode(hp, m[ix])
    edit = [dict(world_id=ws[i]['world_id'], source=1, target=tgt, text=o['text'],
                 score=Ev.score(o['text'], S.gold(ws[i], tgt, 0), ws[i], o['ended'])) for i, o in zip(ix, out2)]
    res = dict(reconstruction=recon, rrr16_plus=edit,
               reconstruction_all_success=all(r['score']['success'] for r in recon),
               rrr16_plus_all_success=all(r['score']['success'] for r in edit),
               resources=eng.resources(), seconds=time.time() - t0)
    dump('results/p0_smoke.json', res)
    print(json.dumps({k: v for k, v in res.items() if 'success' in k}), flush=True)
    assert res['reconstruction_all_success'] and res['rrr16_plus_all_success']


if __name__ == '__main__':
    main()
