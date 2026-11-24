# ESEP：论文写作 + v6 实验计划

- 项目：Encrypted Semantic Editing Pilot（ESEP）
- 日期：2026-11-24
- 两条线并行：
  - **A 线（论文）**：只读取已锁定的结果，不改动任何实验目录。分支 `paper/composability`，从 `origin/experiment/composability-mechanisms-v4`（`b9d70c5`）新建，目录 `paper/`。
  - **B 线（v6 实验）**：实验名 `composability_mechanisms_v5`。分支 `experiment/composability-mechanisms-v5`，从同一提交新建，目录 `experiments/composability_mechanisms_v5/`。
- v6 结束后，把 B 线分支合并进 A 线分支，再在论文里补入 v6 的结果。
- 把本文件存为 `paper/PLAN.md`，同时复制一份到 `experiments/composability_mechanisms_v5/PLAN.md`，都提交。

## 计划编号与目录的对应（写论文时以目录和锁定提交为准）

| 计划 | 目录 | 锁定提交 |
| --- | --- | --- |
| v1 | `experiments/symmetry_composability_v1/` | `b9419d4` |
| v2 | `experiments/composability_mechanisms_v1/` | `e2fa258` |
| v3 | `experiments/composability_mechanisms_v2/` | `078b1e8` |
| v4 | `experiments/composability_mechanisms_v3/` | `51a7579` |
| v5 | `experiments/composability_mechanisms_v4/` | `8667c90` |
| v6 | `experiments/composability_mechanisms_v5/` | 待定 |

---

# A 线：论文

## A1. 定位

**一句话主张**（草稿）：
- 中文：在冻结的编码器–解码器里，单步解码正确的潜空间编辑不一定能连续组合。原因有两类：编辑器写入的是解码器能执行的指令，而不是状态；低秩编辑丢掉了槽位傅里叶编码中负责全局位置的基频。可组合性可以只看潜变量预测，不需要解码。
- English: *Latent edits that decode correctly need not compose. Editors trained through the decoder write decoder-executable instructions instead of states, and low-rank state editors drop the slowest Fourier mode of the slot code, which carries global position. Composability can be predicted from latents alone, without decoding.*

**候选标题**：
1. *Decodable Is Not Composable: When Do Latent Edits Chain in Frozen Encoder–Decoder Models?*
2. *One Correct Step Is Not Enough: Instructions, Fourier Codes, and the Composability of Latent Edits*
3. *Predicting Whether Latent Edits Compose Without Decoding*

**动机的写法**：如果 ESEP 的初衷是"只在潜空间里操作、不解码"（例如加密或隐私场景），那么不解码就能预测可组合性正好回应了这个场景：在这类管线里，没法靠解码来逐步验证编辑。这一点由负责人确认后写进引言。

**会议**：由负责人按截稿日决定。内容（机制分析加预测方法）更接近 ICML 的表示与可解释性方向；投 ACL 时，引言和实验部分要更强调文本编辑。LaTeX 先用中性模板，决定后再移植。

## A2. 主张账本
每条主张都要能追溯到锁定的预测或明确标注的探索性分析。Claude Code 把它维护成 `paper/claims.yaml`（见 A5 的 W1），正文中每段都标注所依据的编号。主张用 CL 编号，避免与编辑器名 C1、C3 混淆。

