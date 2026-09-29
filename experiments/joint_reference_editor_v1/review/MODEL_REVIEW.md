# 模型复核记录（非真人审核）

复核范围：读取训练前预选的20个世界（IID/OOD各10）的源、目标、Joint16/32输出和两种G1顺序的各阶段输出；另读取两种顺序终点的全部15条未决输出（折叠逐token相同，不重复计数）。这没有改变任何评分、训练配置或确认集分母；human_label/human_notes保持空白。

20个配对案例中，联合方法保留了人数角色、对象、数量、计划/取消/报告状态、否定、记录日期和证据限定句。观察到的顺序组合失败主要是第二步把日期又改错：例如IID0009应tomorrow→today并改为Bob，两个顺序的终点却为yesterday；OOD0033应yesterday→two days ago并改为Alice，两个终点却为today。IID0006时间第一步正确，但随后人称编辑把tomorrow改为in three days。这里只解释已保存例子，不用便利复核估计总体错误率。

未决输出按冻结评分器原因分为12条missing_evidence_scope、3条unsupported_clause_or_additional_assertion。前12条实际遗漏了“This record does not establish that the event occurred.”限定句，其中也有日期错误；遗漏不等于明确宣称事件已经完成。其余3条值得真人核对：

- 人称→时间，IID0012/0014：输出将“contains an account of …”缩成“contains …”，人物、数量、否定/取消、日期和证据限定仍在；模型复核认为可能是可接受改写。
- 人称→时间，OOD0018：输出in one day对应目标tomorrow，其余内容相同，模型复核认为是正确日期替代表达。

自动主表仍将这些列为未决、不能确认成功，不在看到测试后扩展parser或偷偷提高旧分数。没有观察到联合方法的事实损坏或未决案例，不能为凑类别编造失败；也不能从有限样本零错误推断总体绝对可靠。

完整原始15条未决文本保留在outputs/Sequential_*.jsonl及其逐阶段评分中；20个固定世界的全方法数据见cases.jsonl、匿名blind_review.csv和CASES.md。审查映射单独存放private_mapping.json。
