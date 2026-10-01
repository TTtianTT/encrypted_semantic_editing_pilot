# G15 own-state continuation and held-out producer transfer

Base is exact G14 c82b5bfeea166edf0516f24e6e01abd3068b0912. Read PROTOCOL.md/configs/main.json/checkpoints_manifest.json and the result REPORT.md. Only G15 files change. Use the same existing `.venv` and read-only BART-base artifact; no package upgrades or old experiment rewrites.

First-run CPU preparation refuses to overwrite a lock:

```bash
.venv/bin/python experiments/g15_self_state_transfer_v1/prepare.py
.venv/bin/python experiments/g15_self_state_transfer_v1/cpu_check.py
```

Archived data can be checked with tests.py without re-preparing. Preparation reuses the actual G14 historical-source list and source SHA, supplements G13/G14 world manifests, and creates2880 new fact worlds (1536 train). All legal date/perspective renderings are checked; unavailable history is a stated limit, not a universal no-leakage claim. Coupled template/polarity support and legal40 natural cells are unchanged.

All GPU work requires sbatch allocation AND srun step. CPU tests must pass before submission; smoke uses only training/historical worlds and never loads U or infers G15 confirmation. After completed/pass smoke, submit exactly one array0–2%2 with explicit seed42/43/44 mapping, one GPU per allocation:

```bash
bash experiments/g15_self_state_transfer_v1/scripts/submit.sh smoke
# Wait until allocation completed and smoke_test.json passed.
bash experiments/g15_self_state_transfer_v1/scripts/submit.sh main
```

Measured smoke atomic/cache/update throughput sets walltime only, with component counts and20% reserve in resource_plan.json. Cumulative requests and actual usage capped at4 GPU-hours, whole experiment peak<=2. Duplicate phases/active G15 jobs block submission. No manual CUDA_VISIBLE_DEVICES setting. Each seed sequentially trains N/F/O from exact frozen P with new AdamW states; fixed final200, no selection. Only after all three trainings complete is U loaded and its today states generated for confirmation. Full state-cache paths/SHA and frozen/current-only gates are written into data/; large caches stay local/ and are not uploaded.

Every optimizer step uses four8-instance CE blocks weighted equally. O reuses differentiable first h1 for A and detach(h1) for D, updating only receiver gradients from D. F keeps fixed P states. No decode/reencode or gold reset in training; first free output is diagnostic only and cannot overwrite h1. training_budget.csv records actual tokens and erroneous-current trajectory-target counts. Resume files retain editor, optimizer, Python/CPU/CUDA RNG, completed step, shared schedule hash and actual logs. Engineering retries require explicit reason and remaining budget; poor results never trigger reruns.

CPU aggregation after jobs finish:

```bash
bash experiments/g15_self_state_transfer_v1/scripts/collect_results.sh
```

account.py uses allocation-level sacct, excludes batch/extern/srun, measures start/end peak. analyze.py recomputes every score, creates core/atomic/source/self/control counts, paired shared-world bootstrap, Wilson and seed SD, stages and complete free-text archives. On uploaded checkouts it can read per_example.jsonl.gz/learning_per_example.jsonl.gz without local output shards. Small final editor weights are under checkpoints/; optimizer/snapshot/base weights are excluded. Restore the requested plain record archive with `gzip -dc per_example.jsonl.gz > per_example.jsonl` in this directory.

The U endpoint is transfer to this repair-held-out exact F2 final200 producer, not unseen semantics, unrelated ancestry or open language OOD. G-today and G13 yesterday checks are restoration/maintenance. Own two-step task is supervised for O and is not new-length generalization. Successful reencoding is a diagnostic control, not a pure-latent result; identical controls do not create independent evidence.

Actual completed runs: smoke2505; main2507_0/1/2 (raw2508/2509/2507); evaluation-only engineering resume2510. All nine final200 trainings and all three seed confirmations completed. Seed43's original allocation hit internal time protection on its last evaluation shard;2510 reused exact saved checkpoints/caches and skipped all training and seven saved shards. `resume_evaluation.py` is a post-lock operational helper restricted to that diagnosed missing shard and budget; its singleton script has explicit seed-index1 and no second array. `resume_evaluation_audit.json` records before/after unchanged hashes. Do not rerun the submission helper on this completed experiment.

After CPU aggregation, restore the committed report annotations and validate delivery with:

```bash
.venv/bin/python experiments/g15_self_state_transfer_v1/annotate_report.py
.venv/bin/python experiments/g15_self_state_transfer_v1/finalize.py
```

`annotate_report.py` only adds factual interpretation/category scope and descriptive boundary cases, asserting main scientific CSVs and the complete free-output archive unchanged. `finalize.py` checks actual completed allocations, final checkpoint hashes, unchanged caches and protected retry artifacts, and writes artifact/cache inventories. It requires the original local caches for those final filesystem checks. Archived CSV/report inspection and CPU aggregation do not require latent caches or GPU. These post-lock helpers and `tests_aggregation.py` are explicitly distinguished from locked scientific inference/configuration; they never modify the model/data/schedule/scorer or training settings.

See [REPORT.md](REPORT.md), [INTERPRETATION.md](INTERPRETATION.md), [delivery_audit.json](delivery_audit.json) and [artifact_manifest.json](artifact_manifest.json). F/O repair their own two-step trajectories and transfer to U, but seed44 loses natural atomic capability; the full three-seed goal is unmet. Original automatic failure sampling tests H2 only; the reporting annotation names it `old_H2_maintenance_failure` rather than suggesting all maintenance sources have zero errors. Supplementary all-source/atomic failures are labeled post-result descriptions. The locked PROTOCOL remains intact; deviations and reporting corrections live in their separate audit files.
