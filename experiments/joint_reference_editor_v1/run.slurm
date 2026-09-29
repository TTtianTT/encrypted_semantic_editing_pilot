#!/bin/bash
#SBATCH --job-name=joint-reference
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:10:00
#SBATCH --output=experiments/joint_reference_editor_v1/logs/slurm-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export RF_WALL_SECONDS="${RF_WALL_SECONDS:-540}"
srun .venv/bin/python "experiments/joint_reference_editor_v1/$1.py" "${@:2}"
