# ESEP 实验计划 v2：线性潜空间编辑为什么能（或不能）组合

- 实验名：`composability_mechanisms_v1`
- 项目：Encrypted Semantic Editing Pilot（ESEP）
- 日期：2026-11-22
- 分支：从 `origin/experiment/symmetry-composability-v1` 新建 `experiment/composability-mechanisms-v1`
- 目录：`experiments/composability_mechanisms_v1/`。把本文件存为该目录下的 `PLAN.md`，与代码一起提交。
- 上一轮：`experiments/symmetry_composability_v1/`（`REPORT.md`、`AMENDMENT_01.md`、`results/`）

---

## 0. 这一轮要回答什么

v1 确立了三件事：

1. **CE 捷径**：只用 CE 训练的编辑器 C1，在 5 个新域 × 3 个 seed 上全部是 R_1 = 100%、R_2 = 0%。它每一步写入的几乎是同一个向量：time 域相邻两步更新的余弦为 0.994–0.999；在 5 个新域上，偏置约 63–76% 落在写入列空间之外。
2. **规范编辑器是 Z_N 的置换表示加收缩**：闭式 RRR-16 在 5 个单 token 域上完全可组合。weekday 的单位模特征值相位为 ±51.4°、±102.8°、±154.2°（360°/7 的倍数），month 为 30° 的倍数，模长 0.994–0.999；其余特征值模长小于 1，即收缩。
3. **秩分离**：month 的 RRR-8、weekday 的 RRR-4 单步成功率都是 100%，单向链却在第 3–6 步归零。秩 ≥ 16 时全部完美。

v1 没有回答"可组合性究竟由什么决定"。本轮用四组对照把候选原因分开：

| 问题 | 假设 A | 假设 B | 决定性实验 |
| --- | --- | --- | --- |
| Q1 几何对称是必要条件吗？ | H-sym-N：编辑映射不是编码器几何的等距变换时，线性编辑失去可组合性 | H-slot：单 token 槽位上任何循环置换都能被线性实现并组合，对称只影响算子的正规性 | S1a 乱序循环：同样的词、句式和编码，只改循环顺序 |
| Q2 person 为什么失败？ | H-bind：目标 token 取决于句中其他位置的内容（需要绑定或复制），逐 token 共享的线性映射做不到 | H-geom：与绑定无关 | S1b：确定性 Z3（代词、固定人名）对比需要绑定的 Z3（参与者名单） |
| Q3 秩阈值是多少？ | H-rank：可组合需要秩 ≥ N − 1（状态张成的维数），单步解码所需的秩更低 | 阈值高于 N − 1，上下文 token 的属性"回声"占了额外维度 | S2：细秩网格、特征相位、按傅里叶模式分解误差 |
| Q4 C1 写入的是什么？ | H-instr：与状态无关的"+1 指令"，由解码器执行；编辑后状态仍编码源状态 | H-approx：近似的目标状态加离流形残差 | S3：写入可移植性、源/目标探针、写入方向 |

S4（C3 锚定强度）和 S5（第二个骨干）为可选。

**理论修正（写进报告背景）**：
- v1 的 E0.2 表明，可组合的算子并不是整体等距：C3 和 RRR 的 ISO 反而更大。
- 它们是"流形上精确置换，流形外收缩"。
- 特征值落在 N 次单位根上，是 T^N = I 的必然结果。任何循环置换，不论几何是否对称，都会这样，所以它不是对称性的证据。
- 对称性只会体现在单位模特征向量是否正交（正规性）上，这是 S1a 要测的量。

---

## 1. 给 Claude Code 的执行规则

### 沿用 v1
详见 `experiments/symmetry_composability_v1/PLAN.md` 的"执行规则"一节。

- 所有 Python 计算都用 `sbatch` 提交，作业内用 `srun` 启动。登录节点只做 git、文件读写和 `squeue`/`sinfo`/`sacct`。入口脚本开头调用 `require_slurm()`。
- **GPU 并发**：
  - 任何时刻，本人名下正在使用的 GPU 不超过 2 张，其他项目的作业也计入。每个 GPU 作业只申请 `--gres=gpu:1`。
  - 只开两条 GPU 通道 A、B，同一通道内的作业严格串行。
  - 通道首个作业提交前运行 `gpu_guard.sh`。依赖只写 `sbatch --parsable` 返回的真实 job ID。
  - 本人若另有 GPU 作业在跑，就只开一条通道。
