# DEVIATIONS（composability_mechanisms_v3，v4 计划）

每条注明时间、原因、影响，以及发生在锁定前还是锁定后。

## 锁定前

1. **2026-11-23，PLAN.md 附录 B**。`PLAN.md` 的附录 B 没有再抄一遍 ERRATUM 全文，而是指向已逐字提交的 `experiments/composability_mechanisms_v2/ERRATUM_01.md`（提交 942c482）。原因：同一文本只保留一份。影响：无。

2. **2026-11-23，bind3fix 的数据量（§5.2、§5.3）**。
   - 原因：bind3fix 的名单固定，模板 3 里也不渲染 status，所以文本只随 (object, color, quantity) 变化，共 8 × 5 × 9 = 360 种。v3 已经用掉 288 种（train 96、dev 32、confirm3 160）。在"文本级去重"的要求下，全新的 confirm4 最多 72 个 world，train 480 不可能做到。
   - 做法：
     - confirm4 取剩下的全部新组合：71 个 world（第 72 个组合的渲染文本与历史文本重合，被去重规则排除）；
     - X 单元的 train/dev 复用 v3 的 288 个 bind3fix world：train 224 = v3 train 96 + v3 confirm3 前 128；dev 64 = v3 dev 32 + v3 confirm3 后 32。world_id 改为 `bind3fix_v4_*`，并用 `origin_world_id` 记录来源。
   - 影响：
     - bind3fix 的 confirm4 只有 71 个 world。X1 的 Wilson CI 会变宽；判定按 seed 中位数的点估计，规则不变。
     - bind3fix 的 train/dev 文本在 v3 中出现过，所以不是"全新"。confirm4 与它们、也与全部历史文本都不重合（审计第 8 项：`confirm4_vs_reused_text_overlap = 0`，`history_text_hits_fresh_worlds = 0`）。
     - X 的 bind3fix 训练集比计划小（224 对 480）。

3. **2026-11-23，FF-r 的实现形式（附录 A.3）**。
   - 做法：v2/v3 的 RRR 求解器（`canonical_write_reachability_v1/fit.py: solve`）是在白化坐标下做的：A = (C + λI)^(-1/2) · cross，RRR-r 保留 A 的前 r 个右奇异向量 V_r，B_r = B̂ V_r V_rᵀ。FF-r 照此实现：Q = orth([Q_1, A(I − Q_1Q_1ᵀ) 的前 r − 2 个右奇异向量])，B_FF = B̂ Q Qᵀ，其中 B̂ = (C + λI)^(-1) cross；偏置与 RRR 相同。
   - 原因：A.3 第 1 点要求"与 v2/v3 的 RRR 相同"。用 A 的右奇异向量，才能让 FF-r 与普通 RRR-r 只差"强制包含平面 1"这一处（A.3 第 5 点）。
   - 影响：A.3 第 2 点写的 Ŷ = X B̂，与 A 的右奇异向量只在岭项上有差别，λ = 0 时两者相同。ridge 的选择沿用 v3 的内层划分程序，FF-r 与 RRR-r 各自独立选择。合成自检 A.8.2 用的就是这个实现：FF-11 与 RRR-11 一致，FF-9 保留平面 1。

4. **2026-11-23，A.8.4 合成指针复制任务的具体构造**。
   - 做法（d = 128，序列长 8，槽位在第 5 位）：
     - 第 1–3 位的名字 token 和槽位都带固定的位置标记；
     - 名单名字与槽位名字放在两个不同的子空间（16 维）；
     - 同一序列中的名字共享一个随机分量（name_i = c + e_i，c 的方差为 e 的 3 倍）；
     - 槽位标记 p_j 的范数为 0.3。
   - 原因：
     - 如果名字两两独立，最优逐 token 预测的相对 L2 上界是 σ²/(2σ² + ‖Δp‖²) < 0.5，"Tok-L2 仍 ≥ 0.5" 就无法成立；
     - 如果名字 token 不带位置标记，单头注意力找不到第 j + 1 位。
   - 影响：只影响自检的构造。结果：Att-L2 留出相对 L2 为 0.0025，Tok-L2 为 0.654，通过。

5. **2026-11-23，锁定前写入协议的操作化定义**（`protocol.json` 的 `operational` 字段，逐条列出）。这些是对计划文字的具体化，没有改动任何阈值：
   - V1/V2 中 H-fund 与 H-flat 的预测相同，记为 "H-fund/H-flat"，由 V3 区分；
   - season（N = 4）的 F{2} 就是 F¬1；
   - V4 的记录范围与 CI 规则；
   - U 中"学不会"的 seed 在 U1/U1b 的中位数里按 R_2N = 0 计，并且不进入 U2；
   - U1b 只有两个域，"至少 2/3 个域"指两个域都满足；
   - S1 中有域不可评时的规则。

6. **2026-11-23，P 的预定义细节**（探索性）：
   - P2 的"已收敛"：最后 1000 次更新中 dev L2 的相对变化 < 2%，各读法按 3 个 seed 中的多数（≥ 2）判断；
   - P5 不再单列 v3 的 "natural successor" 类，并入"其他"（另行报告其比例）；
   - P6 的阈值：相位差 > π/N；幅度比偏离 > 25%；残差或上下文偏离 > 第 1 步的 2 倍。
   - P4 为了覆盖 egoside 的 σ_max 算子，`sym4_semantics.MAPS` 加入 v2 协议中 egoside 的 σ_max 表 [0, 1, 3, 2]（只用于 P4）。

7. **2026-11-23，A.8.3 分两处完成**：
   - CPU 自检（`selftest.py`）：用替身 CE，检验 S = 1 的展开损失与单步公式一致，并检验三种路径的目标序列；
   - GPU 冒烟测试（`smoke.py --backbone bart`）：在真实解码器上比较 S = 1 的展开损失与 v3 `train_editor` 的单步 CE。

   原因：自检按计划是 CPU 作业。影响：无。

8. **2026-11-23，weekday/month 的标定**："沿用 v3 的标定"按字面执行：λ 与平面文件取自 v3（平面逐元素相等由断言保证），派生类别在同一 dev 上用相同程序重算。v3 的 HS 条件集合不含 F{j} 的 minus 类别以外的新内容，因此不需要额外标定。

9. **2026-11-23，P3 的重算方式**：在已解码的 v1/v2 分片上，重跑各自锁定的分析脚本（`p3_rerun.py`），只去掉重复 world 的记录，并删除"160 个 world"的断言；v1 confirm 几何量在剩余 world 上重算。不重新编码或解码。以下部分依赖 confirm 编码上的 GPU 计算，只保存了汇总量，因此没有重算，在 NOTE_DEDUPE 中注明：v1 的 P6（κ_N）；v2 的 M1–M4，以及 A4、A5（这两项只依赖拟合）。
