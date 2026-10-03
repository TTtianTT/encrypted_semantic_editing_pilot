"""Journal a scoring revision before the dependent diagnostic GPU stages."""
import datetime
from common import *

def main():
    archive=ROOT/'protocol_revisions/before_spatial_first_person_aliases'
    extra=[ROOT/name for name in ('spatial_paraphrase_score.py','SPATIAL_PARAPHRASE_AMENDMENT.md','check_spatial_paraphrases.py','SPATIAL_PARAPHRASE_CHECK.json','space_scope_guard.py','quantity_guard.py')]
    for t in read(ROOT/'linguistic_tasks.json'):
        p=ROOT.parent/t['study']/'language_controls'/f"{t['model']}_{t['domain']}"
        assert not list(p.rglob('*.jsonl')) and not (p/'complete.json').exists()
    for t in read(ROOT/'position_tasks.json'):
        p=ROOT.parent/t['study']/'position_foils'/f"{t['model']}_{t['domain']}"
        assert not list(p.rglob('*.jsonl')) and not (p/'complete.json').exists()
    records={}
    for name in ('linguistic_lock.json','position_lock.json'):
        old=read(archive/name);absolute=name=='position_lock.json';files=[]
        for r in old['files']:
            p=Path(r['path']) if absolute else ROOT/r['path'];files.append(p)
            # Rebuilding the position fixtures may change no underlying bytes.
            if '/data/' in str(p):assert digest(p)==r['sha256'],p
        files+=extra
        unique=list(dict.fromkeys(files))
        new=dict(old,files=[dict(path=str(p) if absolute else str(p.relative_to(ROOT)),sha256=digest(p)) for p in unique],prior_lock_sha=digest(archive/name),spatial_equivalent_expression_scoring=True,revision_registered_before_diagnostic_gpu=True)
        dump(ROOT/name,new);records[name]=dict(prior_sha=digest(archive/name),new_sha=digest(ROOT/name))
    record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),locks=records,no_diagnostic_model_predictions=True,no_training_or_selection_change=True,formal_scoring_code_and_scores_unchanged=True,posthoc_formal_adjudication_separate=True,checks=read(ROOT/'SPATIAL_PARAPHRASE_CHECK.json'))
    dump(ROOT/'SPATIAL_PARAPHRASE_REVISION.json',record);ledger=read(ROOT/'submissions.json')
    for r in ledger:
        if r['phase'] in ('linguistic_controls','position_foils'):r['pre_gpu_spatial_alias_revision']=record
    dump(ROOT/'submissions.json',ledger);print('Spatial equivalent-expression scorer frozen before both diagnostic stages.')

if __name__=='__main__':main()
