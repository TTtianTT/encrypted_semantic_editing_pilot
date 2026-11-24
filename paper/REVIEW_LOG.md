# REVIEW_LOG（对抗审稿与发现的问题；由负责人决定处理）

## 2026-11-25，替换引言时发现的问题（Claude Code；引言措辞未改）

按阶段 2 指令，用 `01_intro_draft.tex` 替换引言，只修宏名与引文键。以下问题未改动原文，请负责人决定。

1. **"All editors in our main experiments are rank-limited affine maps"（第 2 段）**：
   - CE 与状态监督编辑器（C1、C3、C3-U4）和闭式算子（RRR-r）都是低秩仿射映射，代码已核实。
   - 绑定单元的注意力编辑器（Att1、Att2、Att2L、OR）是非线性的，而"范围"段又提到绑定。
   - 建议：要么写明"main experiments"不含绑定，要么改成"all editors outside the binding experiments"。
2. **`\CLoneVfiveBaseMin`（"composes for 2N steps on every backbone and domain"）**：
   - 宏取自 v5 G5-0：两个骨干、10 个模板 0 的（骨干，域）组合，全部 1.00。
   - v5 的多句式全序列 RRR-16 不在其中，它在训练句式的 dev 上就失败了。
   - "every backbone and domain" 在模板 0 的范围内成立。是否加"for the fixed-template domains"，请定。
3. **`\CLthirteenHundredMax`（"none of the editors we trained composes over 100 steps"）**：
   - 宏按指令取 Att2L-U8 8 个 seed 的最大 R\_100，为 0.06。
   - v7 中 Att2L-U4、Att1-U8 与 OR-U8 也跑了 100 步，R\_100 都是 0，所以这句话对 v7 的全部绑定编辑器成立。
   - v5、v6 更早的编辑器（Tok-U、Att1-U、Att2-U、OR-U4）没有跑到 100 步，但它们在 12–30 步内就已衰减。
   - 宏只覆盖 Att2L-U8，与"none of the editors"字面上不完全对应。
4. **CL7 的"smallest one-step energy"**：
   - 宏 `\CLsevenSoneSmallestAll` 统计的是"按平面计的一步变化 s\_1 最小"（13/13）。
   - 附录 C 的命题 2 改为按每个维度的能量排序。基频是二维平面，两种排序只在与一维 Nyquist 平面比较时才可能不同。
   - 引言的说法在数据上成立；如需与命题 2 完全一致，可写"per dimension"。
5. **§9（绑定）的结构**：计划 A4 的新结构把绑定单列为 §9；目前绑定仍在 §8"Scope"中，引言引用 `Section~\ref{sec:scope}`。若拆出 §9，引言中的引用需要一并改。
6. **第 1 层注意力**（仅供 §9 参考，不影响引言）：
   - 指令中的"0.89–1.00"是我在简报中只列出的 3 个 seed 的值。
   - 全部 8 个 seed 中有 7 个在 0.89–1.00；seed 45（表现最差，R\_30 = 0.08）的第 1 层完全不看名字。
   - §9 已据此写成"8 个 seed 中有 7 个"，区间按撑过 30 步的 seed 计算。
