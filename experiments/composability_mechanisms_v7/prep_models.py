"""v8 preparation (CPU, network; PLAN v7 C1 'model download during v7'). Downloads the models of units G, D and the scale ladder at a fixed
revision (the current head commit, recorded) into /dataset1/zailong/models/<name>, and records the revision and the SHA256 of every file in
local/model_manifest_v8.json. UL2-IT is preferred for T5Gemma; if a size has no UL2-IT repository, the PrefixLM-IT one of the same size is
used and recorded (PLAN C3)."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

assert os.environ.get('SLURM_JOB_ID'), 'run via sbatch'
OUT = Path('/dataset1/zailong/models'); HERE = Path(__file__).resolve().parent
WANT = [('G', ['google/t5gemma-9b-9b-ul2-it', 'google/t5gemma-9b-9b-prefixlm-it']), ('ladder-B', ['google/t5gemma-b-b-ul2-it', 'google/t5gemma-b-b-prefixlm-it']),
        ('ladder-L', ['google/t5gemma-l-l-ul2-it', 'google/t5gemma-l-l-prefixlm-it']), ('D', ['google/gemma-2-2b-it'])]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    return h.hexdigest()


def main():
    api = HfApi(); man = {}
    for unit, cands in WANT:
        for rid in cands:
            try: info = api.model_info(rid)
            except Exception as e: print('missing', rid, type(e).__name__, flush=True); continue
            t0 = time.time(); d = OUT / rid.split('/')[1]
            snapshot_download(rid, revision=info.sha, local_dir=d, allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', 'tokenizer*'])
            files = {str(p.relative_to(d)): dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(d.rglob('*')) if p.is_file() and '.cache' not in p.parts}
            man[unit] = dict(model_id=rid, revision=info.sha, directory=str(d), fallback=rid != cands[0], files=files, seconds=time.time() - t0)
            print('downloaded', unit, rid, info.sha, f'{sum(v["bytes"] for v in files.values()) / 1e9:.1f} GB', flush=True); break
        else: man[unit] = dict(missing=cands)
    (HERE / 'local/model_manifest_v8.json').write_text(json.dumps(man, indent=1))


if __name__ == '__main__':
    main()
