# Reference frame pilot v1

独立实验目录；不修改原实验。方案见 [PROTOCOL.md](PROTOCOL.md)，实际结论见 [REPORT.md](REPORT.md)。没有真人审核，不应把自动结构化分数当成人工真值。

运行顺序：

1. `prepare.py`生成分组数据及独立解析/规则检查，`configure.py`验证模型hash、共同长度和冻结manifest。已冻结时拒绝覆盖。
2. `sbatch --partition=B300q experiments/reference_frame_pilot_v1/run_e0.slurm`。
3. 仅E0通过后：`run_train.slurm Shift 42`和`run_train.slurm LowRank16 42`串行提交；`summarize_dev.py`计算E1门槛。
4. 仅E1通过后：同入口串行补两种方法的43、44，共六组训练。
5. `run_eval.slurm`要求六组complete和best哈希锁定，只生成规定测试/对照，不调参。
6. `analyze.py`汇总记录级统计和盲审包；`report.py`生成报告。

所有脚本均从仓库根运行，CPU用原`.venv/bin/python`，GPU仅Slurm分配中的srun。提交前必须按budget.json中全部历史job用sacct累计实际单GPU分配秒，扣除失败/重启用量；可恢复不等于获准增加预算。时限须不超过剩余额度，不直接重复默认作业时限。输出JSONL逐批落盘，训练latest.pt含optimizer、RNG和实际步数。既有完成组不会重复训练。

`outputs/atomic.jsonl`包含规定基线与神经方法的全部原子测试；`outputs/composition.jsonl`包含两种链和中间诊断；`outputs/reconstruction_controls.jsonl`保存共同两次重建对照。`evaluation/dev/`独立保留E1统计，顶层evaluation为正式测试。测试结果锁定后不重跑不同配置到本目录。

`review/blind_review.csv`供真人填写；`private_method_map.json`不交给盲审者。模型复核不能替代真人审核。
