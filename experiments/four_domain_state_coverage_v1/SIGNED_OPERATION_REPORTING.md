# Operation-specific contrasts

Added after the completed T5Gemma emotion seed42 behavior, on2026-10-02 UTC. Plus/minus were frozen task signals and existing `summary_by_seed.csv` already separated them. This addition makes the direction-specific matched S/M contrasts directly visible; it is a post-result reporting change, not a new preregistered experiment or a selection rule.

`M_vs_S_by_operation.csv` partitions every existing contrast's complete candidate set by operation, for all backbones/domains/seeds/splits/templates/sources/cohorts. It retains directions with zero success and both positive and negative effects. No changes to gold, grading, candidate membership, checkpoints, updates or inputs. CPU verification reproduced the aggregate n/S_k/M_k from the signed partitions for all231 available comparisons at addition time; the generator asserts that the partitions cover every candidate.

The triggering seed42 emotion U/fixed-core observation is directional: H0 S/M minus0/32 versus18/32, H1 minus18/32 versus32/32, whereas plus is0/32 for both conditions and both splits. Neither the single-seed aggregate gain nor one correctly edited illustration establishes bidirectional or three-seed generalization. Future results append all remaining comparisons under the same grouping rule.