| 编号 | 主张 | 证据 | 关键数字 | 性质 |
| --- | --- | --- | --- | --- |
| CL1 | 单步解码正确 ≠ 可组合 | v1 E1；v2 G2-0；v5 G5-0 | CE 编辑器（C1）R\_1 ≈ 1、R\_2 = 0；RRR-16 的 R\_2N = 1 | 确认 |
| CL2 | CE 编辑器写的是指令，不是状态 | v2 M1–M3；v5 L3 | 不同源状态之间的写入余弦中位数 0.986，与规范写入的余弦 0.003，探针读出源状态 1.0；66/66 个 CE 格子 D = 1、R\_2N = 0；第 1 步后槽位读出仍是起点（抽查的两个编辑器都是 160/160） | 确认 |
| CL2b | 解码器原生会做的运算写相对指令，否则写目标 token | v3 N（乱序映射与 skip2 以"绝对"为主）；v4 P5 | BART 只有 weekday/month 以相对类为主，T5Gemma 三个域都是相对类 | 探索 |
| CL3 | 只用解码器监督，展开训练只学到计步捷径 | v4 U（BART）；v5 L4（T5Gemma） | 视野内几乎完美，过视野 1–2 步崩溃；C1-U4 的 R\_2N 全为 0；compass（N = 4）的视野正好一整圈，R\_N = 1.0 而 R\_2N = 0 | 确认 |
| CL4 | 加上状态监督就可组合 | v4 U 的 C3-U4；v5 L4；v4 P2；v5 L\_new | C3-U4 两个骨干的 R\_2N 都为 1.0；BART month 上，v1 C3（600 次更新）与 L2-600 失败，C3n1200、C3-6000、L2-6000 都可组合 | C3-U4 确认；训练步数的部分为探索 |
| CL5 | 低秩编辑的秩阈值，以及冻结平面的特征 | v2 R1/R2；v3 HS1–HS3；v4 V1、V2a | r\* = N − 1；只冻结基频时单向失败、交替保持、t = N 复活；V1、V2a 都是 8/8 | 确认 |
| CL6 | 读出是多尺度的最近状态 | v3 HV1；v4 V4 | 读出一致率：拟合 0.945/0.937，等权 0.913/0.918，只用基频 0.555/0.526；基频的票数份额随位移上升 | 确认；"多尺度"的解读为探索 |
| CL7 | 谱：基频的一步变化最小 | v3、v4 的 V0 | s\_1 最小 13/13；a\_1 最大，例外是 Z4 与 compass8 的奇偶模式（正方向 vs 斜方向） | s\_1 确认，a\_1 部分 |
| CL8 | 不解码就能预测可组合性 | v5 L1、L2、L\_new | 逐 world 一致率 0.922/0.959，朴素判断 0.583/0.639；类别准确率 0.889/0.915；新编辑器 0.982/0.976 | 确认 |
| CL8b | 等权读出也够用，不需要解码器标定 | v6 P1 复现对话中的事后分析 | 逐 world：等权 0.897/0.945，拟合 0.931/0.959，只用基频 0.736/0.695；类别：等权 0.858/0.903，拟合 0.892/0.913（口径：全部非 CE 格子，含新编辑器，288/207 格） | 探索 |
| CL9 | 第 1 步分歧率可以识别指令捷径 | v5 L3 | CE 与状态监督两类完全分开（66 对 82） | 确认 |
| CL10 | 基频优先的秩分配 | v5 F1；v4 R（探索） | T5Gemma 4/4 格从 0–0.61 升到 1.0；BART 只有部分改善 | T5Gemma 确认 |
| CL11 | 对称不是必要条件 | v2 A1–A3；v4 S1 | 10 个乱序映射的 RRR-16 都可组合；长程上自然映射不占优（v2 A3 四个循环域差值为 0，v4 Q13 month 为 −0.13）；但乱序映射的秩阈值可以更高（month σ\_max 的 r\* = 16） | 确认 |
| CL12 | 理想化预测会失败，原因是累积漂移加读出余量 | v4 V3、V2b；v5 D；v6 P1 | 去耦后 43/58 格的 R\_2N 明显上升；在去耦链的真实潜变量上，逐步读出一致率 0.83–0.99，逐 world 0.927，类别 130/144 | 现象确认，解释为探索 |
| CL13 | 绑定类编辑 | v3 B′；v4 X；v5 B；v6 K | 逐 token 编辑器做不了；展开 L2 训练使 R\_6 达到 0.80，但只在训练视野内有效 | 部分确认，待 v6 |
| CL14 | 多句式语境 | v6 M | — | 待 v6 |

## A3. 论文结构（正文约 8 页 + 附录）

1. **引言**（约 1 页）
   - 问题：多步潜空间编辑；为什么"单步解码正确"不够。
   - 贡献四条：现象；两类机制；不解码预测与第 1 步探测；适用边界。
   - 图 1。
2. **相关工作**（0.5–0.75 页）：见 A7。
3. **设置**（约 1 页）
   - 冻结的 BART-base 与 T5Gemma-2B-2B。
   - 循环属性域与绑定域。
   - 编辑器：闭式 RRR、FF、C1、C3、展开变体、注意力编辑器。
   - 指标：R\_k、A\_t、交替路径、复活、D。
   - 预注册协议：锁定、闸门、world 级 bootstrap。正文只写半段，细节放附录。
4. **单步正确不等于可组合**（约 0.75 页）：CL1。主表覆盖两个骨干的多个域。
5. **写入了什么：指令与状态**（约 1 页）：CL2、CL2b（标注为探索）、CL3、CL4。
6. **保住了什么：槽位的傅里叶编码**（约 1.5 页）
   - 谱：CL7。
   - 秩阈值与冻结平面：CL5。
   - 多尺度读出：CL6。
   - 最小二乘先丢基频，以及基频优先的修正：CL10。
7. **不解码预测可组合性**（约 1 页）
   - 预测器：CL8、CL8b。
   - 对照：朴素判断，以及每格多数类参照。
   - 第 1 步探测：CL9。
   - 失败模式：CL12；未收敛编辑器的上下文漂移（v6 C）。
8. **适用边界**（约 0.5 页）：CL11、CL13、CL14；只有两个骨干；合成域。
9. **结论**
10. **附录**
    - A：预注册协议与全部预测，包括失败、混合与不可评的预测。
    - B：偏差记录。
    - C：补充图。
    - D：实现细节。
    - E：数据与句式。
    - F：复现说明。

## A4. 图表清单

