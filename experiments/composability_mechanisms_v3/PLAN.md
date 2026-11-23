# ESEP 实验计划 v4：补丁轮，以及多尺度读出、秩分配修正、展开训练与绑定结构

- 实验名：`composability_mechanisms_v3`
- 项目：Encrypted Semantic Editing Pilot（ESEP）
- 日期：2026-11-23
- 分支：先在 `experiment/composability-mechanisms-v2` 上提交 v3 的 `ERRATUM_01.md`（§0.1），再从这次提交新建 `experiment/composability-mechanisms-v3`
- 目录：`experiments/composability_mechanisms_v3/`。把本文件存为该目录下的 `PLAN.md`，与代码一起提交。
- 上一轮：`experiments/composability_mechanisms_v2/`（`REPORT.md`、`results/`、`figs/`）

本轮分两部分：

- **P（补丁轮，探索性）**：修正 v3 中设计有缺陷的几项检验，并做诊断。不锁定；结果不能改变本文的任何预测、阈值或程序。
- **主体（确认性）**：V、R、U、X、S 五个单元。锁定后在全新的 confirm4 上检验。

---

## 0. 收尾（先做，不开 GPU）

### 0.1 v3 的 ERRATUM_01
- 在 v3 目录写 `ERRATUM_01.md`（全文见附录 B），单独提交并推送。它只更正报告中的事实陈述和解读，不改变任何锁定判定。
- v3 的 `REPORT.md` 只在 §1 开头加一行，指向该文件。

### 0.2 v1、v2 的去重说明
由 P3 生成，模板见附录 C。在各自分支的实验目录写 `NOTE_DEDUPE.md`，并在各自 `REPORT.md` 开头加一行指向它。其他内容不改。

---

## 1. 背景与问题

### 1.1 v3 留下的事实（按 ERRATUM_01 更正后的解读）
1. **冻结平面机制**（锁定，两个骨干）：在满秩算子上只冻结基频，单向链失败，交替链保持，单向链在 t = N 时复活。
2. **读出**（锁定）：
   - 在真实潜变量上，投票模型与实际解码的一致率为 BART 0.950、T5Gemma 0.944；等权模型为 0.897、0.895；只用基频为 0.602、0.460。
   - 从理想化状态出发的类别预测：单平面冻结时，plus 9/9，minus 8/9，交替链只有 4/9。month 冻结平面 5、6 时，交替链是逐步累积变坏的。
3. **多尺度**（事后分析）：
   - "只冻结基频"（F{1}）与"只让基频转动"（F¬1）的逐步曲线互为镜像：F{1} 只在对径点附近出错，F¬1 只在对径点附近答对。两个骨干都是这样。
   - 按锁定的 λ 与一步距离（循环对称近似）估算，基频的票数份额随位移上升：weekday 从 0.14 升到 0.62，month 从 0.04 升到 0.56。
4. **秩**（事后分析）：
   - 一步变化 s_1 在 7/7 个（骨干，域）组合中最小；振幅 a_1 在 5/7 中最大，例外都是 Z4。
   - 一步最小二乘按 s_k 分配秩，所以先丢掉振幅最大、负责全局位置的基频。
5. **CE 编辑器写的是目标 token 指令，不是状态**：乱序映射与 skip2 的移植以"绝对"为主；自然映射下，weekday/month 在 v2 中以"相对"为主。
6. **绑定**：H-bind 成立。bind3 的 RRR 单步只有 0.45，C1 能做单步。
7. **T5Gemma**：
   - 机制复现。month 的秩阈值更高，r\* 在 13–16 之间。
   - 乱序 month 的 RRR-16 在 2N 步时就只有 0.51，单位模块缺 k = 1。目前没有证据表明，在两种映射都可组合的秩上存在长程对称效应。
8. **C3**：随机初始化的 C3 在第 600 步时规范 L2 仍在下降（0.19–0.20；RRR 初始化为 0.08–0.10），更像是没训够。
9. **数据泄漏**：v2 的 confirm2 有 2–12% 的 world 与 v1 train/dev 的文本完全相同。v1 自己有没有同样的问题还没查。

### 1.2 v3 设计上的教训（本轮的规则据此修改）
- HS4 没有预先检查各假设的预测是否不同；累计类别也不如逐步曲线有区分力。
- HV1 的 0.05 差值门槛是随意定的：BART 以 0.003 的余量通过，T5Gemma 以 0.001 之差未通过。
- T5 在固定的秩 16 上比较自然映射与乱序映射，把秩阈值和对称效应混在了一起。
- N1 的前提错了：余弦 0.97 仍留有约 23% 的源特异分量。
- S4 在 AdamW 下改 λ，几乎不改变优化轨迹。
- A3 用"k = 1 是否在单位模块中"做判定，太粗。

### 1.3 本轮问题

