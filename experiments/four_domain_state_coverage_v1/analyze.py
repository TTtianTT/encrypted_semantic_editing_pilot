"""CPU analysis of immutable predictions. Does not generate or choose models."""
import csv,json,statistics,hashlib
from collections import defaultdict,Counter
from common import *
from evaluator import score,parse

def writecsv(path,records):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in records for k in r))
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(records)

def summary(rows):
    n=len(rows);out=dict(n=n,worlds=len({r['world_id'] for r in rows}))
    for metric in ('success','target','preserved','scope','parseable','grammar','ended'):
        k=sum(r['score'][metric] for r in rows);out[metric+'_k']=k;out[metric+'_rate']=k/n if n else None
    if any('previous_correct' in r for r in rows):
        previous=[r for r in rows if r.get('previous_correct')];out.update(conditional_n=len(previous),conditional_k=sum(r['score']['success'] for r in previous),conditional_rate=sum(r['score']['success'] for r in previous)/len(previous) if previous else None,full_k=sum(r.get('full_success',False) for r in rows),full_rate=sum(r.get('full_success',False) for r in rows)/n)
    if any('current_score' in r for r in rows):
        previous=[r for r in rows if r['current_score']['success']];matched=[r for r in rows if r['common_match']]
        out.update(current_correct_n=len(previous),current_coverage=len(previous)/n,conditional_n=len(previous),conditional_k=sum(r['score']['success'] for r in previous),conditional_rate=sum(r['score']['success'] for r in previous)/len(previous) if previous else None,matched_n=len(matched),matched_k=sum(r['score']['success'] for r in matched),matched_rate=sum(r['score']['success'] for r in matched)/len(matched) if matched else None)
    return out

def error_type(r,world):
    if r.get('current_score') and not r['current_score']['success']:return 'current_text_already_wrong'
    sc=r['score']
    if sc['success']:return 'success'
    if not sc['parseable']:return 'unresolved_parse'
    if not sc['grammar']:return 'controlled_grammar_invalid'
    g=r['gold'];p,_=parse(r['prediction'],g['domain'],g['structure'],g['symbolic'])
    if g['domain']=='person' and any(p.get(k)!=g[k].lower() for k in ('agent','patient','owner')):return 'participant_or_owner_binding'
    if g['domain']=='emotion' and (p.get('focus')!=world['focus'].lower() or p.get('target_object')!=world['object']):return 'evaluator_or_object_binding'
    if g['domain']=='time' and g['structure']==5 and p.get('quote')!=(world['quote_date'],world['people'][1].lower(),world['people'][2].lower(),'the event is tomorrow.'):return 'historical_quote_scope'
    if not sc['preserved']:return 'non_target_changed'
    if not sc['target']:return 'current_correct_next_target_wrong' if r.get('current_score',{}).get('success') else 'target_wrong'
    return 'other_failure'

def keyrow(r):return (r['world_id'],r['state'],r['operation'],r.get('template'),r.get('source'))

