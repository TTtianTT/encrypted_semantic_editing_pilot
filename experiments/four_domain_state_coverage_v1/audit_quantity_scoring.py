"""CPU-only raw-score audit of contradictory exact counts, including current text."""
from collections import defaultdict
from common import *
from quantity_guard import consistent_quantity
from analyze import writecsv

def main():
    counts=defaultdict(lambda:dict(n=0,legacy_success_k=0,contradictory_count_k=0,current_qualified_count_contradiction_k=0));cases=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study;paths=list((base/'runs/formal').glob('*/outputs/**/*.jsonl'))+list((base/'runs/formal').glob('*/dev/*.jsonl'))+list((base/'language_controls').glob('**/*.jsonl'))+list((base/'position_foils').glob('**/*.jsonl'))
        paths=[p for p in paths if 'data' not in p.parts and not p.name.startswith('cohort')]
        for path in sorted(paths):
            for r in rows(path):
                if r.get('gold') is None or 'prediction' not in r:continue
                ok=r['score']['success'];bad=ok and consistent_quantity(r['prediction'],r['gold']) is False
                current_bad=r.get('current_score',{}).get('success',False) and consistent_quantity(r['current_prediction'],r['gold']) is False
                key=(study,str(path.relative_to(base)));v=counts[key];v['n']+=1;v['legacy_success_k']+=ok;v['contradictory_count_k']+=bad;v['current_qualified_count_contradiction_k']+=current_bad
                if bad or current_bad:cases.append(dict(study=study,artifact=key[1],world_id=r['world_id'],state=r['state'],operation=r['operation'],prediction=r['prediction'],gold=r['gold'],legacy_score=r['score'],contradictory_output=bad,qualified_current_contradiction=current_bad,current_prediction=r.get('current_prediction')))
    records=[dict(study=k[0],artifact=k[1],**v,strict_success_k=v['legacy_success_k']-v['contradictory_count_k']) for k,v in sorted(counts.items())]
    writecsv(ROOT/'quantity_scoring_adjudication.csv',records);jsonl(ROOT/'quantity_scoring_false_positive_cases.jsonl',cases)
    dump(ROOT/'QUANTITY_SCORING_AUDIT.json',dict(groups=len(counts),actual_output_false_positives=sum(v['contradictory_count_k'] for v in counts.values()),current_qualification_false_positives=sum(v['current_qualified_count_contradiction_k'] for v in counts.values()),raw_scores_preserved=True,no_gpu=True))
    print('Actual contradictory-count successes/current qualifications:',sum(v['contradictory_count_k'] for v in counts.values()),sum(v['current_qualified_count_contradiction_k'] for v in counts.values()))

if __name__=='__main__':main()
