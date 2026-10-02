#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=experiments/four_domain_state_coverage_v1/logs/%x_%j.out
#SBATCH --error=experiments/four_domain_state_coverage_v1/logs/%x_%j.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONUNBUFFERED=1
srun --ntasks=1 /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -u experiments/four_domain_state_coverage_v1/finalize.py