- **模板**：复制 v1 的 `job_gpu.slurm`、`job_cpu.slurm`、`gpu_guard.sh`、`ledger.sh`。作业名前缀改为 `compmech-`，日志写到新目录的 `logs/`。
- **分区**：先查 `sinfo`，默认用 `B300q`，避开 drain/down 节点。
- **预算**：GPU 分配时间总上限 10 GPU 小时，用 `sacct` 记账并写入 `run_ledger.json`。到 8 小时先报告，到 10 小时立即停止。核心部分（S1–S3）预计约 3 GPU 小时。
- **冻结**：BART-base 冻结，revision `aadd2ab…`。除 S1b 的 C1/C3 和 S4 的 C3 变体外，不训练任何参数。RRR 是确定性闭式解，不能当作多个 seed。编辑器 seed 固定为 42、43、44。
- **提交**：每完成一个编号单元，提交一次并推送，提交信息为 `compmech: <编号> <一句话结果>`。`local/` 不入库，只在 manifest 里记录 SHA256 与大小；超过 50 MB 的单个文件不入 git。
- **偏差**：任何与本文不同的做法都写入 `DEVIATIONS.md`，注明时间、原因、影响，以及发生在锁定前还是锁定后。

### 新增规则
1. **锁定后不得修改预测、阈值或判定规则。** 负责人在看到结果后若要求修改，必须新建 `AMENDMENT_xx.md`。受影响的预测在报告里降为"探索性"，不计入通过或失败；原始判定照常报告。
2. **每个问题同时登记两个竞争假设各自的预期。** 报告要写明数据支持哪一个，或者两者都不支持。
3. **健全性闸门 G2-0**：confirm2 上，自然映射的 RRR-16 必须复现 v1，即单向 R_2N ≥ 0.95，且所有域 C1 的 R_2 ≤ 0.20。不满足就停止，先排查管线。

---

## 2. 复用与新建

| 用途 | 来源 |
| --- | --- |
| 新域语义、评测与工具函数 | v1 的 `sym_semantics.py`、`sym_evaluator.py`、`symutil.py`。复制到新目录后扩展，不改 v1 原文件 |
| 编码、RRR、训练、链式评测、代数诊断、几何 | v1 的 `e1_encode.py`、`e1_fit_rrr.py`（内部 import `canonical_write_reachability_v1/fit.py`）、`e1_train.py`、`e1_eval.py`、`e1_algebra.py`、`e1_geometry.py` |
| v1 的 train/dev 编码与 RRR/C1/C3 权重 | v1 的 `local/`，按 `inputs_manifest.json` 与各 `*_complete.json` 中的 SHA256 定位 |
| KL 定义 | `experiments/operator_residual_v2/core.py` 的 `logits` 与 `distribution` |
| BART 后端 | `.four-domain-worktree/experiments/four_domain_state_coverage_v1/backend.py` 的 `Backend('bart')`；S5 用 `Backend('t5gemma')` |

新建文件，全部放在 `experiments/composability_mechanisms_v1/` 下：

- `sym2_semantics.py`：import v1 的 `sym_semantics`，新增两类域。
  - 乱序映射域 `<domain>_scrmax`、`<domain>_scrmed`：`render` 与原域相同，`advance` 用协议中锁定的置换表。
  - S1b 的三个域 `pron3`、`name3`、`bind3`。
- `sym2_evaluator.py`：扩展 v1 评测器，覆盖 S1b 的句式。它不 import 任何语义模块。
- 脚本：`p0_preflight.py`、`d_make_data.py`、`d_audit.py`、`d_encode.py`、`s1_select.py`、`s1b_geometry.py`、`lock.py`、`fit_rrr.py`、`train.py`、`eval_chains.py`、`algebra.py`、`s2_modes.py`、`s3_mechanism.py`、`analyze.py`。
- 记录文件：`protocol.json`、`inputs_manifest.json`、`DEVIATIONS.md`、`REPORT.md`、`run_ledger.json`。

---

## 3. 数据（D）

