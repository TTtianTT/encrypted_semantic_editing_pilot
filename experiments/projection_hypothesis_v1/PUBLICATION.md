# GitHub publication scope

The G5 branch starts at the published G4 commit `ce0ef36` and adds only `experiments/projection_hypothesis_v1/`. It reuses G4's losslessly archived pure-latent tensor files and the frozen G3 checkpoint; no new editor or projector is trained.

Published artifacts include code, configuration, synthetic-world trajectories, paired length and geometry tables, probe validation and weights, pooled vectors, audit, report, and job logs. The 11 MiB pooled-vector tensor does not replace G4's full latents. G4's `restore_latents.py` reconstructs those full tensors after cloning.

These are single-seed results in a controlled grammar. The world data and outputs are public, so independent confirmation requires new worlds.
