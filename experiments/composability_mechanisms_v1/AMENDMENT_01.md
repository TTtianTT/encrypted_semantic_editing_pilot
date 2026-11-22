# AMENDMENT_01（composability_mechanisms_v1）

- 日期：2026-11-23
- 决定人：项目负责人
- 时间点：核心部分（S1–S3）报告提交之后；S4、S5 尚未产生任何数据。

## 1. S1b（B1、B2）
- B1、B2 改判为“无效：重建天花板”。原因：模板 0 的 reencode 单步成功率只有 0.25–0.41，BART 会改写事实从句中的物体名（DEVIATIONS 第 3 条）；正对照 B1 失败，B2 无法解释。观测值照常保留在 REPORT.md 中。
- B3（C1 的 R_2 ≤ 0.20，9/9 通过）与 B4（锁定前测得，非前瞻）不变。
- Q2 在本实验中维持“不可判定”。
- 复检移到 composability_mechanisms_v2 的 B′ 单元：改用模板 3；全部使用新生成的 confirm world；锁定前在 train/dev 上通过重建闸门（reencode 单步 ≥ 0.99）和正对照准入；新增 bind3fix 对照。
- 本实验的 S1b confirm world 退役：锁定后已在其上评测过模板 3 的 reencode，不再用于任何确认性检验。

## 2. S4、S5
- 不在本实验执行，并入 composability_mechanisms_v2：S4 → A 单元，S5 → T 单元。
- PLAN.md §9 中 S4 的预测逐字带入新协议；S5 的原文照录，并在新协议中按本实验的阈值具体化。两者仍作为确认性预测：它们未写入本实验的 protocol.json，但随 PLAN.md 在任何 S4/S5 数据之前已提交。

## 3. 其他
- 本实验的其他预测、阈值与判定不变。
- REPORT.md 只在 §1 的 Q2 条目与 §7 各加一行，指向本文件。
