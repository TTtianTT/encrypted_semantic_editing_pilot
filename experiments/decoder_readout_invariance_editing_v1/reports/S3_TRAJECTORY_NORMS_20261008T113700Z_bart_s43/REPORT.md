# Validation trajectory magnitude replay seed43

COMPLETED; Slurm 3048_1; 0.016944 GPU-hours. Replayed 64 validation worlds, five frozen methods, four locked trajectories and five steps: 6,400 records. All 100 stored predictions checked on the first world agree exactly; no algorithm/checkpoint changed and test accesses are 0. Padding is excluded from norms.

| Method | Step | Complete prefix | Mean update norm | Mean relative norm |
| --- | --- | --- | --- | --- |
| Original | 1 | 256/256 | 13.119703 | 0.473606 |
| Original | 2 | 0/256 | 14.038551 | 0.460220 |
| Original | 3 | 0/256 | 15.705070 | 0.418051 |
| Original | 4 | 0/256 | 17.714711 | 0.374383 |
| Original | 5 | 0/256 | 20.285243 | 0.338573 |
| Plain | 1 | 256/256 | 14.510188 | 0.523799 |
| Plain | 2 | 0/256 | 13.260437 | 0.425829 |
| Plain | 3 | 0/256 | 13.116260 | 0.353661 |
| Plain | 4 | 0/256 | 12.903694 | 0.298077 |
| Plain | 5 | 0/256 | 13.388769 | 0.262353 |
| Output-only | 1 | 256/256 | 12.378978 | 0.446865 |
| Output-only | 2 | 19/256 | 11.568054 | 0.380347 |
| Output-only | 3 | 0/256 | 11.573103 | 0.329204 |
| Output-only | 4 | 0/256 | 11.803646 | 0.292899 |
| Output-only | 5 | 0/256 | 12.372625 | 0.260666 |
| Mechanism-guided | 1 | 256/256 | 9.848670 | 0.355524 |
| Mechanism-guided | 2 | 124/256 | 8.996827 | 0.305553 |
| Mechanism-guided | 3 | 0/256 | 8.588404 | 0.264725 |
| Mechanism-guided | 4 | 0/256 | 8.556280 | 0.241448 |
| Mechanism-guided | 5 | 0/256 | 8.615569 | 0.216361 |
| Random-site | 1 | 256/256 | 9.906268 | 0.357602 |
| Random-site | 2 | 66/256 | 8.428707 | 0.286141 |
| Random-site | 3 | 0/256 | 7.737353 | 0.239812 |
| Random-site | 4 | 0/256 | 7.941270 | 0.228015 |
| Random-site | 5 | 0/256 | 8.244175 | 0.215797 |

This posthoc diagnostic measures magnitude differences in the already fixed paths. Norm strata are descriptive and do not establish norm-matched causal method effects. Every latent replay ran within the registered sbatch/srun allocation; no additional encoder execution.
