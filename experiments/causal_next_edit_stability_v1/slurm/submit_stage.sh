#!/usr/bin/env bash
set -euo pipefail
cd /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.causal-next-edit-worktree
source experiments/causal_next_edit_stability_v1/slurm/slurm_env.sh
python -m experiments.causal_next_edit_stability_v1.resource_guard "$@"
