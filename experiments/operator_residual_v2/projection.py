"""Exp3: no-donor every-step projection, original and reencoding cost references."""
import time
from core import *

def correct(hidden,mask,fit,method):
    q=fit['q'];coordinates=hidden@q
    if method=='mean':predicted=fit['mean'].expand_as(coordinates)
    else:
        centered=hidden-fit['x_mean'];comp=centered-project(centered,q)
        predicted=fit['mean']+comp@fit['beta']
    return torch.where(mask.bool()[...,None],hidden+(predicted-coordinates)@q.T,hidden)

def mahal(h,m,q,st):
    d=pool(h,m)@q-st['mean'];return ((d@st['inverse'])*d).sum(1)

@torch.no_grad()
def benchmark(eng,ed,fit,worlds):
    render,gold,advance,states,score=semantics();results=[]
    seq=read(ROOT/'protocol.json')['sequences']['primary'];worlds=worlds[:8]
    for repeat in range(3):
        for method in (['none','ridge','reencode'] if repeat%2==0 else ['reencode','ridge','none']):
            torch.cuda.synchronize();start=time.perf_counter();h,m=eng.encode([render(w,0,0) for w in worlds]);current=None;state=0
            tokens=0
            for k,op in enumerate(seq):
                if method=='reencode' and k:h,m=eng.encode(current)
                h=ed[op](h,m);state=advance('time',state,op)
                if method=='ridge':h=correct(h,m,fit['projector'],'ridge')
                if method=='reencode' or k==4:
                    output=eng.decode(h,m);current=[r['text'] for r in output];tokens+=sum(r['generated_tokens'] for r in output)
            torch.cuda.synchronize()
            results.append(dict(repeat=repeat,method=method,length=5,batch_size=8,seconds=time.perf_counter()-start,
                                encoder_calls=5 if method=='reencode' else 1,decoder_calls=5 if method=='reencode' else 1,
                                generated_tokens=tokens,outputs=output,diagnostic_decoding_excluded=True))
    write('results/projection_cost.jsonl',results)

@torch.no_grad()
def main():
    protocol=verify_protocol();eng,load_editor=engine();render,gold,advance,states,score=semantics();worlds=rows(ROOT/'eval_worlds.jsonl')
    for seed in SEEDS:
        ed=load_editor(eng,task(seed)['checkpoint']);ed.requires_grad_(False);fit=load(ROOT/f'local/fit_s{seed}.pt')
        def device(x):
            if isinstance(x,dict):return {k:device(v) for k,v in x.items()}
            return x.cuda() if torch.is_tensor(x) else x
        fit=device(fit);methods=[('none',None),('mean',None),('ridge',None),('reencode',None)]+[('random_ridge',r) for r in protocol['random_seeds']]
        for template in protocol['eval_templates']:
            for seq_name,seq in protocol['sequences'].items():
                for start in range(0,len(worlds),16):
                    name=f'results/projection/s{seed}_t{template}_{seq_name}_b{start:03d}.jsonl'
                    if (ROOT/name).exists():continue
                    ws=worlds[start:start+16];natural,m=eng.encode([render(w,0,template) for w in ws]);out=[]
                    for method,random_seed in methods:
                        h=natural.clone();mm=m.clone();current_text=None;state=0;success=[[] for _ in ws];records=[[] for _ in ws];patch_cost=0.;encoder_calls=1
                        for step,op in enumerate(seq):
                            if step and method=='reencode':h,mm=eng.encode(current_text);encoder_calls+=1
                            h=ed[op](h,mm);state=advance('time',state,op)
                            before=pool(h,mm).cpu();distance=mahal(h,mm,fit['q'],fit['canonical_stats']).cpu().tolist()
                            random_distance=torch.stack([mahal(h,mm,fit['random_projectors'][r]['q'],fit['random_stats'][r]) for r in protocol['random_seeds']]).mean(0).cpu().tolist()
                            torch.cuda.synchronize();t=time.perf_counter()
                            if method in ('mean','ridge'):h=correct(h,mm,fit['projector'],method)
                            elif method=='random_ridge':h=correct(h,mm,fit['random_projectors'][random_seed],'ridge')
                            torch.cuda.synchronize();patch_cost+=time.perf_counter()-t
                            result=evaluate(eng,h,mm,ws,state,template);current_text=[r['text'] for r in result]
                            after=pool(h,mm).cpu()
                            for i,r in enumerate(result):
                                success[i].append(r['score']['success']);records[i].append(dict(step=step+1,state=state,output=r,
                                   mahal=distance[i],random_mahal=random_distance[i],pool_before=before[i].tolist(),pool_after=after[i].tolist()))
                        for i,w in enumerate(ws):
                            out.append(dict(seed=seed,world_id=w['world_id'],template=template,sequence=seq_name,method=method,random_seed=random_seed,
                                            step_successes=success[i],steps=records[i],projection_seconds_per_world=patch_cost/len(ws),encoder_calls=encoder_calls,
                                            prediction_is_reference_free=True,full_trajectory=[all(success[i][:k]) for k in range(1,6)]))
                    write(name,out)
                    print('projection',seed,template,seq_name,start+len(ws),flush=True)
        assert all(p.grad is None for p in eng.model.parameters())
        if seed==42:benchmark(eng,ed,fit,worlds)
        del ed
    write('results/projection.jsonl',[r for p in sorted((ROOT/'results/projection').glob('*.jsonl')) for r in rows(p)])
    dump('results/projection_complete.json',dict(resources=eng.resources(),training_updates=0,protocol_sha256=sha(ROOT/'protocol.json'),code_sha256=sha(__file__)))

if __name__=='__main__':main()
