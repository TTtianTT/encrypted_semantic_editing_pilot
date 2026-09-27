#!/bin/bash
#SBATCH --job-name=ese-pilot-A
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --time=11:00:00
#SBATCH --output=logs/slurm-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export PILOT_WALL_SECONDS="${PILOT_WALL_SECONDS:-39000}"
nvidia-smi
srun .venv/bin/python scripts/pilot.py "$@"
