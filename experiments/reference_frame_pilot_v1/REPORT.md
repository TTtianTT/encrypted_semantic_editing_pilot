# 文本参考系转换 v1：实际运行报告

1. **单步能否做到？** 在受控模板与固定操作 ID 上，LowRank16 的三 seed 单步联合成功率 IID 均值为 100.00%（范围 100.00%–100.00%），OOD 为 97.71%。Shift 的 IID 均值为 46.67%，相同600组更新预算下主要受时间转换限制。这不是 Shift 的性能上限。
2. **损坏了哪些不变量？** 已解析输出中，Shift损坏了事件日期、主体、接收者、数量和取消状态；LowRank16的已解析不一致只涉及事件日期。但两者时间纯表示链的未决输出中均出现记录锚点、事件事实丢失及不可理解词串，不能据已解析子集声称内容始终保持。自动未检测到计划→完成；未决输出未被穷尽审核，这不是零风险证明。
3. **两步还能做到？** LowRank16 在 IID 的时间→人称纯表示链联合成功率均值为 98.33%，相应重编码链为 100.00%；连续两次时间+1纯表示链为 0.00%。其他顺序、OOD和往返见完整表，单步成功不自动推出组合成功。
4. **是否泛化到未见模板？** OOD使用4个未进入训练的句法家族，词汇共享；单步与组合分别评价。结果只能支持这个受控结构迁移范围，不能支持自然长文或开放指令。
5. **下一步？** 先停止向自然文本/长文扩展，优先另立版本诊断时间算子在已编辑表示上的稳定性，以及中间相对日期表达的训练源覆盖。单步和时间×人称组合有信号，但时间连续及往返的纯表示链均未过工程线；本批已完成规定六组训练和全部核心测试，不自动新增训练或资源。未有人类审核，整体标为“结构化自动检查 + 模型复核”。

## 已执行范围与资源

- E0：420/420自由生成逐字重构成功，各状态140/140；直接generate与encoder_outputs路径一致，BART梯度为空，编辑梯度非零、padding有效。
- train/dev/test：480/80/160条独立记录；另有60 calibration；每记录6原子训练/评价路径。无组合训练、无编辑输出训练输入。
- Shift和LowRank16各seed42/43/44，共六组，每组四个独立算子，均600更新；best均由单步dev目标token NLL选择。E1 LowRank16达到100%通过门槛后才启动E2。
- 原始BART SHA256：`1bd3ac8e5b3ac71c77cf18fbcd8b113e0bfceced94c5cfbbb9a2b4bb4781190b`；float32、输入96、生成60、greedy。全部最长gold为52 tokens，未静默截断。
- 本轮单GPU累计 724 分配秒（0.2011 GPU小时），上限7200秒；sacct父/step取最大不重复累加。详见budget.json与logs/slurm_accounting.tsv。
- 正式输出 20680 条：atomic 10920、composition 9600、两次重建 160；到达生成上限 173 条。全固定分母保留。

## 三 seed 单步与组合

以下为joint_ok。范围是三个独立训练seed范围，不是置信区间。完整逐seed、逐状态、逐路径N及其他指标在evaluation/summary.csv、status_summary.csv。

