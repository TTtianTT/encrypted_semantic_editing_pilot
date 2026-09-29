# G8：Decoder Basin Anisotropy

## 固定模型、世界和可比较的“失败”定义

冻结 G7 的 BART G3 `T+` 与 T5Gemma rank-16 `T+`，不训练基座、editor 或新模块。测试仍使用 G5/G7 锁定的 53 个 IID + 53 个模板 OOD 世界及 `offset +1` 起点；另取原 `recorded_plan` train 前 24、dev 前 12 个世界作预先固定的计算检查。每个世界按 G7 的 8-world batch 重建 pure latent `h_k`，仅在 G7 当前文本语义、事实和格式都正确且 `k≤4` 时扫描。BART 使用 Slurm 单卡作业 1799；T5Gemma 由单卡作业 1798 的 train/dev/IID 与 1800 的 OOD 分片合并，同一时刻最多两卡。

在每个 `h_k`，以真实下一次编辑位移 `v_edit=T+(h_k)−h_k` 的 masked token×hidden L2 范数为单位，构造五种等范数方向：真实正向、其反向、与当前 latent 径向向量正交的固定随机向量、指向同一步 gold `E(y_k)` 的向量，以及与真实编辑位移正交的固定随机向量。gold 方向在两表示共有的有效 token 位置上定义；输入 token 数不等时不声称严格对齐。T5Gemma 的候选方向在五路 BF16 decoder batch 内按预定哈希轮换槽位，以避免方向和 batch 位置固定绑定；每次扰动的实际量化后范数另行记录。

对每方向扫描 `α∈{.25,.5,.75,1,1.5,2}`，在**语义 corridor** 第一个失败的相邻网格区间做两轮中点细化；辅助的 content/structure 半径只用预定的粗网格。逐点保存 decoded text、当前/下一步 gold 的 teacher-forced NLL、输出 token 熵和 top-1 margin、正常结束、语义/事实评分。由于正向编辑**本来就应把时间从当前步移到下一步**，把“离开当前文本”直接叫作 decoder 失败会产生平凡结论。主语义指标采用**当前或下一步 gold 状态均可**的 corridor：若两者都不满足评分器，才记语义范围失败。另用可解析、非日期事实不变且正常结束的 *content/structure* 指标，把时间走错与句式/事实破坏分开；这是现有模板评分器兼容性指标，并非开放式语义判读。两个指标的首次失败半径均在 `α≤2` 截断；超出者按 2 处理并保留删失标记。非单调的失败后恢复单独计数，因此半径只代表本次有限网格中的首次观测失败，并非连续空间精确边界。

所有方向在**同一个状态**内配对。按 world 聚类 bootstrap 3000 次比较正向半径与每个对照方向的平均差，并报告配对符号检验。下一步是否失败沿用 G7 原标签，同时保留候选 batch 在 `α=1` 的本地复算标签；两者不一致时不隐藏 BF16/batch 数值敏感性。早期预警额外看 `α=.5` 的状态与分数，避免只用 `α=1` 的结果重复定义下一步失败。

## 结果

### BART：真实方向对句式/事实尤其脆弱

锁定测试中有 242 个当前仍正确的状态。下表半径均截断于 `α=2`，`≤1` 表示扫描到下一次完整编辑幅度以内首次失败；此处的 *content/structure* 只要求可解析、非日期事实保持和正常结束，时间状态另由 semantic corridor 约束。

| BART 方向 | semantic corridor 平均半径 | content/structure 平均半径 | `α≤1` content 失败数 |
|---|---:|---:|---:|
| 正向 editor | **1.210** | **1.348** | **88/242** |
| 反向 editor | .528 | 1.969 | 1/242 |
| 与 latent 径向正交的随机方向 | 1.752 | 1.869 | 14/242 |
| 指向 gold `E(y_k)` | 1.409 | 1.994 | 0/242 |
| 与 editor residual 正交的随机方向 | 1.740 | 1.889 | 13/242 |

在同一个世界和状态内配对，正向 editor 的 content/structure 半径比两种随机对照分别低 **.521**（按 world bootstrap 95% CI `[-.566,-.474]`）和 **.541**（`[-.590,-.494]`）；与 gold 方向相比低 **.646**（`[-.689,-.602]`）。这支持 BART 的真实编辑残差沿一个相对脆弱的 decoder 方向运动，不只是“与 gold 有多远”。反向方向在 semantic corridor 上更早失败，却几乎一直保留句式/事实：它主要把时间推向 corridor 以外，不能据此说 decoder 已坏。