### confirm2
- 为 v1 的五个域（weekday、month、compass、egoside、daysago）各生成 160 个新 world，作为本轮所有确认性评测的唯一数据。
- 核心键（people、object、color、quantity、status）与 v1 的全部 split（train、dev、confirm），以及仓库中所有历史 world 文件互斥。
- 种子写入协议。每个 world 预先抽一个起始状态，供单向链使用。
- train（96）和 dev（32）沿用 v1 的数据与编码。

### S1b 新域
三个域各 96/32/160 个 world，用模板 0。三域句式完全相同，只有槽位填的词不同：

| 域 | 状态（均为单 BPE token，已核对） | 句式 | plus |
| --- | --- | --- | --- |
| pron3 | me, you, them | `Participants: {p0}, {p1}, {p2}. The {o} was sent to {X}. {fact}` | 循环到下一个代词 |
| name3 | Daniel, Sarah, Kevin（不在参与者名单的人名表里） | 同上 | 循环到下一个固定人名 |
| bind3 | 第 j 位参与者 {p_j}，随 world 变化 | 同上 | j → j+1（模 3） |

- {p0, p1, p2} 是该 world 的三个人名，取自 v1 的 `NAMES`。`{fact}` 沿用 v1。
- bind3 的目标 token 取决于该 world 的参与者名单，要从句中其他位置"取来"。pron3 和 name3 的目标 token 只由源 token 决定。
- 模板 3（结构 OOD）：每域设计一个，只做几何与单步分析，不参与拟合或训练。

### 审计（`d_audit.py`）
任一项不通过就修改模板，修好之前不进入下一步。

1. 金标准文本判为成功的比例为 100%。
2. 每个相邻转换在所有 world 上的 attention mask 完全相同。
3. 核心键在各 split 之间、与全部历史 world 之间互不重叠。
4. 输出每个模板、每个状态的 token 数表。
5. 负对照（错状态、改颜色、截断、未结束）全部判为失败。

---

## 4. S1a 乱序循环：几何对称是否必要

### 选择乱序映射（锁定前进行，只用 train+dev 和模板 0）
- **循环域**：N ≤ 7 时枚举全部有向 N-循环 σ；N = 12 时随机抽 2000 个（种子 3101），把 σ 作为新的 plus。用 v1 的 E_iso 计算每个 σ 的几何等变误差。
- **选两个映射**：σ_max 取 E_iso 最大者，σ_med 取 E_iso 中位数者（并列时取字典序最小）。Z4 只有 6 个有向 4-循环；σ_med 若与自然循环或 σ_max 重合就省略。
- **daysago（开边界）**：随机抽 2000 个 8 状态的路径顺序（排除自然顺序及其反向），同样选出 σ_max 和 σ_med。plus 为路径上的后继。
- **参考值**（v1 零分布）：σ_max 的 E_iso 预计如下表。egoside 的反差最大，作为主检验域。

| 域 | 自然映射 E_iso | σ_max 预计 E_iso | 倍数 |
| --- | --- | --- | --- |
| weekday | 0.044 | 约 0.14 | 约 3 |
| month | 0.078 | 约 0.19 | 约 2.4 |
| compass | 0.0023 | 约 0.043 | 约 19 |
| egoside | 0.0024 | 约 0.18 | 约 75 |
| daysago | 0.021 | 约 0.14 | 约 7 |

- 选出的置换表、各自的 E_iso 与选择依据写入 `protocol.json`。

### 拟合与评测
- 对自然映射、σ_max、σ_med 分别闭式拟合 RRR，秩 16（主）和 32。ridge 选择与 v1 相同：只用 train 内部 80/16 划分。只用模板 0。
- confirm2 上的链，每一步都解码：
  - 循环域：从 world 起点单向 plus 10N 步，单向 minus 2N 步，从状态 0 起 plus/minus 交替 2N 步。
  - daysago：从路径起点单向走 7 步，从终点反向走 7 步，从路径第 4 个状态起交替 10 步。
- 代数诊断（定义见附录 A）：
  - 新增两项：单位模块特征向量条件数 κ_u（衡量正规性），瞬态增长 G。
  - 沿用 v1：特征相位与 N 次单位根的偏差、κ_N、e_inv、DRIFT。
  - 对 v1 已有的自然映射 RRR-16 也补算 κ_u 和 G，作为基线。