|方法|测试层|路径|seed42|seed43|seed44|均值|范围|
|---|---|---|---:|---:|---:|---:|---|
|Shift|test_iid|atomic_all|47.92%|44.17%|47.92%|46.67%|44.17%–47.92%|
|Shift|test_iid|atomic_time|23.75%|18.44%|24.38%|22.19%|18.44%–24.38%|
|Shift|test_iid|atomic_perspective|96.25%|95.62%|95.00%|95.62%|95.00%–96.25%|
|Shift|test_iid|time_then_person/latent_chain|2.50%|1.25%|2.50%|2.08%|1.25%–2.50%|
|Shift|test_iid|person_then_time/latent_chain|2.50%|1.25%|2.50%|2.08%|1.25%–2.50%|
|Shift|test_iid|time_twice/latent_chain|0.00%|0.00%|0.00%|0.00%|0.00%–0.00%|
|Shift|test_iid|time_then_person/decode_reencode|12.50%|6.25%|18.75%|12.50%|6.25%–18.75%|
|Shift|test_iid|person_then_time/decode_reencode|10.00%|5.00%|20.00%|11.67%|5.00%–20.00%|
|Shift|test_iid|time_twice/decode_reencode|0.00%|0.00%|0.00%|0.00%|0.00%–0.00%|
|Shift|test_template_ood|atomic_all|39.17%|37.71%|37.29%|38.06%|37.29%–39.17%|
|Shift|test_template_ood|atomic_time|12.50%|10.94%|10.62%|11.35%|10.62%–12.50%|
|Shift|test_template_ood|atomic_perspective|92.50%|91.25%|90.62%|91.46%|90.62%–92.50%|
|Shift|test_template_ood|time_then_person/latent_chain|2.50%|1.25%|2.50%|2.08%|1.25%–2.50%|
|Shift|test_template_ood|person_then_time/latent_chain|2.50%|1.25%|2.50%|2.08%|1.25%–2.50%|
|Shift|test_template_ood|time_twice/latent_chain|0.00%|0.00%|0.00%|0.00%|0.00%–0.00%|
|Shift|test_template_ood|time_then_person/decode_reencode|10.00%|10.00%|13.75%|11.25%|10.00%–13.75%|
|Shift|test_template_ood|person_then_time/decode_reencode|7.50%|6.25%|10.00%|7.92%|6.25%–10.00%|
|Shift|test_template_ood|time_twice/decode_reencode|1.25%|1.25%|0.00%|0.83%|0.00%–1.25%|
|LowRank16|test_iid|atomic_all|100.00%|100.00%|100.00%|100.00%|100.00%–100.00%|
|LowRank16|test_iid|atomic_time|100.00%|100.00%|100.00%|100.00%|100.00%–100.00%|
|LowRank16|test_iid|atomic_perspective|100.00%|100.00%|100.00%|100.00%|100.00%–100.00%|
|LowRank16|test_iid|time_then_person/latent_chain|98.75%|97.50%|98.75%|98.33%|97.50%–98.75%|
|LowRank16|test_iid|person_then_time/latent_chain|97.50%|98.75%|98.75%|98.33%|97.50%–98.75%|
|LowRank16|test_iid|time_twice/latent_chain|0.00%|0.00%|0.00%|0.00%|0.00%–0.00%|
|LowRank16|test_iid|time_then_person/decode_reencode|100.00%|100.00%|100.00%|100.00%|100.00%–100.00%|
|LowRank16|test_iid|person_then_time/decode_reencode|100.00%|100.00%|100.00%|100.00%|100.00%–100.00%|
|LowRank16|test_iid|time_twice/decode_reencode|66.25%|66.25%|66.25%|66.25%|66.25%–66.25%|
|LowRank16|test_template_ood|atomic_all|97.71%|98.33%|97.08%|97.71%|97.08%–98.33%|
|LowRank16|test_template_ood|atomic_time|96.56%|97.50%|95.94%|96.67%|95.94%–97.50%|
|LowRank16|test_template_ood|atomic_perspective|100.00%|100.00%|99.38%|99.79%|99.38%–100.00%|
|LowRank16|test_template_ood|time_then_person/latent_chain|88.75%|83.75%|75.00%|82.50%|75.00%–88.75%|
|LowRank16|test_template_ood|person_then_time/latent_chain|92.50%|87.50%|77.50%|85.83%|77.50%–92.50%|
|LowRank16|test_template_ood|time_twice/latent_chain|0.00%|0.00%|0.00%|0.00%|0.00%–0.00%|
|LowRank16|test_template_ood|time_then_person/decode_reencode|97.50%|97.50%|96.25%|97.08%|96.25%–97.50%|
|LowRank16|test_template_ood|person_then_time/decode_reencode|96.25%|97.50%|96.25%|96.67%|96.25%–97.50%|
|LowRank16|test_template_ood|time_twice/decode_reencode|65.00%|65.00%|63.75%|64.58%|63.75%–65.00%|

## 对照与不变量