BART 第 2 步当前正确的 94 个测试状态中，52 个下一步失败。只走**半步** `α=.5`，正向编辑已使其中 **20/52** 个走出 corridor 且损坏 content/structure，而随后稳定的 42 个中 **0/42** 如此。半步失败二值指标 AUROC `.692`；半步输出熵 AUROC `.815`。完整半径对下一步失败的 AUROC `.943`，但它包含 `α=1` 及更大扰动，部分反映了下一次编辑本身，不应当作无成本的提前预警。

在 `α=1` 的 106 个 BART 下一步失败中，**88** 个已不可解析或无法证实事实保持；另 **18** 个仍输出当前 gold 时间状态，属于算子没有推进时间的 saturation，而不是 decoder 句式崩溃。方向半径能识别前一类，对后一类必须保留原有下一步目标评分。

### T5Gemma 与跨基座比较

锁定测试中 T5Gemma 有 199 个当前正确状态。与 BART 一样，在**每个相同 `h`** 上比较五个等范数方向；因此同一行内 gold distance 完全相同，方向间差异不能只归于当前 latent 离 gold 的标量距离。

| T5Gemma 方向 | semantic corridor 平均半径 | content/structure 平均半径 | `α≤1` content 失败数 |
|---|---:|---:|---:|
| 正向 editor | **.718** | **.894** | **104/199** |
| 反向 editor | .612 | 1.608 | 42/199 |
| 与 latent 径向正交的随机方向 | 1.589 | 1.673 | 43/199 |
| 指向 gold `E(y_k)` | .777 | 1.709 | 10/199 |
| 与 editor residual 正交的随机方向 | 1.609 | 1.711 | 35/199 |

正向 editor 的 content/structure 半径比两种随机对照分别低 **.779**（按 world bootstrap 95% CI `[-.848,-.709]`）和 **.817**（`[-.881,-.748]`），比 gold 方向低 **.814**（`[-.837,-.787]`）；配对符号检验分别为 `p<2×10⁻⁵⁵`、`p<9×10⁻⁵⁶`、`p<7×10⁻²²`。BART 和 T5Gemma 在 IID 与 OOD 上均出现相同方向排序。语义 corridor 对比随机方向也明显：T5Gemma 正向与两种随机方向的平均差是 `−.871`、`−.891`；但反向与 gold 方向可能把时间推到当前/下一状态以外，它们的 corridor 半径不能独立解释为 decoder 损坏。

在 `α=.5`，T5Gemma 正向编辑的 corridor/content 保持率均为 **53.3%**，两种随机方向的 content 保持率为 **86.4%/88.9%**；BART 对应为 **77.3%** 对 **97.5%/98.3%**。两套模型在完整编辑幅度 `α=1` 的方向曲线及其 NLL、熵、margin 见 [BART 曲线](curve_bart.svg)、[T5Gemma 曲线](curve_t5gemma.svg)和[逐 α 数据](direction_curves.csv)。例如 BART 在半步的平均输出熵，正向为 `.0782`，两种随机为 `.0233/.0227`；相应最佳 gold NLL 中位数为 `.0102` 对 `.0042/.0046`。T5Gemma 的半步熵为 `.0668` 对 `.0219/.0181`，最佳 gold NLL 中位数为 `.000926` 对约 `.000009`。这些条件指标指向编辑方向的 decoder 敏感性，但 NLL 和 greedy 解码失败并不一一对应。

T5Gemma 有显著的**非单调盆地**：199 个测试状态中，正向方向的 corridor 有 **72** 个、content/structure 有 **114** 个在粗网格上“先失败，后恢复”；BART 正向对应均为 0。T5Gemma 的 `α=.5` corridor 成功率 53.3%，到 `α=1` 却回升到 62.3%，因此不能把 T5Gemma 的首次失败半径当作连续、单调的安全余量。`α=1` 在五方向 BF16 batch 中与 G7 原 8-world batch 的输出有数值敏感性：全部 268 个状态中 **252** 个文本一致、**263** 个下一步语义判定一致；测试 199 个中分别为 **188** 和 **196**。本报告的方向半径使用同一五方向 batch 的本地输出，下一步失败标签沿用 G7 原输出，并在数据中保留两套标签。

