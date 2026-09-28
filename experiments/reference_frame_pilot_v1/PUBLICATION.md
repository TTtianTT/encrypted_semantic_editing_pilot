# GitHub 发布范围

本次发布包含实验代码、冻结数据与配置、六组best.pt编辑器权重、逐样本输出、统计、报告和审查材料。遵循仓库既有.gitignore，latest.pt优化器恢复状态及Python缓存仅保留原服务器；不上传BART底座或环境。

artifact_manifest.json是实验完成时的本地归档快照，因此包含未发布的latest.pt。PUBLICATION_MANIFEST.json只列本次发布文件（自身除外），供下载后核验。

review/private_method_map.json是方法匿名编号映射，不含凭据；与盲审表分文件保存。组织盲审时只分发blind_review.csv，不向审查者提供映射。没有真人审核，报告中的结果仍为结构化自动检查与模型复核。

在原服务器恢复训练可使用本地latest.pt。异机可使用best.pt复现推理；如需重现训练，应在新目录从固定seed与数据开始，另行核算资源，不能把发布包说成包含完整optimizer恢复状态。
