# 实际状态

S0 BART/T5Gemma 均通过；各8/8 train smoke，12/12 CPU 检查。S1 原生 SDPA 72 worlds/288 pairs discovery-validation-replay 已完成并发布，最大JS0.0124072。独立test未解封，模板OOD UNAVAILABLE。

S2 首次手算AV重构失败已发布；S2_NATIVE job3025正在原生SDPA上进行精确因果干预，实际局部AV误差0。S3_PLAIN三seed快照准备完成，未提交；其他S3训练待内容位置人工抽查。S4/S5未运行。当前资源0.862222 GPU-hours（不包含仍运行的3025），历史峰值2GPU，目前1GPU。所有新临时文件/依赖/产物位于 /dataset1/zailong/ 下。
