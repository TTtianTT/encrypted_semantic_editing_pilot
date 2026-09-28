# v2 发布范围

沿用本会话已授权的独立Git发布方式，只发布v2目录，不修改v1或顺带推送其他本地实验提交。

发布代码、协议、冻结数据/配置/哈希、共享初始化和三组best.pt、A诊断、逐样本输出、统计、报告和审查资料。遵循仓库既有.gitignore：latest.pt优化器恢复状态与Python缓存仅本地；不发布BART底座、环境或访问凭证。

artifact_manifest.json是完成时本地归档清单（包括未发布的latest.pt）。PUBLICATION_MANIFEST.json是发布文件清单，自身不列入以避免循环hash。best.pt足以复现推理；异机重新训练须新目录、相同数据/seed及另行核算预算。原服务器latest.pt可恢复optimizer/RNG，但不属于下载包。

private_mapping.json是匿名方法/路径技术映射，不含凭据。真人盲审只分发blind_review.csv，不能同时分发映射。现无真人标签，结果仍标为结构化自动检查+模型复核。
