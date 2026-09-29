# G4：长度泛化、代数性质与机制诊断

**结论。** G3 的 IID 两步成功不代表学到可重复的时间变换律。在相同的 53 个 IID 世界、同一个 `tomorrow` 起点上，G3 的 `T+` 第 1/2/3/4/5 步终点成功为 **53/53、53/53、33/53、0/53、0/53**；模板 OOD 为 **53/53、41/53、9/53、0/53、0/53**。第 3 步开始出现解码错误，第 4 步所有输出均无法由受控语法解析。表示距离从第 1 步起逐渐累积，更新仍非零，没有观测到 latent 固定点。一个 rank-8 probe-guided 子空间编辑器只尝试一次，未改善未训练长度，甚至单步也失效；停止方法扩展。

## 冻结设计与分母

复用 `facebook/bart-base` revision `aadd2ab0ae0c8268c7c9693540e9904811f36177`、G3 的四个 LowRank16 算子及 seed 42 的 [best.pt](../reference_frame_pilot_v3/checkpoints/G3/best.pt)，SHA256 `dca3cb26c0d3c1e33e3215f86e911d4c19df7417160598dcfdba8fbcffd8654d`。G3 原训练只含原子 `T+`、`T-`、两个 Person 方向，以及 `T+→T+` 两阶段目标；没有训练三步。G4 没重训 G3。

G4 从 G3 新确认集选择能从 offset `+1` 合法走满五步的世界：IID/OOD 各 53 个；另 27+27 个 `event_date=record_date` 世界在起点会使 view date 早于 record date，按输出前规则排除。两层均固定同一批世界与起点，`+1→0→-1→-2→-3→-4` 分别对应 tomorrow/today/yesterday/two/three/four days ago；五步仍在原有语法范围。每个长度都是这 53 个世界的前缀，不能与 G3 报告中不同起点、80 世界的三步 13.75%/5% 直接比较。混合链也沿用相同起点和世界。每步保存完整 `[96,768]` latent、mask、输出文本、gold frame 与语义状态；所有神经输出按同一冻结解析器重算。[配置](config.json)、[数据与模型哈希](provenance.json)、[划分](probe_split.json)、[完整性审计](audit.json) 可复核。

## A：严格长度泛化

数字为通过数/53。轨迹要求从第一步到该长度每一步都成功；fact 要求每一步可解析且非日期事实完整。无法解析算未证实保持，不等同于已确认事实改变。

| 方法 / 层 | 长度 1 | 长度 2 | 长度 3 | 长度 4 | 长度 5 |
|---|---:|---:|---:|---:|---:|
| G3 IID 终点/轨迹 | 53/53 | 53/53 | 33/53 | 0/53 | 0/53 |
| G3 OOD 终点/轨迹 | 53/53 | 41/53 | 9/53 | 0/53 | 0/53 |
| repair IID 终点 | 0/53 | 6/53 | 0/53 | 0/53 | 0/53 |
| repair IID 轨迹 | 0/53 | 0/53 | 0/53 | 0/53 | 0/53 |
| repair OOD 终点 | 0/53 | 7/53 | 0/53 | 0/53 | 0/53 |
| repair OOD 轨迹 | 0/53 | 0/53 | 0/53 | 0/53 | 0/53 |

G3 IID 全轨迹非日期事实可证保持为 53/53、53/53、36/53、0/53、0/53；OOD 为 53/53、53/53、22/53、0/53、0/53。第 3 步能解析的 IID 36 条和 OOD 22 条均保住非日期事实；第 4/5 步的零来自全体无法解析，不是 53 个已确认内容篡改。完整 [长度表](length_generalization.csv)、[曲线](length_curve.svg) 与逐例 [G3](G3_trajectories.jsonl)/[repair](repair_trajectories.jsonl) 轨迹附后。

## B：probe 实际读到什么