| 问题 | 竞争假设 | 决定性检验 |
| --- | --- | --- |
| Q9 读出是否为多尺度投票（新域，两个骨干） | **H-ms**：解码器按谐波平面加权投票，基频的份额随位移上升。**H-fund**：只看基频。**H-flat**：任一平面冲突就出错。**H-equal**：读出是多尺度的，但拟合权重相对等权模型没有额外作用 | V：新循环域上的冻结手术，按逐步正确率计分 |
| Q10 秩阈值是否来自最小二乘的秩分配 | **H-alloc**：强制保留基频后，在普通 RRR 失败的秩上就能组合。**H-capacity**：总容量不够，强制保留基频没用 | R：基频优先的约束 RRR |
| Q11 只用解码器监督，能否训出可组合的编辑器 | **H-state**：多步展开训练迫使 CE 写入状态，超出训练视野仍可组合。**H-shortcut**：只在训练视野内成功，或仍然只写指令 | U：展开 CE 训练 |
| Q12 绑定失败是否只源于逐 token 的结构 | **H-arch**：能跨 token 读取的编辑器可以组合 bind3。**H-deep**：能跨 token 读取也不够 | X：注意力式编辑器 |
| Q13 T5Gemma 在可组合的秩上有没有长程对称效应 | **H-slot**：没有。**H-longsym**：有 | S：RRR-32 上的 10N 步链 |

---

## 2. 给 Claude Code 的执行规则

### 沿用 v3
- **提交方式**：所有 Python 计算都用 `sbatch` 提交，作业内用 `srun` 启动。登录节点只做 git、文件读写和 `squeue`/`sinfo`/`sacct`。入口脚本开头调用 `require_slurm()`。
- **GPU 并发**：
  - 任何时刻，本人名下正在使用的 GPU 不超过 2 张，其他项目的作业也计入。每个 GPU 作业只申请 `--gres=gpu:1`。
  - 只开两条串行通道：**A 通道跑 BART，B 通道跑 T5Gemma**。同一通道内的作业严格串行。
  - 通道首个作业提交前运行 `gpu_guard.sh`。依赖只写 `sbatch --parsable` 返回的真实 job ID。
  - 本人若另有 GPU 作业在跑，就只开一条通道，按 §12 末尾的单通道顺序执行。
- **模板**：复制 v3 的 `job_gpu.slurm`、`job_cpu.slurm`、`gpu_guard.sh`、`ledger.sh`、`lib3.py`。作业名前缀改为 `compmech3-`，日志写到新目录的 `logs/`。T5Gemma 作业用 `--mem=96G`、`--cpus-per-task=8`。
- **分区**：先查 `sinfo`，默认用 `B300q`，避开 drain/down 节点。
- **预算**：P 与主体合计的 GPU 分配时间上限为 16 GPU 小时，用 `sacct` 记账并写入 `run_ledger.json`。到 12 小时先报告，到 16 小时立即停止。预计 7–11 小时。
- **冻结**：
  - BART-base revision `aadd2ab…`；T5Gemma `google/t5gemma-2b-2b-ul2-it` revision `6a196a58…`，按 `model_manifest.json` 校验 SHA256，用 bf16。
  - 编辑器为 float32，seed 固定为 42、43、44。RRR、FF-r 与 reencode 是确定性方法，不算作多个 seed。
- **提交**：每完成一个编号单元，提交一次并推送，提交信息为 `compmech3: <编号> <一句话结果>`。`local/` 不入库；超过 50 MB 的单个文件不入 git。
- **偏差**：任何与本文不同的做法都写入 `DEVIATIONS.md`，注明时间、原因、影响，以及发生在锁定前还是锁定后。
- **锁定后**不得修改预测、阈值或判定规则。负责人若要求修改，必须新建 `AMENDMENT_xx.md`；受影响的预测在报告里降为"探索性"，原判定照常报告。
- **重建闸门**：任何（骨干，域，模板）组合用于编辑之前，都要在 train+dev 上通过 reencode 单步成功率 ≥ 0.99。
- **合成自检**：新指标与新代码先过合成自检（附录 A.8），未通过不得锁定。

### 新增
1. **区分力预检**：
   - 每条确认性检验，锁定前列出各竞争假设在每个计分格子里的预测。
   - 只有至少两个假设预测不同的格子才计分（附录 A.6）。
   - 可计分格子少于本文规定的数量时，该检验在锁定时就标为"不可评"。
2. **模型之间的比较用置信区间，不用随意的差值门槛**。统一用以 world 为单位的 cluster bootstrap（附录 A.7）。
3. **比较两个条件前，两者都要先过各自的门槛**（例如两者都已可组合），否则记为不可评。
4. **冒烟测试是标准步骤**：锁定前只用 dev 数据，把锁定后每个作业的代码路径跑一遍。不编码或解码任何 confirm4 数据。
5. **文本级去重**：所有新 world 与仓库中全部实验的全部渲染文本去重，至少包括 `symmetry_composability_v1`、`composability_mechanisms_v1`、`composability_mechanisms_v2`、`four_domain_state_coverage_v1`。
6. **训练类操纵必须真正改变优化**：本轮改变的是训练步数、初始化和目标的步数视野，不再单独改损失权重。
7. 预测已在本文定稿。`protocol.json` 逐字复制本文的预测、阈值和判定规则。锁定前由 train/dev 计算的量（标定权重、派生类别、可计分格子、基算子的秩）按附录 A 的固定程序计算后写入 `protocol.json`。

---

## 3. 复用与新建

