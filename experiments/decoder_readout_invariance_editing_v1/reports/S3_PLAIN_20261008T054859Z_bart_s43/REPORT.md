# S3_PLAIN bart seed43 终态

状态：COMPLETED；Slurm 3026_1 / COMPLETED。完成world 256；剩余0；正式test评测0；全项目派生donor已有5个test core暴露。GPU-hours=0.137222，本轮累计=1.256389，登记allocation峰值=2 GPU。

结果：{"passed": true, "worlds": 256, "seed": 43, "method": "Plain", "rank": 16, "updates": 400, "validation": {"joint": 1.0, "content": 1.0, "target": 1.0, "denominator": 1536, "worlds": 64}, "checkpoint": "/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-worktree/experiments/decoder_readout_invariance_editing_v1/local/runs/S3_PLAIN_20261008T054859Z/bart_s43/Plain/update400.pt", "checkpoint_sha256": "fc93df82de21202fe00bc4299c8f72ea51a2e47f4c77bf375b3cbcba65ee816b", "human_keep_mask_not_used": true, "test_accessed": 0, "resources": {"model": "bart", "dimension": 768, "backbone_parameters": 139420416, "parameters_per_operator": 25344, "total_editor_parameters": 50688, "gpu": "NVIDIA B300 SXM6 AC", "visible_devices": "0", "allocated_gpu_count": 1, "peak_allocated_bytes": 650343936, "wall_seconds": 461.63907430700783, "job_id": "3028", "step_id": "0"}, "frozen_backbone_sha_before": "7836f07a52877d3457b69cae97a4e46feb972b6789f429014d1e616595026b5b", "frozen_backbone_sha_after": "7836f07a52877d3457b69cae97a4e46feb972b6789f429014d1e616595026b5b", "frozen_history_sha_before": "d316fc6b73fca41c4709f619af9c24b6aa424a0603bf7828b634a6e1ad152650", "frozen_history_sha_after": "d316fc6b73fca41c4709f619af9c24b6aa424a0603bf7828b634a6e1ad152650"}

失败原因：无

完整逐样本重算：{"recomputed": {"denominator": 1536, "worlds": 64, "joint": 1.0, "content": 1.0, "target": 1.0}, "numerators": {"joint": 1536, "target": 1536, "content": 1536}, "sources": {"natural": {"denominator": 768, "joint_numerator": 768}, "history": {"denominator": 768, "joint_numerator": 768}}, "independent_worlds": 64, "scientific_status": "VALIDATION_ONLY", "frozen_backbone_unchanged": true, "history_unchanged": true}

局部机制证据与反证见S2报告。机制相对Output-only/Random-site的收益、独立test和长期能力尚未测量；本run的单操作validation数字为1536/1536，未使用keep mask。正式test主终点因5个派生donor核心暴露而阻塞。

所有源代码来自manifest指向的immutable snapshot；checkpoint、split、代码SHA在RUN_STATUS/manifest。完整逐样本记录及日志压缩提交；大产物路径与SHA索引见 ARTIFACTS.json。
