# G17 reproducible frozen evaluation

Base92fe27beca7053d82074e16c2a0d7f4c87594d0e; G16 parameter manifests read-only, no weights copied. Use original .venv/model artifacts; no upgrades.

```bash
.venv/bin/python experiments/g17_state_source_transfer_v1/audit.py
.venv/bin/python experiments/g17_state_source_transfer_v1/prepare.py
.venv/bin/python experiments/g17_state_source_transfer_v1/tests.py
.venv/bin/python experiments/g17_state_source_transfer_v1/submit.py smoke
# Wait COMPLETED and smoke/frozen checks; resource estimate must fit2 GPUh including reserve.
.venv/bin/python experiments/g17_state_source_transfer_v1/submit.py main
# Wait3seed allocations; no overlapping GPU work.
bash experiments/g17_state_source_transfer_v1/scripts/collect_results.sh
```

prepare/audit refuse an existing lock. All GPU Python requires both Slurm job and srun step. Single one-GPU array0–2%2 maps to42/43/44; tasks run all4 anchors and2splits sequentially. Immutable caches and output shards SHA permit engineering-only missing-shard recovery, not score-driven re-evaluation. Main cohort locked before receiver for each complete anchor/split; fixed F/N/P inputs identical. Original320 worlds, per-source C, intersections and equal-natural-mask subsets are separately recorded.

per_example.jsonl.gz is complete aggregate, not successful examples only. outputs/ perseed/anchor shards retained locally (their checksums/completion metadata submitted); large local/ fullFP32 cache not uploaded, actual paths/hash in cache_manifests. Historical smoke uses first complete16-world G16 batch per split, no new-confirmation scores. Raw output reencoding only in reset control; pure latent handoff/self never reset. No training, optimizer or backward.

Scientific code/data/protocol locked before new model outputs; post-result interpretation/artifact publication helpers do not alter science. Supervision labels limited to actual accessible parameter lineage; all4 anchors reported regardless findings. Report primary IID+2/U F−N first, all otherCI descriptive. Complete cases SHA chosen before inference, posthoc failures separate. Wilson zero/one endpoints and shared-world paired bootstrap retained.

CPU交付验收（collect后，不重新推断）：

```bash
.venv/bin/python experiments/g17_state_source_transfer_v1/finalize.py
.venv/bin/python experiments/g17_state_source_transfer_v1/publish_report.py
.venv/bin/python experiments/g17_state_source_transfer_v1/check_delivery.py
```

若唯一缺失评估分片因已诊断的安全时间故障中断，本次实际使用resume_missing.py依赖主数组afterany，仅补seed43的最后OOD−2分片；恢复锁核验原7输出/8缓存SHA。它不是分数差重试。工程修改/历史锁版本保留，确认阶段科学锁不变。输出shards本地路径/hash与完整公开聚合archive一一对应。Slurm步骤显存原记录在slurm_step_usage.psv，只allocation计GPU小时。
