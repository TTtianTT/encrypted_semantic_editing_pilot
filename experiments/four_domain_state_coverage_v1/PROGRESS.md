# 当前进度（工件快照，非最终结果）

UTC 2026-10-02T16:54:04.477221+00:00。所有GPU计算经Slurm；历史峰值2卡，最近账本累计8.889 GPU小时。

- formal: {"completed": 7, "not_admitted": 6, "in_progress": 3, "not_started": 14}
- identity_probe: {"not_started": 30}
- linguistic_controls: {"not_started": 8}
- position_foils: {"not_started": 8}
- symbol: {"not_started": 8}

任务/准入/checkpoint/已写预测分片见PROGRESS.json。作业和依赖见submissions.json；分配、时限和退出状态见budget.json。

恢复批次2620只接续原正式数组的技术超时，所有后续GPU批次均排在此前。CPU汇总2590在全部阶段之后运行，生成报告及工件核验；Git提交与推送由监督代理另行完成。
