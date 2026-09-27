"""Fixed-budget paired latent-consistency ablation + three-seed Shift audit.
Training references are detached; generation never consumes target encodings.
This is a posthoc experiment on previously inspected, unchanged test data.
"""
import os,time,json,hashlib,copy
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers.modeling_outputs import BaseModelOutput
from pilot import ROOT,Runner,Editor,seed,dump,rows
from b_pilot import Composition,metrics as b_metrics,read as b_read
from evaluate import evaluate,edit_similarity
P=ROOT/'experiments/latent_consistency_v1';CFG=json.load(open(P/'config.json'));CH=hashlib.sha256(json.dumps(CFG,sort_keys=True).encode()).hexdigest();START=time.monotonic()
def check_time():
 if time.monotonic()-START>CFG['max_gpu_wall_seconds']:raise TimeoutError('Supplemental GPU budget stop; saved recovery checkpoints retained')
def tensor_hash(module):
 h=hashlib.sha256()
 for k,v in module.state_dict().items():h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
 return h.hexdigest()
def tokenize(r,texts):
 t=r.tok(texts,padding='max_length',max_length=96,truncation=False,return_tensors='pt').to('cuda');assert t.input_ids.shape[1]==96
 return t
@torch.no_grad()
def encode(r,texts):
 t=tokenize(r,texts);return r.model.get_encoder()(**t).last_hidden_state,t.attention_mask
@torch.no_grad()
def aligned_target(target,target_mask,source_mask):
 out=torch.zeros((len(target),source_mask.shape[1],target.shape[2]),device=target.device,dtype=target.dtype)
 for i,(a,b) in enumerate(zip(target_mask.sum(1).tolist(),source_mask.sum(1).tolist())):
  assert a>0 and b>0
  out[i,:b]=F.interpolate(target[i,:a].T.unsqueeze(0),size=b,mode='linear',align_corners=True)[0].T
 return out

def consistency(memory,aligned,mask):
 w=mask.unsqueeze(-1).to(memory.dtype);count=mask.sum(1)*memory.shape[-1]
 mse=((memory-aligned).square()*w).sum((1,2))/count
 energy=(aligned.square()*w).sum((1,2))/count
 return mse/(energy.detach()+1e-8)

def loss_pair(r,ed,rr):
 x,y=r.batch(rr)
 with torch.no_grad():
  z=r.model.get_encoder()(**x).last_hidden_state;zt,mt=encode(r,[q['reference'] for q in rr]);aligned=aligned_target(zt,mt,x.attention_mask)
 ze=ed(z,x.attention_mask)
 ce=r.model(encoder_outputs=BaseModelOutput(last_hidden_state=ze),attention_mask=x.attention_mask,labels=y,use_cache=False).loss
 co=consistency(ze,aligned,x.attention_mask).mean()
 assert not zt.requires_grad and not aligned.requires_grad
 return ce,co,(y!=-100).sum().item()

@torch.no_grad()
def dev_b(r,eds):
 result={}
 for op in ['future','present','passive','seen_combo']:
  rr=b_read('dev_'+op);ed=Composition(eds,'present') if op=='seen_combo' else eds[op];total=n=co=0.
  for i in range(0,len(rr),8):
   batch=rr[i:i+8];c,l,k=loss_pair(r,ed,batch);total+=c.item()*k;n+=k;co+=l.item()*len(batch)
  result[op]={'n':len(rr),'CE':total/n,'consistency':co/len(rr)}
 return result

def smoke(r,train):
 seed(42);ed=Editor('lowrank_affine',r=64).cuda();rr=train['future'][:4]
 ce,co,_=loss_pair(r,ed,rr);gr=torch.autograd.grad(co,tuple(ed.parameters()),retain_graph=True);gn=float(torch.sqrt(sum(g.square().sum() for g in gr)))
 assert gn>0 and torch.isfinite(co);(ce+.1*co).backward();assert all(p.grad is None for p in r.model.parameters())
 with torch.no_grad():
  z,m=encode(r,[x['input'] for x in rr]);same=aligned_target(z,m,m)
  assert torch.allclose(z[m.bool()],same[m.bool()],atol=1e-6)
  assert consistency(same,same,m).max()==0
  changed=same.clone();changed[~m.bool()]=123.;assert consistency(changed,same,m).max()==0
 dump(P/'results/smoke.json',{'target_stop_gradient':True,'EG_frozen':True,'same_length_alignment_equal':True,'padding_excluded':True,'consistency_gradient_norm':gn,'initial_CE':ce.item(),'initial_consistency':co.item(),'config_hash':CH})

