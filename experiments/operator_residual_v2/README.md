# Frozen residual attribution and projection experiments

This experiment extends the preserved `operator_residual_v1` analysis. It performs PCA component repair and reverse injection, pre/post decoder visibility measurements, native decoder K/V activation replacement, train-world PCA generalization, no-reference Mahalanobis prediction, and five-step projection evaluation. Encoder, decoder, and editor checkpoints stay frozen. PCA, covariance estimation, and ridge regression are closed-form analysis fits on training worlds.

Read [REPORT.md](REPORT.md) for the conclusions, [protocol.json](protocol.json) for the initial fixed design, and [execution_source_manifest.json](execution_source_manifest.json) for the subsequent source snapshot and supplementary controls. The latter explicitly records which stages were already running when the snapshot was taken; it is not retrospective preregistration.

## Run order

Run from the repository root using the existing `.venv`. GPU inference must use Slurm; the supplied launcher allocates one GPU and invokes `srun`. The initial protocol and all input hashes must match before resuming any stage.

1. `prepare.py` writes the protocol once; preserve it thereafter.
2. Submit `extract.py` using `RESIDUAL_PHASE=extract`, then run `fit.py` on CPU.
3. Submit phases `interventions`, `projection`, and `decoder`, sequentially.
4. Submit supplementary phases `g4_same_editor`, `canonical_control`, `cross_conditioned`, and `decoder_cumulative`, sequentially. The cumulative phase is a post-hoc response to the absence of single-layer rescue. [execution_amendments.json](execution_amendments.json) records the padding assertion fix and retry.
5. Run `checks.py`, `aggregate.py`, `estimator_diagnostics.py`, and `supplement.py` on CPU. The estimator diagnostic uses existing cached states and performs no GPU inference.
6. Run `plots.py`, `audit.py`, and `report.py`; run `audit.py` once more to include the finished report in the artifact manifest.

Example inference submission:

```bash
sbatch --partition=B300q --export=ALL,RESIDUAL_PHASE=interventions experiments/operator_residual_v2/job.slurm
```

The initial, projection, and decoder stages can resume complete per-batch shards. Preserve the sources while resuming. `audit.py` uses this run's job IDs, including the failed padding-check attempt, for its allocation ledger; a rerun requires an explicit new ledger rather than silently excluding attempts.

## Outputs and interpretation

The report links the per-seed CSV tables and standalone SVG/PNG figures. Raw JSONL records retain generated texts, semantic scores, KL values, margins, and individual world IDs. Projection records also retain pooled vectors before and after each intervention. Large projection records, inference shards, logs, and `.pt` caches remain local and are excluded from Git. The final artifact manifest hashes retained outputs.

Success-rate intervals are per-seed Wilson intervals. Random-direction controls first average four directions within each world, then bootstrap worlds. AUROC and paired differences use world bootstrap so repeated trajectory depths are not treated as independent worlds. Single-class prediction cohorts have AUROC `NA`.

The 80 evaluation worlds exclude all PCA and normalizer fitting worlds, but are historical analysis-held-out worlds already observed in prior experiments. Template-2 donor patches with unequal token masks are `NA`; template-2 no-reference chains are still fully evaluated. The G4 matched-editor prediction control uses the same frozen G3 checkpoint as historical G4, rather than implying that the main P editor is the same model.

No model training, checkpoint updates, external publication, or repository commit is part of this run.