### 预测
| 编号 | 量 | H-sym-N 预期 | H-slot 预期 |
| --- | --- | --- | --- |
| A1 | egoside σ_max，RRR-16，单向 R_2N | ≤ 0.50 | ≥ 0.95 |
| A2 | 全部 σ_max 与 σ_med，RRR-16，单向 R_2N | 随 E_iso 增大而下降 | 全部 ≥ 0.95 |
| A3 | 长程差值：R_10N(自然) − R_10N(σ_max)，循环域 | ≥ 0.20 | ≤ 0.05 |
| A4 | 单位模特征值的相位 | 两者都落在 N 次单位根上（偏差 < 2°） | 同左 |
| A5 | κ_u(σ_max) / κ_u(自然) | > 1 | > 1 |

A4、A5 两种假设预期相同，只用来核对机制。

**判定**：
- A1、A2、A3 全部按 H-slot 预期成立：结论为"在单 token 槽位上，对称不是可组合的必要条件"。
- A1 和至少一个其他域的 σ_max 按 H-sym-N 预期成立：结论为"对称是必要条件"。
- 其余情况记为部分支持，报告 R_k 与 E_iso、κ_u、G 之间的关系。

---

## 5. S1b 绑定对照：person 为什么失败

- **方法**：RRR 秩 16 和 32；C1 与 C3，seed 42/43/44，600 次更新，配置同 v1。
- **链**（各域 confirm 的 160 个 world）：单向 plus 30 步（10 圈）；单向 minus 6 步；交替 6 步。
- **几何与可预测性**（锁定前，只用 train+dev）：
  - E_iso 与 SEP。
  - 槽位线性可预测性：在 train 上，从源状态的槽位表示 ridge 回归到目标状态的槽位表示，报告 dev 上的 R²。

| 编号 | 量 | H-bind 预期 | H-geom 预期 |
| --- | --- | --- | --- |
| B1 | pron3、name3：RRR-16 单向 R_6 | ≥ 0.95 | ≥ 0.95 |
| B2 | bind3：RRR-16 单向 R_6 | ≤ 0.50 | ≥ 0.95 |
| B3 | 三域 C1 的 R_2（每个 seed） | ≤ 0.20 | ≤ 0.20 |
| B4 | bind3 的槽位可预测 R² 减去 pron3 与 name3 的较小者 | ≤ −0.30 | 绝对值 < 0.10 |

如果 bind3 也能组合（B2 按 H-geom 预期成立），说明解码器能按"指针"复制名字。那么 person 的失败另有原因（长度变化或多槽位），报告里如实写明。

---

## 6. S2 秩定律

### 设置
- **秩网格**：

| 域 | 秩 |
| --- | --- |
| weekday | 4、5、6、7、8 |
| month | 8、9、10、11、12、14、16 |
| compass、egoside | 2、3、4 |
| daysago | 6、7、8、10、12、16 |

  weekday 和 month 的 σ_max 也跑同样的网格。
- **测量**：
  - 单步成功率。
  - 单向 R_N、R_2N 和交替 R_2N。
  - 每个秩下 RRR 单位模块的特征相位：哪些谐波 k 出现在 |λ| ≥ 0.9 的特征值中。
- **按傅里叶模式分解误差**（循环域，自然映射，秩 < N − 1，定义见附录 A）：在属性 token 位置，把每一步的潜变量误差分配到各个谐波平面以及状态张成之外，看误差集中在哪些谐波上。
- **Oracle 模式修补（探索性）**：每一步只在属性 token 位置，把算子缺失的谐波分量替换为规范目标的对应分量，看链是否恢复。
- **daysago**：秩不足时，记录失败发生在哪个转换，看是否集中在走进边界状态 two 或 nine 的那一步。

