# 实际资源与证据审计

远端 HEAD 与 1321 个历史文件的 SHA256 在 manifests/historical_file_audit.json。原工作区和所有已有 worktree 未修改。历史 BART 四维逐有效 token PCA 是大幅 donor-assisted 修补；旧80 worlds 为 replay/discovery。N=R 不重复计来源。P 为历史配置代号。旧 T5Gemma next-fork 排除规则不用于新 SAME_TEXT 面板。Handoff 远端仍只声明 R00 CPU prepared；当前实时作业由 squeue/sacct 单独审计。

跨分支保守排除456个时间 core，1080种原词汇组合中剩624个；新池512在任何模型运行前锁定。模板0-5均已有曝光，模板 OOD 为 UNAVAILABLE，剩余128标 reserved_iid，不作为 OOD。核心忽略不出现在核心文本中的日期和人名。实际输入文件全部 SHA 核验；源码复制进不可变 snapshot，不热加载旧 worktree。

当前环境 torch/transformers 见 INPUTS.json；未升级。B300q 核验 MaxTime=UNLIMITED，AllowAccounts/AllowQos=ALL；单 task gres=gpu:1，64GB host memory，8CPU，1小时 shard（<=3小时规则）。当前 squeue 无本人作业；以后每次提交再查询。外部锁/注册表在 /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-control-v1。峰值/消耗由 allocation级 sacct 计，失败计费，worker不得修改Git。
