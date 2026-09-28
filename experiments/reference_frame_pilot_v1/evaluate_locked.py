"""Fixed test evaluation, resumable by complete batches; never tunes checkpoints."""
import json,time,os,random
from pathlib import Path
from datetime import date,timedelta
import torch
from torch import nn
from transformers.modeling_outputs import BaseModelOutput
from e0 import Runner,Editor
from prepare import ROOT,dump,digest,frame,render
from semantics import score,text_rule
OPS=['T_plus','T_minus','P_13','P_31']
PATHS={'time_then_person':['T_plus','P_13'],'person_then_time':['P_13','T_plus'],'time_twice':['T_plus','T_plus'],'time_return':['T_plus','T_minus'],'person_return':['P_13','P_31']}
def advance(c,op):
 c=c.copy()
 if op.startswith('T'):c['view_date']=(date.fromisoformat(c['view_date'])+timedelta(days=1 if op=='T_plus' else -1)).isoformat()
 else:c['perspective']='third' if op=='P_13' else 'first'
 return c
class Evaluation:
 def __init__(self):
  self.start=time.monotonic();self.limit=float(os.environ['RF_WALL_SECONDS']);self.runner=Runner();self.mhash=digest(ROOT.parents[1]/'models/bart-base/model.safetensors')
  assert json.loads((ROOT/'evaluation/e1_gate.json').read_text())['passed']
  files={}
  for method in ['Shift','LowRank16']:
   for seed in [42,43,44]:
    d=ROOT/f'checkpoints/{method}/s{seed}';assert (d/'complete.json').exists();files[str(d.relative_to(ROOT)/'best.pt')]=digest(d/'best.pt')
  lock=ROOT/'checkpoints/locked.json'
  if lock.exists():assert json.loads(lock.read_text())['files']==files
  else:dump('checkpoints/locked.json',{'files':files,'config_hash':digest(ROOT/'config.json'),'selection':'dev atomic target-token NLL','locked_before_test_generation':True})
  self.worlds={w['record_id']:w for w in map(json.loads,(ROOT/'data/test_worlds.jsonl').read_text().splitlines())}
  self.atomic=[]
  for split in ['test_iid','test_template_ood']:self.atomic += [json.loads(l) for l in (ROOT/f'data/{split}_pairs.jsonl').read_text().splitlines()]
  self.seen={};self.handles={}
  for name in ['atomic','composition','reconstruction_controls']:
   p=ROOT/f'outputs/{name}.jsonl';self.seen[name]={r['uid'] for r in map(json.loads,p.read_text().splitlines())} if p.exists() else set()
  self.runner.generate([r['source_text'] for r in self.atomic[:4]])
 def check(self):
  if time.monotonic()-self.start>self.limit-60:raise TimeoutError('Evaluation budget stop; flushed outputs resumable')
 def uid(self,method,seed,path,rid):return f'{method}/{seed}/{path}/{rid}'
 def save(self,file,row,method,seed,path,out,ended,timing,editor_hash=None,extra=None):
  w=self.worlds[row['gold_record_id']];uid=self.uid(method,seed,path,row.get('pair_id',row['gold_record_id']))
  assert uid not in self.seen[file]
  result={**row,'uid':uid,'method':method,'seed':seed,'path':path,'test_stratum':w['split'],'record_status':w['record_status'],'output':out,'model_hash':self.mhash,'editor_hash':editor_hash,'config_hash':digest(ROOT/'config.json'),'source_tokens':len(self.runner.tok(row['source_text'])['input_ids']),'output_tokens':len(self.runner.tok(out)['input_ids']),'truncated':not ended,'timing_s':timing,'score':score(out,row['allowed_context']['target_frame'],w,ended),**(extra or {})}
  with (ROOT/f'outputs/{file}.jsonl').open('a') as f:f.write(json.dumps(result)+'\n');f.flush()
  self.seen[file].add(uid)
 def missing(self,file,rows,method,seed,path):return [r for r in rows if self.uid(method,seed,path,r.get('pair_id',r['gold_record_id'])) not in self.seen[file]]
 def atomic_method(self,method,seed=None,eds=None,eh=None):
  for path in sorted({r['path'] for r in self.atomic}):
   allrows=[r for r in self.atomic if r['path']==path]
   if method=='Wrong-operation':allrows=[r for r in allrows if int(r['gold_record_id'].rsplit('_',1)[1])<10]
   todo=self.missing('atomic',allrows,method,seed,path)
   for i in range(0,len(todo),16):
    self.check();rs=todo[i:i+16];texts=[r['source_text'] for r in rs];extra=[{} for r in rs];op=rs[0]['operation_ids'][0]
    cpu=0
    if method.startswith('Text-rule'):
     t=time.perf_counter();results=[text_rule(r['source_text'],r['allowed_context']['source_frame'],r['allowed_context']['target_frame']) for r in rs];texts=[r[0] for r in results];cpu=(time.perf_counter()-t)/len(rs);extra=[{'rule_error':r[1]} for r in results]
    if method=='Target reconstruction':texts=[r['target_text'] for r in rs]
    if method in ['Copy','Text-rule']:
     outs=texts;ends=[True]*len(rs);timing={'encode':0,'edit':cpu,'decode':0,'total':cpu}
    else:
     ed=None
     if eds is not None:
      actual=op
      if method=='Wrong-operation':actual='P_13' if op.startswith('T') else 'T_plus'
      ed=eds[actual];extra=[{**x,'actual_operation_ids':[actual]} for x in extra]
     outs,ends,timing,_=self.runner.generate(texts,ed);timing['cpu_rule']=cpu;timing['total']+=cpu
    for r,out,end,e in zip(rs,outs,ends,extra):self.save('atomic',r,method,seed,path,out,end,timing,eh,e)
  print('atomic',method,seed,flush=True)
 @torch.no_grad()
 def latent(self,texts,eds,ops):
  runner=self.runner;t=time.perf_counter();x=runner.batch(texts);torch.cuda.synchronize();a=time.perf_counter();h=runner.model.get_encoder()(**x).last_hidden_state;torch.cuda.synchronize();b=time.perf_counter();h1=eds[ops[0]](h,x.attention_mask);h2=eds[ops[1]](h1,x.attention_mask);torch.cuda.synchronize();c=time.perf_counter()
  gen=runner.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h2),attention_mask=x.attention_mask,**runner.kw);torch.cuda.synchronize();d=time.perf_counter()
  intermediate=runner.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h1),attention_mask=x.attention_mask,**runner.kw);torch.cuda.synchronize();e=time.perf_counter()
  outs=runner.tok.batch_decode(gen,skip_special_tokens=True,clean_up_tokenization_spaces=False);mids=runner.tok.batch_decode(intermediate,skip_special_tokens=True,clean_up_tokenization_spaces=False)
  end=[bool((g[1:]==runner.tok.eos_token_id).any()) for g in gen];midend=[bool((g[1:]==runner.tok.eos_token_id).any()) for g in intermediate]
  timing={'encode':(b-a)/len(texts),'edit':(c-b)/len(texts),'decode':(d-c)/len(texts),'tokenize':(a-t)/len(texts),'diagnostic_decode':(e-d)/len(texts),'total':(time.perf_counter()-t)/len(texts),'core_without_diagnostic':(d-t)/len(texts)}
  return outs,end,mids,midend,timing
 def chains(self,method,seed,eds,eh):
  for name,ops in PATHS.items():
   rows=[]
   for w in self.worlds.values():
    source=frame(w);middle=advance(source,ops[0]);target=advance(middle,ops[1]);rows.append(dict(gold_record_id=w['record_id'],source_text=render(w,source),target_text=render(w,target),allowed_context={'source_frame':source,'middle_frame':middle,'target_frame':target},operation_ids=ops))
   for mode in ['latent_chain','decode_reencode']:
    path=name+'/'+mode;todo=self.missing('composition',rows,method,seed,path)
    for i in range(0,len(todo),16):
     self.check();rs=todo[i:i+16];texts=[r['source_text'] for r in rs]
     if mode=='latent_chain':outs,ends,mids,midends,timing=self.latent(texts,eds,ops)
     else:
      mids,midends,t1,_=self.runner.generate(texts,eds[ops[0]]);outs,ends,t2,_=self.runner.generate(mids,eds[ops[1]]);timing={k:t1.get(k,0)+t2.get(k,0) for k in set(t1)|set(t2)}
     for r,out,end,mid,midend in zip(rs,outs,ends,mids,midends):
      self.save('composition',r,method,seed,path,out,end,timing,eh,{'intermediate_output':mid,'intermediate_score':score(mid,r['allowed_context']['middle_frame'],self.worlds[r['gold_record_id']],midend),'final_ended':end,'intermediate_ended':midend})
   print('chain',method,seed,name,flush=True)
 def reconstruction(self):
  rows=[dict(gold_record_id=w['record_id'],source_text=render(w,frame(w)),allowed_context={'source_frame':frame(w),'target_frame':frame(w)},operation_ids=[]) for w in self.worlds.values()]
  todo=self.missing('reconstruction_controls',rows,'reconstruction_only',None,'two_reconstructions')
  for i in range(0,len(todo),16):
   self.check();rs=todo[i:i+16];mids,me,t1,_=self.runner.generate([r['source_text'] for r in rs]);outs,ends,t2,_=self.runner.generate(mids);timing={k:t1.get(k,0)+t2.get(k,0) for k in set(t1)|set(t2)}
   for r,out,end,mid,midend in zip(rs,outs,ends,mids,me):self.save('reconstruction_controls',r,'reconstruction_only',None,'two_reconstructions',out,end and midend,timing,extra={'intermediate_output':mid,'intermediate_score':score(mid,r['allowed_context']['source_frame'],self.worlds[r['gold_record_id']],midend)})
 def run(self):
  for method in ['Copy','Identity','Target reconstruction','Text-rule','Text-rule + E/D']:self.atomic_method(method)
  self.reconstruction()
  for method in ['Shift','LowRank16']:
   for seed in [42,43,44]:
    path=ROOT/f'checkpoints/{method}/s{seed}/best.pt';eds=nn.ModuleDict({op:Editor(method) for op in OPS}).cuda();eds.load_state_dict(torch.load(path,weights_only=True));eds.eval();eh=digest(path)
    self.atomic_method(method,seed,eds,eh)
    # Include originating editor method in wrong-operation method name by extra hash/seed;
    # distinct method label avoids collisions across Shift and LowRank16.
    if method=='LowRank16':self.atomic_method('Wrong-operation',seed,eds,eh)
    self.chains(method,seed,eds,eh)
  dump('evaluation/test_generation_complete.json',{'completed':True,'wall_seconds':time.monotonic()-self.start,'counts':{k:len(v) for k,v in self.seen.items()},'test_tuning':False})
if __name__=='__main__':Evaluation().run()
