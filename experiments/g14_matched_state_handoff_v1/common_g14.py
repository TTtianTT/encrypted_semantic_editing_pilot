"""CPU helpers and the unchanged G13 controlled reference-frame semantics."""
import csv, gzip, hashlib, importlib.util, json, os, sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parents[1]
G13=ROOT.parent/'g13_source_overfit_audit_v1'; V3=ROOT.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(G13))
sys.path.insert(0,str(V3))
from common import FIELDS, advance, eligible, frame, render, score, valid
CFG=json.loads((ROOT/'configs/main.json').read_text())
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()
def dump(p,x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); q=p.with_suffix(p.suffix+'.tmp'); q.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n'); q.replace(p)
def read(p):
    with (gzip.open(p,'rt',encoding='utf-8') if str(p).endswith('.gz') else Path(p).open()) as f:
        return [json.loads(l) for l in f if l.strip()]
def write(p,rows):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp')
    with q.open('w') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    q.replace(p)
def csvwrite(p,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r)); p=Path(p)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def key(w):return json.dumps({k:w[k] for k in FIELDS},sort_keys=True)
def norm(t):return ' '.join(t.lower().split())
def sub_seed(name):return int.from_bytes(hashlib.sha256(f'{CFG["data_seed"]}/{name}'.encode()).digest()[:8],'big')
def verify_lock():
    z=json.loads((ROOT/'data/lock.json').read_text())
    for p,h in z['files'].items():assert digest(REPO/p)==h,p
    return z
def statehash(state):
    h=hashlib.sha256()
    for k,v in sorted(state.items()):
        h.update(k.encode());h.update(str(v.dtype).encode());h.update(str(tuple(v.shape)).encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()
def error_type(sc,exact):
    if sc['parse_unresolved']:return 'parse_unresolved'
    if sc['parsed_date_error'] and sc['parsed_nondate_error']:return 'date_and_fact_error'
    if sc['parsed_date_error']:return 'date_error'
    if sc['parsed_nondate_error']:return 'fact_error'
    if not sc['perspective_ok']:return 'perspective_error'
    if not sc['normal_end']:return 'length_limit'
    return 'format_only' if sc['joint_ok'] and not exact else 'success'
def observe_text(text,ended,w,offset):
    c=frame(w,offset);gold=render(w,c);sc=score(text,c,w,ended);p=sc['parsed']
    rel=(date.fromisoformat(p['event_date'])-date.fromisoformat(c['view_date'])).days if p is not None else None
    return dict(output=text,gold=gold,exact=text==gold,joint=sc['joint_ok'],normal_end=bool(ended),score=sc,parsed_facts=p,error_type=error_type(sc,text==gold),predicted_relative_date=rel,gold_relative_date=offset,relative_date_delta_days=rel-offset if rel is not None else None)
def current_gate(g,r,mask_equal):
    # Deliberately accepts no second-step information.
    failures=[]
    for name,o in [('G',g),('R',r)]:
        if not o['exact']:failures.append(name+'_current_not_exact')
        if not o['normal_end']:failures.append(name+'_not_normal_end')
        if not o['joint']:failures.append(name+'_'+o['error_type'])
    if not mask_equal:failures.append('producer_mask_mismatch')
    return dict(matched=not failures,failures=failures)
