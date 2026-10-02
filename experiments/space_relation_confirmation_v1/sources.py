import torch
from collections import Counter
from common import *
from semantics import gold,render,advance,states
from evaluator import score,normalize

def incoming(domain,current):
    for op in ('plus','minus'):
        reverse='minus' if op=='plus' else 'plus'
        try:previous=advance(domain,current,reverse)
        except ValueError:continue
        assert advance(domain,previous,op)==current
        return previous,op
    raise ValueError('State has no legal incoming operation')

@torch.no_grad()
def source_cache(eng,ed,worlds,current_states,template,path,checkpoint):
    manifest=path.with_suffix('.json')
    if path.exists() and manifest.exists():
        m=read(manifest);assert m['checkpoint_sha']==digest(checkpoint) and m['cache_sha']==digest(path)
        return torch.load(path,map_location='cpu',weights_only=False)
    result=[]
    for current in current_states:
        previous,op=incoming(worlds[0]['domain'],current)
        for i in range(0,len(worlds),8):
            batch=worlds[i:i+8];text=[render(w,previous,template) for w in batch];h,m=eng.cached(text);edited=ed[op](h,m);out=eng.decode(edited,m)
            for w,t,pred,x,y in zip(batch,text,out,edited,m):
                g=gold(w,current,template)
                result.append(dict(world_id=w['world_id'],state=current,template=template,source_text=t,current_gold=render(w,current,template),current_frame=g,source_operation=op,source_depth=1,hidden=x.cpu(),mask=y.cpu(),text=pred['text'],ended=pred['ended'],current_score=score(pred['text'],g,w,pred['ended'])))
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');torch.save(result,tmp);tmp.replace(path)
    public=[{k:v for k,v in r.items() if k not in ('hidden','mask')} for r in result]
    jsonl(manifest.with_suffix('.jsonl'),public)
    dump(manifest,dict(checkpoint=str(checkpoint),checkpoint_sha=digest(checkpoint),cache=str(path),cache_sha=digest(path),depth=1,template=template,states=current_states,world_ids=[w['world_id'] for w in worlds],correct=sum(r['current_score']['success'] for r in result),candidates=len(result),mask_policy='original incoming text mask; no decoded text refeed'))
    return result

def supplement_pool(cache,worlds,current_states):
    pool={op:[] for op in ('plus','minus')};coverage=Counter();reject=Counter()
    for r in cache:
        if r['state'] not in current_states:continue
        if not r['current_score']['success']:reject['current_incorrect_or_unresolved']+=1;continue
        w=worlds[r['world_id']]
        for op in ('plus','minus'):
            try:nxt=advance(w['domain'],r['state'],op)
            except ValueError:continue
            pool[op].append(dict(world_id=w['world_id'],state=r['state'],operation=op,template=r['template'],symbolic=False,source=render(w,r['state'],r['template']),target=render(w,nxt,r['template']),hidden=r['hidden'],mask=r['mask']))
            coverage[(r['state'],op)]+=1
    expected=[]
    for s in current_states:
        for op in ('plus','minus'):
            try:advance(next(iter(worlds.values()))['domain'],s,op)
            except ValueError:continue
            expected.append((s,op))
    result=dict(cells=[dict(state=s,operation=op,qualifying=coverage[(s,op)]) for s,op in expected],rejections=dict(reject),feasible=all(coverage[k]>=8 for k in expected))
    return pool,result

def covered_states(domain,heldout):
    single=2 if domain=='emotion' else 0
    multi={'time':[-1,0,1],'space':[0,2],'emotion':[0,2,4],'person':[s for s in range(3) if s!=heldout]}[domain]
    assert heldout not in multi and single in multi
    return single,multi
