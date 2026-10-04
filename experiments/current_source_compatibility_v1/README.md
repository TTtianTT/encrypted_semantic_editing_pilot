# Current-source compatibility v1

This study starts at0b73738 on independent branch `experiment/current-source-compatibility-v1`. Read EXPERIMENT_PLAN.md, scientific_lock.json, SOURCE_LINEAGE.json, CPU_AUDIT.json, SMOKE_AUDIT.json, CPU_SMOKE_VERIFICATION.json and ENGINEERING_EVENTS.json. The original backbone/editor/data are read-only; old natural tests are unchanged. No effect is assumed.

Commands from the original repository directory:

```bash
.venv/bin/python .current-source-worktree/experiments/current_source_compatibility_v1/submit.py preflight
.venv/bin/python .current-source-worktree/experiments/current_source_compatibility_v1/submit.py formal
.venv/bin/python .current-source-worktree/experiments/current_source_compatibility_v1/account.py
.venv/bin/python .current-source-worktree/experiments/current_source_compatibility_v1/analyze.py
```

Formal submission requires all three T0 gates and pre-training diagnostic sets to finish. One array%2 per phase; every existing account GPU job is a dependency, regardless of its project. The first smoke is one card only. Never cancel unrelated jobs, start an extra quick test, or override Slurm CUDA_VISIBLE_DEVICES.

Resume only after all previous GPU allocations end:

```bash
.venv/bin/python .current-source-worktree/experiments/current_source_compatibility_v1/submit.py formal --resume
```

The same locked scheduler returns an already-submitted phase rather than duplicate it. A resume includes only seeds missing complete markers. It skips finished methods/checkpoints/shards, resumes the last completed optimizer update (saved each update), restores optimizer and RNG, and reads the exact source snapshot/cache for its refresh window. An incomplete refresh regenerates only missing batches using that window's original frozen snapshot. Check resource_usage.json and Slurm stdout/stderr before recovery; low performance is never a missing task.

All GPU model loading, generation, training and evaluation are guarded by Slurm+srun; only CPU data/audit/report operations run outside an allocation. Large tensor caches, optimizer states and raw predictions remain on shared storage under `local/` and `runs/`. Published small editor exports and deterministic gzip prediction archives/indexes allow review without committing backbone weights or large source tensors. SOURCE_LINEAGE records U as another seed's original T0, never an extra independent training replicate.

Raw semantic score is the original finite evaluator; unknown wording is unresolved. Grammar includes controlled content completeness and is not an unrestricted English grammaticality judge. Prefix error fields separate known relative-state mismatch, missing/changed non-target content, unresolved relative state, completeness and termination. Overlapping categories are labelled as such. F/R never filter or replace errors. Full2 is the primary direct repair measure; method-dependent conditional denominators are descriptive and are not used alone for ranking.

The eight legal five-operation paths are evaluated separately from exhaustive two-step tests; their initial-state/sequence distribution differs. Never compare their length2 versus exhaustive full2 without identifying that distinction. World-cluster bootstrap intervals describe the fixed models and exclude all training randomness. Always inspect all seeds and old T0-success losses, even when macro is stable.
