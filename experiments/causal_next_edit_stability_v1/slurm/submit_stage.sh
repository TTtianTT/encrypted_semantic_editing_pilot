#!/usr/bin/env bash
set -euo pipefail
cd /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.causal-next-edit-worktree
source experiments/causal_next_edit_stability_v1/slurm/slurm_env.sh
if [[ "${1:-}" == "--extend-walltime" ]]; then
  # Resource-only override: no scientific config, task hash or output is changed.
  python - "$@" <<'PY'
import re,subprocess,sys
from datetime import datetime
from experiments.causal_next_edit_stability_v1.resource_guard import locked,refresh,LEDGER
from experiments.causal_next_edit_stability_v1.common import read,dump
_,flag,jid,walltime=sys.argv
assert flag=='--extend-walltime' and jid.isdigit()
assert re.fullmatch(r'\d{2}:\d{2}:\d{2}',walltime)
hours=sum(int(x)*factor for x,factor in zip(walltime.split(':'),(1,1/60,1/3600)))
with locked():
    ledger=refresh(read(LEDGER))
    sub=next(s for s in ledger['submissions'] if s['job_id']==jid)
    assert not sub['terminal'] and sub['gpus_per_task']==1
    assert all(s['terminal'] or s['job_id']==jid for s in ledger['submissions'])
    reservation=len(sub['indices'])*hours*sub['gpus_per_task']
    assert ledger['gpu_hours']+reservation<=ledger['cap_gpu_hours']
    record=dict(time=datetime.now().isoformat(),requested_walltime=walltime,conservative_reserved_gpu_hours=reservation,
        reason='Observed generation throughput requires more allocation time; scientific configuration and seeds unchanged',
        command=['scontrol','update','JobId='+jid,'TimeLimit='+walltime])
    sub.setdefault('resource_only_walltime_overrides',[]).append(record)
    dump(LEDGER,ledger)
    result=subprocess.run(record['command'],text=True,capture_output=True)
    record.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    dump(LEDGER,ledger)
    # An array update can succeed for pending children and fail for running ones.
    ledger=refresh(ledger);sub=next(s for s in ledger['submissions'] if s['job_id']==jid)
    record=sub['resource_only_walltime_overrides'][-1]
    record['observed_child_limit_minutes']={r['array_id']:r['limit_minutes'] for r in sub['allocations']}
    sub['reserved_gpu_hours']=sum(r['limit_minutes']/60 for r in sub['allocations'])
    dump(LEDGER,ledger)
    print(record)
    sys.exit(result.returncode)
PY
  exit
fi
if [[ "${1:-}" == "--resume-walltime" ]]; then
  # Same scientific manifest and task hashes; only the scheduler walltime changes.
  python - "$@" <<'PY'
import argparse,re
from pathlib import Path
from experiments.causal_next_edit_stability_v1 import resource_guard as guard
from experiments.causal_next_edit_stability_v1.common import read,dump
p=argparse.ArgumentParser();p.add_argument('--resume-walltime',required=True);p.add_argument('--config',required=True,type=Path);p.add_argument('--manifest',required=True,type=Path);a=p.parse_args()
assert re.fullmatch(r'\d{2}:\d{2}:\d{2}',a.resume_walltime)
original=read(a.config)
hours=sum(int(x)*factor for x,factor in zip(a.resume_walltime.split(':'),(1,1/60,1/3600)))
def resource_read(path):
    obj=read(path)
    if Path(path).resolve()==a.config.resolve():obj=dict(obj,walltime=a.resume_walltime,walltime_hours=hours)
    return obj
def marked_dump(path,obj):
    if isinstance(obj,dict) and 'command' in obj and 'reserved_gpu_hours' in obj:
        obj['resource_only_walltime_override']=dict(original_walltime=original['walltime'],allocation_walltime=a.resume_walltime,reason='Resume confirmed technical timeout; scientific config/task hashes unchanged')
    return dump(path,obj)
guard.read=resource_read;guard.dump=marked_dump
guard.submit(a.config,a.manifest,resume=True)
PY
  exit
fi
python -m experiments.causal_next_edit_stability_v1.resource_guard "$@"
