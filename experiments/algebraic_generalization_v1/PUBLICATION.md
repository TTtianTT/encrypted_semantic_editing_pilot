# GitHub publication scope

This G4 branch starts at `origin/main` commit `e1ec57b`, which contains the G3 baseline. It contains only `experiments/algebraic_generalization_v1/`; unrelated local experiment branches are not included.

The user explicitly requested uploading these changes. Published files include source code, frozen configuration, synthetic-world evaluations, trajectory texts and semantic states, full latent tensors as lossless zstd parts, probe and repair checkpoints, logs, report, and checksum audits. Run `python experiments/algebraic_generalization_v1/restore_latents.py` after cloning to reconstruct the two original latent `.pt` files and verify SHA256.

The original uncompressed 241 MiB tensor files remain local and are ignored by Git. The pretrained BART model and local environment are not published. Results use one operator-training seed and controlled synthetic English; model review is not human ground truth.
