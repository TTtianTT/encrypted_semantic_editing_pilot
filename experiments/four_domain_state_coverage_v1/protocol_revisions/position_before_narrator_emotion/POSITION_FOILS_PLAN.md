# Secondary position and anchor diagnostics

Registered after the initial BART tests and before any GPU evaluation of these
new fixtures. This is a post-formal diagnostic extension, not part of the initial
preregistration. No new training, hyperparameters, seed selection or checkpoint
selection is allowed. All three seeds and every available P/N/S/M checkpoint are
evaluated. Failed core combinations retain reconstruction and P atomic results;
they do not receive newly trained supplement checkpoints.

Each original dev/test content world stays in its split. Two text orders express
the same world and transition. Emotion places either the target or the other
evaluator first; an additional object belonging to the target evaluator tests
object scope. Space places the fixed observer and absolute position either before
or after the external observer's relation. Person places the fixed historical
speaker/listener quotation either before or after the current speech context.
Time uses identical event-relative wording inside and outside a historical direct
quotation. Its quotation date is E minus three days and its fixed words are
"The OBJECT event is dated three days from now." Both text orders use the same
date and words; this repairs the earlier fixture's non-factive quotation/date
ambiguity. No other world fact changes, and the historical words never update.

The new time scorer checks the quotation words independently, then substitutes
the old canonical quotation only inside the scoring adapter before invoking the
frozen primary parser. Raw model output is preserved. Decode–reencode, if run,
uses raw output; no scorer normalization or gold repair is fed to the model.
Other domains use the frozen independent primary evaluator directly. Gold texts,
wrong-state negatives, changed-fact negatives and changed-quotation negatives
must pass CPU audits before GPU submission.

Reconstruction is measured once per backbone/domain on dev and test. All P seeds
receive dev atomic and gold-reencode next-step controls. Test atomic results are
reported for all available editor roles, even when diagnostic admission fails.
For each order, continuous trajectories run only when that seed's P reaches the
unchanged dev thresholds (reconstruction .95; atomic and gold-next .85; each
state/sign cell .75). Modes, legal horizons and cycles match the primary study.
Missing checkpoints are explicitly recorded rather than silently excluded.

Results include counts, per-seed/order semantic success, parseability, grammar,
scope, non-target preservation, paired same-world order effects and gated
trajectory results. They cannot establish a causal mechanism. Report the temporal
registration, finite grammar, synthetic identity conventions and scope limits.

Slurm: one global eight-task model/domain array with %2, one GPU per task, srun
inside each allocation, six-hour evaluation-only walltime in the verified B300q
partition. It depends on every active project GPU phase. The already pending CPU
finalization receives an additional dependency on this array. Duplicate submission
is guarded by the shared submission lock and ledger; completed prediction shards
are reused only with matching frozen specification/checkpoint hashes. The initial
48 GPU-hour project budget still applies. No CUDA_VISIBLE_DEVICES override.


Pre-GPU parser safety amendment: a separate space_scope_guard checks every
explicit target-A first-person or named-viewpoint relation against A’s gold
relation. A first B viewpoint cannot substitute for A. This only removes false
positive assessments and does not change inputs, weights, updates or selection.
CPU controls:1344 correct gold texts and56 adversarial named-viewpoint swaps;
the old parser incorrectly accepts all56 negatives. Original formal parser and
its raw outputs remain frozen. Existing actual predictions receive a separate
conservative audit, with no retroactive gate/checkpoint change. Old diagnostic
protocol/code are archived before any diagnostic GPU call.

The same pre-GPU independent guard also checks the object mentioned in every
fixed-B relation and in the marker relation. Correct relation words with the
wrong object are rejected. Final CPU controls:1344 positives and168 adversarial
A/B/marker binding negatives; the legacy parser accepts all168 wrong negatives.
The intermediate A-only guard and lock are separately archived; no diagnostic
model output existed in either amendment. Frozen primary scores remain unchanged.
