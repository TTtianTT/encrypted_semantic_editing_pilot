"""Frozen encoder/editor extraction. Linear/statistical fitting is a separate CPU phase."""
from datetime import date,timedelta
from core import *

@torch.no_grad()
def main():
    protocol=verify_protocol();eng,load_editor=engine();render,gold,advance,states,score=semantics()
    train=rows(ROOT/'train_worlds.jsonl');alltokens=[];allpool=[];metas=[];position_sum=torch.zeros(192,768,dtype=torch.float64);position_count=torch.zeros(192,dtype=torch.float64)
    natural={}
    for template in protocol['canonical_fit_templates']:
        for state in protocol['canonical_fit_states']:
            hs=[];ms=[]
            for start in range(0,len(train),16):
                ws=train[start:start+16];h,m=eng.encode([render(w,state,template) for w in ws]);hc,mc=h.cpu(),m.cpu()
                alltokens.append(hc[mc.bool()]);allpool.append(pool(hc,mc));hs.append(hc);ms.append(mc)
                position_sum+=(hc.double()*mc[...,None]).sum(0);position_count+=mc.sum(0)
                metas.extend(dict(world_id=w['world_id'],state=state,template=template) for w in ws)
            if template==0 and state in (0,1):natural[state]=(torch.cat(hs),torch.cat(ms))
    save('local/canonical.pt',dict(tokens=torch.cat(alltokens),pooled=torch.cat(allpool),metas=metas,
                                    position_mean=(position_sum/position_count.clamp_min(1)[:,None]).float(),position_count=position_count))
    h0,m0=natural[0];h1,m1=natural[1];assert torch.equal(m0,m1)
    for seed in SEEDS:
        ed=load_editor(eng,task(seed)['checkpoint']);ed.requires_grad_(False);diffs=[];qual=[]
        for start in range(0,len(train),8):
            ws=train[start:start+8];g=h0[start:start+8].cuda();b=ed['plus'](h1[start:start+8].cuda(),m1[start:start+8].cuda());m=m0[start:start+8].cuda()
            cg=evaluate(eng,g,m,ws,0);cb=evaluate(eng,b,m,ws,0);ng=evaluate(eng,ed['plus'](g,m),m,ws,-1);nb=evaluate(eng,ed['plus'](b,m),m,ws,-1)
            for i,w in enumerate(ws):
                eligible=cg[i]['score']['success'] and cb[i]['score']['success'] and cg[i]['text']==cb[i]['text'] and ng[i]['score']['success'] and not nb[i]['score']['success']
                qual.append(dict(seed=seed,world_id=w['world_id'],eligible=eligible,current_good=cg[i],current_bad=cb[i],next_good=ng[i],next_bad=nb[i]))
                if eligible:diffs.append((b[i]-g[i])[m[i].bool()].cpu())
        assert len(diffs)>=40,'Insufficient training-world failure pairs; do not search held-out cases'
        save(f'local/training_residual_s{seed}.pt',dict(tokens=torch.cat(diffs),worlds=[r['world_id'] for r in qual if r['eligible']]))
        write(f'results/training_qualification_s{seed}.jsonl',qual);print('training-pair extraction',seed,len(diffs),flush=True)
        del ed
    # Independent-format canonical statistics for the historical G4 prediction panel.
    v3=REPO/'experiments/reference_frame_pilot_v3';sys.path.insert(0,str(v3))
    from renderer_v1 import render as render_g4
    ws=rows(v3/'data/train_worlds.jsonl');texts=[];meta=[]
    for w in ws:
        for off in range(-4,5):
            view=(date.fromisoformat(w['event_date'])-timedelta(days=off)).isoformat()
            if view<w['record_date']:continue
            texts.append(render_g4(w,dict(view_date=view,perspective='first')));meta.append(dict(world_id=w['record_id'],offset=off))
    pooled=[]
    for start in range(0,len(texts),32):
        h,m=eng.encode(texts[start:start+32]);pooled.append(pool(h,m).cpu())
    save('local/g4_canonical_pooled.pt',dict(pooled=torch.cat(pooled),meta=meta))
    dump('results/extraction_complete.json',dict(protocol_sha256=sha(ROOT/'protocol.json'),resources=eng.resources(),training_updates=0,
                                                files={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'local').glob('*.pt'))}))

if __name__=='__main__':main()
