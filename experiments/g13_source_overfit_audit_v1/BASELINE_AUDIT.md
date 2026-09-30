# Baseline audit (before GPU execution)

G12 HEAD / original code commit: `389bb85160df6311cc866fc573f73a24b3d87a09`; G11 `0d9da457d8e8362064200ea1d53ecde5793134b9`; G10 training code introduced in `b07abb4`. Remote G11/G12 SHAs verified. No applicable AGENTS.md found. Original worktree untracked unrelated artifacts preserved. No existing Slurm jobs at start.

T0 is G10 rank16 b+UV, 25,344 parameters per independent T_plus. G10 trained 200 updates, same G3 schedule: 3200 source samples, 1600 replacements explicitly supervise both first/second calls. Actual source manifest and schedule audited, not inferred from later report. Natural support offset[-3,3], both perspectives/all legal statuses; two-call replacements have source offset[-2,2]. G12 A/B start this T0, 200 AdamW updates LR .001, equal three stage losses; B third source is own stopgrad(h2), A canonical natural yesterday. Three is supervised in G12; Original supervised length is one or selected two, not three.

BART-base facebook revision `aadd2ab0ae0c8268c7c9693540e9904811f36177`, frozen unadapted E/D; FP32, sdpa, TF32 false, 96-position max padding; greedy beam1, max_new_tokens60, forced EOS null, clean_up_tokenization_spaces false. Existing independent parser/renderer unchanged. Model SHA256 `1bd3ac8e5b3ac71c77cf18fbcd8b113e0bfceced94c5cfbbb9a2b4bb4781190b`.

| seed | checkpoint | SHA256 |
|---|---|---|
|42|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g10_matched_editor_composability_v1/checkpoints/rank16/rank16_seed42.pt|00706fc2c904455bc8c5f6e490d24a4b1772e2bb1ece433ff8e1ecf455b9f160|
|42|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g12_matched_input_source_v1/checkpoints/A_seed42.pt|4a12bf2114d12f3bff0e9d79edf2b88b2af2ae4ec617fa895d2d71e19292573f|
|42|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g12_matched_input_source_v1/checkpoints/B_seed42.pt|a3be9e4a42a22f674c5383d5953c4a899f81c95518ac7b2a515b510ac53b3ef1|
|43|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g10_matched_editor_composability_v1/checkpoints/rank16/rank16_seed43.pt|6b02ce643055786bdb46ddf395d952593ae44116f07c8521735e24997e8eb215|
|43|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g12_matched_input_source_v1/checkpoints/A_seed43.pt|abe4d52df0528fdd6e1a7250efb3b4c1f69bc725232b1afcae6220c486e58d8e|
|43|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g12_matched_input_source_v1/checkpoints/B_seed43.pt|cc08d207e79d66041da7c6e5874a7b6b563ad75eb7aa25a279a4c5e687434764|
|44|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g10_matched_editor_composability_v1/checkpoints/rank16/rank16_seed44.pt|cc6ac6aae2a7f233cb201e3e38d366c540ce829c28e736e62e67a742ea50b4a4|
|44|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g12_matched_input_source_v1/checkpoints/A_seed44.pt|87c932e8377a39aaed55deb5c379644c7293e4f3a6df62c76b99aef6204add3b|
|44|/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g13-worktree/experiments/g12_matched_input_source_v1/checkpoints/B_seed44.pt|17956ad36c41c7c1d97b3d77379331ff943c7f42830285da379a641f81d1a88a|

Checkpoints are tracked small editor-only state dicts; base model is read-only symlink to original shared artifact, exact model files/hashes in baseline_audit.json. No substitute model. Other original independent operators live in V3 checkpoints/G3/best.pt and are never optimized.

Data provenance/overlap audits, actual train/template ranges and file hashes: baseline_audit.json and data/manifest.json (produced by prepare.py before GPU work). Enumerated accessible old data/world manifests only; unavailable history is unaudited. Main anchor/rollout universe recorded plans; supplemental cancelled/completed worlds protect complete original natural input scope. No illegal future completed states. Extra legal offset+4 is outside T0 source support and will be separately visible.

Historical archived outputs will be independently rescored and a six-world/three-step GPU reproduction run for all accessible models/seeds; results in baseline/. Eighty real supervised training worlds per task/seed compare against independent IID worlds of same template/status/polarity/source offset/perspective/supervised length. G12 A third natural source is reported separately from free own-state trajectories. Old loss logs exist only as batch aggregate, without same-world validation curves; no claim about historical dev worsening.

Slurm B300q available, nodes01–03,8 B300/node, no partition time limit, account/QOS cluster defaults; no user association returned, AccountingStorageEnforce=none. Successful G12 excludes node01,4 CPUs,64G host memory; G13 reuses it. Smoke requests one GPU20min. Main walltime from measured smoke throughput, total requested <=12 GPU-hours and at most two active G13 GPUs. Resources/runtime/memory in smoke_test.json, seed completion metadata, slurm_jobs.csv, allocation_details.psv and budget.json.
