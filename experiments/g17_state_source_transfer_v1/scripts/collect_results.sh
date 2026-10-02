#!/usr/bin/env bash
set -euo pipefail
.venv/bin/python experiments/g17_state_source_transfer_v1/account.py
.venv/bin/python experiments/g17_state_source_transfer_v1/analyze.py
