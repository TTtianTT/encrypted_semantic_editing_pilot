"""Exploratory validation atomic and pure latent trajectories; never opens test."""
import torch
from .common import *
from .engine import editors,render,advance

@torch.no_grad()
def run(eng,folder):
    task=eng.task;seed=task['seed'];lock=read(ROOT/'configs/PLAIN_CHECKPOINT_LOCK.json');item=next(r for r in lock['checkpoints'] if r['seed']==seed)
    assert sha(item['path'])==item['sha256']
    plain=editors(eng.d,seed);plain.load_state_dict(torch.load(item['path'],map_location='cuda',weights_only=False)['editor']);plain.eval()
    models={'Original':eng.ed,'Plain':plain}
    worlds=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='validation']
    old=rows(Path(item['run_folder'])/'Plain/Plain_validation.jsonl');current={(r['world_id'],r['state'],r['source']):r['current'] for r in old}
    sequences=[['plus','minus','plus','minus','plus'],['plus','plus','minus','minus','plus']]
    atomics=[];tracks=[]
    for i,w in enumerate(worlds):
        atomic_path=folder/(w['world_id']+'_editing.jsonl');chain_path=folder/(w['world_id']+'_trajectories.jsonl');marker=folder/(w['world_id']+'_COMPLETE.json')
        if marker.exists():atomics.extend(rows(atomic_path));tracks.extend(rows(chain_path));continue
        cache=torch.load(Path(item['run_folder'])/'source_worlds'/(w['world_id']+'.pt'),map_location='cpu',weights_only=False)
        record=[];chains=[]
        for state in range(-3,4):
            for op in ('plus','minus'):
                try:next_state=advance('time',state,op)
                except ValueError:continue
                for source in ('natural','history'):
                    r=cache[(w['world_id'],state,source)];h=r['hidden'][None].cuda();m=r['mask'][None].cuda();edited=eng.ed[op](h,m);pred=eng.evaluate(edited,m,w,next_state)
                    record.append(dict(world_id=w['world_id'],split='validation',seed=seed,method='Original',source=source,state=state,operation=op,current_correct=current[(w['world_id'],state,source)]['score']['success'],prediction=pred,joint=pred['score']['success'],target=pred['score']['target'],content=pred['score']['preserved'],parseable=pred['score']['parseable'],EOS=pred['ended'],update_norm=float((edited-h).float()[m.bool()].norm()),donor_used=False,gold_text_given_to_editor=False,test_time_backward=False))
        r=cache[(w['world_id'],0,'natural')];h0=r['hidden'][None].cuda();m=r['mask'][None].cuda()
        for order,sequence in enumerate(sequences):
            for direction in ('forward','inverse'):
                ops=sequence if direction=='forward' else ['minus' if op=='plus' else 'plus' for op in sequence]
                for method,ed in models.items():
                    h=h0.clone();state=0;steps=[]
                    for step,op in enumerate(ops,1):
                        state=advance('time',state,op);h=ed[op](h,m);pred=eng.evaluate(h,m,w,state)
                        steps.append(dict(step=step,operation=op,state=state,prediction=pred))
                    chains.append(dict(world_id=w['world_id'],split='validation',seed=seed,method=method,source='natural_start',order=order,direction=direction,steps=steps,length_success={str(length):all(s['prediction']['score']['success'] for s in steps[:length]) for length in (1,2,3,5)},latent_only=True,gold_state_replacements=0,donor_used=False))
        jsonl(atomic_path,record);jsonl(chain_path,chains);dump(marker,dict(world_id=w['world_id'],completed=True));atomics.extend(record);tracks.extend(chains)
        if (i+1)%8==0:print('validation trajectories',seed,i+1,flush=True)
    chain_summary=[]
    for method in models:
        rs=[r for r in tracks if r['method']==method]
        for length in (1,2,3,5):
            good=sum(r['length_success'][str(length)] for r in rs)
            all_orders_good=sum(all(r['length_success'][str(length)] for r in rs if r['world_id']==w['world_id']) for w in worlds)
            chain_summary.append(dict(method=method,length=length,complete_numerator=good,trajectory_denominator=len(rs),independent_worlds=len(worlds),all_orders_world_numerator=all_orders_good))
    return dict(passed=True,worlds=64,seed=seed,split='validation',scientific_status='EXPLORATORY_VALIDATION_ONLY',Original_atomic_joint=sum(r['joint'] for r in atomics),Original_atomic_denominator=len(atomics),trajectories=chain_summary,main_methods=['Original','Plain'],test_evaluations=0,extra_test_inputs=False,pure_latent=True,resources=eng.resources())
