# 空间关系状态确认结果

仍在运行或存在缺失任务；本文件是当前工件快照，不能当作全部完成。

## 空间关系状态确认：独立结果



状态0front/1right/2back/3left；plus物理朝向顺时针90度，关系状态减1。S只补训front，M补训front/back，right与left仅自然原子训练见过，未补训其编辑态续步。原世界坐标、人物、split和自然原子文本对集合不变。



|模型|seed|重构|原子|gold续步|准入|
|---|---|---|---|---|---|
|bart|42|78.65%|56.77%|56.77%|False|
|bart|43|78.65%|54.69%|54.69%|False|
|bart|44|78.65%|54.43%|54.43%|False|



|模型|seed|划分|世界|S|M|M减S|
|---|---|---|---|---|---|---|



完整逐seed/group CSV与mean_and_range保存在space_relation_confirmation_v1。来源/状态/表达交叉保存在主目录transfer_quad.csv；字面全文与标准化全文匹配分别保存在literal_fulltext*及same_text_source_disagreement.csv。cross_backbone_fixed_worlds给共同内容世界/当前全文集合以及各backbone自己的覆盖；跨backbone token mask不能相同，限制另存JSON。

完整综合报告位于../four_domain_state_coverage_v1/RESULTS.md，逐seed原始CSV/预测/checkpoint在本目录。
