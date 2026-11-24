# AMENDMENT_01（composability_mechanisms_v5，锁定后）

- 日期：2026-11-24，全部锁定后作业与 `analyze.py` 完成之后。
- 性质：**只增加描述性的置信区间，不改变任何锁定的判定、阈值或数据**。由 Claude 在写报告时加入，提交给负责人审阅。

## 变更
- **原因**：v6 计划 B10 沿用 v5 §13，要求预测对照表的每个观测值给出 95% CI。锁定的 `analyze.py` 只对 M4、CT1、CT2 的配对差值给出 world-cluster bootstrap CI。M1–M3 与 K1–K4 的成功率只有点值。
- **做法**：
  - 新增 `report_ci.py`（CPU 作业 73100），只读 `results/chains.csv`。
  - 对每个（骨干，域，方法，路径）在预测用到的步数（1、2、8、12、2N、30）上，按 n 个 world 计算 Wilson 95% 区间，写入 `results/report_ci.json`。
  - 报告中，seed 中位数的条目逐 seed 给出区间。
- **不变**：`protocol.json`、全部锁定源码、`results/predictions.json` 与 `results/paper_export.json` 都不改动。判定只来自 `analyze.py` 的锁定规则。

## 锁定后的其他情况
- 锁定后的作业都一次完成，没有失败或重跑：G6-0 73062/73066，M 73063/73067，C 73064，K 73065，分析 73098，分片打包 73099。
- 一致性：链式评测中记录的潜空间 argmax 与锁定的模拟文件逐 world、逐步完全一致（不一致 0 处）。