| 用途 | 来源 |
| --- | --- |
| 共享库：谐波平面、投票模型、手术、链式评测、RRR、训练 | v3 的 `lib3.py`。复制为 `lib4.py` 后扩展，不改 v3 原文件 |
| 语义与评测 | v3 的 `sym3_semantics.py`、`sym3_evaluator.py`。复制为 `sym4_*` 后新增 hour、compass8、season 三个域 |
| v3 的标定（weekday、month、compass；两个骨干） | v3 `results/calib_bart.json`、`calib_t5.json` |
| v1 的 C1、C3 权重；v3 的 C3 变体、T5Gemma 的 C1；各秩的 RRR 拟合 | v1–v3 的 `local/`，按 `inputs_manifest.json` 定位 |
| 后端 | `four_domain_state_coverage_v1/backend.py` 的 `Backend('bart')` 与 `Backend('t5gemma')` |
| 乱序置换表 | v2 `protocol.json` 的 `s1a.maps` |

新建文件，全部放在 `experiments/composability_mechanisms_v3/` 下：

- 脚本：`p_diag.py`（P0、P1、P3、P4）、`p_c3.py`（P2）、`p_transplant.py`（P5）、`p_dyn.py`（P6）、`d_make_data.py`、`d_audit.py`、`d_encode.py`、`gates.py`、`calib.py`、`prelock_fits.py`、`selftest.py`、`smoke.py`、`lock.py`、`v_chains.py`、`r_chains.py`、`u_run.py`、`x_run.py`、`s_long.py`、`analyze.py`。
- 记录文件：`protocol.json`、`inputs_manifest.json`、`DEVIATIONS.md`、`REPORT.md`、`run_ledger.json`。

---

## 4. P：补丁轮（探索性）

可与主体的锁定前步骤并行。结果写入 `results/patch/`，在锁定前提交。

- **P0 校验**：定位并哈希 v1–v3 的拟合、编辑器权重、编码缓存与分片，写入 `inputs_manifest.json`。
- **P1 T5Gemma 算子的逐平面诊断**（CPU）：对 v3 的 T5Gemma RRR（weekday、month；自然映射与 σ\_max；全部秩），计算逐平面的 ρ\_k、δ\_k、ε\_k（附录 A.2），与 v3 的单位模块结果和 R\_2N 对照。
- **P2 C3 的收敛性**（GPU，A 通道）：
  - 设置：month 与 daysago，seed 42/43/44，三种变体：
    - (a) C3（λ = 1），6000 次更新；
    - (b) 只用规范 L2，600 次更新；
    - (c) 只用规范 L2，6000 次更新。
  - 记录：每 50 次更新记一次 CE 与训练 L2，每 500 次记一次 dev L2。
  - 评测（confirm3）：month 的 R\_12 与 R\_24、daysago 的 R\_7、DRIFT、逐平面 ε\_k。
  - 预先写定的解读：
    - (a) 或 (c) 的 L2 降到 RRR-16 的 1.2 倍以内且可组合 → "没训够"；
    - L2 已收敛但仍不可组合 → "收敛到了不同的解"；
    - (c) 可组合而 (a) 不可组合 → CE 与规范写入存在冲突。
- **P3 去重**（CPU）：
  - 检查 v1 各 confirm 与 v1 train/dev 的文本重叠；v2 confirm2 与 v1 train/dev 的重叠（已知为 2–12%）。
  - 从分片重算 v1、v2 的关键数字（去掉重复的 world），按附录 C 写 `NOTE_DEDUPE.md`。
- **P4 逐平面判据**（CPU）：对 v3 的全部算子（BART/T5Gemma 各秩的 RRR，自然映射与 σ\_max；12 个 C3）计算 ε\_k。比较两种判据预测可组合（单向 R\_2N ≥ 0.90）的准确率与 AUC：
  - "所有平面 ε\_k ≤ 0.5"；
  - "k = 1 在单位模块中"。

  只报告，不能改变附录 A.2 的定义与阈值。
- **P5 移植分类**（GPU，两条通道各一个作业）：
  - BART 用 v1 的 C1（5 个域 × 3 个 seed），T5Gemma 用 v3 的 C1（3 个域 × 3 个 seed），在 confirm3 上做同一 world 内的移植。
  - 输出分为五类：相对、绝对、无效、其他、不可解析。
  - 要看的问题：自然映射下，相对类是否只在 weekday/month 占多数。
- **P6 动力学诊断**（GPU）：
  - 对象：v3 中理想化预测落空的条件，即 BART month F{4}、F{5}、F{6} 的交替链，以及 BART 与 T5Gemma month 的 E\_K\* plus 链。
  - 在 confirm3 上重算潜变量（不解码），逐步记录：
    - 各平面相对目标的相位差与幅度比；
    - 槽位在谐波张成之外的残差；
    - 上下文位置相对 E(目标) 的偏离。
  - 报告失败之前哪一项先增长。

---

## 5. 数据与闸门（D、G）

### 5.1 新循环域（模板 0，仿照 v1 的写法）

| 域 | N | 句式 | 状态（按循环顺序） |
| --- | --- | --- | --- |
| hour | 12 | `The {o} event starts at {X} o'clock. Its status is {st}. {fact}` | one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve |
| compass8 | 8 | `In {a}'s report, the {o} is on the {X} side. {fact}` | north, northeast, east, southeast, south, southwest, west, northwest |
| season | 4 | `The {o} event is held in {X}. Its status is {st}. {fact}` | spring, summer, autumn, winter |

- `{fact}` 与 v1 相同：`The {o} is {color}. There are {q} copies.`
- 负责人已用 GPT-2 BPE（与 BART 相同）确认：全部状态词带前导空格时都是单 token；`o'clock` 为固定的三个 token。Gemma 分词器由审计检查。
- 各域生成 train 96、dev 32、confirm4 160 个 world。

