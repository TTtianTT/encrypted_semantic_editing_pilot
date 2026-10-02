"""Finish explicit object-binding checks before any position diagnostic GPU call."""
import datetime
from common import *
old=read(ROOT/'protocol_revisions/position_A_guard_before_object_guard/position_lock.json')
for t in read(ROOT/'position_tasks.json'):
    p=ROOT.parent/t['study']/'position_foils'/f"{t['model']}_{t['domain']}";assert not any(p.rglob('*.jsonl')) and not (p/'complete.json').exists()
plan=ROOT/'POSITION_FOILS_PLAN.md';text=plan.read_text();text+='\nThe same pre-GPU independent guard also checks the object mentioned in every\nfixed-B relation and in the marker relation. Correct relation words with the\nwrong object are rejected. Final CPU controls:1344 positives and168 adversarial\nA/B/marker binding negatives; the legacy parser accepts all168 wrong negatives.\nThe intermediate A-only guard and lock are separately archived; no diagnostic\nmodel output existed in either amendment. Frozen primary scores remain unchanged.\n';plan.write_text(text)
files=[Path(r['path']) for r in old['files']];dump(ROOT/'position_lock.json',dict(files=[dict(path=str(p),sha256=digest(p)) for p in files],no_training=True,registered_after_initial_formal=True,pre_gpu_observer_and_object_guard=True,previous_A_only_lock_sha=digest(ROOT/'protocol_revisions/position_A_guard_before_object_guard/position_lock.json')))
record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_specification_sha=digest(ROOT/'protocol_revisions/position_A_guard_before_object_guard/position_lock.json'),new_specification_sha=digest(ROOT/'position_lock.json'),diagnostic_gpu_predictions_exist=False,inputs_weights_training_or_selection_changed=False,check_sha=digest(ROOT/'SPACE_SCOPE_GUARD_CHECK.json'));dump(ROOT/'POSITION_OBJECT_GUARD_REVISION.json',record)
ledger=read(ROOT/'submissions.json')
for r in ledger:
    if r['phase']=='position_foils':r['pre_gpu_object_guard_revision']=record
dump(ROOT/'submissions.json',ledger);print('Pre-GPU observer/object guard locked')
