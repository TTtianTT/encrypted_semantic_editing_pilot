#!/usr/bin/env bash
#SBATCH --job-name=g17-main
#SBATCH --partition=B300q
#SBATCH --exclude=node01
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --array=0-2%2
#SBATCH --output=experiments/g17_state_source_transfer_v1/logs/%x_%A_%a.out
#SBATCH --error=experiments/g17_state_source_transfer_v1/logs/%x_%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
srun --ntasks=1 --gres=gpu:1 .venv/bin/python -u experiments/g17_state_source_transfer_v1/run.py --seed-index "${SLURM_ARRAY_TASK_ID:?}"
