"""Outcome-only pairing; donor ordering never examines later trajectories."""
from collections import Counter
import torch
from .common import *
from .adapter import render,gold,advance,reconstruct

HISTORIES=[dict(id='E_from_future_plus',start=1,operations=['plus']),dict(id='E_from_past_minus',start=-1,operations=['minus'])]

@torch.no_grad()
def scan(eng,worlds,folder,resume=True):
    records=[];audits=[]
    for wi,w in enumerate(worlds):
        wp=folder/'worlds'/w['world_id'];done=wp/'complete.json'
        if done.exists():
            marker=read(done);assert marker['checkpoint_hash']==eng.task['checkpoint_hash'] and marker['data_hash']==eng.task['data_hash']
            records.extend(rows(wp/'pairs.jsonl'));audits.extend(rows(wp/'audit.jsonl'));continue
        template=0;current=0;states={};nexts={}
        for history in HISTORIES:
            h,m=reconstruct(eng,w,history,template);r=eng.evaluate(h,m,w,current,template)
            states[history['id']]=(h,m,r,history)
        hn,mn=eng.encode([render(w,current,template)]);rn=eng.evaluate(hn,mn,w,current,template)
        states['N_current']=(hn,mn,rn,dict(id='N_current',start=current,operations=[]))
        # Exactly one decode–reencode from the first fixed edited history, labelled R.
        first=states[HISTORIES[0]['id']][2]
        hr,mr=eng.encode([first['text']]);rr=eng.evaluate(hr,mr,w,current,template)
        states['R_once']=(hr,mr,rr,dict(id='R_once',start=current,operations=[],reencode_of=HISTORIES[0]['id'],input_text=first['text']))
        for key,(h,m,r,hist) in states.items():
            for op in ('plus','minus'):
                if key=='R_once' and torch.equal(hr,hn) and torch.equal(mr,mn):nexts[key,op]=nexts['N_current',op]
                else:nexts[key,op]=eng.evaluate(eng.ed[op](h,m),m,w,advance('time',current,op),template)
        confidence_cache={}
        selected=[];wa=[]
        for source,donorkeys in [('E→E',[h['id'] for h in HISTORIES]),('N→E',['N_current']),('R→E',['R_once'])]:
            for op in ('plus','minus'):
                chosen=None;counts=Counter();counts['candidate_worlds']=1
                for dk in donorkeys:
                    for bk in [h['id'] for h in HISTORIES]:
                        if dk==bk:continue
                        hg,mg,g,hg_hist=states[dk];hb,mb,b,hb_hist=states[bk]
                        counts['candidate_history_combinations']+=1
                        if not(g['success'] and b['success']):counts['current_not_both_correct']+=1;continue
                        counts['current_double_correct']+=1
                        if g['text']!=b['text']:counts['current_text_mismatch']+=1;continue
                        counts['exact_current_text']+=1
                        if not(nexts[dk,op]['success'] and not nexts[bk,op]['success']):counts['not_good_bad_fork']+=1;continue
                        counts['next_step_fork']+=1
                        if hg.shape!=hb.shape or not torch.equal(mg,mb):counts['shape_or_mask_mismatch']+=1;continue
                        counts['same_shape_mask']+=1
                        if chosen is None:chosen=(dk,bk)
                if chosen:
                    dk,bk=chosen;hg,m,g,dh=states[dk];hb,_,b,bh=states[bk]
                    pair_id=f"{eng.name}_s{eng.task['editor_seed']}_{w['world_id']}_{source.replace('→','_')}_{op}"
                    for key in (dk,bk):
                        if key not in confidence_cache:confidence_cache[key]=eng.confidence(states[key][0],states[key][1],render(w,0,0))
                    gc=confidence_cache[dk];bc=confidence_cache[bk]
                    cached=wp/(pair_id+'.pt');wp.mkdir(parents=True,exist_ok=True)
                    temporary=cached.with_suffix('.tmp');torch.save(dict(good=hg.cpu(),bad=hb.cpu(),mask=m.cpu()),temporary);temporary.replace(cached)
                    r=dict(run_id=RUN_ID,world_id=w['world_id'],world=w,pair_id=pair_id,split=w['mechanism_split'],original_split=w['original_split'],original_IID_OOD='IID/template0',model_id=eng.task['model_id'],model=eng.name,checkpoint_hash=eng.task['checkpoint_hash'],editor_condition='P',editor_seed=eng.task['editor_seed'],donor_source=source,donor_history=dh,recipient_history=bh,current_state=0,current_text=g['text'],operation=op,template=0,gold_next_state=advance('time',0,op),gold_current=gold(w,0,0),mask_hash=objsha(m.cpu().tolist()),valid_memory_length=int(m.sum()),state_path=str(cached),good_current=gc,bad_current=bc,confidence_matched_nll=abs(gc['token_mean_nll']-bc['token_mean_nll'])<=.1,confidence_matched_margin=None,donor_next=nexts[dk,op],recipient_next=nexts[bk,op],job_id=__import__('os').environ['SLURM_JOB_ID'])
                    selected.append(r);counts['final_pair_worlds']=1
                else:counts['final_pair_worlds']=0
                wa.append(dict(world_id=w['world_id'],split=w['mechanism_split'],original_split=w['original_split'],source=source,operation=op,model=eng.name,editor_seed=eng.task['editor_seed'],**counts))
        jsonl(wp/'pairs.jsonl',selected);jsonl(wp/'audit.jsonl',wa);dump(done,dict(checkpoint_hash=eng.task['checkpoint_hash'],data_hash=eng.task['data_hash']))
        records.extend(selected);audits.extend(wa)
        print(f'scan {wi+1}/{len(worlds)} {w["world_id"]} pairs={len(selected)}',flush=True)
    jsonl(folder/'pairs.jsonl',records);jsonl(folder/'pair_audit.jsonl',audits)
    return dict(pair_records=len(records),paired_worlds=len({r['world_id'] for r in records}),candidate_worlds=len(worlds),source_counts=dict(Counter(r['donor_source'] for r in records)),split_counts=dict(Counter(r['split'] for r in records)),resources=eng.resources())

def primary_pairs(rs,split_name=None,cap=None):
    """Fixed E→E,N→E,R→E precedence; one plus pair/world for primary analysis."""
    out=[]
    for wid in sorted({r['world_id'] for r in rs}):
        eligible=[r for r in rs if r['world_id']==wid and r['operation']=='plus' and (split_name is None or r['split']==split_name)]
        eligible.sort(key=lambda r:(['E→E','N→E','R→E'].index(r['donor_source']),r['pair_id']))
        if eligible:out.append(eligible[0])
    return out if cap is None else out[:cap]