| 编号 | 内容 | 来源 |
| --- | --- | --- |
| 图 1 | (a) 示意：单步解码正确 vs 可组合。(b) month 上 C1、RRR-16、C3-U4 的 R\_k 曲线 | v2/v4/v5 |
| 图 2 | (a) 秩不足的 RRR 的逐步 A\_t：复活与交替保持。(b) F{1} 与 F¬1 的镜像曲线（两个骨干） | v2 分片；v4 V |
| 图 3 | (a) a\_k 与 s\_k 的谱。(b) 各平面票数份额随位移的变化 | v3/v4 |
| 图 4 | FF-r 与 RRR-r 的 R\_2N 随秩的变化：T5Gemma 为确认、BART 为探索 | v4 R；v5 F |
| 图 5 | (a) 展开 CE 的视野崩溃。(b) D 对 R\_2N 的散点 | v4 U；v5 L |
| 图 6 | 潜空间预测对观测的散点，并画出朴素判断、等权读出与每格多数类作对照 | v5 L；v6 P1 |
| 附录图 | 去耦冻结与标准冻结的曲线；绑定的 R\_k；多句式结果 | v5 D、B；v6 |
| 表 1 | 两个骨干的主结果汇总 | 各轮 |
| 表 2 | 各轮预注册预测的计数：确认、失败、混合、不可评 | 各轮 `predictions.json` |
| 附录表 | 全部预测逐条列出 | 同上 |

## A5. 分工与流程

**Claude Code（W 单元，只用 CPU，在 `paper/composability` 分支上做）**：
- **W1 主张账本**：`paper/claims.yaml`。按 A2 的表，每条写明：证据文件路径、预测编号、锁定提交、数值与 CI、性质。由脚本从各轮的 `predictions.json` 与 `protocol.json` 读出数值，不手抄。
- **W2 数字宏**：生成 `paper/generated/numbers.tex`，正文中所有数字都通过宏引用（例如 `\LoneBartAgree`）。
- **W3 图**：`paper/figs/make_*.py` 只从锁定的结果和分片作图，不做新计算；输出 PDF（矢量），图例完整，两个骨干的配色固定。
- **W4 预测总表**：从 v1–v6 的全部预测生成附录总表与表 2，包括失败、混合和不可评的条目。
- **W5 LaTeX 骨架**：`paper/main.tex`，章节按 A3，先用中性模板。
- **W6 初稿**：
  - 起草 §3–§7 与附录 A、B、D、E、F。只使用账本中的主张，数字只用宏；每段末尾以注释标注账本编号。探索性内容必须写明"exploratory"。
  - 引言、相关工作、讨论不由 Claude Code 起草。
- **W7 复现说明**：`paper/REPRODUCE.md`，写明每张图、每个表格对应的命令与输入哈希。
- **W8 一致性检查**：`paper/check.py`。检查正文用到的宏都存在、每个账本编号都存在、标为"确认"的主张都有锁定预测作支撑。

**负责人（与 Claude 在对话中合作）**：
- 引言、相关工作、讨论、标题与摘要；
- 决定投稿会议；
- 确认 A1 中关于动机的写法。

**对抗审稿**：第一版全文完成后，在一个全新的 Claude Code 会话里，只给它草稿和账本，要求列出：
- 夸大的主张；
- 缺失的对照或基线；
- 定义不清的地方；
- 读者最可能质疑的三点。

回应记录在 `paper/REVIEW_LOG.md`，逐条修改或说明理由。

## A6. 写作规范
- 数字只从 `numbers.tex` 引用。v6 未完成之前，相关位置用 `\TODO{v6}` 占位。
- 探索性结果只出现在正文的专门段落或附录，不进摘要。
- 失败与混合的预测在附录总表中全部列出。正文要正面交代以下几项：
  - 理想化预测的失败（CL12）；
  - 绑定（CL13）；
  - 多句式（CL14）；
  - 历次计划中的检验设计缺陷（如 v4 的 HS4、R1），这部分写进附录 A。
- 不写"对称导致可组合"。对称论文只用于解释谱（CL7），并写明平移对称被打破时的例外。
- 术语统一，在 `paper/glossary.md` 中维护中英文对照。核心词：decodable、composable、instruction write、state write、slot、harmonic plane、fundamental、frozen plane、revival、readout、drift、margin。

## A7. 相关工作（候选，引用前必须逐条核实出处与年份）
- 激活或表示层面的引导与编辑：Turner et al.（Activation Addition）；Zou et al.（Representation Engineering）；Li et al.（Inference-Time Intervention）；Tan et al.（steering vector 的泛化与可靠性）。
- 模型编辑与连续编辑：Meng et al.（ROME、MEMIT）；Gupta et al.（大规模编辑导致的逐步与灾难性遗忘）。
- 循环与傅里叶表示：
  - Engels et al.（星期与月份的环形特征）；Nanda et al.（grokking 中的傅里叶特征）；Zhong et al.（The Clock and the Pizza）；Gurnee & Tegmark（时空表示）。
  - Karkada, Korchinski, Nava, Wyart, Bahri 2026：arXiv 2602.15029（已核实）。ICML 2026 版的题目为 *Symmetries in language statistics shape the geometry of model representations*，引用以会议版为准。
  - 同方向的后续：Storan, Tolias, Miolane，*Group-Invariant Statistics Determine Embedding Geometry*（arXiv 2610.00647），把平移对称推广到一般群；Modell et al. 2025（表示流形的起源）。
  - Wurgaft et al. 2026（流形引导）。
