# R00 CPU audit

1080种既有核心组合中，跨远端21个branch及本地既有数据保守排除456，剩624。用固定seed2026100801选512，分train192/validation64/test_iid128/reserved_iid128；全部核心互斥且与registry无交集。已暴露的旧80 PCA test仅作replay，不进入新确认。

9/9 CPU检查通过：world泄漏、有效生成token（BART decoder-start EOS排除、生成EOS包含）、零分母NA、padding范数、联合成功、Wilson边界、allocation GPU计数、原子幂等、未授权登录节点worker拒绝。无模型导入/计算；GPU-hours0、并发0、遗留job0。

没有真实未暴露模板：OOD UNAVAILABLE，reserved128不能改名OOD。下一步S0两模型注入/梯度/8-world overfit。科学结论尚不存在，机制及编辑收益NA。原工作区branch/已跟踪diff保存在INPUTS.json。