先在 480 个训练世界的 **gold encoder 表示**拟合 Ridge 线性 probe；80 个开发世界和 106 个测试世界从未参与拟合。覆盖 offset `-4…+5`（额外包括五步终点 `-4`）、person 和 author/recipient/action/object/quantity/status/polarity；`+5` 的 `in five days` 只供 probe gold 输入，任何训练或测试编辑链都不用这个新词。比较 encoder layer 0/3/6 的 mean/BOS/EOS。最终层 mean 在独立 gold 测试上的时间分类 96.3%、person 100%；action 99.9%、object/status 100%，quantity 70.9%、recipient 68.5%。完整 81 组结果见 [probe_accuracy.json](probe_accuracy.json)。

**gold probe 不能直接迁移到编辑 latent**：它在 G3 正确解码的第一、二步时间读数都是 0/53。另用训练世界的 G3/repair 0–2 步表示重训同一 Ridge probe，开发世界 G3 第 1/2 步仍仅 52.2%/62.5%（[校准验证](calibrated_probe_validation.json)）。因此 [线性 probe 候选分类](calibrated_failure_taxonomy.csv) 不能作为机制结论。

按预定次序再训练一个宽度 64 的单隐层 MLP 时间 probe：仅 G3 **训练世界的 0/1/2 步**，按独立开发世界选第 5 epoch，未见测试链没有参与拟合。开发 0/1/2 步准确率约 99.4%/99.2%/99.1%；测试 1/2 步均 53/53。它不是线性可读性的证据，三步以上也仍是外推；保存 [权重](mlp_probe.pt)、[验证过程](mlp_probe_validation.json) 和 [每步预测](mlp_probe_predictions.jsonl)。

| G3 测试层 | 第 1 步 | 第 2 步 | 第 3 步 | 第 4 步 | 第 5 步 |
|---|---:|---:|---:|---:|---:|
| IID MLP 时间 probe 正确 | 53/53 | 53/53 | 44/53 | 0/53 | 53/53* |
| OOD MLP 时间 probe 正确 | 53/53 | 53/53 | 47/53 | 0/53 | 53/53* |
| IID decoded 可解析 | 53/53 | 53/53 | 36/53 | 0/53 | 0/53 |
| OOD decoded 可解析 | 53/53 | 53/53 | 22/53 | 0/53 | 0/53 |

`*` 第五步的预测全是最小标签 `-4`，probe 没有 `<-4` 类，**不能**用 53/53 推断正确语义或固定点。[逐步表](mlp_probe_trajectory.csv) 同时给出成功率。Person 的 gold 线性 probe 为 100%；混合链 Person 成败另在代数表。内容 probe 在 gold 与编辑域间迁移不齐：可靠的 action/object/status 线性校准在开发世界 0–2 步为 100%，但单靠它不能证明其它内容属性不漂移，故主要用解析出的事实字段判定内容。

## C：表示几何

几何在带原始 mask 的编辑 latent **mean pooling** 后与对应 gold sentence 的编码 mean 比较；cosine distance=`1-cos`，normalized L2=`||h-E(y)||/||E(y)||`，time projection distance=`||R(h-E(y))||/||R E(y)||`，`R` 是 gold 时间线性 probe 的 8 维右奇异子空间。投影分母可小，故它只作辅助读数。最近 gold 状态从同一世界的合法 `-4…+5` 编码里按 cosine 选。不同 token 长度没有被当成逐 token 对齐。

| G3 IID 步 | cosine distance | normalized L2 | 最近 gold 状态正确 | 单步更新 norm/token |
|---:|---:|---:|---:|---:|
| 1 | .097 | .463 | 0/53 | 2.027 |
| 2 | .265 | .876 | 0/53 | 1.467 |
| 3 | .393 | 1.218 | 0/53 | 1.209 |
| 4 | .479 | 1.510 | 49/53 | 1.119 |
| 5 | .544 | 1.770 | 2/53 | 1.086 |

