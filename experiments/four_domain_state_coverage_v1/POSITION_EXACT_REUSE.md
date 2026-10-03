# Exact duplicate inference reuse

Engineering cache registration before the position GPU phase. Scientific inputs,
budgets, checkpoints, selection and scoring rules are unchanged. The emotion
position variant0 is exactly the existing multi-object structure4: every source
and target string, all current-state renderings, content worlds, signed operation
sequences, editor weights, frozen backbone/interface and decode configuration are
the same. Integer fixture IDs and gold-only foil metadata do not enter inference.

The CPU reuse script checks all256 atomic source/target pairs and all content
world/state renderings. It reuses every available original structure4 trajectory
shard across all three seeds and all seven roles, without filtering by outcomes.
The source predictions were generated through Slurm array task2587_6. Raw output,
mask length and technical errors are preserved. New gold-only fixture metadata,
the frozen position scores, previous-step correctness and full-trajectory flags
are recomputed from actual text on CPU. File and checkpoint SHA256 links are kept
in POSITION_EXACT_REUSE_AUDIT.json. The position worker already supports existing
complete shards; no frozen worker, model input, update or threshold is modified.

No new cache shard may be inserted once this model/domain's position reconstruction
has started. Other orders, narrator/quotation contrasts, dev gates and test atomic
predictions are executed as scheduled. This is exact-input compute reuse, not an
extra training condition or a new result selected after examining continuation.
