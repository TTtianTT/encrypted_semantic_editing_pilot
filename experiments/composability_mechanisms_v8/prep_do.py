"""DO preparation (CPU, network; PLAN v9 section 5): download Qwen2.5-1.5B-Instruct at its current head revision (recorded) into
/dataset1/zailong/models; check that the month and weekday words are single tokens in the repeat prompt for every template-0 world
(train, dev, confirm7) and every month-nat world (train, dev, confirm8): the state variants of a world differ in exactly one token. If
Qwen is not downloadable or fails the check, Llama-3.2-1B-Instruct is tried and the switch recorded. Gemma 2 2B (v8) is checked on the
same data. Output: data/model_manifest_v9.json, results/do_tokens.json."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from huggingface_hub import HfApi, snapshot_download
from transformers import AutoTokenizer
from symutil import *
import sym5_semantics as S

OUT = Path('/dataset1/zailong/models'); CANDS = ['Qwen/Qwen2.5-1.5B-Instruct', 'meta-llama/Llama-3.2-1B-Instruct']
V1 = EXP / 'symmetry_composability_v1'; V7D = EXP / 'composability_mechanisms_v6'; V8D = EXP / 'composability_mechanisms_v7'


def worlds():
    out = {}
    for d in ('weekday', 'month'):
        out[d] = [w for w in rows(V1 / f'data/{d}/worlds.jsonl') if w['split'] in ('train', 'dev')] + [w for w in rows(V7D / f'data/{d}/worlds.jsonl') if w['split'] == 'confirm7']
    out[S.NAT] = list(rows(V8D / f'data/{S.NAT}/worlds.jsonl')); return out


def check(tok, W):
    ids = lambda t: tok(tok.apply_chat_template([dict(role='user', content=f'Repeat this sentence exactly: {t}')], tokenize=False, add_generation_prompt=True), add_special_tokens=False)['input_ids']
    res = {}
    for d, ws in W.items():
        bad = 0
        for w in ws:
            seqs = [ids(S.render(w, s, 0)) for s in S.states(d)]
            if len({len(x) for x in seqs}) != 1: bad += 1; continue
            diff = {i for x in seqs for i in range(len(x)) if x[i] != seqs[0][i]}
            bad += len(diff) != 1
        res[d] = dict(worlds=len(ws), not_single_token=bad)
    return res


def main():
    assert os.environ.get('SLURM_JOB_ID'), 'run via sbatch'; t0 = time.time(); W = worlds(); api = HfApi(); man = {}; tokres = {}
    tokres['gemma'] = check(AutoTokenizer.from_pretrained('/dataset1/zailong/models/gemma-2-2b-it', local_files_only=True), W)
    for rid in CANDS:
        try: info = api.model_info(rid)
        except Exception as e: tokres[rid] = dict(error=type(e).__name__); print('missing', rid, type(e).__name__, flush=True); continue
        d = OUT / rid.split('/')[1]
        try: snapshot_download(rid, revision=info.sha, local_dir=d, allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', 'tokenizer*', '*.jinja'])
        except Exception as e: tokres[rid] = dict(error=f'download {type(e).__name__}'); print('download failed', rid, flush=True); continue
        r = check(AutoTokenizer.from_pretrained(str(d), local_files_only=True), W); tokres[rid] = r
        ok = all(v['not_single_token'] == 0 for v in r.values()); print(rid, info.sha, r, flush=True)
        files = {str(p.relative_to(d)): dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(d.rglob('*')) if p.is_file() and '.cache' not in p.parts}
        man[rid] = dict(model_id=rid, revision=info.sha, directory=str(d), passes_token_check=ok, fallback=rid != CANDS[0], files=files)
        if ok: man['DO2'] = rid; break
    dump(ROOT / 'data/model_manifest_v9.json', man); dump(ROOT / 'results/do_tokens.json', dict(tokens=tokres, chosen=man.get('DO2'), seconds=time.time() - t0))
    print('chosen', man.get('DO2'), flush=True)


if __name__ == '__main__':
    main()