OOD 几乎相同。[完整距离表](representation_distance.csv)、[曲线](representation_curve.svg) 披露两模型两层。偏离从第一步已有，normalized L2 每步增量约 .41/.34/.29/.26，**不是第三步才突然跳出**；decoder 在这种持续远离自然编码的轨迹上，前两步仍能输出正确文本。最近邻不准说明编辑表示和 gold 编码不是同一简单轨道；不能把“最近邻错”单独解释成错误语义。Repair 第一步距离较小（IID .148），却 0/53 成功，说明 pooled 接近也不足以保证正确解码。

## D：动力学与 Jacobian

G3 IID `T+` 的 token 有效位 RMS 更新从 2.027→1.467→1.209→1.119→1.086；相邻 residual 方向 cosine 为 .519/.927/.967/.969。mean pooled residual norm 从 1.393 降到 .974，第五步仍为第一步的 70%，**没有接近零更新的 latent 固定点**。不同世界在同一步的 mean residual 几乎同向（与该组均值方向 cosine .997–1.000），更像共享的近固定方向加状态相关幅度；随步数方向继续转动。[residual_dynamics.csv](residual_dynamics.csv) 有所有层/模型。

仿射 LowRank 算子的 Jacobian 可精确写成 `I+UV`，无需构造样本级高维 autodiff Jacobian。G3 `T+` 奇异值最小 .066、最大 3.268、谱半径 1.021；随机方向 JVP 五步平均增益约 1.006–1.008。存在局部强收缩和扩张方向，但总体不是简单全局 contraction。Repair 的 `T+` 谱半径 1.302，mean residual norm 五步增长约 6.66 倍，解释其反复应用后明显发散。[完整谱](jacobian_spectrum.csv)、[JVP 样本](jvp_dynamics.json) 附后；这些是局部线性指标，不能单独证明文本失败因果。

## E：代数性质

同一输入的真实 latent 链与 decoded 语义分别计算。下表 latent inverse 为对原始 `h` 的**全有效 token**相对 L2；commutator 为两种次序终点 latent 的全有效 token 相对 L2。百分比是终点语义成功，轨迹另见 [代数表](algebraic_consistency.csv)。

| G3 路径 | IID latent L2 | IID 终点 | OOD latent L2 | OOD 终点 |
|---|---:|---:|---:|---:|
| `T-∘T+` inverse | .631 | 28/53 | .623 | 12/53 |
| `T+∘T-` inverse | .571 | 0/53 | .564 | 0/53 |
| `P∘T+` | — | 53/53 | — | 46/53 |
| `T+∘P` | — | 53/53 | — | 53/53 |
| 两次 `T+` 后接 `P` | — | 53/53 | — | 23/53 |
| commutator 两路径的 latent 差 / decoded state 相同 | .0575 | 53/53 | .0568 | 46/53 |

即使 IID commutator 两边 decoded semantic state 全部相同，latent 仍相差 5.75%；文本相同不能称算子交换。`T+∘T+` 对两步 gold `E(y₂)` 的 IID normalized L2=.876，虽 decoded 53/53；这就是本协议的 repeated-application/associativity 检查。两次相同函数的括号结合本身是恒等式，且没有独立学习的 `T+²` 算子，因此不能凭括号重排另造一个非平凡 associator。[全 latent inverse](inverse_full_latent.csv) 与 [逐步输出](G3_trajectories.jsonl) 可核对。

## F：唯一的 structured repair

从 **gold 训练世界**的最终层 mean 线性时间 probe 权重取前 8 个右奇异方向 `R`；仅新训 `T+`/`T-`，逐 token 使用 `h' = h + Rᵀ(A Rh+b)`，Person 沿用冻结 G3。初始化是把 G3 affine 权重投影到此空间。复用 G3 的固定 sample schedule，各 200 次更新，只有原子和被标记的 `T+→T+` 两阶段目标；损失为 token CE + `.1` pooled gold latent + `.1` inverse + `.1` 正交漂移。正交漂移因参数化几乎为零。无三步及以上目标、无 rank/权重/seed 搜索。细节、计数、过程和 [checkpoint](repair.pt) 见 [config](config.json)、[repair_training.json](repair_training.json)。

