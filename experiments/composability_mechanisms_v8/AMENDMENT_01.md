# AMENDMENT_01（锁定后，2026-11-28）

- **预算（负责人批准）**：锁定前已用 21.4 GPU 小时，超过 20 小时的报告线。锁定后的运行预计还需 6–8 小时，合计约 27–29 小时，超过 26 小时上限。负责人批准跑完全部锁定后的运行：
  - BART 与 T5Gemma 的确认链，含 B6；
  - Gemma 的 DO 链；
  - 锁定的分析。
- **未用模型权重已删除（负责人要求）**：删除 v9 下载、但未通过闸门因而不使用的权重，共约 16 GB：
  - Qwen2.5-1.5B-Instruct；
  - OLMo-2-0425-1B-Instruct；
  - Phi-3.5-mini-instruct；
  - SmolLM2-1.7B-Instruct。
  它们的 revision 与逐文件 SHA256 仍在 `data/model_manifest_v9.json` 中，可按原 revision 重新下载复现闸门结果。删除前已确认其他项目不引用这些目录。
- 不涉及任何预测、判定规则或数据。
