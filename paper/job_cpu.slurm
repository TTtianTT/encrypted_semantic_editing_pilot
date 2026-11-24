#!/bin/bash
#SBATCH --job-name=paper
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=paper/logs/%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
srun /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python "paper/${SCRIPT:?}" ${ARGS:-}
