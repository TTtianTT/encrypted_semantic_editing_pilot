# Publication scope

The conversation explicitly authorized uploading to GitHub. This delivery adds only `experiments/reference_frame_pilot_v3/` to the public branch based on v2 commit `8bf6d42`. Local unrelated experiment commits are not included. v1/v2 are unchanged.

Included: protocol, synthetic controlled data, code, operator initial/best checkpoint, logs, complete outputs, evaluation, report, anonymous review packet and separately named mapping. No human participant data are present. The mapping must be withheld from reviewers for actual blinded review.

Excluded: BART weights, environment, credentials, Python caches and local-only `checkpoints/G3/latest.pt` (optimizer/RNG recovery state). Full local artifacts are listed in `artifact_manifest.json`; public files are listed in `PUBLICATION_MANIFEST.json`. Each manifest excludes itself and the other manifest to avoid circular hashes.

Single-seed results and model review are not human-validated ground truth. Test data and outputs are public for reproducibility, so future independent confirmation must use new worlds.
