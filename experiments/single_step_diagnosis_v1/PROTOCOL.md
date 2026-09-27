# 单步回溯诊断 v1（先任务审核，再生成）

仅用既有StylePTB TFU测试来源，按source_id排序去规范化重复，random.Random(20260928)抽100，再按source_id排序编号。已使用数据，探索性诊断。选择现有两种检查点共同最小seed42：Shift延长5000步的开发best4800，低秩rank64预算1000步的开发best600；不能把不等预算结果解释为架构性能上限。不训练、不换模型、不扫描、不用clean_composition_v1。

任务模型复核在生成前完成；只读x、y，记录valid/invalid/uncertain及逐源理由。审查者为Codex（GPT-6系列，运行界面未提供精确模型修订号），非真人，已接触项目与历史案例，不是独立盲评。PTB小写、缺末尾句号、分词空格、分数转义和可辨认的引语省略不自动判失败；实际谓词缺失、助动词错位、角色改变仍判失败。时间定位不明/模态多义保留uncertain。valid固定后不因模型结果改标签，invalid/uncertain不替换。

同一BART冻结eval/float32，长度96、不截断输入、各输入自身mask、greedy beams1/max_new_tokens100/forced_eos=None、解码去特殊token但不clean tokenization spaces。四路径源还原、目标还原、Shift(E(x))、Lowrank(E(x))。y仅进入目标还原和离线评分。全部重新自由生成，不复用旧输出；之后可核对旧输出。先用前3抽中来源做直接generate vs encoder_outputs封装、identity Editor逐元素一致与mask长度检查。

输出评分：逐个来源查看四个输出，记录time/meaning/readability的pass/fail/uncertain和可核查理由；仅全pass计确认联合通过。identity_source时间维是保留原有时态，不要求未来；identity_target意义相对y，时间维检查y中的未来目标；编辑意义相对x，仅容许必要时间变化。即使任务invalid，也保留评分并标记不适用主比较；不强行称y为“正确”目标。源句/参考自身错误与还原新增错误单列。

输出模型复核可接触方法信息，标为非独立模型复核；另导出方法匿名表与分开的映射，真人字段全部空白。不给相同字符串机械赋成功；先语义审查x/y及输出，完全一致但本身有误的参考仍可失败。模型评分不是人工真值。

汇总所有100源、固定valid源及invalid/uncertain分层。主配对比较仅固定valid来源；来源bootstrap2000次，种子20260928，区间不含单检查点/单评分者不确定性。输出评分含uncertain而无fail者为联合uncertain，保守计不通过、乐观计通过，并报告方法相反处理的极端差值。另报将任务uncertain纳入时的结果但不混入主valid。任务invalid不纳入主能力比较。

诊断子集为固定valid中两种还原均确认通过的来源；报告n及编辑结果，不能取代全valid。四种编辑通过/未确认通过的交叉表及pass/fail/uncertain完整3×3表均保留。错误类别可重叠：输入/参考、重建新增错误、时态、角色、信息、否定/数字、语法。正确目标还原不是上界。还原通过而编辑失败只定位到编辑后的路径，不能排除隐表示与解码器交互。

单sbatch+srun、1GPU4CPU，作业上限20分钟，程序15分钟；记录显存峰值与实际作业用量，结果出现后不追加训练或实验。
