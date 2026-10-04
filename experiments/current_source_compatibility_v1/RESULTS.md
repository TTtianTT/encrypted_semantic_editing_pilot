# 当前来源兼容性：实验结果



**当前工件快照；尚未全部完成，不能视为最终结论。**



模型google/t5gemma-2b-2b-ul2-it，原子T0 seeds42/43/44，各600步已选checkpoint；骨干冻结，两个rank16操作头共152064参数。N/F/R从各seed同一T0出发，各200 optimizer updates，800自然replay+800续步。训练覆盖全部合法当前状态及操作头输出标签；R仅一次前缀、每20更新重建、detach，不筛除错误。主checkpoint固定200，100仅诊断。



沿用96/24/32世界划分；IID与模板OOD共享32个测试世界，是同世界不同表达，不能当64个独立世界。旧自然测试768行/seed原样保留；IID/OOD穷举两步各704序列，长链每种模板在32个世界上合计256条序列、每步1–5。实际独立世界仍为32。U循环下一seed的原子T0，是来源对照，不是第四次训练重复。



## 原始能力与准入



|seed|重构|原子|gold续步|通过|
|---|---|---|---|---|
|42|100.00%|100.00%|100.00%|True|
|43|100.00%|100.00%|100.00%|True|
|44|100.00%|100.00%|100.00%|True|



准入针对原有核心dev。模板OOD是另外的表达留出测量，没有被当作通过核心准入即可保证的能力。其自然单步及gold-reencode对照单列，OOD失败同时可能包含表达识别不足。



|seed|条件|测试|自然单步macro|成功|
|---|---|---|---|---|
|42|T0|iid|100.00%|768/768|
|42|T0|ood|58.33%|224/384|
|43|T0|iid|100.00%|768/768|
|43|T0|ood|53.65%|206/384|
|44|T0|iid|100.00%|768/768|
|44|T0|ood|60.68%|233/384|



## 自身运行：逐seed主结果



|seed|条件|测试|第一步|第二步endpoint|两步完整|条件续步|
|---|---|---|---|---|---|---|
|42|T0|iid|704/704|0/704|0/704|0/704|
|42|T0|ood|384/704|0/704|0/704|0/384|
|43|T0|iid|704/704|0/704|0/704|0/704|
|43|T0|ood|348/704|33/704|2/704|2/348|
|44|T0|iid|704/704|0/704|0/704|0/704|
|44|T0|ood|402/704|52/704|30/704|30/402|



条件分母因模型而变化，不用于单独排名；错误前缀恢复可以提高endpoint，full2仍失败。长度2穷举集与后面的五步路径初始分布不同。



## 均值与范围



|条件|测试|来源|指标|seeds|均值|最小|最大|
|---|---|---|---|---|---|---|---|
|T0|iid|natural|atomic_macro|3|100.00%|100.00%|100.00%|
|T0|ood|natural|atomic_macro|3|57.55%|53.65%|60.68%|
|T0|iid|self|full2|3|0.00%|0.00%|0.00%|
|T0|ood|self|full2|3|1.52%|0.00%|4.26%|
|T0|iid|latent|full3_all|3|0.00%|0.00%|0.00%|
|T0|iid|latent|full4_all|3|0.00%|0.00%|0.00%|
|T0|iid|latent|full5_all|3|0.00%|0.00%|0.00%|
|T0|ood|latent|full3_all|3|0.00%|0.00%|0.00%|
|T0|ood|latent|full4_all|3|0.00%|0.00%|0.00%|
|T0|ood|latent|full5_all|3|0.00%|0.00%|0.00%|



均值及范围保留训练seed层级；逐seed结果为主。条件成功率无有效分母时记NA，不补零。完整分项另见mean_and_range.csv、continuation_cells.csv、sequence_metrics.csv及quality_metrics.csv。



## R−F、F−N：固定世界配对



|seed|对比|测试|来源|指标|集合|差值pp|世界CI|世界|
|---|---|---|---|---|---|---|---|---|



2000次按世界聚类的paired bootstrap，共享世界及其所有序列；区间只描述固定训练模型的内容抽样，不含完整训练随机性。零差区间[0,0]不证明总体效应严格为零。



