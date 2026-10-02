# Evaluation timeout recovery

Formal child2568_12 (T5Gemma time seed42) reached its original two-hour walltime
after P/U and all six200-update N/S/M runs completed. Completed evaluation shards
and frozen source caches are retained. Controller requeue was attempted only after
checking the child's actual TIMEOUT and global project allocations; it returned
Invalid job id because the child record had been purged. That attempt allocated
no GPU and did not restart training. Its log/accounting snapshot is preserved.

Array2620, two one-GPU workers with %2, begins only after the entire original
formal2568 array terminates. Workers lock a shared claim ledger and resume only
missing original formal tasks whose recorded state is TIMEOUT/NODE_FAIL. They
do not rerun completed low-scoring runs. All downstream phases2571/2582/2585/2587
and CPU2590 have an additional2620 dependency. No unrelated job was changed.

The recovery allocation has six-hour walltime, within the previously verified
unlimited B300q partition. This is a resource amendment prompted by evaluation
runtime, not a scientific training/budget/selection change. Each worker uses srun
and one assigned GPU; the global cap is two and initial total budget is48GPUh.
The account script counts allocation attempts, not nested steps, and asserts the
observed historical peak is at most two. Every future technical retry must retain
all completed shards, immutable sources and hashes, and record its resources.