Copy、Identity评价目标转换，因此即使复制保真也不能通过目标参考系。Target reconstruction仅为可重构性诊断，不是数学上界。Text-rule从源文本和框架解析字段，不读取W。Wrong-operation只对LowRank16使用固定每测试层前10个记录×6原子路径×3seed；不用于选模型。

|对照|测试层|N|joint_ok|content_ok|plan_to_completed|parse_unresolved|
|---|---|---:|---:|---:|---:|---:|
|reconstruction_only s|test_iid|80|100.00%|100.00%|0.00%|0.00%|
|reconstruction_only s|test_template_ood|80|100.00%|100.00%|0.00%|0.00%|
|Copy s|test_iid|480|0.00%|33.33%|0.00%|0.00%|
|Copy s|test_template_ood|480|0.00%|33.33%|0.00%|0.00%|
|Identity s|test_iid|480|0.00%|33.33%|0.00%|0.00%|
|Identity s|test_template_ood|480|0.00%|33.33%|0.00%|0.00%|
|Target reconstruction s|test_iid|480|100.00%|100.00%|0.00%|0.00%|
|Target reconstruction s|test_template_ood|480|100.00%|100.00%|0.00%|0.00%|
|Text-rule s|test_iid|480|100.00%|100.00%|0.00%|0.00%|
|Text-rule s|test_template_ood|480|100.00%|100.00%|0.00%|0.00%|
|Text-rule + E/D s|test_iid|480|100.00%|100.00%|0.00%|0.00%|
|Text-rule + E/D s|test_template_ood|480|100.00%|100.00%|0.00%|0.00%|
|Wrong-operation s42|test_iid|60|0.00%|0.00%|0.00%|0.00%|
|Wrong-operation s42|test_template_ood|60|0.00%|0.00%|0.00%|0.00%|
|Wrong-operation s43|test_iid|60|0.00%|0.00%|0.00%|0.00%|
|Wrong-operation s43|test_template_ood|60|0.00%|0.00%|0.00%|0.00%|
|Wrong-operation s44|test_iid|60|0.00%|0.00%|0.00%|0.00%|
|Wrong-operation s44|test_template_ood|60|0.00%|0.00%|0.00%|0.00%|

已成功解析输出中的槽位不一致次数（跨所有种子、路径；诊断计数，不视为独立样本）：

|方法|槽位|次数|
|---|---|---:|
|LowRank16|event_date|388|
|Shift|actor|91|
|Shift|event_date|3552|
|Shift|quantity|60|
|Shift|recipient|12|
|Shift|record_status|4|

神经方法解析未决共 2579 条；已解析的非日期不变量错误输出共 141 条。原始分数保持冻结；模型复核见review/model_review.md，不能用便利抽查估计总体准确率。

## 顺序一致和往返

Shift的加法天然交换，输出一致不证明语义独立。两条顺序都正确的比例与一致率分别报告。以下按三seed取均值；单seed见CSV。

|方法|测试层|执行方式|语义一致|两条都正确|
|---|---|---|---:|---:|
|Shift|test_iid|latent_chain|91.25%|2.08%|
|Shift|test_iid|decode_reencode|84.17%|10.83%|
|Shift|test_template_ood|latent_chain|72.92%|2.08%|
|Shift|test_template_ood|decode_reencode|76.67%|7.50%|
|LowRank16|test_iid|latent_chain|97.50%|97.50%|
|LowRank16|test_iid|decode_reencode|100.00%|100.00%|
|LowRank16|test_template_ood|latent_chain|83.33%|80.00%|
|LowRank16|test_template_ood|decode_reencode|98.75%|96.67%|

