#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
.venv/bin/python experiments/g15_self_state_transfer_v1/submit.py "${1:?smoke or main}"