def main():
    grouped=[];gates=[];status=[];errors=Counter();cases=defaultdict(list);payloads={};cohorts=[];probe_failure=[];allrows=0
    for phase in ('formal','symbol'):
        for run in sorted((ROOT/'runs'/phase).glob('*')):
            pieces=run.name.split('_');model,d,seed=pieces[0],pieces[1],int(pieces[2][1:]);meta=dict(model=model,domain=d,seed=seed,phase=phase)
            ws={w['world_id']:w for w in rows(ROOT/f'data/{d}/worlds.jsonl')}
            complete=read(run/'complete.json') if (run/'complete.json').exists() else None
            status.append(dict(**meta,status=complete['status'] if complete else 'technical_failure' if (run/'failure.json').exists() else 'running_or_not_started'))
            gp=run/'dev/admission.json'
            if gp.exists():
                gate=read(gp)
                for kind in ('reconstruction','atomic','gold_next'):gates.append(dict(**meta,kind=kind,passed=gate['passed'],**{k:gate[kind][k] for k in ('n','success','rate','min_cell')}))
            dirs=list((run/'outputs').glob('*')) if (run/'outputs').exists() else [run]
            for output in dirs:
                role=output.name if output!=run else 'P';payloads[(model,d,seed,role)]={}
                for p in sorted(output.glob('*.jsonl')):
                    if p.name.startswith('cohort'):
                        cr=rows(p);h=int(p.stem.split('_')[1][1:]);t=int(p.stem.split('_')[2][1:]);reject=Counter(reason for r in cr for reason in r['reasons'])
                        cohorts.append(dict(**meta,condition=role,holdout_split=h,template=t,candidates=len(cr),matched=sum(r['common_match'] for r in cr),**dict(reject)));continue
                    if not (p.name.startswith(('atomic','trajectory','matrix','test_atomic','test_reconstruction'))):continue
                    rr=rows(p);payloads[(model,d,seed,role)][p.stem]=rr;cells=defaultdict(list)
                    for r in rr:
                        if r.get('gold') is not None:
                            # Raw scores retained. Final scoring is independently
                            # recomputed from emitted text, world and frozen gold.
                            ended=r['score']['ended'];rescored=score(r['prediction'],r['gold'],ws[r['world_id']],ended)
                            assert rescored==r['score'],f'Frozen score mismatch: {p} {r["world_id"]}'
                        allrows+=1
                        if p.name.startswith('matrix'):
                            h=int(p.stem.split('_')[1][1:]);cell=dict(kind='source_matrix',holdout_split=h,template=r['template'],state=r['state'],operation=r['operation'],source=r['source'],state_heldout=r['state_heldout'])
                        elif p.name.startswith('trajectory'):
                            cell=dict(kind='trajectory',template=r['template'],mode=r['mode'],trajectory=r['trajectory'],step=r['step'])
                        else:cell=dict(kind=r['kind'],template=r['template'],state=r['state'],operation=r['operation'])
                        cells[json.dumps(cell,sort_keys=True)].append(r)
                        et=error_type(r,ws[r['world_id']]) if r.get('gold') is not None else 'technical_input_cap'
                        if et!='success':
                            errors[(model,d,seed,role,et)]+=1
                            case=dict(**meta,condition=role,error=et,artifact=str(p.relative_to(ROOT)),**{k:v for k,v in r.items() if k not in ('hidden','mask')})
                            cases[(model,d,et)].append(case)
                    for cell,values in cells.items():grouped.append(dict(**meta,condition=role,**json.loads(cell),**summary(values)))
            # Join cross-source probe predictions with next failures; no re-fit.
            probe_path=run/'probe_per_world.jsonl'
            if probe_path.exists():
                lookup={(r['world_id'],r['state'],r['test_source'],r['variable'],r['training_source']):r for r in rows(probe_path)}
                for (m,domain,s,role),shards in list(payloads.items()):
                    if (m,domain,s)!=(model,d,seed):continue
                    for name,rr in shards.items():
                        if not name.startswith('matrix') or not name.endswith('t0'):continue
                        for variable in ('current_state','target_binding','target_object'):
                            subset=[]
                            for r in rr:
                                if r['current_score']['success'] and not r['score']['success']:
                                    q=lookup.get((r['world_id'],r['state'],r['source'],variable,'natural'))
                                    if q:subset.append(q['correct'])
                            if subset:probe_failure.append(dict(**meta,condition=role,shard=name,variable=variable,current_correct_next_failed_n=len(subset),probe_correct_k=sum(subset),probe_accuracy=sum(subset)/len(subset)))
    writecsv(ROOT/'summary_by_seed.csv',grouped);writecsv(ROOT/'admission.csv',gates);writecsv(ROOT/'completion_status.csv',status);writecsv(ROOT/'paired_cohort_coverage.csv',cohorts);writecsv(ROOT/'probe_on_next_failures.csv',probe_failure)
    writecsv(ROOT/'error_counts.csv',[dict(model=m,domain=d,seed=s,condition=c,error=e,n=n) for (m,d,s,c,e),n in sorted(errors.items())])
    selected=[]
    for group,values in sorted(cases.items()):
        values.sort(key=lambda r:hashlib.sha256(json.dumps([r['world_id'],r.get('state'),r.get('operation'),r['condition'],r['artifact']],sort_keys=True).encode()).hexdigest());selected+=values[:6]
    jsonl(ROOT/'failure_cases.jsonl',selected)
    # Fixed-model mean and range, never pooling seeds as independent worlds.
    averaged=defaultdict(list)
    for row in grouped:
        key=json.dumps({k:v for k,v in row.items() if k not in ('seed',) and not k.endswith(('_k','_n','_rate')) and k not in ('n','worlds','matched_n','current_coverage')},sort_keys=True)
        averaged[key].append(row)
    means=[]
    for key,rr in averaged.items():
        metrics=sorted({k for r in rr for k in r if k.endswith('_rate') or k=='current_coverage'})
        for metric in metrics:
            vals=[r[metric] for r in rr if r.get(metric) is not None]
            if vals:means.append(dict(**json.loads(key),metric=metric,seeds=','.join(str(r['seed']) for r in rr if r.get(metric) is not None),seed_count=len(vals),mean=statistics.mean(vals),minimum=min(vals),maximum=max(vals)))
    writecsv(ROOT/'mean_and_range.csv',means)
    # Paired S/M and capability gains/losses on original fixed worlds/inputs.
    contrasts=[];regressions=[];phenomena=[]
    for (model,d,seed,role),shards in payloads.items():
        for name,rr in shards.items():
            if not name.startswith('trajectory'):continue
            controls={(r['world_id'],r['trajectory'],r['step']):r for r in rr if r['mode']=='gold_reencode'}
            groups=defaultdict(list)
            for r in rr:
                if r['mode']=='latent' and r['step']>=2:
                    control=controls.get((r['world_id'],r['trajectory'],r['step']))
                    eligible=r['previous_correct'] and control is not None and control['score']['success']
                    groups[(r['template'],r['trajectory'],r['step'])].append((eligible,eligible and not r['score']['success']))
            for (t,tr,k),pairs in groups.items():phenomena.append(dict(model=model,domain=d,seed=seed,condition=role,template=t,trajectory=tr,step=k,rows=len(pairs),current_correct_and_gold_next_correct_n=sum(a for a,b in pairs),latent_next_failed_k=sum(b for a,b in pairs)))
    for model in MODELS:
        for d in DOMAINS:
            for seed in (42,43,44):
                base=payloads.get((model,d,seed,'P'),{})
                for h in range(2):
                    for template in (0,2):
                        name=f'matrix_h{h}_t{template}';S=payloads.get((model,d,seed,f'S_h{h}'),{}).get(name,[]);M=payloads.get((model,d,seed,f'M_h{h}'),{}).get(name,[])
                        ml={keyrow(r):r for r in M}
                        for source in ('P','Q','U'):
                            matched=[(r,ml[keyrow(r)]) for r in S if keyrow(r) in ml and r['source']==source and r['state_heldout'] and r['common_match']]
                            raw=[(r,ml[keyrow(r)]) for r in S if keyrow(r) in ml and r['source']==source and r['state_heldout']]
                            for cohort,paired in [('fixed_fulltext_mask',matched),('all_candidates',raw)]:
                                if paired:contrasts.append(dict(model=model,domain=d,seed=seed,holdout_split=h,template=template,source=source,cohort=cohort,n=len(paired),worlds=len({a['world_id'] for a,b in paired}),S_k=sum(a['score']['success'] for a,b in paired),M_k=sum(b['score']['success'] for a,b in paired),M_minus_S=(sum(b['score']['success']-a['score']['success'] for a,b in paired))/len(paired)))
                    for role in ('N','S','M'):
                        shards=payloads.get((model,d,seed,f'{role}_h{h}'),{})
                        for name,rr in shards.items():
                            if name not in base or name.startswith('trajectory'):continue
                            previous={keyrow(r):r for r in base[name]};paired=[(previous[keyrow(r)],r) for r in rr if keyrow(r) in previous]
                            if name.startswith('matrix'):paired=[(a,b) for a,b in paired if a['current_score']['success']]
                            if paired:regressions.append(dict(model=model,domain=d,seed=seed,condition=role,holdout_split=h,shard=name,n=len(paired),P_success_k=sum(a['score']['success'] for a,b in paired),condition_success_k=sum(b['score']['success'] for a,b in paired),old_success_lost=sum(a['score']['success'] and not b['score']['success'] for a,b in paired),old_failure_repaired=sum(not a['score']['success'] and b['score']['success'] for a,b in paired)))
    writecsv(ROOT/'M_vs_S.csv',contrasts);writecsv(ROOT/'capability_regressions.csv',regressions)
    writecsv(ROOT/'current_correct_next_failure.csv',phenomena)
    dump(ROOT/'analysis_audit.json',dict(predictions_independently_rescored=allrows,case_selection='first6 per model/domain/error by fixed world/condition/artifact hash, not best seed',bootstrap='not used; per-seed counts plus mean/min/max',complete_formal_runs=sum(r['phase']=='formal' and r['status']=='completed' for r in status),status_rows=len(status)))
    print('Analyzed',allrows,'predictions;',len(contrasts),'paired contrasts')

if __name__=='__main__':main()
