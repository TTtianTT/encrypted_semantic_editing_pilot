"""Real shared BART reconstruction, editor fitting, frozen-config inference.
Resume by re-running identical command; latest optimizer/RNG checkpoints retained.
"""
import argparse,json,hashlib,time,random,os,signal,copy
from pathlib import Path
import numpy as np
import torch
from torch import nn
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from transformers.modeling_outputs import BaseModelOutput
from evaluate import evaluate,features,edit_similarity
ROOT=Path(__file__).resolve().parents[1]
CONFIG={'model_revision':'aadd2ab0ae0c8268c7c9693540e9904811f36177','length':96,'max_new_tokens':100,'lr':.001,'batch':16,'max_steps':1000,'eval_interval':200,'patience':3,'min_delta':.0001,'ranks':[4,16,64],'precision':'float32','task':'StylePTB_TFU','seeds':[42,43,44]}
HASH=hashlib.sha256(json.dumps(CONFIG,sort_keys=True).encode()).hexdigest()
START=time.monotonic(); LIMIT=float(os.environ.get('PILOT_WALL_SECONDS','39000'))
def dump(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False));tmp.replace(p)
def rows(split):return [json.loads(x) for x in (ROOT/f'data/{split}.jsonl').read_text().splitlines()]
def log(s):print(s,flush=True)
def seed(s):random.seed(s);np.random.seed(s);torch.manual_seed(s);torch.cuda.manual_seed_all(s)
def budget():
 if time.monotonic()-START>LIMIT:raise TimeoutError('Predeclared GPU allocation budget reached; resume checkpoints retained')
class Editor(nn.Module):
 def __init__(self,kind,d=768,r=16):
  super().__init__();self.kind=kind;self.r=r
  if kind!='identity':self.b=nn.Parameter(torch.zeros(d))
  if kind in ['lowrank_affine','nonlinear_bottleneck']:
   self.v=nn.Linear(d,r,bias=False);self.u=nn.Linear(r,d,bias=False)
   nn.init.normal_(self.v.weight,std=.01);nn.init.zeros_(self.u.weight)
 def forward(self,z,mask):
  if self.kind=='identity':return z
  delta=self.b
  if hasattr(self,'v'):
   q=self.v(z)
   if self.kind=='nonlinear_bottleneck':q=torch.nn.functional.gelu(q)
   delta=delta+self.u(q)
  return z+delta*mask.unsqueeze(-1).to(z.dtype)