结果是明确的负例：IID/OOD 单步均 **0/53**，两步终点仅 6/53、7/53 且轨迹均 0/53；三至五步全部 0/53。它改善 inverse 的全 latent L2（IID `T-∘T+` .631→.188），也缩短前几步 pooled gold 距离，却没有保住语义编辑，且 Jacobian 谱半径 >1、更新持续增大。**没有 unseen-length generalization 改善**，不继续叠加方法。

## G：故障层级与可反驳边界

第 2 步 OOD 有 12/53 时间解码错误，而 MLP 时间 probe 为 53/53。第 3 步 IID 中，MLP 时间 probe 正确但 decoder 无法解析 13/53、另有可解析的时间错 1/53；OOD 分别是 31/53 与 9/53。这直接指向 **decoder/离开训练过的表示分布** 对失败有重要贡献。另有第 3 步 probe 指向比 gold 更早状态的候选 IID 6/53、OOD 4/53；第 4 步全部指向 `-4` 而 gold 是 `-3`，是 **over-shoot 候选**，但因为 probe 在未训练长度上外推，不能当成真值。第 5 步触及类别下界，无法区分固定点与继续越界。第 4/5 步文本全无法解析，故不能从解析器断言具体内容漂移；可靠内容 probe 仍有下降，属于警讯而非已证实的每字段损坏。[自动 taxonomy](mlp_failure_taxonomy.csv)、[计数](mlp_failure_counts.csv) 同时保留 probe/decoder 不一致和未决项，没有强行归入四种机制之一。

例子：IID 世界 `...0009` 第 3 步 gold 为 `two days ago`，MLP 也读 `-2`，输出却保留 `yesterday` 并多出 `described today`，第 4 步转为重复的日期碎片。IID `...0017` 第 3 步 gold `-2`、probe `-4`，输出 `has an event date ago`；两者都显示第三步可由不同故障路径失败。[典型完整轨迹](typical_trajectories_mlp.json) 含 IID/OOD 的 gold、预测和全部文本。

因此本批最稳妥的机制回答是：**G3 会沿一条持续远离自然 gold 编码的轨迹更新，decoder 对前两步有局部容忍；继续迭代后出现语义失配和生成崩坏。它不是一个在测试范围内可靠可重复的 semantic transformation law。** 这个证据不能唯一分离 decoder 的因果作用与 off-manifold 表示的因果作用；单 seed、合成短句、受控解析器及 probe 对未见长度的外推仍限制结论。

## 复现与审计

从仓库根目录运行 `sbatch --partition=B300q --exclude=node01 experiments/algebraic_generalization_v1/run.slurm`，再运行同目录 `calibrate.slurm`、`mlp.slurm`；CPU 汇总为 `analyze.py`、`analyze_calibrated.py`、`analyze_mlp.py`、`analyze_dynamics.py`、`audit.py`。GPU 正式作业为 1760/1761/1762；最初 node01 作业步启动失败，随后一次试跑因把 BART encoder 错索引为第 12 层而失败，均未产生有效 probe/模型训练结果，修正为层 0/3/6 后只做上述一次 repair。主作业产出 G3/repair 各 1696 个阶段 latent 与文本；审计重算所有评分、验证 106 个 source latent、训练/开发/测试世界不交叉以及共享路径前缀 latent 精确一致，见 [audit.json](audit.json)。所有种子、checkpoint、输出和数据哈希在同目录机器可读文件中；基础 BART 权重按仓库既有约定保留本地。

GitHub 版本将两份各约 241 MiB 的完整 latent 无损压缩、拆为每片小于 100 MB 的 [归档分片](latents_archive/manifest.json)，克隆后运行 `python experiments/algebraic_generalization_v1/restore_latents.py` 即恢复原 `.pt`，脚本逐片和恢复后均验 SHA256。原始两份 `.pt` 在本地保留并被本目录 `.gitignore` 排除；其余文本结果、probe/repair checkpoint 与 16 MiB source latent 直接发布。归档解压后 SHA256 已与原文件逐一核对。
