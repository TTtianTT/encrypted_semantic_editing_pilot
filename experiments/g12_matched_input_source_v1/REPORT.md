# G12: Matched Input-Source Training

**B相对A没有提高第四/第五步完整轨迹：两组各seed、各split均0/80。第五步配对差IID 0.00 pp, OOD 0.00 pp。** A/B共同strict+equal-mask集合全部为空，历史差距变化不可估计；不能称差距已缩小。 原子保护不满足预定5pp范围，不能称可靠语义算子已恢复。 已解析输出存在数量损坏，第五步输出全部解析未决，不能确认全体事实保持。数值继续门槛全部满足=False。下表使用全部80个新世界；共同cohort历史对照另列，不能用各模型不同筛选集合替代固定分母。第三步已监督，第四/第五步才是本轮未训练长度。

## 直接回答与固定seed概览

|method|split|atomic_mean|atomic_range|third_endpoint|third_trajectory|fourth_trajectory|fifth_trajectory|
|---|---|---|---|---|---|---|---|
|Original|iid|97.50%|92.50% to 100.00%|19.58%|19.58%|0.00%|0.00%|
|A|iid|59.46%|57.14% to 63.39%|0.00%|0.00%|0.00%|0.00%|
|B|iid|44.35%|39.46% to 52.32%|100.00%|100.00%|0.00%|0.00%|
|Original|template_ood|89.46%|88.93% to 90.36%|7.92%|7.92%|0.00%|0.00%|
|A|template_ood|57.32%|56.96% to 57.68%|0.00%|0.00%|0.00%|0.00%|
|B|template_ood|43.39%|37.14% to 50.18%|99.58%|92.08%|0.00%|0.00%|

直接测量：B的受监督第三步终点在IID全对、OOD三seed均值99.58%，A的纯表示第三步均未通过；但B的OOD seed42在第二步只有62/80正确，所以该seed第三步完整轨迹只有77.50%，不是100%。所有组四/五步完整轨迹均为0；Original seed44 IID第四步有1个终点正确，但此前已失败，不算完整轨迹成功。

输入来源对照支持的局部解释：在相同目标/监督/初始化预算下，edited-input监督更能修复实际第三步表示输入；本批没有未训练四/五步延伸证据，并伴随明显的自然输入原子能力代价。它不证明容量必然受限，也不证明获得了可组合规则。

机制分析受阻：A/B全部seed/split的strict cohort及共同交集为0。其自然编码today的单次编辑没有输出正确yesterday，主要停留在today；与从tomorrow连续两次编辑得到正确yesterday并存。全部下一步仍已生成，不能因cohort为空删除失败。在全分母中，B seed43/44的canonical yesterday下一步也为0，而H2下一步接近100%；这种H0退化不能包装成历史差距修复。

决策：没有达到预定继续信号。本固定方案只显示受监督第三步局部修复，第四步即再次失败，且单步明显受损；结束本批，不追加G13或继续加长监督追分。

## 固定世界主表

