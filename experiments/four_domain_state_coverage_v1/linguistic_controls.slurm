#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=experiments/four_domain_state_coverage_v1/logs/%x_%A_%a.out
#SBATCH --error=experiments/four_domain_state_coverage_v1/logs/%x_%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
srun --ntasks=1 --gres=gpu:1 /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -u experiments/four_domain_state_coverage_v1/linguistic_controls.py --index "${SLURM_ARRAY_TASK_ID:?}"
