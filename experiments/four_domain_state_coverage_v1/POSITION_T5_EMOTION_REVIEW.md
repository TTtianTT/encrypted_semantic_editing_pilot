# 情感目标对象与Narrator范围的固定顺序案例

助手审阅T5Gemma三个seed、emotion_0120、neutral状态2、plus的四个表达变体共12个原子输出，依据固定首世界选择而非按成败筛选。两对分别是多对象原/反顺序和第一人称Narrator/引语原/反顺序；两对的完整语义结构不同，不互相当同一完整状态配对。原文本、gold和哈希见POSITION_FIXED_REVIEW_CASES。不是12个独立世界或总体人工标注。

三seed在这个固定世界均产生相同的四类结果：

- 多对象原顺序0：正确把Alice对parcel从neutral改成likes；Henry neutral、非目标Alice dislikes the box、blue和9 copies保持。该输出完整成功。
- 多对象反顺序1：Alice对parcel仍neutral；处于第一个评价位置的非目标Alice对box从dislikes改成neutral。Henry neutral及客观事实保持，完整文本可解析且语法合法。这是明确的错误对象范围，不能凭出现neutral或Alice的名字判为目标评价已正确。
- 第一人称/引语顺序2：Narrator Alice头被丢弃，外部I am neutral未提高；Focus Alice、Henry评价和事实及David的原话保留。缺少规定的Narrator身份信息，原有限评分无法确认完整外部I绑定，不把全部未解析段落标为明确错误人物身份。外部等级没有成功提高。
- 引语在前的第一人称顺序3：Narrator头和历史David引语均丢失，外部I am neutral也未提高。区分目标变化失败、锚点信息和历史内容缺失。

所有四结构的dev重构均100%。三seed原顺序0均准入（dev原子98.96%、100%、100%），反顺序1为10.42%、1.56%、0%，均未准入；Narrator顺序2为0%、0%、26.04%，顺序3为0%、0%、0.52%，均未准入。反顺序和第一人称结构的失败属于基本范围/表达泛化失败，不作为latent组合失败平均。顺序0连续轨迹与已有多对象结构完全相同，依据全部输入和checkpoint等价性复用原Slurm预测并用位置评分重算，见POSITION_EXACT_REUSE_AUDIT。

这套原子训练中目标评价总在首个评价位置。固定顺序差异与全集position_order_pairs说明原先多对象成功不足以证明按Focus对象选择作用范围；位置敏感性与这些输入一致，尚未通过其他位置干预、受控补训或因果实验识别唯一机制。保留顺序0正确反例和seed44第一人称的部分成功，不作所有表达均失败的结论。
