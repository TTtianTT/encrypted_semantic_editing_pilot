# G7：Repeated Intervention Stability Diagnosis

**结论。** 两个冻结 editor 在 pure latent 链上都累积了明显的表示偏移，但“偏移量大”本身不能可靠地区分**同一步仍输出正确文本**的状态下一步会否失败。BART 第 2 步的 94 个正确状态中，pooled normalized L2 的下一步失败 AUROC 仅 **0.470**，gold 文本 NLL 和自由输出熵分别为 **0.780**、**0.807**；用训练世界拟合、开发世界定阈值的 decoder-likelihood logistic 在独立测试上报出 31/52 个下一步失败，误报 4/42。T5Gemma 第 1 步同样是 pooled L2 **0.516**、NLL **0.767**，但其风险方向是**更低**的 NLL；开发集定出的全步数阈值在这 13 个早期失败上检出 **0/13**。T5Gemma 第 2 步正确的 93 个测试状态随后全部失败，无法计算该步的区分性 AUROC。因此 decoder 条件分数在可比较的步数上比 pooled 几何更有排序信息，**尚无跨基座可靠的单调 stability score 或预警阈值**。

## 固定协议与预测目标

直接冻结 G3 `facebook/bart-base` rank-16 `T+` checkpoint 和 T5Gemma 2B-2B UL2-IT rank-16 `T+` checkpoint；没有更新 editor、主模型或训练新表示。两者沿用 G5/T5Gemma 复现的同一 `offset +1` 起点、53 个 IID 与 53 个模板 OOD 测试世界，以及原有评分器。独立预测训练集为 160 个 `recorded_plan` train worlds，开发集 27 个；五步 pure latent 链对每个世界分别重跑，仅新增特征。锁定测试的 BART 与 T5Gemma 各 **530/530 条**输出逐字吻合原 G5/T5Gemma 轨迹，成功标签也各 530/530 一致。[提取审计](audit.json)、[BART agreement](agreement_bart.json)、[T5Gemma agreement](agreement_t5gemma.json)。

预测单位是第 `k=1…4` 步**当前语义、事实和格式均正确**的 latent，标签是第 `k+1` 步是否失败。BART 测试有 242 个这类状态（下一步失败 106 个），T5Gemma 有 199 个（下一步失败 106 个）。对每个状态记录 `E(gold)` 的 masked-mean pooled cosine/L2、共享有效 token 位置的距离、token pairwise cosine Gram RMS、token 方差迹比例、目标文本 teacher-forced NLL、自由 greedy 输出的熵/前二 logit margin、编辑 residual norm/方向、沿 residual 的 JVP 增益，以及当前/下一步文本。BART 用原无提示、FP32 接口；T5Gemma 沿用之前固定的 chat 复制指令与 BF16 接口。输出 margin 排除了被强制 EOS 造成的单候选位置。逐例原始数据见 [BART](features_bart.jsonl) 与 [T5Gemma](features_t5gemma.jsonl)。

单指标的风险方向**只在 train** 上按 AUROC 确定；logistic 使用固定 `C=1`、训练集 median 缺失值填补、标准化和 class weight；阈值**只在 dev** 上按 balanced accuracy 选择，没有用 test 选指标或阈值。比较 `step_only`、pooled/token 几何、decoder 分数、编辑动力学与全部特征。表中 AUROC 是独立 test；95% 区间按 world 聚类 bootstrap 2000 次。完整 [预测对照及阈值](predictor_comparison.csv)、[同一步分层](within_step_auroc.csv) 和[逐例测试分数](test_predictions.csv)允许重算。

## 当前成功时，哪项特征能预测下一步？

全步数汇总会受到确定的失败时间影响。下表在**相同当前步**计算 AUROC，风险方向仍来自 train；`—` 表示该组标签只有一类。T5Gemma OOD 第 1 步仅 1 个下一步失败，单层数值尤其不稳。

| 特征或模型 | BART 第 2 步，52/94 失败 | T5Gemma 第 1 步，13/106 失败 | T5Gemma 第 2 步，93/93 失败 |
|---|---:|---:|---:|
| pooled L2 | 0.470 | 0.516 | — |
| token-aligned L2 | 0.493 | 0.447 | — |
| gold target NLL | 0.780 | 0.767（**低 NLL 更危险**） | — |
| greedy 输出熵 | 0.807 | 0.435 | — |
| greedy top-1 margin | 0.720 | 0.514 | — |
| residual norm | 0.514 | 0.501 | — |
| decoder-likelihood logistic | **0.803** | **0.792** | — |
| pooled-geometry logistic | 0.497 | 0.501 | — |

