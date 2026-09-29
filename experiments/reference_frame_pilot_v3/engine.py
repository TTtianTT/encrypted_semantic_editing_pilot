import os,time,json,hashlib
import torch
from torch import nn
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from transformers.modeling_outputs import BaseModelOutput
from common import *
class Editor(nn.Module):
 def __init__(self):
  super().__init__();self.b=nn.Parameter(torch.zeros(768));self.v=nn.Linear(768,16,bias=False);self.u=nn.Linear(16,768,bias=False)
  nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,h,mask):return h+(self.b+self.u(self.v(h)))*mask.unsqueeze(-1).to(h.dtype)
def tensorhash(state):
 h=hashlib.sha256()
 for k,v in sorted(state.items()):h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
 return h.hexdigest()
def new_editors():
 torch.manual_seed(42);return nn.ModuleDict({op:Editor() for op in OPS}).cuda().eval()
class Engine:
 def __init__(self):
  assert os.environ.get('SLURM_JOB_ID') and torch.cuda.is_available(),'Slurm GPU required'
  self.start=time.monotonic();self.limit=float(os.environ.get('RF_WALL_SECONDS','840'));self.cfg=json.loads((ROOT/'config.json').read_text())
  for p in json.loads((ROOT/'source_model_manifest.json').read_text())['actual_files']:assert digest(p['file'])==p['sha256']
  torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  self.tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
  self.model=AutoModelForSeq2SeqLM.from_pretrained(REPO/'models/bart-base',local_files_only=True,attn_implementation='sdpa').cuda().float().eval()
  for p in self.model.parameters():p.requires_grad_(False);p.grad=None
  self.kw={k:self.cfg[k] for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']}
  self.model_hash=digest(REPO/'models/bart-base/model.safetensors')
 def check(self,reserve=60):
  if time.monotonic()-self.start>self.limit-reserve:raise TimeoutError('Allocation budget stop; outputs/checkpoint preserved')
 def batch(self,texts):
  lens=[len(self.tok(t)['input_ids']) for t in texts];assert max(lens)<=96,'No silent truncation'
  return self.tok(texts,padding='max_length',max_length=96,truncation=False,return_tensors='pt').to('cuda')
 @torch.no_grad()
 def encode(self,texts):
  start=time.perf_counter();x=self.batch(texts);torch.cuda.synchronize();h=self.model.get_encoder()(**x).last_hidden_state;torch.cuda.synchronize();return h,x.attention_mask,time.perf_counter()-start
 @torch.no_grad()
 def decode(self,h,mask):
  torch.cuda.synchronize();t=time.perf_counter();g=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,**self.kw);torch.cuda.synchronize();elapsed=time.perf_counter()-t
  outs=self.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False);ended=[bool((x[1:]==self.tok.eos_token_id).any()) for x in g]
  return outs,ended,[int((x!=self.tok.pad_token_id).sum()) for x in g],elapsed
 @torch.no_grad()
 def infer(self,texts,eds=None,ops=(),mode='latent_chain'):
  self.check();start=time.perf_counter();h,mask,enc=self.encode(texts);bs=len(texts);steps=[];edit=dec=diagnostic=0.;current=texts;original_lengths=mask.sum(1).tolist()
  sequence=ops or ['identity']
  for k,op in enumerate(sequence):
   if k and mode=='decode_reencode':h,mask,t=self.encode(current);enc+=t
   torch.cuda.synchronize();a=time.perf_counter()
   if op!='identity':h=eds[op](h,mask)
   torch.cuda.synchronize();edit+=time.perf_counter()-a
   current,ended,lens,t=self.decode(h,mask)
   if mode=='latent_chain' and k<len(sequence)-1:diagnostic+=t
   else:dec+=t
   steps.append([{'output':s,'ended':e,'generated_tokens':n,'input_mask_length':int(ml),'output_reencoded_tokens':len(self.tok(s)['input_ids'])} for s,e,n,ml in zip(current,ended,lens,mask.sum(1).tolist())])
  timing={'encode':enc/bs,'edit':edit/bs,'decode':dec/bs,'diagnostic_decode':diagnostic/bs,'actual_path':(enc+edit+dec)/bs,'total_including_diagnostics':(time.perf_counter()-start)/bs,'batch_size':bs}
  return [[step[j] for step in steps] for j in range(bs)],timing,original_lengths
 def loss(self,eds,rows,replace=None):
  x=self.batch([r['source_text'] for r in rows]);h=self.model.get_encoder()(**x).last_hidden_state.detach();op=rows[0]['operations'][0];assert all(r['operations']==[op] for r in rows)
  h=eds[op](h,x.attention_mask)
  if replace and any(replace):
   assert op=='T_plus';ids=torch.where(torch.tensor(replace,device=h.device))[0];h2=eds[op](h[ids],x.attention_mask[ids]);h=h.index_copy(0,ids,h2)
  y=self.tok([r['target_text'] for r in rows],padding=True,truncation=False,return_tensors='pt').input_ids.cuda();y[y==self.tok.pad_token_id]=-100
  l=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=x.attention_mask,labels=y,use_cache=False).loss
  return l,int((y!=-100).sum()),int(x.attention_mask.sum())

 def stage_loss(self,eds,rows,replace,worlds,alpha=.5,beta=.5,return_parts=False):
  """Keep endpoint token weights; split each chain sample's CE across stages."""
  import torch.nn.functional as F
  x=self.batch([r['source_text'] for r in rows]);op=rows[0]['operations'][0]
  assert all(r['operations']==[op] for r in rows)
  with torch.no_grad():h0=self.model.get_encoder()(**x).last_hidden_state
  h1=eds[op](h0,x.attention_mask)
  def ce(h,mask,texts):
   y=self.tok(texts,padding=True,truncation=False,return_tensors='pt').input_ids.cuda();y[y==self.tok.pad_token_id]=-100
   logits=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,labels=y,use_cache=False).logits
   nt=(y!=-100).sum(1);loss=F.cross_entropy(logits.reshape(-1,logits.size(-1)),y.reshape(-1),ignore_index=-100,reduction='none').reshape(y.shape).sum(1)/nt
   return loss,nt
  texts1=[r['target_text'] for r in rows] # y1 never overwritten
  ell1,n1=ce(h1,x.attention_mask,texts1);weights=n1.clone();per=ell1
  ids=torch.where(torch.tensor(replace,device=h1.device))[0];n2=torch.zeros(0,device=h1.device,dtype=torch.long)
  if len(ids):
   assert op=='T_plus';texts2=[render(worlds[rows[i]['record_id']],advance(rows[i]['frames'][-1],op)) for i in ids.tolist()]
   h2=eds[op](h1[ids],x.attention_mask[ids]);ell2,n2=ce(h2,x.attention_mask[ids],texts2)
   weights=weights.index_copy(0,ids,n2);per=ell1.index_copy(0,ids,alpha*ell1[ids]+beta*ell2)
  total=(weights*per).sum()/weights.sum()
  stats=dict(endpoint_weight_tokens=int(weights.sum()),supervision_tokens=int(n1.sum()+n2.sum()),input_tokens=int(x.attention_mask.sum()),decoder_batch_calls=1+int(len(ids)>0),decoder_sample_calls=len(rows)+len(ids),operator_sample_calls=len(rows)+len(ids))
  if return_parts:
   assert len(ids)
   return total,stats,(weights[ids]*ell1[ids]).sum()/weights.sum(),(weights[ids]*ell2).sum()/weights.sum()
  return total,stats
