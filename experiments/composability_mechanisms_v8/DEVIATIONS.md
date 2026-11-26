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
3. **2026-11-26，区分力预检的操作化（锁定前，负责人决定）**：
   - 计划第 1 节写"dev 上已经落在阈值一侧的，降为描述性"。若字面执行（在 dev 上解码全部链），几乎所有 B、S 预测都会降级。
   - 负责人选择按 v8 的做法：锁定前在 dev 上只做潜空间模拟，不解码 dev 链；某个条件被潜空间模型自己预测落在阈值另一侧时，剔除该条件（降为探索性）。
   - 由构造决定的预测，在模拟上已 ≥ 0.95 时降为描述性。这里指 B5：精确旋转使潜空间读出按构造正确。
   - 操作细节：
     - 预检用只看槽位的读出：一条链被预测为成功，当且仅当每一步的读出都等于金标准。
     - CE 编辑器的 R_1 不做预检：潜空间模型不建模指令式写入，CE 第 1 步的读出就是起点。
     - D 需要解码，不做预检。
     - 其余带阈值的量都做预检：B1 的 R_1 与 R_2N，B2–B4 与 S 的 R_2 / R_2N / 视野外的 R，DO1、DO2、DO5。
4. **2026-11-26，DO 的运行环境与闸门（锁定前）**：
   - Qwen 的 `do_prep`（作业 73712）在 SDPA 注意力中报 cuDNN "No valid execution plans built"（与 v8 DEVIATIONS 6 相同）。
     - 做法：只对 Qwen 关闭 cuDNN 的 SDPA 后端，由其余 SDPA 后端计算同一注意力。
     - 重跑；Qwen 此前没有任何编码或解码。
   - Gemma 2 2B 在自然文本 month-nat 上的重建率为 0.983，低于闸门 0.99，按附录 B.2 第 7 步，该组合（Gemma，自然文本）不评测。Gemma 只剩 weekday 模板 0 一个组合。
