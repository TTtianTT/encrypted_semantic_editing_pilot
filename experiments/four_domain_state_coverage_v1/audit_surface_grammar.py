"""Post hoc three-way syntax coverage over every available natural prediction."""
from collections import defaultdict
from common import *
from analyze import writecsv
from controlled_surface_grammar import surface_grammar

def main():
    groups=defaultdict(lambda:dict(n=0,known_valid_k=0,identified_agreement_case_error_k=0,unknown_k=0,old_grammar_false_but_surface_known_valid_k=0));cases=[];total=0
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study;paths=[]
        for run in (base/'runs/formal').glob('*'):
            paths+=list((run/'outputs').glob('*/*.jsonl'))+list(run.glob('test_*.jsonl'))
        for folder in ('language_controls','position_foils'):
            paths+=list((base/folder).glob('*_*/*.jsonl'))+list((base/folder).glob('*_*/s*/*.jsonl'))+list((base/folder).glob('*_*/s*/*/*.jsonl'))
        for path in sorted(set(paths)):
            rel=str(path.relative_to(base));phase='formal' if rel.startswith('runs/') else rel.split('/')[0]
            owner=path.parts[path.parts.index('formal')+1] if phase=='formal' else path.parts[path.parts.index(phase)+1]
            pieces=owner.split('_');model,domain=pieces[:2];seed=pieces[2][1:] if phase=='formal' else next((p[1:] for p in path.parts if re_seed(p)),'shared_backbone');role=path.parent.name if path.parent.parent.name=='outputs' or path.parent.parent.name.startswith('s') else 'identity_or_P'
            for i,r in enumerate(rows(path),1):
                if 'prediction' not in r or 'score' not in r or r.get('symbolic'):continue
                result=surface_grammar(r['prediction']);meta=dict(study=study,model=model,domain=domain,seed=seed,phase=phase,condition=role,kind=r.get('kind','unknown'),template=r.get('template'),mode=r.get('mode','atomic_or_matrix'));key=json.dumps(meta,sort_keys=True);v=groups[key];v['n']+=1;total+=1
                v['known_valid_k']+=result is True;v['identified_agreement_case_error_k']+=result is False;v['unknown_k']+=result is None;v['old_grammar_false_but_surface_known_valid_k']+=result is True and not r['score']['grammar']
                if len(cases)<64 and (result is False or result is True and not r['score']['grammar']):cases.append(dict(**meta,artifact=rel,line=i,world_id=r.get('world_id'),prediction=r['prediction'],old_score=r['score'],surface_grammar=result,interpretation='known surface grammar does not imply semantic completeness or correctness' if result else 'identified controlled-English agreement/case error, not a general grammar judgment'))
    table=[dict(**json.loads(k),**v,classified_n=v['known_valid_k']+v['identified_agreement_case_error_k'],known_valid_all_candidate_rate=v['known_valid_k']/v['n'],classified_coverage=(v['known_valid_k']+v['identified_agreement_case_error_k'])/v['n'],known_valid_conditioned_on_classification=v['known_valid_k']/(v['known_valid_k']+v['identified_agreement_case_error_k']) if v['known_valid_k']+v['identified_agreement_case_error_k'] else None) for k,v in sorted(groups.items())]
    writecsv(ROOT/'surface_grammar_by_seed.csv',table);jsonl(ROOT/'surface_grammar_audit_cases.jsonl',cases);dump(ROOT/'SURFACE_GRAMMAR_AUDIT.json',dict(predictions=total,groups=len(table),raw_grammar_gates_scores_and_models_unchanged=True,posthoc=True,checker_sha=digest(ROOT/'controlled_surface_grammar.py'),fixture_sha=digest(ROOT/'SURFACE_GRAMMAR_CHECK.json'),unknown_is_not_confirmed_ungrammatical=True))
    print('Surface grammar independently classified:',total,'natural predictions')

def re_seed(s):return len(s)>1 and s[0]=='s' and s[1:].isdigit()

if __name__=='__main__':main()
