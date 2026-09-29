#!/bin/bash
#SBATCH --job-name=g8-basin
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=03:00:00
#SBATCH --output=experiments/decoder_basin_anisotropy_v1/g8-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
if [[ "${G8_PILOT:-0}" == 1 ]]; then
  srun .venv/bin/python experiments/decoder_basin_anisotropy_v1/extract.py --backbone "${G8_BACKBONE:?}" --pilot
elif [[ -n "${G8_ONLY_SPLIT:-}" ]]; then
  srun .venv/bin/python experiments/decoder_basin_anisotropy_v1/extract.py --backbone "${G8_BACKBONE:?}" --only-split "${G8_ONLY_SPLIT}"
else
  srun .venv/bin/python experiments/decoder_basin_anisotropy_v1/extract.py --backbone "${G8_BACKBONE:?}"
fi
