# Selected BART editors seed43: own-latent validation trajectories

COMPLETED; Slurm 3045_1; allocation GPU-hours 0.164167. 64 validation core worlds, two locked operation orders and two directions, 256 trajectories per method. All prefixes must succeed for complete-trajectory success. Source starts are natural; subsequent memory is each method's own edited output, without resetting to gold states. Original/Plain full trajectories are SHA-verified earlier results, with identical cached H and unchanged checkpoints; they were not generated or charged twice.

| Method | 1 step | 2 steps | 3 steps | 5 steps |
| --- | --- | --- | --- | --- |
| Original | 256/256 | 0/256 | 0/256 | 0/256 |
| Plain | 256/256 | 0/256 | 0/256 | 0/256 |
| Output-only | 256/256 | 19/256 | 0/256 | 0/256 |
| Mechanism-guided | 256/256 | 124/256 | 0/256 | 0/256 |
| Random-site | 256/256 | 66/256 | 0/256 | 0/256 |

All 1,280 trajectories and every intermediate prediction are retained, including failures. NUMERICAL_AUDIT independently recomputes the full records; each seed's world-level all-four-trajectory proportion also has a Wilson interval. Inference latency is measured on a fixed eight-world subset, with identical source/operation conditions, one editor forward and native free decoding; warmups and measured repeats are explicit. No donor, target-text input, re-encoding, test-time gradient, rejection sampling or future gold activation is used by these editors.

These are validation results, not independent confirmation. The original 128-world test remains BLOCKED_TEST_INTEGRITY after five prior core exposures; no replacement pool or amended denominator is authorized. Atomic ability is evaluated in the preceding training run and cannot be inferred from these natural-start chains. Three seeds describe these fixed checkpoints. Mechanism-guided versus Output-only/Random-site requires paired world-cluster summaries, and any longer-chain improvement remains exploratory.
