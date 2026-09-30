#!/bin/bash
#SBATCH --job-name=g12-input-source
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --array=0-2%2
#SBATCH --time=00:30:00
#SBATCH --output=experiments/g12_matched_input_source_v1/logs/%A_%a.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
srun .venv/bin/python experiments/g12_matched_input_source_v1/train_pair.py --seed-index "${SLURM_ARRAY_TASK_ID:?}"
