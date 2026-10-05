#!/usr/bin/env bash
set -euo pipefail
: "${SLURM_JOB_ID:?Requires Slurm}"
: "${SLURM_ARRAY_TASK_ID:?Requires array}"
SNAPSHOT=$1
PYTHON=$2
MANIFEST=$3
cd "$SNAPSHOT"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
srun --ntasks=1 --kill-on-bad-exit=1 \
  "$PYTHON" -u -m experiments.state_handoff_diagnosis_v1.run \
  --manifest "$MANIFEST" --task-index "$SLURM_ARRAY_TASK_ID" --resume
