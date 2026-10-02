# Four-domain controlled state-coverage experiment

Read EXPERIMENT_PLAN.md, DATA_SPEC.md, AMENDMENTS.md and the immutable formal_lock.json. New branch starts from audited G17; no old parameter checkpoint initializes this experiment. Existing `.venv`, BART and admitted T5Gemma2B-2B UL2-IT artifacts are read-only reused. No admitted270M IT model was found; the old pretrained270M failure is retained in AUDIT/model_manifest.

From original repository working directory:

```bash
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/account.py
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/analyze.py
```

GPU submission/recovery always uses the single locked scheduler. Existing submitted phases are returned, never duplicated. Resume is permitted only after all previous phase allocations terminate, and submits only tasks lacking immutable complete markers:

```bash
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/submit.py formal --resume
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/submit.py symbol --resume
```

One global array%2 per phase, one GPU/task, dependencies on every existing project allocation (including retries/interactive). Runtime GPU paths require allocation plus srun. No CUDA_VISIBLE_DEVICES override. Check budget.json before recovery. Do not edit config/code/data after the formal lock. Engineering faults may be repaired with an explicit engineering-deviation record; no score-based retries. A completed low-scoring run is not a recoverable missing task.

The Slurm task runs P600, its full dev gate, independentU600 and fixedQstep300 source generation, N/S/M200×two holdout splits, full behavior and descriptive probe, in sequence. Non-admitted runs keep dev/test atomic diagnostics and have no supplement. Symbol diagnostics use independently fitted600-step rank16 editors, seed42, their own gate, and no N/S/M. All train data are grouped by world; only core templates0/1 are used for natural fitting. Third-person pronoun challenge6 and quantity/negation repairs are pre-formal amendments.

Checkpoint/RNG/latest and full tensor source caches remain in `local/`, with published checkpoint/hash/index and cache manifests. Prediction shards are atomically written; a timeout cannot turn a partial shard into a complete output. Exact selected/final parameter exports and raw local checkpoint path hashes are separately indexed at publication. Do not replace immutable P/Q/U sources with updated receivers. Test shards are not used for dev selection or budgets.

Initial engineering2555, interface2564, formal2568; authoritative phase IDs including recovery and symbol are in submissions.json and Slurm ledger. RESULTS.md is generated from completed prediction artifacts, never from the training loss alone. Running/technical failure/not-admitted/not-executed remain explicit.

Spatial facing labels in the initial protocol did not hold out visible relation states. The independent `space_relation_confirmation_v1` protocol preserves all worlds/text pair sets, but indexes front/right/back/left and uses fresh atomic editors. Original outputs remain intact; see POSTFORMAL_SEMANTIC_AUDIT.md and the confirmation plan. Confirmation2582 depends on formal2568 and symbol2571; identity probes2585 depend on all previous phases; structural generation/gated-continuation controls2587 follow them. Final CPU evidence build2590 requests no GPU and waits for all phases.

Additional recovery commands, after earlier phase allocations terminate:

```bash
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/submit_confirmation.py --resume
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/submit_addon.py linguistic_controls --resume
.venv/bin/python .four-domain-worktree/experiments/four_domain_state_coverage_v1/submit_addon.py finalize --resume
```

If an individual child actually times out while its parent array still has pending/running siblings, `recover_timeout.py JOBID_TASK` may requeue it within the same array%2. The guard refuses concurrent other project GPU phases, non-TIMEOUT states or duplicate recovery. Archive logs before requeue; accounting uses duplicate Slurm records so repeated allocation attempts count. Do not use requeue after the parent has terminated; use a new dependent missing-task submission instead. All completed shards and fixed source tensors are retained. No score-based rerun is permitted.

The authoritative postprocessors in this directory accept `analyze.py --study space_relation_confirmation_v1` and `publish.py --study space_relation_confirmation_v1`; early copied utilities in the confirmation scientific lock remain archived but do not supersede these corrected CPU postprocessors. Exports include phase in their namespace so independently trained symbol P cannot overwrite natural P. publication_audit checks exact tensor equality and JSONL roundtrip hashes. Raw full tensor caches/optimizer checkpoints and stdout/stderr stay on shared cluster storage; published parameter files, prediction gzip archives, source/log indexes and hashes are in Git. The final CPU build does not commit or push automatically.

The secondary structure gate was added after some original test observations and is explicitly labelled a post-core protocol extension. It cannot change editor training/checkpoint selection. The finite parser's unresolved outputs are separated from parsed semantic mismatch, grammar-only and termination-only failures. A fixed18-case assistant review verifies clear continuation corruption for BART time/person, without claiming independent human labels or relabelling all unresolved predictions.

On another machine, configure ORIGINAL/model directories and the verified Slurm partition; reuse pinned revisions and package versions. Fresh CPU data preparation is `prepare.py` followed by `revise_data.py`, then tests.py and audit.py. Reproduction must use a fresh experiment namespace rather than overwrite this locked delivery.

The original 2568_12 timed out after all its training finished, during evaluation.
Its controller record had already been purged when requeue was attempted; no
successful requeue or extra allocation occurred. Recovery array2620 has two
one-GPU workers, waits for the entire2568 parent, and claims only missing original
TIMEOUT/NODE_FAIL tasks. It retains every completed shard/checkpoint/source and
uses a six-hour evaluation recovery allocation in B300q. All downstream GPU
phases and CPU2590 gained this dependency. See retry_wave_intent and
POSTFORMAL_RESOURCE_RECOVERY.md; the 48GPUh project cap remains unchanged.

Position diagnostics2621 follow all other GPU phases, and CPU2590 now waits for
2621 too. They use frozen P/N/S/M, same-world clause-order pairs, and identical
event-relative phrases inside/outside the time quotation. This is a documented
post-formal diagnostic extension, not a training amendment. Its plan, fixtures,
CPU positive/negative checks and code are frozen in position_lock.json. Completed
outputs are archived by extra_archives.py; raw scoring adapter transformations
never enter decode–reencode inputs. Use submission ledger/status files to inspect
active recovery rather than submit an independent quick GPU test.

`progress.py` creates a CPU-only task/checkpoint/shard snapshot in PROGRESS.md/json.
Run account.py first for fresh GPU-hours. Components and exposure definitions are
in semantic_component_audit.json and TRANSFER_DEFINITIONS.json: primary scope is a
joint target/preservation outcome; individual anchor/binding constraints are
reported separately with unknown coverage. Seen source and seen state factors do
not imply their joint was trained. N has no edited-source exposure. Every legal
natural conversion is trained; there is no fully-untrained natural conversion
condition in this study.

SOURCE_LINEAGE_RESOLVED.json audits actual steps, dev selection and exact P
initialization. Q is the same atomic optimization run's step300 snapshot; the
legacy raw Q.parent field identifies its associated selected P and is not a
claim that Q was initialized from that later selected checkpoint. U is independent
seed+10000; every N/S/M200 shares exact selected P. Raw metadata is retained.

REMAINING_ATOMIC_PREFLIGHT.md discloses the initial per-combination interleaving
of admission/supplement/behavior. To correct the remaining order, original
children16–23 are held while atomic-preflight2650 computes their originally
budgeted P600 and full dev gates, with no test/U/supplement work. CPU2651 releases
those eight children after the preflight array ends; they reuse P/dev artifacts.
The inserted GPU array waits for current children14/15, uses %2 and one GPU/task,
and does not overlap downstream phases waiting on the original formal parent.
It adds model-loading overhead but no P training updates. If CPU2651 fails, inspect
its log and the held-child record, then rerun the zero-GPU release script under
Slurm; do not release children while any preflight GPU task is still active.
