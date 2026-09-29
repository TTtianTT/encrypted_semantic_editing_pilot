# 发布范围

本实验从 `bc5087483b5c3d2476d615d8e9452b0f54bd289c` 建立独立分支 `experiment/joint-reference-editor-v1`，只新增本目录，不覆盖 main 或旧实验。

按本会话已有 GitHub 上传授权，同步协议、代码、合成世界、完整输出、统计、预选案例以及小编辑器初始化/各检查点/最优权重。基础模型仍保留在 `/dataset1/zailong/models/reference-frame-cross-backbone/`，不重复上传。环境、缓存、访问凭证和用于本地恢复的 `latest.pt`（optimizer/RNG）不发布。

`artifact_manifest.json` 列出最终发布内容的 SHA-256 和字节数（不包含该清单自身）。人工审查标签保持空白；独立方法映射供组织盲审的人保管，公开映射后的审查者需自行避免读取它。
