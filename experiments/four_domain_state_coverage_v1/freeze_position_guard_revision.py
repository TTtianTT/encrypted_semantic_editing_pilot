"""CPU-only record of a stricter observer-binding check BEFORE diagnostic GPU work."""
import subprocess,shutil,datetime
from common import *

def main():
    dest=ROOT/'protocol_revisions/position_before_view_guard';dest.mkdir(parents=True,exist_ok=True);old=read(ROOT/'position_lock.json');dump(dest/'position_lock.json',old)
    item=next(r for r in old['files'] if Path(r['path']).name=='position_spec.py');relative=str(Path(item['path']).relative_to(WORKTREE));oldcode=subprocess.check_output(['git','show','HEAD:'+relative],cwd=WORKTREE);(dest/'position_spec.py').write_bytes(oldcode);assert digest(dest/'position_spec.py')==item['sha256']
    shutil.copyfile(ROOT/'POSITION_FOILS_PLAN.md',dest/'POSITION_FOILS_PLAN.md')
    for t in read(ROOT/'position_tasks.json'):
        folder=ROOT.parent/t['study']/'position_foils'/f"{t['model']}_{t['domain']}";assert not any(folder.rglob('*.jsonl')) and not (folder/'complete.json').exists(),'Cannot amend silently after diagnostic model evaluation'
    text=(ROOT/'POSITION_FOILS_PLAN.md').read_text();text+='\n\nPre-GPU parser safety amendment: a separate space_scope_guard checks every\nexplicit target-A first-person or named-viewpoint relation against A\u2019s gold\nrelation. A first B viewpoint cannot substitute for A. This only removes false\npositive assessments and does not change inputs, weights, updates or selection.\nCPU controls:1344 correct gold texts and56 adversarial named-viewpoint swaps;\nthe old parser incorrectly accepts all56 negatives. Original formal parser and\nits raw outputs remain frozen. Existing actual predictions receive a separate\nconservative audit, with no retroactive gate/checkpoint change. Old diagnostic\nprotocol/code are archived before any diagnostic GPU call.\n';(ROOT/'POSITION_FOILS_PLAN.md').write_text(text)
    files=[Path(r['path']) for r in old['files']]+[ROOT/p for p in ('space_scope_guard.py','check_space_scope_guard.py','SPACE_SCOPE_GUARD_CHECK.json')];dump(ROOT/'position_lock.json',dict(files=[dict(path=str(p),sha256=digest(p)) for p in files],no_training=True,registered_after_initial_formal=True,pre_gpu_observer_guard_revision=True,old_lock_sha=digest(dest/'position_lock.json')))
    record=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),diagnostic_gpu_predictions_exist=False,old_specification_sha=digest(dest/'position_lock.json'),new_specification_sha=digest(ROOT/'position_lock.json'),old_code_sha=item['sha256'],new_code_sha=digest(ROOT/'position_spec.py'),reason='Independent adversarial observer-binding negatives reveal first-viewpoint fallback false positives. Strict guard added before diagnostic GPU phase.',model_inputs_or_weights_changed=False,existing_formal_scores_preserved=True,cpu_check_sha=digest(ROOT/'SPACE_SCOPE_GUARD_CHECK.json'));dump(ROOT/'POSITION_GUARD_REVISION.json',record)
    ledger=read(ROOT/'submissions.json')
    for r in ledger:
        if r['phase']=='position_foils':r['pre_gpu_guard_revision']=record
    dump(ROOT/'submissions.json',ledger);print('Recorded pre-GPU position guard revision')

if __name__=='__main__':main()
