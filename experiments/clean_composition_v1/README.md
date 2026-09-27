# 干净任务组合诊断：准备中，尚未运行模型

本轮不训练。已执行未使用来源与变体的排除、保守句法/时间风险筛选，导出待真人审核的源句和官方目标；完整审计见candidate_audit.json。规则筛选不是人工确认，不能据此宣称完成新可信评估集。

已实现真实入口：
```
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 .venv/bin/python scripts/prepare_clean_diagnostic.py
# 额外资源审计：允许目标暂时缺失，供真人补写，不生成编辑器输出
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 .venv/bin/python scripts/prepare_clean_diagnostic.py --include-incomplete-targets
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 .venv/bin/python scripts/prepare_clean_diagnostic.py --include-incomplete-targets --include-tfu-sources
# 仅在足量任务经真人审核、数据来源问题解决之后
.venv/bin/python scripts/freeze_clean_diagnostic.py --review <真人审核CSV> --attestation <真人声明JSON>
sbatch --partition=<查询后实际获准分区> experiments/clean_composition_v1/run.slurm
```

协议见PROTOCOL.md，审核说明见TASK_REVIEW.md。冻结脚本会拒绝未完成评分、缺少真人声明、变更源句、不足40/100和重复来源；推理脚本会拒绝未冻结或修改过的数据/检查点。没有通过审核之前不要提交Slurm作业。现有checkpoint参数只读；推理脚本无优化器，不训练。单GPU、4CPU，单作业上限1小时，恢复时核对配置hash并跳过已完成逐样本路径。

生成后输出文件为results/dev.jsonl和test.jsonl，每源12条（共享两个identity，两个既有编辑器各5条编辑路径），记录异常且不删分母。原有auto只能作诊断；真正的继续门槛需要输出真人评分，不能用旧有缺陷的auto冒充。尚未生成输出，所以尚无输出盲审包、配对结果或go/no-go判断；不预填表格。已知63个旧来源需确认属于旧B100或提供ID进一步排除。

`expanded_tfu_candidates/` 进一步加入未使用的原始TFU自然来源句，目标缺失处保留空白供真人补写。它是资源审计候选池，不自动成为新划分，不改变当前冻结协议。若采用新诊断划分，必须先登记与确认新划分方案，再更新冻结入口。