@torch.no_grad()
def decode(r,memory,mask):
 ids=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=memory),attention_mask=mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
 text=r.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False);eos=[bool((g[1:]==r.tok.eos_token_id).any()) for g in ids]
 return text,eos

def train_b(r,train,context,lam):
 name=f'{context}_lambda{lam:g}';d=P/'checkpoints'/name;d.mkdir(exist_ok=True)
 seed(42);eds=nn.ModuleDict({op:Editor('lowrank_affine',r=64).cuda() for op in ['future','present','passive']});initial_hash=tensor_hash(eds)
 if (d/'complete.json').exists():eds.load_state_dict(torch.load(d/'final.pt',weights_only=True));return eds,json.load(open(d/'complete.json'))
 opt=torch.optim.AdamW(eds.parameters(),lr=.001,weight_decay=0);rng=np.random.default_rng(42);schedule=[]
 for step in range(600):
  op=['future','present','passive'][step%3];ix=rng.integers(0,len(train[op]),size=8).tolist();cx=rng.integers(0,len(train['seen_combo']),size=8).tolist() if context=='seen_combo' else [];schedule.append((op,ix,cx))
 schedule_hash=hashlib.sha256(json.dumps(schedule).encode()).hexdigest();history=[];begin=0;previous_time=0.
 if (d/'latest.pt').exists():
  ck=torch.load(d/'latest.pt',weights_only=False);assert ck['config_hash']==CH;eds.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);begin=ck['step'];history=ck['history'];previous_time=ck['wall_s']
 start=time.monotonic()
 for step in range(begin,600):
  check_time();op,ix,cx=schedule[step];opt.zero_grad(set_to_none=True);ce,co,_=loss_pair(r,eds[op],[train[op][i] for i in ix])
  if cx:
   c2,l2,_=loss_pair(r,Composition(eds,'present'),[train['seen_combo'][i] for i in cx]);ce=.5*(ce+c2);co=.5*(co+l2)
  loss=ce+lam*co;assert torch.isfinite(loss);loss.backward();assert all(p.grad is None for p in r.model.parameters());gn=torch.nn.utils.clip_grad_norm_(eds.parameters(),1.);opt.step()
  if (step+1)%100==0:
   record={'step':step+1,'train_CE':ce.item(),'train_consistency':co.item(),'total_loss':loss.item(),'gradient_norm_before_clip':float(gn)};history.append(record)
   torch.save({'editor':eds.state_dict(),'optimizer':opt.state_dict(),'step':step+1,'history':history,'wall_s':previous_time+time.monotonic()-start,'config_hash':CH},d/'latest.pt');print(name,record,flush=True)
 torch.cuda.synchronize();fit_time=previous_time+time.monotonic()-start
 torch.save(eds.state_dict(),d/'final.pt');md={'name':name,'context':context,'lambda':lam,'seed':42,'steps':600,'parameters':sum(p.numel() for p in eds.parameters()),'single_examples':4800,'seen_combo_examples':4800 if context=='seen_combo' else 0,'target_encoder_batches':1200 if context=='seen_combo' else 600,'initial_hash':initial_hash,'schedule_hash':schedule_hash,'final_hash':tensor_hash(eds),'training_wall_s':fit_time,'history':history,'dev':dev_b(r,eds),'config_hash':CH}
 dump(d/'complete.json',md);return eds,md

