"""G13 CPU utilities; the frozen historical grammar/scorer remain authoritative."""
import csv, hashlib, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V3 = ROOT.parent / 'reference_frame_pilot_v3'
G10 = ROOT.parent / 'g10_matched_editor_composability_v1'
G12 = ROOT.parent / 'g12_matched_input_source_v1'
sys.path.insert(0, str(V3))
from common import frame, render, score, valid, eligible, FIELDS, advance
CFG = json.loads((ROOT / 'configs/main.json').read_text())
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return [json.loads(l) for l in Path(p).read_text().splitlines() if l]
def dump(p, x):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix + '.tmp'); q.write_text(json.dumps(x, indent=2, ensure_ascii=False) + '\n'); q.replace(p)
def write(p, rows):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_suffix(p.suffix + '.tmp'); q.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)); q.replace(p)
def csvwrite(p, rows, fields=None):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n'); w.writeheader(); w.writerows(rows)
def key(w): return json.dumps({k: w[k] for k in FIELDS}, sort_keys=True)
def norm(t): return ' '.join(t.lower().split())
def original(s): return G10 / f'checkpoints/rank16/rank16_seed{s}.pt'
def statehash(state):
    h = hashlib.sha256()
    for k, v in sorted(state.items()):
        h.update(k.encode()); h.update(str(v.dtype).encode()); h.update(str(tuple(v.shape)).encode()); h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()
def atomic_specs(w):
    return [(d, p) for d in range(-3, 5) for p in ['first', 'third'] if eligible(w, ['T_plus'], d, p)]
def verify_lock():
    z = json.loads((ROOT / 'data/lock.json').read_text())
    for p, h in z['files'].items(): assert digest(REPO / p) == h, p
    return z
