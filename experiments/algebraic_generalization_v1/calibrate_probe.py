"""Fit linear readers on G3/repair train-world states of length at most two."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import torch
from sklearn.linear_model import RidgeClassifier

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(V3))
from run import CFG, SubspaceEditor, frame, render, advance, get_worlds, pooled, Engine, new_editors, renderer_v1, write_json, write_jsonl

OFFSETS=[-2,0,1,3,5]
ATTRS=['offset','person','author','recipient','action','object','quantity','record_status','polarity']


def cases(worlds):
    out=[]
    for w in worlds:
        for off in OFFSETS:
            f=frame(w,off)
            if f['view_date']<w['record_date']: continue
            for person in ('first','third'):
                ff=dict(f,perspective=person)
                out.append((w,ff,render(w,ff)))
    return out


@torch.no_grad()
def features(eng, cases, g3, repair):
    xs=[];meta=[]
    for start in range(0,len(cases),16):
        batch=cases[start:start+16]
        h,m,_=eng.encode([z[2] for z in batch])
        for group,ed in [('G3',g3['T_plus']),('repair',repair['T_plus'])]:
            z=h
            frames=[b[1] for b in batch]
            for k in range(3):
                if k:
                    z=ed(z,m)
                    frames=[advance(f,'T_plus') for f in frames]
                xs.append(pooled(z,m).float().cpu().numpy())
                for (w,_,_),f in zip(batch,frames):
                    label=dict(group=group,step=k,world_id=w['record_id'],offset=(__import__('datetime').date.fromisoformat(w['event_date'])-__import__('datetime').date.fromisoformat(f['view_date'])).days,person=f['perspective'])
                    for attr in ATTRS[2:]: label[attr]=w[attr]
                    meta.append(label)
        if start%512==0:print('calibration features',start,'/',len(cases),flush=True)
    return np.concatenate(xs),meta


def predict_latents(probe, group):
    path=HERE/f'{group}_latents.pt'
    data=torch.load(path,map_location='cpu',weights_only=False)
    keys=list(data)
    results=[]
    for i in range(0,len(keys),256):
        kk=keys[i:i+256]
        xx=np.stack([(d['latent'].float()*d['mask'][:,None]).sum(0).numpy()/int(d['mask'].sum()) for d in (data[k] for k in kk)])
        pp={a:model.predict(xx).tolist() for a,model in probe.items()}
        for j,key in enumerate(kk):results.append(dict(key=key,group=group,prediction={a:pp[a][j] for a in pp}))
    return results


def main():
    eng=Engine();g3=new_editors();g3.load_state_dict(torch.load(V3/'checkpoints/G3/best.pt',weights_only=True))
    state=torch.load(HERE/'repair.pt',weights_only=True)
    R=state['T_plus.R'].cuda()
    repair=torch.nn.ModuleDict({op:SubspaceEditor(R,g3[op]) for op in ['T_plus','T_minus']})
    repair.load_state_dict(state)
    tx,tm=features(eng,cases(get_worlds('train')),g3,repair)
    dx,dm=features(eng,cases(get_worlds('dev')),g3,repair)
    probe={};report=[];weight={}
    for a in ATTRS:
        y=np.array([m[a] for m in tm]);yd=np.array([m[a] for m in dm])
        model=RidgeClassifier(alpha=10.).fit(tx,y);probe[a]=model
        pred=model.predict(dx)
        for group in ['G3','repair']:
            for step in range(3):
                ids=[i for i,m in enumerate(dm) if m['group']==group and m['step']==step]
                report.append(dict(group=group,step=step,attribute=a,n=len(ids),dev_accuracy=float(np.mean(pred[ids]==yd[ids]))))
        weight[a+'_coef']=model.coef_;weight[a+'_intercept']=model.intercept_;weight[a+'_classes']=model.classes_
    np.savez_compressed(HERE/'calibrated_probe_weights.npz',**weight)
    write_json('calibrated_probe_validation.json',dict(training_worlds=len(get_worlds('train')),dev_worlds=len(get_worlds('dev')),
                                                       training_cases=len(tm),dev_cases=len(dm),max_trained_steps=2,
                                                       source_offsets=OFFSETS,models=['G3','repair'],accuracy=report))
    predictions=predict_latents(probe,'G3')+predict_latents(probe,'repair')
    write_jsonl('calibrated_probe_predictions.jsonl',predictions)
    # Source h0 is required for exact latent inverse, using the same input/mask as evaluation.
    source={}
    for split in ['test_iid','test_template_ood']:
        from run import eligible_worlds
        ww=eligible_worlds(split)
        for i in range(0,len(ww),16):
            batch=ww[i:i+16]
            hh,mm,_=eng.encode([render(w,frame(w,1)) for w in batch])
            for j,w in enumerate(batch):source[f'{split}/{w["record_id"]}']=dict(latent=hh[j].half().cpu(),mask=mm[j].cpu())
    torch.save(source,HERE/'source_latents.pt')
    print('calibrated probe complete',len(predictions),flush=True)

if __name__=='__main__':main()
