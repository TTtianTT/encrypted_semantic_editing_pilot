# Reference frame pilot v3: G3 stage supervision

See [PROTOCOL.md](PROTOCOL.md) for the pretraining protocol and [REPORT.md](REPORT.md) for measured results. Only G3 seed42 is newly trained. G1/G2 and their diagnostic outputs are reused from v2; both prior experiment directories remain read-only.

Reproduction (existing environment, BART files and v2 artifacts required):

1. `prepare.py` creates and freezes confirmation data; refuses to overwrite the lock. Shipped data are already prepared.
2. `sbatch --partition=B300q experiments/reference_frame_pilot_v3/run.slurm train` validates loss/gradients, trains G3, observes dev trajectories and selects by atomic dev token NLL.
3. `sbatch --partition=B300q --time=00:30:00 --export=ALL,RF_WALL_SECONDS=1740 experiments/reference_frame_pilot_v3/run.slurm test` freezes checkpoints and performs paired evaluation. Outputs resume by unique row ID.
4. `account.py JOB_IDS...` records Slurm allocation accounting; always check remaining cumulative budget before submission.
5. CPU-only `audit.py`, `analyze.py`, `report.py` produce verification, statistics and report.

Use a fresh versioned directory to rerun training from scratch. Do not remove locks or overwrite the delivered results. Completed checkpoints are reused. Latest optimizer state is local-only; best and initial operator weights are included, BART weights and credentials are excluded.

The baseline target text is oracle information only in target-reconstruction diagnostics. Ordinary inference only uses input text and fixed operation IDs. `trajectory_joint` requires every stage on the same world to pass, not the average stage score. No human labels have been supplied.
