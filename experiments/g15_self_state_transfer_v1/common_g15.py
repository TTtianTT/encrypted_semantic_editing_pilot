"""CPU provenance utilities and unchanged historical reference-frame semantics."""
import collections, csv, gzip, hashlib, importlib.util, json, os, random, sys
from pathlib import Path
from datetime import date
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
G13 = ROOT.parent / 'g13_source_overfit_audit_v1'
G14 = ROOT.parent / 'g14_matched_state_handoff_v1'
V3 = ROOT.parent / 'reference_frame_pilot_v3'
sys.path.insert(0, str(G13))
sys.path.insert(0, str(V3))
from common import FIELDS, advance, eligible, frame, render, score, valid
CFG = json.loads((ROOT / 'configs/main.json').read_text())

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n'); temp.replace(path)
def read(path):
    with (gzip.open(path, 'rt', encoding='utf-8') if str(path).endswith('.gz') else Path(path).open()) as f:
        return [json.loads(line) for line in f if line.strip()]
def write(path, rows):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    with (gzip.open(temp, 'wt', encoding='utf-8') if str(path).endswith('.gz') else temp.open('w')) as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False) + '\n')
    temp.replace(path)
def csvwrite(path, rows):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def key(w): return json.dumps({k: w[k] for k in FIELDS}, sort_keys=True)
def norm(t): return ' '.join(t.lower().split())
def sub_seed(name): return int.from_bytes(hashlib.sha256(f'{CFG["data_seed"]}/g15/{name}'.encode()).digest()[:8], 'big')
def atomic_specs(w): return [(d,p) for d in range(-3,5) for p in ['first','third'] if eligible(w,['T_plus'],d,p)]
def statehash(state):
    h = hashlib.sha256()
    for k,v in sorted(state.items()):
        h.update(k.encode()); h.update(str(v.dtype).encode()); h.update(str(tuple(v.shape)).encode())
        h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()
def verify_lock():
    z = json.loads((ROOT / 'data/lock.json').read_text())
    for p, sha in z['files'].items(): assert digest(REPO / p) == sha, p
    return z
def observation(text, ended, world, offset, perspective='first'):
    target = frame(world, offset, perspective); gold = render(world,target)
    sc = score(text,target,world,ended); parsed = sc['parsed']; exact = text == gold
    if sc['parse_unresolved']: error = 'parse_unresolved'
    elif sc['parsed_date_error'] and sc['parsed_nondate_error']: error = 'date_and_fact_error'
    elif sc['parsed_date_error']: error = 'date_error'
    elif sc['parsed_nondate_error']: error = 'fact_error'
    elif not sc['perspective_ok']: error = 'perspective_error'
    elif not sc['normal_end']: error = 'length_limit'
    else: error = 'success' if exact else 'format_only'
    rel = (date.fromisoformat(parsed['event_date'])-date.fromisoformat(target['view_date'])).days if parsed is not None else None
    return dict(output=text,gold=gold,joint=sc['joint_ok'],exact=exact,normal_end=bool(ended),score=sc,parsed_facts=parsed,error_type=error,predicted_relative_date=rel,relative_date_delta_days=rel-offset if rel is not None else None)
def gate_current(observations, masks_equal):
    failures=[]
    for name,o in observations.items():
        if not o['exact']: failures.append(name+'_not_exact')
        if not o['normal_end']: failures.append(name+'_not_normal_end')
        if not o['joint']: failures.append(name+'_'+o['error_type'])
    if not masks_equal: failures.append('producer_masks_differ')
    return dict(matched=not failures,failures=failures)
def full_success(first, second): return bool(first['joint'] and second['joint'])
