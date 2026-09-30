#!/bin/bash
#SBATCH --job-name=g12-inference
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=experiments/g12_matched_input_source_v1/logs/%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
if [ "${G12_PHASE:?}" = preflight ]; then
 srun .venv/bin/python experiments/g12_matched_input_source_v1/train_pair.py --preflight
else
 srun .venv/bin/python experiments/g12_matched_input_source_v1/evaluate.py "${G12_PHASE}"
fi
