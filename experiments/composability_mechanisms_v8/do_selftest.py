"""PLAN v9 appendix A.6 item 5 (GPU, before the lock): the decoder-only interface - replacing the slot latent after the layer by the same
vector leaves the output identical to no edit (every domain of the model, 48 dev prompts per state-0 and state-1 render). --model gemma|qwen.
Output: results/do_selftest_<model>.json."""
from do_prep import *


def main():
    require_slurm(); model = sys.argv[sys.argv.index('--model') + 1]; prep = read(ROOT / f'results/do_prep_{model}.json'); layer = prep['layer']; eng = DEngine(model=model); res = {}
    for d, r in prep['domains'].items():
        if r.get('skipped'): continue
        L = load(ROOT / f'local/do_{model}_{d}_dev.pt'); wmap = {w['world_id']: w for w in worlds5(d, 'dev')}; ws = [wmap[i] for i in L['world_ids']][:48]; pos = L['pos'][:48]; same = []
        for s in S.states(d)[:2]:
            texts = [ren(w, s) for w in ws]; a = eng.generate(texts); b = eng.generate(texts, pos, layer, L['latents'][:48, s].float())
            same += [x['text'] == y['text'] and x['ended'] == y['ended'] for x, y in zip(a, b)]
        res[d] = dict(n=len(same), identical=float(np.mean(same)))
    res['pass_'] = all(v['identical'] == 1.0 for v in res.values() if isinstance(v, dict)); dump(ROOT / f'results/do_selftest_{model}.json', res); print(json.dumps(res), flush=True)


if __name__ == '__main__':
    main()
