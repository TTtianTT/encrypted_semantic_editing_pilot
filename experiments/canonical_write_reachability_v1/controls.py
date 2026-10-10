"""Displacements matched to edited-state ridge correction, in two contexts."""
from shared import *
from projection import correct

@torch.no_grad()
def main():
    p=verify();eng,load_editor=frozen_engine();allrecords=[]
    for seed in SEEDS:
        ed=load_editor(eng,previous.task(seed)['checkpoint']);ed.requires_grad_(False)
        fit=device(load(V2/f'local/fit_s{seed}.pt')['projector']);pairs=previous.selections(seed)
        for start in range(0,len(pairs),8):
            shard=f'results/shards/controls_s{seed}_b{start:03d}.jsonl'
            if (ROOT/shard).exists():continue
            ps=pairs[start:start+8];bad,good,m=previous.patch_pair_batch(ps);ws=[r['world'] for r in ps]
            delta=correct(bad,m,fit,'ridge')-bad;norm=delta.flatten(1).norm(dim=1);conditions=[('none',None,torch.zeros_like(delta)),('ridge_delta',None,delta)]
            for rs in p['random_seeds']:
                g=torch.Generator(device='cuda').manual_seed(rs+seed*100)
                rf=torch.randn(delta.shape,generator=g,device='cuda')*m[...,None]
                q=previous.random_basis(768,4,rs+seed*100).cuda()
                rr=project(torch.randn(delta.shape,generator=g,device='cuda'),q)*m[...,None]
                for name,d in [('random_full',rf),('random4',rr)]:
                    d=d*(norm/d.flatten(1).norm(dim=1))[:,None,None]
                    assert torch.allclose(d.flatten(1).norm(dim=1),norm,rtol=1e-5,atol=1e-5)
                    assert not d[m==0].any();conditions.append((name,rs,d))
            records=[]
            for context,base in [('edited',bad),('canonical',good)]:
                for ci in range(0,len(conditions),2):
                    batch=conditions[ci:ci+2];h=torch.cat([base+d for _,_,d in batch]);mm=torch.cat([m]*len(batch));ww=ws*len(batch)
                    current=evaluate(eng,h,mm,ww,0,0);nxt=evaluate(eng,ed['plus'](h,mm),mm,ww,-1,0)
                    for k,(condition,rs,d) in enumerate(batch):
                        for j,pair in enumerate(ps):
                            ix=k*len(ps)+j;records.append(dict(seed=seed,world_id=pair['world_id'],context=context,condition=condition,random_seed=rs,
                                norm=float(d[j].norm()),matched_ridge_norm=float(norm[j]),current_exact=current[ix]['text']==pair['current_text'],
                                current=current[ix],next=nxt[ix]))
            write(shard,records);print('matched controls',seed,start+len(ps),flush=True)
        del ed
    write('results/matched_controls.jsonl',(r for f in sorted((ROOT/'results/shards').glob('controls_*.jsonl')) for r in stream(f)))
    dump('results/controls_complete.json',dict(training_updates=0,resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
