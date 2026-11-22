# DEVIATIONS

Every difference from PLAN.md, with time (UTC+local server clock), reason, impact, and whether it happened before or after the E1.3 protocol lock.

| # | 时间 | 单元 | 偏差 | 原因 | 影响 | 锁定前/后 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-11-22 21:49 | P0 | BART revision 没有直接写在 `models/manifest.json` 里（该文件只记录各文件的 SHA256）。改为核对：`models/bart_metadata.json` 的 `sha`、四域 `model_manifest.json` 的 `revision`、仓库 `config.json` 的 `model_revision` 都等于 `aadd2ab0…`，且 `models/bart-base/*` 的 SHA256 与 `models/manifest.json` 一致。 | manifest 格式与计划描述不同 | 无；冻结检验更严格 | 前 |
| 2 | 2026-11-22 21:49 | P0 | 作业名改为 `symcomp-<phase>`（通过 `--job-name`），便于 `sacct` 记账；新增 `ledger.sh`（jq 写 `run_ledger.json`，不运行 Python）。 | 记账便利 | 无 | 前 |
| 3 | 2026-11-22 21:55 | E0.2 | 作业 72266 失败：B300 上 NVRTC 无法 JIT 复数 `abs`（`invalid value for --gpu-architecture`）。特征值改在 CPU 上算后重交。 | 已知环境原因，非不明失败 | 无；数值定义不变 | 前 |
| 4 | 2026-11-22 21:59 | E0.2 | 作业 72271 手动取消：环 L = A₋A₊ 的幂范数原用 768 维全矩阵 GPU SVD，单算子约 1–2 分钟，有超 1 小时之虞。改为在 span[U₊,V₊ᵀ,U₋,V₋ᵀ]（L 在其正交补上为恒等）内精确计算，CPU float64；重交为 72274（33 秒完成）。 | 性能 | 无；数学上等价（‖Lᵏ‖ = max(1, ‖L_Qᵏ‖)，‖Lᵏ−I‖ = ‖L_Qᵏ−I‖） | 前 |
| 5 | 2026-11-22 21:58 | E0.2 | e_inv 的单一标量取两种复合（T₋∘T₊ 与 T₊∘T₋）各自 world 均值的平均（`mean_both`），G0(c) 用它判定；两个方向分别是否满足也一并记录在 `g0_decision.json`。 | 计划未指定方向 | 解释性选择，无数据依赖 | 前 |
| 6 | 2026-11-22 22:20 | G0 | **AMENDMENT_01**（负责人书面授权，数据驱动）：G0(a) 由 E1.2 的 G1a 代替，(c) 去掉 ISO 条款，规则改为 (b) 或 (c1∧c2)。修订后判定为 pass（`results/g0_amended_decision.json`）；原判定 fail 保持不变。 | 时间域 7 状态几何被 token 长度簇混淆；ISO 与 e\_inv 方向矛盾 | 进入 E1.0–E1.2 与 E2；E1 预测仍在看到 E1 编辑结果前锁定 | 前 |
| 7 | 2026-11-22 22:30 | E1.1 | 语料从 HuggingFace `Salesforce/wikitext` 的 parquet（wikitext-103-raw-v1 train，2 个文件共 314 MB，SHA 记录在 `results/e1_corpus.json`）在登录节点下载，存于 `local/corpus_download/`。分词为 `[A-Za-z]+`，上下文小写，取前 50k；P(c) 用 0.75 次方平滑。compass/egoside 只匹配小写形式（排除 “North America” 等专名）。daysago 的 “N days ago” 每个短语出现 0–5 次（<200），按计划改用数词 two…nine，变体中排除数词作为上下文。 | 计划未指定下载源与分词细节 | 无；E1.1 只作辅助指标 | 前 |
