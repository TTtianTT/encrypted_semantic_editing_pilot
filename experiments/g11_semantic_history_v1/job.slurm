#!/bin/bash
#SBATCH --job-name=g11-history
#SBATCH --partition=B300q
#SBATCH --exclude=node01
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=experiments/g11_semantic_history_v1/logs/%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 RF_WALL_SECONDS=1620
srun .venv/bin/python experiments/g11_semantic_history_v1/gpu.py "${G11_PHASE:?}"
