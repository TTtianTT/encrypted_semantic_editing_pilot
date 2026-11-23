# NOTE_DEDUPE（symmetry_composability_v1）

- 日期：2026-11-23
- 检查内容：本实验各 confirm world 的渲染文本（模板 0 与模板 3，全部状态），与 v1 train/dev + pre-v1 (pre-v1 = four_domain_state_coverage_v1, canonical_confirmation_v1, manifold_controls_v1, operator_residual_v2) 的渲染文本完全相同的数量（按域、按 split）。
- 重复的 world ID：见 `experiments/composability_mechanisms_v3/results/patch/dedupe_v1_excluded.json`（分支 `experiment/composability-mechanisms-v3`）。
- 生成：`composability_mechanisms_v3/p_diag.py` 的 P3（Slurm CPU 作业）；重算用 `p3_rerun.py` 在已解码的分片上重跑本实验锁定的分析脚本，只去掉重复 world 的记录，不重新编码或解码。

| 域 | split | confirm world 数 | 与 v1 train/dev 重复 | 与 pre-v1 重复 | 任一来源重复（已去掉） | 比例 |
| --- | --- | --- | --- | --- | --- | --- |
| weekday | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |
| month | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |
| compass | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |
| egoside | confirm | 160 | 0（模板 0：0） | 0（模板 0：0） | 0 | 0.000 |
| daysago | confirm | 160 | 0（模板 0：0） | 22（模板 0：22） | 22 | 0.138 |

## 去掉重复 world 后重算的关键数字

| 结论或预测 | 原值 | 去重后 | 判定是否改变 |
| --- | --- | --- | --- |
| P1 | pass：{"weekday": 1.0, "month": 1.0} | pass：{"weekday": 1.0, "month": 1.0} | 否 |
| P2 | pass：{"weekday": 1.0, "month": 1.0} | pass：{"weekday": 1.0, "month": 1.0} | 否 |
| P3a | fail：{"diff": -0.0001, "ci95": [-0.0003, 0.0001]} | fail：{"diff": -0.0001, "ci95": [-0.0003, 0.0001]} | 否 |
| P3b | fail：{"diff": 0.0, "p": null} | fail：{"diff": 0.0, "p": null} | 否 |
| P4 | pass：{"R7_plus_from_two": 1.0, "R10_alternating": 1.0} | pass：{"R7_plus_from_two": 1.0, "R10_alternating": 1.0} | 否 |
| P5 | fail：{"C1_R2_max": 0.0, "C3_RN_min": 0.4437} | fail：{"C1_R2_max": 0.0, "C3_RN_min": 0.4437} | 否 |
| P6 | pass：{"weekday": 0.2274, "month": 0.1947} | pass：{"weekday": 0.2274, "month": 0.1947} | 否 |
| P7 | report only (n = 5)：{"rho": NaN} | report only (n = 5)：{"rho": NaN} | 否 |

## 结论

全部判定不变。P6（κ_N，由 confirm 编码上的代数分析得到）未重算，表中为原值。
