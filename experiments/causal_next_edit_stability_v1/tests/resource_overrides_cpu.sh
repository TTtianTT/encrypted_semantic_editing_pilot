#!/usr/bin/env bash
set -euo pipefail
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python - <<'PY'
import contextlib
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from experiments.causal_next_edit_stability_v1 import resource_guard as guard
from experiments.causal_next_edit_stability_v1.common import ROOT,read,dump,sha

bodies=(ROOT/'slurm/submit_stage.sh').read_text().split("<<'PY'\n")
extend=bodies[1].split('\nPY\n')[0]
resume=bodies[2].split('\nPY\n')[0]
checks=[]
with tempfile.TemporaryDirectory() as directory:
    tmp=Path(directory);config=tmp/'config.json';manifest=tmp/'manifest.json'
    dump(config,dict(stage='test',gpus=1,walltime='01:00:00',walltime_hours=1))
    digest=sha(config)
    def fake_submit(cp,mp,resume=False):
        assert resume
        c=guard.read(cp)
        assert c['walltime']=='03:00:00' and c['walltime_hours']==3
        guard.dump(tmp/'intent.json',dict(command=['sbatch','--time='+c['walltime']],reserved_gpu_hours=3))
    with patch.object(guard,'submit',fake_submit),patch.object(guard,'read',guard.read),patch.object(guard,'dump',guard.dump),patch.object(sys,'argv',['-', '--resume-walltime','03:00:00','--config',str(config),'--manifest',str(manifest)]):
        exec(compile(resume,'resource_resume','exec'),{})
    assert sha(config)==digest
    assert read(tmp/'intent.json')['resource_only_walltime_override']['original_walltime']=='01:00:00'
    checks.append('retry changes scheduler resources without modifying scientific config')

    ledger=tmp/'ledger.json'
    def sample(cap=40):
        return dict(cap_gpu_hours=cap,gpu_hours=2,submissions=[dict(job_id='123',gpus_per_task=1,terminal=False,indices=[0,1,2],allocations=[dict(array_id='123_'+str(i),limit_minutes=t) for i,t in enumerate([60,60,180])])])
    class Denied:
        returncode=1;stdout='';stderr='123_0-1: Access/permission denied'
    dump(ledger,sample())
    with patch.object(guard,'LEDGER',ledger),patch.object(guard,'locked',contextlib.nullcontext),patch.object(guard,'refresh',lambda x:x),patch('subprocess.run',return_value=Denied()),patch.object(sys,'argv',['-','--extend-walltime','123','03:00:00']):
        try:exec(compile(extend,'resource_extend','exec'),{})
        except SystemExit as ex:assert ex.code==1
    sub=read(ledger)['submissions'][0]
    assert sub['reserved_gpu_hours']==5
    assert sub['resource_only_walltime_overrides'][0]['returncode']==1
    checks.append('partial array update preserves denial and accounts observed child limits')
    dump(ledger,sample(cap=4))
    with patch.object(guard,'LEDGER',ledger),patch.object(guard,'locked',contextlib.nullcontext),patch.object(guard,'refresh',lambda x:x),patch('subprocess.run') as command,patch.object(sys,'argv',['-','--extend-walltime','123','03:00:00']):
        try:exec(compile(extend,'resource_budget','exec'),{})
        except AssertionError:pass
        else:raise AssertionError('budget should reject')
        command.assert_not_called()
    checks.append('extension exceeding conservative budget is rejected before Slurm mutation')
dump(ROOT/'results/resource_override_CPU_checks.json',dict(passed=True,checks=checks,no_GPU_execution=True,no_real_Slurm_mutations=True))
print(checks)

PY
