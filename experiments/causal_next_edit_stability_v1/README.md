# Causal next-edit stability v1

The experiment intervenes on a current edited memory **before** the original frozen editor. Decoder activation interventions are a separate readout mechanism analysis. All effects are donor-assisted, operation-specific, and restricted to the recorded finite task distribution. Negative results and missing stages remain explicit.

Base branch `experiment/four-domain-state-coverage-v1`, fetched SHA `0b73738cf552e1ec29aa7a5db1eb1ee703804b66`; working branch `experiment/causal-next-edit-stability-v1`, worktree `.causal-next-edit-worktree`. `ARTIFACT_AUDIT.md`, `run_manifest.json`, and `preregistered_protocol.yaml` define actual resources, source/checkpoint hashes, fixed world splits, method/seed budgets, eligibility and statistical endpoints. All 96 training worlds are excluded; the fixed pool contains 24 old dev, 32 exposed old test and 200 new worlds with disjoint core content. Primary independent intervention test uses new-world test only; old dev/test history and the template axis remain labelled.

All GPU execution uses the single entry below, a shared lock, one active 1-GPU array stage, `%2` maximum global concurrency, and `srun`. Smoke is also an array. No direct CUDA on login nodes; no overriding `CUDA_VISIBLE_DEVICES`. Failure and retry allocations count toward the 40 GPU-hour cap. New stage submission conservatively reserves the full walltime for every new shard and refuses active/unconfirmed experiment allocations. Other user GPU jobs trigger concurrency1 and are left intact. Runtime verifies its registered allocation and one visible GPU. Allocation records, not `.batch`/steps, determine cost and maximum concurrency.

From this worktree:

```bash
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m unittest experiments.causal_next_edit_stability_v1.tests.test_cpu
bash experiments/causal_next_edit_stability_v1/slurm/submit_stage.sh --config experiments/causal_next_edit_stability_v1/configs/scan_bart.json --manifest experiments/causal_next_edit_stability_v1/configs/scan_bart_tasks.json --resume
bash experiments/causal_next_edit_stability_v1/slurm/submit_stage.sh --account
```

The unified worker command is:

```bash
python -m experiments.causal_next_edit_stability_v1.run_stage --config CONFIG --manifest MANIFEST --task-index INDEX --resume
```

It is called inside `worker.sbatch` via `srun`, never directly for GPU work. Config/manifest names in the directory are the actual runnable stage snapshots; code/config/data/checkpoint hashes are checked. Completed markers and per-world partial results are atomic. Resume only applies to unchanged missing or technically failed shards after the entire earlier stage terminates. A low result is not a retry trigger. For a new checkout, recreate configs with audited absolute resource paths rather than altering historical manifests or mixing outputs.

Small source code, configs, denominators, aggregate CSV/JSON and sample records are committed. Full state tensors, complete per-example result streams and logs use the original project's shared `local/` artifact convention and are excluded from Git. Published indexes link paths and hashes. Backbone and editor training are never performed.

Official scheduling references: [Slurm arrays](https://slurm.schedmd.com/job_array.html), [sbatch](https://slurm.schedmd.com/sbatch.html). The distinction between intervention choice and scoring follows the concerns described in [Towards Best Practices of Activation Patching](https://arxiv.org/abs/2309.16042); no model conversion library is required.
