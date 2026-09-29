"""Explicit final-encoder-output adapter. No decoder-layer or inputs_embeds intervention."""
import os,time,inspect,math
import torch
from torch import nn
import torch.nn.functional as F
from transformers import AutoTokenizer,AutoConfig,AutoModelForSeq2SeqLM,T5Gemma2ForConditionalGeneration,T5GemmaForConditionalGeneration
from transformers.modeling_outputs import BaseModelOutput
from common import *
COPY='Copy the following text exactly. Output only the copied text.\n\n'
class Editor(nn.Module):
 def __init__(self,d):
  super().__init__();self.b=nn.Parameter(torch.zeros(d));self.v=nn.Linear(d,16,bias=False);self.u=nn.Linear(16,d,bias=False);nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,h,mask):return h+(self.b+self.u(self.v(h)))*mask.unsqueeze(-1).to(h.dtype)
def tensorhash(state):
 import hashlib
 h=hashlib.sha256()
 for k,v in sorted(state.items()):h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
 return h.hexdigest()
def new_editors(d):
 torch.manual_seed(42);return nn.ModuleDict({op:Editor(d) for op in OPS}).cuda().float().eval()
class Backend:
 def __init__(self,name,wrapper=None):
  assert os.environ.get('SLURM_JOB_ID') and torch.cuda.is_available(),'GPU use requires Slurm'
  self.name=name;self.started=time.monotonic();self.limit=float(os.environ.get('RF_WALL_SECONDS','840'));torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  self.manifest=json.loads((ROOT/f'models/{name}.json').read_text());self.directory=Path(self.manifest['directory']);self.tok=AutoTokenizer.from_pretrained(self.directory,local_files_only=True)
  self.chat=name=='t5gemma-2b-2b-ul2-it';assert not self.chat or self.tok.chat_template,'Official IT chat template required'
  c=AutoConfig.from_pretrained(self.directory,local_files_only=True);cls=T5Gemma2ForConditionalGeneration if c.model_type=='t5gemma2' else T5GemmaForConditionalGeneration if c.model_type=='t5gemma' else AutoModelForSeq2SeqLM
  attention='sdpa' if name=='BART' else 'eager';self.model=cls.from_pretrained(self.directory,local_files_only=True,dtype=torch.float32,attn_implementation=attention).cuda().float().eval()
  for p in self.model.parameters():p.requires_grad_(False);p.grad=None
  cfgfile=ROOT/f'models/{name}_interface.json'
  if cfgfile.exists():self.cfg=json.loads(cfgfile.read_text())
  else:
   texts=[]
   for f in ['train_G1.jsonl','dev_atomic.jsonl','calibration_views.jsonl']:
    for r in read('data/'+f):texts += [r['source_text'],r['target_text']]
   texts += [r['text'] for r in read('data/calibration_targets.jsonl')]
   maxlabel=max(map(len,self.label_ids(texts)));maxinput=max(len(self.tok(self.wrap(t,w),add_special_tokens=not self.chat)['input_ids']) for t in set(texts) for w in ['A','B'])
   self.cfg=dict(source_length=96 if name=='BART' else math.ceil(maxinput/8)*8,max_new_tokens=60 if name=='BART' else maxlabel+8,max_gold_tokens=maxlabel,dtype='float32',attention=attention,micro_batch=4,num_beams=1,do_sample=False,forced_eos_token_id=None,chat_template=self.tok.chat_template if self.chat else None,label_convention='BART/T5 tokenizer native specials; Gemma body without BOS plus EOS, model shifts decoder BOS',model_class=type(self.model).__name__,module_hash=digest(inspect.getfile(type(self.model))),revision=self.manifest['revision'],tokenizer_revision=self.manifest['revision'])
   dump(f'models/{name}_interface.json',self.cfg)
  self.wrapper=wrapper or ('A' if name=='BART' else json.loads((ROOT/f'calibration/{name}/admission.json').read_text())['selected_wrapper'])
  self.kw={k:self.cfg[k] for k in ['max_new_tokens','num_beams','do_sample','forced_eos_token_id']}
  if name!='BART':self.kw['cache_implementation']='dynamic'
  if c.model_type.startswith('t5gemma'):self.kw['decoder_start_token_id']=c.decoder.bos_token_id
  h,mask,_=self.encode([read('data/train_G1.jsonl')[0]['source_text']]);self.d=h.shape[-1];self.cfg.update(encoder_output_dimension=self.d,parameters_per_operator=33*self.d,total_editor_parameters=132*self.d,edit_site='encoder_outputs.last_hidden_state before decoder cross-attention projections',mask_policy='all nonpadding tokens including wrapper and special tokens')
  dump(f'models/{name}_interface.json',self.cfg)
 def check(self,reserve=60):
  if time.monotonic()-self.started>=self.limit-reserve:raise TimeoutError('budget reserve reached')
 def wrap(self,text,wrapper=None):
  body=(COPY if (wrapper or self.wrapper)=='B' else '')+text
  return self.tok.apply_chat_template([{'role':'user','content':body}],tokenize=False,add_generation_prompt=True) if self.chat else body
 def batch(self,texts):
  wrapped=[self.wrap(t) for t in texts];x=self.tok(wrapped,add_special_tokens=not self.chat,padding='max_length',max_length=self.cfg['source_length'],truncation=False,return_tensors='pt')
  assert x.input_ids.shape[1]<=self.cfg['source_length'],'input length exceeds frozen cap; no truncation permitted'
  return x.to('cuda')
 def label_ids(self,texts):
  if self.name.startswith('t5gemma'):return [self.tok(t,add_special_tokens=False)['input_ids']+[self.tok.eos_token_id] for t in texts]
  return self.tok(texts,truncation=False)['input_ids']
 def labels(self,texts):
  ids=self.label_ids(texts);y=torch.full((len(ids),max(map(len,ids))),-100,device='cuda',dtype=torch.long)
  for i,a in enumerate(ids):y[i,:len(a)]=torch.tensor(a,device='cuda')
  return y
 @torch.no_grad()
 def encode(self,texts):
  start=time.perf_counter();x=self.batch(texts);h=self.model.get_encoder()(**x).last_hidden_state;torch.cuda.synchronize();return h,x.attention_mask,time.perf_counter()-start
 def token_ce(self,h,mask,texts):
  y=self.labels(texts);out=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,labels=y,use_cache=False)
  n=(y!=-100).sum(1);ce=F.cross_entropy(out.logits.reshape(-1,out.logits.shape[-1]),y.reshape(-1),ignore_index=-100,reduction='none').reshape(y.shape).sum(1)/n
  return ce,n
 @torch.no_grad()
 def generate(self,h,mask):
  torch.cuda.synchronize();t=time.perf_counter();g=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,**self.kw);torch.cuda.synchronize();elapsed=time.perf_counter()-t
  eos=self.model.generation_config.eos_token_id;eos=eos if isinstance(eos,list) else [eos];texts=self.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False)
  result=[]
  for text,ids in zip(texts,g.tolist()):
   normal=any(i in eos for i in ids[1:]);result.append(dict(output=text,ended=normal,token_ids=ids,generated_tokens=sum(i!=self.tok.pad_token_id for i in ids),hit_limit=len(ids)-1>=self.cfg['max_new_tokens'] and not normal,special_token_ids=[i for i in ids if i in self.tok.all_special_ids]))
  return result,elapsed
 @torch.no_grad()
 def infer(self,texts,eds,ops,mode='latent_chain'):
  self.check();h,mask,enc=self.encode(texts);lens=mask.sum(1).tolist();results=[[] for _ in texts];active=list(range(len(texts)));edit=dec=diag=0.;sequence=ops or ['identity']
  for k,op in enumerate(sequence):
   if k and mode=='decode_reencode':
    keep=[]
    for j in active:
     text=results[j][-1]['output'];n=len(self.tok(self.wrap(text),add_special_tokens=not self.chat)['input_ids'])
     if n>self.cfg['source_length']:
      for _ in sequence[k:]:results[j].append(dict(output='',ended=False,token_ids=[],generated_tokens=0,hit_limit=False,special_token_ids=[],input_mask_length=n,execution_error='actual reencoded input exceeds frozen cap; not truncated; remaining stages not executed'))
     else:keep.append(j)
    active=keep
    if not active:break
    h,mask,t=self.encode([results[j][-1]['output'] for j in active]);enc+=t
   torch.cuda.synchronize();t=time.perf_counter()
   if op!='identity':h=eds[op](h,mask)
   torch.cuda.synchronize();edit+=time.perf_counter()-t;out,t=self.generate(h,mask)
   if mode=='latent_chain' and k<len(sequence)-1:diag+=t
   else:dec+=t
   for j,r,n in zip(active,out,mask.sum(1).tolist()):r['input_mask_length']=n;results[j].append(r)
  timing={k:v/len(texts) for k,v in dict(encode=enc,edit=edit,decode=dec,diagnostic_decode=diag,actual_path=enc+edit+dec).items()};timing['batch_size']=len(texts)
  return results,timing,lens
 def objective(self,eds,rows,flags,worlds,group,denominator=None):
  h0,mask,_=self.encode([r['source_text'] for r in rows]);op=rows[0]['operations'][0];h1=eds[op](h0,mask);ell1,n1=self.token_ce(h1,mask,[r['target_text'] for r in rows]);w=n1.clone();per=ell1;extra=0;ids=[i for i,f in enumerate(flags) if f and group=='G3']
  if ids:
   assert op=='T_plus';h2=eds[op](h1[ids],mask[ids]);texts2=[render(worlds[rows[i]['record_id']],advance(rows[i]['frames'][-1],op)) for i in ids];ell2,n2=self.token_ce(h2,mask[ids],texts2);idx=torch.tensor(ids,device='cuda');w=w.index_copy(0,idx,n2);per=ell1.index_copy(0,idx,.5*ell1[ids]+.5*ell2);extra=int(n2.sum())
  numerator=(w*per).sum();den=int(w.sum()) if denominator is None else denominator
  return numerator/den,dict(weight_tokens=int(w.sum()),supervision_tokens=int(n1.sum())+extra,operator_calls=len(rows)+len(ids),decoder_sample_calls=len(rows)+len(ids),decoder_forward_calls=1+bool(ids))