- 线性表示假设：Park et al.
- 捷径学习：Geirhos et al.
- 多尺度编码的类比：Fiete 等人关于网格细胞的工作（多尺度相位编码与纠错）。只作类比，不作主张。
- 骨干：Lewis et al.（BART）；T5Gemma 的技术报告。

由 Claude Code 用文献检索工具核实，生成 `paper/refs.bib`，无法核实的条目删除。

## A8. 时间表（按 2–3 周安排，按截稿日倒排调整）

| 时间 | A 线 | B 线 |
| --- | --- | --- |
| 第 1 周 | W1–W5；负责人起草引言与贡献 | v6 锁定前的全部步骤与锁定 |
| 第 2 周 | W6 初稿；相关工作；图定稿 | v6 锁定后的运行与报告 |
| 第 3 周 | 并入 v6；对抗审稿与修改；W7、W8；按会议模板排版 | — |

---

# B 线：v6 实验（`composability_mechanisms_v5`）

## B0. 要回答的问题

| 问题 | 竞争假设 | 检验 |
| --- | --- | --- |
| Q18′ 机制能否推广到未见过的句式 | **H-general**：以槽位为中心的算子在留出句式上可组合，冻结特征、潜空间预测与 D 探测都成立。**H-template**：只在训练句式上成立 | M |
| Q19 预测器加上下文项能否修正未收敛 C3 的误判 | **H-context**：误判来自非槽位位置的漂移，加上下文读出后显著改善。**H-slot**：加上下文项也不改善 | C |
| Q17′ bind3 为什么只在训练视野内有效 | **H-representable**（oracle 路由下可以超出视野组合）对 **H-unrepresentable**；**H-closure**（两层注意力能学会两跳指针，超出视野组合）对 **H-horizon**（有效步数随训练视野而定） | K |

## B1. 执行规则

### 沿用 v5
- **提交方式**：全部计算用 `sbatch` 提交，作业内用 `srun` 启动；登录节点只做 git 与查询；入口脚本调用 `require_slurm()`。
- **GPU 并发**：
  - 本人名下同时使用的 GPU 不超过 2 张，其他项目的作业也计入；每个 GPU 作业只申请 `--gres=gpu:1`。
  - A 通道跑 BART，B 通道跑 T5Gemma，同一通道内严格串行。
  - 首个作业提交前运行 `gpu_guard.sh`；依赖只写 `sbatch --parsable` 返回的真实 job ID。
  - 本人另有 GPU 作业时只开一条通道。
- **模板与分区**：沿用 v5 的 `job_gpu.slurm`、`job_cpu.slurm`、`gpu_guard.sh`、`ledger.sh`、`lib5.py`（复制为 `lib6.py`）。作业名 `compmech5`，日志路径改为 v6 目录；T5Gemma 用 `--mem=96G`。先查 `sinfo`，默认 `B300q`。
- **预算**：v6 的 GPU 上限 12 小时，到 9 小时先报告。预计 6–9 小时。A 线只用 CPU，不计入。
- **冻结**：骨干、revision、seed 同 v5。
- **提交**：每个编号单元完成后提交并推送，提交信息为 `compmech5: <编号> <一句话结果>`；`local/` 不入库。
- **偏差**：一律写入 `DEVIATIONS.md`。锁定后不改预测、阈值与规则，需要时新建 AMENDMENT。
- **标准步骤**：重建闸门、合成自检、冒烟测试（只用 dev）、文本级去重（对全部历史渲染，包括 confirm5 与 confirm5-mt）、区分力预检、world 级 cluster bootstrap、confirm6 锁定前可编码但不得解码。

### 新增
1. **多句式一律用以槽位为中心的算子。** 全序列 RRR 只作参照，不参与判定。
2. **凡是会用到的编辑器，全部在锁定前训练完毕。** 包括 M 的 C1 与槽位 C3-U4、C 的新 C3、K 的全部编辑器。
3. **带 oracle 的编辑器**（K 的 oracle 路由）在报告和论文中一律标为诊断，不作为可用方法。
4. **A 线只读取锁定结果。** 若写作中发现实验结果有错，回到 B 线以 ERRATUM 或 AMENDMENT 处理，不在 `paper/` 里改数。

## B2. 复用与新建

| 用途 | 来源 |
| --- | --- |
| 共享库 | v5 的 `lib5.py`，复制为 `lib6.py` 后扩展 |
| 多句式的句式、训练/留出划分、train/dev world 与编码 | v5 的 `data/templates_mt.json` 与划分（20 个训练句式 / 9 个留出句式）；v5 的 train/dev 编码 |
| 循环域的标定与基算子 | v3/v4 的 `calib_*.json`；v4 的 `gates_*.json` |
| 状态监督类编辑器（C 单元） | v1 C3；v3 C3-l3、C3-l10、C3-rrrinit；v4 P2a（C3-6000）、P2b（L2-600）、P2c（L2-6000）、C3-U4；v5 C3n1200、C3n2400 |
| 绑定编辑器与数据 | v5 B 的 Tok-U、Att1-U、Att2-U；v4 X 的 train（480）与 dev（64） |

