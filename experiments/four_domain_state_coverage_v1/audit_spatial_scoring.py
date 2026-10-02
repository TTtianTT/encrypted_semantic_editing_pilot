"""Retain legacy scores and remove confirmed wrong-observer false positives."""
from collections import defaultdict
from common import *
from space_scope_guard import valid_target_relation,valid_non_target_relations
from analyze import writecsv

def main():
    groups=defaultdict(lambda:dict(n=0,legacy_success_k=0,confirmed_false_positive_k=0,independent_guard_unresolved_k=0));cases=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study;ws={w['world_id']:w for w in rows(base/'data/space/worlds.jsonl')}
        paths=[]
        for run in (base/'runs/formal').glob('*_space_*'):
            paths+=list((run/'outputs').rglob('*.jsonl'))+list(run.glob('test_atomic.jsonl'))
        for model in MODELS:
            paths+=list((base/'language_controls'/f'{model}_space').rglob('*.jsonl'))+list((base/'position_foils'/f'{model}_space').rglob('*.jsonl'))
        for path in sorted(paths):
            if path.name.startswith('cohort'):continue
            rel=str(path.relative_to(base));stage='position' if 'position_foils/' in rel else 'structure' if 'language_controls/' in rel else 'formal'
            for r in rows(path):
                if r.get('gold') is None:continue
                g=r['gold'];ok=r['score']['success'];checks=(valid_target_relation(r['prediction'],g,ws[r['world_id']]),valid_non_target_relations(r['prediction'],g,ws[r['world_id']]));bad=ok and False in checks;key=json.dumps(dict(study=study,stage=stage,artifact=rel,template=r['template']),sort_keys=True);v=groups[key];v['n']+=1;v['legacy_success_k']+=ok;v['confirmed_false_positive_k']+=bad;v['independent_guard_unresolved_k']+=ok and not bad and None in checks
                if bad:cases.append(dict(study=study,stage=stage,artifact=rel,world_id=r['world_id'],state=r['state'],operation=r['operation'],prediction=r['prediction'],gold=g,legacy_score=r['score'],strict_success=False,reason='Target A/fixed B/marker relation has incorrect observer or object binding; retain raw score but reject the confirmed false positive.'))
    result=[dict(**json.loads(k),**v,strict_success_k=v['legacy_success_k']-v['confirmed_false_positive_k'],strict_success_rate=(v['legacy_success_k']-v['confirmed_false_positive_k'])/v['n']) for k,v in sorted(groups.items())];writecsv(ROOT/'spatial_scoring_adjudication.csv',result);jsonl(ROOT/'spatial_scoring_false_positive_cases.jsonl',cases);dump(ROOT/'SPATIAL_SCORING_AUDIT.json',dict(groups=len(result),actual_confirmed_false_positives=len(cases),raw_scores_preserved=True,strict_audit_never_promotes_failed_primary_outputs=True,primary_space_state_study='space_relation_confirmation_v1',synthetic_negative_control_sha=digest(ROOT/'SPACE_SCOPE_GUARD_CHECK.json')));print('Actual spatial false positives:',len(cases))

if __name__=='__main__':main()
