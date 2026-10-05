import contextlib
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WT = ROOT.parent.parent
ORIGINAL = Path('/dataset1/zailong/workspace/encrypted_semantic_editing_pilot')
SOURCE = ORIGINAL / '.four-domain-worktree/experiments/four_domain_state_coverage_v1'
CURRENT = ORIGINAL / '.current-source-worktree/experiments/current_source_compatibility_v1'
CAUSAL = ORIGINAL / '.causal-next-edit-worktree/experiments/causal_next_edit_stability_v1'
DELIVERY = ORIGINAL / '.state-handoff-worktree'
PUBLIC = DELIVERY / 'experiments/state_handoff_diagnosis_v1'
LOCAL = PUBLIC / 'local'
PYTHON = ORIGINAL / '.venv/bin/python'
BRANCH = 'experiment/state-handoff-diagnosis-v1'
BASE_SHA = '2f4713f259b980c47b9e9dfeb4d54f183d749c77'
CURRENT_SHA = 'aea8310b2f1a239cdbf690a11cbdf646b19a2a4f'
SEMANTIC_VERSION = 'handoff-v1-raw-text-frozen-20261005'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def objsha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def rows(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def atomic(p, data):
    p = Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    fd,t = tempfile.mkstemp(dir=p.parent,prefix='.'+p.name)
    try:
        with os.fdopen(fd,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(t,p)
    finally:
        if os.path.exists(t): os.unlink(t)
def text(p,s): atomic(p,s.encode())
def dump(p,x): text(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x): text(p,''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))
def cmd(args,cwd=None): return subprocess.check_output(list(map(str,args)),cwd=cwd,text=True).strip()
@contextlib.contextmanager
def lock(name='resource'):
    p=ORIGINAL / ('.state-handoff-'+name+'.lock')
    with p.open('a') as f: fcntl.flock(f,fcntl.LOCK_EX); yield
def cells():
    import sys
    sys.path.insert(0,str(SOURCE))
    from semantics import advance,states
    result=[]
    for s in states('time'):
        for a in ('plus','minus'):
            try: s1=advance('time',s,a)
            except ValueError: continue
            for b in ('plus','minus'):
                try: s2=advance('time',s1,b)
                except ValueError: continue
                result.append(dict(initial_state=s,a=a,b=b,state1=s1,state2=s2))
    assert len(result)==22
    return result
