# PARITY_DIAG bart seed42 终态

状态：BLOCKED_BACKEND_PARITY；Slurm 3012_0 / FAILED。完成world 1；剩余0；独立test访问0。GPU-hours=0.009167，本轮累计=0.118611，登记allocation峰值=2 GPU。

结果：{"passed": false, "status": "BLOCKED_BACKEND_PARITY", "worlds": 1, "world_id": "drie_013a626fe072d215", "split": "train", "reference_backend": "sdpa", "candidate_backend": "eager", "dtype": "torch.float32", "repeat_noise_max": 0.0, "logit_max_error": 5.91278076171875e-05, "logit_mean_error": 3.710003056767164e-06, "logit_quantiles": {"0.5": 2.86102294921875e-06, "0.9": 7.867813110351562e-06, "0.95": 1.0013580322265625e-05, "0.99": 1.5497207641601562e-05}, "tolerance": 3e-05, "unchanged_tolerance": true, "greedy_tokens_equal": true, "reference_ids": [2, 0, 133, 9626, 515, 16, 7000, 452, 4, 3139, 2194, 16, 8102, 4, 20, 9626, 16, 2272, 4, 345, 32, 231, 11288, 4, 2], "candidate_ids": [2, 0, 133, 9626, 515, 16, 7000, 452, 4, 3139, 2194, 16, 8102, 4, 20, 9626, 16, 2272, 4, 345, 32, 231, 11288, 4, 2], "worst_position": 19, "worst_vocab_id": 32, "reference_value": 28.497440338134766, "candidate_value": 28.49738121032715, "after_failed_S1": true, "downstream_analysis": false, "test_accessed": 0, "resources": {"model": "bart", "dimension": 768, "backbone_parameters": 139420416, "parameters_per_operator": 25344, "total_editor_parameters": 50688, "gpu": "NVIDIA B300 SXM6 AC", "visible_devices": "0", "allocated_gpu_count": 1, "peak_allocated_bytes": 627168768, "wall_seconds": 7.0681018629984464, "job_id": "3012", "step_id": "0"}}

失败原因：无

当前机制、机制相对Output-only/Random-site编辑收益、原子与长期能力、新T5Gemma独立资格均为NA，尚未执行。技术验收失败阻断该模型后续分析，不删除world通过。关键失败详细记录在 FAILURE.txt / 原始压缩日志。

所有源代码来自manifest指向的immutable snapshot；checkpoint、split、代码SHA在RUN_STATUS/manifest。完整逐样本记录及日志压缩提交；大产物路径与SHA索引见 ARTIFACTS.json。
