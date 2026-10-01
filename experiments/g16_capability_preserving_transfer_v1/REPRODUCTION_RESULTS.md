# G16 本次执行与CPU结果复现

科学训练/推断入口、配置、数据及依赖在data/lock.json中，未修改。旧G15/G13/G14工件只读。README为事前流程，本文件补充交付顺序：

```bash
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/account.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/analyze.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/finalize.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/publish.py
```

analyze可使用已上传per_example_sSEED.jsonl.gz/learning_per_example_sSEED.jsonl.gz而不加载GPU。重新做完整GPU实验需要精确基础BART与本地模型路径，不能在现有锁/结果上覆盖；使用新的独立实验路径并保留原工件。finalize的执行本地cache证明依赖实际本地大cache/候选/optimizer，Git不包含它们，路径/hash在artifact_manifest.json；execution_timeline使用保存的一次性本地mtime证据，不把clone时间冒充执行时间。

finalize/publish是锁后CPU交付助手。旧final接口原step字段恒200；G16已在原推断中记录actual_updates和精确SHA，导出将step规范化为actual_updates并保留legacy_final_interface_step。文本、gold、解析、联合/exact、gate与模型SHA未改变。没有科学配置修改或GPU工程重试。publish仅展示CSV统计、列失败cell和事后描述G边界案例；不重选模型或增科学比较。

本次smoke2520；训练array2521（raw2522/2523/2521对应seed42/43/44）；确认array2524（raw2525/2526/2524）。全部7allocation成功；实际2.073611GPUh，申请3.40GPUh，峰值2。提交命令在commands.log，资源查询在allocation_details.psv/slurm_step_usage.psv。未上传基础模型、环境、凭据、大型latent或无关历史。