|方法|测试层|往返路径|前向正确|回程正确|两者都正确|
|---|---|---|---:|---:|---:|
|Shift|test_iid|time_return/latent_chain|12.50%|0.00%|0.00%|
|Shift|test_iid|person_return/latent_chain|95.00%|100.00%|95.00%|
|Shift|test_iid|time_return/decode_reencode|12.50%|44.58%|0.00%|
|Shift|test_iid|person_return/decode_reencode|95.00%|97.50%|92.50%|
|Shift|test_template_ood|time_return/latent_chain|11.25%|0.00%|0.00%|
|Shift|test_template_ood|person_return/latent_chain|90.00%|100.00%|90.00%|
|Shift|test_template_ood|time_return/decode_reencode|11.25%|57.92%|0.00%|
|Shift|test_template_ood|person_return/decode_reencode|90.00%|91.25%|82.92%|
|LowRank16|test_iid|time_return/latent_chain|100.00%|0.00%|0.00%|
|LowRank16|test_iid|person_return/latent_chain|100.00%|98.33%|98.33%|
|LowRank16|test_iid|time_return/decode_reencode|100.00%|66.25%|66.25%|
|LowRank16|test_iid|person_return/decode_reencode|100.00%|100.00%|100.00%|
|LowRank16|test_template_ood|time_return/latent_chain|97.50%|0.00%|0.00%|
|LowRank16|test_template_ood|person_return/latent_chain|99.58%|91.25%|90.83%|
|LowRank16|test_template_ood|time_return/decode_reencode|97.50%|64.17%|64.17%|
|LowRank16|test_template_ood|person_return/decode_reencode|99.58%|99.58%|99.58%|

计划跨事件日结果见evaluation/plan_crossing.csv，未把reported_completed/cancelled混入计划分母。逆向算子独立训练；回程单独成功不能排除Identity式无作用。

## 时间组合失败的附加诊断

LowRank16 IID的连续两次T_plus和T_minus∘T_plus纯表示链三seed均为0%；同样任务的重编码链三seed均为66.25%，而同次数无编辑重建对照为100%。这提示编辑后表示上的算子稳定性问题，但不足以给出唯一机制归因。

额外按中间目标相对日期分层（明确为事后诊断，不替换主分母）：每个IID seed的80记录中，27条中间应表达three days ago（offset=-3）；T_plus/T_minus训练源只覆盖offset=-2…+2。重编码链这27条均失败，其余53/53成功。纯表示链在这53条中仍为0/53。因此既有源表达支持范围外的问题，也有在该范围内的纯表示链失败，不能把所有失败归咎于未见日期词。完整分层见temporal_support_diagnostic.csv。

计划跨日小组不含所有相对日期条件，不能用它代替整体时间组合评价。建议后续独立版本先检验输入支持范围闭合及编辑后表示稳定性，保留本轮结果不改分母、不追加本轮训练。

## 统计、时延及限制

2000次配对bootstrap以record_id为单位，IID/OOD内分别重采样；同记录全部视图、路径和seed一起保留。对三seed平均记录分数的区间只覆盖记录抽样，不覆盖全部训练随机性。逐seed表、均值/范围和paired differences均保存，不把多个视图当独立样本。

计时包括实际encode/edit/decode、CPU规则和重复编解码；latent链的诊断中间解码单列，也计入total，core_without_diagnostic另存原始输出。数据准备、CPU评分不包含在模型推理计时，GPU分配总耗时则保守包含作业内全部操作。主生成批大小16，Wrong-operation末批4；禁止把它与批16直接比较。Copy为直接字符串引用，未进行可信微基准，时间0不能解读为零成本。这里只提供分阶段原始描述性计时，不宣称端到端加速。

评分器完整消费受控句子并接受部分非reference替代表达，但不覆盖任意自然改写。parse_unresolved不是已证实语义错误；保守通过率不计成功。recorded_plan/reported_cancelled阴性样例在本生成方案中与较早事件日有相关性，因而不能声称完整解耦泛化。negative reported_completed按已发生时间段的否定事件报告解释；取消“不做”的计划不推导“做了”。

数据协议预检前唯一修订是明确event date作用域，旧草稿留档；没有根据测试修改数据/评分/阈值。身份词汇共享，不能声称未见人物或词汇迁移。源标题与record_date均为输入的一部分，无目标前缀。所有框架条件由外部提供，不是学会日历计算或任意指令理解。

固定40个test record_id、按方法匿名的全部关键路径在review/blind_review.csv；private_method_map.json单独保存。尚无人类填写。该包既含IID也含OOD，不用便利审查估总体准确率。

## 固定20例

