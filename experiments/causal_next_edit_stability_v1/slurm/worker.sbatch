#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
set -euo pipefail
: "${SLURM_JOB_ID:?Must run in Slurm}"
: "${SLURM_ARRAY_TASK_ID:?Even smoke is a one-element array}"
cd "$1"
source "$2"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export TOKENIZERS_PARALLELISM=false
srun --ntasks=1 --kill-on-bad-exit=1 python -u -m experiments.causal_next_edit_stability_v1.run_stage --config "$3" --manifest "$4" --task-index "$SLURM_ARRAY_TASK_ID" --resume
if [[ "$3" == */configs/aggregate_cpu.json ]]; then
  srun --ntasks=1 --kill-on-bad-exit=1 bash experiments/causal_next_edit_stability_v1/slurm/finish_cpu.sh
fi
