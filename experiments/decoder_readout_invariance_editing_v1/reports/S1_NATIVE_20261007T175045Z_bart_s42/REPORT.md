# S1_NATIVE bart seed42 终态

状态：COMPLETED；Slurm 3013_0 / COMPLETED。完成world 72；剩余0；独立test访问0。GPU-hours=0.733056，本轮累计=0.851667，登记allocation峰值=2 GPU。

结果：{"passed": true, "worlds": 72, "panel_counts": {"discovery": {"scanned_worlds": 32, "qualified_worlds": 32, "qualified_pairs": 128}, "validation": {"scanned_worlds": 32, "qualified_worlds": 32, "qualified_pairs": 128}, "replay": {"scanned_worlds": 8, "qualified_worlds": 8, "qualified_pairs": 32}}, "maximum_JS": 0.01240723580121994, "mean_JS": 0.0003062500978124818, "mechanism_status": "DISCOVERY_VALIDATION_ONLY; head-level/fixed-pattern controls still required before regularizer", "independent_test_accessed": 0, "resources": {"model": "bart", "dimension": 768, "backbone_parameters": 139420416, "parameters_per_operator": 25344, "total_editor_parameters": 50688, "gpu": "NVIDIA B300 SXM6 AC", "visible_devices": "0", "allocated_gpu_count": 1, "peak_allocated_bytes": 773005312, "wall_seconds": 2611.0836217950055, "job_id": "3013", "step_id": "0"}}

失败原因：无

当前支持离散 token 决策保持而概率分布不等价。候选 layer5 是 discovery 筛选结果，尚无独立确认或唯一机制证据。正式编辑收益、原子与长期能力、新 T5Gemma 独立资格均为 NA。失败 eager 路径完整保留；本 run 使用验收通过的原生 SDPA。

所有源代码来自manifest指向的immutable snapshot；checkpoint、split、代码SHA在RUN_STATUS/manifest。完整逐样本记录及日志压缩提交；大产物路径与SHA索引见 ARTIFACTS.json。

独立重算见 NUMERICAL_AUDIT.json：32/32 discovery、32/32 validation、8/8 replay world，各4对；概率共6912个有效 token×pair 记录。Validation 同范数 alpha=1 端点：

- E_future_plus:E_past_minus / isotropic: 18/64
- E_future_plus:E_past_minus / real: 8/8
- E_future_plus:E_past_minus / shared_rank4: 14/64
- E_future_plus:N / isotropic: 15/64
- E_future_plus:N / real: 8/8
- E_future_plus:N / shared_rank4: 15/64
- E_future_plus:P / isotropic: 17/64
- E_future_plus:P / real: 8/8
- E_future_plus:P / shared_rank4: 17/64
- E_past_minus:N / isotropic: 4/64
- E_past_minus:N / real: 8/8
- E_past_minus:N / shared_rank4: 9/64

匹配保持率随机对照按预设 validation 网格选幅度，含 alpha=0 的退化情况；它不提供同范数解释。每 world 多 pair/随机方向非独立世界；未作 test 显著性检验。
