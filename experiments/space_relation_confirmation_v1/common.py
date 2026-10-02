"""CPU utilities. GPU entrypoints are guarded separately."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parent.parent
ORIGINAL = WORKTREE.parent
PYTHON = ORIGINAL / '.venv/bin/python'
DOMAINS = ['space']
MODELS = ['bart', 't5gemma']

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)

def read(path):
    return json.loads(Path(path).read_text())

def jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    temporary.replace(path)

def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines()]