BART 第 2 步按模板分开，pooled L2 的 AUROC 为 IID **0.527**、OOD **0.299**；NLL 为 **0.618/0.799**，输出熵为 **0.636/0.840**。这说明 pooled 距离的大部分汇总预测力来自步数和模板差异，不是同一步的可靠失稳指标。BART 的 NLL/熵在 OOD 尤其有用，但 IID 效果较弱。T5Gemma 第 1 步的 NLL AUROC 为 IID **0.713**、OOD **0.885**；OOD 只有一个阳性，不能据此推断稳健的 OOD 性能。T5Gemma 的 NLL 风险符号与 BART 相反：train/dev 都学到低 NLL 更危险；第 2 步仍正确的 test 样本 median NLL 从第 1 步约 `9.95×10⁻⁶` 降至 `9.7×10⁻⁷`，而其第三步全失败。**低 teacher-forced NLL 并不保证下一次自由生成可解码。**

开发世界确定的**同一个阈值**在 matched-step 测试的结果：

| 当前状态 / 模型 | 下一步失败检出 | 稳定状态误报 | balanced accuracy |
|---|---:|---:|---:|
| BART 第 2 步：pooled geometry logistic | 7/52 | 5/42 | 0.508 |
| BART 第 2 步：decoder-likelihood logistic | **31/52** | **4/42** | **0.750** |
| BART 第 2 步：decoder scores logistic | 37/52 | 16/42 | 0.665 |
| T5Gemma 第 1 步：pooled geometry logistic | 0/13 | 0/93 | 0.500 |
| T5Gemma 第 1 步：decoder-likelihood logistic | **0/13** | 0/93 | 0.500 |

T5Gemma 的 NLL 虽有第 1 步 AUROC 0.767，固定全步数阈值**没有提前检出**任何这 13 个失败。报告排序能力时必须同时报告此阈值失败。第 2 步的所有 93 个仍正确状态下一步都失败，任何只靠步数的规则都可预警，不能证明某个 latent property 有额外作用。

跨步数的总体 AUROC 更高，但不能独立支持某特征：[完整表](predictor_comparison.csv)中 BART `step_only`/pooled geometry/decoder likelihood 为 **0.850/0.884/0.894**，T5Gemma 为 **0.939/0.939/0.871**。T5Gemma pooled 与 step-only 几乎完全相同；“所有特征”模型在 OOD 反而较差，BART 0.736、T5Gemma 0.790，因此没有事后挑选复杂组合。开发集阈值和测试 bootstrap 区间均在 CSV，不能把同一世界的多个步骤当成独立样本。

## 轨迹、几何与局部动力学

以下是两个测试层合并的**每步所有 pure 状态平均值**，含已失败状态；用于描述轨迹，不用于预测 AUROC。[逐步曲线数据](stability_curves.csv)、[BART stability 曲线](stability_curve_bart.svg)、[T5Gemma stability 曲线](stability_curve_t5gemma.svg)。每行顺序为第 1→5 步。

| 基座 | pooled L2 | token L2 | token Gram RMS | residual norm | residual JVP gain |
|---|---|---|---|---|---|
| BART | .466→.877→1.221→1.511→1.771 | .361→.520→.936→1.056→1.175 | .034→.100→.188→.242→.286 | 2.03→1.46→1.21→1.12→1.08 | .72→.82→.92→.97→1.03 |
| T5Gemma | .517→1.187→2.050→3.150→4.531 | .338→.663→1.251→1.728→2.349 | .044→.145→.279→.389→.486 | 31.4→38.2→47.5→58.9→72.8 | 1.22→1.24→1.24→1.24→1.23 |

两个基座都远离 gold encoder 表示，pairwise token geometry 也持续改变；token 方差迹的 log ratio 从 BART `.078→.232`、T5Gemma `.055→1.338`。相邻编辑 residual 的平均方向 cosine 在 BART 约 `.977→.963`，T5Gemma `.989→.999`；方向持续相近，但 BART 更新变小、T5Gemma 更新变大。低秩 editor 对每个有效 token 是仿射映射，连续空间 Jacobian `I+UV` **不随状态改变**；80 次 power iteration 得到 BART spectral norm **3.268**、T5Gemma **2.423**。所以这个**全局**谱范数无法在同一基座内预测哪个世界下一步失败；沿实际 residual 的 JVP gain 才随步数变化。T5Gemma 的 BF16 实际执行含量化，上述谱分析对应其连续仿射近似。