16个固定随机记录的原子路径（方法/路径在查结果前固定），加每层首记录两方法的时间→人称纯表示链4例。没有按成功筛选。全部为seed42；包括原句、外部框架、目标语义、输出及冻结判定。

### 1. test_iid_0018 / Shift / T_plus_first

- 原句：Author: Emma. Record date: 2026-09-20. According to the record, my plan to bring six parcels to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-09-21", "perspective": "first"}, "target_frame": {"view_date": "2026-09-22", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_iid_0018", "author": "Emma", "actor": "Emma", "recipient": "Bob", "action": "bring", "object": "parcel", "quantity": 6, "record_date": "2026-09-20", "event_date": "2026-09-20", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma"}`
- 输出：Author: Emma. Record date: 2026-09-20. According to the record, my plan to bring six parcels to Bob concerns an event dated yesterday. This record does not establish that the event occurred.
- 判定：joint=False，frame=False，content=False，unresolved=False，原因=None。

### 2. test_iid_0030 / LowRank16 / T_plus_first

- 原句：Author: Emma. Record date: 2026-08-10. The subject of the record is my plan to not give nine sensors to Carol, with the event dated two days ago. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-11", "perspective": "first"}, "target_frame": {"view_date": "2026-08-12", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_iid_0030", "author": "Emma", "actor": "Emma", "recipient": "Carol", "action": "give", "object": "sensor", "quantity": 9, "record_date": "2026-08-10", "event_date": "2026-08-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma"}`
- 输出：Author: Emma. Record date: 2026-08-10. The subject of the record is my plan to not give nine sensors to Carol, with the event dated three days ago. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 3. test_iid_0037 / Shift / P_13_first

- 原句：Author: Frank. Record date: 2026-09-04. In the record, my report of bringing four tickets to Bob has an event date of yesterday.
- 框架：`{"source_frame": {"view_date": "2026-09-05", "perspective": "first"}, "target_frame": {"view_date": "2026-09-05", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_iid_0037", "author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "bring", "object": "ticket", "quantity": 4, "record_date": "2026-09-04", "event_date": "2026-09-04", "record_status": "reported_completed", "polarity": "positive", "attribution": "Frank"}`
- 输出：Author: Frank. Record date: 2026-09-04. In the record, Frank's report of bringing four tickets to Bob has an event date of yesterday.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 4. test_iid_0046 / LowRank16 / P_13_first

- 原句：Author: Carol. Record date: 2026-09-15. The subject of the record is my report of not bringing one ticket to Frank, with the event dated yesterday.
- 框架：`{"source_frame": {"view_date": "2026-09-16", "perspective": "first"}, "target_frame": {"view_date": "2026-09-16", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_iid_0046", "author": "Carol", "actor": "Carol", "recipient": "Frank", "action": "bring", "object": "ticket", "quantity": 1, "record_date": "2026-09-15", "event_date": "2026-09-15", "record_status": "reported_completed", "polarity": "negative", "attribution": "Carol"}`
- 输出：Author: Carol. Record date: 2026-09-15. The subject of the record is Carol's report of not bringing one ticket to Frank, with the event dated yesterday.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 5. test_iid_0048 / Shift / T_minus_third

- 原句：Author: Alice. Record date: 2026-08-05. The record describes Alice's plan to give six parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-06", "perspective": "third"}, "target_frame": {"view_date": "2026-08-05", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_iid_0048", "author": "Alice", "actor": "Alice", "recipient": "David", "action": "give", "object": "parcel", "quantity": 6, "record_date": "2026-08-05", "event_date": "2026-08-05", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Alice"}`
- 输出：Author: Alice. Record date: 2026-08-05. The record describes Alice's plan to give six parcels to David, with the event dated yesterday. This record does not establish that the event occurred.
- 判定：joint=False，frame=False，content=False，unresolved=False，原因=None。

### 6. test_iid_0055 / LowRank16 / T_minus_third

- 原句：Author: Grace. Record date: 2026-09-19. The event is dated two days ago in the record describing Grace's report of delivering three books to Henry.
- 框架：`{"source_frame": {"view_date": "2026-09-20", "perspective": "third"}, "target_frame": {"view_date": "2026-09-19", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_iid_0055", "author": "Grace", "actor": "Grace", "recipient": "Henry", "action": "deliver", "object": "book", "quantity": 3, "record_date": "2026-09-19", "event_date": "2026-09-18", "record_status": "reported_completed", "polarity": "positive", "attribution": "Grace"}`
- 输出：Author: Grace. Record date: 2026-09-19. The event is dated yesterday in the record describing Grace's report of delivering three books to Henry.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 7. test_iid_0059 / Shift / P_31_third

- 原句：Author: Henry. Record date: 2026-08-21. Henry's cancelled plan to bring two tickets to Emma, with the event dated in two days, is described in the record. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-22", "perspective": "third"}, "target_frame": {"view_date": "2026-08-22", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_iid_0059", "author": "Henry", "actor": "Henry", "recipient": "Emma", "action": "bring", "object": "ticket", "quantity": 2, "record_date": "2026-08-21", "event_date": "2026-08-24", "record_status": "reported_cancelled", "polarity": "positive", "attribution": "Henry"}`
- 输出：Author: Henry. Record date: 2026-08-21. My cancelled plan to bring two tickets to Emma, with the event dated in two days, is described in the record. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 8. test_iid_0066 / LowRank16 / P_31_third

- 原句：Author: Bob. Record date: 2026-08-19. According to the record, Bob's plan to send seven sensors to Alice concerns an event dated today. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-20", "perspective": "third"}, "target_frame": {"view_date": "2026-08-20", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_iid_0066", "author": "Bob", "actor": "Bob", "recipient": "Alice", "action": "send", "object": "sensor", "quantity": 7, "record_date": "2026-08-19", "event_date": "2026-08-20", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Bob"}`
- 输出：Author: Bob. Record date: 2026-08-19. According to the record, my plan to send seven sensors to Alice concerns an event dated today. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 9. test_template_ood_0001 / Shift / T_plus_first

- 原句：Author: Grace. Record date: 2026-07-03. It is my report of not giving four parcels to Emma that the record describes for an event dated yesterday.
- 框架：`{"source_frame": {"view_date": "2026-07-04", "perspective": "first"}, "target_frame": {"view_date": "2026-07-05", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_template_ood_0001", "author": "Grace", "actor": "Grace", "recipient": "Emma", "action": "give", "object": "parcel", "quantity": 4, "record_date": "2026-07-03", "event_date": "2026-07-03", "record_status": "reported_completed", "polarity": "negative", "attribution": "Grace"}`
- 输出：Author: Grace. Record date: 2026-07-03. It is my report of not giving four parcels to Emma that the record describes for an event dated yesterday.
- 判定：joint=False，frame=False，content=False，unresolved=False，原因=None。

### 10. test_template_ood_0008 / LowRank16 / T_plus_first

- 原句：Author: Emma. Record date: 2026-08-03. What the record describes for an event dated today is my cancelled plan to send four parcels to Grace. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-04", "perspective": "first"}, "target_frame": {"view_date": "2026-08-05", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_template_ood_0008", "author": "Emma", "actor": "Emma", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 4, "record_date": "2026-08-03", "event_date": "2026-08-04", "record_status": "reported_cancelled", "polarity": "positive", "attribution": "Emma"}`
- 输出：Author: Emma. Record date: 2026-08-03. What the record describes for an event dated yesterday is my cancelled plan to send four parcels to Grace. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 11. test_template_ood_0039 / Shift / P_13_first

- 原句：Author: Frank. Record date: 2026-07-21. The event date assigned in the record to my plan to deliver five parcels to Carol is tomorrow. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-07-22", "perspective": "first"}, "target_frame": {"view_date": "2026-07-22", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_template_ood_0039", "author": "Frank", "actor": "Frank", "recipient": "Carol", "action": "deliver", "object": "parcel", "quantity": 5, "record_date": "2026-07-21", "event_date": "2026-07-23", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Frank"}`
- 输出：Author: Frank. Record date: 2026-07-21. The event date assigned in the record to Frank's plan to deliver five parcels to Carol is tomorrow. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 12. test_template_ood_0054 / LowRank16 / P_13_first

- 原句：Author: Emma. Record date: 2026-08-27. As described in the record, my plan to send six sensors to Henry has the event dated tomorrow. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-28", "perspective": "first"}, "target_frame": {"view_date": "2026-08-28", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_template_ood_0054", "author": "Emma", "actor": "Emma", "recipient": "Henry", "action": "send", "object": "sensor", "quantity": 6, "record_date": "2026-08-27", "event_date": "2026-08-29", "record_status": "recorded_plan", "polarity": "positive", "attribution": "Emma"}`
- 输出：Author: Emma. Record date: 2026-08-27. As described in the record, Emma's plan to send six sensors to Henry has the event dated tomorrow. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 13. test_template_ood_0058 / Shift / T_minus_third

- 原句：Author: Alice. Record date: 2026-07-29. As described in the record, Alice's report of giving six books to Emma has the event dated two days ago.
- 框架：`{"source_frame": {"view_date": "2026-07-30", "perspective": "third"}, "target_frame": {"view_date": "2026-07-29", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_template_ood_0058", "author": "Alice", "actor": "Alice", "recipient": "Emma", "action": "give", "object": "book", "quantity": 6, "record_date": "2026-07-29", "event_date": "2026-07-28", "record_status": "reported_completed", "polarity": "positive", "attribution": "Alice"}`
- 输出：Author: Alice. Record date: 2026-07-29. As described in the record, Alice's report of giving six books to Emma has the event dated two days ago.
- 判定：joint=False，frame=False，content=False，unresolved=False，原因=None。

### 14. test_template_ood_0061 / LowRank16 / T_minus_third

- 原句：Author: Frank. Record date: 2026-07-13. It is Frank's report of not bringing four parcels to Bob that the record describes for an event dated two days ago.
- 框架：`{"source_frame": {"view_date": "2026-07-14", "perspective": "third"}, "target_frame": {"view_date": "2026-07-13", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_template_ood_0061", "author": "Frank", "actor": "Frank", "recipient": "Bob", "action": "bring", "object": "parcel", "quantity": 4, "record_date": "2026-07-13", "event_date": "2026-07-12", "record_status": "reported_completed", "polarity": "negative", "attribution": "Frank"}`
- 输出：Author: Frank. Record date: 2026-07-13. It is Frank's report of not bringing four parcels to Bob that the record describes for an event dated yesterday.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 15. test_template_ood_0064 / Shift / P_31_third

- 原句：Author: David. Record date: 2026-07-01. What the record describes for an event dated yesterday is David's report of sending three parcels to Carol.
- 框架：`{"source_frame": {"view_date": "2026-07-02", "perspective": "third"}, "target_frame": {"view_date": "2026-07-02", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_template_ood_0064", "author": "David", "actor": "David", "recipient": "Carol", "action": "send", "object": "parcel", "quantity": 3, "record_date": "2026-07-01", "event_date": "2026-07-01", "record_status": "reported_completed", "polarity": "positive", "attribution": "David"}`
- 输出：Author: David. Record date: 2026-07-01. What the record describes for an event dated yesterday is my report of sending three parcels to Carol.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 16. test_template_ood_0077 / LowRank16 / P_31_third

- 原句：Author: Alice. Record date: 2026-09-10. It is Alice's cancelled plan to not send eight books to Bob that the record describes for an event dated two days ago. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-09-11", "perspective": "third"}, "target_frame": {"view_date": "2026-09-11", "perspective": "first"}}`
- 目标语义：`{"record_id": "test_template_ood_0077", "author": "Alice", "actor": "Alice", "recipient": "Bob", "action": "send", "object": "book", "quantity": 8, "record_date": "2026-09-10", "event_date": "2026-09-09", "record_status": "reported_cancelled", "polarity": "negative", "attribution": "Alice"}`
- 输出：Author: Alice. Record date: 2026-09-10. It is my cancelled plan to not send eight books to Bob that the record describes for an event dated two days ago. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 17. test_iid_0000 / Shift / time_then_person/latent_chain

- 原句：Author: Emma. Record date: 2026-08-23. The record describes my plan to not send seven parcels to Grace, with the event dated two days ago. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-24", "perspective": "first"}, "middle_frame": {"view_date": "2026-08-25", "perspective": "first"}, "target_frame": {"view_date": "2026-08-25", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_iid_0000", "author": "Emma", "actor": "Emma", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 7, "record_date": "2026-08-23", "event_date": "2026-08-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma"}`
- 输出：Author: Emma. Record date: 2026-08-23. The record describes Emma's plan to not send three parcels to Grace, with the event dated two days ago. This record does not establish that the event occurred.
- 判定：joint=False，frame=False，content=False，unresolved=False，原因=None。

### 18. test_iid_0000 / LowRank16 / time_then_person/latent_chain

- 原句：Author: Emma. Record date: 2026-08-23. The record describes my plan to not send seven parcels to Grace, with the event dated two days ago. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-24", "perspective": "first"}, "middle_frame": {"view_date": "2026-08-25", "perspective": "first"}, "target_frame": {"view_date": "2026-08-25", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_iid_0000", "author": "Emma", "actor": "Emma", "recipient": "Grace", "action": "send", "object": "parcel", "quantity": 7, "record_date": "2026-08-23", "event_date": "2026-08-22", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Emma"}`
- 输出：Author: Emma. Record date: 2026-08-23. The record describes Emma's plan to not send seven parcels to Grace, with the event dated three days ago. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

### 19. test_template_ood_0000 / Shift / time_then_person/latent_chain

- 原句：Author: Bob. Record date: 2026-08-10. What the record describes for an event dated two days ago is my plan to not bring nine sensors to Carol. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-11", "perspective": "first"}, "middle_frame": {"view_date": "2026-08-12", "perspective": "first"}, "target_frame": {"view_date": "2026-08-12", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_template_ood_0000", "author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "bring", "object": "sensor", "quantity": 9, "record_date": "2026-08-10", "event_date": "2026-08-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob"}`
- 输出：Author: Bob. Record date: 2026-08-10. What the record describes for an event dated two days ago is Bob's plan to not bring nine sensors to Carol. This record does not establish that the event occurred.
- 判定：joint=False，frame=False，content=False，unresolved=False，原因=None。

### 20. test_template_ood_0000 / LowRank16 / time_then_person/latent_chain

- 原句：Author: Bob. Record date: 2026-08-10. What the record describes for an event dated two days ago is my plan to not bring nine sensors to Carol. This record does not establish that the event occurred.
- 框架：`{"source_frame": {"view_date": "2026-08-11", "perspective": "first"}, "middle_frame": {"view_date": "2026-08-12", "perspective": "first"}, "target_frame": {"view_date": "2026-08-12", "perspective": "third"}}`
- 目标语义：`{"record_id": "test_template_ood_0000", "author": "Bob", "actor": "Bob", "recipient": "Carol", "action": "bring", "object": "sensor", "quantity": 9, "record_date": "2026-08-10", "event_date": "2026-08-09", "record_status": "recorded_plan", "polarity": "negative", "attribution": "Bob"}`
- 输出：Author: Bob. Record date: 2026-08-10. What the record describes for an event dated three days ago is Bob's plan to not bring nine sensors to Carol. This record does not establish that the event occurred.
- 判定：joint=True，frame=True，content=True，unresolved=False，原因=None。

## 文件与复现

准备脚本：prepare.py、configure.py（已有冻结文件时拒绝覆盖）。GPU入口：run_e0.slurm、run_train.slurm、run_eval.slurm（必须先核算剩余累计预算，再指定更短时限；不能重置预算）。train.py按相同seed/路径顺序恢复latest.pt的optimizer和RNG；evaluate_locked.py按uid续写缺失输出，锁定best哈希必须相同。CPU汇总：`.venv/bin/python experiments/reference_frame_pilot_v1/analyze.py`，报告：同路径report.py。

PROTOCOL.md、config.json、source_model_manifest.json、frozen_manifest.json、checkpoints/locked.json、commands.log、budget.json给出冻结与执行证据。未更改旧实验、未运行HE、未发布或推送。本报告不作新颖性承诺。
