# DEVIATIONS（v9，composability_mechanisms_v8）

1. **2026-11-26，数据沿用（计划第 1 节）**：模板 0 的文本空间已经用尽。
   - 模板 0 沿用 v6/v7 的 confirm 集（confirm7 = confirm6）。
   - 自然文本沿用 v8 的 confirm8。
   - 对新编辑器（B1–B5、S 的新 seed）与新模型（Qwen 或 Llama，见 DO）：**文本沿用，对该编辑器或模型为首次评测**。
   - Gemma 2 2B 只用它在 v8 中没见过的数据：weekday 模板 0 与 confirm8。
2. **2026-11-26，DO 的第二个模型（锁定前）**：
   - Qwen2.5-1.5B-Instruct 可以下载（revision 989aa798…）。在 weekday、month 模板 0 的全部 288 + 288 个 world 上，状态词都是单 token。
   - 但在自然文本 month-nat 的 960 个 world 中，有 8 个的月份在 Qwen 的分词里不是单 token。
   - 备选 Llama-3.2-1B-Instruct 是受限仓库，下载失败（GatedRepoError）。
   - 做法：保留 Qwen 作为第二个 decoder-only 家族，只对 Qwen 剔除这 8 个自然文本 world（在任何解码之前，按分词判定）。剔除清单与各 split 的数目由 `do_prep.py` 写入 `data/do_worlds_qwen.json`。
   - Gemma 2 2B 在全部数据上都通过分词检查。
