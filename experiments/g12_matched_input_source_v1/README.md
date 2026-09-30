# G12 reproduction

Run at repository root with the existing `.venv`. Only the new directory is writable; keep G10/G11/v3 unchanged. Current published data are locked; preparation refuses to overwrite. Fresh inference must use an isolated result copy, retaining worlds/config but archiving old outputs/local activations/cohort lock first. Do not mix new cohort hashes with old next outputs.

```bash
.venv/bin/python experiments/g12_matched_input_source_v1/prepare.py
.venv/bin/python experiments/g12_matched_input_source_v1/submit.py preflight
# Wait for completion; refresh the global allocation ledger before each subsequent stage.
.venv/bin/python experiments/g12_matched_input_source_v1/account.py
.venv/bin/python experiments/g12_matched_input_source_v1/submit.py train
# The entire array must finish (A/B per seed; max2 GPUs). No concurrent evaluation.
.venv/bin/python experiments/g12_matched_input_source_v1/account.py
.venv/bin/python experiments/g12_matched_input_source_v1/submit.py current
.venv/bin/python experiments/g12_matched_input_source_v1/account.py
.venv/bin/python experiments/g12_matched_input_source_v1/submit.py finish
.venv/bin/python experiments/g12_matched_input_source_v1/account.py
.venv/bin/python experiments/g12_matched_input_source_v1/analyze.py
.venv/bin/python experiments/g12_matched_input_source_v1/audit.py
.venv/bin/python experiments/g12_matched_input_source_v1/audit_supplement.py
.venv/bin/python experiments/g12_matched_input_source_v1/components.py
.venv/bin/python experiments/g12_matched_input_source_v1/report.py
```

The submitter uses sbatch B300q/exclude node01 and checks the global phase barrier/reservations; every job invokes srun. No login-node CUDA. account.py records array task allocations once, not steps. Incomplete training resumes optimizer/RNG/update index from local files without extending200 updates. Fully completed arms validate and reuse final weights. Inference resumes shard outputs; activation tensors and optimizer restores stay local. No post-training best checkpoint selection; no new experiments.
