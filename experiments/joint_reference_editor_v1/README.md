# Joint reference editor v1

Baseline: `bc5087483b5c3d2476d615d8e9452b0f54bd289c`. Read `PROTOCOL.md`, `EVIDENCE_AUDIT.md`, and `REPORT.md`. Only this directory is added; old experiments remain unchanged.

The backbone weights and tokenizer are shared read-only at `/dataset1/zailong/models/reference-frame-cross-backbone/t5gemma-2b-2b-ul2-it/`. The existing `.venv` is reused; exact versions and file hashes are recorded. No downloads or environment upgrades are required in the original workspace. A separate reproduction environment must first provision the pinned model revision, not a newer checkpoint.

The copied `models/*_interface.json` preserves the frozen baseline's interface and historical editor metadata. Actual current-method parameter counts are in `editor_manifest.json` and training completion records.

CPU preparation (already locked; refuses overwrite):

```bash
.venv/bin/python experiments/joint_reference_editor_v1/prepare.py
```

GPU execution, one GPU per allocation, at most two concurrent and 7200 cumulative allocation seconds:

```bash
sbatch --partition=B300q --exclude=node01 experiments/joint_reference_editor_v1/run.slurm preflight
# After preflight and budget verification:
sbatch --partition=B300q --exclude=node01 --time=00:30:00 --export=ALL,RF_WALL_SECONDS=1740 experiments/joint_reference_editor_v1/run.slurm train 16
sbatch --partition=B300q --exclude=node01 --time=00:30:00 --export=ALL,RF_WALL_SECONDS=1740 experiments/joint_reference_editor_v1/run.slurm train 32
# Only after both best checkpoints are frozen:
sbatch --partition=B300q --exclude=node01 --time=00:30:00 --export=ALL,RF_WALL_SECONDS=1740 experiments/joint_reference_editor_v1/run.slurm evaluate
```

`run.slurm` invokes `srun`. The job timeout includes a saving reserve. `latest.pt` holds local optimizer/RNG state every100 updates and on an internal budget/signal stop; completed groups do not retrain. Generation resumes by record ID, and fold numerical checks have independent resume keys. No output is retried or selected based on semantic scores.

Capture the actual `sacct` columns `JobIDRaw,State,ElapsedRaw,AllocTRES,Submit,Start,End` with `-n -P` in `logs/sacct.txt`, then update the cumulative offline ledger:

```bash
.venv/bin/python experiments/joint_reference_editor_v1/account.py JOBID:PHASE:LABEL
```

All previous jobs must remain in the snapshot and ledger. Allocation seconds use parent/step maximum, not their sum. `commands.log` and the saved snapshot identify actual jobs. A reproduction is a new run requiring its own explicitly authorized budget; do not clear the delivered ledger or overwrite these results.

CPU analysis and delivery checks:

```bash
.venv/bin/python experiments/joint_reference_editor_v1/analyze.py
.venv/bin/python experiments/joint_reference_editor_v1/check.py
.venv/bin/python experiments/joint_reference_editor_v1/report.py
```

Main outputs: `outputs/{Joint16,Joint32,Sequential_T_then_P,Sequential_P_then_T,Folded_T_then_P,Folded_P_then_T}.jsonl`; controls/rules and numerical fold checks are separate. `evaluation/summary.csv`, `field_scores.csv`, `paired_statistics.json` retain fixed denominators and paired comparisons. `review/CASES.md` contains exactly20 preselected paired worlds, with anonymous CSV and private method mapping stored separately. Human labels are blank; model review is not human verification.

Publish only this experiment addition on the independent branch. Base model weights, environments, credentials, caches and local `latest.pt` optimizer/RNG files are excluded from Git. Initial editors, all100-step editor checkpoints, best checkpoints and complete predictions are included.
