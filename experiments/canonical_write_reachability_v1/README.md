# Canonical-write reachability and residual semantics

Read [REPORT.md](REPORT.md) for frozen-checkpoint experiments A and B. This run does not train experiment C or create a new confirmation cohort. The prior three-seed mechanism analysis remains unchanged in `../operator_residual_v2`.

Reduced-rank regression fits masked, position-shared affine ideal updates with rank 16, 64, 256, or 768. The exact penalized solution uses augmented-design SVD truncation, an unpenalized intercept, and train-only ridge selection. The 96 training worlds are split 80/16 for ridge selection and then all 96 are used for refitting. All 80 evaluation worlds are excluded from every fit. They remain historical analysis-held-out worlds, not new confirmation data. Template 3 is structural OOD only for the template-0-only fit condition.

Run from the repository root with `.venv`; GPU inference requires Slurm and `srun`. Existing frozen checkpoints and prior local analysis caches are needed. Paths and hashes are locked in `protocol.json`; local caches and raw inference shards are excluded from Git.

1. Run `checks.py` and `prepare.py` once before inference. Preserve sources and the protocol after locking.
2. Submit `WRITE_PHASE=extract` through `job.slurm`; run `fit.py` and `probes.py` on CPU after completion.
3. Submit `WRITE_PHASE=evaluate`, then `WRITE_PHASE=controls`, sequentially. Maximum one GPU at a time, total actual allocation cap 5400 GPU seconds.
4. Run `failures.py` and `analyze.py` on CPU. Capture all run job IDs in `run_ledger.json` and approved `sacct` output in `results/sacct_snapshot.json`.
5. Run `audit.py`, `report.py`, then `audit.py` again to include the final report hash.

This run also has two explicitly post-hoc extensions, each separately locked before its inference. `alignment_followup.py` tests five-step paths starting at +1 and -1 entirely inside the mask-aligned {-1,0,+1} component. Template numbers alone do not ensure alignment: transitions -2↔-1 and +1↔+2 change token lengths and were excluded from token-level fitting. Its initial design is preserved; the pre-inference shard-directory correction is recorded in the current `alignment_followup_protocol.json`.

`initial_projection_controls.py` tests the exact CE( E(0) )→state -1 context of the original projection failure, separately from historical 1→0 matched pairs. Its own design is in `initial_projection_controls_protocol.json`. After the main report is generated, run `followup_report.py` and `initial_controls_report.py`, then rerun `audit.py` to include their reports and integrity receipts. These additional GPU stages remain sequential and are included in the same allocation ledger. Supplemental raw shards also remain local.

Example: `sbatch --partition=B300q --export=ALL,WRITE_PHASE=extract experiments/canonical_write_reachability_v1/job.slurm`.

Output records retain actual texts, independent grammar scores, per-seed PCA4 residuals, and fit alignment flags. Non-aligned residuals are NA. Rank curves report complete trajectory success separately from one-step protection and conditional continuation. Reencoding uses the previous actual decoded text, not a gold oracle. Single-step reencoding shares the CE operator and should exactly match its CE baseline.

Norm controls use the edited state's actual ridge displacement as the per-world norm target for both full-space and random-4 directions, on both edited and canonical contexts. Probe conclusions require canonical-state calibration; a low-accuracy component probe cannot establish source/target conflict. Error classes have explicit precedence and additionally retain overlapping target/preservation/grammar labels. Repeated transitions and random directions use world-level clustered uncertainty.

Full trajectory and nonrandom control success intervals use Wilson intervals with 80 worlds per cell. Empirical bootstrap intervals for a cluster average can collapse at all-zero/all-one boundaries; they do not imply zero population uncertainty. Use the separately reported Wilson trajectory intervals for boundary success claims.

All neural parameters remain frozen. RRR/covariance/probe fitting is closed-form analysis. A failed L2 RRR experiment does not establish impossibility of every linear editor, and it does not authorize training C automatically. New worlds and five editor seeds for final confirmation require a separate locked design.
