#!/bin/bash
#SBATCH --job-name=g14-handoff
#SBATCH --partition=B300q
#SBATCH --exclude=node01
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --array=0-2%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --output=experiments/g14_matched_state_handoff_v1/logs/%A_%a.out
#SBATCH --error=experiments/g14_matched_state_handoff_v1/logs/%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
srun --ntasks=1 --gres=gpu:1 .venv/bin/python -u experiments/g14_matched_state_handoff_v1/run.py --seed-index "${SLURM_ARRAY_TASK_ID:?}"
