# Spatial current-state correction

During continuing CPU semantic auditing, after the BART spatial admission runs had finished, we identified a distinction between absolute facing and visible relative bearing. In the original core task, object world directions vary across worlds. Holding out facing east/west therefore does not hold out the relative right/left relation: training at facing north/south already contains all four relations.

The original protocol, data, checkpoints and predictions remain immutable. Its spatial matrix measures facing/world-anchor combination transfer, not a pure unseen relative-relation state. All three BART spatial seeds failed the original reconstruction gate (302/384). This is a capability limitation under the chosen interface, not composition evidence.

An attempted in-place correction was stopped by an assertion detecting existing spatial admission outputs before it changed any data, config or locks. The temporarily edited semantics module was restored to the original SHA. No scientific files in the original formal lock changed. The original code and lock are also archived in protocol_revisions/initial_formal_lock.

The separate space_relation_confirmation_v1 study uses relative states front/right/back/left. It preserves world positions and computes the corresponding physical facing. This correction follows the task's semantics; it does not alter thresholds, hyperparameters, model inputs, parser or checkpoint choice. Fresh editors and all three seeds will be run under a new pre-run lock after all existing arrays terminate. Original spatial results will remain separately labelled.
