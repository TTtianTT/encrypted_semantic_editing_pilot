"""Reproduce G4's final-mean gold Ridge probe for re-encoded states."""
import json,sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import RidgeClassifier

HERE=Path(__file__).resolve().parent
G4=HERE.parent/'algebraic_generalization_v1'
V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(V3))
from common import frame,render
from engine import Engine
import renderer_v1

renderer_v1.REL[5]='in five days' # Same probe-only extension as G4.
OFFSETS=list(range(-4,6))

def worldfile(split):return [json.loads(s) for s in (V3/f'data/{split}_worlds.jsonl').read_text().splitlines()]
def examples(worlds):
    out=[]
    for w in worlds:
        for off in OFFSETS:
            f=frame(w,off)
            if f['view_date']<w['record_date']:continue
            for person in ['first','third']:
                ff=dict(f,perspective=person)
                out.append(dict(world_id=w['record_id'],offset=off,text=render(w,ff)))
    return out
@torch.no_grad()
def encode(eng,items):
    xs=[]
    for start in range(0,len(items),32):
        h,m,_=eng.encode([x['text'] for x in items[start:start+32]])
        xs.append(((h*m[...,None]).sum(1)/m.sum(1)[:,None]).float().cpu().numpy())
        if start%1024==0:print('gold probe examples',start,'/',len(items),flush=True)
    return np.concatenate(xs)

def main():
    eng=Engine()
    train=examples(worldfile('train'));dev=examples(worldfile('dev'))
    ids=json.loads((HERE/'provenance.json').read_text())['world_ids']
    testworlds={w['record_id']:w for s in ['test_iid','test_template_ood'] for w in worldfile(s)}
    test=examples([testworlds[w] for s in ['test_iid','test_template_ood'] for w in ids[s]])
    x=encode(eng,train);xd=encode(eng,dev);xt=encode(eng,test)
    y=np.array([r['offset'] for r in train]);yd=np.array([r['offset'] for r in dev]);yt=np.array([r['offset'] for r in test])
    probe=RidgeClassifier(alpha=10.).fit(x,y)
    dp=probe.predict(xd);tp=probe.predict(xt)
    byclass=[]
    for off in OFFSETS:
        for split,actual,pred in [('dev',yd,dp),('test_gold',yt,tp)]:
            mask=actual==off
            byclass.append(dict(split=split,offset=off,n=int(mask.sum()),accuracy=float(np.mean(pred[mask]==actual[mask])) if mask.any() else None))
    payload=dict(train_worlds=480,dev_worlds=80,test_worlds=106,train_examples=len(train),dev_examples=len(dev),test_examples=len(test),
                 dev_accuracy=float(np.mean(dp==yd)),test_gold_accuracy=float(np.mean(tp==yt)),by_class=byclass,
                 alpha=10.,representation='final encoder mean',training='gold train worlds only',
                 no_g5_chain_fit=True)
    (HERE/'gold_probe_validation.json').write_text(json.dumps(payload,indent=2)+'\n')
    np.savez_compressed(HERE/'gold_probe_weights.npz',coef=probe.coef_,intercept=probe.intercept_,classes=probe.classes_)
    vectors=torch.load(HERE/'pooled_representations.pt',map_location='cpu',weights_only=False)
    keys=list(vectors);rows=[]
    for start in range(0,len(keys),512):
        kk=keys[start:start+512]
        a=np.stack([vectors[k]['edited'].numpy() for k in kk]);b=np.stack([vectors[k]['reset'].numpy() for k in kk]);g=np.stack([vectors[k]['gold'].numpy() for k in kk])
        pa=probe.predict(a);pb=probe.predict(b);pg=probe.predict(g)
        for i,k in enumerate(kk):rows.append(dict(key=k,edited_offset=int(pa[i]),reset_offset=int(pb[i]),gold_offset=int(pg[i])))
    with (HERE/'gold_probe_predictions.jsonl').open('w') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    print('gold probe',payload['dev_accuracy'],payload['test_gold_accuracy'],flush=True)

if __name__=='__main__':main()
