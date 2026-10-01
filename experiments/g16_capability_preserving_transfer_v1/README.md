# G16复现入口

精确父提交155cd8793d2f83d21c0f567e45073d845753ad6f。旧G15/G13数据、实现、checkpoint只读复用，新g16 namespace；当前独立worktree保留原用户工作区。使用原`.venv`和BART-base，不升级环境。

准备及锁定（prepare拒绝覆盖锁）：

```bash
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/audit_g15.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/prepare.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/cpu_check.py
```

GPU只能Slurm分配+srun，各阶段不得重叠。CPU submit检查重复/活动G16及预算；smoke测完整dev和final接口，不用U或新确认。训练必须完整NF各200，guard不另训。等所有训练allocation完成，再锁定全部选择，之后确认：

```bash
bash experiments/g16_capability_preserving_transfer_v1/scripts/submit.sh smoke
# Wait COMPLETED/pass smoke; resource plan must fit4GPU hours including reserve.
bash experiments/g16_capability_preserving_transfer_v1/scripts/submit.sh train
# Wait all3 train tasks COMPLETED;6final and3 immutable selections exist.
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/selection.py
bash experiments/g16_capability_preserving_transfer_v1/scripts/submit.sh confirm
# Wait all3 confirm tasks COMPLETED.
bash experiments/g16_capability_preserving_transfer_v1/scripts/collect_results.sh
```

step0/50/100/150/200 train诊断采用小固定hash子集；dev0及全部8候选用完整128/status。selection.py只看F开发原始计数并永久锁最早合格，不用own second/U/G-today，不fallback。诊断保持Python/CPU/CUDA RNG；每10步/候选保存editor/optimizer/RNG/完整日志/schedule，可恢复中断的候选诊断而不重训已完成更新。

最终版本P、N-final、F-final、存在时F-guard；同SHA复用。per_example_sSEED.jsonl.gz保留完整自由输出、gold/frame/解析/raw与conditional，learning_per_example_sSEED.jsonl.gz保留所有阶段；上传后CPU analyze可从这些archive恢复。大型local caches与候选/optimizer不上传，精确路径/hash在data缓存manifest及最终工件目录。main数据/来源角色、guard实际步与完整200步算力分别记录。

事前PROTOCOL及科学锁不可改。REPORT/INTERPRETATION记录真实四个问题答案、逐seed失败cell与门槛、CI/sample SD、JobIDs/预算和偏离；工作阈值并非总体保证。本轮是已考察过U的新世界复验，不是新优化算法、无限长组合或开放语言泛化。
