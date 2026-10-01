#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
.venv/bin/python experiments/g14_matched_state_handoff_v1/submit.py "${1:?smoke or main}"
