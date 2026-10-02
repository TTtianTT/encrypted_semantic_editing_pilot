import os,time
import torch
from torch import nn
import torch.nn.functional as F
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from transformers.modeling_outputs import BaseModelOutput
from common import *

class Editor(nn.Module):
    def __init__(self,d,rank=16):
        super().__init__();self.b=nn.Parameter(torch.zeros(d));self.v=nn.Linear(d,rank,bias=False);self.u=nn.Linear(rank,d,bias=False)
        nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
    def forward(self,h,m):
        z=h.float();delta=self.b+self.u(self.v(z))
        return (z+delta*m[...,None]).to(h.dtype)

def editors(d,seed):
    torch.manual_seed(seed)
    return nn.ModuleDict({op:Editor(d) for op in ('plus','minus')}).cuda().float()

class Backend:
    def __init__(self,name):
        assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'GPU requires Slurm allocation and srun step'
        assert torch.cuda.is_available()
        self.name=name;self.cfg=read(ROOT/'config.json');m=read(ROOT/'model_manifest.json')[name]
        self.start=time.monotonic();self.tok=AutoTokenizer.from_pretrained(m['directory'],local_files_only=True)
        self.chat=name=='t5gemma';self.cap=self.cfg['source_cap'][name]
        torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        self.model=AutoModelForSeq2SeqLM.from_pretrained(m['directory'],local_files_only=True,dtype=torch.bfloat16 if self.chat else torch.float32,attn_implementation='sdpa').cuda().eval()
        for p in self.model.parameters():p.requires_grad_(False)
        self.d=self.model.config.encoder.hidden_size if self.chat else self.model.config.d_model
        self.eos=self.model.generation_config.eos_token_id;self.eos=set(self.eos if isinstance(self.eos,list) else [self.eos])
        self.kw=dict(max_new_tokens=self.cfg['max_new_tokens'],num_beams=1,do_sample=False,forced_eos_token_id=None)
        if self.chat:self.kw.update(decoder_start_token_id=self.model.config.decoder.bos_token_id,cache_implementation='dynamic')
        self.cache={}
    def wrap(self,t):
        if not self.chat:return t
        body=getattr(self,'instruction',self.cfg.get('copy_instruction','Return exactly one copy of the text below, with no introduction, ending, or extra text.\n\n'))+t
        return self.tok.apply_chat_template([dict(role='user',content=body)],tokenize=False,add_generation_prompt=True)
    @torch.no_grad()
    def encode(self,texts):
        wrapped=[self.wrap(t) for t in texts]
        x=self.tok(wrapped,add_special_tokens=not self.chat,padding='max_length',max_length=self.cap,truncation=False,return_tensors='pt').to('cuda')
        assert x.input_ids.shape[1]==self.cap,'Input cap exceeded, no truncation'
        h=self.model.get_encoder()(**x).last_hidden_state
        return h,x.attention_mask
    @torch.no_grad()
    def cached(self,texts):
        missing=list(dict.fromkeys(t for t in texts if t not in self.cache))
        for i in range(0,len(missing),8):
            ts=missing[i:i+8];h,m=self.encode(ts)
            for t,x,y in zip(ts,h,m):self.cache[t]=(x.cpu(),y.cpu())
        return torch.stack([self.cache[t][0] for t in texts]).cuda(),torch.stack([self.cache[t][1] for t in texts]).cuda()
    def labels(self,texts):
        ids=[self.tok(t,add_special_tokens=False)['input_ids']+[self.tok.eos_token_id] for t in texts] if self.chat else self.tok(texts,truncation=False)['input_ids']
        y=torch.full((len(ids),max(map(len,ids))),-100,device='cuda',dtype=torch.long)
        for i,seq in enumerate(ids):y[i,:len(seq)]=torch.tensor(seq,device='cuda')
        return y
    def ce(self,h,m,texts):
        y=self.labels(texts);out=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=y,use_cache=False)
        n=(y!=-100).sum(1)
        loss=F.cross_entropy(out.logits.float().reshape(-1,out.logits.shape[-1]),y.reshape(-1),ignore_index=-100,reduction='none').reshape(y.shape).sum(1)/n
        return loss,n
    @torch.no_grad()
    def decode(self,h,m):
        g=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,**self.kw)
        text=self.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False)
        return [dict(text=t,ended=any(int(v) in self.eos for v in ids[1:]),generated_tokens=int((ids!=self.tok.pad_token_id).sum())) for t,ids in zip(text,g)]
    def resources(self):
        return dict(model=self.name,dimension=self.d,backbone_parameters=sum(p.numel() for p in self.model.parameters()),parameters_per_operator=33*self.d,total_editor_parameters=66*self.d,gpu=torch.cuda.get_device_name(),visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),allocated_gpu_count=torch.cuda.device_count(),peak_allocated_bytes=torch.cuda.max_memory_allocated(),wall_seconds=time.monotonic()-self.start,job_id=os.environ['SLURM_JOB_ID'],step_id=os.environ['SLURM_STEP_ID'])
