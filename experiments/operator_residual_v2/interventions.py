"""Exp1 PCA component repair/injection with matched random doses; Exp2 visibility."""
from core import *

@torch.no_grad()
def attribution(eng,ed,seed,rs,start):
    protocol=read(ROOT/'protocol.json');bad,good,m=patch_pair_batch(rs);worlds=[r['world'] for r in rs]
    s=old_basis(seed).cuda();q=basis(ed['plus'].v.weight.cpu()).cuda();e=(bad-good)*m[...,None]
    es=project(e,s)*m[...,None];er=project(es,q)*m[...,None];ep=es-er
    assert float(ed['plus'].v(ep).abs().max())<1e-5
    assert float((ed['plus'](good+ep,m)-ed['plus'](good,m)-ep).abs().max())<2e-6
    components=dict(S=es,S_R=er,S_perp=ep)
    randoms={}
    for group in components:
        for random_seed in protocol['random_seeds']:
            rq=random_basis(768,4,random_seed+seed*100, q.cpu() if group!='S' else None, group=='S_perp').cuda()
            randoms[group,random_seed]=matched_random(e,rq,m,components[group].flatten(1).norm(dim=1))
    conditions=[]
    for direction in ('repair','injection'):
        base=bad if direction=='repair' else good;sign=-1 if direction=='repair' else 1
        for group,c in components.items():
            for alpha in protocol['alphas']:
                for random_seed in [None]+protocol['random_seeds']:
                    component=c if random_seed is None else randoms[group,random_seed]
                    h=torch.where(m.bool()[...,None],base+sign*alpha*component,base)
                    assert torch.equal(h[m==0],base[m==0])
                    spec=dict(direction=direction,component=group,alpha=alpha,random_seed=random_seed,
                              norm=(alpha*component).flatten(1).norm(dim=1).cpu().tolist(),
                              matched_real_norm=(alpha*c).flatten(1).norm(dim=1).cpu().tolist())
                    conditions.append((spec,h))
    output=[]
    # Two condition blocks per generation batch; fixed batch audit below.
    for ci in range(0,len(conditions),2):
        cs=conditions[ci:ci+2];h=torch.cat([x[1] for x in cs]);mm=torch.cat([m]*len(cs));ww=worlds*len(cs)
        current=evaluate(eng,h,mm,ww,0);nxt=evaluate(eng,ed['plus'](h,mm),mm,ww,-1)
        for k,(spec,_) in enumerate(cs):
            for j,r in enumerate(rs):
                ix=k*len(rs)+j
                output.append(dict(seed=seed,world_id=r['world_id'],direction=spec['direction'],component=spec['component'],alpha=spec['alpha'],
                                   random_seed=spec['random_seed'],norm=spec['norm'][j],matched_real_norm=spec['matched_real_norm'][j],
                                   current_exact=current[ix]['text']==r['current_text'],current_success=current[ix]['score']['success'],
                                   next_success=nxt[ix]['score']['success'],current=current[ix],next=nxt[ix]))
        if start==0 and ci==0:
            single=evaluate(eng,ed['plus'](h[:1],mm[:1]),mm[:1],ww[:1],-1)
            assert single[0]['text']==nxt[0]['text'],'Mixed-batch/single generation mismatch'
    write(f'results/attribution/s{seed}_b{start:03d}.jsonl',output)
    return components,randoms,bad,good,m,worlds

@torch.no_grad()
def visibility(eng,ed,seed,rs,start,components,randoms,bad,good,m,worlds):
    protocol=read(ROOT/'protocol.json');render,gold,advance,states,score=semantics();output=[]
    for context,state,base in [('pre',0,good),('post',-1,ed['plus'](good,m))]:
        texts=[render(w,state,0) for w in worlds];reference,labels=logits(eng,base,m,texts)
        for alpha in protocol['alphas']:
            for random_seed in [None]+protocol['random_seeds']:
                c=components['S_perp'] if random_seed is None else randoms['S_perp',random_seed]
                perturbed=base+alpha*c
                changed,y=logits(eng,perturbed,m,texts);assert torch.equal(labels,y)
                metrics=distribution(reference,changed,y)
                for j,(r,metric) in enumerate(zip(rs,metrics)):
                    output.append(dict(seed=seed,world_id=r['world_id'],context=context,alpha=alpha,random_seed=random_seed,
                                       perturbation_norm=float((alpha*c[j]).norm()),**metric))
    write(f'results/visibility/s{seed}_b{start:03d}.jsonl',output)

