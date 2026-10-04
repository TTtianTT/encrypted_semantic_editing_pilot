import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WT = ROOT.parent.parent
ORIGINAL = WT.parent
SOURCE = ORIGINAL / '.four-domain-worktree/experiments/four_domain_state_coverage_v1'
RUN_ID = 'causal_next_edit_stability_v1'
ARTIFACT = ROOT / 'local'  # Existing shared artifact convention; excluded from Git.

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def objsha(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def read(path): return json.loads(Path(path).read_text())
def rows(path): return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def dump(path, x):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + f'.{os.getpid()}.tmp')
    t.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n'); t.replace(p)

def jsonl(path, xs):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + f'.{os.getpid()}.tmp')
    t.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in xs)); t.replace(p)

def code_hash():
    return objsha({str(p.relative_to(ROOT)): sha(p) for p in sorted(ROOT.rglob('*.py')) if 'local' not in p.parts})

def split(world_id):
    n = int(hashlib.sha256(('cesv1-world-split-20261004:' + world_id).encode()).hexdigest()[:8], 16) % 10
    return 'discovery' if n < 4 else 'validation' if n < 6 else 'test'
