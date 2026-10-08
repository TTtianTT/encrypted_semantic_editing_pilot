#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
set -euo pipefail
: "${SLURM_JOB_ID:?Slurm required}"
: "${SLURM_ARRAY_TASK_ID:?Registered array required}"
: "${RUN_SNAPSHOT:?Snapshot required}"
: "${MANIFEST:?Manifest required}"
: "${PYTHON_BIN:?Audited Python required}"
TASK_STORAGE=/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-control-v1
mkdir -p "$TASK_STORAGE/tmp" "$TASK_STORAGE/cache"
export TMPDIR="$TASK_STORAGE/tmp"
export MPLCONFIGDIR="$TASK_STORAGE/cache/matplotlib"
export PIP_CACHE_DIR="$TASK_STORAGE/cache/pip"
export TORCHINDUCTOR_CACHE_DIR="$TASK_STORAGE/cache/torchinductor"
export TRITON_CACHE_DIR="$TASK_STORAGE/cache/triton"
cd "$RUN_SNAPSHOT"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export TOKENIZERS_PARALLELISM=false
srun --kill-on-bad-exit=1 --unbuffered "$PYTHON_BIN" -m experiments.decoder_readout_invariance_editing_v1.run_stage --manifest "$MANIFEST" --task-index "$SLURM_ARRAY_TASK_ID" --resume
