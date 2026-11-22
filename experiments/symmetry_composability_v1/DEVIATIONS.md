# DEVIATIONS

Every difference from PLAN.md, with time (UTC+local server clock), reason, impact, and whether it happened before or after the E1.3 protocol lock.

| # | 时间 | 单元 | 偏差 | 原因 | 影响 | 锁定前/后 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-11-22 21:49 | P0 | BART revision 没有直接写在 `models/manifest.json` 里（该文件只记录各文件的 SHA256）。改为核对：`models/bart_metadata.json` 的 `sha`、四域 `model_manifest.json` 的 `revision`、仓库 `config.json` 的 `model_revision` 都等于 `aadd2ab0…`，且 `models/bart-base/*` 的 SHA256 与 `models/manifest.json` 一致。 | manifest 格式与计划描述不同 | 无；冻结检验更严格 | 前 |
| 2 | 2026-11-22 21:49 | P0 | 作业名改为 `symcomp-<phase>`（通过 `--job-name`），便于 `sacct` 记账；新增 `ledger.sh`（jq 写 `run_ledger.json`，不运行 Python）。 | 记账便利 | 无 | 前 |
| 3 | 2026-11-22 21:55 | E0.2 | 作业 72266 失败：B300 上 NVRTC 无法 JIT 复数 `abs`（`invalid value for --gpu-architecture`）。特征值改在 CPU 上算后重交。 | 已知环境原因，非不明失败 | 无；数值定义不变 | 前 |
| 4 | 2026-11-22 21:59 | E0.2 | 作业 72271 手动取消：环 L = A₋A₊ 的幂范数原用 768 维全矩阵 GPU SVD，单算子约 1–2 分钟，有超 1 小时之虞。改为在 span[U₊,V₊ᵀ,U₋,V₋ᵀ]（L 在其正交补上为恒等）内精确计算，CPU float64；重交为 72274（33 秒完成）。 | 性能 | 无；数学上等价（‖Lᵏ‖ = max(1, ‖L_Qᵏ‖)，‖Lᵏ−I‖ = ‖L_Qᵏ−I‖） | 前 |
| 5 | 2026-11-22 21:58 | E0.2 | e_inv 的单一标量取两种复合（T₋∘T₊ 与 T₊∘T₋）各自 world 均值的平均（`mean_both`），G0(c) 用它判定；两个方向分别是否满足也一并记录在 `g0_decision.json`。 | 计划未指定方向 | 解释性选择，无数据依赖 | 前 |
