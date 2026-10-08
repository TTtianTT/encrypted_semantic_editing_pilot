# Native implementation acceptance

BART FP32、原版T5Gemma BF16均通过各8world native验收：注入路径与原路径token/logits一致，no-op/self/alpha0及padding-only测试、全部cross K/V donor replacement、cache/no-cache一致性；梯度有限非零，新editor可训练，冻结backbone SHA未变。实际hook map见HOOK_MAP.json，精确逐项结果见S0_ACCEPTANCE.json及两个S0终态报告。

各120-update8world过拟合联合成功8/8：BART CE0.5906764269→0.0001041699；T5Gemma CE1.328215301→0.0000104833。不是独立任务能力评测。BART最小eps0.001方向导数相对误差0.0455662；T5Gemma eps0.015625误差0.0290866。更大有限幅度误差保留，不把局部检查解释为全局线性性。

可选SDPA→eager logits对齐随后失败（最大5.91278e-5，预设阈值3e-5）；未放宽阈值或使用该路径。原生SDPA投影hook无干预误差0，另建新快照验收后用于机制诊断。首次手算AV重构也失败，原生日志保留；后续实际mask原生SDPA重放局部误差严格0。所有三次失败均已计费并独立发布。

CPU最终检查16项（包括后增的泄漏门禁、桥接口径和NA规则）；初始S0时仅12项。最终实际测试回执见results/CPU_ACCEPTANCE_FINAL.json。
