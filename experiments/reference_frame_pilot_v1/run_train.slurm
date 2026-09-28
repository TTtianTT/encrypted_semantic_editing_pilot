#!/bin/bash
#SBATCH --job-name=reference-frame-train
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=00:15:00
#SBATCH --signal=B:USR1@90
#SBATCH --output=experiments/reference_frame_pilot_v1/logs/slurm-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export RF_WALL_SECONDS=840
srun .venv/bin/python experiments/reference_frame_pilot_v1/train.py --method "$1" --seed "$2"
