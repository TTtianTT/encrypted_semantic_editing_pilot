"""Zero-GPU controller releases only the recorded held original children."""
import subprocess
from common import *
record=read(ROOT/'atomic_preflight_submission.json');released=[]
for jid in record['held_children']:
    before=subprocess.check_output(['scontrol','show','job',jid,'--oneliner'],text=True)
    assert 'fdsc-v1-formal' in before and str(WORKTREE) in before and 'JobState=PENDING' in before
    subprocess.run(['scontrol','release',jid],check=True);released.append(jid)
dump(ROOT/'atomic_preflight_release.json',dict(released_children=released,gpu_requested=0,atomic_preflight_statuses=[dict(task=t,complete=(ROOT/'atomic_preflight'/f"{t['model']}_{t['domain']}_s{t['seed']}"/'complete.json').exists()) for t in read(ROOT/'atomic_preflight_tasks.json')]))
print(json.dumps(dict(released_children=released,gpu_requested=0)))
