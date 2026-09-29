# G6：Learned Latent Reset（固定一次训练）

**结论：这次小型纯 latent reset 没有复现 G5 的长链收益，且比不加 reset 更差。** 同一批 53 个 IID + 53 个 OOD 世界，learned reset 第 1 步仅分别成功 27/53，第 2–5 步两层都为 0/53；每步 `decode→re-encode` 的第 5 步分别为 53/53、37/53。我们按预先固定的 300 次更新训练了一个 width 64 residual MLP，没有按 3–5 步结果选参或训练第二个方法。负结果不能证明**任何**纯 latent projector 都不可能成功；它表明当前低容量、固定 token/mask、MSE 模仿 `E(D(h))` 的版本不够。

## 协议与训练边界

固定 `facebook/bart-base` 和 G3 seed 42 LowRank16 `T+` checkpoint SHA256 `dca3cb26c0d3c1e33e3215f86e911d4c19df7417160598dcfdba8fbcffd8654d`；不训练或调参 editor。reset 是唯一新模块：先对 token 做无参数 LayerNorm，以 masked mean 提取句级 context，经 width 64 的 residual MLP 输出逐 token 修正；输入 mask 保持不变。目标为**同一编辑表示所解出的文本**重新编码后的 `E(D(h))`，训练损失是输入有效 token 的 MSE 加 0.5 倍 pooled 表示 MSE。目标文本来自冻结 G3/decoder，不使用 gold 文本训练 reset。

480 个 G4 train 世界中，前 432 个用于优化，后 48 个仅作第 1–2 步模仿误差验证。源状态按世界类别选 offset `+1`（future）或 `-1`（completed），各用 first/third 人称；只有从起点开始每步 decoded 语义正确的阶段才进入样本。实际收集 1,919 个样本（第 1 步 960、第 2 步 959）；其中优化 1,727，保留验证 192。更新数 300、batch 16、AdamW learning rate .001、seed 42，取**预定最终更新** checkpoint。保留验证的模仿损失从更新 1 的 .0210 下降到最终 .00244，但这个 MSE 不是文本解码成功率。训练样本中 1,280/1,919 的原输入与重新编码目标有效 token 长度不同；固定长度的逐位置损失在这些位置上未提供真正的 token 对齐。

测试完全复用 G5 固定的 53 IID + 53 OOD 世界、相同 `offset +1` 起点、greedy `max_new_tokens=60` 和前两条路径的已锁定输出。第三条路径为 `h_{k+1}=R(T+(h_k))`，每步只把该 latent 传给下一步；解码仅供评分，gold 仅供评分和距离。stage 1 的三路径源文本及 G3 编辑态相同。评价无测试链选参、无第二次 reset 训练。 [配置](config.json)、[训练日志](training.json)、[逐条训练清单](train_manifest.jsonl)、[来源哈希与固定世界](provenance.json)和[运行记录](run_complete.json)可复核。

## 三路径长度泛化

各格为 endpoint / 完整 trajectory 成功数，分母 53；这批数据两者相同。trajectory 要求之前每一步也成功。[完整表](length_generalization.csv)含逐步非日期事实可证保持率，[长度曲线](length_curve.svg)和[配对差异及 5000 次按世界 bootstrap 区间](paired_effects.csv)另存。

| 测试层与路径 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| IID pure latent | 53/53 | 53/53 | 33/53 | 0/53 | 0/53 |
| IID decode-reencode | 53/53 | 53/53 | 53/53 | 53/53 | 53/53 |
| IID learned reset | 27/53 | 0/53 | 0/53 | 0/53 | 0/53 |
| OOD pure latent | 53/53 | 41/53 | 9/53 | 0/53 | 0/53 |
| OOD decode-reencode | 53/53 | 41/53 | 41/53 | 41/53 | 37/53 |
| OOD learned reset | 27/53 | 0/53 | 0/53 | 0/53 | 0/53 |

IID 第 3 步 learned 比 pure 少 33/53（-62.26pp，配对 bootstrap 95% 区间 [-75.47,-49.06]pp）；比 decode-reencode 少 53/53。OOD 第 3 步 learned 比 pure 少 9/53（-16.98pp，[-28.30,-7.55]pp），比 decode-reencode 少 41/53。第 5 步 learned 与 pure 同为 0/53，所以**没有未见长度收益**。事实保持的 0/53 主要是输出无法按受控语法解析，表示“未证实保持”，不能解读为每个事实都被明确改写。

## 表示距离：几何改善不足以保证可解码

下表为到对应 gold `E(y_k)` 的 mean-pooled normalized L2。`pure` 的斜线后是 G5 的*独立诊断* `E(D(h))`，并未反馈到 pure 链；`decode-reencode` 和 `learned` 的斜线后是下一步实际使用的状态。逐例 cosine、编辑前后距离、残差范数在[距离表](representation_distance.csv)及[曲线](distance_curve.svg)。

| 层与路径 | 1 步 | 2 步 | 3 步 | 4 步 | 5 步 |
|---|---:|---:|---:|---:|---:|
| IID pure 编辑后 / 独立重编码 | .463/.000 | .876/.000 | 1.218/.050 | 1.510/.741 | 1.770/1.131 |
| IID decode-reencode 编辑后 / 重编码 | .463/.000 | .457/.000 | .455/.000 | .452/.000 | .456/.000 |
| IID learned 编辑后 / reset | .463/.057 | .478/.109 | .454/.148 | .450/.195 | .458/.232 |
| OOD pure 编辑后 / 独立重编码 | .469/.000 | .879/.014 | 1.223/.120 | 1.513/.724 | 1.772/1.148 |
| OOD decode-reencode 编辑后 / 重编码 | .469/.000 | .461/.014 | .463/.024 | .461/.024 | .464/.026 |
| OOD learned 编辑后 / reset | .469/.066 | .478/.111 | .462/.155 | .459/.199 | .468/.233 |

