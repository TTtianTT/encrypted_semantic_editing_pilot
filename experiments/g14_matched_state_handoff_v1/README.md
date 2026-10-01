# G14 matched today-state handoff

This independent branch is based on exact G13 commit `c124e8c91a5b379725e17ef89937f4cf9da82301`. Read REPORT.md, PROTOCOL.md, baseline_audit.json and checkpoints_manifest.json. Old directories and checkpoint files remain read-only. Only G14 files are staged; the worktree environment/model links are not uploaded.

The experiment has zero training, no optimizer/backward, only G/T0 and F3/F2 final200 within seed42/43/44, and at most two semantic edits. All scientific data/config/code/dependencies are hashed before model inference in data/lock.json. `prepare.py` refuses an existing lock and verifies the exact starting baseline; it is the first-run entry, not a command to overwrite this archived experiment. It audits complete facts and normalized legal renderings across enumerated available historical manifests, extracts the first16 G13 worlds per split for reproduction, then creates independent160+160 confirmation worlds with named RNG leaves.

Use the same existing `.venv` and read-only `models/bart-base` artifact as G13. Local environment/base paths and versions are recorded in environment.json. First-run CPU preparation and state-flow tests:

```bash
.venv/bin/python experiments/g14_matched_state_handoff_v1/prepare.py
.venv/bin/python experiments/g14_matched_state_handoff_v1/tests.py
```

Archived data may be verified with `tests.py` directly. cpu_tests.json/cpu_tests.log preserve the actual test result; the submission barrier requires success. `run.py` rejects execution without both Slurm allocation and job step variables. It imports only the existing G13 editor definition, loads exact checked final weights, freezes every parameter and keeps models in eval mode. State-flow tests execute the real handoff routines on CPU spy engines.

GPU execution always uses sbatch allocation and srun, one GPU/job, one array at most:

```bash
bash experiments/g14_matched_state_handoff_v1/scripts/submit.sh smoke
# Wait for smoke COMPLETED and smoke_test.json passed.
bash experiments/g14_matched_state_handoff_v1/scripts/submit.sh main
```

No duplicate submission is allowed. Main walltime is computed only from measured smoke throughput; scientific scale remains fixed and all requested allocations must fit4 GPU-hours. Main indices0/1/2 map explicitly to42/43/44. It sequentially reproduces history, freezes both splits' current cohorts, then evaluates four latent cross cells, natural input and actual-free-output reencoding controls. Current cohorts never use next-step outputs, and natural mask mismatch never removes a matched G/R comparison.

CPU collection after allocations finish:

```bash
bash experiments/g14_matched_state_handoff_v1/scripts/collect_results.sh
```

`account.py` records allocation raw IDs and excludes batch/extern/srun steps, computes actual GPU-hours and start/end concurrency. `analyze.py` recomputes every score from output text and fixed world/reference frame, records each seed denominator, paired source patterns/differences, common F2/F3 cohorts,2000 shared-world bootstraps, Wilson intervals, seed mean/sample SD, raw first/two-step/gate-and-next measures, controls and parsed date/error counts. No inference or GPU is used for aggregation.

All confirmation outputs are preserved in per_example.jsonl.gz including wrong and unmatched worlds. On an uploaded checkout, aggregation falls back to this archive when ignored raw shards are absent. Restore the plain artifact with:

```bash
gzip -dc experiments/g14_matched_state_handoff_v1/per_example.jsonl.gz > experiments/g14_matched_state_handoff_v1/per_example.jsonl
```

Exact plain/archive hashes and local path are in per_example_manifest.json. Large full FP32 token memory/mask/source-ID caches remain under ignored local/; data/confirm_s*_states.json records real paths and SHA256 plus per-world state hashes, actual masks and IDs, current output and pre-receiver gates. No base weights, repeated old checkpoints or latent caches are uploaded. The fixed12 F3 cases are selected before inference by hash, two per seed/split, never by scientific outcome.

The32 historical worlds are reused across seeds solely for exact engineering reproduction and are excluded from confirmation statistics. Seed42 is checked in smoke and checked again in its formal allocation; this repeated verification is not additional independent evidence. Semantic T_plus advances observation day while preserving absolute event date; targets are rendered from facts/reference frames. TemplateOOD uses the original shared controlled vocabulary, not open natural-language generalization.

Slurm execution syntax was checked against official [job array](https://slurm.schedmd.com/job_array.html), [sbatch](https://slurm.schedmd.com/sbatch.html) and [srun](https://slurm.schedmd.com/srun.html) documentation; no external scientific assumptions were introduced.

INTERPRETATION.md records post-result interpretation without changing locked science. REPORT.md links it; analyze.py regenerates numerical report sections, while the interpretation remains separate. history_reproduction_s42_smoke.json preserves the smoke-phase historical verdict, and smoke_per_example.jsonl.gz archives its 640 historical cross/control rows separately from confirmation. delivery_manifest.json inventories committed G14 artifacts with SHA256; large local caches are listed by actual path/hash in state metadata.
