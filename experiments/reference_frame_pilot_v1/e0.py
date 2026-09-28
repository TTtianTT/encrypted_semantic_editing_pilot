"""GPU-only E0. Never imports the legacy runner or reconstruction repair."""
import os,time,json,hashlib,signal
from pathlib import Path
import torch
from torch import nn
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from transformers.modeling_outputs import BaseModelOutput
from prepare import ROOT,dump,digest
from semantics import score
REPO=ROOT.parents[1]
class Editor(nn.Module):
 def __init__(self,kind):
  super().__init__();self.b=nn.Parameter(torch.zeros(768));self.kind=kind
  if kind=='LowRank16':
   self.v=nn.Linear(768,16,bias=False);self.u=nn.Linear(16,768,bias=False)
   nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,h,mask):
  d=self.b+(self.u(self.v(h)) if self.kind=='LowRank16' else 0)
  return h+d*mask.unsqueeze(-1).to(h.dtype)
class Runner:
 def __init__(self):
  assert os.environ.get('SLURM_JOB_ID') and torch.cuda.is_available(),'Slurm GPU required'
  self.cfg=json.loads((ROOT/'config.json').read_text())
  frozen=json.loads((ROOT/'frozen_manifest.json').read_text())
  for name,h in frozen['files'].items():assert digest(ROOT/name)==h,name
  for item in json.loads((ROOT/'source_model_manifest.json').read_text())['actual_files']:assert digest(Path(item['file']))==item['sha256']
  torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  self.tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
  self.model=AutoModelForSeq2SeqLM.from_pretrained(REPO/'models/bart-base',local_files_only=True,attn_implementation='sdpa').cuda().float().eval()
  for p in self.model.parameters():p.requires_grad_(False);p.grad=None
  self.kw={k:self.cfg[k] for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']}
 def batch(self,texts):
  lens=[len(self.tok(t)['input_ids']) for t in texts];assert max(lens)<=self.cfg['source_length'],'No truncation permitted'
  return self.tok(texts,padding='max_length',max_length=self.cfg['source_length'],truncation=False,return_tensors='pt').to('cuda')
 @torch.no_grad()
 def generate(self,texts,editor=None,direct=False):
  start=time.perf_counter();x=self.batch(texts);torch.cuda.synchronize();a=time.perf_counter()
  if direct:
   gen=self.model.generate(**x,**self.kw);torch.cuda.synchronize();d=time.perf_counter();b=c=a
  else:
   h=self.model.get_encoder()(**x).last_hidden_state;torch.cuda.synchronize();b=time.perf_counter()
   if editor is not None:h=editor(h,x.attention_mask)
   torch.cuda.synchronize();c=time.perf_counter()
   gen=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=x.attention_mask,**self.kw);torch.cuda.synchronize();d=time.perf_counter()
  output=self.tok.batch_decode(gen,skip_special_tokens=True,clean_up_tokenization_spaces=False)
  ended=[bool((g[1:]==self.tok.eos_token_id).any()) for g in gen]
  timing=dict(tokenize=(a-start)/len(texts),encode=(b-a)/len(texts),edit=(c-b)/len(texts),decode=(d-c)/len(texts),total=(time.perf_counter()-start)/len(texts))
  return output,ended,timing,[int((g!=self.tok.pad_token_id).sum()) for g in gen]
 def smoke(self,texts):
  torch.manual_seed(42);x=self.batch(texts)
  with torch.no_grad():h=self.model.get_encoder()(**x).last_hidden_state
  audits={}
  for kind in ['Shift','LowRank16']:
   ed=Editor(kind).cuda();assert torch.equal(ed(h,x.attention_mask),h)
   y=x.input_ids.clone();y[y==self.tok.pad_token_id]=-100
   loss=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=ed(h,x.attention_mask)),attention_mask=x.attention_mask,labels=y,use_cache=False).loss;loss.backward()
   gradients={k:float(p.grad.norm()) for k,p in ed.named_parameters()};assert gradients['b']>0
   if kind=='LowRank16':assert gradients['u.weight']>0
   assert all(p.grad is None for p in self.model.parameters())
   with torch.no_grad():
    ed.b.fill_(.01)
    if kind=='LowRank16':ed.u.weight.normal_(std=.01)
    assert torch.equal(ed(h,x.attention_mask)[x.attention_mask==0],h[x.attention_mask==0])
   audits[kind]={'parameters':sum(p.numel() for p in ed.parameters()),'gradients':gradients,'padding_unchanged':True,'zero_initial_identity':True}
  a=self.generate(texts);b=self.generate(texts,direct=True);assert a[0]==b[0]
  dump('calibration/smoke.json',{'operators':audits,'bart_gradients_empty':True,'model_eval':not self.model.training,'direct_encoder_outputs_equal':True,'copy_is_exact_string':True,'precision':str(next(self.model.parameters()).dtype)})
