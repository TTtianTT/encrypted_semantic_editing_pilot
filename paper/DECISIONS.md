# 负责人决定记录（A 线）

| 日期 | 事项 | 决定 |
| --- | --- | --- |
| 2026-11-24 | A2 动机（引言主线） | 采用更宽的版本：以"中间状态不被解码的管线"作动机；加密只作为其中一个例子，不作主线；标题中不出现 encrypted。 |

## 阶段 2 指令（2026-11-25），第 1 节"决定"（原文照录）

1. **阶段 2 开始**。顺序为：v7 并入论文 → 第一轮对抗审稿 → v8 锁定前的 GPU 工作。
2. **引言**：
   - 用 `01_intro_draft.tex` 替换 `paper/sections/01_intro.tex`。
   - CL15 不进引言。绑定只在"范围"段出现一句，由 K5 支撑。
   - 措辞不要改，只修宏名与引文键。发现问题写进 `REVIEW_LOG.md`，由负责人决定。
3. **标题（工作版本）**：*Decodable Is Not Composable: What Latent Edits Must Write and Preserve*。
   - v8 之后定稿：自然文本与规模都成立，就保持这个标题；否则在后面加 "in Encoder–Decoder Models"。
4. **v8 的模板 0 数据**：
   - G 单元与规模阶梯沿用 v6/v7 的 confirm 集（confirm6 = confirm7），train/dev 沿用原划分；不扩充词表。
   - DEVIATIONS 写明"文本沿用，对该模型为首次评测"。
5. **v8 新增两个探索性单元 E1、E2**（定义见第 5 节）。v8 锁定前，把它们写进 v8 的 PLAN，并在 DEVIATIONS 中记为计划变更。
