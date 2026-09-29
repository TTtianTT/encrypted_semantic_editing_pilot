# G5：Projection Hypothesis 最小验证

**结论。** 在 G4 固定的 53 个 IID + 53 个模板 OOD 世界、同一 `offset +1` 起点上，冻结 G3 `T+` 的 pure latent 链到第 4/5 步两层全为 0/53；每步 `decode→re-encode` 的完整五步轨迹为 IID **53/53**、OOD **37/53**。配对世界的第 3–5 步差异均有不跨零的 95% bootstrap 区间。重编码后表示到对应 gold 编码的距离通常大幅下降，成功的链持续落在 gold 编码附近。这支持“每步重新编码可重置到 BART encoder 产生、decoder 易解码的表示区域”，但不证明它是某种最近点投影，更不能修复**已被错误文本带走的语义状态**。

## 固定协议

两路径使用同一 `facebook/bart-base`、G3 seed 42 LowRank16 `T+` best checkpoint SHA256 `dca3cb26c0d3c1e33e3215f86e911d4c19df7417160598dcfdba8fbcffd8654d`，greedy、`max_new_tokens=60`、输入上限 96。没有训练 editor、新 projector、新 loss 或调参。106 个世界及 `+1→0→-1→-2→-3→-4` 五步起点与 G4 完全一致。pure 路径直接复用 G4 [逐步输出](../algebraic_generalization_v1/G3_trajectories.jsonl)和完整 latent，避免重复生成误差；decode-reencode 路径从相同源文本新运行，每一步只把**自身 decoded text** 输入冻结 encoder，gold 文本只用于评分和距离。第一步两路径输出逐字一致 106/106。

每步保存编辑后文本、受控解析的语义/事实状态、G4 编辑态 MLP probe、对应 gold 状态、编辑 residual norm、编辑后及重编码后的 cosine 和 normalized L2。另对 pure 编辑态 `h` 单独做 `E(D(h))` 并计算 `D(E(D(h)))`，检验同一步能否修复。距离以有效 token mean 向量计算：`1−cos(h,E(y))` 与 `||h−E(y)||/||E(y)||`；这是可复核的 pooled 几何代理，不是完整 decoder manifold 的距离。所有逐例向量与文本在 [pooled_representations.pt](pooled_representations.pt)、[pure reset controls](pure_reset_controls.jsonl)、[decode-reencode trajectories](decode_reencode_trajectories.jsonl)。

## 长度泛化：两路径配对结果

表中为 endpoint/完整 trajectory 成功数，分母均 53；这批数据里两者数值相同。trajectory 必须此前所有阶段均成功。非日期事实可证保持率、未决解析和每步文本在 [完整表](length_generalization.csv)与[长度曲线](length_curve.svg)。

| 层与路径 | 1 步 | 2 步 | 3 步 | 4 步 | 5 步 |
|---|---:|---:|---:|---:|---:|
| IID pure latent | 53/53 | 53/53 | 33/53 | 0/53 | 0/53 |
| IID decode-reencode | 53/53 | 53/53 | **53/53** | **53/53** | **53/53** |
| OOD pure latent | 53/53 | 41/53 | 9/53 | 0/53 | 0/53 |
| OOD decode-reencode | 53/53 | 41/53 | **41/53** | **41/53** | **37/53** |

在 IID 第 3 步，重编码比 pure 多 20/53 成功，差 +37.74pp，配对世界 bootstrap 95% 区间 `[+24.53,+50.94]pp`；第 4/5 步均多 53/53。OOD 第 3/4/5 步分别多 32/41/37 个成功，差 `+60.38/+77.36/+69.81pp`，区间分别 `[+47.17,+73.58]`、`[+66.04,+88.68]`、`[+56.60,+81.13]pp`。相应精确 McNemar 双侧 p 均 `<2×10⁻⁶`，见[配对结果](paired_effects.csv)。这说明在固定世界样本上改善明确；区间没有包含 editor 训练种子的变异，且实验只在受控短句语法上进行。

OOD 的 12/53 在第 2 步两路径都把日期留在错误状态；重编码把这个**错误文本**稳定成下一步输入，不能挽回它们。第 5 步另有 4 个 OOD 世界新出错。所有 decode-reencode 阶段的非日期事实均可解析且保留 53/53；pure 第 4/5 步全部不可解析，故其事实保持计 0 只表示未证实，不能当作 53 个已确认内容篡改。

## 表示 reset：`d(h,E(y))` 对照 `d(E(D(h)),E(y))`

下表给出平均 normalized L2，斜线前是编辑后，斜线后是把**该步输出**重新编码后。IID 成功链的 re-encode 后向量与 gold 向量几乎相同，因为 decoded text 正是 gold 文本；OOD 的小非零值对应已错误的日期文本。全表同时含 cosine、逐例是否下降、residual norm 和 reset 后重新解码评分，见 [representation_reset.csv](representation_reset.csv) 和[距离曲线](distance_curve.svg)。

| 层与路径 | 1 步 | 2 步 | 3 步 | 4 步 | 5 步 |
|---|---:|---:|---:|---:|---:|
| IID pure `h / E(D(h))` | .463 / .000 | .876 / .000 | 1.218 / .050 | 1.510 / .741 | 1.770 / 1.131 |
| IID reencode 链 `h' / E(D(h'))` | .463 / .000 | .457 / .000 | .455 / .000 | .452 / .000 | .456 / .000 |
| OOD pure `h / E(D(h))` | .469 / .000 | .879 / .014 | 1.223 / .120 | 1.513 / .724 | 1.772 / 1.148 |
| OOD reencode 链 `h' / E(D(h'))` | .469 / .000 | .461 / .014 | .463 / .024 | .461 / .024 | .464 / .026 |