### 5.2 confirm4
- weekday、month、compass、hour、compass8、season 各 160 个新 world，用模板 0。
- bind3、bind3fix、name3 各 160 个新 world，用模板 3。
- 全部做文本级去重。

### 5.3 X 单元的训练集
- bind3、bind3fix、name3（模板 3）：train 480、dev 64 个新 world。注意力编辑器的参数更多，所以用更多数据。
- bind3fix 沿用 v3 的固定名单。

### 5.4 审计（`d_audit.py`，CPU）
沿用 v3 的七项，另加：
- 文本级去重；
- 新域在两个骨干下都是单 token，槽位位置在同一域的所有 world 上相同（模板 3 按 world 记录）。

### 5.5 锁定前闸门（GPU，只用 train+dev）

| 编号 | 内容 | 不通过时 |
| --- | --- | --- |
| GR | 每个（骨干，域，模板）的 reencode 单步 ≥ 0.99 | 该组合退出 |
| GT | 状态词单 token，槽位位置恒定（两个骨干） | 该组合退出 |
| GB（基算子） | 每个（骨干，V 的域）：RRR-16 在 dev 上单向 R\_2N ≥ 0.95，则基算子取 RRR-16；否则 RRR-32 满足即取 RRR-32；都不满足则该域退出 V 与 R | 见左 |

某个骨干上通过闸门的新域少于 2 个时，在报告中说明，其余部分照常进行。

### 5.6 锁定后的健全性闸门 G4-0
- 每个保留的（骨干，V 的域），基算子在 confirm4 上单向 R\_2N ≥ 0.95；
- v1 的 C1 在 weekday、month、compass 上 R\_2 ≤ 0.20。

新域不通过，该域退出；旧域不通过，停止并排查管线。

---

## 6. V：多尺度读出（Q9，两个骨干，核心）

### 6.1 条件
- **域**：weekday、month（在新数据上复检），hour、compass8、season（新域）。两个骨干都做。
- **基算子**：按 §5.5 的 GB 规则。
- **手术**（只作用于槽位，定义同 v3）：F∅、F{1}、F¬1，以及全部单平面冻结 F{j}（j ≥ 2）。N = 4 的域中 F¬1 即 F{2}。
- **路径**：plus、minus、交替，各 2N 步，从 world 起点出发，每步解码。与 v3 一样，同时记录每一步三个投票模型（拟合、等权、只用基频）的 argmax。

### 6.2 锁定前的标定与派生量（只用 dev）
- weekday、month 沿用 v3 的标定（同一 dev、同一平面）。hour、compass8、season 按 v3 的程序重新标定，两个骨干各一次。
- **V0**：用 train 计算新域的 a\_k 与 s\_k（描述性量，写入协议）。
- **派生类别**：对每个（骨干，域，F{j}，路径 ∈ {plus, minus}），用理想化状态计算 R̂\_2N 并分类：≥ 0.90 为"可组合"，≤ 0.20 为"失败"，其余为"部分"。
- **V3 的区分力预检**（附录 A.6）：列出各比较的可计分格子数。

### 6.3 预测

| 编号 | 格子 | H-ms | H-fund | H-flat | 判定 |
| --- | --- | --- | --- | --- | --- |
| V0 | 新域，两个骨干：一步变化 s\_1 与振幅 a\_1 | s\_1 最小（全部新域）；a\_1 在 N ≥ 7 的新域中最大 | — | — | 全部成立为通过。这是写本文时就定下的预测，数据尚不存在 |
| V1 | F{1}：N ≥ 7 的域 × 两个骨干（至多 8 格） | 单向 plus R\_2N ≤ 0.20，且交替 R\_2N ≥ 0.80 | 单向与交替都 ≤ 0.20 | 单向与交替都 ≤ 0.20 | 除至多 1 格外都符合某一假设，即判为该假设 |
| V2a | F{1} 的 plus：A(1) − A(⌊N/2⌋)（附录 A.1），同上 8 格 | ≥ 0.50 | ≤ 0.10（A(1) 约为 0） | ≤ 0.10（处处约为 0） | 同 V1 |
| V2b | F¬1 的 plus：A(⌊N/2⌋) − A(1)，同上 8 格 | ≥ 0.25 | ≤ 0.10（处处约为 1） | ≤ 0.10（处处约为 0） | 同 V1 |
| V3 | 单平面冻结 F{j}（j ≥ 2）的类别：plus 与 minus × 五个域 × 两个骨干 | 锁定的派生类别 | "可组合" | "失败" | 按附录 A.6，H-ms 分别与 H-fund、H-flat 比较；每个比较至少 4 个可计分格子，否则不可评 |
| V4 | 冲突条件（S 非空的 F\_S）下逐 world、逐步的一致率（真实潜变量，只计可解析输出），每个骨干 | 拟合 ≥ 0.85；拟合 − 等权的 95% CI 下界 > 0；拟合 − 只用基频的 CI 下界 > 0.10 | 只用基频 ≥ 拟合 | — | 拟合 − 等权的 CI 含 0 时判为 H-equal |

