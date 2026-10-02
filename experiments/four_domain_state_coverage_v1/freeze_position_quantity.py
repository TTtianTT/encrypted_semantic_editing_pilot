"""Freeze every-count consistency after independent negatives, before GPU output."""
import datetime,subprocess
from common import *
from quantity_guard import consistent_quantity

def main():
    archive=ROOT/'protocol_revisions/position_before_all_quantity_claims';old=read(archive/'position_lock.json')
    oldcode=subprocess.check_output(['git','show','cf751d8:experiments/four_domain_state_coverage_v1/position_spec.py'],cwd=WORKTREE);(archive/'position_spec.py').write_bytes(oldcode)
    tests=read(ROOT/'EMOTION_ADDITION_NEGATIVE_AUDIT.json')['candidates']
    worlds={w['world_id']:w for w in rows(ROOT/'data/emotion/worlds.jsonl')}
    for r in tests:
        if r['type']=='contradictory_quantity':assert consistent_quantity(r['text'],worlds[r['world_id']]) is False
    for quantity in range(1,10):
        phrase=('There is 1 copy.' if quantity==1 else f'There are {quantity} copies.')
        assert consistent_quantity(phrase+' '+phrase,dict(quantity=quantity)) is True
        assert consistent_quantity(phrase.replace(' ','  '),dict(quantity=quantity)) is True
        assert consistent_quantity('"There are 9 copies." '+phrase,dict(quantity=quantity)) is True
    for t in read(ROOT/'position_tasks.json'):
        path=ROOT.parent/t['study']/'position_foils'/f"{t['model']}_{t['domain']}";assert not any(path.rglob('*.jsonl')) and not (path/'complete.json').exists()
    files=[Path(r['path']) for r in old['files']]+[ROOT/'quantity_guard.py',ROOT/'POSITION_QUANTITY_AMENDMENT.md']
    dump(ROOT/'position_lock.json',dict(files=[dict(path=str(p),sha256=digest(p)) for p in files],no_training=True,registered_after_initial_formal=True,narrator_emotion_variants=[2,3],prior_lock_sha=digest(archive/'position_lock.json'),guard_unrecognized_is_unknown=True,every_unquoted_quantity_checked=True))
    record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_specification_sha=digest(archive/'position_lock.json'),new_specification_sha=digest(ROOT/'position_lock.json'),no_diagnostic_model_predictions=True,no_training_or_selection_change=True,constructed_contradictions_rejected=56,consistent_repetitions_whitespace_and_quote_checks=27)
    dump(ROOT/'POSITION_QUANTITY_REVISION.json',record);ledger=read(ROOT/'submissions.json')
    for r in ledger:
        if r['phase']=='position_foils':r['pre_gpu_quantity_revision']=record
    dump(ROOT/'submissions.json',ledger);print('Every-count consistency frozen before diagnostic model evaluation')

if __name__=='__main__':main()
