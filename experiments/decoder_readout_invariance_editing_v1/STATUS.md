# 实际状态（2026-10-08）

整体 BLOCKED，未完成完整S0–S4研究。S0两模型通过；BART S1/S2探索机制完成部分项目；Plain三seed400updates及Original/Plain64world validation单操作/纯latent轨迹完成；T5Gemma一般SAME_TEXT 32探索world完成。

S3其他三方法 BLOCKED_MASK_REVIEW；S4 BLOCKED_TEST_INTEGRITY（5/128派生core已编码；不换split/不补搜）；S5 NOT_RUN_PREREQUISITES。机制增量收益NA。模板OOD UNAVAILABLE。

总2.392500 GPU-hours、16 allocation（3失败），峰值2GPU，全部终态、实时队列无遗留任务。最终16CPU检查通过。所有新文件和临时/缓存/环境/产物位于 /dataset1/zailong/。详见FINAL_REPORT.md及各run稳定报告；推送SHA核验回执在外部ledger。
