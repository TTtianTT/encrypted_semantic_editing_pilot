"""Pre-lock gates (GPU; train + dev of the training templates only). --backbone bart|t5. PLAN B4.
GM (multi-template base operator): candidates in order S-RRR-16, S-RRR-32, E_all (appendix A.1, A.2; fitted on the train worlds of the
training templates, slot token only); the first with dev single-step success >= 0.95 (plus and minus pooled over every dev world and
state) and dev one-way plus R_2N >= 0.95 is the (backbone, domain)'s base operator; none -> the domain leaves M. Every candidate is
evaluated and reported; reference: v5's full-sequence RRR-16 (single step and R_2N). Planes: v5's (train slot vectors of the training
templates pooled; identical to A.2 step 1-2). GR: v5's GR (results/gates_mt_<bb>.json of v5; templates and backbones unchanged)."""
import time
from lib6 import *


def main():
    require_slurm(); bb = sys.argv[sys.argv.index('--backbone') + 1]; t0 = time.time(); eng = engine5(bb)
    res = dict(backbone=bb, GR_v5=read(V5DIR / f'results/gates_mt_{bb}.json')['GR'], GM={})
    for d in M_DOMAINS[bb]:
        N = len(S.states(d)); pos = slots(bb, d, 'dev'); P = planes(bb, d)
        fits, info = fit_srrr(bb, d, (16, 32)); save(f'local/{bb}_srrr_{d}.pt', fits)
        ea, B = fit_eall(bb, d); save(f'local/{bb}_eall_{d}.pt', dict(fits=ea, B=B))
        cand = {'SRRR16': {op: SlotRRRop(fits[op, 16], pos) for op in ('plus', 'minus')}, 'SRRR32': {op: SlotRRRop(fits[op, 32], pos) for op in ('plus', 'minus')},
                'Eall': {op: PlaneEd(ea[op][0], ea[op][1], B, pos) for op in ('plus', 'minus')}, 'RRR16full_ref': full_rrr16_ops(bb, d)}
        r = {}
        for name, ops in cand.items():
            single = dev_single(eng, bb, d, 'natural', ops); chain = dev_chain(eng, bb, d, 'natural', ops, ['plus'] * (2 * N))
            r[name] = dict(single=single, plus=dict(R1=chain[0], R_N=chain[N - 1], R_2N=chain[-1]),
                           passes=single['rate'] >= .95 and chain[-1]['rate'] >= .95)
            print('GM', bb, d, name, round(single['rate'], 4), round(chain[-1]['rate'], 4), flush=True)
        base = next((n for n in ('SRRR16', 'SRRR32', 'Eall') if r[n]['passes']), None)
        res['GM'][d] = dict(candidates=r, base=base, ridge=info, planes=[dict(k=k, dim=b.shape[1]) for k, b in P],
                            srrr_sha256=sha(ROOT / f'local/{bb}_srrr_{d}.pt'), eall_sha256=sha(ROOT / f'local/{bb}_eall_{d}.pt'),
                            planes_sha256=sha(V5DIR / f'local/planes_{bb}_{d}.pt'))
    res['M_domains'] = [d for d in M_DOMAINS[bb] if res['GM'][d]['base']]
    res['resources'] = eng.resources(); res['seconds'] = time.time() - t0; dump(f'results/gates_{bb}.json', res)


if __name__ == '__main__':
    main()
