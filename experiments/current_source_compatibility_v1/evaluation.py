"""Unfiltered two-step tests and legal long trajectories; checkpoints never selected here."""
import torch,time
from engine import *

@torch.no_grad()
def natural(eng,ed,rs,path,identity=False):
    if path.exists():return rows(path)
    out=[];ws=worldmap()
    for op in ('plus','minus'):
     group=[r for r in rs if r['operation']==op]
     for i in range(0,len(group),8):
      batch=group[i:i+8];h,m=eng.cached([r['source'] for r in batch]);pred=eng.decode(h if identity else ed[op](h,m),m)
      for r,p,mask in zip(batch,pred,m):
       g=gold(ws[r['world_id']],r['state'],r['template']) if identity else r['gold']
       out.append(dict(id=f"{r['world_id']}_t{r['template']}_s{r['state']}_{op}",world_id=r['world_id'],template=r['template'],state=r['state'],operation=op,source=r['source'],target=r['source'] if identity else r['target'],gold=g,mask_length=int(mask.sum()),**result(p,g,ws[r['world_id']])))
    jsonl(path,out);return out

@torch.no_grad()
def continuation(eng,ed,records,inputs,firsts,source,path):
    if path.exists():return rows(path)
    out=[];ws=worldmap()
    for op in ('plus','minus'):
     group=[r for r in records if r['b']==op]
     for i in range(0,len(group),8):
      batch=group[i:i+8]
      if source=='gold_reencode':h,m=eng.cached([r['current_text'] for r in batch])
      elif source=='actual_reencode':h,m=eng.cached([firsts[r['prefix_id']]['prediction'] for r in batch])
      else:h=torch.stack([inputs[r['prefix_id']]['h'] for r in batch]).cuda();m=torch.stack([inputs[r['prefix_id']]['m'] for r in batch]).cuda()
      preds=eng.decode(ed[op](h,m),m)
      for r,p,mask in zip(batch,preds,m):
       first=firsts[r['prefix_id']];res=result(p,r['target_gold'],ws[r['world_id']]);ok=first['score']['success']
       out.append(dict(id=r['id'],prefix_id=r['prefix_id'],world_id=r['world_id'],template=r['template'],initial_state=r['initial_state'],current_state=r['current_state'],a=r['a'],b=r['b'],target_state=r['target_state'],target=r['target_text'],gold=r['target_gold'],source=source,first_prediction=first['prediction'],first_score=first['score'],first_success=ok,full2=bool(ok and res['score']['success']),mask_length=int(mask.sum()),**res))
    jsonl(path,out);return out

@torch.no_grad()
def long_paths(eng,ed,paths,mode,folder):
    ws=worldmap();allrows=[]
    # Each shard is an entire batch/trajectory; timeout repeats only its incomplete batch.
    groups=collections.defaultdict(list)
    for r in paths:groups[(r['template'],tuple(r['operations']))].append(r)
    for gi,(_,group) in enumerate(sorted(groups.items())):
     for i in range(0,len(group),8):
      target=folder/f'{mode}_{gi:02}_{i:03}.jsonl'
      if target.exists():allrows+=rows(target);continue
      batch=group[i:i+8];h,m=eng.cached([r['original_text'] for r in batch]);full=[True]*len(batch);first_failure=[None]*len(batch);prev=[True]*len(batch);out=[]
      for k,op in enumerate(batch[0]['operations']):
       if k and mode=='gold_reencode':h,m=eng.cached([render(ws[r['world_id']],r['states'][k-1],r['template']) for r in batch])
       elif k and mode=='actual_reencode':h,m=eng.cached(texts)
       before=getattr(eng,'encode_calls',0);h=ed[op](h,m);pred=eng.decode(h,m)
       if mode=='latent':assert getattr(eng,'encode_calls',0)==before,'Latent path reencoded'
       texts=[p['text'] for p in pred]
       for j,(r,p,mask) in enumerate(zip(batch,pred,m)):
        g=gold(ws[r['world_id']],r['states'][k],r['template']);res=result(p,g,ws[r['world_id']]);success=res['score']['success'];full[j]=full[j] and success
        if not success and first_failure[j] is None:first_failure[j]=k+1
        out.append(dict(id=r['id'],world_id=r['world_id'],template=r['template'],initial_state=r['initial_state'],family=r['family'],operations=r['operations'],step=k+1,operation=op,current_state=r['states'][k],method=mode,previous_success=prev[j],full_success=full[j],first_failure=first_failure[j],mask_length=int(mask.sum()),gold=g,target=render(ws[r['world_id']],r['states'][k],r['template']),latent_reencoded=False if mode=='latent' else None,**res));prev[j]=success
      jsonl(target,out);allrows+=out
    return allrows

def first_records(folder):return {r['prefix_id']:r for r in rows(folder/'prefix_quality.jsonl')}

def evaluate(eng,seed,ed,cp,folder,baseline=False):
    folder.mkdir(parents=True,exist_ok=True);done=folder/'complete.json'
    if done.exists():return
    records=rows(ROOT/'data/test_pairs.jsonl');basefolder=ROOT/f'local/preflight/s{seed}';started=time.monotonic()
    for label,datafile in (('old_natural','test_core'),('ood_natural','test_expression')):natural(eng,ed,rows(ROOT/f'data/{datafile}.jsonl'),folder/f'{label}.jsonl')
    producer=load(eng,checkpoint(seed));fixed,_=cache(eng,producer,records,basefolder/'fixed_T0','F',digest(checkpoint(seed)));del producer
    useed={42:43,43:44,44:42}[seed];producer=load(eng,checkpoint(useed));external,_=cache(eng,producer,records,basefolder/'fixed_U','U',digest(checkpoint(useed)));del producer
    if baseline:selfinputs=fixed;selffirst=first_records(basefolder/'fixed_T0')
    else:
      selfinputs,_=cache(eng,ed,records,folder/'self_prefix','SELF',digest(cp));selffirst=first_records(folder/'self_prefix')
    for name,inputs,first in [('fixed_T0',fixed,first_records(basefolder/'fixed_T0')),('U',external,first_records(basefolder/'fixed_U')),('self',selfinputs,selffirst),('gold_reencode',None,selffirst),('actual_reencode',None,selffirst)]:continuation(eng,ed,records,inputs,first,name,folder/f'continuation_{name}.jsonl')
    if baseline:
      a={r['id']:r for r in rows(folder/'continuation_self.jsonl')};g={r['id']:r for r in rows(folder/'continuation_gold_reencode.jsonl')}
      cohort=[dict(id=r['id'],world_id=r['world_id'],template=r['template'],qualified=bool(a[r['id']]['first_success'] and g[r['id']]['score']['success']),first_success=a[r['id']]['first_success'],gold_next_success=g[r['id']]['score']['success']) for r in records];jsonl(folder/'fixed_diagnostic.jsonl',cohort)
    paths=rows(ROOT/'data/long_paths.jsonl')
    for mode in ('latent','gold_reencode','actual_reencode'):long_paths(eng,ed,paths,mode,folder/'trajectories')
    dump(done,dict(seed=seed,checkpoint=str(cp),checkpoint_sha=digest(cp),finished_utc=now(),wall_seconds=time.monotonic()-started,outputs={str(p.relative_to(folder)):digest(p) for p in sorted(folder.rglob('*.jsonl'))}))

import collections
