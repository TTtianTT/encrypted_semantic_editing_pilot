from collections import defaultdict
import torch
from common import *
from semantics import gold,render,advance,states
from evaluator import score,normalize

@torch.no_grad()
def atomic(eng,ed,rs,worlds,path,identity=False):
    output=[]
    # Groups homogeneous operation, batch for throughput without changing state.
    for op in ('plus','minus'):
        group=[r for r in rs if r['operation']==op]
        for offset in range(0,len(group),8):
            batch=group[offset:offset+8];h,m=eng.cached([r['source'] for r in batch])
            decoded=eng.decode(h if identity else ed[op](h,m),m)
            for r,pred,mask in zip(batch,decoded,m):
                w=worlds[r['world_id']];g=gold(w,r['state'],r['template'],r['symbolic']) if identity else r['gold']
                output.append(dict(**{k:v for k,v in r.items() if k!='gold'},gold=g,prediction=pred['text'],score=score(pred['text'],g,w,pred['ended']),mask_length=int(mask.sum()),exact=pred['text'].strip()==(r['source'] if identity else r['target']).strip(),kind='reconstruction' if identity else 'atomic'))
    jsonl(path,output);return output

def rates(rows):
    cells=defaultdict(list)
    for r in rows:cells[(r['state'],r['operation'])].append(r['score']['success'])
    return dict(n=len(rows),success=sum(r['score']['success'] for r in rows),rate=sum(r['score']['success'] for r in rows)/len(rows),cells=[dict(state=s,operation=op,n=len(v),success=sum(v),rate=sum(v)/len(v)) for (s,op),v in sorted(cells.items())],min_cell=min(sum(v)/len(v) for v in cells.values()))

@torch.no_grad()
def gold_next(eng,ed,rs,worlds,path):
    derived=[]
    for r in rs:
        w=worlds[r['world_id']];current=r['gold']['state'];op=r['operation']
        try:nxt=advance(w['domain'],current,op)
        except ValueError:continue
        derived.append(dict(**{k:v for k,v in r.items() if k not in ('source','target','gold','state')},state=current,source=r['target'],target=render(w,nxt,r['template'],r['symbolic']),gold=gold(w,nxt,r['template'],r['symbolic'])))
    return atomic(eng,ed,derived,worlds,path)

def admission(eng,ed,rs,worlds,folder):
    identity=atomic(eng,ed,rs,worlds,folder/'reconstruction.jsonl',True)
    edited=atomic(eng,ed,rs,worlds,folder/'atomic.jsonl')
    nextrows=gold_next(eng,ed,rs,worlds,folder/'gold_next.jsonl')
    i,e,n=rates(identity),rates(edited),rates(nextrows);g=eng.cfg['gate']
    passed=i['rate']>=g['reconstruction'] and e['rate']>=g['atomic'] and e['min_cell']>=g['min_cell'] and n['rate']>=g['atomic'] and n['min_cell']>=g['min_cell']
    result=dict(passed=passed,reconstruction=i,atomic=e,gold_next=n,thresholds=g)
    dump(folder/'admission.json',result);return result