### 预测
| 编号 | 预测 | 通过条件 |
| --- | --- | --- |
| R1 | 自然循环域的可组合秩阈值 r* = N − 1（weekday 6、month 11、Z4 3）：r = N − 1 时单向 R_2N ≥ 0.95，r = N − 2 时 ≤ 0.20 | 三种 N 都成立，允许 ±1 |
| R2 | 单步阈值低于组合阈值：month 在 r ≤ 8、weekday 在 r ≤ 4 时，单步成功率 ≥ 0.95 | 成立 |
| R3 | 乱序循环的组合阈值与自然循环相同，但秩不足时单步成功率更低（"对称让近似编辑更容易解码"） | weekday、month 在 r = N − 2 时，单步(自然) − 单步(σ_max) ≥ 0.20 |
| R4（探索） | 秩不足时保留的是哪些谐波（低频还是高频） | 只报告 |
| R5（探索） | daysago 秩不足的失败集中在边界转换 | 只报告 |

---

## 7. S3 C1 机制：写入的是"指令"还是"状态"

- **对象**：v1 已训练的 C1（5 个域 × seed 42/43/44），以 RRR-16 和规范写入作对照。数据为 confirm2。
- **测量**（定义见附录 A）：
  1. **写入与状态无关的程度**：同一 world 内，不同源状态的 C1 写入两两之间的余弦（token 级）。
  2. **写入方向**：C1 写入与规范写入 E(g·x) − E(x) 之间的余弦。
  3. **源/目标探针**：在属性 token 位置，用 train 的规范编码训练多类逻辑回归（标签为状态），再读取 C1 第一步之后的状态。
  4. **写入移植**：把源状态 x 的 C1 写入加到同一 world 的其他源状态 x′ 上，看解码是否为 x′ 的下一状态。跨 world 的移植同理。
  5. **推力缩放（探索）**：对 E(x) + α·W(x)，α ∈ {0.25, 0.5, 0.75, 1, 1.5, 2, 3}，统计解码落在源状态、下一状态、下下状态、其他状态和不可解析的比例。
  6. **作用位置（探索）**：只在属性 token 上施加写入，或只在其余位置施加，看第一步是否成功。
  7. **环绕可见性（探索）**：取 C1 状态与规范目标之差 r，加到同一 world 的 E(x+k) 上（k = 0 … N − 1），测相对 x+k 文本的 KL，并与等范数随机方向比较。

| 编号 | 量 | H-instr 预期 | H-approx 预期 |
| --- | --- | --- | --- |
| M1 | 不同源状态之间 C1 写入的平均余弦 | ≥ 0.90 | ≤ 0.60 |
| M2 | C1 写入与规范写入的余弦（world 中位数） | 绝对值 ≤ 0.20 | ≥ 0.50 |
| M3 | 探针在 C1 状态上读出源状态的比例 | ≥ 0.80（读出目标 ≤ 0.20） | 读出目标 ≥ 0.80 |
| M4 | 同 world 写入移植的成功率 | ≥ 0.80 | ≤ 0.20 |
| M5–M7（探索） | 推力缩放、作用位置、环绕可见性 | 只报告 | 只报告 |

---

## 8. 锁定（L）

1. 依次完成：D（数据与审计）→ S1b 的 train/dev 编码 → S1a 乱序映射选择 → S1b 几何与可预测性。
2. `lock.py` 写 `protocol.json`，内容包括全部预测、阈值、判定规则、置换表、数据与源码的 SHA256。
3. 提交并推送，记录提交哈希。
4. 此后才能编码或解码 confirm2 和 S1b 的 confirm world。`lock.py` 要断言此前不存在任何 confirm2 的编码或解码文件。

---

## 9. 可选部分

S1–S3 全部完成、且 GPU 用量低于 5 小时，才做以下两项。

### S4 C3 的锚定强度
- **设置**：month 与 daysago 两个域。C3 的 λ ∈ {3, 10}，另加以 RRR-16 初始化的 C3（λ = 1），seed 42/43/44。
- **H-weight（锚定权重不足）**：λ = 10 时，month 单向 R_24 ≥ 0.90，daysago 单向 R_7 ≥ 0.90。
- **H-conflict（CE 与规范写入本质冲突）**：上述条件不满足，且以 RRR 初始化的 C3 会漂离：DRIFT 上升，单向 R 下降。
- 同时报告各变体的 DRIFT 与相邻写入余弦，检验"单向失败、交替保持"是否来自残余的常数推力。

