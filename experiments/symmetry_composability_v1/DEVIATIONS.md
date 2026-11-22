# DEVIATIONS

Every difference from PLAN.md, with time (UTC+local server clock), reason, impact, and whether it happened before or after the E1.3 protocol lock.

| # | 时间 | 单元 | 偏差 | 原因 | 影响 | 锁定前/后 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-11-22 21:49 | P0 | BART revision 没有直接写在 `models/manifest.json` 里（该文件只记录各文件的 SHA256）。改为核对：`models/bart_metadata.json` 的 `sha`、四域 `model_manifest.json` 的 `revision`、仓库 `config.json` 的 `model_revision` 都等于 `aadd2ab0…`，且 `models/bart-base/*` 的 SHA256 与 `models/manifest.json` 一致。 | manifest 格式与计划描述不同 | 无；冻结检验更严格 | 前 |
| 2 | 2026-11-22 21:49 | P0 | 作业名改为 `symcomp-<phase>`（通过 `--job-name`），便于 `sacct` 记账；新增 `ledger.sh`（jq 写 `run_ledger.json`，不运行 Python）。 | 记账便利 | 无 | 前 |