**Q9 的判定**：
- V1、V2a、V2b 都符合 H-ms，V3 胜过两个对手（或不可评），且 V4 在两个骨干上都成立：判为 **H-ms**。
- V1–V3 同上，但 V4 中拟合 − 等权的 CI 在至少一个骨干上含 0：判为 **H-equal**（多尺度来自几何本身，拟合权重没有额外作用）。
- V1、V2a、V2b 符合 H-fund 或 H-flat：判为相应假设。
- 其他情况如实报告为混合。

### 6.4 探索性
- 交替路径的派生类别与观测的对照（动力学部分）。
- 把 P6 的分解方法用到新域。
- 用锁定的 λ 与真实的逐平面距离（不再用循环对称近似）计算各平面的票数份额随位移的变化。

---

## 7. R：基频优先的秩分配（Q10，两个骨干，核心）

### 7.1 条件
- **域**：weekday、month、hour、compass8。
- **秩**：BART 取 r ∈ {N − 4, N − 3, N − 2}；T5Gemma 取 r ∈ {N − 2, N − 1, N, N + 2}。
- **方法**：普通 RRR-r，与 FF-r（基频优先的约束 RRR，附录 A.3）。两者都作用于所有位置。
- **路径**：plus、minus、交替，各 2N 步，在 confirm4 上评测。

### 7.2 锁定前（只用 train/dev，确定性）
1. 拟合全部 RRR-r 与 FF-r，计算每个算子的逐平面误差 ε\_k（附录 A.2）。"平面 k 被准确旋转"定义为 ε\_k ≤ 0.5。
2. 对每个格子（骨干，域，r）记录：
   - 普通 RRR-r 是否缺基频，即 ε\_1 > 0.5；
   - FF-r 中未被准确旋转的平面集合 S\_FF；
   - 投票模型在理想化状态上（S\_FF 冻结，其余转动）对 FF-r 预测的类别。
3. **可计分格子**同时满足三个条件：普通 RRR-r 缺基频；S\_FF 至多含一个平面；投票模型预测 FF-r 为"可组合"。
4. 把可计分格子写入协议。少于 3 格时，R1 在锁定时标为不可评。

### 7.3 预测

| 编号 | 量（可计分格子，plus） | H-alloc | H-capacity |
| --- | --- | --- | --- |
| R1 | FF-r 的 R\_2N，以及 ΔR = R\_2N(FF-r) − R\_2N(RRR-r) | FF-r ≥ 0.90，且 ΔR ≥ 0.20 | ΔR ≤ 0.05 |

- **判定**：≥ 75% 的可计分格子符合哪一方，就判为哪一方；否则为混合。
- **探索性**：不可计分格子的结果；FF-r 中各谐波进入的次序。

---

## 8. U：多步展开训练（Q11，BART，核心）

### 8.1 条件
- **域**：weekday、month、compass。
- **编辑器**：与 v1 的 Editor 结构相同（秩 16），plus 与 minus 联合训练，随机初始化，seed 42/43/44。
- **变体**（训练细节见附录 A.4）：
  - **C1-U4**：展开 CE。每个 batch 随机抽路径类型（plus^S、minus^S、交替）和 S ∈ {1, 2, 3, 4}，每一步都计算 CE。1200 次更新。
  - **C1-UN**：同上，但 S ∈ {1, …, N}。只做 weekday、month。
  - **C3-U4**：每一步计算 CE + 规范 L2（λ = 1），S ∈ {1, …, 4}。只做 month。
- **参照**：v1 的 C1（单步 CE，600 次更新）；P2 的长训练 C3。
- **准入**：dev 上训练视野内（S = 4）的 plus 成功率 ≥ 0.90。不满足就用 2400 次更新重训一次；仍不满足则记为"学不会"，并作为结果报告。

### 8.2 测量（confirm4）
- R\_k：plus、minus、交替各走 2N 步。第 5 步及以后为训练视野之外。
- 探针读出：用 v3 的 M3 探针，读第 1、2 步的状态。
- M1、M2、逐平面 ε\_k。

### 8.3 预测

| 编号 | 量 | H-state | H-shortcut |
| --- | --- | --- | --- |
| U1 | C1-U4 的单向 plus R\_2N（每个域取 seed 中位数） | ≥ 0.90（至少 2/3 个域） | ≤ 0.20（至少 2/3 个域） |
| U2 | C1-U4 在第 1 步状态上的探针读出 | 读出目标 ≥ 0.80 | 读出源 ≥ 0.80 |
| U1b | C1-UN：同 U1 | 同 U1 | 同 U1 |

- **判定**：U1 与 U2 同向才下结论，否则为混合。
- **探索性**：视野内外的分界（R\_4 对 R\_2N）；C3-U4；写入是否变得依赖状态（M1）。

---

## 9. X：跨 token 编辑器与绑定（Q12，BART，核心）

### 9.1 条件
- **域**：bind3、bind3fix、name3（模板 3）。
- **编辑器**（结构见附录 A.5）：只用规范 L2 训练（所有位置），plus 与 minus 分别训练，seed 42/43/44，4000 次更新。
  - **Tok-L2**：逐 token 的低秩编辑器，秩 32。
  - **Att-L2**：在 Tok-L2 上加一个单头注意力分支，可以读取同一句中其他位置。
- **参照**：RRR-32（闭式解）。
- **准入**：name3、bind3fix 上，两种编辑器的 dev 单步成功率都 ≥ 0.95。不满足就用 8000 次更新重训一次；仍不满足则 X 停止并报告。bind3 在锁定后才评测，包括 dev。
- **链**（confirm4）：单向 plus 30 步，单向 minus 6 步，交替 6 步。

