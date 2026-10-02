"""Frozen behavior evaluation. Pure latent branch never reencodes predictions."""
import torch
from common import *
from train import load_editor
from evaluate import atomic,admission
from sources import source_cache,covered_states
from semantics import gold,render,advance,states
from evaluator import score,normalize

def trajectories(domain):
    if domain=='time':initial_plus,initial_minus=3,-3
    elif domain=='emotion':initial_plus,initial_minus=0,4
    else:initial_plus=initial_minus=0
    length=4 if domain=='emotion' else 5
    return [('forward',initial_plus,['plus']*length),('reverse',initial_minus,['minus']*length),('inverse',2 if domain=='emotion' else 0,['plus','minus','plus','minus','plus'])]

@torch.no_grad()
def rollout(eng,ed,world_list,template,path):
    output=[];d=world_list[0]['domain']
    for name,start,ops in trajectories(d):
        for mode in ('latent','decode_reencode','gold_reencode'):
            for offset in range(0,len(world_list),8):
                batch=world_list[offset:offset+8];initial=[render(w,start,template) for w in batch];h,m=eng.cached(initial);current=start;previous=[True]*len(batch);full=[True]*len(batch);last_text=initial
                for k,op in enumerate(ops,1):
                    if k>1 and mode=='decode_reencode':
                        # Actual emitted output only, no cleanup or oracle repair.
                        try:h,m=eng.encode(last_text)
                        except AssertionError:
                            for i,w in enumerate(batch):output.append(dict(world_id=w['world_id'],template=template,trajectory=name,mode=mode,step=k,state=current,operation=op,prediction='',gold=None,score=dict(success=False,target=False,preserved=False,scope=False,parseable=False,grammar=False,ended=False),previous_correct=previous[i],full_success=False,technical_error='decoded input cap exceeded',kind='trajectory'))
                            break
                    if k>1 and mode=='gold_reencode':h,m=eng.cached([render(w,current,template) for w in batch])
                    current=advance(d,current,op);h=ed[op](h,m);decoded=eng.decode(h,m);last_text=[p['text'] for p in decoded]
                    for i,(w,pred,mask) in enumerate(zip(batch,decoded,m)):
                        g=gold(w,current,template);sc=score(pred['text'],g,w,pred['ended']);full[i]=full[i] and sc['success']
                        output.append(dict(world_id=w['world_id'],template=template,trajectory=name,mode=mode,step=k,state=current,operation=op,prediction=pred['text'],gold=g,score=sc,previous_correct=previous[i],full_success=full[i],mask_length=int(mask.sum()),kind='trajectory'))
                        previous[i]=sc['success']
    jsonl(path,output)

