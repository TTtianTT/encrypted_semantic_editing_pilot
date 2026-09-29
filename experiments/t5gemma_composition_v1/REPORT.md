# T5Gemma 上的 G4–G5 composition / drift / re-encode 复现

**结论。** 在冻结的原版 T5Gemma 2B-2B UL2-IT 上，只训练一个 G3 式 rank-16 `T+`，G5 锁定的 53 IID + 53 模板 OOD 世界也出现了“前两步多半正确、第三步 pure latent 全部失败、每步 decode→re-encode 恢复五步”的现象。T5Gemma pure 第 3–5 步两层均为 **0/53**；decode-reencode 第 1–5 步两层均为 **53/53**。因此这一**定性现象不是 BART 独有**。不过，T5Gemma 的 pure 轨迹比 BART 更早、更快地漂移，编辑 residual 由小变大；BART residual 逐步缩小。两基座的参数规模、训练目标、提示和精度不同，不能将量化差异单独归因于架构。

## 基座、接口和固定训练

使用已存在于 `/dataset1/zailong/models/reference-frame-cross-backbone/t5gemma-2b-2b-ul2-it` 的 [Google T5Gemma 2B-2B UL2-IT](https://huggingface.co/google/t5gemma-2b-2b-ul2-it)，不是 T5Gemma 2 270M。官方模型卡说明这是 2B encoder + 2B decoder 的 instruction-tuned UL2 版本，并展示 chat template 推理方式。实际模型共 5,596,853,760 参数，encoder hidden size 2,304；全程冻结主模型，只优化一个 bias + rank-16 `U(Vh)` residual `T+`。本地三份权重 SHA256、config/index/tokenizer 哈希与不上传基础权重的记录在 [base_model_manifest.json](base_model_manifest.json) 和 [training_provenance.json](training_provenance.json)。

在**训练世界**的 16 句预检中，无指令和普通文字复制指令的 `D(E(x))` 均为 0/16 语义正确；固定 chat 格式、要求只返回一次原文后为 14/16。故正式训练/测试将同一固定指令应用于 source、重新编码的 decoded text 和 gold `E(y_k)`；解码文本直接交原 G4/G5 评分器，不附加后处理。[三次预检](preflight_unprompted.json)、[普通提示](preflight_plain_prompt.json)、[固定 chat 提示](preflight.json)保留原文与输出。这个提示是 T5Gemma 指令版的输入接口适配，**BART 无此提示**，必须作为对照限制。

训练只用 G3 的 960 条 `T+` 单步源行及原 G3 `T+` sample schedule 的两步阶段标记。把 200 个 T+ batch 顺序重复三次，共 600 次更新、batch 16，第二步目标始终为 `T+(T+(x))` 的 gold 文本，**没有 3–5 步监督**。第 1/2 步目标 token NLL 各占 0.5；seed 42、AdamW learning rate .001、weight decay 0、gradient clip 1。仅按独立 G3 dev 世界上的**单步** target-token NLL 在每 100 次更新选 checkpoint，最终选第 600 次，dev NLL `7.87×10⁻⁶`。[配置](config.json)、[训练历史](training.json)、[编辑器 checkpoint](editor_best.pt)。BART G3 的 T+ 只得到其多算子总训练中的 200 次更新；T5Gemma 用 600 次 T+ 更新，训练预算不完全匹配，但数据任务和最长监督长度一致。

测试用 G5 的**同一 106 个世界和 `offset +1` 起点**，greedy 解码，最长 96 个 T5Gemma token；输入最少 pad 到 128，decoded text 超长时动态扩展、从不截断。两路径为 `T+^k` 与 `(E∘D∘T+)^k`，后者只反馈自身 decoded text。每一步保存文本、语义/非日期事实评分、mask 长度、编辑 residual norm、编辑 latent 及 `E(D(h))` 到对应 gold `E(y_k)` 的 masked-mean cosine / normalized L2；保存[逐例记录](trajectories.jsonl)和[pooled 向量](pooled_representations.pt)。对 BART 直接复用 G5 的固定结果，保证相同世界配对。

## BART vs T5Gemma：长度泛化

每格为 endpoint / 完整 trajectory 成功数，分母 53；本批样本中两者相同。完整 trajectory 要求从第 1 步到当前步全部成功。[对照表](backbone_comparison.csv)还含逐步非日期事实可证保持率和“前两步成功”条件分母。[IID 曲线](length_curve_iid.svg)、[OOD 曲线](length_curve_ood.svg)、[配对 bootstrap / McNemar](paired_effects.csv)。

| 基座 · 路径 | IID 1 | IID 2 | IID 3 | IID 4 | IID 5 | OOD 1 | OOD 2 | OOD 3 | OOD 4 | OOD 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BART · pure | 53 | 53 | 33 | 0 | 0 | 53 | 41 | 9 | 0 | 0 |
| BART · decode-reencode | 53 | 53 | 53 | 53 | 53 | 53 | 41 | 41 | 41 | 37 |
| T5Gemma · pure | 53 | 41 | **0** | 0 | 0 | 53 | 52 | **0** | 0 | 0 |
| T5Gemma · decode-reencode | 53 | 53 | **53** | 53 | 53 | 53 | 53 | **53** | 53 | 53 |

T5Gemma 在第一步两层都为 53/53。IID 第 2 步 pure 已有 12 个无法解析，故不能说所有样本均两步成功；**在前两步成功的 41/53 IID、52/53 OOD 中，第三步也全部失败**。BART IID 第三步还有 33/53 成功，第四步才全败；BART OOD 第三步 9/53。T5Gemma 的 decode-reencode 在第三步相对 pure 两层均 +53/53（+100pp；配对 exact McNemar `p=2.22×10⁻¹⁶`），一直保持到第五步。其全部 530 个 decoded text 在 `strip()` 后与对应 gold 文本逐字相同，[精确匹配表](exact_text_match.csv)。BART OOD reencode 的 12 个第二步日期错误及第五步新增错误在 T5Gemma 这次未出现；这反映新模型、训练与提示的差别，不是 reset 能改写已经错误的文本。

T5Gemma pure 第三步 IID 有 41/53 个**可解析但时间错**、12/53 个无法解析；OOD 分别为 26/53 和 27/53。可解析的 IID 错误中，31 个将事件日滞后一日（典型为目标 `two days ago` 却输出 `yesterday`，表现为 saturation）；OOD 有 23 个将事件日前冲一日（常输出 `three days ago`，表现为 overshoot）。第四、五步 pure 两层都不可解析。[分类](failure_counts.csv)、[时间偏差](parsed_time_error_counts.csv)和[逐例 taxonomy](failure_taxonomy.csv)给出可重算数据。事实保持计数仅在受控解析成功时成立；不可解析不等于已证实篡改了事实。

## 几何与动态：相同现象，不同漂移速度

下表是**编辑后、进入 decoder 的 latent** 到对应 gold encoder 表示的 mean-pooled normalized L2；每个基座都除以自身 gold 向量范数。逐步 cosine、独立 `E(D(h))` 距离及 residual norm 见[完整表](representation_distance.csv)、[IID 距离曲线](distance_curve_iid.svg)、[OOD 距离曲线](distance_curve_ood.svg)、[漂移摘要](drift_summary.csv)。

| 基座 · 路径 | IID 1→2→3→4→5 | OOD 1→2→3→4→5 |
|---|---|---|
| BART · pure | .463 → .876 → 1.218 → 1.510 → 1.770 | .469 → .879 → 1.223 → 1.513 → 1.772 |
| BART · decode-reencode | .463 → .457 → .455 → .452 → .456 | .469 → .461 → .463 → .461 → .464 |
| T5Gemma · pure | .517 → 1.189 → 2.053 → 3.155 → 4.536 | .516 → 1.186 → 2.047 → 3.146 → 4.525 |
| T5Gemma · decode-reencode | .517 → .516 → .524 → .524 → .530 | .516 → .514 → .518 → .517 → .522 |

T5Gemma pure 从第 2 至第 5 步的 IID L2 增量为 `+3.348`，BART 为 `+0.894`；两层曲线接近。T5Gemma pure cosine distance 同期约 `.351→.771`，BART `.265→.544`。T5Gemma 的每步 residual norm（按有效 token 数平方根归一）IID 约 `31.5→38.3→47.5→59.0→72.9`，呈**扩张**；BART `2.03→1.47→1.21→1.12→1.09`，呈**收缩/趋饱和**。绝对 residual 尺度跨模型不可直接比较，但相反的链内趋势说明失败动力学不同。每步重编码使两模型下一步使用的表示不持续远离 gold；T5Gemma decode-reencode 编辑态距离稳定约 `.51–.53`，重编码后因输出就是 gold 文本，pooled gold 距离为 0。此处的 mean pooling 是几何代理，不是完整 decoder manifold 距离。

## 典型轨迹与基座控制

[完整逐步案例](typical_trajectories.json)含 gold、两基座各两路径的文本与距离。IID `...0000` 的 T5Gemma pure 前两步正确，第三步目标 `two days ago` 却仍输出 `yesterday`，第四步变成重复的多语种碎片，第五步为空；decode-reencode 五步依次正确。OOD `...0000` 前两步同样正确，第三步 pure 将目标 `two days ago` 改为不完整的 `three days ago` 句，第四步碎片化；decode-reencode 五步正确。IID 例的 BART pure 到第四步才坏；OOD 例两种基座都在第三步失败。

对冻结 T5Gemma 的 `D(E(source))` 单独测试，IID 48/53、OOD 50/53 语义正确；逐阶段 gold `D(E(y_k))` 为 IID 50–52/53、OOD 52–53/53，见[自编码控制](autoencoding_controls.csv)。因此此基座**并非无条件完美复述器**。不过测试中的 T5Gemma 编辑一步和逐步重编码五步全部正确；pure 第三步崩溃不能简单归咎于 gold 本来无法被 decoder 读出。前两步训练虽使 dev token loss 很低，自回归自由解码仍是独立测量。

## 结论边界、审计与复现

三个预设问题的回答是：**（1）是**，T5Gemma 在绝大多数前两步成功样本上第三步 pure 全败；**（2）是**，到 gold encoder 表示的距离随重复编辑明显累积，且比本次 BART 对照增长更快；**（3）是**，逐步 decode-reencode 把两层五步都恢复到 53/53。第一种跨基座重复现象得到支持，但不能证明相同的微观机制：T5Gemma residual 越变越大，BART 越变越小；T5Gemma 是更大的 instruction-tuned UL2 模型，用固定 chat 复制指令、BF16 和 600 次 `T+` 更新，而 BART 是较小的 FP32 基座、无提示且 T+ 只有 200 次更新。没有新 reset、probe repair、复杂搜索或第二个训练 seed。

正式 Slurm 单卡作业：预检 1767（无提示）、1768（普通提示）、1769（固定 chat），训练 1770，最终评估 1772。评估 1771 在一条 OOD decoded 文本加提示后达到 130 tokens、超过最初 128 padding 时于写结果前退出；1772 只将 padding **按实际长度扩展且不截断**，编辑器、训练及评分均未改动。[审计](audit.json)核对三份本地基座权重哈希、checkpoint 与数据哈希、106 个测试世界与训练世界零交集、1,060 个 paired 阶段和 1,696 次文本评分，并复算保存的 pooled 距离，最大误差 `<9×10⁻⁷`。[eval provenance](eval_provenance.json)、[运行完成记录](eval_complete.json)锁定本次结果。复现顺序：`preflight.slurm`（固定 chat 版）、`train.slurm`、`evaluate.slurm`、`analyze.py`、`audit.py`；所有 GPU 作业均由 Slurm 提交，单次只申请一张卡。仅上传小型 editor checkpoint、代码、报告和关键结果，不上传 T5Gemma 基础权重或优化器恢复文件。
