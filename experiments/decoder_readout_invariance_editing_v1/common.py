import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WT = ROOT.parent.parent
PROJECT = Path('/dataset1/zailong/workspace/encrypted_semantic_editing_pilot')
CONTROL = PROJECT / '.decoder-readout-control-v1'
TASK_TMP = CONTROL / 'tmp'
TASK_TMP.mkdir(parents=True, exist_ok=True)
# The execution request requires every task-created temporary file under /dataset1/zailong.
os.environ['TMPDIR'] = str(TASK_TMP)
tempfile.tempdir = str(TASK_TMP)
for key, folder in {'MPLCONFIGDIR':'matplotlib','PIP_CACHE_DIR':'pip',
                    'TORCHINDUCTOR_CACHE_DIR':'torchinductor','TRITON_CACHE_DIR':'triton'}.items():
    os.environ[key] = str(CONTROL / 'cache' / folder)
PYTHON = PROJECT / '.venv/bin/python'
BRANCH = 'experiment/decoder-readout-invariance-editing-v1'

def command(*args, cwd=WT):
    return subprocess.check_output(list(map(str,args)),cwd=cwd,text=True).strip()

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def objsha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def read(p):return json.loads(Path(p).read_text())
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]

def atomic(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.'+p.name)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:Path(tmp).unlink(missing_ok=True)

def dump(p,x):atomic(p,(json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def jsonl(p,x):atomic(p,''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x).encode())
def text(p,x):atomic(p,x.encode())
def core(w):return (w['object'],w['color'],int(w['quantity']),w['status'])

def world_dicts(x):
    if isinstance(x,dict):
        if x.get('domain')=='time' and all(k in x for k in ('object','color','quantity','status')):
            yield x
        for v in x.values():yield from world_dicts(v)
    elif isinstance(x,list):
        for v in x:yield from world_dicts(v)