新建脚本：`p_posthoc6.py`、`d_make_data.py`、`d_audit.py`、`d_encode.py`、`gates.py`、`calib_mt.py`、`calib_ctx.py`、`train_new.py`、`simulate.py`、`selftest.py`、`smoke.py`、`lock.py`、`m_chains.py`、`c_chains.py`、`k_chains.py`、`analyze.py`。

## B3. P：复现事后分析（探索性，锁定前，CPU）
结果写入 `results/patch/`，并作为探索性条目进入 A 线的账本（CL8b、CL12）。
- **P0**：清单与哈希（v1–v5 的输入）。
- **P1a**：用 v5 的 L 分片，计算等权读出与只用基频读出的逐 world 一致率和类别准确率，分别按两种口径：报告口径（243/201 格），以及全部非 CE 格子（含新编辑器，288/207 格）。对话中的事后分析（后一种口径）得到：
  - 逐 world：拟合 0.931/0.959，等权 0.897/0.945，只用基频 0.736/0.695，朴素 0.630/0.641；
  - 类别：拟合 0.892/0.913，等权 0.858/0.903，只用基频 0.615/0.599。
- **P1b**：v5 L 的每格多数类参照：每个 world 都预测为该格观测中占多数的结果。它用到了观测，是任何格子级预测器的上限；潜空间预测器要超过它，才能说明逐 world 的预测有格子以外的信息。
- **P1c**：在 v5 D 的分片上，计算去耦链真实潜变量的读出一致率。对话中的事后分析得到：逐步一致率（拟合）0.83–0.99，逐 world 0.927，类别 130/144。
- **P1d**：BART month 上未收敛的状态监督编辑器（v1 C3、v3 C3-l3/l10、v4 P2b，各 3 个 seed）首次失败的类型。对话中的事后分析得到：
  - plus 路径上，首次失败全部是"错成另一个状态"，没有不可解析的输出；
  - 在首次失败那一步，槽位读出仍正确的 world 为 103–158 个（失败的 world 为 128–160 个）；
  - minus 与交替路径上这个比例低得多（31–144 个），交替路径还有少量不可解析的输出。

数字与上面不一致时，记录差异与原因，但不阻塞锁定。

## B4. 数据与闸门

### confirm6（全新，文本级去重）

| 单元 | 域 | 句式 | world 数 | 骨干 |
| --- | --- | --- | --- | --- |
| M | weekday-mt、month-mt、hour-mt | v5 的 9 个留出句式 | 各 160 | BART |
| M | month-mt | 同上 | 160 | T5Gemma |
| C | weekday、month | 模板 0 | 各 160 | BART |
| K | bind3、name3 | 模板 3 | 各 160 | BART |
| K | bind3fix | 模板 3 | 沿用 v4/v5 的 71 个评测 world（组合空间已用尽，v5 新生成数为 0，见 v5 DEVIATIONS #3）；报告中标明不是全新数据 | BART |

### 锁定前闸门
- **GM（多句式的基算子，在训练句式的 dev 上）**：按顺序尝试 S-RRR-16、S-RRR-32、E\_all（附录 A.1、A.2），取第一个同时满足"单步 ≥ 0.95"与"单向 plus R\_2N ≥ 0.95"的作为该（骨干，域）的基算子。都不满足，则该域退出 M 并报告。同时记录全序列 RRR-16 的单步成功率作参照（v5 为 0.69）。
- **准入**：
  - 单步编辑器：dev 单步 ≥ 0.90；
  - 展开编辑器：dev 视野内 ≥ 0.90；
  - K 的编辑器：name3 与 bind3fix 的 dev 单步 ≥ 0.95。
  - 不满足就用两倍更新重训一次，仍不满足则记为"学不会"并报告。

### 锁定后健全性闸门 G6-0
- M 的每个保留域：基算子在**训练句式**的 dev 上复核单向 R\_2N ≥ 0.95；
- C：基算子 RRR-16 在 confirm6 上单向 R\_2N ≥ 0.95；
- K：name3 上 Tok-U 的 R\_6 ≥ 0.95。

不通过即停止排查。

## B5. M：多句式（Q18′，核心）

### 条件
- **基算子**：由 GM 选定，只作用于槽位。
- **冻结手术**：F∅、F{1}、F¬1，以及全部 F{j}（j ≥ 2）。平面由训练句式的槽位表示合并估计（附录 A.2）。
- **编辑器**：
  - C1（全序列，600 次更新，seed 42/43/44）；
  - 槽位 C3-U4（只作用于槽位，展开 CE 加槽位上的规范 L2，S ≤ 4，1200 次更新，seed 42/43/44；只做 BART）。