Learned reset 对**每个**逐步表示的 pooled gold 距离均有下降，但距离仍逐步累积，IID `.057→.232`、OOD `.066→.233`。它在第一步已让 52/106 个原本可正确解码的 G3 编辑态变成无法解析；其中原编辑态第一步为 106/106 成功。这是直接的 reset/decoder 界面失效，不是等到未见第 3 步才出现的 operator 饱和。该 pooled 距离只汇总 token，不能保证每个位置落在 decoder 可接受的完整序列表示分布上。

## 长度、mask、tokenization 诊断与失败分类

第一步 106/106 个 pure 编辑文本与源文本的有效 token **长度相等**，且原编辑文本 106/106 正确；learned reset 仍有 52/106 失败。将**同一** learned latent 的 decoder mask 换成 `E(D(T+(h)))` 的 mask，没有救回任何 learned 失败案例，第一步本来就无长度差。由此可排除“仅仅没更新 mask 长度”作为第一步失败的充分解释。第一步文本 token ID 序列 106/106 与源文本不同，即使 token 数相同，`E(D(h))` 仍重新分词并完整通过 encoder；这与 learned 固定 token 布局有实质差异。它提示位置相关的 encoder 变换/离散文本瓶颈可能重要，但本试验不能把 tokenizer 因果作用与 MLP 容量、逐位置 MSE 错位或 decoder 对小误差的敏感性分开。

到第二步，两层 53/53 均失败，其中 IID 26/53、OOD 26/53 存在输入与 oracle 的 mask 长度差；各层另有 27/53 个失败**长度相同**。第三步以后 mask 差更常见，但往往是早期输出已错后的次生现象；换 oracle mask 的反事实解码在全部失败样本中救回 **0** 个。[逐例诊断](mask_token_diagnostic.csv)、[分层计数](mask_token_summary.csv)。

[失败分类](failure_counts.csv)采用优先级：成功、无法解析、可解析但非日期事实错误、可解析但时间/人称错误。Learned 第一步每层 `27 成功 + 26 无法解析`；第二步 IID `39 无法解析 + 14 语义错误`，OOD `42 无法解析 + 11 语义错误`；第三至第五步两层均 53/53 无法解析。[逐例分类](failure_taxonomy.csv)保留事实可证保持标记。OOD decode-reencode 的 12 个第二步语义错误由 G3 本身带来，符合 G5 的“重编码不能修复已写错的文本”。

典型 [IID 0000](typical_trajectories.json)：learned 第一步正确，第二步已错，此后无可解析文本；pure 前三步正确、第四步崩；decode-reencode 五步正确。典型 OOD 0000 同样在 learned 第二步失败，而 decode-reencode 五步正确。OOD 0009 是对照：pure 与 decode-reencode 第二步均错，learned 也失败。没有“learned 恢复而 pure 失败”的完整五步案例。文件包含逐阶段 gold、三条路径文本和距离。

## 对核心问题的回答与限制

1. **不能复现长链收益。** 这个唯一的 reset checkpoint 在完全未见的 3–5 步为 0/53 IID、0/53 OOD；在第 1–2 步已破坏不少原本成功的 G3 输出。
2. **文本离散化/重新 tokenization 可能是必要组成，但尚未证明必要。** 相同长度 mask 下第一步也失败，oracle mask 对照无救回，排除纯长度修正；重新编码实际还包含 token ID、位置与整句 encoder 计算。模型容量、对齐目标及 loss 也可能解释失败。
3. **G5 的收益对本方法更像完整 discrete language bottleneck reset，不能简化成“把 pooled latent 拉近 gold”。** Learned 将 pooled L2 降到约 `.06` 仍导致约半数首步输出崩坏；G5 重编码在第一步与 gold 编码重合并保持文本成功。这里的证据支持“完整重编码所做的事情超出了该小型固定布局 MLP 的几何拟合”，而非所有 latent reset 的不可能性定理。

单一训练 seed、一个宽度和单一受控语言环境限制外推。test 上的 pooled gold 距离只是分析指标，未喂给模型；G5 的 `E(D(h))` 与正确文本相同的情形按定义接近 gold，不能作为独立的最邻近流形投影证明。我们按预设停止，没有继续堆方法。

## 复核与交付

运行 `sbatch experiments/latent_reset_v1/run.slurm`（本次 Slurm job **1766**），随后 `.venv/bin/python experiments/latent_reset_v1/analyze.py` 与 `.venv/bin/python experiments/latent_reset_v1/audit.py`。 [审计](audit.json)复算 1,590 个编辑前/reset/反事实 mask 文本评分和 530 组保存向量距离，最大误差 `<5×10⁻⁷`；核对训练只含步骤 1–2、train/test 世界无交集、106 个第一步源一致、424 个后续链输入连续。 [reset checkpoint](reset.pt)约 584 KiB，[保存的 mean-pooled 向量](pooled_representations.pt)约 6.9 MiB；不上传 BART 基础模型或完整 96×768 中间激活。
