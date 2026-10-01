#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/account.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/analyze.py