- **参照**：全序列 RRR-16；reencode。
- **标定**：在训练句式的 dev 上，用 v3 的平面替换程序重新标定投票模型（两个骨干）。
- **路径**：plus、minus、交替，各 2N 步。成功的判定用精确匹配（v5 附录 A.6）。
- **锁定前**：在留出句式的 confirm6 编码上，按真实动力学算出全部条件的潜空间预测，逐 world 写入协议。对 M3 做预检：模型自己预测落在阈值另一侧的格子，在锁定时排除并记录。

### 预测（全部在留出句式上）

| 编号 | 量 | H-general | H-template |
| --- | --- | --- | --- |
| M1 | 基算子的单向 plus R\_2N，每个（骨干，域） | ≥ 0.90 | ≤ 0.50 |
| M2 | C1：R\_1、R\_2、D（seed 中位数） | R\_1 ≥ 0.90、R\_2 ≤ 0.20、D ≥ 0.8 | R\_1 ≤ 0.50 |
| M3 | F{1}：单向 plus R\_2N ≤ 0.20，交替 R\_2N ≥ 0.80，且 A(1) − A(⌊N/2⌋) ≥ 0.50 | 全部可评格子成立 | — |
| M4 | 状态监督类（基算子、手术、槽位 C3-U4）的潜空间预测 | 逐 world 一致率 ≥ 0.85，且相对朴素判断的提升 CI 下界 > 0；类别准确率 ≥ 0.80 | 一致率 < 0.75 |
| M5 | D 探测：CE 格子 D ≥ 0.5 且 R\_2N ≤ 0.20；状态监督格子 D ≤ 0.20 | ≥ 90% 的格子成立 | — |

- **判定**：M1、M3、M4 都成立为 H-general；M1 在至少 2/3 个 BART 域上符合 H-template，则为 H-template；其他为混合。若预检后 M3 没有可评格子，按 M1 与 M4 判定，并在报告中注明。
- **探索性**：
  - 槽位 C3-U4 的 R\_2N；
  - 含干扰词句式的单独结果（干扰词保留率）；
  - 各句式平面之间的主角度；
  - 全序列 RRR 与槽位算子的对比。

## B6. C：预测器的上下文项（Q19，BART，核心）

### 条件
- **域**：weekday、month（模板 0，confirm6）。
- **编辑器**：
  - 已有的未收敛状态监督编辑器：v1 C3、v3 C3-l3 与 C3-l10、v4 P2b（L2-600），都在 BART month 上（v5 L 在 12 个这样的格子里预测 partial、观测 fail）。v1 C3 另有 weekday 版本，v5 没有评测；若它的数据定义（句式、槽位位置）与 v6 的 weekday 一致就纳入，否则不用，并记录原因。
  - 新训的 C3（λ = 1）：300、450、600、900 次更新，weekday 与 month 各 3 个 seed。它们事先不知道会不会收敛，是前瞻部分。
  - 非劣检验集：
    - 基算子手术：F∅、F{1}、F¬1、F{j}；
    - 秩网格：RRR-r、FF-r，r ∈ {N − 4, N − 3, N − 2}；
    - 已收敛的状态监督编辑器：v3 C3-rrrinit、v4 P2a（C3-6000）、P2c（L2-6000）、C3-U4，以及 v5 的 C3n1200、C3n2400。
- **"未收敛"**：dev L2 > 1.2 倍 RRR-16 的 dev L2。锁定前判定并写入协议。

### 上下文读出（附录 A.3）
- 在槽位得分之外，加上非槽位位置的最近状态距离，用 λ\_ctx 加权。
- λ\_ctx 用 dev 上的"上下文替换探针"标定：槽位保持状态 x、上下文换成 x + m，以及反过来的补集型。
- 槽位部分沿用 v5 锁定的投票模型（v5 `protocol.json` 的 `vote_models`），λ\_k 不重新拟合。

### 预测

| 编号 | 量 | H-context | H-slot |
| --- | --- | --- | --- |
| CT1 | 未收敛 C3 系格子：槽位+上下文预测器的类别准确率，以及逐 world 一致率相对只看槽位的提升 | 类别 ≥ 0.80，且提升的 CI 下界 > 0 | 提升的 CI 含 0 |
| CT2 | 非劣检验集：槽位+上下文 − 只看槽位的逐 world 一致率 | 下降 ≤ 0.01，且 CI 下界 > −0.02 | — |

- **判定**：CT1 与 CT2 都成立为 H-context。
- **探索性**：失败世界中，槽位与上下文各自的读出谁先出错；新 C3 的训练步数与可组合性的关系。

## B7. K：绑定的闭合性（Q17′，BART，核心）

