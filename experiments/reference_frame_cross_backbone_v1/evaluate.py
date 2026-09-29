import argparse,time,collections,torch
from common import *
from backend import Backend,new_editors

def metric(output,frame,w,ended):
 sc=score(output,frame,w,ended);sc['person_ok']=sc['perspective_ok'];p=sc['parsed'];sc['field_ok']={f:p is not None and p[f]==w[f] for f in NONDATE}
 # Surface diagnostics do not turn unresolved output into a confirmed semantic error.
 sc['missing_header']=not output.startswith('Author: ');sc['repeated_header']=output.count('Author:')>1;sc['empty_output']=not output.strip();sc['repeated_trigram']=False
 words=output.split();triples=[tuple(words[i:i+3]) for i in range(len(words)-2)];sc['repeated_trigram']=len(triples)>len(set(triples));return sc
class Eval:
 def __init__(self,be):self.be=be;self.worlds={w['record_id']:w for p in (ROOT/'data').glob('*worlds.jsonl') for w in read(p.relative_to(ROOT))}
 def neural(self,rows,eds,group,mode,dest):
  p=ROOT/dest;p.parent.mkdir(parents=True,exist_ok=True);existing=read(dest) if p.exists() else [];seen={r['uid'] for r in existing};groups=collections.defaultdict(list)
  for r in rows:groups[r['path'],tuple(r['operations'])].append(r)
  for (path,ops),rs in groups.items():
   todo=[r for r in rs if f'{group}/{mode}/'+r['row_id'] not in seen]
   for i in range(0,len(todo),self.be.cfg.get('generation_batch_size',4)):
    batch=todo[i:i+self.be.cfg.get('generation_batch_size',4)];ss,timing,lens=self.be.infer([r['source_text'] for r in batch],eds,list(ops),mode)
    with p.open('a') as f:
     for r,steps,n in zip(batch,ss,lens):
      for step,c in zip(steps,r['frames'][1:]):step['frame']=c;step['score']=metric(step['output'],c,self.worlds[r['record_id']],step['ended'])
      record={**r,'model':self.be.name,'model_revision':self.be.manifest['revision'],'editor_hash':getattr(self.be,'editor_hash',None),'interface_hash':digest(ROOT/f'models/{self.be.name}_interface.json'),'group':group,'mode':mode,'uid':f'{group}/{mode}/'+r['row_id'],'source_tokens':n,'wrapped_source':self.be.wrap(r['source_text']),'steps':steps,'output':steps[-1]['output'],'score':steps[-1]['score'],'endpoint_joint':steps[-1]['score']['joint_ok'],'trajectory_joint':all(s['score']['joint_ok'] for s in steps),'timing':timing};f.write(json.dumps(record)+'\n')
   print('evaluated',self.be.name,group,mode,path,flush=True)
 def controls(self,rows):
  be=self.be;folder=ROOT/f'outputs/{be.name}';folder.mkdir(parents=True,exist_ok=True);cachefile=folder/'reconstruction_cache.jsonl';cache={r['source_text']:r for r in [json.loads(l) for l in cachefile.read_text().splitlines()]} if cachefile.exists() else {}
  def ensure(texts):
   missing=list(dict.fromkeys(t for t in texts if t not in cache));valid=[]
   for text in missing:
    n=len(be.tok(be.wrap(text),add_special_tokens=not be.chat)['input_ids'])
    if n<=be.cfg['source_length']:valid.append(text);continue
    rec=dict(source_text=text,wrapped_input=be.wrap(text),source_tokens=n,output='',ended=False,token_ids=[],generated_tokens=0,hit_limit=False,special_token_ids=[],input_mask_length=n,execution_error='actual input exceeds frozen cap; not truncated',timing={})
    cache[text]=rec
    with cachefile.open('a') as f:f.write(json.dumps(rec)+'\n')
   missing=valid
   for i in range(0,len(missing),be.cfg.get('generation_batch_size',4)):
    batch=missing[i:i+be.cfg.get('generation_batch_size',4)];ss,timing,lens=be.infer(batch,None,[])
    with cachefile.open('a') as f:
     for text,s,n in zip(batch,ss,lens):
      r=dict(source_text=text,wrapped_input=be.wrap(text),source_tokens=n,**s[0],timing=timing);cache[text]=r;f.write(json.dumps(r)+'\n')
  # Deterministic reconstruction cached only for identical actual input strings.
  ensure([t for r in rows for t in [r['source_text']]+r['gold_step_texts']]);current=[r['source_text'] for r in rows]
  for k in range(3):ensure(current);current=[cache[t]['output'] for t in current if not cache[t].get('execution_error')]
  result=[]
  for r in rows:
   w=self.worlds[r['record_id']]
   for kind,texts,frames in [('source',[r['source_text']],[r['frames'][0]]),('target_stages',r['gold_step_texts'],r['frames'][1:])]:
    steps=[dict(**cache[t],frame=c,score=metric(cache[t]['output'],c,w,cache[t]['ended'])) for t,c in zip(texts,frames)]
    result.append(dict(record_id=r['record_id'],row_id=r['row_id'],split=r['split'],path=r['path'],kind=kind,steps=steps,endpoint_joint=steps[-1]['score']['joint_ok'],trajectory_joint=all(s['score']['joint_ok'] for s in steps)))
   text=r['source_text'];steps=[];stopped=None
   for k in range(3):
    out=stopped or cache[text]
    if out.get('execution_error'):stopped=out
    c=r['frames'][0];steps.append(dict(**out,frame=c,score=metric(out['output'],c,w,out['ended'])));text=out['output'];result.append(dict(record_id=r['record_id'],row_id=r['row_id'],split=r['split'],path=r['path'],kind=f'reconstruction_{k+1}',steps=steps.copy(),endpoint_joint=steps[-1]['score']['joint_ok'],trajectory_joint=all(s['score']['joint_ok'] for s in steps)))
  write(f'outputs/{be.name}/controls.jsonl',result)
 def rules(self,rows):
  if (ROOT/'outputs/text_rule.jsonl').exists():return
  out=[]
  for r in rows:
   text=r['source_text'];steps=[];t=time.perf_counter()
   for c0,c1 in zip(r['frames'],r['frames'][1:]):text,err=text_rule(text,c0,c1);steps.append(dict(output=text,frame=c1,score=metric(text,c1,self.worlds[r['record_id']],True),rule_error=err))
   out.append({**r,'model':'Text-rule','group':'rule','mode':'rule','steps':steps,'endpoint_joint':steps[-1]['score']['joint_ok'],'trajectory_joint':all(s['score']['joint_ok'] for s in steps),'cpu_seconds':time.perf_counter()-t})
  write('outputs/text_rule.jsonl',out)
