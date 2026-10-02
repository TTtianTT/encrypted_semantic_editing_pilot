# 错误审计



所有错误按原始逐例输出保留。数量包含同世界的多个方向、来源、轨迹和步骤，不是独立样本数。受控规则未解析不会被算成功；语法标签不是通用语法判断。



|模型|领域|类型|计数|
|---|---|---|---|
|bart|emotion|controlled_grammar_invalid|1627|
|bart|emotion|unresolved_parse|679|
|bart|emotion|non_target_changed|116|
|bart|person|unresolved_parse|41973|
|bart|person|participant_or_owner_binding|15199|
|bart|person|controlled_grammar_invalid|9816|
|bart|person|current_text_already_wrong|8608|
|bart|person|non_target_changed|3208|
|bart|person|current_correct_next_target_wrong|7|
|bart|person|target_wrong|3|
|bart|space|non_target_changed|837|
|bart|space|unresolved_parse|97|
|bart|space|controlled_grammar_invalid|67|
|bart|time|unresolved_parse|35373|
|bart|time|target_wrong|22779|
|bart|time|current_text_already_wrong|19128|
|bart|time|historical_quote_scope|7830|
|bart|time|current_correct_next_target_wrong|7437|
|bart|time|controlled_grammar_invalid|3993|
|bart|time|non_target_changed|571|
|t5gemma|time|current_correct_next_target_wrong|6159|
|t5gemma|time|unresolved_parse|4182|
|t5gemma|time|controlled_grammar_invalid|3511|
|t5gemma|time|current_text_already_wrong|3320|
|t5gemma|time|target_wrong|2359|
|t5gemma|time|historical_quote_scope|1532|
|t5gemma|time|non_target_changed|786|



案例按固定hash在每个模型/领域/错误类型中取前6，未按最好seed或最大差选取。failure_cases.jsonl保留源/当前/输出/gold与分项指标，可检查当前已错、当前正确续步错、参与者/所有者绑定、非目标改动和历史引语作用域等。时间目标错误不自动称为“锚点选择错误”，除非直接引语或明确固定锚点保持规则支持该归因。



BART工程试跑的情感重构输出有重复/损坏词及句式变化，空间有对象名改写；评分器修复了合理协调/it指代，未接受客观事实丢失。T5Gemma原Return提示丢弃视角标签；统一Copy-exact dev接口复核通过后才冻结正式提示，工程原始结果保留。



core单步准入、未训练expression/structure单步、固定来源续步和自身完整路径分开检查。不能用source自身正确率的筛选变化，伪装为同一固定cohort的改善。固定同全文/同mask/depth1交集与全候选覆盖均保留，空cohort为NA。



修复与退化可以同时发生；capability_regressions.csv逐seed给P成功损失及P失败修复，不能只给净增量。机制probe的可读性不证明变量被使用，有限角色槽/常量锚点标签的限制已明示。


连续生成未解析与已解析的语义错误分开。固定18例的助手审阅记录是存在性案例证据，不是对全部未解析预测的独立标注。原空间朝向状态划分有解释限制；关系确认独立运行，旧结果不被改写。语言结构重构/原子准入失败先归入该结构基本能力限制，不进入组合失败平均。