@torch.no_grad()
def matrix(eng,ed,caches,worlds,heldout,covered,path,cohort_path):
    bysource={source:{(r['world_id'],r['state']):r for r in cache} for source,cache in caches.items()}
    pairs=[];cohort=[];first=next(iter(bysource.values()))
    # Establish matching BEFORE any receiver continuation output is computed.
    for key in sorted(first):
        group=[bysource[source][key] for source in ('P','Q','U')];correct=all(r['current_score']['success'] for r in group);same_text=len({normalize(r['text']) for r in group})==1;same_mask=all(torch.equal(group[0]['mask'],r['mask']) for r in group[1:]);same_depth=len({r['source_depth'] for r in group})==1
        reasons=[]
        if not correct:reasons.append('one_or_more_current_semantically_incorrect')
        if not same_text:reasons.append('current_full_text_mismatch')
        if not same_mask:reasons.append('mask_or_length_mismatch')
        if not same_depth:reasons.append('edited_depth_mismatch')
        pair_status={}
        for lhs,rhs in [('P','Q'),('P','U'),('Q','U')]:
            x,y=bysource[lhs][key],bysource[rhs][key]
            pair_status[lhs+'_'+rhs]=x['current_score']['success'] and y['current_score']['success'] and normalize(x['text'])==normalize(y['text']) and torch.equal(x['mask'],y['mask']) and x['source_depth']==y['source_depth']
        cohort.append(dict(world_id=key[0],state=key[1],common_match=not reasons,reasons=reasons,pair_matches=pair_status,candidate=True))
    jsonl(cohort_path,cohort);locked={ (r['world_id'],r['state']):r for r in cohort }
    for source,cache in caches.items():
        for op in ('plus','minus'):
            legal=[]
            for r in cache:
                try:nxt=advance(worlds[r['world_id']]['domain'],r['state'],op)
                except ValueError:continue
                legal.append((r,nxt))
            for offset in range(0,len(legal),8):
                batch=legal[offset:offset+8];h=torch.stack([r['hidden'] for r,n in batch]).cuda();m=torch.stack([r['mask'] for r,n in batch]).cuda();decoded=eng.decode(ed[op](h,m),m)
                for (r,nxt),pred in zip(batch,decoded):
                    w=worlds[r['world_id']];g=gold(w,nxt,r['template']);matched=locked[(r['world_id'],r['state'])]
                    pairs.append(dict(world_id=r['world_id'],state=r['state'],operation=op,template=r['template'],source=source,source_seen=source in ('P','Q'),state_seen=r['state'] in covered,state_heldout=r['state']==heldout,current_prediction=r['text'],current_score=r['current_score'],prediction=pred['text'],gold=g,score=score(pred['text'],g,w,pred['ended']),common_match=matched['common_match'],pair_matches=matched['pair_matches'],source_depth=r['source_depth'],mask_length=int(r['mask'].sum()),kind='source_matrix'))
    jsonl(path,pairs)

def evaluate_all(eng,task,folder,published,worlds,index,conditions):
    d=task['domain'];test_worlds=[w for w in worlds.values() if w['split']=='test']
    # Each immutable output shard is checkpoint/config associated; completed
    # shards are never redone because scores are low.
    roles=['P']+[f'{c}_{h}' for h,v in conditions.items() if v['status']=='trained' for c in ('N','S','M')]
    source_sets={}
    for template in (0,2):
        caches={}
        for source in ('P','Q','U'):
            cp=Path(index[source]['path']);ed=load_editor(eng,cp)
            caches[source]=source_cache(eng,ed,test_worlds,states(d),template,folder/f'sources/{source}_test_t{template}.pt',cp)
        source_sets[template]=caches
    for role in roles:
        ed=load_editor(eng,Path(index[role]['path']));outdir=published/'outputs'/role;outdir.mkdir(parents=True,exist_ok=True)
        for kind in ('core','expression','challenge'):
            p=outdir/f'atomic_{kind}.jsonl'
            if not p.exists():atomic(eng,ed,rows(ROOT/f'data/{d}/test_{kind}.jsonl'),worlds,p)
        for template in (0,2):
            p=outdir/f'trajectory_t{template}.jsonl'
            if not p.exists():rollout(eng,ed,test_worlds,template,p)
        splitindices=range(2) if role=='P' else [int(role[-1])]
        for hi in splitindices:
            heldout=eng.cfg['holdouts'][d][hi];single,multi=covered_states(d,heldout)
            covered=[single] if role.startswith('S') else multi if role.startswith('M') else []
            for template,caches in source_sets.items():
                p=outdir/f'matrix_h{hi}_t{template}.jsonl'
                if not p.exists():matrix(eng,ed,caches,worlds,heldout,covered,p,outdir/f'cohort_h{hi}_t{template}.jsonl')
        # Per editor immutable output index ties every prediction to a checkpoint.
        dump(outdir/'manifest.json',dict(checkpoint=index[role],config_sha=digest(ROOT/'config.json'),files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in sorted(outdir.glob('*.jsonl'))]))
    P=load_editor(eng,Path(index['P']['path']))
    identitypath=published/'test_reconstruction.jsonl'
    if not identitypath.exists():atomic(eng,P,rows(ROOT/f'data/{d}/test_core.jsonl'),worlds,identitypath,True)
    # Mechanism work follows completed behavior; it cannot change checkpoint or
    # eligibility. Probes are descriptive cross-source readouts, not interventions.
    from probe import run_probe
    run_probe(eng,folder,published,worlds,index,source_sets[0])
