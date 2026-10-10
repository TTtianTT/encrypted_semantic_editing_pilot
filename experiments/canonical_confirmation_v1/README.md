# Canonical confirmation and closure

This closes the time-domain exploration with frozen BART, rank-16 affine editors,
optimizer controls, fresh five-seed confirmation, and a person-domain replication.
The protocol was committed before fresh-world predictions in commit `946b5fa`.
See [protocol.json](protocol.json) and [control_protocol.json](control_protocol.json).

The time training set remains the same 96 worlds. Evaluation uses 160 newly
generated semantic cores, disjoint from all four explicitly fingerprinted legacy
world files. Closure and interventions use the fixed first 80 of these worlds.
Person replication uses 96 original training worlds and 80 new evaluation worlds.
State 1↔2 is mask-aligned; state 0 and structural template 3 are reported as
coverage boundaries whenever their single-step prerequisite fails.

Run GPU phases with `FINAL_PHASE` and [job.slurm](job.slurm), submitted using
`sbatch` and executed with `srun`. The user changed the resource ceiling from one
to at most two simultaneous GPUs in [resource_amendment.json](resource_amendment.json).
This resource-only amendment preserves the original scientific protocol. Phases are:
`optimizer_controls`, `extract_fresh`, `train_final`, `eval_final`, `closure_final`,
`mechanism_final`, then `loss_old`. No backbone update is permitted. The final
phase only measures historical likelihoods and a synchronized cost reference.
Its cost benchmark is derived after locking and never selects a method.

Derived CPU analyses are `analyze_existing`, `horizon_existing`,
`summarize_controls`, `summarize_final`, and `audit_final`. Raw predictions are
retained locally and published as deterministic gzip archives with uncompressed
SHA256 hashes. Weights, GPU logs, and encoder caches remain local; the checkpoint
index fingerprints them for reproduction.

Previously local derived computation is replayed using `CPU_PHASE=replay` and
[job_cpu.slurm](job_cpu.slurm), which requests no GPU. After all GPU phases finish,
`CPU_PHASE=finalize` computes summaries, audits, archives, and the report using
the same `sbatch`/`srun` CPU workflow. The run ledger records allocation overlap.

RRR and canonical reencoding are deterministic reference maps, evaluated once;
their results do not constitute five independent training seeds. C1/C3 seeds
42–44 reuse the fixed previous endpoints; seeds 45–46 are newly trained, and
dense C4 replays must match old weights at updates 10, 25, and 50. Report each
seed separately and bootstrap semantic worlds for aggregates over transitions.

Finite 50-step success does not establish arbitrary-length closure. Mask-aligned
fitting does not solve length-changing transitions. Lower residual production
does not imply robustness to injected residuals. Scalar residual-risk curves are
descriptive and must retain condition-specific calibration and held-world checks.
