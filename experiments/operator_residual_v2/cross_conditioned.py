"""Cross-seed PCA repair after fixing recipient read coordinates.

This separates failed full-S transfer from a possible recipient-specific read
component barrier. It does not claim that a shared backbone-only space exists.
"""
from core import *

@torch.no_grad()
def main():
    verify_protocol();eng,load_editor=engine();render,gold,advance,states,score=semantics();worlds=rows(ROOT/'eval_worlds.jsonl');out=[]
    fitted={s:load(ROOT/f'local/fit_s{s}.pt')['q'].cuda() for s in SEEDS}
    for seed in SEEDS:
        ed=load_editor(eng,task(seed)['checkpoint']);ed.requires_grad_(False);r=basis(ed['plus'].v.weight.cpu()).cuda()
        for template in (0,3):
            for start in range(0,len(worlds),8):
                ws=worlds[start:start+8];ref,m=eng.encode([render(w,0,template) for w in ws]);src,sm=eng.encode([render(w,1,template) for w in ws]);assert torch.equal(m,sm)
                bad=ed['plus'](src,m);delta=(ref-bad)*m[...,None];read=project(delta,r)*m[...,None]
                for source_seed,s in fitted.items():
                    component=project(delta,s)*m[...,None];perp=component-project(component,r);changed=bad+read+perp
                    assert torch.equal(changed[m==0],bad[m==0])
                    assert float(ed['plus'].v((changed-ref)*m[...,None]).abs().max())<1e-5
                    cur=evaluate(eng,changed,m,ws,0,template);nxt=evaluate(eng,ed['plus'](changed,m),m,ws,-1,template)
                    for i,w in enumerate(ws):out.append(dict(target_seed=seed,basis_seed=source_seed,template=template,world_id=w['world_id'],
                        current=cur[i],next=nxt[i],current_exact=cur[i]['text']==render(w,0,template),
                        joint=cur[i]['score']['success'] and cur[i]['text']==render(w,0,template) and nxt[i]['score']['success'],
                        read_fixed=True,patch_norm=float((read[i]+perp[i]).norm())))
            print('cross-seed, read-conditioned',seed,template,flush=True)
    write('results/cross_conditioned.jsonl',out)
    dump('results/cross_conditioned_complete.json',dict(resources=eng.resources(),training_updates=0,code_sha256=sha(__file__),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