### 编辑器
全部用展开 L2 训练，seed 42/43/44，结构见附录 A.4、A.5：
- **OR-U4**（oracle 路由，诊断用）：注意力固定指向名单中"下一个名字"的位置，只训练取值与输出映射和逐 token 低秩部分；S ≤ 4，4000 次更新。
- **Att2L-U4**、**Att2L-U8**：两层注意力编辑器，能做"先找当前名字、再取下一个"的两跳查找；分别用 S ≤ 4（4000 次更新）与 S ≤ 8（8000 次更新）。
- **Att1-U8**：v5 Att1-U 的结构，改为 S ≤ 8，8000 次更新。
- **参照**：v5 的 Att1-U、Att2-U（S ≤ 4）；Tok-U。

### 链
confirm6 上，plus 30 步，minus 与交替各 12 步。

### 预测（bind3，seed 中位数）

| 编号 | 量 | 支持方 | 对立方 |
| --- | --- | --- | --- |
| K1 | OR-U4 的单向 R\_30 | H-representable：≥ 0.90 | H-unrepresentable：≤ 0.50 |
| K2 | max(Att2L-U4, Att2L-U8) 的单向 R\_30 | H-closure：≥ 0.90 | H-horizon：Att2L-U4 的 R\_8 ≤ 0.50，且 Att2L-U8 的 R\_12 ≤ 0.50 |
| K3 | Att1-U8：R\_8 与 R\_12 | H-horizon：R\_8 ≥ 0.70 且 R\_12 ≤ 0.50 | H-closure：R\_30 ≥ 0.90 |
| K4 | name3、bind3fix 上各编辑器的 R\_30 | ≥ 0.95（稳定性） | ≤ 0.50 |

- **读法**：
  - K1 成立、K2 不成立：表示上可以做到，问题在学会路由。
  - K1 不成立：取值映射或表示本身有限制。
  - K3 符合 H-horizon：有效步数跟着训练视野走，这与"缺少闭合的实现"一致。
- **探索性**：第 2 层落在第 j + 1 个名字上的注意力权重；失败输出的类型。

## B8. 锁定

1. 依次完成以下步骤：
   - P；
   - 数据与审计；
   - 合成自检；
   - 编码（含 confirm6，但不解码）；
   - GM 与准入；
   - 多句式标定与上下文标定；
   - 全部编辑器的训练；
   - `simulate.py` 的全部预测；
   - M3 的预检；
   - 冒烟测试。
2. `lock.py` 写 `protocol.json`，内容包括：
   - 本文 B 线的全部预测、阈值与判定规则；
   - 逐 world 的预测（SHA256）；
   - 基算子的选择、准入结果、未收敛名单；
   - 闸门结果与被剔除的组合；
   - 数据与源码的哈希。
3. `lock.py` 断言：
   - 不存在任何 confirm6 的解码输出；
   - 冒烟测试的产物只在 `local/smoke/`。
4. 提交并推送，记录哈希，并把锁定提交写入 A 线账本。

## B9. 作业编排

| 阶段 | 作业（按顺序） | 资源 | `--time` | 依赖 | 通道 |
| --- | --- | --- | --- | --- | --- |
| P | `p_posthoc6` | CPU | 02:00 | — | — |
| D | `d_make_data` → `d_audit` → `selftest` | CPU | 01:30 | — | — |
| 锁定前（A） | `encode_bart` → `gates_bart`（GM、准入）→ `calib_bart`（多句式与上下文）→ `train_new_bart`（M、C、K）→ `simulate_bart` → `smoke_bart` | 1 GPU | 01:00 → 01:30 → 01:30 → 03:00 → 01:00 → 01:00 | d\_audit、selftest | A |
| 锁定前（B） | `encode_t5` → `gates_t5` → `calib_t5`（month-mt）→ `train_new_t5`（多句式 C1）→ `simulate_t5` → `smoke_t5` | 1 GPU，96G | 01:00 → 01:30 → 01:30 → 01:30 → 00:45 → 00:45 | d\_audit、selftest | B |
| L | `lock` | CPU | 00:15 | 以上全部 | — |
| 主体（A） | `g60_bart` → `m_chains_bart` → `c_chains` → `k_chains` | 1 GPU | 00:45 → 02:00 → 01:30 → 01:30 | lock | A |
| 主体（B） | `g60_t5` → `m_chains_t5` | 1 GPU，96G | 00:45 → 02:00 | lock | B |
| 汇总 | `analyze` 与报告 | CPU | 01:30 | 全部 | — |

- 预计 6–9 GPU 小时，墙钟约 1.5–2 天。
- **只能开一条通道时的顺序**：锁定前（A）→ 锁定前（B）→ lock → M（BART）→ M（T5Gemma）→ C → K。
- **停止规则**：G6-0 不通过；同一作业因不明原因失败两次；发现泄漏；达到预算上限。

## B10. 输出与报告
- 目录结构同 v5，`REPORT.md` 用中文，结构同 v5 的 §13。
- 额外产出一个 `results/paper_export.json`：v6 所有预测的数值与 CI，格式与 A 线 W1 一致，供论文直接读取。

## B11. 结果如何进入论文

