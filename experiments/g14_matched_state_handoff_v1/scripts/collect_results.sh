#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
.venv/bin/python experiments/g14_matched_state_handoff_v1/account.py
.venv/bin/python experiments/g14_matched_state_handoff_v1/analyze.py