### S5 第二个骨干
- **设置**：T5Gemma，即 `Backend('t5gemma')`，bf16。
  - 范围：weekday 与 month，自然映射和 σ_max 各一套。
  - 方法：RRR 秩 {N − 2, N − 1, 16, 32}，C1 × 3 个 seed。
  - 数据：confirm2 的前 80 个 world。
- **预测**：A1–A3、R1–R2、B3 的方向与 BART 一致。

---

## 10. 作业编排

| 单元 | 作业 | 资源 | `--time` | 依赖 | 通道 |
| --- | --- | --- | --- | --- | --- |
| P0 | `p0_preflight`（定位并哈希 v1 产物，验证 BART revision） | CPU | 00:30:00 | — | — |
| D | `d_make_data`、`d_audit` | CPU | 00:30:00 | P0 | — |
| D | `d_encode`（S1b 的 train/dev） | 1 GPU | 00:30:00 | d_audit | A |
| S1a | `s1_select`（候选映射的 E_iso） | CPU | 01:00:00 | d_audit | — |
| S1b | `s1b_geometry` | CPU | 00:30:00 | d_encode | — |
| L | `lock` | CPU | 00:15:00 | s1_select、s1b_geometry | — |
| 拟合 | `fit_rrr`（S1a 的映射 × 秩、S2 的秩网格、S1b） | 1 GPU | 01:00:00 | lock | A |
| 训练 | `train`（S1b：3 域 × C1/C3 × 3 seed，共 18 次） | 1 GPU | 02:00:00 | lock | B |
| 评测 | `d_encode` confirm2 + `eval_chains`：A 跑 weekday、month、daysago；B 跑 compass、egoside、S1b | 每通道 1 GPU | 每组 03:00:00 | fit_rrr、train | A、B |
| S2 | `s2_modes`（模式分解与修补） | 1 GPU | 01:00:00 | 评测 | A |
| S3 | `s3_mechanism` | 1 GPU | 01:00:00 | confirm2 编码 | B |
| 代数 | `algebra` | CPU | 00:30:00 | fit_rrr | — |
| 汇总 | `analyze` 与报告 | CPU | 01:00:00 | 全部 | — |
| 可选 | S4 训练与评测；S5 编码、拟合、训练与评测 | 每通道 1 GPU | 每项 ≤ 03:00:00 | 核心完成 | A、B |

预计：核心部分约 3 GPU 小时（month 10N = 120 步的链占最多），墙钟约 1–2 天；可选部分另加 3–4 GPU 小时。

---

## 11. 输出与报告

```text
experiments/composability_mechanisms_v1/
  PLAN.md  protocol.json  inputs_manifest.json  DEVIATIONS.md  REPORT.md  run_ledger.json
  *.py  job_gpu.slurm  job_cpu.slurm  gpu_guard.sh  ledger.sh
  data/      confirm2 与 S1b 的 world、渲染记录、审计结果
  results/   s1a_*.json  s1b_*.json  s2_*.json  s3_*.json  chains.csv  singles.csv  algebra.json  shards.tar.gz
  figs/      *.png  *.svg
  logs/      <jobid>.out  submitted.txt
  local/     不入 git：编码缓存、RRR 拟合、编辑器权重、latents
```

### `REPORT.md` 的结构
1. **结论**（3–5 句）：Q1–Q4 分别支持哪个假设；健全性闸门 G2-0 是否通过；对论文主线的含义。
2. **预测对照表**：每条预测给出两种假设的预期、锁定阈值、观测值、CI、判定，以及锁定提交的哈希。
3. **S1a、S1b、S2、S3 各一节**：一句话方法、主表、主图、适用边界。
4. **偏差与审计**：DEVIATIONS 摘要、泄漏检查、SHA 校验、GPU 用量（总 GPU 小时与峰值并发）。

### 主图
- S1a：自然映射与乱序映射的 R_k 曲线，横轴到 10N。
- S2：单步成功率与 R_2N 随秩的变化，横轴标出 N − 1，这是论文的核心图候选。
- S2：每个秩下的特征相位分布，以及误差按谐波的分解。
- S3：源/目标探针的读出比例与写入移植的成功率。
- S1b：三域的 R_k 曲线与槽位可预测 R²。

### 统计约定（同 v1）
- 以 world 为统计单位；成功率给 Wilson 95% CI；连续量用 world bootstrap（2000 次，种子 3101）。
- 确定性方法（RRR、reencode）不算作多个 seed。
- 探索性结果与确认性结果分开标注。

