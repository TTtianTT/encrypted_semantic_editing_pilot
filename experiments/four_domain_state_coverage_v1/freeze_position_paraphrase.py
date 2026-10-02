"""Register the independent guard's false rejections before diagnostic GPU work."""
import datetime,subprocess
from common import *

def main():
    archive=ROOT/'protocol_revisions/position_guard_before_relative_clause_paraphrase'
    old=read(archive/'position_lock.json')
    for name in ('position_spec.py','check_space_scope_guard.py'):
        oldcode=subprocess.check_output(['git','show','dd40964:experiments/four_domain_state_coverage_v1/'+name],cwd=WORKTREE)
        (archive/name).write_bytes(oldcode)
    for t in read(ROOT/'position_tasks.json'):
        p=ROOT.parent/t['study']/'position_foils'/f"{t['model']}_{t['domain']}"
        assert not any(p.rglob('*.jsonl')) and not (p/'complete.json').exists()
    dump(ROOT/'position_lock.json',dict(files=[dict(path=r['path'],sha256=digest(Path(r['path']))) for r in old['files']],no_training=True,registered_after_initial_formal=True,narrator_emotion_variants=[2,3],prior_lock_sha=digest(archive/'position_lock.json'),guard_unrecognized_is_unknown=True))
    record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_specification_sha=digest(archive/'position_lock.json'),new_specification_sha=digest(ROOT/'position_lock.json'),no_diagnostic_model_predictions=True,no_training_or_selection_change=True,legacy_model_scores_unchanged=True,retracted_guard_false_positive_candidates=12,reason='The twelve alleged mismatches were correct same-object relative-clause paraphrases. The revised independent guard accepts them; unfamiliar wording is unknown, never a confirmed contradiction.',positive_checks=1344,relative_clause_checks=224,wrong_binding_checks=168)
    dump(ROOT/'POSITION_PARAPHRASE_GUARD_REVISION.json',record)
    ledger=read(ROOT/'submissions.json')
    for r in ledger:
        if r['phase']=='position_foils':r['pre_gpu_paraphrase_guard_revision']=record
    dump(ROOT/'submissions.json',ledger)
    print('Correct relative clauses and guard unknowns registered before diagnostic GPU work')

if __name__=='__main__':main()
