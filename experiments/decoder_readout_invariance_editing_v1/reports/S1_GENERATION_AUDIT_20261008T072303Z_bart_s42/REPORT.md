# S1_GENERATION_AUDIT bart seed42 终态

状态：COMPLETED；Slurm 3035_0 / COMPLETED。完成world 8；剩余0；独立test访问0。GPU-hours=0.015833，本轮累计=2.317222，登记allocation峰值=2 GPU。

结果：{"passed": true, "worlds": 8, "generation_token_records": 1536, "non_initial_token_records": 1472, "non_initial_raw_argmax_disagrees": 0, "non_initial_processed_argmax_disagrees": 0, "forced_token_records": 64, "observational_head_records": 9408, "generation_encoder_calls": 0, "test_evaluations": 0, "resources": {"model": "bart", "dimension": 768, "backbone_parameters": 139420416, "parameters_per_operator": 25344, "total_editor_parameters": 50688, "gpu": "NVIDIA B300 SXM6 AC", "visible_devices": "0", "allocated_gpu_count": 1, "peak_allocated_bytes": 601184256, "wall_seconds": 27.694094845006475, "job_id": "3035", "step_id": "0", "encoder_calls": 32, "decoder_forward_calls": 2560, "SLURM_JOB_GPUS": "1", "SLURM_STEP_GPUS": "1"}}

失败原因：无

固定4 train+4 validation worlds，1536实际generation token记录：64个初始BOS由processor强制；剩余1472个token的raw和processed argmax均与实际生成一致。memory注入generation encoder调用0。9408个逐head/W_O观测单独标observational，线性求和抵消不作为完整自然电路证明。主方法增益与独立test尚未测量。

所有源代码来自manifest指向的immutable snapshot；checkpoint、split、代码SHA在RUN_STATUS/manifest。完整逐样本记录及日志压缩提交；大产物路径与SHA索引见 ARTIFACTS.json。
