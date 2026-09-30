import sys,json,hashlib,csv,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
V3=ROOT.parent/'reference_frame_pilot_v3'
V2=ROOT.parent/'reference_frame_pilot_v2'
G10=ROOT.parent/'g10_matched_editor_composability_v1'
sys.path.insert(0,str(V3))
from common import frame,advance,render,score,valid,eligible,FIELDS
CFG=json.loads((ROOT/'config.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 return [json.loads(x) for x in p.read_text().splitlines() if x]
def dump(p,x):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');q.replace(p)
def write(p,rs):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs));q.replace(p)
def csvwrite(p,rows):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def key(w):return json.dumps({k:w[k] for k in FIELDS},sort_keys=True)
def checkpoint(seed):return G10/f'checkpoints/rank16/rank16_seed{seed}.pt'
def depfiles():
 return [V3/'engine.py',V3/'common.py',V3/'semantics_v1.py',V3/'renderer_v1.py',V3/'config.json',V3/'source_model_manifest.json',V2/'prepare.py',G10/'train.py',G10/'PROTOCOL.md']+[checkpoint(s) for s in CFG['seeds']]
def load_gpu():
 import torch,os
 from engine import Engine
 assert os.environ.get('SLURM_JOB_ID')
 engine=Engine();engine.limit=CFG['software_limit_seconds']
 assert all(not p.requires_grad and p.grad is None for p in engine.model.parameters())
 for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']:assert engine.kw[k]==CFG[k]
 return engine
def editor(seed):
 import torch
 from torch import nn
 class LowRank(nn.Module):
  def __init__(self):
   super().__init__();self.b=nn.Parameter(torch.zeros(768));self.v=nn.Linear(768,16,bias=False);self.u=nn.Linear(16,768,bias=False)
  def forward(self,h,m):
   z=h.float();return (z+(self.b+self.u(self.v(z)))*m[...,None]).to(h.dtype)
 ed=LowRank().cuda().eval();ed.load_state_dict(torch.load(checkpoint(seed),map_location='cuda',weights_only=True))
 for p in ed.parameters():p.requires_grad_(False)
 return ed
def tensorhash(t):return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
def decode(engine,h,m,worlds,frames,golds):
 texts,ended,lens,seconds=engine.decode(h,m)
 return [dict(output=t,normal_end=bool(e),generated_tokens=n,exact=t.strip()==gold,score=score(t,c,w,e),target_text=gold,frame=c,decode_seconds=seconds/len(texts)) for t,e,n,c,w,gold in zip(texts,ended,lens,frames,worlds,golds)]
def ensure_lock():
 lock=json.loads((ROOT/'data/manifest.json').read_text())
 assert all(digest(REPO/p)==h for p,h in lock['dependencies'].items())
 assert digest(ROOT/'config.json')==lock['config_sha256']
 assert digest(ROOT/'data/worlds.jsonl')==lock['worlds_sha256']
 return lock
