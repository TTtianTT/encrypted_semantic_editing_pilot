# Validation trajectory magnitude replay seed44

COMPLETED; Slurm 3048_2; 0.016944 GPU-hours. Replayed 64 validation worlds, five frozen methods, four locked trajectories and five steps: 6,400 records. All 100 stored predictions checked on the first world agree exactly; no algorithm/checkpoint changed and test accesses are 0. Padding is excluded from norms.

| Method | Step | Complete prefix | Mean update norm | Mean relative norm |
| --- | --- | --- | --- | --- |
| Original | 1 | 256/256 | 12.839238 | 0.463479 |
| Original | 2 | 0/256 | 14.432046 | 0.474044 |
| Original | 3 | 0/256 | 16.869059 | 0.448381 |
| Original | 4 | 0/256 | 19.378825 | 0.404735 |
| Original | 5 | 0/256 | 22.397328 | 0.361324 |
| Plain | 1 | 256/256 | 12.968014 | 0.468129 |
| Plain | 2 | 7/256 | 12.017959 | 0.395296 |
| Plain | 3 | 0/256 | 11.492411 | 0.325949 |
| Plain | 4 | 0/256 | 11.293610 | 0.277279 |
| Plain | 5 | 0/256 | 12.026924 | 0.252243 |
| Output-only | 1 | 256/256 | 11.592020 | 0.418458 |
| Output-only | 2 | 55/256 | 10.624671 | 0.354125 |
| Output-only | 3 | 0/256 | 10.049619 | 0.296205 |
| Output-only | 4 | 0/256 | 9.721304 | 0.253531 |
| Output-only | 5 | 0/256 | 10.141720 | 0.228765 |
| Mechanism-guided | 1 | 256/256 | 9.803021 | 0.353877 |
| Mechanism-guided | 2 | 7/256 | 9.156561 | 0.312041 |
| Mechanism-guided | 3 | 0/256 | 8.730738 | 0.268428 |
| Mechanism-guided | 4 | 0/256 | 8.705560 | 0.241308 |
| Mechanism-guided | 5 | 0/256 | 9.433842 | 0.231492 |
| Random-site | 1 | 256/256 | 9.527908 | 0.343945 |
| Random-site | 2 | 54/256 | 8.651707 | 0.295475 |
| Random-site | 3 | 0/256 | 8.004031 | 0.247776 |
| Random-site | 4 | 0/256 | 7.851394 | 0.220784 |
| Random-site | 5 | 0/256 | 8.511460 | 0.215940 |

This posthoc diagnostic measures magnitude differences in the already fixed paths. Norm strata are descriptive and do not establish norm-matched causal method effects. Every latent replay ran within the registered sbatch/srun allocation; no additional encoder execution.