@torch.no_grad()
def generate_b(r,eds,name,rr,pathkind):
 path=P/f'results/B_{name}_{pathkind}.jsonl'
 if path.exists() and len(path.read_text().splitlines())==len(rr):return
 # Per-run output is safely replayable; training checkpoints are unaffected.
 with path.open('w') as f:
  for i in range(0,len(rr),8):
   batch=rr[i:i+8];check_time();torch.cuda.synchronize();t=time.perf_counter();intermediates=['']*len(batch);error=None;memory=None
   try:
    z,m=encode(r,[q['input'] for q in batch]);memory=eds['passive'](z,m)
    if pathkind=='decode_reencode':
     intermediates,mid_eos=decode(r,memory,m)
     if not all(mid_eos):raise ValueError('intermediate_no_eos')
     memory,m=encode(r,intermediates)
    if pathkind!='single_passive':memory=eds['future'](memory,m)
    outputs,eos=decode(r,memory,m)
   except Exception as ex:outputs=['']*len(batch);eos=[False]*len(batch);error=type(ex).__name__+': '+str(ex)
   torch.cuda.synchronize();seconds=time.perf_counter()-t
   # Offline diagnostics AFTER generation. Targets never enter generate/decode.
   target_errors=[None]*len(batch);cycle_errors=[None]*len(batch)
   if memory is not None and error is None:
    zt,mt=encode(r,[q['reference'] for q in batch]);target_errors=consistency(memory,aligned_target(zt,mt,m),m).cpu().tolist()
    for j,out in enumerate(outputs):
     if len(r.tok(out)['input_ids'])<=96:
      zo,mo=encode(r,[out]);cycle_errors[j]=float(consistency(memory[j:j+1],aligned_target(zo,mo,m[j:j+1]),m[j:j+1])[0])
   for q,out,e,mid,te,cy in zip(batch,outputs,eos,intermediates,target_errors,cycle_errors):
    met=b_metrics(q['input'],out,q['reference'],e)
    if error:met['failure_reasons'].append(error)
    rec={**q,'method':name,'path':pathkind,'seed':42,'rank':64,'config_hash':CH,'output':out,'intermediate':mid,'metrics':met,'exact_reference':out in q['references'],'target_memory_error_offline':te if pathkind!='single_passive' else None,'reencode_memory_error_offline':cy,'timing_s':{'generate_total':seconds/len(batch)},'failure':error}
    f.write(json.dumps(rec)+'\n');f.flush()
 print('B_GENERATED',name,pathkind,len(rr),flush=True)

def train_shift(r,sd):
 d=P/'checkpoints'/f'shift_s{sd}';d.mkdir(exist_ok=True);seed(sd);ed=Editor('shift').cuda();opt=torch.optim.AdamW(ed.parameters(),lr=.001,weight_decay=0)
 if (d/'complete.json').exists():ed.load_state_dict(torch.load(d/'best.pt',weights_only=True));return ed,json.load(open(d/'complete.json'))
 source=ROOT/f'checkpoints/shift_r0_s{sd}/latest.pt';ck=torch.load(source,weights_only=False);assert ck['step']==1000
 ed.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);assert opt.param_groups[0]['lr']==.001
 history=copy.deepcopy(ck['history']);best=ck['best'];beststep=ck['beststep'];begin=1000;wall_old=0.;initial=tensor_hash(ed)
 if not (d/'latest.pt').exists():torch.save(torch.load(ROOT/f'checkpoints/shift_r0_s{sd}/best.pt',weights_only=True),d/'best.pt')
 if (d/'latest.pt').exists():
  ck=torch.load(d/'latest.pt',weights_only=False);assert ck['config_hash']==CH;ed.load_state_dict(ck['editor']);opt.load_state_dict(ck['optimizer']);history=ck['history'];best=ck['best'];beststep=ck['beststep'];begin=ck['step'];wall_old=ck['wall_s']
 rng=np.random.default_rng(sd);schedule=[]
 while len(schedule)<5000:schedule.extend([list(v) for v in np.array_split(rng.permutation(len(r.train)),int(np.ceil(len(r.train)/16)))])
 resumed_devloss=r.devloss(ed);start=time.monotonic()
 for step in range(begin,5000):
  check_time();opt.zero_grad(set_to_none=True);loss,_=r.loss(ed,[r.train[i] for i in schedule[step]]);assert torch.isfinite(loss);loss.backward();gn=float(ed.b.grad.norm());before=ed.b.detach().clone();torch.nn.utils.clip_grad_norm_(ed.parameters(),1.);opt.step()
  if (step+1)%200==0:
   vl=r.devloss(ed);delta=float((ed.b.detach()-before).norm());history.append({'step':step+1,'dev_token_loss':vl,'train_loss':float(loss),'gradient_norm':gn,'last_parameter_update_l2':delta,'b_l2':float(ed.b.detach().norm())})
   if vl<best-.0001:best=vl;beststep=step+1;torch.save(ed.state_dict(),d/'best.pt')
   torch.save({'editor':ed.state_dict(),'optimizer':opt.state_dict(),'step':step+1,'history':history,'best':best,'beststep':beststep,'wall_s':wall_old+time.monotonic()-start,'config_hash':CH},d/'latest.pt');print('SHIFT',sd,history[-1],flush=True)
 torch.save(ed.state_dict(),d/'final.pt');curve={v['step']:v['dev_token_loss'] for v in history};gains=[(curve[x]-curve[x+1000])/curve[x] for x in [3000,4000]]
 md={'seed':sd,'start_step':1000,'final_step':5000,'best_step':beststep,'best_dev_loss':best,'source_checkpoint':str(source.relative_to(ROOT)),'initial_editor_hash':initial,'resumed_devloss':resumed_devloss,'optimizer_moments_resumed':True,'training_wall_s':wall_old+time.monotonic()-start,'history':history,'last_two_1000_step_relative_improvements':gains,'near_plateau_by_preregistered_rule':all(0<=v<=.01 for v in gains),'config_hash':CH}
 dump(d/'complete.json',md);ed.load_state_dict(torch.load(d/'best.pt',weights_only=True));return ed,md

