import sys,json,hashlib,csv,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
V3=ROOT.parent/'reference_frame_pilot_v3'
G10=ROOT.parent/'g10_matched_editor_composability_v1'
G11=ROOT.parent/'g11_semantic_history_v1'
sys.path.insert(0,str(V3))
from common import frame,render,score,valid,eligible,FIELDS
CFG=json.loads((ROOT/'config.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 return [json.loads(x) for x in p.read_text().splitlines() if x]
def dump(p,x):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def write(p,x):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x));q.replace(p)
def csvwrite(p,rs):
 if not rs:return
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rs for k in r)),lineterminator='\n');w.writeheader();w.writerows(rs)
def key(w):return json.dumps({k:w[k] for k in FIELDS},sort_keys=True)
def original(s):return G10/f'checkpoints/rank16/rank16_seed{s}.pt'
def checkpoint(method,s):return original(s) if method=='Original' else ROOT/f'checkpoints/{method}_seed{s}.pt'
def statehash(state):
 h=hashlib.sha256()
 for k,v in sorted(state.items()):h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
 return h.hexdigest()
def load_editor(s,method='Original',train=False):
 import torch
 from torch import nn
 class LowRank(nn.Module):
  def __init__(self):
   super().__init__();self.b=nn.Parameter(torch.zeros(768));self.v=nn.Linear(768,16,bias=False);self.u=nn.Linear(16,768,bias=False)
  def forward(self,h,m):return h+(self.b+self.u(self.v(h)))*m[...,None].to(h.dtype)
 ed=LowRank().cuda().eval();ed.load_state_dict(torch.load(checkpoint(method,s),map_location='cuda',weights_only=True))
 for p in ed.parameters():p.requires_grad_(train)
 return ed
def load_gpu():
 from engine import Engine
 assert os.environ.get('SLURM_JOB_ID')
 e=Engine();e.limit=CFG['software_limit_seconds']
 for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']:assert e.kw[k]==CFG[k]
 return e
def lock():
 l=json.loads((ROOT/'data/lock.json').read_text())
 assert all(digest(REPO/p)==h for p,h in l['files'].items())
 return l
def decode(e,h,m,ws,offset):
 outs,ends,ns,t=e.decode(h,m)
 return [dict(output=x,normal_end=bool(z),generated_tokens=n,frame=frame(w,offset),target_text=render(w,frame(w,offset)),exact=x.strip()==render(w,frame(w,offset)),score=score(x,frame(w,offset),w,z),decode_seconds=t/len(ws)) for x,z,n,w in zip(outs,ends,ns,ws)]
