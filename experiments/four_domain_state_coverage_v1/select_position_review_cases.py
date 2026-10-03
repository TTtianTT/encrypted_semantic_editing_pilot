"""CPU-only fixed-input order audit; never select by prediction success."""
from common import *

def main():
    cases=[];availability=[]
    for task in read(ROOT/'position_tasks.json'):
        base=ROOT.parent/task['study'];domain=task['domain'];model=task['model']
        dest=base/'position_foils'/f'{model}_{domain}'
        records=rows(base/f'position_foils/data/{domain}/test.jsonl')
        world=min(r['world_id'] for r in records)
        state=2 if domain=='emotion' else 0
        families=[(0,1),(2,3)] if domain=='emotion' else [(0,1)]
        for seed in (42,43,44):
            path=dest/f's{seed}/P/test_atomic.jsonl'
            if not path.exists():
                availability.append(dict(study=task['study'],model=model,domain=domain,seed=seed,status='not_available'))
                continue
            rr=rows(path);lookup={(r['world_id'],r['state'],r['operation'],r['template']):r for r in rr}
            for operation in ('plus','minus'):
                for lhs,rhs in families:
                    pair=[lookup[(world,state,operation,v)] for v in (lhs,rhs)]
                    golds=[{k:v for k,v in r['gold'].items() if k!='foil_variant'} for r in pair]
                    assert golds[0]==golds[1], 'Order pair changes gold meaning'
                    cases.append(dict(study=task['study'],model=model,domain=domain,seed=seed,condition='P',world_id=world,state=state,operation=operation,pair_family='narrator_quote_order' if lhs==2 else 'clause_order',source_file=str(path.relative_to(base)),source_sha256=digest(path),variants=pair,selection='lexicographically first test world, fixed interior state, both legal signs; no outcome filter',equal_mask_length=pair[0]['mask_length']==pair[1]['mask_length']))
            availability.append(dict(study=task['study'],model=model,domain=domain,seed=seed,status='available'))
    jsonl(ROOT/'POSITION_FIXED_REVIEW_CASES.jsonl',cases)
    dump(ROOT/'POSITION_FIXED_REVIEW_SELECTION.json',dict(pairs=len(cases),availability=availability,selection_is_posthoc_but_outcome_independent=True,independent_worlds_per_domain=1,not_independent_human_labels=True))
    print('Position fixed review pairs:',len(cases))

if __name__=='__main__':main()
