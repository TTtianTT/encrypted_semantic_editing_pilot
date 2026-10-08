# Original T5Gemma BF16 SAME_TEXT re-audit

状态 COMPLETED；Slurm 3037_0；实际 GPU-hours 0.075278。原版 google/t5gemma-2b-2b-ul2-it，未替换模型/精度。

固定 train16/validation16 worlds，分别16/16严格资格、16 pair；合计32/32world、32pair。资格不要求next fork。来源计数 {'E_future_plus:E_past_minus': 32}；有效memory差值最大范数 444.502625。共同前缀768token记录，最大全词表JS 3.717842628e-05。下一步正确性分叉 0/64；原始生成token分叉 63/64，二者分别重算。

这是探索性配对存在性证据。每split只有16独立world，未达到40-world确认门槛；独立test扫描0，固定test池完整128独立终点因5个派生core暴露已阻塞，不能把32探索world写成独立机制确认。旧报告无next-edit-fork不等于本面板不存在。

已完成S0 native/梯度/8world过拟合验收和本小规模S1概率分析；未完成本模型候选选择/S2因果确认/三个seed新方法强对照/长期独立评测。没有复用BART同号head或hidden basis。机制增量收益NA。资格诊断中N/E/R允许按来源规则比较；它不是无需donor主编辑器效果。

完整资格/排除/逐token分数和桥接预测压缩提交；大memory/cache索引及SHA见ARTIFACTS.json；模型、split、来源和不可变代码SHA见RUN_STATUS与manifest。
