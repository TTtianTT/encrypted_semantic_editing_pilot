# Emotion continuation: three-seed assistant review

Completed P core trajectory shards for seeds42/43/44 are available. The full N/S/M evaluations of43/44 are still running at review time. This is assistant inspection, not independent human annotation.

At step2, the fixed eligibility rule requires both an actually correct previous latent output and a correct gold-current-reencode next output. Each seed has96 eligible rows from32 test content worlds and3 paths. These are repeated trajectories, not96 independent worlds.

| Seed | Strict next successes | Strict next failures | Parsed slot mismatch | Unresolved |
|---|---:|---:|---:|---:|
|42|1|95|64|31|
|43|0|96|37|59|
|44|2|94|21|73|

All3 successful rows are saved in `emotion_three_seed_continuation_counterexamples.jsonl`; no success is removed to maintain a failure narrative. They were also inspected: seed42/reverse in emotion_0127 correctly changes Frank from positive to neutral while preserving David/parcel/black/9; seed44/inverse in emotion_0124 changes Carol from positive to neutral while preserving Alice/key/blue/2; seed44/inverse in emotion_0137 changes Grace from positive to neutral while preserving Bob/cup/red/2. These are semantically correct continuation counterexamples, not isolated sentiment-word matches. Slot mismatches and unresolved outputs are controlled-evaluator categories, not independent semantic adjudications of every row.

The nine inspected cases use the first lexicographic content world, emotion_0120, for every seed and all3 eligible paths. Current outputs all correctly express Alice's negative stance for the forward path, or positive stance for reverse/inverse, while retaining Henry's neutral stance, parcel identity, blue color and9 copies. The next gold target is neutral in each case; the gold-reencode outputs correctly express that target and retain the other content.

| Seed/path | Independently inspected next-output problem |
|---|---|
|42/forward|Leaves Alice negative and loses Henry/facts.|
|42/reverse|Makes Alice negative instead of neutral; other content remains.|
|42/inverse|Makes Alice negative instead of restoring neutral; other content remains.|
|43/forward|Produces positive and strongly positive claims for Alice, and omits Henry/facts.|
|43/reverse|Makes Alice negative instead of neutral; other content remains.|
|43/inverse|Makes Alice negative instead of restoring neutral; other content remains.|
|44/forward|Makes Alice positive instead of neutral; other content remains.|
|44/reverse|Makes Alice strongly positive and loses Henry/facts.|
|44/inverse|Correctly restores Alice to neutral but loses Henry's evaluation and the objective facts.|

These fixed cases confirm current-correct/next-failure existence in all3 seeds under this model/data/editor setting. In particular, seed44/inverse fails preservation while its target evaluation is correct; do not label it a wrong-target case merely because the frozen parser returns an incomplete-output failure. These cases do not establish a causal mechanism or universal inability to compose.