### 9.2 预测

| 编号 | 量（seed 中位数） | H-arch | H-deep |
| --- | --- | --- | --- |
| X1 | name3、bind3fix：Att-L2 的单向 R\_6 | ≥ 0.95 | ≥ 0.95 |
| X2 | bind3：Att-L2 与 Tok-L2 的单向 R\_6 | Att-L2 ≥ 0.90，且 Tok-L2 ≤ 0.20 | Att-L2 ≤ 0.50 |

- X1 是正对照，两种假设的预期相同。X1 不通过时，X2 不可评。
- **探索性**：bind3 上，从槽位到名单第 j + 1 位的注意力权重比例；失败时的输出类型。

---

## 10. S：T5Gemma 的长程对称检验（Q13）

- **设置**：T5Gemma，weekday 与 month，自然映射与 σ\_max（v2 的置换表），RRR-32，单向 plus 走 10N 步，confirm4。
- **门槛**：两种映射在 RRR-32 上的 R\_2N 都 ≥ 0.95，否则该域不可评。

| 编号 | 量 | H-slot | H-longsym |
| --- | --- | --- | --- |
| S1 | R\_10N(自然) − R\_10N(σ\_max) | 两个域都 ≤ 0.05 | 至少一个域 ≥ 0.20 |

---

## 11. 锁定（L）

1. 依次完成以下步骤：
   - §0 收尾；
   - D 与审计；
   - 合成自检；
   - 锁定前编码；
   - 闸门（GR、GT、GB）；
   - 新域的标定与派生类别；
   - V3 的区分力预检；
   - R 的锁定前拟合与可计分格子；
   - 冒烟测试；
   - P 的结果提交。
2. `lock.py` 写 `protocol.json`，内容包括：
   - 本文的全部预测、阈值与判定规则；
   - 派生类别、可计分格子、基算子的秩、各骨干的投票权重；
   - 各 split 的 world 种子；
   - 数据与源码的 SHA256；
   - 闸门结果与被剔除的组合。
3. `lock.py` 断言（冒烟测试的产物放在 `local/smoke/`，不计入）：
   - 不存在任何 confirm4 的编码或解码文件；
   - 不存在 bind3 的任何编辑器评测文件；
   - 不存在 U、X 的训练权重。
4. 提交并推送，记录提交哈希。

---

## 12. 作业编排

| 阶段 | 作业（按顺序） | 资源 | `--time` | 依赖 | 通道 |
| --- | --- | --- | --- | --- | --- |
| 收尾 | §0.1 ERRATUM 提交 | — | — | — | — |
| P（CPU） | `p_diag`（P0、P1、P3、P4） | CPU | 02:00:00 | — | — |
| D | `d_make_data` → `d_audit` → `selftest` | CPU | 01:30:00 | — | — |
| P（A） | `p_c3`（P2）→ `p_transplant --bb bart` → `p_dyn --bb bart` | 1 GPU | 03:00 → 00:45 → 00:30 | p\_diag | A |
| P（B） | `p_transplant --bb t5` → `p_dyn --bb t5` | 1 GPU，96G | 01:00 → 00:45 | p\_diag | B |
| 锁定前（A） | `encode_pre_bart`（新域、X 的 train/dev）→ `gates_bart` → `calib_bart`（新域）→ `prelock_fits_bart` → `smoke_bart` | 1 GPU | 01:00 → 01:30 → 01:00 → 01:00 → 01:00 | d\_audit、selftest、P（A） | A |
| 锁定前（B） | `encode_pre_t5` → `gates_t5` → `calib_t5`（新域）→ `prelock_fits_t5` → `smoke_t5` | 1 GPU，96G | 01:30 → 02:00 → 03:00 → 01:30 → 01:00 | d\_audit、selftest、P（B） | B |
| L | `lock` | CPU | 00:15:00 | 以上全部 | — |
| 主体（A） | `encode_c4_bart` → `g40_bart` → `v_chains_bart` → `r_chains_bart` → `u_train` → `u_eval` → `x_train` → `x_eval` | 1 GPU | 01:00 → 00:45 → 03:00 → 02:00 → 03:00 → 01:30 → 01:30 → 01:30 | lock | A |
| 主体（B） | `encode_c4_t5` → `g40_t5` → `v_chains_t5` → `r_chains_t5` → `s_long` | 1 GPU，96G | 01:30 → 01:00 → 05:00 → 04:00 → 02:00 | lock | B |
| 汇总 | `analyze` 与报告 | CPU | 01:30:00 | 全部 | — |

- 预计 7–11 GPU 小时，墙钟约 2–3 天。
- **只能开一条通道时的顺序**：P（A）→ P（B）→ 锁定前（A）→ 锁定前（B）→ lock → `encode_c4_bart` → `g40_bart` → V（BART）→ R（BART）→ `encode_c4_t5` → `g40_t5` → V（T5）→ R（T5）→ S → U → X。
- **停止规则**：G4-0 的旧域不通过；同一作业因不明原因失败两次；发现泄漏；达到预算上限。

---

## 13. 输出与报告

