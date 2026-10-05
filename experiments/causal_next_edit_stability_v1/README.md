# Causal next-edit stability v1

The experiment intervenes on a current edited memory **before** the original frozen editor. Decoder activation interventions are a separate readout mechanism analysis. All effects are donor-assisted, operation-specific, and restricted to the recorded finite task distribution. Negative results and missing stages remain explicit.

Base branch `experiment/four-domain-state-coverage-v1`, fetched SHA `0b73738cf552e1ec29aa7a5db1eb1ee703804b66`; working branch `experiment/causal-next-edit-stability-v1`, worktree `.causal-next-edit-worktree`. `ARTIFACT_AUDIT.md`, `run_manifest.json`, and `preregistered_protocol.yaml` define actual resources, source/checkpoint hashes, fixed world splits, method/seed budgets, eligibility and statistical endpoints. All 96 training worlds are excluded; the fixed pool contains 24 old dev, 32 exposed old test and 200 new worlds with disjoint core content. Primary independent intervention test uses new-world test only; old dev/test history and the template axis remain labelled.

All GPU execution uses the single entry below, a shared lock, one active 1-GPU array stage, `%2` maximum global concurrency, and `srun`. Smoke is also an array. No direct CUDA on login nodes; no overriding `CUDA_VISIBLE_DEVICES`. Failure and retry allocations count toward the 40 GPU-hour cap. New stage submission conservatively reserves the full walltime for every new shard and refuses active/unconfirmed experiment allocations. Other user GPU jobs trigger concurrency1 and are left intact. Runtime verifies its registered allocation and one visible GPU. Allocation records, not `.batch`/steps, determine cost and maximum concurrency.

From this worktree:

```bash
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m unittest experiments.causal_next_edit_stability_v1.tests.test_cpu experiments.causal_next_edit_stability_v1.tests.test_storage_cpu
bash experiments/causal_next_edit_stability_v1/slurm/submit_stage.sh --account
```

The unified worker command is:

```bash
python -m experiments.causal_next_edit_stability_v1.run_stage --config CONFIG --manifest MANIFEST --task-index INDEX --resume
```

It is called inside `worker.sbatch` via `srun`, never directly for GPU work. Config/manifest names in the directory are the actual runnable stage snapshots; code/config/data/checkpoint hashes are checked. Completed markers and per-world partial results are atomic. Resume only applies to unchanged missing or technically failed shards after the entire earlier stage terminates. A low result is not a retry trigger. For a new checkout, recreate configs with audited absolute resource paths rather than altering historical manifests or mixing outputs.

Historical stage manifests intentionally require their recorded code hash. To reproduce the locked BART test from the final implementation, create a fresh output namespace using the existing audited state caches and locked discovery bases (do not overwrite the historical test). The commands below create and submit the replay; repeated scientific evaluation is labelled replay and excluded from the original independent-test aggregate.

```bash
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -c "from experiments.causal_next_edit_stability_v1.audit import make_stage; from experiments.causal_next_edit_stability_v1.common import ROOT,read,sha; lock=read(ROOT/'results/final_test_lock.json'); make_stage('replay_bart',[('bart',s) for s in (42,43,44)],'03:00:00',dict(mode='test',input_hashes=dict(lock['input_hashes'],**{'results/final_test_lock.json':sha(ROOT/'results/final_test_lock.json')})))"
bash experiments/causal_next_edit_stability_v1/slurm/submit_stage.sh --config experiments/causal_next_edit_stability_v1/configs/replay_bart.json --manifest experiments/causal_next_edit_stability_v1/configs/replay_bart_tasks.json
```

Replay uses the same 40 GPU-hour ledger and two-GPU limit. Choose a new explicit namespace if replay results already exist. CPU aggregation is a `defq`, zero-GPU stage through the same worker; original stage inputs remain immutable.

Small source code, configs, denominators, aggregate CSV/JSON and sample records are committed. Full state tensors, complete per-example result streams and logs use the original project's shared `local/` artifact convention and are excluded from Git. Published indexes link paths and hashes. Backbone and editor training are never performed.

Official scheduling references: [Slurm arrays](https://slurm.schedmd.com/job_array.html), [sbatch](https://slurm.schedmd.com/sbatch.html). The distinction between intervention choice and scoring follows the concerns described in [Towards Best Practices of Activation Patching](https://arxiv.org/abs/2309.16042); no model conversion library is required.

The original test allocations used a one-hour limit; timeouts and a partially accepted Slurm limit increase are retained in the ledger. Technical recovery uses `--resume-walltime 03:00:00` on the original config/manifest after the entire prior array terminates. This changes only the allocation reservation, preserves scientific hashes, and skips complete world records. Three hours is the conservative replay allocation limit, not a runtime forecast.

The executed independent-test and CPU-analysis Python snapshot is `c288ad1` (code SHA256 `4924e61a677e4902cfd649a92853a18e5080584d6ed7d66eb253220c02b156a4`). After every allocation terminated, delivery changes added atomic PCA/module-basis/CSV/report publication, refusal to overwrite stage namespaces, and repeatable final resource refresh. These storage/report changes do not change intervention mathematics, selection, data, or the original results. Historical manifests retain their execution hashes; fresh replay manifests use the delivery code hash.

Final results are in `CAUSAL_NEXT_EDIT_STABILITY_V1_REPORT.md` and `results/table_{A,B,C,D,E}_*.csv/json`. `FINAL_STATUS.json` records terminal jobs, fixed scope and negative outcomes. `FINAL_HASH_VERIFICATION.json` confirms 8,684 artifact/backbone/editor/source files (15.61 GB); the immutable inputs of that CPU audit are preserved under `results/hash_audit_inputs/`. Historical `verify_cpu` manifests refer to the pre-final metadata snapshot. Replaying that historical CPU audit requires an isolated checkout of `3e5c3ef` with those two snapshot files restored at the declared original paths; use a fresh namespace and current hashes for a new audit. Never replace the original results in this worktree.

The same replay can be prepared and submitted with `bash experiments/causal_next_edit_stability_v1/slurm/replay_locked_bart.sh` from this worktree. Supply a fresh `replay_...` namespace as its first argument if the default already exists. The helper performs CPU-only manifest preparation and delegates submission to the sole resource-guarded entry. It was syntax-checked without submitting an extra evaluation.
