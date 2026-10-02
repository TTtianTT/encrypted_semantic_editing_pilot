# Execution-order correction for remaining tasks

Initial engineering checked all eight model/domain combinations, followed by a
fixed T5 copy-interface check. However, the initial formal array bundled each
combination's600-update atomic admission and subsequent N/S/M before other
combinations' final600-update atomic admission had run. This does not fully follow
the requested global admission-before-supplement execution order. Completed
predictions/checkpoints are retained with this deviation disclosed; they are not
retrospectively described as following a global600-update gate phase.

The remaining unstarted original formal children16–23 are held. A single
eight-task %2 one-GPU array, waiting for the two currently running children14/15,
executes only their already authorized P600 and full dev reconstruction/atomic/
gold-next gates. It writes the original P location and dev gate, without test
evaluation, U training, supplement training or source generation. The original
scientific code, data, seeds, hyperparameters, selection rule, mask, decoder and
thresholds remain frozen. P training is not duplicated: original formal tasks
subsequently reuse the completed P and dev gate. Atomic checkpoint hashes and
dev gate provenance are recorded before release.

One zero-GPU CPU controller task follows the entire preflight array and releases
only these eight held original children. Their original unified formal array%2
then continues. All other GPU phases still wait for the original formal parent,
so they cannot overlap the inserted preflight array. Submission holds and
dependencies are checked under the same project lock; no unrelated job is changed.
The inserted phase uses six-hour allocations in verified B300q and one GPU/task;
the48GPUh total cap and global two-GPU cap remain unchanged. Scientific training
updates/data exposure are exactly the original budgets; only task packaging and
the order of remaining atomic admission are changed. If a preflight technical
failure occurs, the later original task resumes its unfinished P normally.

This amendment cannot undo the order of completed experiments. Final reports must
retain the initial interleaving deviation. Independent space relation confirmation
still uses its separately frozen protocol; source/state results are not pooled.