|method|seed|split|fixed_worlds|single_step_world_mean|third_endpoint|fourth_trajectory|fifth_trajectory|H0_all|H2_all|own_strict|AB_common|AB_common_equal_mask|H0_common|H2_common|nondate_errors|unresolved|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|Original|42|iid|80|100.00%|47/80|0/80|0/80|80/80|47/80|80|0|0|N/A|N/A|0|218|
|A|42|iid|80|57.86%|0/80|0/80|0/80|80/80|0/80|0|0|0|N/A|N/A|0|300|
|B|42|iid|80|52.32%|80/80|0/80|0/80|80/80|80/80|0|0|0|N/A|N/A|0|112|
|Original|43|iid|80|100.00%|0/80|0/80|0/80|80/80|0/80|80|0|0|N/A|N/A|4|164|
|A|43|iid|80|63.39%|0/80|0/80|0/80|80/80|0/80|0|0|0|N/A|N/A|1|110|
|B|43|iid|80|39.46%|80/80|0/80|0/80|0/80|80/80|0|0|0|N/A|N/A|0|138|
|Original|44|iid|80|92.50%|0/80|0/80|0/80|80/80|0/80|80|0|0|N/A|N/A|6|211|
|A|44|iid|80|57.14%|0/80|0/80|0/80|80/80|0/80|0|0|0|N/A|N/A|0|292|
|B|44|iid|80|41.25%|80/80|0/80|0/80|0/80|80/80|0|0|0|N/A|N/A|0|129|
|Original|42|template_ood|80|90.36%|19/80|0/80|0/80|80/80|19/80|56|0|0|N/A|N/A|0|281|
|A|42|template_ood|80|56.96%|0/80|0/80|0/80|80/80|0/80|0|0|0|N/A|N/A|0|278|
|B|42|template_ood|80|50.18%|80/80|0/80|0/80|60/80|80/80|0|0|0|N/A|N/A|0|111|
|Original|43|template_ood|80|89.11%|0/80|0/80|0/80|72/80|0/80|60|0|0|N/A|N/A|0|162|
|A|43|template_ood|80|57.68%|0/80|0/80|0/80|80/80|0/80|0|0|0|N/A|N/A|0|127|
|B|43|template_ood|80|37.14%|79/80|0/80|0/80|0/80|79/80|0|0|0|N/A|N/A|1|121|
|Original|44|template_ood|80|88.93%|0/80|0/80|0/80|63/80|0/80|59|0|0|N/A|N/A|8|202|
|A|44|template_ood|80|57.32%|0/80|0/80|0/80|80/80|0/80|0|0|0|N/A|N/A|0|230|
|B|44|template_ood|80|42.86%|80/80|0/80|0/80|0/80|80/80|0|0|0|N/A|N/A|0|133|

单步保护分数是每世界7个合法自然输入offset的joint平均，再对80世界平均。H0/H2 all均为主锚点下一步成功n/80。末两列是next+chain+atomic的输出观察计数（每行1200个输出），不是独立世界数，错误字段可重叠；各路径/字段及正常终止详见原始表。所有世界recorded_plan、first-person；未决不算成功，也不是已确认事实错误。

## 四/五步配对效果与原子保护

|split|contrast|mean|seed_range|CI95_pp|positive_seeds|
|---|---|---|---|---|---|
|iid|B-A/trajectory4|0.00 pp|0.00 pp to 0.00 pp|[0.0, 0.0]|0|
|iid|B-A/trajectory5|0.00 pp|0.00 pp to 0.00 pp|[0.0, 0.0]|0|
|iid|B-Original/trajectory5|0.00 pp|0.00 pp to 0.00 pp|[0.0, 0.0]|0|
|iid|B-A/atomic|-15.12 pp|-23.93 pp to -5.54 pp|[-15.89, -14.4]|0|
|iid|B-Original/atomic|-53.15 pp|-60.54 pp to -47.68 pp|[-53.93, -52.44]|0|
|template_ood|B-A/trajectory4|0.00 pp|0.00 pp to 0.00 pp|[0.0, 0.0]|0|
|template_ood|B-A/trajectory5|0.00 pp|0.00 pp to 0.00 pp|[0.0, 0.0]|0|
|template_ood|B-Original/trajectory5|0.00 pp|0.00 pp to 0.00 pp|[0.0, 0.0]|0|
|template_ood|B-A/atomic|-13.93 pp|-20.54 pp to -6.79 pp|[-14.46, -13.39]|0|
|template_ood|B-Original/atomic|-46.07 pp|-51.96 pp to -40.18 pp|[-48.99, -42.98]|0|

2000次world-cluster bootstrap，方法/seed/状态/步骤共享IID或OOD内抽样索引；不重采样seed。区间只反映世界抽样。Original只识别继续训练的收益，主对照始终B−A。

Original在本批7个自然输入offset上并非所有seed都满分：IID seed44保护为92.50%，OOD约88.93–90.36%。这些是新的固定状态全覆盖分数，不能拿旧不同视图分母上的G10单步分数代替。A/B相对同新集Original的下降已在配对表中计算。

