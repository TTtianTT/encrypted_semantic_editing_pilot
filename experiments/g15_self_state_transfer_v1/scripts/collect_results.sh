#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
.venv/bin/python experiments/g15_self_state_transfer_v1/account.py
.venv/bin/python experiments/g15_self_state_transfer_v1/analyze.py
