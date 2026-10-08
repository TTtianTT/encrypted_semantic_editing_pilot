"""Independent evaluator. Main methods see only H, mask, operation."""
import time
import torch
from .common import *
from .engine import editors,render,advance
from .training import source_record
from .readout import pairs,distribution,token_sites

@torch.no_grad()
def run(eng,folder):
    lock=read(ROOT/'configs/FINAL_TEST_LOCK.json');assert lock['all_seeds_locked'] and lock['independent_test_unseal_stage']=='S4'
    auth=read(ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json');proposal=read(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json')
    assert auth['approved'] and auth['proposal_sha256']==sha(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json')
    assert lock['checkpoint_lock_sha256']==sha(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')
    seed=eng.task['seed'];models={'Original':eng.ed}
    for item in lock['checkpoints']:
        if item['seed']!=seed:continue
        assert sha(item['path'])==item['sha256'];ed=editors(eng.d,seed);ed.load_state_dict(torch.load(item['path'],map_location='cuda',weights_only=False)['editor']);models[item['method']]=ed.eval()
    all_test=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='test_iid']
    assert len(all_test)==128 and set(proposal['eligible_worlds'])|set(proposal['excluded_worlds'])=={w['world_id'] for w in all_test}
    ws=[w for w in all_test if w['world_id'] in proposal['eligible_worlds']];assert len(ws)==123
    jsonl(folder/'pre_exposure_exclusions.jsonl',[dict(world_id=w['world_id'],status='NA_PRIOR_EXPOSURE',reason='counterfactual encoder exposure before S4',not_zero_failure=True) for w in all_test if w['world_id'] in proposal['excluded_worlds']])
    records=[];trajectories=[];qualification=[];readouts=[]
    sequences=[['plus','minus','plus','minus','plus'],['plus','plus','minus','minus','plus']]
    for wi,w in enumerate(ws):
        marker=folder/(w['world_id']+'_COMPLETE.json')
        if marker.exists():continue
        sources={}
        for state in range(-3,4):
            for source in ('natural','history'):
                r=source_record(eng,w,state,source);h=r['hidden'][None].cuda();m=r['mask'][None].cuda();sources[(state,source)]=(h,m,eng.evaluate(h,m,w,state))
        world_records=[];world_trajectories=[]
        for state in range(-3,4):
            for operation in ('plus','minus'):
                try:next_state=advance('time',state,operation)
                except ValueError:continue
                for source in ('natural','history'):
                    h,m,current=sources[(state,source)]
                    for name,ed in models.items():
                        torch.cuda.synchronize();start=time.perf_counter();edited=ed[operation](h,m);torch.cuda.synchronize();latency=time.perf_counter()-start
                        pred=eng.evaluate(edited,m,w,next_state)
                        world_records.append(dict(world_id=w['world_id'],split='test_iid',seed=seed,model=eng.name,method=name,source=source,state=state,operation=operation,current_correct=current['score']['success'],current=current,prediction=pred,joint=pred['score']['success'],target=pred['score']['target'],content=pred['score']['preserved'],parseable=pred['score']['parseable'],EOS=pred['ended'],exact_match=pred['text']==render(w,next_state),update_norm=float((edited-h).float()[m.bool()].norm()),relative_update_norm=float((edited-h).float()[m.bool()].norm()/(h.float()[m.bool()].norm()+1e-9)),editor_latency_seconds=latency,editor_forward_calls=1,donor_used=False,target_text_given_to_editor=False,test_time_backward=False,peak_allocated_bytes=torch.cuda.max_memory_allocated()))
        for order,sequence in enumerate(sequences):
            for direction in ('forward','inverse'):
                ops=sequence if direction=='forward' else ['minus' if o=='plus' else 'plus' for o in sequence]
                for name,ed in models.items():
                    h,m,_=sources[(0,'natural')];state=0;all_success=True;steps=[]
                    for step,op in enumerate(ops,1):
                        state=advance('time',state,op);h=ed[op](h,m);pred=eng.evaluate(h,m,w,state);all_success=all_success and pred['score']['success'];steps.append(dict(step=step,operation=op,state=state,prediction=pred,complete_trajectory_success=all_success))
                    world_trajectories.append(dict(world_id=w['world_id'],seed=seed,method=name,source='natural_start',order=order,direction=direction,steps=steps,length_success={str(length):all(s['prediction']['score']['success'] for s in steps[:length]) for length in (1,2,3,5)},latent_only=True,gold_state_replacements=0))
        # S1/S2 confirmation qualification is only now unsealed, using the unchanged A rules.
        ps,_,_=pairs(eng,w,folder)
        from .test_mechanism import confirm
        confirmed=confirm(eng,w,ps,folder,wi)
        jsonl(folder/(w['world_id']+'_editing.jsonl'),world_records);jsonl(folder/(w['world_id']+'_trajectories.jsonl'),world_trajectories)
        dump(marker,dict(world_id=w['world_id'],complete=True,seed=seed,editing_rows=len(world_records),trajectories=len(world_trajectories),panel_A_pairs=len(ps),mechanism_confirmation=confirmed))
        if (wi+1)%8==0:print('S4',seed,wi+1,len(ws),flush=True)
    return dict(passed=True,worlds=len(ws),original_scan_worlds=128,excluded_prior_exposure=5,endpoint='explicit amended unexposed123, not original128',methods=list(models),source_weights={'natural':.5,'history':.5},OOD_status='UNAVAILABLE',donor_used_by_main_methods=False,test_time_backward=False,reencoding_used_by_main_methods=False,resources=eng.resources())
