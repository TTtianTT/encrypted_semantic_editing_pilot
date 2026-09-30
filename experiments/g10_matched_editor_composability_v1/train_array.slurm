#!/bin/bash
#SBATCH --job-name=g10-train
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:20:00
#SBATCH --array=0-2%2
#SBATCH --output=experiments/g10_matched_editor_composability_v1/logs/train-%A_%a.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
rank=(8 16 32)
srun .venv/bin/python experiments/g10_matched_editor_composability_v1/train.py --rank "${rank[$SLURM_ARRAY_TASK_ID]}"