全部 2×2×5×53 个逐步对照中，re-encode 后到 gold 的 L2 都下降。但这个数值**不等于语义修复**：pure 第 4 步 IID 距离由 1.510 降到 .741，`D(E(D(h)))` 仍 0/53 成功；第 5 步同样 0/53。第 3 步 pure 的单次同阶段 reset 成功率仍等于原 pure 成功率，IID 33/53、OOD 9/53。正确解释是重编码把任何 decoded text 都送回自然 encoder image；它只在先前文本语义正确时才会落到**正确的** gold 邻域。连续链必须在错误首次出现前重置。

## Probe、decoder 与 failure taxonomy

G4 的小 MLP 时间 probe 只用独立训练世界的 0/1/2 步 G3 编辑态训练，开发世界这三层约 99% 正确。它可作 pure 第 3 步的探索性读数，却对第 3 步以后的 decode-reencode 编辑态和某些重新编码的 gold 状态分布迁移不稳；不能把其错误预测当作 reencode 链的语义错误。[逐步原始读数](pure_reset_controls.jsonl)和[分类](failure_taxonomy.csv)保留这些结果。

为检查 reset 状态，另严格复现 G4 gold encoder mean 的 Ridge time probe（`alpha=10`，只拟合 480 个训练世界的 gold 编码，覆盖 `-4…+5`，没有测试链拟合）。独立开发准确率 97.22%，测试 gold 编码 96.27%；各时间类准确率与 [权重](gold_probe_weights.npz)见 [验证](gold_probe_validation.json)。它在 edited latent 上也不校准，故只将其 **reset 向量**预测用于解释。成功的 IID reencode 链第 1–3 步 reset probe 均 53/53 正确，第 4/5 步随 `-3/-4` gold 类本身错误率降至 52/53、51/53；OOD 成功输出条件下的第 3/4/5 步 reset probe 正确率约 97.56%/95.12%/86.49%。完整逐例与按类表在 [gold_probe_trajectory.csv](gold_probe_trajectory.csv)。

G4 编辑态 MLP 标为“时间正确、decoder 失败”的 pure 第 3 步案例：IID 14 个、OOD 40 个；对应世界的 decode-reencode 链在第 3 步分别成功 14/14、32/40，而对**同一个已失败 pure 输出**单独做 `D(E(D(h)))`，成功 0/14、0/40。后者是关键区分：配对世界的预防性链恢复，不代表已经输出的错误可被投影挽回。第 5 步 probe 全读最小类 `-4`，存在类别下界，故不据此声称 latent time state 正确。[probe/decoder 配对计数](probe_decoder_recovery.csv)、[failure taxonomy](failure_counts.csv)保留成功、日期错误和无法解析三个主要层级。

典型 IID `...0000`：pure 前三步正确，第四步输出重复的日期碎片，第五步继续崩；reencode 五步依次为 `today→yesterday→two days ago→three days ago→four days ago`。典型 OOD `...0000`：pure 第三步已破坏句式，reencode 到第五步仍正确。失败对照 OOD `...0009`：两路径第二步都把目标 `yesterday` 留作 `today`，reencode 随后稳定在错误日期，五步均未恢复。[完整配对轨迹](typical_trajectories.json)包含每步文本、gold、probe 与几何。

## 机制解释与边界

结果同时符合三个可观察事实：pure 编辑向量逐步远离对应 gold 编码并在第 4/5 步不能被正常解码；逐步 decode-reencode 后的表示距离不累积，长链成功大幅恢复；已经错误的 pure 输出虽可被重新编码成合法 encoder 表示，却不会自动回到正确语义。这**支持**重编码作为每步 representation reset 的解释，并表明 reset 必须在语义错误前发生。

这还不是对“最近流形投影”的独立数学证明：`E(D(h))` 按定义就是某个文本的 encoder image；解码、重新分词、mask 改变和文本层纠错同时发生，不能从该比较唯一归因给几何投影。gold 距离使用 mean pooling，无法覆盖完整高维 manifold。OOD 的既有第二步日期错误未被 reset 修复，说明正确内容仍是必要条件。单 seed、合成短句、固定 BART/语法和 probe 对未训练步骤的外推限制推广。

## 配置、审计与复现

[config.json](config.json) 固定 seed、两个路径、probe 来源、greedy 解码与 5000 次按世界配对 bootstrap。G3 checkpoint、BART、G4 pure 输出/latent/probe、原始 world 文件和固定世界 ID 的 SHA256 记录在 [provenance.json](provenance.json)；[run_complete.json](run_complete.json)锁定 G5 输出哈希。正式 GPU 作业 1764，之前 1763 仅因 G4 probe state-dict 键名前缀加载错误而在输出前退出；独立 gold probe 作业 1765。`audit.py` 重算 2120 个编辑/重编码文本评分、核对 106/106 第一步与 G4 一致、所有 paired key 和保存向量的距离（最大数值误差 `<5×10⁻⁷`），详见 [audit.json](audit.json)。运行顺序为 `run.slurm`、`analyze.py`、`gold_probe.slurm`、`analyze_gold_probe.py`、`audit.py`；整个 G5 无编辑器或 projector 训练。
