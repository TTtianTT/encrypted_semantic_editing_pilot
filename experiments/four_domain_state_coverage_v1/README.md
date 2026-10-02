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

On another machine, configure ORIGINAL/model directories and the verified Slurm partition; reuse pinned revisions and package versions. Fresh CPU data preparation is `prepare.py` followed by `revise_data.py`, then tests.py and audit.py. Reproduction must use a fresh experiment namespace rather than overwrite this locked delivery.