## 长度迁移与重编码控制



|seed|条件|测试|方法|指标|成功|
|---|---|---|---|---|---|
|42|T0|iid|latent|full2_all|0/256|
|42|T0|iid|latent|full3_all|0/256|
|42|T0|iid|latent|full4_all|0/256|
|42|T0|iid|latent|full5_all|0/256|
|42|T0|iid|gold_reencode|full2_all|256/256|
|42|T0|iid|gold_reencode|full3_all|256/256|
|42|T0|iid|gold_reencode|full4_all|256/256|
|42|T0|iid|gold_reencode|full5_all|256/256|
|42|T0|iid|actual_reencode|full2_all|256/256|
|42|T0|iid|actual_reencode|full3_all|256/256|
|42|T0|iid|actual_reencode|full4_all|256/256|
|42|T0|iid|actual_reencode|full5_all|256/256|
|42|T0|ood|latent|full2_all|0/256|
|42|T0|ood|latent|full3_all|0/256|
|42|T0|ood|latent|full4_all|0/256|
|42|T0|ood|latent|full5_all|0/256|
|42|T0|ood|gold_reencode|full2_all|96/256|
|42|T0|ood|gold_reencode|full3_all|64/256|
|42|T0|ood|gold_reencode|full4_all|64/256|
|42|T0|ood|gold_reencode|full5_all|64/256|
|42|T0|ood|actual_reencode|full2_all|128/256|
|42|T0|ood|actual_reencode|full3_all|128/256|
|42|T0|ood|actual_reencode|full4_all|128/256|
|42|T0|ood|actual_reencode|full5_all|128/256|
|43|T0|iid|latent|full2_all|0/256|
|43|T0|iid|latent|full3_all|0/256|
|43|T0|iid|latent|full4_all|0/256|
|43|T0|iid|latent|full5_all|0/256|
|43|T0|iid|gold_reencode|full2_all|256/256|
|43|T0|iid|gold_reencode|full3_all|256/256|
|43|T0|iid|gold_reencode|full4_all|256/256|
|43|T0|iid|gold_reencode|full5_all|256/256|
|43|T0|iid|actual_reencode|full2_all|256/256|
|43|T0|iid|actual_reencode|full3_all|256/256|
|43|T0|iid|actual_reencode|full4_all|256/256|
|43|T0|iid|actual_reencode|full5_all|256/256|
|43|T0|ood|latent|full2_all|0/256|
|43|T0|ood|latent|full3_all|0/256|
|43|T0|ood|latent|full4_all|0/256|
|43|T0|ood|latent|full5_all|0/256|
|43|T0|ood|gold_reencode|full2_all|80/256|
|43|T0|ood|gold_reencode|full3_all|64/256|
|43|T0|ood|gold_reencode|full4_all|64/256|
|43|T0|ood|gold_reencode|full5_all|64/256|
|43|T0|ood|actual_reencode|full2_all|96/256|
|43|T0|ood|actual_reencode|full3_all|96/256|
|43|T0|ood|actual_reencode|full4_all|96/256|
|43|T0|ood|actual_reencode|full5_all|96/256|
|44|T0|iid|latent|full2_all|0/256|
|44|T0|iid|latent|full3_all|0/256|
|44|T0|iid|latent|full4_all|0/256|
|44|T0|iid|latent|full5_all|0/256|
|44|T0|iid|gold_reencode|full2_all|256/256|
|44|T0|iid|gold_reencode|full3_all|256/256|
|44|T0|iid|gold_reencode|full4_all|256/256|
|44|T0|iid|gold_reencode|full5_all|256/256|
|44|T0|iid|actual_reencode|full2_all|256/256|
|44|T0|iid|actual_reencode|full3_all|256/256|
|44|T0|iid|actual_reencode|full4_all|256/256|
|44|T0|iid|actual_reencode|full5_all|256/256|
|44|T0|ood|latent|full2_all|0/256|
|44|T0|ood|latent|full3_all|0/256|
|44|T0|ood|latent|full4_all|0/256|
|44|T0|ood|latent|full5_all|0/256|
|44|T0|ood|gold_reencode|full2_all|105/256|
|44|T0|ood|gold_reencode|full3_all|64/256|
|44|T0|ood|gold_reencode|full4_all|64/256|
|44|T0|ood|gold_reencode|full5_all|64/256|
|44|T0|ood|actual_reencode|full2_all|146/256|
|44|T0|ood|actual_reencode|full3_all|146/256|
|44|T0|ood|actual_reencode|full4_all|146/256|
|44|T0|ood|actual_reencode|full5_all|146/256|