```text
experiments/composability_mechanisms_v3/
  PLAN.md  protocol.json  inputs_manifest.json  DEVIATIONS.md  REPORT.md  run_ledger.json
  *.py  lib4.py  job_gpu.slurm  job_cpu.slurm  gpu_guard.sh  ledger.sh
  data/      新域与 confirm4 的 world、渲染记录、审计与闸门结果
  results/   patch/  calib_*.json  prelock_*.json  v_*.json  r_*.json  u_*.json  x_*.json  s_*.json
             chains.csv（逐步 A_t 与累计 R_t）  predictions.json  shards_*.tar.gz
  figs/      *.png  *.svg
  logs/      <jobid>.out  submitted.txt
  local/     不入 git：编码缓存、拟合、编辑器权重、潜变量
```

### `REPORT.md` 的结构
1. **结论**（3–6 句）：Q9–Q13 各支持哪个假设；对论文主线的含义。
2. **P 的结果**（探索性，单列一节）。
3. **预测对照表**：每条预测列出各假设的预期、锁定阈值、观测值、95% CI、可计分格子数、判定，以及锁定提交的哈希。
4. **V、R、U、X、S 各一节**：一句话方法、主表、主图、适用边界。
5. **偏差与审计**：DEVIATIONS 摘要、泄漏检查、SHA 校验、GPU 用量（总 GPU 小时与峰值并发）。

### 主图
- V（论文核心图候选）：每个新域、每个骨干的 F{1} 与 F¬1 逐步曲线，叠加锁定前派生的预测曲线，标出 N/2、N 与 2N。
- V：各平面票数份额随位移的变化（两个骨干，五个域）。
- R：普通 RRR-r 与 FF-r 的 R\_2N 随秩的变化。
- U：C1、C1-U4、C1-UN 的 R\_t 曲线，标出训练视野。
- X：三个域、三种编辑器的 R\_k，以及 bind3 的注意力热图。

### 统计约定（同 v3）
- 以 world 为统计单位；成功率给 Wilson 95% CI；模型之间的比较用附录 A.7 的 cluster bootstrap。
- 确定性方法不算作多个 seed。
- 探索性结果与确认性结果分开标注。

---

## 14. 结果之后

| 结果 | 含义 | 下一步 |
| --- | --- | --- |
| Q9 为 H-ms | 多尺度读出在新域和两个骨干上得到确认，成为论文的核心机制 | 推广到自然语境（多模板、真实句子） |
| Q9 为 H-equal | 多尺度来自几何本身，拟合权重没有额外作用 | 把读出模型简化为张成内的最近状态 |
| Q10 为 H-alloc | 秩阈值是一步最小二乘的产物；强制保留基频就是一个廉价的修正 | 把基频优先或按位移加权的秩分配写成方法 |
| Q10 为 H-capacity | 秩阈值是真实的容量限制 | 回到"秩 N − 1"的表述 |
| Q11 为 H-state | 只用解码器监督，也能通过多步展开训练得到可组合的编辑器 | 方法一节；在原四域任务上验证 |
| Q11 为 H-shortcut | 规范监督（或 RRR 初始化）是必要的 | 研究需要多长的训练视野，或换别的目标 |
| Q12 为 H-arch | 绑定类编辑需要跨 token 的编辑器 | 写进方法与适用边界 |
| Q12 为 H-deep | 绑定类编辑超出了小型编辑器的能力 | 作为局限写明 |
| Q13 为 H-slot | 秩足够时，任何长度上都不需要对称 | 加强"对称不是必要条件"的结论 |
| Q13 为 H-longsym | 第一个真正的长程对称效应 | 单独追查它的机制 |

---

## 附录 A：定义

### A.1 按位移汇总的逐步正确率 A(m̃)
- 路径从 x\_0 出发，第 t 步的目标状态为 g\_t。位移 m\_t = (g\_t − x\_0) mod N，折叠后 m̃\_t = min(m\_t, N − m\_t)。
- A(m̃) 是 t ∈ [1, 2N] 中所有 m̃\_t = m̃ 的步的 A\_t 平均值。A\_t 为第 t 步答对的 world 比例（非累计）。

### A.2 逐平面误差 ε\_k
1. 记算子在槽位上的线性部分为 L（逐 token 编辑器在每个位置用同一个矩阵；注意 v2/v3 中 RRR 的行向量约定）。平面 k 的正交基为 B\_k，记 A\_k = B\_kᵀ L B\_k。
2. **二维平面**：
   - 取 A\_k 的"旋转—缩放部分" r = ((A₀₀ + A₁₁) + i(A₁₀ − A₀₁)) / 2，得到 ρ = |r|，θ = arg r。
   - 用同样的方法从 train 的 c̄ 拟合理想映射，得到 θ\*（约为 ±2πk/N）。
   - 令 δ\_k = wrap(θ − θ\*)，ρ\_k = ρ / ρ\*。
3. **一维平面**（k = N/2）：A\_k 是标量 a，理想值 a\* 约为 −1。令 q = a / a\*，则 ρ\_k = |q|；q > 0 时 δ\_k = 0，否则 δ\_k = π。
4. **误差**：ε\_k = max\_{1 ≤ t ≤ 2N} |ρ\_k^t · e^{i t δ\_k} − 1|。
   - 冻结的平面（L ≈ I）给出 ε = 2。
   - 取最大值而不是第 2N 步的值，是因为冻结平面的相位误差在 t = N 时会绕回零。
5. **判据**：ε\_k ≤ 0.5 时，称平面 k "被准确旋转"。
6. 平面之间的交叉耦合与非正规部分不计入，报告中注明。

