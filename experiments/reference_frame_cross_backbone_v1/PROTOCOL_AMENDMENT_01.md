# 执行资源上限修订

2026-09-29，在FLAN-T5-base准入完成后，用户明确允许最多同时两张GPU，并要求使用srun和sbatch。并发上限由1改为2；总GPU分配秒14400和准入总秒3600不变，按每张卡的分配时间累加，不重复累计父/step。模型顺序、数据/评分、A/B包装、训练配方和预算停止规则均不变。原PROTOCOL及原锁hash保留。所有作业仍通过run.slurm中的srun执行，由sbatch分配资源。最多两张是上限，不要求无用并行分配。

模型下载位置依用户明确要求为/dataset1/zailong/models/reference-frame-cross-backbone/，不上传基础权重。此次修订不由模型成绩触发。