全部endpoint、条件分母、路径family、100步checkpoint和首次失败位置在CSV。纯latent只在第一步前编码；gold重编码使用正确当前文本，是能力控制；actual重编码回灌原始真实输出，无清洗或gold替换。二者分别报告。



## 旧自然能力：平均值与逐例损失



|seed|条件|update|macro|相对T0pp|旧成功损失|旧失败修复|保留判据|
|---|---|---|---|---|---|---|---|
|42|N|100|100.00%|+0.00|0|0|True|



每个seed独立采用下降≤2pp工作判据；仍保留全部损失ID、状态及操作，不能只凭macro声称旧能力完好。



## 训练来源质量及收益归属



|seed|条件|刷新|实际监督单位|正确前缀|已知相对状态错误|内容缺失或改变|评分未定|
|---|---|---|---|---|---|---|---|
|42|N|0|800|800|0|0|0|
|43|N|0|800|800|0|0|0|



错误类别可重叠，未解析/relative未知不算已证实语义错误。没有删除、替换、重新抽样或加权失败输入。prefix_quality另给唯一前缀与全池权重；实际监督表按对应20更新窗口的draws计数。正确前缀条件续步、失败前缀端点恢复、已知错误relative恢复与未定前缀恢复在summary分别列。后两类恢复不能解释为当前正确续步修复。repair_attribution.csv另将配对full2差值按双方前缀是否正确分解：endpoint差值=full2差值+失败前缀恢复差值；这些更新后分层是描述性分析，不能替换训练前固定诊断集或总体主指标。



## 补训前固定诊断集



|seed|条件|测试|来源|两步完整|
|---|---|---|---|---|



成员由T0第一步与T0 gold-current-reencode下一步同时成功确定，在正式训练前冻结。每个方法使用全部原始成员；更新后第一步变错计入自身full2失败。不会按更新后成功重新筛选。



## 七个研究问题



1. R是否优于F：IID自身full2 尚未完成；固定T0 尚未完成；U 尚未完成。不能用条件成功率独立排名。

2. 长度迁移：IID纯latent full3 尚未完成；full4 尚未完成；full5 尚未完成。每一步完整率的绝对计数见表；端点恢复不等于完整长链。

3. 更新后的自身输出能力由第一步、full2、条件续步及固定诊断集共同判断，详见逐seed表。仅固定来源成功不代表自身成功；第一步失败不能被条件筛选隐藏。

4. 来源与表达迁移：模板OOD自身full2 尚未完成；OOD U 尚未完成。U冻结且独立于该运行补训，仍只是三个原子编辑器间的来源对照。

5. 旧自然单步是否退化：按每个seed、条件的≤2pp规则及旧成功损失表判断，全部损失ID保留。平均分维持也可能掩盖不同样本的一失一得。

6. 收益归属：训练刷新表及测试前缀分项区分正确前缀续步与失败前缀端点恢复；已知错误relative、内容缺失及评分未定另列。恢复错误/未定前缀不支持当前正确续步被修复的解释。

7. GPU开销：每个seed的源刷新pipeline及optimizer时间见RESOURCE_USAGE。刷新时间包含新编码、前缀调用、质量解码与缓存I/O，额外分配GPU时间如实记录；累计allocation包括技术失败和恢复。



观察仅限于本模型、数据、rank16双头编辑器和200更新设置。即使R有帮助也不证明来源滞后是唯一失败机制。没有追加领域、probe、范围挑战或超参数搜索。



累计2.908333 allocation GPUh，本项目峰值2，本轮开始后账号峰值2。未完成列表见ANALYSIS_AUDIT。
