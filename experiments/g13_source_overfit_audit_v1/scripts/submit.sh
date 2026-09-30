#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
exec .venv/bin/python experiments/g13_source_overfit_audit_v1/submit.py "$@"
