# State handoff diagnosis v1

Frozen BART P second-step attribution and original T5Gemma F200/R200 cross handoff. No training. Read protocol.yaml, AUDIT.md and STATUS.md.

CPU CLI: `python -m experiments.state_handoff_diagnosis_v1.prepare --round R00`, then submit/collect/publish with the same `--round`. Submit only via this interface; run only in sbatch+srun. Immutable execution snapshot and actual manifest are recorded for every run. Outputs under ignored local/runs; small compressed observations and reports published per terminal run.
