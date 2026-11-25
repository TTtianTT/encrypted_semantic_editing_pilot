"""N data gate (GPU, before the lock; PLAN v7 C2, appendix B.1 step 7). Candidates: local/natural_candidates.jsonl (prep_natural.py,
steps 1-6 and 8). A sentence is kept iff the original and all 12 month variants are reconstructed exactly (whitespace-normalised, output
ended) by both BART-base and T5Gemma 2B-2B (encode, then greedy decode, no edit). Pools are visited in a seeded order (rng 3101 + pool
index) until the targets are met: train 600, dev 120, confirm8 240 (if confirm8 has fewer than 160, all passing sentences are kept and
reported). Decoding the clean sentences of the confirm8 pool is part of the plan's selection gate (B.1 step 7); no edit is applied.
Output: data/month-nat/worlds.jsonl, data/month-nat/renders.jsonl, results/n_gate.json."""
import random
from collections import Counter
import time
from lib8 import *

TARGET = {'train': 600, 'dev': 120, 'confirm8': 240}
MONTHS = [S.word('month', s) for s in S.states('month')]


@torch.no_grad()
def passes(eng, texts):
    out = []
    for i in range(0, len(texts), 96):
        ts = texts[i:i + 96]; h, m = eng.encode(ts); dec = eng.decode(h, m)
        out += [o['ended'] and Ev.ws_norm(o['text']) == Ev.ws_norm(t) for o, t in zip(dec, ts)]
    return out


def main():
    require_slurm(); t0 = time.time(); engs = {bb: engine8(bb) for bb in ('bart', 't5')}
    cands = [json.loads(l) for l in (ROOT / 'local/natural_candidates.jsonl').read_text().split('\n') if l.strip()]
    worlds = []; stats = {}
    for pi, pool in enumerate(('train', 'dev', 'confirm8')):
        cs = [c for c in cands if c['pool'] == pool]; random.Random(3101 + pi).shuffle(cs); kept = []; tried = 0; fails = Counter()
        for i in range(0, len(cs), 16):
            if len(kept) >= TARGET[pool]: break
            batch = cs[i:i + 16]; tried += len(batch)
            ws = [dict(prefix=c['text'][:c['char']], suffix=c['text'][c['char'] + len(c['month']):], start_state=MONTHS.index(c['month'])) for c in batch]
            texts = [w['prefix'] + mo + w['suffix'] for w in ws for mo in MONTHS]
            ok = {bb: passes(e, texts) for bb, e in engs.items()}
            for j, (c, w) in enumerate(zip(batch, ws)):
                good = {bb: all(ok[bb][12 * j:12 * j + 12]) for bb in engs}
                if all(good.values()) and len(kept) < TARGET[pool]:
                    kept.append(dict(domain='month-nat', split=pool, prefix=w['prefix'], suffix=w['suffix'], start_state=w['start_state'], form=c['form'],
                                     article=c['article'], title=c['title'], source_text=c['text']))
                else: fails.update(bb for bb, g in good.items() if not g)
            print('N gate', pool, tried, len(kept), dict(fails), flush=True)
        for k, w in enumerate(kept): w['world_id'] = f"month-nat_{ {'train': 'tr', 'dev': 'dv', 'confirm8': 'c8'}[pool] }_{k:04d}".replace(' ', '')
        worlds += kept; stats[pool] = dict(candidates=len(cs), tried=tried, kept=len(kept), failures=dict(fails), pass_rate=len(kept) / max(tried, 1))
    write('data/month-nat/worlds.jsonl', worlds)
    write('data/month-nat/renders.jsonl', [dict(world_id=w['world_id'], split=w['split'], state=s, text=S.render(w, s)) for w in worlds for s in S.states('month')])
    dump(ROOT / 'results/n_gate.json', dict(target=TARGET, pools=stats, resources={bb: e.resources() for bb, e in engs.items()}, seconds=time.time() - t0))


if __name__ == '__main__':
    main()
