"""Validate projection estimators on held-out canonical states before interpreting failure."""
from core import *
from projection import correct

@torch.no_grad()
def main():
    verify_protocol();eng,_=engine();render,gold,advance,states,score=semantics();worlds=rows(ROOT/'eval_worlds.jsonl');out=[]
    random_seed=read(ROOT/'protocol.json')['random_seeds'][0]
    for seed in SEEDS:
        f=load(ROOT/f'local/fit_s{seed}.pt')
        def device(x):return {k:device(v) for k,v in x.items()} if isinstance(x,dict) else x.cuda() if torch.is_tensor(x) else x
        fit=device(f)
        for template in (0,2,3):
            for state in (0,-1):
                for start in range(0,len(worlds),16):
                    ws=worlds[start:start+16];h,m=eng.encode([render(w,state,template) for w in ws]);baseline=evaluate(eng,h,m,ws,state,template)
                    for method in ('mean','ridge','random_ridge'):
                        p=fit['random_projectors'][random_seed] if method=='random_ridge' else fit['projector'];changed=correct(h,m,p,'mean' if method=='mean' else 'ridge')
                        assert torch.equal(changed[m==0],h[m==0])
                        result=evaluate(eng,changed,m,ws,state,template)
                        q=p['q'];err=((changed-h)@q).square();mse=(err*m[...,None]).sum((1,2))/(m.sum(1)*4)
                        for i,w in enumerate(ws):out.append(dict(seed=seed,template=template,state=state,method=method,world_id=w['world_id'],
                                                              baseline=baseline[i],output=result[i],success=result[i]['score']['success'],
                                                              exact_preservation=result[i]['text']==baseline[i]['text'],coordinate_mse=float(mse[i])))
                print('canonical control',seed,template,state,flush=True)
    write('results/canonical_control.jsonl',out)
    dump('results/canonical_control_complete.json',dict(resources=eng.resources(),training_updates=0,code_sha256=sha(__file__),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
