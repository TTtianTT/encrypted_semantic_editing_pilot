"""Separate target-state accuracy from anchor/binding/preservation constraints.

The frozen primary score's scope is target AND preserved: a joint outcome, not an
independent diagnosis of anchor selection. These auxiliary components use its
independent parser, with unresolved/invalid grammar left explicitly unknown.
"""
from collections import defaultdict
import hashlib
from common import *
from evaluator import parse
from analyze import writecsv

def components(r,w):
    g=r['gold'];d=g['domain'];t=g['structure'];p,grammar=parse(r['prediction'],d,t,g['symbolic']);a,b,c=[s.lower() for s in w['people']]
    applicable=['objective_facts_preserved','target_value_correct','target_identity_correct','scope_constraints_satisfied']
    if d=='time':applicable+=['event_status_preserved']+(['absolute_date_preserved'] if t>=3 else [])+(['fixed_event_relation_preserved'] if t==4 else [])
    if d=='space':applicable+=(['absolute_position_preserved'] if t>=3 else [])+(['fixed_observer_preserved'] if t==4 else [])+(['object_relation_preserved'] if t==5 else [])
    if d=='emotion':applicable+=['non_target_evaluation_preserved']+(['non_target_object_evaluation_preserved'] if t==4 else [])
    if d=='person':applicable+=['event_participant_bindings_preserved','speech_context_correct']+(['reflexive_binding_preserved'] if t==3 else [])+(['static_participants_preserved'] if t==5 else [])
    if (d=='time' and t==5) or (d=='emotion' and t==5) or (d=='person' and t==4):applicable+=['quotation_anchor_and_words_preserved']
    # Do not infer identity/scope errors from unresolved or malformed output.
    if p is None or not grammar or not r['score']['ended']:return {k:None for k in applicable}
    values={'objective_facts_preserved':p.get('object')==g['object'] and p.get('color')==g['color'] and p.get('quantity')==g['quantity']}
    if d=='time':
        values.update(target_value_correct=p.get('relative')==g['relative'],target_identity_correct=p.get('event_object')==g['object'],event_status_preserved=p.get('status')==g['status'])
        if t>=3:values['absolute_date_preserved']=p.get('absolute')==g['event_date']
        if t==4:values['fixed_event_relation_preserved']=p.get('fixed_launch',False)
        if t==5:values['quotation_anchor_and_words_preserved']=p.get('quote')==(w['quote_date'],b,c,g.get('foil_quote','The event is tomorrow.').lower())
    elif d=='space':
        values.update(target_value_correct=p.get('relation')==g['relation'],target_identity_correct=p.get('observer')==a and p.get('relation_object')==g['object'])
        if t>=3:
            x,y=w['object_xy'];ox,oy=w['observer_xy'];direction='east' if x>ox else 'west' if x<ox else 'north' if y>oy else 'south';values['absolute_position_preserved']=p.get('absolute')==direction
        if t==4:values['fixed_observer_preserved']=p.get('views',{}).get(b)==g['fixed_relation']
        if t==5:values['object_relation_preserved']=p.get('marker_north',False)
    elif d=='emotion':
        focus=w['focus'].lower();other=b if focus==a else a;target=(focus,g['object']);ev=p.get('evaluations',{});expected={target,(other,g['object'])}
        if t==4:expected.add((focus,w['other_object']))
        values.update(target_value_correct=ev.get(target)==g['target_level'],target_identity_correct=p.get('focus')==focus and p.get('target_object')==g['object'] and target in ev and set(ev)==expected,non_target_evaluation_preserved=ev.get((other,g['object']))==w['other_level'])
        if t==4:values['non_target_object_evaluation_preserved']=ev.get((focus,w['other_object']))==1
        if t==5:values['quotation_anchor_and_words_preserved']=p.get('quote')==(c,f"i dislike the {g['object']}.")
    else:
        bindings=all(p.get(k)==g[k].lower() for k in ('agent','patient','owner'));context=p.get('speaker')==g['speaker'].lower() and p.get('listener')==g['listener'].lower()
        values.update(target_value_correct=context,target_identity_correct=p.get('event_object')==g['object'],event_participant_bindings_preserved=bindings,speech_context_correct=context)
        if t==3:values['reflexive_binding_preserved']=p.get('reflexive') is not None and p['reflexive'][:2]==(a,a)
        if t==4:values['quotation_anchor_and_words_preserved']=p.get('quote')==(b,c,'i give you my key.')
        if t==5:values['static_participants_preserved']=p.get('static_participants')==(c,a,b)
    # Deliberately exclude target state/context accuracy from scope constraints.
    values['scope_constraints_satisfied']=all(v for k,v in values.items() if k not in ('target_value_correct','speech_context_correct'))
    assert set(values)==set(applicable)
    return values

def main():
    groups=defaultdict(lambda:dict(n=0,resolved_n=0,correct_k=0));cases=defaultdict(list);count=0
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for run in sorted((base/'runs/formal').glob('*')):
            model,domain,se=run.name.split('_');seed=int(se[1:]);ws={w['world_id']:w for w in rows(base/f'data/{domain}/worlds.jsonl')}
            paths=[p for p in sorted((run/'outputs').rglob('*.jsonl')) if not p.name.startswith('cohort')]+list(run.glob('test_atomic.jsonl'))
            for path in paths:
                role=path.parent.name if path.parent!=run else 'P'
                for r in rows(path):
                    if r.get('gold') is None:continue
                    cc=components(r,ws[r['world_id']]);count+=1
                    cell=dict(study=study,model=model,domain=domain,seed=seed,condition=role,shard=path.stem,template=r['template'])
                    if 'source' in r and r['kind']=='source_matrix':cell['source']=r['source']
                    for metric,value in cc.items():
                        key=json.dumps(dict(**cell,metric=metric),sort_keys=True);v=groups[key];v['n']+=1;v['resolved_n']+=value is not None;v['correct_k']+=value is True
                        if value is False and metric not in ('target_value_correct','scope_constraints_satisfied'):
                            sample=dict(**cell,metric=metric,world_id=r['world_id'],state=r['state'],operation=r['operation'],prediction=r['prediction'],gold=r['gold'],artifact=str(path.relative_to(base)))
                            ck=(study,model,domain,metric);rank=hashlib.sha256(json.dumps([sample['artifact'],sample['world_id'],sample['state'],sample['operation']],sort_keys=True).encode()).hexdigest();cases[ck].append((rank,sample));cases[ck]=sorted(cases[ck],key=lambda x:x[0])[:4]
    output=[]
    for key,v in sorted(groups.items()):output.append(dict(**json.loads(key),**v,unresolved_n=v['n']-v['resolved_n'],resolved_coverage=v['resolved_n']/v['n'],conditional_component_rate=v['correct_k']/v['resolved_n'] if v['resolved_n'] else None,strict_all_candidate_rate=v['correct_k']/v['n']))
    writecsv(ROOT/'semantic_components_by_seed.csv',output);jsonl(ROOT/'semantic_component_cases.jsonl',[r for key in sorted(cases) for rank,r in cases[key]])
    dump(ROOT/'semantic_component_audit.json',dict(predictions=count,groups=len(output),scope_definition='Identity/binding and non-target constraints, excluding target state/context endpoint. Frozen primary scope remains target AND preserved.',unknown_policy='Parser failure, grammar failure or unfinished generation is unknown for these components; retain unknown count/coverage and strict all-candidate rate.',posthoc_no_selection_or_training=True,primary_spatial_study='space_relation_confirmation_v1; initial facing results separately retained'))
    print('Semantic component rows',len(output),'from',count,'predictions')

if __name__=='__main__':main()