## 同当前文本的历史差距：共同分母

|split|contrast|seed_N|mean|CI95_pp|
|---|---|---|---|---|
|iid|A/Delta2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|iid|B/Delta2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|iid|B-A/Delta2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|iid|B-A/H0|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|iid|B-A/H2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|iid|B-Original/H2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|template_ood|A/Delta2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|template_ood|B/Delta2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|template_ood|B-A/Delta2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|template_ood|B-A/H0|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|template_ood|B-A/H2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|
|template_ood|B-Original/H2|{'42': 0, '43': 0, '44': 0}|N/A|[None, None]|

Delta2=H0−H2；B−A/Delta2小于0才是差距缩小，且须与H0/H2绝对变化联合看，不能把H0退化当修复。以下同时给 own strict、A/B共同strict+equal mask、prefix-clean及跨seed敏感性分母。N<40只作低覆盖诊断，不补世界。

|method|seed|split|cohort|history|N|low_coverage|next_joint|next_rate|full_history_joint|date_errors|nondate_errors|unresolved|non_normal_end|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|Original|42|iid|own_strict_equal_mask|0|80|False|80|100.00%|80|0|0|0|0|
|Original|42|iid|own_strict_equal_mask|1|80|False|80|100.00%|80|0|0|0|0|
|Original|42|iid|own_strict_equal_mask|2|80|False|47|58.75%|47|4|0|29|0|
|Original|42|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|Original|42|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|A|42|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|B|42|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|own_strict_equal_mask|0|80|False|80|100.00%|80|0|0|0|0|
|Original|43|iid|own_strict_equal_mask|1|80|False|80|100.00%|80|0|0|0|0|
|Original|43|iid|own_strict_equal_mask|2|80|False|0|0.00%|0|78|2|2|0|
|Original|43|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|Original|43|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|A|43|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|B|43|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|own_strict_equal_mask|0|80|False|80|100.00%|80|0|0|0|0|
|Original|44|iid|own_strict_equal_mask|1|80|False|80|100.00%|80|0|0|0|0|
|Original|44|iid|own_strict_equal_mask|2|80|False|0|0.00%|0|54|3|26|0|
|Original|44|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|Original|44|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|A|44|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|B|44|iid|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|own_strict_equal_mask|0|56|False|56|100.00%|56|0|0|0|0|
|Original|42|template_ood|own_strict_equal_mask|1|56|False|32|57.14%|32|0|0|24|0|
|Original|42|template_ood|own_strict_equal_mask|2|56|False|19|33.93%|19|1|0|36|0|
|Original|42|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|Original|42|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|A|42|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|B|42|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|own_strict_equal_mask|0|60|False|60|100.00%|60|0|0|0|0|
|Original|43|template_ood|own_strict_equal_mask|1|60|False|60|100.00%|60|0|0|0|0|
|Original|43|template_ood|own_strict_equal_mask|2|60|False|0|0.00%|0|59|0|1|0|
|Original|43|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|Original|43|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|A|43|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|B|43|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|own_strict_equal_mask|0|59|False|59|100.00%|59|0|0|0|0|
|Original|44|template_ood|own_strict_equal_mask|1|59|False|59|100.00%|59|0|0|0|0|
|Original|44|template_ood|own_strict_equal_mask|2|59|False|0|0.00%|0|39|4|20|0|
|Original|44|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|Original|44|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|A|44|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|own_strict_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|own_strict_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|own_strict_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|AB_common_equal_mask|0|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|AB_common_equal_mask|1|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|AB_common_equal_mask|2|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|AB_common_prefix_clean|0|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|AB_common_prefix_clean|1|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|AB_common_prefix_clean|2|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|cross_seed_AB_common|0|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|cross_seed_AB_common|1|0|True|0|N/A|0|0|0|0|0|
|B|44|template_ood|cross_seed_AB_common|2|0|True|0|N/A|0|0|0|0|0|


