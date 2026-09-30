#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
.venv/bin/python experiments/g13_source_overfit_audit_v1/account.py
.venv/bin/python experiments/g13_source_overfit_audit_v1/analyze.py
