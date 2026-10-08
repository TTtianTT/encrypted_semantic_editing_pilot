# Validation trajectory magnitude replay seed42

COMPLETED; Slurm 3048_0; 0.019722 GPU-hours. Replayed 64 validation worlds, five frozen methods, four locked trajectories and five steps: 6,400 records. All 100 stored predictions checked on the first world agree exactly; no algorithm/checkpoint changed and test accesses are 0. Padding is excluded from norms.

| Method | Step | Complete prefix | Mean update norm | Mean relative norm |
| --- | --- | --- | --- | --- |
| Original | 1 | 256/256 | 12.558892 | 0.453357 |
| Original | 2 | 0/256 | 14.212850 | 0.468896 |
| Original | 3 | 0/256 | 16.041082 | 0.431235 |
| Original | 4 | 0/256 | 18.591426 | 0.396911 |
| Original | 5 | 0/256 | 20.493268 | 0.342363 |
| Plain | 1 | 256/256 | 12.613124 | 0.455313 |
| Plain | 2 | 9/256 | 10.829907 | 0.357249 |
| Plain | 3 | 0/256 | 10.549496 | 0.304671 |
| Plain | 4 | 0/256 | 10.290643 | 0.264486 |
| Plain | 5 | 0/256 | 10.458118 | 0.237573 |
| Output-only | 1 | 256/256 | 11.105343 | 0.400887 |
| Output-only | 2 | 0/256 | 10.023447 | 0.336250 |
| Output-only | 3 | 0/256 | 9.927626 | 0.295870 |
| Output-only | 4 | 0/256 | 9.975285 | 0.266044 |
| Output-only | 5 | 0/256 | 10.082664 | 0.237370 |
| Mechanism-guided | 1 | 256/256 | 9.335524 | 0.337001 |
| Mechanism-guided | 2 | 0/256 | 8.291501 | 0.284005 |
| Mechanism-guided | 3 | 0/256 | 7.766833 | 0.243617 |
| Mechanism-guided | 4 | 0/256 | 7.355527 | 0.211645 |
| Mechanism-guided | 5 | 0/256 | 7.162632 | 0.187489 |
| Random-site | 1 | 256/256 | 9.633298 | 0.347749 |
| Random-site | 2 | 0/256 | 8.498098 | 0.290165 |
| Random-site | 3 | 0/256 | 8.069387 | 0.251772 |
| Random-site | 4 | 0/256 | 7.842404 | 0.224261 |
| Random-site | 5 | 0/256 | 7.810750 | 0.202079 |

This posthoc diagnostic measures magnitude differences in the already fixed paths. Norm strata are descriptive and do not establish norm-matched causal method effects. Every latent replay ran within the registered sbatch/srun allocation; no additional encoder execution.
