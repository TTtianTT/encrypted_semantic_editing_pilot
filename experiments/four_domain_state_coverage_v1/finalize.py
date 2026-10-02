"""Final CPU-only evidence build, also safe for honest partial snapshots."""
import subprocess,datetime
from common import *

def call(script,*args,base=ROOT):
    subprocess.run([str(PYTHON),str(base/script),*args],check=True)

def main():
    call('account.py')
    confirmation=ROOT.parent/'space_relation_confirmation_v1'
    call('analyze.py');call('analyze.py','--study','space_relation_confirmation_v1')
    call('check_training_budget.py');call('check_training_budget.py',base=confirmation)
    call('source_pair_audit.py');call('transfer_audit.py');call('cross_backbone_audit.py');call('source_geometry_audit.py');call('component_audit.py');call('repair_regression_witnesses.py')
    call('collect_identity_probes.py');call('collect_language_controls.py');call('collect_position_foils.py');call('audit_spatial_scoring.py');call('artifact_audit.py');call('lineage_audit.py')
    call('publish.py');call('publish.py','--study','space_relation_confirmation_v1')
    call('publication_audit.py');call('publication_audit.py','--study','space_relation_confirmation_v1');call('extra_archives.py')
    call('scientific_answers.py');call('report.py');call('final_report.py')
    pending=[]
    for base,name in [(ROOT,'main'),(confirmation,'spatial_confirmation')]:
        for task in read(base/'tasks.json'):
            if task['phase'] not in ('formal','symbol'):continue
            path=base/'runs'/task['phase']/f"{task['model']}_{task['domain']}_s{task['seed']}"/'complete.json'
            if not path.exists():pending.append(dict(study=name,**task))
    for task in read(ROOT/'identity_probe_tasks.json'):
        p=ROOT.parent/task['study']/'runs/formal'/f"{task['model']}_{task['domain']}_s{task['seed']}"/'identity_probe/complete.json'
        if not p.exists():pending.append(dict(stage='identity_probe',**task))
    for task in read(ROOT/'linguistic_tasks.json'):
        p=ROOT.parent/task['study']/'language_controls'/f"{task['model']}_{task['domain']}"/'complete.json'
        if not p.exists():pending.append(dict(stage='linguistic_controls',**task))
    for task in read(ROOT/'position_tasks.json'):
        p=ROOT.parent/task['study']/'position_foils'/f"{task['model']}_{task['domain']}"/'complete.json'
        if not p.exists():pending.append(dict(stage='position_foils',**task))
    dump(ROOT/'FINALIZATION_STATUS.json',dict(status='artifacts_complete' if not pending else 'partial_technical_or_running',pending=pending,at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),git_commit_and_push='performed separately by supervising agent; no unattended git/network mutation'))
    call('progress.py')
    print('Final CPU build complete; missing tasks:',len(pending))

if __name__=='__main__':main()