## 1–5步原始结果

|method|seed|split|step|N|endpoint|trajectory|date_errors|nondate_errors|unresolved|non_normal_end|
|---|---|---|---|---|---|---|---|---|---|---|
|Original|42|iid|1|80|80/80|80/80|0|0|0|0|
|Original|42|iid|2|80|80/80|80/80|0|0|0|0|
|Original|42|iid|3|80|47/80|47/80|4|0|29|0|
|Original|42|iid|4|80|0/80|0/80|0|0|80|0|
|Original|42|iid|5|80|0/80|0/80|0|0|80|1|
|A|42|iid|1|80|80/80|80/80|0|0|0|0|
|A|42|iid|2|80|80/80|80/80|0|0|0|0|
|A|42|iid|3|80|0/80|0/80|10|0|70|0|
|A|42|iid|4|80|0/80|0/80|0|0|80|0|
|A|42|iid|5|80|0/80|0/80|0|0|80|1|
|B|42|iid|1|80|80/80|80/80|0|0|0|0|
|B|42|iid|2|80|80/80|80/80|0|0|0|0|
|B|42|iid|3|80|80/80|80/80|0|0|0|0|
|B|42|iid|4|80|0/80|0/80|79|0|1|0|
|B|42|iid|5|80|0/80|0/80|0|0|80|8|
|Original|43|iid|1|80|80/80|80/80|0|0|0|0|
|Original|43|iid|2|80|80/80|80/80|0|0|0|0|
|Original|43|iid|3|80|0/80|0/80|78|2|2|0|
|Original|43|iid|4|80|0/80|0/80|0|0|80|0|
|Original|43|iid|5|80|0/80|0/80|0|0|80|0|
|A|43|iid|1|80|80/80|80/80|0|0|0|0|
|A|43|iid|2|80|80/80|80/80|0|0|0|0|
|A|43|iid|3|80|0/80|0/80|80|0|0|0|
|A|43|iid|4|80|0/80|0/80|51|1|29|0|
|A|43|iid|5|80|0/80|0/80|0|0|80|0|
|B|43|iid|1|80|80/80|80/80|0|0|0|0|
|B|43|iid|2|80|80/80|80/80|0|0|0|0|
|B|43|iid|3|80|80/80|80/80|0|0|0|0|
|B|43|iid|4|80|0/80|0/80|76|0|4|0|
|B|43|iid|5|80|0/80|0/80|0|0|80|1|
|Original|44|iid|1|80|80/80|80/80|0|0|0|0|
|Original|44|iid|2|80|80/80|80/80|0|0|0|0|
|Original|44|iid|3|80|0/80|0/80|54|3|26|0|
|Original|44|iid|4|80|1/80|0/80|0|0|79|0|
|Original|44|iid|5|80|0/80|0/80|0|0|80|0|
|A|44|iid|1|80|80/80|80/80|0|0|0|0|
|A|44|iid|2|80|80/80|80/80|0|0|0|0|
|A|44|iid|3|80|0/80|0/80|14|0|66|0|
|A|44|iid|4|80|0/80|0/80|0|0|80|0|
|A|44|iid|5|80|0/80|0/80|0|0|80|0|
|B|44|iid|1|80|80/80|80/80|0|0|0|0|
|B|44|iid|2|80|80/80|80/80|0|0|0|0|
|B|44|iid|3|80|80/80|80/80|0|0|0|0|
|B|44|iid|4|80|0/80|0/80|41|0|39|0|
|B|44|iid|5|80|0/80|0/80|0|0|80|0|
|Original|42|template_ood|1|80|80/80|80/80|0|0|0|0|
|Original|42|template_ood|2|80|56/80|56/80|20|0|4|0|
|Original|42|template_ood|3|80|19/80|19/80|18|0|43|0|
|Original|42|template_ood|4|80|0/80|0/80|0|0|80|0|
|Original|42|template_ood|5|80|0/80|0/80|0|0|80|0|
|A|42|template_ood|1|80|80/80|80/80|0|0|0|0|
|A|42|template_ood|2|80|80/80|80/80|0|0|0|0|
|A|42|template_ood|3|80|0/80|0/80|21|0|59|0|
|A|42|template_ood|4|80|0/80|0/80|0|0|80|0|
|A|42|template_ood|5|80|0/80|0/80|0|0|80|0|
|B|42|template_ood|1|80|80/80|80/80|0|0|0|0|
|B|42|template_ood|2|80|62/80|62/80|18|0|0|0|
|B|42|template_ood|3|80|80/80|62/80|0|0|0|0|
|B|42|template_ood|4|80|0/80|0/80|80|0|0|0|
|B|42|template_ood|5|80|0/80|0/80|0|0|80|15|
|Original|43|template_ood|1|80|80/80|80/80|0|0|0|0|
|Original|43|template_ood|2|80|60/80|60/80|20|0|0|0|
|Original|43|template_ood|3|80|0/80|0/80|79|0|1|0|
|Original|43|template_ood|4|80|0/80|0/80|0|0|80|0|
|Original|43|template_ood|5|80|0/80|0/80|0|0|80|1|
|A|43|template_ood|1|80|80/80|80/80|0|0|0|0|
|A|43|template_ood|2|80|80/80|80/80|0|0|0|0|
|A|43|template_ood|3|80|0/80|0/80|80|0|0|0|
|A|43|template_ood|4|80|0/80|0/80|34|0|46|1|
|A|43|template_ood|5|80|0/80|0/80|0|0|80|1|
|B|43|template_ood|1|80|80/80|80/80|0|0|0|0|
|B|43|template_ood|2|80|80/80|80/80|0|0|0|0|
|B|43|template_ood|3|80|79/80|79/80|0|0|1|0|
|B|43|template_ood|4|80|0/80|0/80|52|1|28|8|
|B|43|template_ood|5|80|0/80|0/80|0|0|80|0|
|Original|44|template_ood|1|80|80/80|80/80|0|0|0|0|
|Original|44|template_ood|2|80|59/80|59/80|21|0|0|0|
|Original|44|template_ood|3|80|0/80|0/80|59|4|21|0|
|Original|44|template_ood|4|80|0/80|0/80|0|0|80|0|
|Original|44|template_ood|5|80|0/80|0/80|0|0|80|1|
|A|44|template_ood|1|80|80/80|80/80|0|0|0|0|
|A|44|template_ood|2|80|80/80|80/80|0|0|0|0|
|A|44|template_ood|3|80|0/80|0/80|45|0|35|0|
|A|44|template_ood|4|80|0/80|0/80|0|0|80|1|
|A|44|template_ood|5|80|0/80|0/80|0|0|80|1|
|B|44|template_ood|1|80|80/80|80/80|0|0|0|0|
|B|44|template_ood|2|80|80/80|80/80|0|0|0|0|
|B|44|template_ood|3|80|80/80|80/80|0|0|0|0|
|B|44|template_ood|4|80|0/80|0/80|44|0|36|0|
|B|44|template_ood|5|80|0/80|0/80|0|0|80|0|

