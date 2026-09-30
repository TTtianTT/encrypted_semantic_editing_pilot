# G13 source / overfit audit

Independent branch: `experiment/g13-source-overfit-audit-v1`, based on verified G12 HEAD `389bb85160df6311cc866fc573f73a24b3d87a09`. Only this directory is added; old experiments are read-only dependencies. Start with REPORT.md, PROTOCOL.md and BASELINE_AUDIT.md.

Use the repository's existing `.venv` and read-only `models/bart-base` artifacts. `baseline_audit.json` records exact Original/G12 checkpoint paths and SHA256; `data/lock.json` records scientific inputs and dependencies. No base weights or latent caches are committed. The temporary shared worktree uses links to existing model/environment, without copying or upgrading them.

CPU-only first-run preparation (refuses to overwrite a lock):

```bash
.venv/bin/python experiments/g13_source_overfit_audit_v1/prepare.py
.venv/bin/python experiments/g13_source_overfit_audit_v1/tests.py
.venv/bin/python experiments/g13_source_overfit_audit_v1/tests_analysis.py
.venv/bin/python experiments/g13_source_overfit_audit_v1/tests_rollout.py
```

GPU runs, always `sbatch` and `srun`, one card per seed, at most two simultaneously:

```bash
bash experiments/g13_source_overfit_audit_v1/scripts/submit.sh smoke
# wait for smoke COMPLETED and smoke_test.json passed
bash experiments/g13_source_overfit_audit_v1/scripts/submit.sh main
```

The submission manifest prevents blind duplicates, checks active G13 jobs and the cumulative request budget. Historical engineering retry is explicitly recorded in engineering_retry_1.json, including unchanged data/schedule/scientific config. Never retry for an unfavorable result. `run.py --seed-index` reads the manifest mapping; four independent fresh R/optimizer states run sequentially. G caches are created/locked before any R training. Resume optimizer/editor/RNG files live under ignored `local/`; final/best-dev editor-only weights are tracked. All five snapshot diagnostics are uploaded; redundant snapshot weights remain local.

CPU aggregation after allocations finish:

```bash
bash experiments/g13_source_overfit_audit_v1/scripts/collect_results.sh
```

For the delivery's enriched resource fields and measured concurrency, use the CPU-only `finalize_account.py` followed by `analyze.py`. This leaves the pre-training locked `account.py` unchanged, adds raw allocation IDs/account/QOS/time limits, and computes peak concurrent GPUs from allocation start/end times. It changes no scientific inputs or GPU execution:

```bash
.venv/bin/python experiments/g13_source_overfit_audit_v1/finalize_account.py
.venv/bin/python experiments/g13_source_overfit_audit_v1/analyze.py
.venv/bin/python experiments/g13_source_overfit_audit_v1/finalize_delivery.py
```

`finalize_delivery.py` verifies all twelve completed trainings, the unchanged scientific lock, final/best checkpoint hashes, frozen-operator outputs, shared schedules, instance/token counts, source rotation, result row counts and actual resource bounds. It writes `delivery_verification.json` and `artifact_manifest.json` with an explicit hash inventory of files allowed by Git ignore rules. It excludes large local caches, base weights and optimizer resumes.

`account.py` queries allocation-level sacct only, excluding array parent and job steps. `analyze.py` rescores every output, generates two core tables, transition counts, training curves, source and rollout tables, paired world bootstrap/Wilson intervals, actual cases and report. For an uploaded result checkout, aggregation also reads `per_example.jsonl.gz` and `learning_per_example.jsonl.gz` without requiring ignored raw shards. Those archives preserve raw text, expected world facts, parsed outputs and per-step/source scores. Recover the requested plain file with:

```bash
gzip -dc experiments/g13_source_overfit_audit_v1/per_example.jsonl.gz > experiments/g13_source_overfit_audit_v1/per_example.jsonl
```

Precise local plain-file path/hash are recorded in per_example_manifest.json. Reports use fixed step200 as primary; best-dev is separate. The 40-cell natural macro covers all original legal status/perspective/date transitions plus the legal source offset+4, disclosed outside T0 training support. Main fixed-source and rollout denominators contain160 recorded-plan worlds per confirmation split; additional replay-only worlds never inflate that denominator. No on-policy or depth4/5 training occurs.
