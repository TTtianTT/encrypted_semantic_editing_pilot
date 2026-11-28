"""DO second-family replacement (CPU, network; DEVIATIONS 5): download the candidates in order at their current head revision and run the
token check of prep_do.py (state words single-token in the repeat prompt for every template-0 and month-nat world). The reconstruction
gate runs on GPU in do_gate2.py, in the same order. Output: data/model_manifest_v9.json (candidates added), results/do_tokens2.json."""
import os
import time
from prep_do import *

CANDS2 = ['allenai/OLMo-2-0425-1B-Instruct', 'microsoft/Phi-3.5-mini-instruct', 'HuggingFaceTB/SmolLM2-1.7B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.3']


def main():
    assert os.environ.get('SLURM_JOB_ID'), 'run via sbatch'; t0 = time.time(); W = worlds(); api = HfApi(); man = read(ROOT / 'data/model_manifest_v9.json'); res = {}
    for rid in CANDS2:
        try: info = api.model_info(rid)
        except Exception as e: res[rid] = dict(error=type(e).__name__); print('missing', rid, type(e).__name__, flush=True); continue
        d = OUT / rid.split('/')[1]
        try: snapshot_download(rid, revision=info.sha, local_dir=d, allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', 'tokenizer*', '*.jinja', '*.py'])
        except Exception as e: res[rid] = dict(error=f'download {type(e).__name__}'); print('download failed', rid, type(e).__name__, flush=True); continue
        try: r = check(AutoTokenizer.from_pretrained(str(d), local_files_only=True), W)
        except Exception as e: res[rid] = dict(error=f'tokenizer {type(e).__name__}: {e}'[:300]); print('tokenizer failed', rid, flush=True); continue
        ok = all(v['not_single_token'] == 0 for v in r.values()); res[rid] = dict(tokens=r, passes=ok); print(rid, info.sha, r, flush=True)
        files = {str(p.relative_to(d)): dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(d.rglob('*')) if p.is_file() and '.cache' not in p.parts}
        man[rid] = dict(model_id=rid, revision=info.sha, directory=str(d), passes_token_check=ok, files=files, candidate_order=CANDS2.index(rid))
    dump(ROOT / 'data/model_manifest_v9.json', man); dump(ROOT / 'results/do_tokens2.json', dict(tokens=res, seconds=time.time() - t0))


if __name__ == '__main__':
    main()
