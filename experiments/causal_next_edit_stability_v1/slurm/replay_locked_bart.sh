#!/usr/bin/env bash
set -euo pipefail
CES_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CES_WORKTREE=$(cd "$CES_ROOT/../.." && pwd)
CES_REPLAY_STAGE=${1:-replay_bart}
if [[ ! "$CES_REPLAY_STAGE" =~ ^replay_[a-zA-Z0-9_]+$ ]]; then
  echo 'Use a fresh replay_ namespace containing letters, digits or underscores.' >&2
  exit 2
fi
cd "$CES_WORKTREE"
source "$CES_ROOT/slurm/slurm_env.sh"
# Manifest preparation is CPU-only. Every model forward uses the guarded Slurm entry.
python - "$CES_REPLAY_STAGE" <<'PY'
import sys
from experiments.causal_next_edit_stability_v1.audit import make_stage
from experiments.causal_next_edit_stability_v1.common import ROOT,read,sha
lock=read(ROOT/'results/final_test_lock.json')
inputs=dict(lock['input_hashes'])
inputs['results/final_test_lock.json']=sha(ROOT/'results/final_test_lock.json')
make_stage(sys.argv[1],[('bart',seed) for seed in (42,43,44)],'03:00:00',dict(mode='test',input_hashes=inputs))
PY
bash "$CES_ROOT/slurm/submit_stage.sh" \
  --config "$CES_ROOT/configs/${CES_REPLAY_STAGE}.json" \
  --manifest "$CES_ROOT/configs/${CES_REPLAY_STAGE}_tasks.json"
