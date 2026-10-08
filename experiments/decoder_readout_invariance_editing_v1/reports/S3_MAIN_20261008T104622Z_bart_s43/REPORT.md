# BART S3 seed43 training/validation terminal

COMPLETED；Slurm3043_0；allocation GPU-hours0.186667。192train worlds、64validation worlds，每world12合法操作×自然/history两来源，来源各768，均未按方法成功筛样本；所有方法rank16/400updates、同seed初始化与全部400 minibatch序列已逐条核验。Plain重用已完成checkpoint及预测，未额外复训，旧allocation已在账本中计费。

| 方法/候选 | 联合成功 | 目标正确 | 非目标内容 | keep权重 | mechanism权重 |
| --- | --- | --- | --- | --- | --- |
| Mechanism-guided | 1519/1536 | 1532/1536 | 1532/1536 | 0.1 | 0.1 |
| Output-only | 1520/1536 | 1525/1536 | 1525/1536 | 0.1 | 0 |
| Plain | 1536/1536 | 1536/1536 | 1536/1536 | 0.0 | 0.0 |
| Random-site | 1524/1536 | 1532/1536 | 1532/1536 | 0.1 | 0.1 |

每方法64独立world，1536操作不是1536独立样本；当前源读出与旧Plain完整记录一致。全部逐样本预测、400更新日志及小checkpoint保存；NUMERICAL_AUDIT从全量记录独立重算。teacher分支无梯度、student H→decoder保留梯度，backbone/history前后SHA相同。所有推理输入H/mask/op，一次latent forward，无donor/目标全文/重编码/推理反传。训练gold仅用于loss。

候选或正式训练的validation结果均为探索性；固定128独立test仍因5个派生core暴露阻塞，正式test评测0，不能作为独立机制编辑确认。方法选择只能按锁定validation规则；同单操作分数不意味着相同长期轨迹。完整轨迹本run未执行，后续需要在各方法自己的latent输出上测1/2/3/5步。

计算成本：Plain训练每update8 student forward/8 backward；keep/mech方法额外8 teacher forward。同更新预算不是同GPU耗时，实际train walltime/前反向次数记录在NUMERICAL_AUDIT；初始化参数量相同。扰动norm全样本已记录，将按训练前锁定norm bins汇总。全部失败/负结果保留。