---

## 12. 结果之后

| S1a | S1b | S2 | 含义与下一步 |
| --- | --- | --- | --- |
| H-slot | H-bind | R1 成立 | **可组合性由三件事决定**：写入规范状态（不是 CE 推力）、秩覆盖全部 N − 1 维、槽位目标只由源 token 决定。对称性解释几何弯曲（CE 的常数推力为什么第二步失败）和近似编辑的解码容忍度，但不是必要条件。论文主线改为"解码正确不等于可组合：目标、秩与绑定"。 |
| H-sym-N | 任意 | 任意 | **对称是必要条件**。主线回到"统计对称 → 等变 → 可组合"，下一轮写 E3（群结构编辑器）计划。 |
| H-slot | H-geom | 任意 | person 的失败另有原因，下一轮做多槽位与长度变化的对照。 |
| 任意 | 任意 | R1 不成立 | 阈值高于 N − 1，说明上下文 token 占了额外维度。补做按位置分解的秩分析。 |

S3 的结论决定机制一节怎么写：
- H-instr：写成"CE 学会给解码器下一条可执行的指令，而不是改写状态"。
- H-approx：写成"CE 写的是近似目标加离流形残差"。

---

## 附录 A：新增指标定义

记 A_Q 为 v1 定义的算子核心矩阵（列向量约定，见 v1 PLAN 附录）。

- **单位模块与 κ_u**：对 A_Q 做特征分解，取 |λ| ≥ 0.9 的特征值及其单位化特征向量（复数），组成矩阵 V_u。κ_u = σ_max(V_u) / σ_min(V_u)。正规算子的特征向量正交，此时 κ_u = 1。
- **瞬态增长 G**：G = max_{1 ≤ k ≤ 10N} ‖A_Q^k‖₂。在 A_Q 的子空间里用 float64 计算。
- **相位偏差**：对每个 |λ| ≥ 0.9 的特征值，δ = min_j |arg λ − 2πj/N|（单位为度），报告 max δ。若某个特征值的 δ < 2°，就记谐波 j 为"出现"。
- **谐波平面与误差分解**（只用于循环域）：
  1. 在属性 token 位置，取每个 train world 的规范槽位表示，在 world 内去均值，再对 world 取平均，得到 c̄(x)。x 按自然顺序编号，不随映射改变。
  2. 对 k = 1 … ⌊N/2⌋，令 u_k = Σ_x cos(2πkx/N)·c̄(x)，v_k = Σ_x sin(2πkx/N)·c̄(x)。按 k 从小到大做 Gram–Schmidt 正交化，得到各谐波平面 P_k。
  3. 第 t 步的误差 e = h_slot − E_slot(target)，各谐波的能量占比为 ‖P_k e‖² / ‖e‖²，余下部分记为"状态张成之外"。
- **写入**：W_w(x) = M ⊙ (T(E_w(x)) − E_w(x))，把有效 token 展平成向量。单 token 槽位域的 mask 在各状态间相同。
- **探针**：
  - 模型：`sklearn` 的多类 `LogisticRegression`，输入为标准化后的槽位表示，C 在 {0.01, 0.1, 1, 10} 中用 5 折交叉验证在 train 上选择。
  - 健全性：dev 规范编码的准确率应 ≥ 0.99。
  - 报告：在 C1 第一步状态上预测为源状态、目标状态、其他状态的比例。RRR-16 的第一步状态作对照，预期读出目标。
- **移植**：
  - 同 world：对所有 x′ ≠ x，解码 E_w(x′) + W_w(x)；结果为 g(x′) 且非目标事实保持，记为成功。
  - 跨 world：解码 E_{w′}(x) + W_w(x)；结果为 g(x) 且带 w′ 的事实，记为成功。
- **槽位可预测 R²（S1b）**：在 train 上，从源状态槽位表示 ridge 回归到目标状态槽位表示，λ 用 5 折交叉验证选择；报告 dev 上的 R²。
- **KL**：与 `operator_residual_v2/core.py` 的 `distribution` 相同，即 KL(参照‖扰动)，用同一组 teacher-forcing 标签，排除 padding。
