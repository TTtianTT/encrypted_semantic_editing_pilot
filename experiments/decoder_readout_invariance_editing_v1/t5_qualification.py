"""Original T5Gemma SAME_TEXT re-audit, independent of old next-fork rule."""
import torch
from .common import *
from .engine import render
from .readout import pairs,distribution

@torch.no_grad()
def run(eng,folder):
    assert eng.name=='t5gemma'
    worlds=rows(ROOT/'configs/worlds.jsonl');ws=[w for w in worlds if w['split']=='train'][:16]+[w for w in worlds if w['split']=='validation'][:16]
    counts={};scores=[];bridges=[]
    for i,w in enumerate(ws):
        ps,_,_=pairs(eng,w,folder);split=w['split'];counts.setdefault(split,dict(scanned_worlds=0,qualified_worlds=0,qualified_pairs=0));counts[split]['scanned_worlds']+=1;counts[split]['qualified_worlds']+=bool(ps);counts[split]['qualified_pairs']+=len(ps)
        for r,a,b,m in ps:
            ids=torch.tensor(r['a']['token_ids'],device='cuda')[None];la=eng.logits(a,m,decoder_ids=ids[:,:-1]);lb=eng.logits(b,m,decoder_ids=ids[:,:-1])
            scores.extend(dict(world_id=w['world_id'],split=split,source_pair=r['source_pair'],delta_norm=r['delta_norm'],**p) for p in distribution(la,lb,ids[:,1:]))
            for op,state in [('plus',-1),('minus',1)]:
                na=eng.evaluate(eng.ed[op](a,m),m,w,state);nb=eng.evaluate(eng.ed[op](b,m),m,w,state)
                bridges.append(dict(world_id=w['world_id'],split=split,source_pair=r['source_pair'],operation=op,panel_A=True,panel_B=na['score']['success']!=nb['score']['success'],a=na,b=nb))
        jsonl(folder/'readout_scores.jsonl',scores);jsonl(folder/'bridge.jsonl',bridges)
        print('T5 SAME_TEXT re-audit',i+1,counts,flush=True)
    return dict(passed=True,status='COMPLETED' if scores else 'NOT_ESTIMABLE',worlds=len(ws),counts=counts,readout_token_rows=len(scores),max_JS=max((r['JS'] for r in scores),default=None),max_delta_norm=max((r['delta_norm'] for r in scores),default=None),fork_records=sum(r['panel_B'] for r in bridges),fork_denominator=len(bridges),qualification_requires_next_fork=False,confirmation_test_scanned=0,independent_confirmation_status='NOT_RUN_TEST_SEALED',resources=eng.resources())