@torch.no_grad()
def generate_a(r,ed,rr,name,sd):
 path=P/f'results/A_{name}_s{sd}.jsonl'
 if path.exists() and len(path.read_text().splitlines())==len(rr):return
 with path.open('w') as f:
  for i in range(0,len(rr),16):
   batch=rr[i:i+16];check_time();torch.cuda.synchronize();t=time.perf_counter();error=None
   try:z,m=encode(r,[q['input'] for q in batch]);out,eos=decode(r,ed(z,m),m)
   except Exception as ex:out=['']*len(batch);eos=[False]*len(batch);error=type(ex).__name__+': '+str(ex)
   torch.cuda.synchronize();elapsed=time.perf_counter()-t
   for q,s,e in zip(batch,out,eos):
    met=evaluate(q['input'],s,q['reference'],e)
    if error:met['failure_reasons'].append(error)
    row={**q,'method':name,'seed':sd,'config_hash':CH,'output':s,'metrics':met,'exact_reference':s in q['references'],'failure':error,'timing_s':{'total':elapsed/len(batch)}};f.write(json.dumps(row)+'\n');f.flush()
 print('A_GENERATED',name,sd,len(rr),flush=True)

def main():
 r=Runner();train={op:b_read('train_'+op) for op in ['future','present','passive','seen_combo']};smoke(r,train);fits={};meta=[]
 for context in CFG['B_contexts']:
  for lam in CFG['lambda_values']:
   eds,md=train_b(r,train,context,lam);fits[md['name']]=eds;meta.append(md)
 for context in CFG['B_contexts']:
  pair=[x for x in meta if x['context']==context];assert pair[0]['initial_hash']==pair[1]['initial_hash'] and pair[0]['schedule_hash']==pair[1]['schedule_hash']
 dump(P/'results/B_frozen.json',{'runs':meta,'config_hash':CH,'frozen_before_supplemental_test_generation':True})
 test=b_read('test_heldout_combo')
 for name,eds in fits.items():
  for path in ['latent_once','decode_reencode','single_passive']:generate_b(r,eds,name,test,path)
 # r.train/dev still original A sets; B loss never changed Runner datasets.
 assert len(r.train)==5000 and len(r.dev)==363
 shifts={};shiftmeta=[]
 for sd in [42,43,44]:ed,md=train_shift(r,sd);shifts[sd]=ed;shiftmeta.append(md)
 dump(P/'results/Shift_frozen.json',{'runs':shiftmeta,'config_hash':CH,'frozen_before_supplemental_A_test_generation':True})
 test=rows('test')
 for sd in [42,43,44]:
  original=Editor('shift').cuda();original.load_state_dict(torch.load(ROOT/f'checkpoints/shift_r0_s{sd}/best.pt',weights_only=True))
  lowrank=Editor('lowrank_affine',r=64).cuda();lowrank.load_state_dict(torch.load(ROOT/f'checkpoints/lowrank_affine_r64_s{sd}/best.pt',weights_only=True))
  for name,ed in [('shift_1000',original),('shift_extended',shifts[sd]),('lowrank_1000_budget',lowrank)]:generate_a(r,ed,test,name,sd)
 dump(P/'results/complete.json',{'complete':True,'wall_s':time.monotonic()-START,'job_id':os.environ.get('SLURM_JOB_ID'),'config_hash':CH});print('CONSISTENCY_AND_CONVERGENCE_COMPLETE',flush=True)
if __name__=='__main__':
 try:main()
 finally:dump(P/'logs'/f'usage_{os.environ.get("SLURM_JOB_ID","local")}.json',{'wall_s':time.monotonic()-START,'gpu_count':torch.cuda.device_count(),'job_id':os.environ.get('SLURM_JOB_ID')})
