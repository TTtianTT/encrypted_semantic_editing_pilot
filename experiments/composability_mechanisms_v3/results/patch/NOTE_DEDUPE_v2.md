# NOTE_DEDUPE（composability_mechanisms_v1）

- 日期：2026-11-23
- 检查内容：本实验各 confirm world 的渲染文本（模板 0 与模板 3，全部状态），与 v1 train/dev + v1 confirm + v2 S1b train/dev + pre-v1 (pre-v1 = four_domain_state_coverage_v1, canonical_confirmation_v1, manifold_controls_v1, operator_residual_v2) 的渲染文本完全相同的数量（按域、按 split）。
- 重复的 world ID：见 `experiments/composability_mechanisms_v3/results/patch/dedupe_v2_excluded.json`（分支 `experiment/composability-mechanisms-v3`）。
- 生成：`composability_mechanisms_v3/p_diag.py` 的 P3（Slurm CPU 作业）；重算用 `p3_rerun.py` 在已解码的分片上重跑本实验锁定的分析脚本，只去掉重复 world 的记录，不重新编码或解码。

| 域 | split | confirm world 数 | 与 v1 train/dev 重复 | 与 v1 confirm 重复 | 与 v2 S1b train/dev 重复 | 与 pre-v1 重复 | 任一来源重复（已去掉） | 比例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weekday | confirm2 | 160 | 15（模板 0：15） | 25（模板 0：25） | 0（模板 0：0） | 0（模板 0：0） | 40 | 0.250 |
| month | confirm2 | 160 | 18（模板 0：18） | 19（模板 0：19） | 0（模板 0：0） | 0（模板 0：0） | 37 | 0.231 |
| compass | confirm2 | 160 | 3（模板 0：3） | 11（模板 0：11） | 0（模板 0：0） | 0（模板 0：0） | 14 | 0.087 |
| egoside | confirm2 | 160 | 10（模板 0：10） | 8（模板 0：8） | 0（模板 0：0） | 0（模板 0：0） | 18 | 0.113 |
| daysago | confirm2 | 160 | 19（模板 0：19） | 17（模板 0：17） | 0（模板 0：0） | 17（模板 0：17） | 52 | 0.325 |
| pron3 | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |
| name3 | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |
| bind3 | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |

## 去掉重复 world 后重算的关键数字

| 结论或预测 | 原值 | 去重后 | 判定是否改变 |
| --- | --- | --- | --- |
| G2_0 | True：{"RRR16_min": 1.0, "C1_R2_max": 0.0} | True：{"RRR16_min": 1.0, "C1_R2_max": 0.0} | 否 |
| A1 | H-slot：1.0 | H-slot：1.0 | 否 |
| A2 | H-slot：{"rho": null, "min_scr": 1.0} | H-slot：{"rho": null, "min_scr": 1.0} | 否 |
| A3 | H-slot：{"weekday": 0.0, "month": 0.0, "compass": 0.0, "egoside": 0.0} | H-slot：{"weekday": 0.0, "month": 0.0, "compass": 0.0, "egoside": 0.0} | 否 |
| Q1 | H-slot：null | H-slot：null | 否 |
| A4 | False：null | False：null | 否 |
| A5 | False：null | False：null | 否 |
| B1 | False：{"pron3": 0.2687, "name3": 0.3625} | False：{"pron3": 0.2687, "name3": 0.3625} | 否 |
| B2 | H-bind：0.0 | H-bind：0.0 | 否 |
| B3 | True：0.0 | True：0.0 | 否 |
| B4 | H-bind：null | H-bind：null | 否 |
| Q2 | H-bind：null | H-bind：null | 否 |
| R1 | True：{"weekday": 6, "month": 11, "compass": 3, "egoside": 4} | True：{"weekday": 6, "month": 11, "compass": 3, "egoside": 4} | 否 |
| R2 | True：{"month_r8": 1.0, "weekday_r4": 1.0} | True：{"month_r8": 1.0, "weekday_r4": 1.0} | 否 |
| R3 | False：{"weekday": 0.0, "month": 0.0} | False：{"weekday": 0.0, "month": 0.0} | 否 |
| R4 | None：null | None：null | 否 |
| R5 | None：null | None：null | 否 |
| M1 | H-instr：null | H-instr：null | 否 |
| M2 | H-instr：null | H-instr：null | 否 |
| M3 | H-instr：null | H-instr：null | 否 |
| M4 | H-approx：null | H-approx：null | 否 |
| Q4 | H-instr：null | H-instr：null | 否 |

## 结论

全部判定不变。M1–M4（S3，GPU 上在 confirm2 编码上计算的汇总量）与 A4、A5（只依赖拟合）未重算，表中为原值；S2 与 S1a 的链式结果已重算。
