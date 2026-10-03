"""Uniform post hoc person attribution audit over every available prediction."""
from collections import defaultdict
from common import *
from evaluator import score as base_score
from semantics import gold,render
from position_spec import make_functions
from person_quote_attribution_score import score_person_attributions,adapt_outer_attribution
from analyze import writecsv

def main():
    groups=defaultdict(lambda:dict(n=0,raw_k=0,adjudicated_k=0,adapted_text_k=0,rescued_k=0,rejected_k=0));changes=[];cases=[];files=[];total=0
    worlds={w['world_id']:w for w in rows(ROOT/'data/person/worlds.jsonl')};position_worlds={w['world_id']:w for w in rows(ROOT/'position_foils/data/person/worlds.jsonl')}
    _,_,position_score=make_functions(gold,render,base_score)
    paths=[]
    for run in (ROOT/'runs/formal').glob('*_person_s*'):
        paths+=list((run/'outputs').glob('*/*.jsonl'))+list(run.glob('test_*.jsonl'))+list(run.glob('dev/*.jsonl'))
    for folder in ('language_controls','position_foils'):
        for dest in (ROOT/folder).glob('*_person'):
            paths+=list(dest.glob('*.jsonl'))+list(dest.glob('s*/*.jsonl'))+list(dest.glob('s*/*/*.jsonl'))
    for path in sorted(set(paths)):
        rel=str(path.relative_to(ROOT));phase='formal' if rel.startswith('runs/') else rel.split('/')[0]
        owner=path.parts[path.parts.index('formal')+1] if phase=='formal' else path.parts[path.parts.index(phase)+1];model=owner.split('_')[0]
        seed=owner.split('_')[-1][1:] if phase=='formal' else next((part[1:] for part in path.parts if part.startswith('s') and part[1:].isdigit()),'shared_backbone')
        role=path.parent.name if path.parent.parent.name=='outputs' or path.parent.parent.name.startswith('s') else 'P' if path.parent.name.startswith('s') else 'identity_or_P'
        file_count=0
        for line,r in enumerate(rows(path),1):
            if 'prediction' not in r or 'score' not in r or r.get('gold') is None or r['gold']['domain']!='person':continue
            ws=position_worlds if phase=='position_foils' else worlds;world=ws[r['world_id']];scorer=position_score if phase=='position_foils' else base_score
            assert scorer(r['prediction'],r['gold'],world,r['score']['ended'])==r['score']
            new=score_person_attributions(r['prediction'],r['gold'],world,r['score']['ended'],scorer)
            meta=dict(model=model,domain='person',seed=seed,phase=phase,split=world['split'],evaluation_artifact=path.stem,condition=role,kind=r.get('kind','unknown'),template=r.get('template'),mode=r.get('mode','atomic_or_matrix'))
            key=json.dumps(meta,sort_keys=True);v=groups[key];v['n']+=1;v['raw_k']+=r['score']['success'];v['adjudicated_k']+=new['success'];v['adapted_text_k']+=adapt_outer_attribution(r['prediction'])!=r['prediction'] if r['gold']['structure']==4 else False
            v['rescued_k']+=new['success'] and not r['score']['success'];v['rejected_k']+=r['score']['success'] and not new['success'];total+=1;file_count+=1
            if new!=r['score']:
                change=dict(**meta,artifact=rel,line=line,world_id=r['world_id'],state=r['state'],operation=r['operation'],raw_success=r['score']['success'],adjudicated_success=new['success']);changes.append(change)
                if len(cases)<48:cases.append(dict(**change,prediction=r['prediction'],gold=r['gold'],raw_score=r['score'],adjudicated_score=new,scoring_only_adapted_text=adapt_outer_attribution(r['prediction'])))
        if file_count:files.append(dict(path=rel,sha256=digest(path),predictions=file_count))
    output=[dict(**json.loads(k),**v,raw_rate=v['raw_k']/v['n'],adjudicated_rate=v['adjudicated_k']/v['n']) for k,v in sorted(groups.items())]
    writecsv(ROOT/'person_quote_attribution_by_seed.csv',output);writecsv(ROOT/'person_quote_attribution_changes.csv',changes);jsonl(ROOT/'PERSON_QUOTE_ATTRIBUTION_REVIEW_CASES.jsonl',cases)
    dump(ROOT/'PERSON_QUOTE_ATTRIBUTION_AUDIT.json',dict(predictions=total,groups=len(output),files=files,raw_scores_and_gates_unchanged=True,posthoc=True,scorer_sha=digest(ROOT/'person_quote_attribution_score.py'),control_sha=digest(ROOT/'PERSON_QUOTE_ATTRIBUTION_CHECK.json'),rescued_success_flags=sum(v['rescued_k'] for v in groups.values()),rejected_success_flags=sum(v['rejected_k'] for v in groups.values()),current_core_and_source_matrix_inputs_have_no_historical_attribution=True))
    print('Person attribution audit:',total,'predictions;',sum(v['rescued_k'] for v in groups.values()),'rescued;',sum(v['rejected_k'] for v in groups.values()),'rejected')

if __name__=='__main__':main()
