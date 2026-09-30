#!/bin/bash
#SBATCH --job-name=g13-source-audit
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --output=experiments/g13_source_overfit_audit_v1/logs/%A_%a.out
#SBATCH --error=experiments/g13_source_overfit_audit_v1/logs/%A_%a.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
if [[ "${G13_PHASE:?}" == smoke ]]; then
  srun --ntasks=1 --gres=gpu:1 .venv/bin/python -u experiments/g13_source_overfit_audit_v1/run.py --smoke
else
  srun --ntasks=1 --gres=gpu:1 .venv/bin/python -u experiments/g13_source_overfit_audit_v1/run.py --seed-index "${SLURM_ARRAY_TASK_ID:?}"
fi