def bart_check(be):
 audit=[]
 for group,root in [('G1',V2),('G3',V3)]:
  eds=new_editors(be.d);eds.load_state_dict(torch.load(root/f'checkpoints/{group}/best.pt',weights_only=True));file=V3/f'outputs/confirmation_{group}.jsonl'
  old=[json.loads(l) for l in file.read_text().splitlines()]
  for path in ['T_plus_first','plus_plus']:
   rs=[r for r in old if r['path']==path and r['mode']=='latent_chain' and r['split']=='test_iid'][:16];ss,timing,lens=be.infer([r['source_text'] for r in rs],eds,rs[0]['operations'])
   for r,steps in zip(rs,ss):
    match=[s['output'] for s in steps]==[s['output'] for s in r['steps']];audit.append(dict(group=group,row_id=r['row_id'],match=match,actual=[s['output'] for s in steps],archived=[s['output'] for s in r['steps']]))
 write('calibration/BART/reproduction.jsonl',audit);assert all(r['match'] for r in audit),'BART archive mismatch, not eligible for paired comparison'
 dump('calibration/BART/admission.json',dict(status='reused_reference',passed=True,selected_wrapper='A',exact_reproductions=len(audit),N=len(audit)))
def main(name):
 started=time.monotonic();be=Backend(name);ev=Eval(be)
 if name=='BART':bart_check(be)
 else:assert json.loads((ROOT/f'calibration/{name}/admission.json').read_text())['passed']
 roots={g:(V2 if g=='G1' else V3) if name=='BART' else ROOT/f'checkpoints/{name}' for g in ['G1','G3']}
 paths={g:(roots[g]/f'checkpoints/{g}/best.pt' if name=='BART' else roots[g]/g/'best.pt') for g in roots};frozen={g:digest(p) for g,p in paths.items()};lockfile=ROOT/f'checkpoints/{name}/evaluation_lock.json'
 if lockfile.exists():assert json.loads(lockfile.read_text())['checkpoints']==frozen
 else:dump(f'checkpoints/{name}/evaluation_lock.json',dict(checkpoints=frozen,interface_hash=digest(ROOT/f'models/{name}_interface.json'),data_lock_hash=digest(ROOT/'data/lock.json')))
 rows=[r for split in ['test_iid','test_template_ood'] for kind in ['atomic','chains'] for r in read(f'data/{split}_{kind}.jsonl')];ev.rules(rows);ev.controls(rows)
 for group,path in paths.items():
  be.editor_hash=frozen[group]
  eds=new_editors(be.d);eds.load_state_dict(torch.load(path,weights_only=True));ev.neural([r for r in rows if len(r['operations'])==1],eds,group,'latent_chain',f'outputs/{name}/{group}.jsonl')
  for mode in ['latent_chain','decode_reencode']:ev.neural([r for r in rows if len(r['operations'])>1],eds,group,mode,f'outputs/{name}/{group}.jsonl')
 dump(f'evaluation/{name}_complete.json',dict(completed=True,wall_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated(),rows_per_group=3732))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model');main(p.parse_args().model)