### A.3 基频优先的约束 RRR（FF-r）
1. 与 v2/v3 的 RRR 相同，先在全部 token 上得到 OLS 映射 B̂（行向量约定）和拟合更新 Ŷ = X B̂。
2. Q\_1 为槽位平面 1 的正交基（d × 2）。令 Ŷ\_⊥ = Ŷ (I − Q\_1 Q\_1ᵀ)，取它的前 r − 2 个右奇异向量 V\_⊥。
3. Q = orth([Q\_1, V\_⊥])，得到 B\_FF = B̂ Q Qᵀ（秩为 r）。偏置与普通 RRR 相同。
4. 普通 RRR-r 为 B\_r = B̂ V\_r V\_rᵀ，V\_r 是 Ŷ 的前 r 个右奇异向量。
5. 两者唯一的区别：FF-r 的输出子空间强制包含平面 1。

### A.4 展开训练
1. 每次更新：
   - 等概率抽路径类型 ∈ {plus^S、minus^S、交替}，从规定集合中均匀抽 S；
   - 从 train 抽 batch 8 个（world，起点）；
   - h\_0 = E(x\_0)（缓存）；对 s = 1…S，h\_s = T\_{op\_s}(h\_{s−1})，编辑器作用于所有非 pad 位置。
2. 损失：
   - C1-U：(1/S) Σ\_s CE(decoder(h\_s), text(x\_s))；
   - C3-U：再加 (1/S) Σ\_s L2(h\_s, E(x\_s))，L2 的定义同 v3。
3. 梯度穿过整条展开链，同时更新 plus 与 minus 两个编辑器；编码器与解码器冻结。
4. AdamW，lr 1e-3，weight decay 0，梯度裁剪 1；micro-batch 与 v3 相同。
5. 自检要求：S = 1 时，损失与 v3 `train_editor` 的单步 CE 完全一致。

### A.5 X 单元的编辑器
- **Tok-L2**：Δ\_i = b + U V h\_i，秩 32。
- **Att-L2**：Δ\_i = b + U V h\_i + W\_o Σ\_j α\_ij W\_v h\_j。
  - α\_ij = softmax\_j((W\_q h\_i)ᵀ(W\_k h\_j) / √64)，j 取同一句中的非 pad 位置。
  - W\_q、W\_k、W\_v ∈ R^{64×d}，W\_o ∈ R^{d×64}，W\_o 零初始化（训练开始时等于 Tok-L2）。
- **L2 损失**：在所有非 pad 位置上，取 ‖h\_i + Δ\_i − E(目标)\_i‖² 的平均，除以 ‖E(目标)\_i − E(源)\_i‖² 的平均（相对 L2）。batch 16，AdamW 1e-3，梯度裁剪 1。

### A.6 区分力计分
1. 比较假设 H 与 H′ 时，可计分格子集合 C = {c : pred\_H(c) ≠ pred\_H′(c)}。|C| 在锁定前已知，写入协议。
2. match\_H 为 C 中观测类别等于 pred\_H 的比例，match\_H′ 同理。
3. |C| 不少于规定数量，且 match\_H ≥ 0.75、match\_H′ ≤ 0.50 时，判 H 胜过 H′。

### A.7 cluster bootstrap
- 以 world 为单位有放回抽样，重复 2000 次，种子 3101。
- 每次合并所抽 world 的全部条件与步数，重算一致率之差，取 2.5% 与 97.5% 分位数为 95% CI。

### A.8 合成自检（锁定前必须全部通过）
1. **逐平面误差**：对已知 (ρ, δ) 的合成旋转—缩放算子，恢复误差 < 1e-6；冻结平面给出 ε = 2。
2. **FF-r**：在 s\_1 最小的合成 Z\_12 数据上，普通 RRR-9 的 ε\_1 > 0.5，FF-9 的 ε\_1 ≤ 0.01。
3. **展开训练**：S = 1 时损失与 v3 的单步 CE 一致（误差 < 1e-6）；三种路径的目标序列正确。
4. **注意力编辑器（合成指针复制任务）**：
   - 序列长 8，第 1–3 位放随机"名字"向量；槽位放 name\_j 加位置标记 p\_j；目标槽位为 name\_{j+1} 加 p\_{j+1}；其他位置不变。
   - Att-L2 在留出序列上的相对 L2 ≤ 0.05；Tok-L2 仍 ≥ 0.5。
5. **计分工具**：A(m̃)、区分力计分与 bootstrap 用手工构造的输入做单元测试。

---

## 附录 B：v3 的 `ERRATUM_01.md` 全文

（见 `experiments/composability_mechanisms_v2/ERRATUM_01.md`，已在提交 942c482 中逐字提交。）

---

## 附录 C：`NOTE_DEDUPE.md` 模板

```markdown
# NOTE_DEDUPE（<实验名>）

- 日期：
- 检查内容：本实验各 confirm world 的渲染文本，与 <历史 split 列表> 的渲染文本完全相同的数量（按域、按 split）。
- 重复的 world ID：见 <文件路径>。

| 域 | confirm world 数 | 与历史文本重复的数 | 比例 |
| --- | --- | --- | --- |

## 去掉重复 world 后重算的关键数字

| 结论或预测 | 原值 | 去重后 | 判定是否改变 |
| --- | --- | --- | --- |

## 结论
（全部判定不变 / 以下判定改变：……）
```