| 结果 | 论文中的写法 |
| --- | --- |
| Q18′ 为 H-general | §8 写"以槽位为中心的算子在未见过的句式上同样成立"；图放附录，表 1 加一行 |
| Q18′ 为 H-template | §8 明确写结论只在固定句式上成立，并给出单步精度的数据 |
| Q19 为 H-context | §7 的预测器改为"槽位 + 上下文"，未收敛编辑器的误判作为已修正的失败模式 |
| Q19 为 H-slot | §7 保留只看槽位的版本，把误判写成已知限制 |
| Q17′：K1 成立、K2 不成立 | §8：绑定在表示上可以做到，难点在学会路由 |
| Q17′：K2 成立 | §8：两层注意力加多步规范监督可以组合绑定类编辑，这可以成为一个正面结果 |
| Q17′：K3 为 H-horizon | §8：有效步数跟着训练视野走，与"缺少闭合的实现"一致 |

---

## 附录 A：v6 的定义

### A.1 槽位 RRR（S-RRR-r）
- 只用槽位 token 的 (源, 目标) 对拟合，来自训练句式的全部 train world 与全部转换。
- 拟合程序同 `lib5.fit_rrr4`：相对 ridge 网格 {1e-4, 1e-3, 1e-2, 1e-1}，在 train world 的内部划分上逐秩选择，再在全部 train 上重拟合；降到秩 r，带偏置。
- 只作用于槽位位置，其他位置不变。plus 与 minus 分别拟合。

### A.2 槽位平面编辑器（E\_all）与合并平面
1. 先对每个（world，句式）在状态之间去均值，再对全部训练句式的 world 取平均，得到 c̄(x)。
2. 平面构造同 v3 的附录 A.1。
3. E\_all 只改槽位在全部平面张成的子空间（维数 N − 1）内的分量：对这些坐标做联合最小二乘，加偏置；正交补不变，其他位置也不变。
4. 冻结手术定义同 v3。

### A.3 上下文读出
1. 上下文位置：除槽位外的全部非 pad 位置。
2. 上下文子空间 Q\_ctx：对训练集上各上下文位置在状态之间去均值的表示，合并后做 PCA，取前 N − 1 个主成分。
3. d\_ctx(h, y) = 各上下文位置 ‖Q\_ctxᵀ(h\_i − E\_w(y)\_i)‖² 的平均。
4. 合并得分 S(y) = −Σ\_k λ\_k d\_k(槽位, y) − λ\_ctx d\_ctx(h, y)。λ\_k 固定，λ\_ctx 用上下文替换探针做最大似然拟合。

### A.4 两层注意力编辑器（Att2L）
1. 第 1 层：z\_i = h\_i + W\_o1 Σ\_j α¹\_ij W\_v1 h\_j，其中 α¹ 由 W\_q1 h\_i 与 W\_k1 h\_j 计算。
2. 第 2 层：Δ\_i = b + U V h\_i + W\_o2 Σ\_j α²\_ij W\_v2 z\_j，其中 α² 由 W\_q2 z\_i 与 W\_k2 z\_j 计算。
3. 各头维数 64；W\_o1、W\_o2 零初始化；U V 的秩为 32。

### A.5 oracle 路由编辑器（OR）
1. 槽位：Δ\_slot = b + U V h\_slot + W\_o W\_v h\_{π(j\*+1)}。π(k) 是名单中第 k 个参与者所在的位置，j\* 是该步输入的金标准索引。
2. 其他位置：Δ\_i = b + U V h\_i。
3. 只训练 W\_v、W\_o、U、V、b。这是诊断工具，不是可用的编辑器。

### A.6 展开 L2（S ≤ 8）
同 v5 的附录 A.4，只是 S 从 {1, …, 8} 中均匀抽取，更新次数加倍。

### A.7 计分
同 v5：
- R\_k、A\_t、D、逐 world 一致率、类别准确率；
- 多句式用精确匹配；
- world 级 cluster bootstrap（2000 次，种子 3101）。

### A.8 合成自检（锁定前必须通过）
1. S-RRR 与 E\_all 在合成的多句式数据上（槽位 = 共享的循环编码加句式偏移），能恢复出精确的旋转。
2. 上下文读出：在合成数据上，从上下文替换探针恢复出已知的 λ\_ctx，误差 < 0.05。
3. Att2L：在两跳的合成指针任务上（先找当前、再取下一个），留出相对 L2 ≤ 0.05，而单层编辑器 ≥ 0.5。
4. OR 编辑器：在合成指针任务上，留出相对 L2 ≤ 0.01。
5. 展开 L2：S = 1 时与单步 L2 完全一致。

---

## 附录 B：`paper/` 目录

```text
paper/
  PLAN.md  claims.yaml  claim_map.yaml  glossary.md  REVIEW_LOG.md  REPRODUCE.md
  main.tex  sections/*.tex  refs.bib
  generated/numbers.tex  generated/tables/*.tex
  figs/make_*.py  figs/*.pdf
  check.py
```

- `claim_map.yaml` 由负责人维护：每条主张对应哪些预测编号、哪些图。
- `claims.yaml` 由脚本生成：数值、CI、锁定提交。
- `check.py` 在每次提交前运行，不通过则不得提交。
