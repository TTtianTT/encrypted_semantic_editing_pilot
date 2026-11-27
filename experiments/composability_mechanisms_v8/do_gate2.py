"""DO second-family selection (GPU, before the lock; DEVIATIONS 5): in candidate order, among the models that passed the token check
(results/do_tokens2.json), the reconstruction screen on dev (greedy repeat of the clean prompts, every state): weekday and month template 0
and month-nat. The first model with >= 0.99 on both template-0 domains is chosen (month-nat is evaluated only if it also passes, as for
Gemma); the full train + dev gate is then do_prep.py's. Output: results/do_gate2.json (data/model_manifest_v9.json gets DO2_final)."""
from do_prep import *

ORDER = [('olmo', 'allenai/OLMo-2-0425-1B-Instruct'), ('phi', 'microsoft/Phi-3.5-mini-instruct'), ('smol', 'HuggingFaceTB/SmolLM2-1.7B-Instruct'),
         ('mistral', 'mistralai/Mistral-7B-Instruct-v0.3')]


def main():
    require_slurm(); tk = read(ROOT / 'results/do_tokens2.json')['tokens']; res = {}; chosen = None
    for key, rid in ORDER:
        if not (tk.get(rid) or {}).get('passes'): res[key] = dict(skipped='token check'); continue
        eng = DEngine(model=key); r = {}
        for d in ('weekday', 'month', S.NAT):
            ws = [w for w in worlds5(d, 'dev') if slot_position(eng, w, d) is not None]; ok = []
            for s in S.states(d):
                for lo in range(0, len(ws), 64): ok += [success(o, w, s, d) for o, w in zip(eng.generate([ren(w, s) for w in ws[lo:lo + 64]]), ws[lo:lo + 64])]
            r[d] = rate(ok); print('gate2', key, d, r[d]['rate'], flush=True)
        res[key] = r; del eng; torch.cuda.empty_cache()
        if r['weekday']['rate'] >= .99 and r['month']['rate'] >= .99: chosen = key; break
    dump(ROOT / 'results/do_gate2.json', dict(screen=res, chosen=chosen, rule='first candidate with dev reconstruction >= 0.99 on weekday and month template 0'))
    man = read(ROOT / 'data/model_manifest_v9.json'); man['DO2_final'] = dict(ORDER).get(chosen); dump(ROOT / 'data/model_manifest_v9.json', man); print('chosen', chosen, flush=True)


if __name__ == '__main__':
    main()
