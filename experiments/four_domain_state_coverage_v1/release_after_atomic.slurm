#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=512M
#SBATCH --time=00:10:00
#SBATCH --output=experiments/four_domain_state_coverage_v1/logs/release-atomic-%j.out
#SBATCH --error=experiments/four_domain_state_coverage_v1/logs/release-atomic-%j.err
set -euo pipefail
../.venv/bin/python experiments/four_domain_state_coverage_v1/release_after_atomic.py
