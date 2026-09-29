# Delivery and publication scope

Only `experiments/reference_frame_cross_backbone_v1/` is added. Local work is on `experiment/reference-frame-cross-backbone-v1`, based on local `18bcf8c`. The public branch is based on the reviewed public v3 commit `e1ec57b01a6aa8d3ddb2235b1e85c140b1911583`; the new experiment-only commit is replayed there to avoid publishing unrelated local historical commits. Remote `main` is not updated.

Included: protocol and amendment, evidence audit, frozen data/paths/score code, model/interface manifests, calibration A/B raw outputs, small editor initializations and all six checkpoints per trained group plus best, logs, complete confirmation outputs, paired statistics, reports and review package. All weights in checkpoint files are editor weights, not language-model weights.

Excluded from Git: downloaded base models, environments, model download caches, credentials, Python caches, and `latest.pt` optimizer/RNG recovery files. The latter remain locally under `checkpoints/t5gemma-2b-2b-ul2-it/{G1,G3}/latest.pt`. Training completed 600 updates per group; these files are retained for truthful local recovery/provenance, not used for additional training.

`PUBLICATION_MANIFEST.json` records the hash and size of every public experiment file except itself. Run-time code used for training and IT confirmation is separately fixed in `training_code_manifest.json`; later analysis and metadata enrichment did not change predictions or scores. `evaluation/provenance_enrichment.json` records the unchanged prediction/score/timing payload hashes when adding per-row provenance to completed outputs.

The review mapping is stored separately from the anonymous CSV. Human labels are empty. Publishing a review package does not constitute human validation.