def main():
 start=time.monotonic();runner=Runner()
 rows=[json.loads(l) for l in (ROOT/'data/calibration_views.jsonl').read_text().splitlines()]
 worlds={r['record_id']:r for r in map(json.loads,(ROOT/'data/calibration_worlds.jsonl').read_text().splitlines())}
 runner.smoke([r['source_text'] for r in rows[:4]])
 runner.generate([r['source_text'] for r in rows[:4]]) # warmup
 outpath=ROOT/'calibration/reconstruction_outputs.jsonl'
 existing=[json.loads(l) for l in outpath.read_text().splitlines()] if outpath.exists() else []
 done={r['view_id'] for r in existing};todo=[r for r in rows if r['view_id'] not in done]
 modelhash=digest(REPO/'models/bart-base/model.safetensors')
 for i in range(0,len(todo),16):
  rs=todo[i:i+16];outs,ended,timing,lens=runner.generate([r['source_text'] for r in rs]);direct=runner.generate([r['source_text'] for r in rs],direct=True)
  assert outs==direct[0],'direct generation mismatch'
  with outpath.open('a') as f:
   for r,out,end,ln in zip(rs,outs,ended,lens):
    w=worlds[r['gold_record_id']];result={**r,'output':out,'method':'Identity','seed':None,'model_hash':modelhash,'editor_hash':None,'source_tokens':len(runner.tok(r['source_text'])['input_ids']),'output_tokens':ln,'truncated':not end,'timing_s':timing,'direct_generation_timing_s':direct[2],'direct_equal':True,'score':score(out,r['allowed_context']['target_frame'],w,end),'record_status':w['record_status']}
    existing.append(result);f.write(json.dumps(result)+'\n');f.flush()
  print(f'E0 {len(existing)}/420',flush=True)
 groups={'all':existing,**{s:[r for r in existing if r['record_status']==s] for s in ['recorded_plan','reported_completed','reported_cancelled']}}
 metrics={g:{'N':len(rs),**{k:sum(r['score'][k] for r in rs)/len(rs) for k in ['joint_ok','frame_ok','content_ok','parse_unresolved','plan_to_completed']}} for g,rs in groups.items()}
 passed=metrics['all']['joint_ok']>=.98 and all(metrics[s]['joint_ok']>=.95 for s in groups if s!='all') and metrics['recorded_plan']['plan_to_completed']==0
 dump('calibration/gate.json',{'passed':passed,'metrics':metrics,'decision':'eligible_for_E1' if passed else 'STOP_E0_reconstruction_bottleneck','wall_seconds':time.monotonic()-start,'all_direct_paths_equal':True,'human_review':False})
 print(json.dumps(metrics),flush=True)
if __name__=='__main__':
 start=time.monotonic()
 try:main()
 finally:dump('logs/e0_usage_'+os.environ.get('SLURM_JOB_ID','local')+'.json',{'process_wall_seconds':time.monotonic()-start,'job_id':os.environ.get('SLURM_JOB_ID'),'stage':'E0','gpu_count':1})
