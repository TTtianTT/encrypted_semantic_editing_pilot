"""Post-hoc controls on the exact 0 -> -1 transition of the failed projection."""
from shared import *
from projection import correct
from probes import prediction

@torch.no_grad()
def main():
    p=verify();spec=read(ROOT/'initial_projection_controls_protocol.json')
    assert all(sha(ROOT/k)==v for k,v in spec['sources'].items())
    eng,load_editor=frozen_engine();worlds=rows(V2/'eval_worlds.jsonl');render=semantics()[0]
    source=canonical('eval',0,0);target=canonical('eval',0,-1);probes=device(load(ROOT/'local/probes.pt'))
    assert torch.equal(source['m'],target['m'])
    for seed in SEEDS:
        ed=load_editor(eng,previous.task(seed)['checkpoint']);ed.requires_grad_(False)
        fit=device(load(V2/f'local/fit_s{seed}.pt')['projector']);probe=probes[seed];q=probe['q']
        for start in range(0,len(worlds),8):
            name=f'results/initial_control_shards/s{seed}_b{start:03d}.jsonl'
            if (ROOT/name).exists():continue
            ws=worlds[start:start+8];stop=start+len(ws);m=source['m'][start:stop].cuda();bad=ed['plus'](source['h'][start:stop].cuda(),m);good=target['h'][start:stop].cuda()
            delta=correct(bad,m,fit,'ridge')-bad;norm=delta.flatten(1).norm(dim=1)
            conditions=[('none',None,torch.zeros_like(delta)),('ridge_delta',None,delta)]
            for rs in p['random_seeds']:
                g=torch.Generator(device='cuda').manual_seed(rs+seed*100);rq=previous.random_basis(768,4,rs+seed*100).cuda()
                full=torch.randn(delta.shape,generator=g,device='cuda')*m[...,None]
                rand4=project(torch.randn(delta.shape,generator=g,device='cuda'),rq)*m[...,None]
                for name2,d in [('random_full',full),('random4',rand4)]:
                    d=d*(norm/d.flatten(1).norm(dim=1))[:,None,None]
                    assert torch.allclose(d.flatten(1).norm(dim=1),norm,rtol=1e-5,atol=1e-5);conditions.append((name2,rs,d))
            records=[]
            for context,base in [('edited',bad),('canonical',good)]:
                # The original asymmetry also involved a smaller displacement
                # on canonical states; keep that operation as a labelled control.
                cs=conditions+[('own_ridge',None,correct(base,m,fit,'ridge')-base)]
                for ci in range(0,len(cs),2):
                    batch=cs[ci:ci+2];h=torch.cat([base+d for _,_,d in batch]);mm=torch.cat([m]*len(batch));ww=ws*len(batch)
                    cur=evaluate(eng,h,mm,ww,-1,0);nxt=evaluate(eng,ed['plus'](h,mm),mm,ww,-2,0)
                    for k,(condition,rs,d) in enumerate(batch):
                        for j,w in enumerate(ws):
                            ix=k*len(ws)+j;records.append(dict(panel='control',seed=seed,world_id=w['world_id'],context=context,condition=condition,random_seed=rs,
                                source_state=0,target_state=-1,norm=float(d[j].norm()),matched_ridge_norm=float(norm[j]),
                                current_exact=cur[ix]['text']==render(w,-1,0),current=cur[ix],next=nxt[ix]))
                z=pool(base,m);fl=prediction(z,probe['full']);sl=prediction(z@q,probe['S']);cl=prediction(z-project(z,q),probe['complement'])
                centered=z-probe['full']['mean'];sc=project(centered,q)@probe['full']['beta'];pc=(centered-project(centered,q))@probe['full']['beta']
                assert torch.allclose(sc+pc+probe['full']['bias'],fl,atol=2e-5)
                for j,w in enumerate(ws):records.append(dict(panel='probe',seed=seed,world_id=w['world_id'],context=context,source_state=0,target_state=-1,
                    full_prediction=int(fl[j].argmax())-3,S_prediction=int(sl[j].argmax())-3,complement_prediction=int(cl[j].argmax())-3,
                    full_margin=float(fl[j,2]-fl[j,3]),S_margin=float(sl[j,2]-sl[j,3]),complement_margin=float(cl[j,2]-cl[j,3]),
                    shared_S_contribution=float(sc[j,2]-sc[j,3]),shared_complement_contribution=float(pc[j,2]-pc[j,3]),shared_bias=float(probe['full']['bias'][2]-probe['full']['bias'][3])))
            write(name,records);print('initial projection controls',seed,stop,flush=True)
        del ed
    write('results/initial_projection_controls.jsonl',(r for f in sorted((ROOT/'results/initial_control_shards').glob('*.jsonl')) for r in stream(f)))
    dump('results/initial_projection_controls_complete.json',dict(training_updates=0,post_hoc=True,resources=eng.resources(),design_sha256=sha(ROOT/'initial_projection_controls_protocol.json')))

if __name__=='__main__':main()