首次失败步数见evaluation/first_failure.csv；0表示五步全对。单步逐offset保护见atomic_by_state.csv。

## 保真与未决

|kind|method|field_errors|unresolved_observations|observation_N|
|---|---|---|---|---|
|current|Original|{'event_date': 109}|4|1440|
|current|A|{'event_date': 480}|0|1440|
|current|B|{'event_date': 498}|0|1440|
|next|Original|{'quantity': 9, 'event_date': 329}|150|1440|
|next|A|{'event_date': 700}|230|1440|
|next|B|{'event_date': 511}|2|1440|
|chain|Original|{'quantity': 9, 'event_date': 353}|1085|2400|
|chain|A|{'quantity': 1, 'event_date': 335}|1105|2400|
|chain|B|{'quantity': 1, 'event_date': 390}|589|2400|
|atomic|Original|{'event_date': 216}|3|3360|
|atomic|A|{'event_date': 1396}|2|3360|
|atomic|B|{'event_date': 1733}|153|3360|

字段错误可重叠，已解析子集无错误不能等同于全体保真。数量、作者/主体/接收者、动作、状态、否定、归属、记录日期均逐项核对；人称固定first-person。所有逐输出分数及正常终止保留。人工label为空，本轮为结构化自动检查，尚无真人审核。