class Runner:
 def __init__(self):
  assert torch.cuda.is_available(),'GPU job required'
  torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
  self.tok=AutoTokenizer.from_pretrained(ROOT/'models/bart-base',local_files_only=True)
  self.model=AutoModelForSeq2SeqLM.from_pretrained(ROOT/'models/bart-base',local_files_only=True,attn_implementation='sdpa').cuda().eval()
  self.freeze();self.train=rows('train');self.dev=rows('dev')
 def freeze(self):
  self.model.eval()
  for p in self.model.parameters():
   p.requires_grad_(False);p.grad=None
 def batch(self,rs,target='reference'):
  x=self.tok([r['input'] for r in rs],padding='max_length',max_length=96,truncation=False,return_tensors='pt').to('cuda')
  y=self.tok([r[target] for r in rs],padding=True,return_tensors='pt')['input_ids'].cuda();y[y==self.tok.pad_token_id]=-100
  assert x.input_ids.shape[1]==96 and y.shape[1]<=96
  return x,y
 def loss(self,ed,rs,reconstruct=False):
  x,y=self.batch(rs,'input' if reconstruct else 'reference')
  with torch.no_grad():z=self.model.get_encoder()(**x).last_hidden_state
  memory=ed(z,x.attention_mask)
  return self.model(encoder_outputs=BaseModelOutput(last_hidden_state=memory),attention_mask=x.attention_mask,labels=y,use_cache=False).loss,(y!=-100).sum().item()
 @torch.no_grad()
 def devloss(self,ed,reconstruct=False):
  total=n=0
  for i in range(0,len(self.dev),16):
   loss,c=self.loss(ed,self.dev[i:i+16],reconstruct);total+=loss.item()*c;n+=c
  return total/n
 def generate(self,ed,rs,method,sd,path,rank=0):
  existing={}
  if path.exists():
   for line in path.read_text().splitlines():
    r=json.loads(line);assert r['config_hash']==HASH;existing[r['source_id']]=r
  with path.open('a') as f:
   for i in range(0,len(rs),16):
    batch=[r for r in rs[i:i+16] if r['source_id'] not in existing]
    if not batch:continue
    budget();x,_=self.batch(batch)
    try:
     with torch.no_grad():
      torch.cuda.synchronize();t=time.perf_counter();z=self.model.get_encoder()(**x).last_hidden_state;torch.cuda.synchronize();t1=time.perf_counter()
      ze=ed(z,x.attention_mask);torch.cuda.synchronize();t2=time.perf_counter()
      gen=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=ze),attention_mask=x.attention_mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
      torch.cuda.synchronize();t3=time.perf_counter()
      outputs=self.tok.batch_decode(gen,skip_special_tokens=True,clean_up_tokenization_spaces=False)
      # BART decoder start is EOS; exclude first position from termination check.
      eos=[bool((g[1:]==self.tok.eos_token_id).any()) for g in gen]
     error=None
    except Exception as e:
     outputs=['']*len(batch);eos=[False]*len(batch);t=t1=t2=t3=0;error=type(e).__name__+': '+str(e)
    for row,out,ended in zip(batch,outputs,eos):
     ev=evaluate(row['input'],out,row['reference'],ended)
     srcids=self.tok(row['input'],add_special_tokens=False)['input_ids'];outids=self.tok(out,add_special_tokens=False)['input_ids']
     ev['token_reconstruction_similarity']=edit_similarity(srcids,outids)
     if error:ev['failure_reasons'].append(error)
     result={**row,'method':method,'seed':sd,'rank':rank,'config_hash':HASH,'output':out,'metrics':ev,'timing_s':{'encode':(t1-t)/len(batch),'edit':(t2-t1)/len(batch),'decode':(t3-t2)/len(batch),'total':(t3-t)/len(batch)},'timing_note':'batch wall time / actual batch size; excludes CPU automatic scoring','generation_error':error}
     f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush();existing[row['source_id']]=result
    log(f'generate {method} seed={sd} {len(existing)}/{len(rs)} -> {path.name}')
  assert len(existing)==len(rs)
  return [existing[r['source_id']] for r in rs]
 def controlled_repair(self):
  dest=ROOT/'checkpoints/shared_reconstruction.pt'
  if dest.exists():self.model.load_state_dict(torch.load(dest,weights_only=True));return
  seed(42)
  for p in self.model.parameters():p.requires_grad_(True)
  # Same training sources and paired targets, no dev/test text used for fitting.
  corpus=[{'input':r[key],'reference':r[key]} for r in self.train for key in ['input','reference']]
  rng=np.random.default_rng(42);schedule=[]
  for epoch in range(2):schedule.extend([list(v) for v in np.array_split(rng.permutation(len(corpus)),int(np.ceil(len(corpus)/16)))])
  opt=torch.optim.AdamW(self.model.parameters(),lr=3e-5,weight_decay=0)
  latest=ROOT/'checkpoints/reconstruction_latest.pt';best=float('inf');start=0
  if latest.exists():
   ck=torch.load(latest,weights_only=False);self.model.load_state_dict(ck['model']);opt.load_state_dict(ck['optimizer']);start=ck['step'];best=ck['best'];torch.set_rng_state(ck['rng']);torch.cuda.set_rng_state_all(ck['cuda_rng'])
  for step,ids in enumerate(schedule[:1200]):
   if step<start:continue
   budget();self.model.train();x,y=self.batch([corpus[j] for j in ids]);opt.zero_grad(set_to_none=True)
   loss=self.model(**x,labels=y,use_cache=False).loss;loss.backward();torch.nn.utils.clip_grad_norm_(self.model.parameters(),1.);opt.step()
   if (step+1)%50==0:log(f'reconstruction step={step+1} loss={loss.item():.5f}')
   if (step+1)%200==0 or step+1==min(len(schedule),1200):
    self.model.eval();vl=self.devloss(Editor('identity').cuda(),True)
    log(f'reconstruction validation step={step+1} loss={vl:.5f}')
    if vl<best:best=vl;torch.save(self.model.state_dict(),ROOT/'checkpoints/reconstruction_best.pt')
    torch.save({'model':self.model.state_dict(),'optimizer':opt.state_dict(),'step':step+1,'best':best,'rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all()},latest)
  self.model.load_state_dict(torch.load(ROOT/'checkpoints/reconstruction_best.pt',weights_only=True));torch.save(self.model.state_dict(),dest);self.freeze()
 def fit(self,kind,rank,sd):
  name=f'{kind}_r{rank}_s{sd}';directory=ROOT/'checkpoints'/name;directory.mkdir(exist_ok=True)
  seed(sd);ed=Editor(kind,r=rank).cuda();bestpath=directory/'best.pt';meta=directory/'complete.json'
  if meta.exists():ed.load_state_dict(torch.load(bestpath,weights_only=True));return ed,json.load(open(meta))
  opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0);rng=np.random.default_rng(sd);schedule=[]
  while len(schedule)<1000:schedule.extend([list(v) for v in np.array_split(rng.permutation(len(self.train)),int(np.ceil(len(self.train)/16)))])
  latest=directory/'latest.pt';best=float('inf');bad=0;start=0;elapsed=0.;grad_audit={};history=[];beststep=0
  if latest.exists():
   ck=torch.load(latest,weights_only=False);ed.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);start=ck['step'];best=ck['best'];bad=ck['bad'];elapsed=ck['elapsed'];history=ck['history'];beststep=ck['beststep'];grad_audit=ck['grad_audit']
  t=time.monotonic()
  for step,ids in enumerate(schedule[:1000]):
   if step<start:continue
   budget();opt.zero_grad(set_to_none=True);loss,_=self.loss(ed,[self.train[j] for j in ids]);assert torch.isfinite(loss)
   loss.backward()
   if step in [0,1]:
    grad_audit[str(step)]={k:float(p.grad.norm()) if p.grad is not None else None for k,p in ed.named_parameters()}
    assert ed.b.grad is not None and ed.b.grad.norm()>0
    if hasattr(ed,'u'):assert ed.u.weight.grad.norm()>0
    if step==1 and hasattr(ed,'v'):assert ed.v.weight.grad.norm()>0
    assert all(p.grad is None for p in self.model.parameters()),'E/G must remain frozen'
   torch.nn.utils.clip_grad_norm_(ed.parameters(),1.);opt.step()
   if (step+1)%50==0:log(f'{name} step={step+1} train_loss={loss.item():.5f}')
   if (step+1)%200==0:
    vl=self.devloss(ed);history.append({'step':step+1,'dev_token_loss':vl});log(f'{name} validation step={step+1} loss={vl:.5f}')
    if vl<best-.0001:best=vl;beststep=step+1;bad=0;torch.save(ed.state_dict(),bestpath)
    else:bad+=1
    ck={'editor':ed.state_dict(),'optimizer':opt.state_dict(),'step':step+1,'best':best,'bad':bad,'elapsed':elapsed+time.monotonic()-t,'history':history,'beststep':beststep,'grad_audit':grad_audit}
    torch.save(ck,latest)
    if bad>=3:break
  md={'method':kind,'rank':rank,'seed':sd,'steps':step+1,'best_step':beststep,'best_dev_loss':best,'elapsed_s':elapsed+time.monotonic()-t,'parameters':sum(p.numel() for p in ed.parameters()),'history':history,'gradient_audit':grad_audit,'config_hash':HASH}
  dump(meta,md);ed.load_state_dict(torch.load(bestpath,weights_only=True));return ed,md
 def smoke(self):
  seed(42);x,_=self.batch(self.train[:4]);ed=Editor('lowrank_affine',r=4).cuda()
  with torch.no_grad():
   z=self.model.get_encoder()(**x).last_hidden_state
   assert torch.equal(ed(z,x.attention_mask),z)
   ed.u.weight.normal_(std=.01);out=ed(z,x.attention_mask)
   dense=z+((z@ed.v.weight.T)@ed.u.weight.T+ed.b)*x.attention_mask.unsqueeze(-1)
   assert torch.allclose(out,dense,atol=1e-6)
   assert torch.equal(out[x.attention_mask==0],z[x.attention_mask==0])
   fresh=Editor('lowrank_affine',r=4).cuda();fresh.load_state_dict(ed.state_dict());assert torch.equal(out,fresh(z,x.attention_mask))
   direct=self.model.generate(**x,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
   memory=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=z),attention_mask=x.attention_mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
   assert torch.equal(direct,memory)
  loss,_=self.loss(ed,self.train[:4]);loss.backward();assert ed.u.weight.grad.norm()>0 and ed.v.weight.grad.norm()>0
  dump(ROOT/'results/smoke.json',{'identity_path_equal':True,'mask_preserved':True,'factor_direction_correct':True,'state_reload_equal':True,'gradient_through_frozen_G':True,'loss':loss.item(),'memory_shape':list(z.shape)})
 def run(self):
  dump(ROOT/'config.json',CONFIG);self.smoke()
  identity=Editor('identity').cuda()
  devbase=self.generate(identity,self.dev,'identity_pre_repair',42,ROOT/'results/dev_identity_initial.jsonl')
  def gate(rr):return {'n':len(rr),'content_auto':sum(x['metrics']['content_auto'] for x in rr)/len(rr),'invalid_auto':sum(not x['metrics']['valid_auto'] for x in rr)/len(rr),'exact_reconstruction':sum(x['metrics']['exact_reconstruction'] for x in rr)/len(rr),'token_reconstruction_similarity':float(np.mean([x['metrics']['token_reconstruction_similarity'] for x in rr]))}
  g=gate(devbase);log(f'R initial {g}');initial=g
  if g['content_auto']<.9 or g['invalid_auto']>.05:
   log('ONE controlled shared reconstruction repair');self.controlled_repair();self.freeze()
   g=gate(self.generate(identity,self.dev,'identity_post_repair',42,ROOT/'results/dev_identity_repaired.jsonl'))
  passed=g['content_auto']>=.9 and g['invalid_auto']<=.05
  dump(ROOT/'results/gate_R.json',{'initial':initial,'final':g,'passed':passed,'repaired':(ROOT/'checkpoints/shared_reconstruction.pt').exists()})
  if not passed:log('STOP: representation bottleneck');return
  # Development evaluator calibration only; never alter rule after inspecting outputs.
  gold=[evaluate(r['input'],r['reference'],r['reference']) for r in self.dev]
  dump(ROOT/'results/evaluator_validation.json',{'n':len(gold),'gold_future_detection':float(np.mean([r['attribute_auto'] for r in gold])),'source_future_detection':float(np.mean([features(r['input'])['future'] for r in self.dev])),'gold_content_acceptance':float(np.mean([r['content_auto'] for r in gold])),'note':'coverage against paired developer data, not human-labelled accuracy; strict lemma/POS/NER errors possible','reliable_for_gate_A':float(np.mean([r['content_auto'] for r in gold]))>=.9})
  fitted=[]
  for kind,r in [('shift',0)]+[('lowrank_affine',r) for r in CONFIG['ranks']]:
   ed,md=self.fit(kind,r,42);fitted.append(md)
  chosen=min([m for m in fitted if m['method']=='lowrank_affine'],key=lambda m:(m['best_dev_loss'],m['rank']))['rank']
  self.fit('nonlinear_bottleneck',chosen,42)
  frozen={'chosen_rank':chosen,'config_hash':HASH,'selection':'seed42 developer target token NLL; no test output accessed','fitted':fitted,'frozen_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
  lock=ROOT/'results/frozen_configuration.json'
  if lock.exists():assert json.load(open(lock))['chosen_rank']==chosen
  else:dump(lock,frozen)
  for sd in [43,44]:
   for kind,r in [('shift',0),('lowrank_affine',chosen),('nonlinear_bottleneck',chosen)]:self.fit(kind,r,sd)
  # Only now open fixed test split; no subsequent tuning allowed.
  test=rows('test');self.generate(identity,test,'identity',42,ROOT/'results/test_identity.jsonl')
  diagnostics=rows('diagnostic');self.generate(identity,diagnostics,'identity',42,ROOT/'results/diagnostic_identity.jsonl')
  for sd in CONFIG['seeds']:
   for kind,r in [('shift',0),('lowrank_affine',chosen),('nonlinear_bottleneck',chosen)]:
    ed,_=self.fit(kind,r,sd);self.generate(ed,test,kind,sd,ROOT/f'results/test_{kind}_s{sd}.jsonl',r)
    self.generate(ed,diagnostics,kind,sd,ROOT/f'results/diagnostic_{kind}_s{sd}.jsonl',r)
  dump(ROOT/'results/run_complete.json',{'completed':True,'wall_s':time.monotonic()-START,'config_hash':HASH});log('STAGE_A_COMPLETE')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--smoke',action='store_true');args=a.parse_args()
 try:
  runner=Runner()
  if args.smoke:runner.smoke()
  else:runner.run()
 finally:dump(ROOT/f'logs/process_usage_{os.environ.get("SLURM_JOB_ID","local")}.json',{'wall_s':time.monotonic()-START,'gpu_count':torch.cuda.device_count(),'job_id':os.environ.get('SLURM_JOB_ID'),'budget_limit_s':LIMIT})