@torch.no_grad()
def generalization(eng,ed,seed):
    protocol=read(ROOT/'protocol.json');worlds=rows(ROOT/'eval_worlds.jsonl');render,gold,advance,states,score=semantics()
    fitted={s:load(ROOT/f'local/fit_s{s}.pt')['q'].cuda() for s in SEEDS};out=[]
    for template in protocol['eval_templates']:
        for start in range(0,len(worlds),8):
            ws=worlds[start:start+8];g,mg=eng.encode([render(w,0,template) for w in ws]);h,m=eng.encode([render(w,1,template) for w in ws]);b=ed['plus'](h,m)
            current_g=evaluate(eng,g,mg,ws,0,template);current_b=evaluate(eng,b,m,ws,0,template)
            next_g=evaluate(eng,ed['plus'](g,mg),mg,ws,-1,template);next_b=evaluate(eng,ed['plus'](b,m),m,ws,-1,template)
            same=[bool(torch.equal(m[j],mg[j])) for j in range(len(ws))]
            for source_seed,q in list(fitted.items())+[('full',None)]:
                delta=(g-b)*m[...,None];component=delta if q is None else project(delta,q)*m[...,None]
                changed=torch.where(m.bool()[...,None],b+component,b)
                ix=[j for j,s in enumerate(same) if s]
                cur=evaluate(eng,changed[ix],m[ix],[ws[j] for j in ix],0,template) if ix else []
                nxt=evaluate(eng,ed['plus'](changed[ix],m[ix]),m[ix],[ws[j] for j in ix],-1,template) if ix else []
                lookup={j:k for k,j in enumerate(ix)}
                for j,w in enumerate(ws):
                    k=lookup.get(j);out.append(dict(target_seed=seed,basis_seed=source_seed,world_id=w['world_id'],template=template,
                                                same_mask=same[j],baseline_current=current_b[j],reference_current=current_g[j],
                                                baseline_next=next_b[j],reference_next=next_g[j],
                                                patched_current=None if k is None else cur[k],patched_next=None if k is None else nxt[k],
                                                status='MASK_MISMATCH_NOT_PATCHED' if k is None else 'evaluated',
                                                eligible_mechanism=current_g[j]['score']['success'] and current_b[j]['score']['success'] and current_g[j]['text']==current_b[j]['text'] and next_g[j]['score']['success'] and not next_b[j]['score']['success'] and same[j]))
        print('generalization',seed,template,flush=True)
    write(f'results/generalization_s{seed}.jsonl',out)

@torch.no_grad()
def main():
    protocol=verify_protocol();assert (ROOT/'results/fit_complete.json').exists();eng,load_editor=engine()
    for seed in SEEDS:
        ed=load_editor(eng,task(seed)['checkpoint']);ed.requires_grad_(False);rs=selections(seed)
        for start in range(0,len(rs),8):
            if (ROOT/f'results/attribution/s{seed}_b{start:03d}.jsonl').exists() and (ROOT/f'results/visibility/s{seed}_b{start:03d}.jsonl').exists():continue
            state=attribution(eng,ed,seed,rs[start:start+8],start)
            visibility(eng,ed,seed,rs[start:start+8],start,*state)
            print('PCA attribution/visibility',seed,start+len(rs[start:start+8]),flush=True)
        if not (ROOT/f'results/generalization_s{seed}.jsonl').exists():generalization(eng,ed,seed)
        assert all(p.grad is None for p in eng.model.parameters())
        del ed
    for phase in ('attribution','visibility'):
        write(f'results/{phase}.jsonl',[r for p in sorted((ROOT/f'results/{phase}').glob('*.jsonl')) for r in rows(p)])
    write('results/generalization.jsonl',[r for s in SEEDS for r in rows(ROOT/f'results/generalization_s{s}.jsonl')])
    dump('results/interventions_complete.json',dict(resources=eng.resources(),training_updates=0,protocol_sha256=sha(ROOT/'protocol.json'),code_sha256=sha(__file__)))

if __name__=='__main__':main()
