#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=experiments/four_domain_state_coverage_v1/logs/position-%A_%a.out
#SBATCH --error=experiments/four_domain_state_coverage_v1/logs/position-%A_%a.err
set -euo pipefail
export OMP_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
srun ../.venv/bin/python experiments/four_domain_state_coverage_v1/position_dispatch.py --index "$SLURM_ARRAY_TASK_ID"