### 当前正确、下一步失败：预警的边界

BART 测试第 2 步的半步熵 AUROC `.815`，半步 corridor/content 失败 AUROC `.692`（52 失败、42 稳定）；第 1 步没有半步失败，不能提前区分其 12 个下一步失败。T5Gemma 第 1 步 106 个当前正确状态中 13 个下一步失败，但半步失败数为 0，故半步二值 AUROC 仅 `.500`；第 2 步 93 个当前正确状态全部在下一步失败，无法计算 AUROC。完整 content 半径在 T5Gemma 第 1 步的 AUROC `.879`，BART 第 2 步 `.949`，但它包含 `α≥1` 的解码试探，属于干预实验，不能声称是无需额外解码的运行时预测器。**方向性脆弱在两基座一致；固定半步预警指标没有跨基座一致性。**

### 可核对的 pre-failure 轨迹

* BART OOD `v3_confirmation_test_template_ood_0015` 第 2 步当前文本正确：“…send three tickets to Grace…event dated yesterday”。下一目标为 “two days ago”。正向半径 `.0625`，与 editor 正交随机方向的半径为 `2`（删失）；`α=.25` 出现重复的 “This track …” 及错误时间，`α=1` 仍输出 “yesterday”，下一步失败。只看当前 decoded text 会遗漏此脆弱性。
* T5Gemma IID `v3_confirmation_test_iid_0035` 第 2 步当前文本正确：“…give four tickets to David…yesterday”。下一目标为 “two days ago”。正向半径 `.0625`，`α=.25` 与 `.5` 开始附加 `\endverbatim`，`α=1` 变为缺失事实的 “With the event dated three days ago …”；随机正交方向的半径见[原始案例](pre_failure_cases.json)。
* T5Gemma IID `v3_confirmation_test_iid_0038` 展示非单调性：当前 “Henry … not give six tickets to Emma … yesterday” 正确；正向 `α=.25/.5` 附加 `\endverbatim` 因而评分失败，`α=1` 又回到可解析的原时间句子，尽管没有成功推进到 “two days ago”。这解释了为什么首次失败半径与完整下一步结果不能混为一谈。

## 结论与限制

**同一状态、相同扰动范数下，实际 editor 方向显著比随机方向更脆弱，BART 与 T5Gemma 均成立。** 当前 gold distance 是同一状态的常数，因此单一“离 gold 太远”解释不足以解释局部方向差异；但已有 representation drift 仍可能决定基线位置，不能据此断言距离完全无关。BART 的 pre-failure 半步熵上升和 T5Gemma 的强非单调性表明 decoder-compatible 区域具有方向性，而且 T5Gemma 还具有复杂边界及 BF16/batch 敏感性。由于只取每状态一个固定随机样本、只扫 `α≤2`、使用贪心解码与模板解析器，统计证明的是**本实验定义的条件方向对比**，不是对完整 latent 空间或连续边界的估计。未训练任何新模块，也未据此调 editor。

审计复算了 **606** 个状态、**22,544** 个候选方向点的评分与扰动范数，检查 3,030 行半径、48 组配对统计、世界划分互斥、T5Gemma 分片合并哈希和两套 G7 标签；结果为 `ok=true`。两个冻结 editor SHA256 分别为 `dca3cb26c0d3c1e33e3215f86e911d4c19df7417160598dcfdba8fbcffd8654d` 和 `66cd1f5c454514c9129c4a8bac54b028fe09063656b451c23242cc427a8db506`，完整依赖版本与文件哈希记录在[结果清单](run_complete.json)。

## 文件与复现

[config.json](config.json) 固定世界、方向、随机种子、α 网格和 bootstrap；[原始逐候选文本和分数](scan_bart.jsonl)、[T5Gemma 原始扫描](scan_t5gemma.jsonl)与对应 `states_*.jsonl` 允许逐条重算。[方向半径](directional_radii.csv)、[半径摘要](radius_summary.csv)、[α 曲线数据](direction_curves.csv)、[配对 bootstrap](paired_bootstrap.csv)、[早期预警](early_warning.csv)、[典型案例](pre_failure_cases.json)、[审计](audit.json)和[结果哈希](run_complete.json)构成正式输出。仅上传代码、报告和这些必要结果；冻结的基座与 editor checkpoint 仍由 G3/G7/T5Gemma provenance 引用。
