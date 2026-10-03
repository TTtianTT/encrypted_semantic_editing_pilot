# 当前进度（工件快照，非最终结果）

UTC 2026-10-03T08:06:00.021120+00:00。所有GPU计算经Slurm；历史峰值2卡，最近账本累计36.582 GPU小时。

- formal: {"completed": 21, "not_admitted": 9}
- identity_probe: {"completed": 21, "not_executed_not_admitted_or_behavior_incomplete": 9}
- linguistic_controls: {"in_progress": 2, "completed": 3, "not_started": 3}
- position_foils: {"not_started": 8}
- symbol: {"symbol_diagnostic": 8}

任务/准入/checkpoint/已写预测分片见PROGRESS.json。作业和依赖见submissions.json；分配、时限和退出状态见budget.json。

恢复批次2620只接续原正式数组的技术超时，所有后续GPU批次均排在此前。CPU汇总2590在全部阶段之后运行，生成报告及工件核验；Git提交与推送由监督代理另行完成。
