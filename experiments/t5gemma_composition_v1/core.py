"""Frozen local T5Gemma with one BART-G3-matched low-rank editor."""
import json,sys
from pathlib import Path
import torch
from torch import nn
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from transformers.modeling_outputs import BaseModelOutput

HERE=Path(__file__).resolve().parent;CFG=json.loads((HERE/'config.json').read_text())
V3=HERE.parent/'reference_frame_pilot_v3';sys.path.insert(0,str(V3))
from common import frame,advance,render,score,digest
PREFIX='Return exactly one copy of the text below, with no introduction, ending, or extra text.\n\n'

def readjsonl(p):return [json.loads(s) for s in p.read_text().splitlines()]
def writejson(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def writejsonl(p,rows):p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def pooled(h,m):return (h.float()*m[...,None]).sum(1)/m.sum(1).clamp(min=1)[:,None]

class Editor(nn.Module):
 def __init__(self,hidden,rank):
  super().__init__();self.b=nn.Parameter(torch.zeros(hidden));self.v=nn.Linear(hidden,rank,bias=False);self.u=nn.Linear(rank,hidden,bias=False)
  nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,h,m):
  z=h.float();delta=self.b+self.u(self.v(z))
  return (z+delta*m[...,None]).to(h.dtype)

class Engine:
 def __init__(self):
  assert torch.cuda.is_available() and __import__('os').environ.get('SLURM_JOB_ID')
  torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
  self.root=Path(CFG['local_model']);self.tok=AutoTokenizer.from_pretrained(self.root,local_files_only=True)
  self.model=AutoModelForSeq2SeqLM.from_pretrained(self.root,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa').cuda().eval()
  for p in self.model.parameters():p.requires_grad_(False)
  self.hidden=self.model.config.encoder.hidden_size
  self.max_length=CFG['source_length']
  eos=self.model.generation_config.eos_token_id
  self.eos=set(eos if isinstance(eos,list) else [eos])
 def prompt(self,t):return self.tok.apply_chat_template([{'role':'user','content':PREFIX+t}],tokenize=False,add_generation_prompt=True)
 def batch(self,texts):
  prompts=[self.prompt(t) for t in texts]
  lengths=[len(self.tok(p)['input_ids']) for p in prompts]
  maxlen=max(self.max_length,max(lengths))
  x=self.tok(prompts,padding='max_length',max_length=maxlen,truncation=False,return_tensors='pt')
  assert int(x.attention_mask.sum(1).max())==max(lengths),'No silent source truncation'
  return x.to('cuda')
 @torch.no_grad()
 def encode(self,texts):
  x=self.batch(texts);return self.model.get_encoder()(**x).last_hidden_state,x.attention_mask
 @torch.no_grad()
 def decode(self,h,m):
  g=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,max_new_tokens=CFG['max_new_tokens'],do_sample=False,num_beams=1)
  outs=self.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False)
  ended=[any(int(t) in self.eos for t in row[1:]) for row in g]
  return outs,ended
 def ce(self,h,m,texts):
  y=self.tok(texts,padding=True,truncation=False,return_tensors='pt').input_ids.cuda();y[y==self.tok.pad_token_id]=-100
  out=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=y,use_cache=False)
  return out.loss,int((y!=-100).sum())
