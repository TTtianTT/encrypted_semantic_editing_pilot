#!/bin/bash
#SBATCH --job-name=g15-eval-resume
#SBATCH --partition=B300q
#SBATCH --exclude=node01
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --output=experiments/g15_self_state_transfer_v1/logs/%j_resume.out
#SBATCH --error=experiments/g15_self_state_transfer_v1/logs/%j_resume.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
srun --ntasks=1 --gres=gpu:1 .venv/bin/python -u experiments/g15_self_state_transfer_v1/run.py --seed-index "${G15_RETRY_INDEX:?}"
