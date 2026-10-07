# S0 bart seed42 终态

状态：COMPLETED；Slurm 3009_0 / COMPLETED。完成验收world 8/8；独立test访问0。GPU-hours=0.025000，本轮累计=0.098056，登记allocation峰值=2 GPU。

8-world smoke联合成功：8/8；CE 0.5906764268875122 → 0.00010416990335215814，更新120。这些为训练验收数据，不是方法独立效果。关键验收结果在 S0_ACCEPTANCE.json，失败详细记录在 FAILURE.txt / 原始压缩日志。

当前机制、机制相对Output-only/Random-site编辑收益、原子与长期能力、新T5Gemma资格均为NA，尚未执行。技术验收失败必须阻断该模型后续分析，不能删除world通过。下一步依赖该模型完整S0验收与锁定。

所有源代码来自manifest指向的immutable snapshot；checkpoint、split、代码SHA在RUN_STATUS/manifest。完整逐样本记录及日志压缩提交；大产物路径与SHA索引见 ARTIFACTS.json。
