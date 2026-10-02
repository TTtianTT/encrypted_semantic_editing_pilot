"""Pre-GPU lock for an explicitly requested narrator/quoted-speaker distinction."""
import datetime
from common import *
old=read(ROOT/'protocol_revisions/position_before_narrator_emotion/position_lock.json')
for t in read(ROOT/'position_tasks.json'):
    p=ROOT.parent/t['study']/'position_foils'/f"{t['model']}_{t['domain']}";assert not any(p.rglob('*.jsonl')) and not (p/'complete.json').exists()
files=[Path(r['path']) for r in old['files']]+[ROOT/'narrator_scope_score.py',ROOT/'POSITION_NARRATOR_AMENDMENT.md'];dump(ROOT/'position_lock.json',dict(files=[dict(path=str(p),sha256=digest(p)) for p in files],no_training=True,registered_after_initial_formal=True,narrator_emotion_variants=[2,3],prior_lock_sha=digest(ROOT/'protocol_revisions/position_before_narrator_emotion/position_lock.json')))
record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_specification_sha=digest(ROOT/'protocol_revisions/position_before_narrator_emotion/position_lock.json'),new_specification_sha=digest(ROOT/'position_lock.json'),no_diagnostic_model_predictions=True,no_training_or_selection_change=True,data_manifest_sha=digest(ROOT/'position_foils/data/emotion/manifest.json'));dump(ROOT/'POSITION_NARRATOR_REVISION.json',record)
ledger=read(ROOT/'submissions.json')
for r in ledger:
    if r['phase']=='position_foils':r['pre_gpu_narrator_revision']=record
dump(ROOT/'submissions.json',ledger);print('Narrator/quote distinction frozen before diagnostic GPU evaluation')
