import time,torch
from torch import nn
from task import *
from backend import Backend,new_editors,tensorhash
class Joint(nn.Module):
 def __init__(self,d,rank):
  super().__init__();self.b=nn.Parameter(torch.zeros(d));self.v=nn.Linear(d,rank,bias=False);self.u=nn.Linear(rank,d,bias=False);nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,h,mask):return h+(self.b+self.u(self.v(h)))*mask.unsqueeze(-1).to(h.dtype)
def new_joint(d,rank):
 torch.manual_seed(42);return Joint(d,rank).cuda().float().eval()
def old_editors(be):
 ed=new_editors(be.d);ed.load_state_dict(torch.load(CROSS/f'checkpoints/{NAME}/G1/best.pt',weights_only=True));return ed
@torch.no_grad()
def fold(a,b,d):
 c=new_joint(d,32);c.v.weight.copy_(torch.cat([a.v.weight,b.v.weight],0));c.u.weight.copy_(torch.cat([a.u.weight+b.u.weight@b.v.weight@a.u.weight,b.u.weight],1));c.b.copy_(a.b+b.u(b.v(a.b))+b.b);return c
def devloss(be,ed,rows):
 total=n=0
 with torch.no_grad():
  for i in range(0,len(rows),4):
   rr=rows[i:i+4];h,m,_=be.encode([r['source_text'] for r in rr]);ell,nt=be.token_ce(ed(h,m),m,[r['target_text'] for r in rr]);total+=float((ell*nt).sum());n+=int(nt.sum())
 return total/n