几何漂移能描述已走多远，却不能自动代表 decoder 可解码边界。BART 第 2 步失败/下一步稳定两组的 pooled L2 均值为 `.875/.877`，几乎重合；gold NLL 为 `.00425/.00215`，输出熵为 `.0143/.00882`。T5Gemma 第 1 步 pooled L2 均值为 `.5170/.5166`。NLL 属于**需要 oracle gold 目标**的诊断特征；输出熵/margin 需要先解码当前状态，成本与早期风险判别不同。它们不能直接充当免费的在线控制器。

## 正确文本后的失败案例

[四条完整五步轨迹](pre_failure_trajectories.json)记录每步文本、gold、正确性、NLL、熵、margin、几何和 residual；[按 NLL 选的额外案例](pre_failure_examples.json)供检查个体差异。

* BART OOD `…0015`：第 2 步文本与 gold **逐字相同**，但 NLL `.01668`，是同一步下一步稳定样本中位数 `.00201` 的 **8.28 倍**；第 3 步把 `for an event dated two days ago` 破坏为 `describes yesterday`。其 pooled L2 `.888`，并未形成可靠的同一步几何告警。
* BART IID `…0000`：前三步仍正确，第 4 步开始生成重复日期碎片。第 3 步已是剩余正确状态全部会失败的阶段，因此任何第 3 步分数无法再做有意义的二类 AUROC。
* T5Gemma IID `…0000`：第 2 步文本仍与 gold 相同（去除生成末尾空白）；pooled L2 从 `.528` 升至 `1.215`，输出熵 `.00253→.02025`，但目标 NLL **下降** `6.97×10⁻⁶→1.04×10⁻⁶`、平均 top-1 margin **上升** `17.34→22.45`；第 3 步时间停在 `yesterday` 而非 `two days ago`。OOD `…0000` 也在第 2 步完全正确后第 3 步失败。这些案例展示了**过度自信的 teacher-forced/平均 margin 分数仍可伴随下一次算子失败**。

## 回答与边界

目前最有证据的回答是：**同一步 BART 的 decoder 条件分数比 pooled 距离更接近下一步稳定性，但不是通用定律。** T5Gemma 的 NLL 有一定排序能力却符号反转、阈值早期检出为零；输出熵和 margin 在 T5Gemma 第 1 步接近随机。两个基座在后续步数发生几乎确定的整体崩溃，造成严重的步数混杂和标签单类问题。局部 Jacobian 全局谱范数在固定仿射 editor 下是常数，不能作为样本级预警器；JVP、residual、token Gram 等虽跟随轨迹变化，同一步的泛化表现仍不稳定。G7 因而**没有找到一个跨 BART/T5Gemma、可单调阈值化的 latent stability property**。这不否定 G5 的 decode→re-encode reset 现象；它说明本次有限的几何/decoder 统计不足以识别统一的“安全继续编辑”边界。

本研究只覆盖一个 editor seed、两个不同大小/精度/提示接口的基座和合成短句；T5Gemma 的测试 OOD 第 1 步只有一个阳性，第 2 步没有阴性。token 距离按共享位置比较，长度变化另在 `active_token_delta` 记录，不能解释为严格的 token 对齐；masked-mean 距离和 token Gram 是 gold encoder 邻域代理，不是自然表示流形的数学距离。teacher-forced NLL 与 greedy 下一次编辑是不同过程，因而风险方向可不同。未增加新 editor、repair 或选参搜索。

## 配置、审计和复现

[config.json](config.json) 锁定 seed 42、world 划分、batch、特征定义、logistic `C=1`、2000 次 world bootstrap；[BART 提取 provenance](extraction_bart.json)与[T5Gemma 提取 provenance](extraction_t5gemma.json)记录 editor、G5 world 文件和特征哈希、Jacobian 谱值及完整世界 ID。基础模型的本地权重哈希沿用 [T5Gemma base manifest](../t5gemma_composition_v1/base_model_manifest.json) 与 G3/G5 provenance；没有上传基础权重。正式提取使用 Slurm 单卡作业 **1777**、**1778**，同时最多两卡；早期 1773/1774 在输出前因 source-list 代码错误退出，1775/1776 在排除强制 EOS margin 问题后被正式重跑取代。CPU 端运行 `analyze.py`、`cases.py`、`audit.py`；审计复算 **2930** 个文本评分、**2344** 个下一步链接、**9261** 条测试预测标签，并核对每基座锁定测试 530/530 精确输出及 train/dev/test 零交叠。[最终审计](audit.json)、[结果文件清单和哈希](run_complete.json)。
