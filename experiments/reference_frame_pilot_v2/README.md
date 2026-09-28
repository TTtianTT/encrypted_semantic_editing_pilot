# Reference frame pilot v2

范围与预注册门槛见 [PROTOCOL.md](PROTOCOL.md)，实际运行结果见 [REPORT.md](REPORT.md)。v1只读；本轮只用同一冻结BART和LowRank16，最多三个seed42组。

从仓库根运行，复用原`.venv/bin/python`。GPU脚本只允许Slurm+srun，入口`run.slurm <script> [arguments]`：

1. CPU `prepare.py`生成世界、匹配G0/G1数据、G2替换计划及固定审查世界。
2. `run.slurm preflight`：920个合法视图，必须100%重构通过才锁定test。
3. `run.slurm diagnostic_a`：旧checkpoint有限诊断，已有输出复用，不训练。
4. 串行`run.slurm train G0`、`run.slurm train G1`；G1产出dev门槛文件。
5. 仅`evaluation/c_gate.json`允许时运行`run.slurm train G2`；G2重新加载共享initial.pt。
6. `run.slurm test`锁定实际全部checkpoint后执行新测试。
7. CPU `analyze.py`、`audit.py`、`report.py`汇总与审计。`report.py`生成定量报告，模型复核另存review目录。

所有提交前先按budget.json历史job和sacct刷新累计GPU用量；最多7200分配秒、同时一张GPU。恢复须缩短作业限时到剩余额度内，不重复重置15/45分钟额度。训练latest.pt保存optimizer、RNG、step，已经完成的组会跳过；评估按uid补缺失输出。模型/数据/配置不一致不得复用同一目录。

同一世界可能不具备合法的completed/minus3视图，预定不适用清单与每路径分母见data/structural_inapplicability.csv；不把这些数学不可能项当作模型失败，也不声称已覆盖。全部其他失败保留在分母。

`outputs/G*.jsonl`是主要固定矩阵；`*_extended.jsonl`是源±3诊断，不参与选模。`diagnostic_a/outputs.jsonl`是旧IID探索诊断。`review/blind_review.csv`匿名方法和路径，`private_mapping.json`单独保管；没有真人审查结果。
