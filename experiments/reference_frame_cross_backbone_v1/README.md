# Cross-backbone reference-frame pilot v1

Read `PROTOCOL.md`, `PROTOCOL_AMENDMENT_01.md`, `EVIDENCE_AUDIT.md`, and `REPORT.md`.

CPU preparation/download (already completed in delivered artifacts):

```bash
.venv/bin/python experiments/reference_frame_cross_backbone_v1/assets.py
.venv/bin/python experiments/reference_frame_cross_backbone_v1/prepare.py
```

Weights are stored at `/dataset1/zailong/models/reference-frame-cross-backbone/`, not in Git. The existing `.venv` is reused without changes. Prepared data refuse overwrite. Four model IDs and revisions are fixed in manifests. `assets.py` on a fresh checkout downloads these pinned revisions when local files are absent; `RF_MODEL_ROOT` can relocate the model directory in a separate reproduction workspace. It does not silently resolve a newer model revision.

GPU entrypoints always run through Slurm:

```bash
sbatch --partition=B300q experiments/reference_frame_cross_backbone_v1/run.slurm preflight flan-t5-base
# After admission, measure the paired training/evaluation cost without optimizer updates:
sbatch --partition=B300q experiments/reference_frame_cross_backbone_v1/run.slurm plan_training MODEL
# Only after that model passes admission AND remaining allocation budget reserves 1.5x evaluation estimate:
sbatch --partition=B300q experiments/reference_frame_cross_backbone_v1/run.slurm train MODEL G1
sbatch --partition=B300q experiments/reference_frame_cross_backbone_v1/run.slurm train MODEL G3
sbatch --partition=B300q experiments/reference_frame_cross_backbone_v1/run.slurm evaluate MODEL
# Archived reference; never retrain BART:
sbatch --partition=B300q experiments/reference_frame_cross_backbone_v1/run.slurm evaluate BART
```

Use the fixed candidate order in the protocol. Failed admission forbids full training. `run.slurm` invokes `srun`; each job requests one GPU, at most two concurrently after the user's amendment. Every allocation, failed attempt and retry counts toward 14400 GPU seconds; preflight is capped at 3600. Default job cap is 900 seconds, with an internal reserve. Check and update `budget.json` via `account.py JOB:PHASE:MODEL ...`; never reset historical accounting. Queuing is separate, parent/step are not double counted.

CPU analysis:

```bash
.venv/bin/python experiments/reference_frame_cross_backbone_v1/audit.py
.venv/bin/python experiments/reference_frame_cross_backbone_v1/length_audit.py
.venv/bin/python experiments/reference_frame_cross_backbone_v1/provenance.py
.venv/bin/python experiments/reference_frame_cross_backbone_v1/analyze.py
.venv/bin/python experiments/reference_frame_cross_backbone_v1/final_check.py
.venv/bin/python experiments/reference_frame_cross_backbone_v1/report.py
```

Neural outputs and reconstruction caches resume by exact input/row identity. `latest.pt` stores training optimizer/RNG locally, each 100-step editor is saved, and best is selected only by complete atomic dev token NLL. To rerun a finished experiment from scratch, use a new versioned directory; do not erase this delivery's locks/results. Preflight output filenames include wrapper and scoring roles. An unsupported/incomplete attempt is retained before any implementation repair or retry.

All human labels are blank. The anonymous review mapping is separate and should not be given to actual reviewers. Convenience cases are not unbiased estimates. The published branch contains only this experiment addition; old v1/v2/v3 data, results and checkpoints are unchanged.

`commands.log` contains the actual longer Slurm time limits and `RF_WALL_SECONDS` used for the admitted model; the 15-minute default alone is not a promise that every entrypoint finishes. Check the accumulated ledger before allocating any replay, and use a separate explicitly authorized budget for new reproduction work. `provenance.py` only enriches completed rows with seed/checkpoint/interface metadata and records before/after hashes plus an unchanged prediction/score/timing payload hash.