## 训练监督与实际计算

|method|seed|updates|parameters|supervised_samples|supervision_tokens|stage_tokens|encoder_sample_calls|editor_sample_calls|decoder_sample_calls|training_seconds|peak_GPU_GB|
|---|---|---|---|---|---|---|---|---|---|---|---|
|A|42|200|25344|3200|446800|[146800, 146800, 153200]|6400|9600|9600|21.45|2.089|
|B|42|200|25344|3200|446800|[146800, 146800, 153200]|6400|9600|9600|21.84|2.089|
|A|43|200|25344|3200|446800|[146800, 146800, 153200]|6400|9600|9600|18.84|2.089|
|B|43|200|25344|3200|446800|[146800, 146800, 153200]|6400|9600|9600|15.22|2.089|
|A|44|200|25344|3200|446800|[146800, 146800, 153200]|6400|9600|9600|22.75|2.089|
|B|44|200|25344|3200|446800|[146800, 146800, 153200]|6400|9600|9600|21.37|2.089|

两组独立加载各seed同一G10 checkpoint；optimizer均新建。阶段CE按该阶段batch有效token归一化，三阶段等权。两臂均在线编码y0和y2，无缓存；B的第三次输入为本组当前h2.detach()，不使用测试激活或teacher。每batch2encoder、3editor、3decoder调用，stage有效token完全一致。训练计算结构配对，隐藏状态轨迹不同；不声称严格等FLOPs。最终200步固定，不选最优test/dev链checkpoint。dev每50步仅作固定诊断。

训练合法源 160 世界，开发 27 世界，3200个固定出现；mask/日期/模板排除记录在training_exclusions.json。所有8个原训练模板保留。梯度smoke test确认第三项不回传h2、第三T仍有有限非零梯度、前两损失照常传播；backbone梯度为空且weights不变。

## 资源、审计与边界

累计GPU分配 862 秒（0.239 GPU小时），上限14400秒；并发峰值 2。每allocation1卡，训练数组0–2%2且每seed串行A/B，训练结束才开评估。加载、失败/重试和dev都计入；队列等待不计GPU，parent/task不与step重复累加。完整账本budget.json。
固定门槛：{"iid_mean_fifth_gain_at_least10pp": false, "iid_at_least_two_positive_seeds": false, "iid_world_ci_lower_positive": false, "ood_mean_same_positive_direction": false, "atomic_protection_within5pp_all_comparisons": false, "next_experiment_started": false, "all_predefined_numerical_gates_met": false}
本批不追加方法、seed、长度或G13。更长训练轨迹上的局部修复不能叫普遍可组合规律；跨文本严格匹配只是表面/评分状态匹配，不保证所有隐藏语义相同。mask一致不代表语义token位置对齐。G11 crossover没有唯一部件归因，本实验也不作神经元或离开流形机制宣称。

## 冻结与复现

data/lock.json记录训练前协议/配置/数据/日程/模型和评分依赖hash；cohort_lock在所有最终checkpoint固定、current-only inference完成后先锁定，再执行任何next/long-chain。80+80新世界与全部可获得旧世界完整事实键及规范化render文本无重叠；数据选择只依语法/tokenizer。恢复文件在local/仅本地；公开六个小editor，基础模型及activation不上传。原始输出含目标/实际文本、frame、评分、mask、终止、耗时和模型hash。
README.md与commands.log给出入口。review/blind_cases.csv及CASES.md覆盖输出前抽取的20世界，方法映射独立保存。所有未决和失败保留原分母；没有真人审核。
