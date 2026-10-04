# 资源核验

全部GPU计算经sbatch+srun，单任务1GPU；累计2.908333 allocation GPUh，本项目峰值2，账号本轮峰值2。失败/重试计入，batch/step行不重复加总。

|seed|R源pipeline秒|F源pipeline秒|额外R减F_来源GPUh|R减F_训练壁钟GPUh|R减F_含评估阶段GPUh|
|---|---|---|---|---|---|

刷新pipeline按实际GPU分配下的壁钟时间记录，包括新编码、前缀计算、质量解码、缓存I/O；不是GPU内核利用率。optimizer、训练和两次评估时间在condition_compute.csv；评估输出长度会影响运行时间，因此额外来源成本与含评估阶段净差分别列。正式阶段无恢复时，可定位训练+评估阶段的壁钟可比较；共享模型加载、任务进入/退出及不可定位开销由总allocation记账覆盖。全部其他模型加载、评估、队列后分配等待与CPU写盘开销包含在总allocation记账中，不归因于纯前缀计算。原始JobID、GPU请求、节点、开始结束、退出码和Elapsed在slurm_accounting.psv；Start/End保留集群UTC+8显示，来源生成UTC另存。
