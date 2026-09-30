# G11 reproduction

Run from repository root with the existing `.venv`. No training. Baseline b07abb4. New-world data and cohorts must not be overwritten after lock.

```bash
.venv/bin/python experiments/g11_semantic_history_v1/prepare.py
sbatch --export=ALL,G11_PHASE=current experiments/g11_semantic_history_v1/job.slurm
# After the current job completes: account its allocation; verify cohort_lock exists.
.venv/bin/python experiments/g11_semantic_history_v1/account.py --job JOB_ID --phase current
sbatch --export=ALL,G11_PHASE=next experiments/g11_semantic_history_v1/job.slurm
.venv/bin/python experiments/g11_semantic_history_v1/account.py --job JOB_ID --phase next
.venv/bin/python experiments/g11_semantic_history_v1/analyze.py
.venv/bin/python experiments/g11_semantic_history_v1/provenance.py
.venv/bin/python experiments/g11_semantic_history_v1/audit.py
.venv/bin/python experiments/g11_semantic_history_v1/report.py
```

Submit stages sequentially (one GPU maximum). Before each submission, require allocated seconds plus requested 1800-second job limit <=7200. Resume an incomplete current stage using its saved shards; do not rerun a completed locked cohort in place. Next validates all local shard hashes and pre-next cohort hash. Saved next-shard outputs permit resuming an interrupted next stage. Missing activations after a complete run require an independent fresh inference directory as described below. Do not run G12. `.gitignore` excludes local activation tensors; public raw output/metadata hashes retain provenance.

The published package already contains locked data. `prepare.py` is the original preparation entry and refuses to overwrite it. For independent fresh inference use an isolated checkout, retain those worlds/configuration, and archive existing outputs, evaluation and `data/cohort_lock.json` outside the active result directory before running the two stages. Do not mix a new cohort hash with old next-state outputs. CPU audit of the public package records unavailable local activation shards explicitly; the original completed run verified all 120 local shard hashes. Historical full-fact key hashes permit checking new-world independence even if an earlier untracked world file is unavailable. Base models and small G10 rank16 checkpoints are referenced in place.
