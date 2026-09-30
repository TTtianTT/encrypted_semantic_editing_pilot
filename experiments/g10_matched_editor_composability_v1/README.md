# G10 Matched Editor Composability

Read `PROTOCOL.md` before reproducing. `prepare.py` locks four disjoint world sets before training or inference. Nine fresh BART low-rank T+ editors are trained under the original G3 200-update schedule, then a fresh IID/OOD single-step matching set fixes the retained cohort before composition-test outputs are generated.

```bash
.venv/bin/python experiments/g10_matched_editor_composability_v1/prepare.py
sbatch --partition=B300q experiments/g10_matched_editor_composability_v1/preflight.slurm
sbatch --partition=B300q experiments/g10_matched_editor_composability_v1/train_array.slurm
# Wait for all 3 array tasks (each task trains one rank across seeds 42/43/44).
sbatch --partition=B300q experiments/g10_matched_editor_composability_v1/screen.slurm
# Review evaluation/gate_lock.json; it is frozen by screen.py before composition inference.
sbatch --partition=B300q experiments/g10_matched_editor_composability_v1/evaluate.slurm
sbatch --partition=B300q experiments/g10_matched_editor_composability_v1/basin_array.slurm
# After all retained-editor basin array tasks complete:
.venv/bin/python experiments/g10_matched_editor_composability_v1/analyze.py
.venv/bin/python experiments/g10_matched_editor_composability_v1/audit.py
.venv/bin/python experiments/g10_matched_editor_composability_v1/report.py
```

Every GPU job requests one device and invokes the workload with `srun`; train/basin arrays cap concurrency at two. BART remains read-only. The checkpoints contain only low-rank editors. `evaluation/per_step_raw.csv`, `basin/scan_*.jsonl`, and `outputs/trajectory_*.jsonl` retain complete generated text and labels, including failures.
