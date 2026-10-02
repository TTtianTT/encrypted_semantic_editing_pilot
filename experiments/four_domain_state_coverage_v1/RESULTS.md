# 四领域连续表示编辑：结果

本轮整体状态：**仍在运行或存在缺失任务；本文件是当前工件快照，不能当作全部完成。**

空间原协议按绝对朝向分层，不能据此声称留出了相对关系状态；它的行为/退化工件全部保留。主状态泛化问题使用独立预注册的关系确认版，语义与更正时间见POSTFORMAL_SEMANTIC_AUDIT.md。确认版重新初始化原子编辑器，训练文本集合相同但抽样行序改变，原版与确认版的差异不能只归因于补训覆盖。





**状态：仍在运行；以下是已写入工件的观察，不是全轮最终结论。**

正式完成N/S/M组合7/24；未通过准入6/24；来源训练不可行0；符号对照完成0/8。独立重评分预测445,824条。每领域96/24/32个train/dev/test内容世界，各改写/轨迹共享世界划分。



实际模型是冻结facebook/bart-base和google/t5gemma-2b-2b-ul2-it。仓库270M为预训练版、旧重构准入失败，不是已通过准入的270M IT；见AUDIT、model_manifest及EXPERIMENT_PLAN。结果不外推为所有语言模型性质。



## 准入：逐模型、领域、seed



门槛：重构≥95%，自然原子和gold-current-reencode续步macro≥85%、每state/sign cell≥75%。选择仅看600步原子训练期间完整dev NLL；N/S/M均final200。失败组合保留，未训练其N/S/M。



|模型|领域|seed|输入|重构|原子|最低原子cell|gold续步|准入|
|---|---|---|---|---|---|---|---|---|
|bart|emotion|42|formal|10.42%|36.98%|29.17%|39.24%|False|
|bart|emotion|43|formal|10.42%|32.81%|16.67%|34.38%|False|
|bart|emotion|44|formal|10.42%|39.32%|25.00%|42.71%|False|
|bart|person|42|formal|100.00%|100.00%|100.00%|100.00%|True|
|bart|person|43|formal|100.00%|100.00%|100.00%|100.00%|True|
|bart|person|44|formal|100.00%|100.00%|100.00%|100.00%|True|
|bart|space（原朝向划分）|42|formal|78.65%|56.51%|52.08%|56.51%|False|
|bart|space（原朝向划分）|43|formal|78.65%|60.16%|50.00%|60.16%|False|
|bart|space（原朝向划分）|44|formal|78.65%|52.08%|50.00%|52.08%|False|
|bart|time|42|formal|100.00%|100.00%|100.00%|100.00%|True|
|bart|time|43|formal|100.00%|100.00%|100.00%|100.00%|True|
|bart|time|44|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|emotion|42|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|emotion|43|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|emotion|44|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|person|42|formal|99.31%|100.00%|100.00%|100.00%|True|
|t5gemma|person|43|formal|99.31%|100.00%|100.00%|100.00%|True|
|t5gemma|person|44|formal|99.31%|100.00%|100.00%|100.00%|True|
|t5gemma|space（原朝向划分）|42|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|space（原朝向划分）|43|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|space（原朝向划分）|44|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|time|42|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|time|43|formal|100.00%|100.00%|100.00%|100.00%|True|
|t5gemma|time|44|formal|100.00%|100.00%|100.00%|100.00%|True|



## 当前正确但不能继续



以下计数要求latent前一步语义正确、同世界的gold重编码下一步正确，但latent下一步失败。它比“终点错”更窄；不证明语义已丢失或任何纯latent编辑器不可能。重复路径/步骤不是独立世界。



|模型|领域|seed|失败|备注|
|---|---|---|---|---|
|bart|person|42|96/96|合计路径步骤；独立世界32|
|bart|person|43|96/96|合计路径步骤；独立世界32|
|bart|person|44|96/96|合计路径步骤；独立世界32|
|bart|time|42|96/96|合计路径步骤；独立世界32|
|bart|time|43|96/96|合计路径步骤；独立世界32|
|bart|time|44|96/96|合计路径步骤；独立世界32|
|t5gemma|space（原朝向划分）|42|96/96|合计路径步骤；独立世界32|
|t5gemma|time|42|96/96|合计路径步骤；独立世界32|
|t5gemma|time|43|96/96|合计路径步骤；独立世界32|
|t5gemma|time|44|96/96|合计路径步骤；独立世界32|



## M与S：留出当前状态 × 留出U来源



主表只列template0、预先固定P/Q/U当前全文及mask共同匹配集；两符号方向合计，rows不是独立世界。配对cohort不用下一步结果筛选。各来源全候选/current-correct覆盖及排除原因另见paired_cohort_coverage和summary_by_seed。



|模型|领域|seed|留出划分|世界|S|M|M减S|
|---|---|---|---|---|---|---|---|
|bart|time|42|0|32|54/64|0/64|-84.38pp|
|bart|time|42|1|32|15/64|0/64|-23.44pp|
|bart|time|43|0|32|0/64|0/64|+0.00pp|
|bart|time|43|1|32|0/64|0/64|+0.00pp|
|bart|time|44|0|32|15/64|0/64|-23.44pp|
|bart|time|44|1|32|0/64|0/64|+0.00pp|
|bart|person|42|0|32|0/64|0/64|+0.00pp|
|bart|person|42|1|32|0/64|0/64|+0.00pp|
|bart|person|43|0|32|0/64|0/64|+0.00pp|
|bart|person|43|1|32|0/64|0/64|+0.00pp|
|bart|person|44|0|32|0/64|0/64|+0.00pp|
|bart|person|44|1|32|0/64|0/64|+0.00pp|
|t5gemma|time|43|0|32|0/64|0/64|+0.00pp|
|t5gemma|time|43|1|32|0/64|0/64|+0.00pp|
|t5gemma|time|44|0|32|0/64|0/64|+0.00pp|
|t5gemma|space（原朝向划分）|42|0|32|59/64|64/64|+7.81pp|
|t5gemma|space（原朝向划分）|42|1|32|54/64|50/64|-6.25pp|



三seed均值与范围（缺seed时明确n）：



|模型|领域|留出划分|seed数|均值|范围|
|---|---|---|---|---|---|
|bart|person|0|3|+0.00pp|[+0.00,+0.00]pp|
|bart|person|1|3|+0.00pp|[+0.00,+0.00]pp|
|bart|time|0|3|-35.94pp|[-84.38,+0.00]pp|
|bart|time|1|3|-7.81pp|[-23.44,+0.00]pp|
|t5gemma|space（原朝向划分）|0|1|+7.81pp|[+7.81,+7.81]pp|
|t5gemma|space（原朝向划分）|1|1|-6.25pp|[-6.25,-6.25]pp|
|t5gemma|time|0|2|+0.00pp|[+0.00,+0.00]pp|
|t5gemma|time|1|1|+0.00pp|[+0.00,+0.00]pp|



没有使用bootstrap区间；均值与范围展示训练seed差异，不把同一世界的多种表面表达当独立样本。来源迁移、当前状态迁移、表达迁移分别在source_matrix、template和state标签中报告；自然规则全训练，留出只指编辑态续步未补训。完全未训练的结构组合在challenge中单列，不能混成同一种留出。



## 连续轨迹及恢复性



CSV逐步列endpoint、条件续步、完整轨迹、保持/范围/可解析/受控语法。此表列template0的正向纯latent完整终点；空间四步整圈、人称三步循环另列。



|模型|领域|seed|条件|步|endpoint|完整|条件续步|
|---|---|---|---|---|---|---|---|
|bart|person|42|P|3|0/32|0/32|NA|
|bart|person|42|P|5|0/32|0/32|NA|
|bart|person|42|M_h0|3|0/32|0/32|NA|
|bart|person|42|M_h0|5|0/32|0/32|NA|
|bart|person|42|S_h0|3|0/32|0/32|NA|
|bart|person|42|S_h0|5|0/32|0/32|NA|
|bart|person|42|N_h0|3|0/32|0/32|NA|
|bart|person|42|N_h0|5|0/32|0/32|NA|
|bart|person|43|P|3|0/32|0/32|NA|
|bart|person|43|P|5|0/32|0/32|NA|
|bart|person|43|M_h0|3|0/32|0/32|NA|
|bart|person|43|M_h0|5|0/32|0/32|NA|
|bart|person|43|S_h0|3|0/32|0/32|NA|
|bart|person|43|S_h0|5|0/32|0/32|NA|
|bart|person|43|N_h0|3|0/32|0/32|NA|
|bart|person|43|N_h0|5|0/32|0/32|NA|
|bart|person|44|P|3|0/32|0/32|NA|
|bart|person|44|P|5|0/32|0/32|NA|
|bart|person|44|M_h0|3|0/32|0/32|NA|
|bart|person|44|M_h0|5|0/32|0/32|NA|
|bart|person|44|S_h0|3|0/32|0/32|NA|
|bart|person|44|S_h0|5|0/32|0/32|NA|
|bart|person|44|N_h0|3|0/32|0/32|NA|
|bart|person|44|N_h0|5|0/32|0/32|NA|
|bart|time|42|P|5|0/32|0/32|NA|
|bart|time|42|M_h0|5|0/32|0/32|NA|
|bart|time|42|S_h0|5|0/32|0/32|NA|
|bart|time|42|N_h0|5|0/32|0/32|NA|
|bart|time|43|P|5|0/32|0/32|NA|
|bart|time|43|M_h0|5|0/32|0/32|NA|
|bart|time|43|S_h0|5|0/32|0/32|NA|
|bart|time|43|N_h0|5|0/32|0/32|NA|
|bart|time|44|P|5|0/32|0/32|NA|
|bart|time|44|M_h0|5|0/32|0/32|NA|
|bart|time|44|S_h0|5|0/32|0/32|NA|
|bart|time|44|N_h0|5|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|P|4|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|P|5|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|M_h0|4|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|M_h0|5|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|S_h0|4|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|S_h0|5|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|N_h0|4|0/32|0/32|NA|
|t5gemma|space（原朝向划分）|42|N_h0|5|0/32|0/32|NA|
|t5gemma|time|42|P|5|0/32|0/32|NA|
|t5gemma|time|42|S_h0|5|0/32|0/32|NA|
|t5gemma|time|42|N_h0|5|0/32|0/32|NA|
|t5gemma|time|43|P|5|0/32|0/32|NA|
|t5gemma|time|43|M_h0|5|0/32|0/32|NA|
|t5gemma|time|43|S_h0|5|0/32|0/32|NA|
|t5gemma|time|43|N_h0|5|0/32|0/32|NA|
|t5gemma|time|44|P|5|0/32|0/32|NA|
|t5gemma|time|44|M_h0|5|0/32|0/32|NA|
|t5gemma|time|44|S_h0|5|0/32|0/32|NA|
|t5gemma|time|44|N_h0|5|0/32|0/32|NA|



## 锚点、作用范围及旧能力



自然单步挑战与对应纯latent失败分开；template3/4/5及人称6是未训练结构，若单步不具备能力，不能归为组合失败。历史直接引语、固定绝对日期/坐标、未转身观察者、非目标评价、参与者/对象/所有者都独立计保持。合理受控释义被接受，未解析不判正确；不是开放语言评分器。



|模型|领域|seed|条件|单步成功|非目标保持|范围正确|
|---|---|---|---|---|---|---|
|bart|person|42|M_h0|45/768|116/768|116/768|
|bart|person|42|P|1/768|34/768|34/768|
|bart|person|42|S_h0|65/768|100/768|100/768|
|bart|person|43|M_h0|13/768|25/768|25/768|
|bart|person|43|P|3/768|42/768|42/768|
|bart|person|43|S_h0|36/768|71/768|71/768|
|bart|person|44|M_h0|13/768|61/768|61/768|
|bart|person|44|P|0/768|57/768|57/768|
|bart|person|44|S_h0|17/768|40/768|40/768|
|bart|time|42|M_h0|654/1152|654/1152|654/1152|
|bart|time|42|P|693/1152|695/1152|693/1152|
|bart|time|42|S_h0|618/1152|618/1152|618/1152|
|bart|time|43|M_h0|733/1152|736/1152|733/1152|
|bart|time|43|P|760/1152|762/1152|760/1152|
|bart|time|43|S_h0|768/1152|768/1152|768/1152|
|bart|time|44|M_h0|736/1152|736/1152|736/1152|
|bart|time|44|P|736/1152|736/1152|736/1152|
|bart|time|44|S_h0|739/1152|739/1152|739/1152|
|t5gemma|space（原朝向划分）|42|M_h0|322/768|322/768|322/768|
|t5gemma|space（原朝向划分）|42|P|252/768|253/768|253/768|
|t5gemma|space（原朝向划分）|42|S_h0|354/768|354/768|354/768|
|t5gemma|space（原朝向划分）|43|P|330/768|330/768|330/768|
|t5gemma|space（原朝向划分）|44|P|183/768|183/768|183/768|
|t5gemma|time|42|M_h0|616/1152|635/1152|616/1152|
|t5gemma|time|42|P|510/1152|510/1152|510/1152|
|t5gemma|time|42|S_h0|670/1152|670/1152|670/1152|
|t5gemma|time|43|M_h0|676/1152|676/1152|676/1152|
|t5gemma|time|43|P|491/1152|491/1152|491/1152|
|t5gemma|time|43|S_h0|732/1152|732/1152|732/1152|
|t5gemma|time|44|M_h0|645/1152|645/1152|645/1152|
|t5gemma|time|44|P|639/1152|639/1152|639/1152|
|t5gemma|time|44|S_h0|733/1152|733/1152|733/1152|



旧能力：以下只列自然core原子输入上P原本成功但补训后失败的计数；完整来源/表达/结构旧路径损伤另见capability_regressions.csv，改善不能抵消未报告的退化。



|模型|领域|seed|条件|划分|P成功|损失|修复|分母|
|---|---|---|---|---|---|---|---|---|
|bart|time|42|N|0|768|0|0|768|
|bart|time|42|S|0|768|0|0|768|
|bart|time|42|M|0|768|0|0|768|
|bart|time|42|N|1|768|0|0|768|
|bart|time|42|S|1|768|0|0|768|
|bart|time|42|M|1|768|0|0|768|
|bart|time|43|N|0|768|0|0|768|
|bart|time|43|S|0|768|0|0|768|
|bart|time|43|M|0|768|0|0|768|
|bart|time|43|N|1|768|0|0|768|
|bart|time|43|S|1|768|0|0|768|
|bart|time|43|M|1|768|0|0|768|
|bart|time|44|N|0|768|0|0|768|
|bart|time|44|S|0|768|0|0|768|
|bart|time|44|M|0|768|0|0|768|
|bart|time|44|N|1|768|0|0|768|
|bart|time|44|S|1|768|0|0|768|
|bart|time|44|M|1|768|0|0|768|
|bart|person|42|N|0|384|0|0|384|
|bart|person|42|S|0|384|0|0|384|
|bart|person|42|M|0|384|8|0|384|
|bart|person|42|N|1|384|0|0|384|
|bart|person|42|S|1|384|2|0|384|
|bart|person|42|M|1|384|2|0|384|
|bart|person|43|N|0|384|0|0|384|
|bart|person|43|S|0|384|0|0|384|
|bart|person|43|M|0|384|0|0|384|
|bart|person|43|N|1|384|0|0|384|
|bart|person|43|S|1|384|0|0|384|
|bart|person|43|M|1|384|1|0|384|
|bart|person|44|N|0|384|0|0|384|
|bart|person|44|S|0|384|0|0|384|
|bart|person|44|M|0|384|0|0|384|
|bart|person|44|N|1|384|0|0|384|
|bart|person|44|S|1|384|6|0|384|
|bart|person|44|M|1|384|2|0|384|
|t5gemma|time|42|N|0|768|0|0|768|
|t5gemma|time|42|S|0|768|0|0|768|
|t5gemma|time|42|M|0|768|0|0|768|
|t5gemma|time|43|N|0|768|0|0|768|
|t5gemma|time|43|S|0|768|0|0|768|
|t5gemma|time|43|M|0|768|0|0|768|
|t5gemma|time|43|N|1|768|0|0|768|
|t5gemma|time|43|S|1|768|0|0|768|
|t5gemma|time|43|M|1|768|0|0|768|
|t5gemma|time|44|N|0|768|0|0|768|
|t5gemma|time|44|S|0|768|0|0|768|
|t5gemma|time|44|M|0|768|0|0|768|
|t5gemma|space（原朝向划分）|42|N|0|512|0|0|512|
|t5gemma|space（原朝向划分）|42|S|0|512|0|0|512|
|t5gemma|space（原朝向划分）|42|M|0|512|0|0|512|
|t5gemma|space（原朝向划分）|42|N|1|512|0|0|512|
|t5gemma|space（原朝向划分）|42|S|1|512|0|0|512|
|t5gemma|space（原朝向划分）|42|M|1|512|0|0|512|



## 机制分析的边界



行为完成后的小型masked-mean线性probe以train世界拟合，跨P/Q/U新test世界读取当前状态、目标绑定槽、对象。角色槽不是完整参与者身份机制；core的锚点归属常量不能提供有意义分类证据。probe_on_next_failures列当前正确且续步失败的可读变量。可读出不等于编辑器使用；没有子空间替换或因果干预，不以距离/聚类给机制结论。



## 七个研究问题：以已完成证据回答

1. 固定案例审阅已确认BART的person、time三个seed发生当前正确、gold续步正确而latent续步表达破碎/不完整；这证明这些案例失败存在，不把全部未解析输出判成语义错误。另有可解析的下一步语义不匹配的模型/领域为t5gemma/time。未解析、仅语法或终止失败另列，逐seed计数见表。未准入组合bart/emotion只说明此配置基础能力不足。仍待完成：bart/space、t5gemma/time、t5gemma/space、t5gemma/emotion、t5gemma/person。

2. 留出状态×留出U、固定同全文/mask集合的M−S：bart/person/H0：3seed均值+0.00pp，范围[+0.00,+0.00]pp；bart/person/H1：3seed均值+0.00pp，范围[+0.00,+0.00]pp；bart/time/H0：3seed均值-35.94pp，范围[-84.38,+0.00]pp；bart/time/H1：3seed均值-7.81pp，范围[-23.44,+0.00]pp；t5gemma/time/H0：2seed均值+0.00pp，范围[+0.00,+0.00]pp；t5gemma/time/H1：1seed均值+0.00pp，范围[+0.00,+0.00]pp。正负方向和零效果均保留；只有同一领域两个划分和全部seed支持时才称稳定优势。空间主问题使用更正后的关系状态划分，原绝对朝向结果不作为未见关系状态证据。

3. 三类迁移使用独立轴和固定来源，不能互相替代。已完成的P原子能力：bart/time P自然IID2304/2304，留出表达322/1152；bart/person P自然IID1152/1152，留出表达122/576；t5gemma/time P自然IID2304/2304，留出表达663/1152。来源/状态交叉按各seed及状态分别报告，不能用全候选覆盖变化冒充固定配对集改善；汇总计数不把多改写视为独立世界。

4. 锚点/范围挑战的完整语义成功：bart/time P挑战2189/3456；bart/person P挑战4/2304；t5gemma/time P挑战1640/3456。错误案例逐项区分绝对日期、历史原话、固定观察者、非目标评价、人物/所有者绑定；只错相对目标不自动证明选错锚点。未训练结构的单步失败不能归于latent组合。原空间朝向划分存在状态定义限制，确认版固定世界坐标并真正留出right/left当前关系。 后正式位置诊断：尚待结果。此扩展单独标记，不冒充最初预注册；目标首句的原挑战不能排除位置捷径。

5. 旧自然能力出现损失的设置：bart/person/M自然core原成功损失13、原失败修复0；bart/person/S自然core原成功损失8、原失败修复0。此处跨两个划分汇总用于定位，逐seed、逐划分及旧来源的损失/修复数是主要证据，见capability_regressions。

6. 两种模型全部三seed均完成并准入的领域为尚无全部完成的领域；只有这些组合可作本轮受控跨模型比较。单模型准入失败与另一模型组合失败不能合并平均，T5Gemma实际是已核验2B IT而非270M IT，rank相同但编辑器参数量不同。

7. 最有证据的下一步是围绕已确认的“同当前文本、同mask/深度、下一步分歧”做受控兼容性和能力保护研究；先分别验证来源、当前关系/角色状态和表达结构的覆盖，而不是仅增加补训步数。多状态补训若稳定劣于S，应检查各状态梯度干扰和旧路径保护的预算分配。未准入领域优先解决固定接口的重构/原子能力。当前probe只支持可读性，不支持编辑器使用或因果机制；没有进行子空间干预。

## 执行与工件

累计实际GPU小时：12.746666666666666；allocation账本峰值：2张。job IDs：['2555', '2564', '2568', '2571', '2582', '2585', '2587', '2590', '2620', '2621', '2650', '2651']。始终一任务一卡、一个项目全局最多两卡；符号数组依赖正式数组afterany，工程失败/重试也计入账本。



科学锁、数据/模型/配置hash、SOURCE_LINEAGE_COMPLETE、逐例gzip预测及可恢复原始分片、checkpoint_index、来源cache manifests、完整日志索引共同构成证据。数据manifest的两个摘要行数仍保留修订前值；最终person6文件SHA正确，最终实际行数在data_delivery_audit中明确给出。无人类独立标签；评分范围是受控语义语法。


## 空间关系状态确认：独立结果



状态0front/1right/2back/3left；plus物理朝向顺时针90度，关系状态减1。S只补训front，M补训front/back，right与left仅自然原子训练见过，未补训其编辑态续步。原世界坐标、人物、split和自然原子文本对集合不变。



|模型|seed|重构|原子|gold续步|准入|
|---|---|---|---|---|---|



|模型|seed|划分|世界|S|M|M减S|
|---|---|---|---|---|---|---|



完整逐seed/group CSV与mean_and_range保存在space_relation_confirmation_v1。来源/状态/表达交叉保存在主目录transfer_quad.csv；字面全文与标准化全文匹配分别保存在literal_fulltext*及same_text_source_disagreement.csv。cross_backbone_fixed_worlds给共同内容世界/当前全文集合以及各backbone自己的覆盖；跨backbone token mask不能相同，限制另存JSON。



## 语言结构能力与连续路径：后核心控制



LINGUISTIC_CONTROLS_PLAN在此阶段拟合/解码前冻结，但在部分原始BART测试结果之后新增，不能冒充最初预注册。没有新训练或test调参。先做未编辑dev/test重构与三个P的dev原子/gold-next；同一固定门槛通过的结构才运行所有现存N/S/M的1–5步三路径，失败结构单列。此阶段没有新的复杂结构来源矩阵。



|模型|领域|seed|结构|状态|重构|原子|gold续步|
|---|---|---|---|---|---|---|---|



逐例控制及轨迹在ADDITIONAL_PREDICTION_ARCHIVES；逐seed/结构/条件/路径/步骤的计数在language_structure_by_seed.csv。未解析、语法与终止失败不自动等同于已证实语义错误。



semantic_components_by_seed单独给身份/对象绑定、绝对日期/方向、固定观察者、非目标评价和引语锚点/原话的约束。原冻结评分的scope=target∧preserved，是联合任务结果，不能单凭它判定锚点选择错误。新增scope_constraints_satisfied排除目标状态/说话语境端点正确性；语法破碎、未解析和未结束输出标为未知，另报覆盖、已解析条件率及全候选严格率。解析的身份/引语等槽位失败才作为对应语义错误案例；这项事后分析不影响准入或选择。



独立负例审计发现原空间解析器的first-viewpoint回退可以把B的关系用于A，并且B视角和marker描述未校验物体身份：168个构造的错误A关系/B物体/marker物体负例均被原实现接受。独立SPACE_SCOPE_GUARD_CHECK拒绝全部168例，并通过1344个正确文本。构造负例与模型实际预测分别报告。原正式评分和门槛不改写；spatial_scoring_adjudication逐工件保留原通过数、实际确认假阳性数及保守修正数，不能把这些假阳性用作范围成功证据。位置诊断在GPU评估之前增加独立A视角和非目标物体检查，旧锁/代码和修订时间保存在protocol_revisions和POSITION_*REVISION。该修订不增加输入、训练或重新选checkpoint。



## 续步输出审阅和身份probe



主phenomenon表的完整任务失败包含未解析输出；current_correct_next_failure.csv另给可解析语义不匹配、未解析、仅语法和仅终止计数。固定首个test世界×三个seed×三种轨迹的18个BART时间/人称案例由Codex助手逐一审阅：当前和gold-reencode下一步均正确，latent下一步输出重复/破碎或丢失必要关系，不是合理释义。仅据此证明这些案例的失败存在；不把全部未解析输出标成语义错误，不作独立人工标注或因果机制结论。见CONTINUATION_AGENT_REVIEW及continuation_review_set。



|实验|模型|领域|变量|seed数|留出U均值|范围|
|---|---|---|---|---|---|---|



命名身份probe只从冻结P train表示拟合，跨P/Q/U test读取；current-correct-next-failed子集准确率另见identity_probe_on_failures。时间core锚点归属是常量，未拟合归属分类器；没有quote/external-anchor对照probe或子空间干预。可读出不等于编辑器使用。



T5_CONTINUATION_AGENT_REVIEW另保存固定首个test世界的12例：时间三个seed、原朝向空间seed42，各三种轨迹。Codex逐一阅读当前、latent下一步与gold重编码对照，确认日期/关系错误、固定事实损失或破碎重复。空间例不是更正关系确认版的证据；保存这些例时部分正式评估尚未结束。此记录同样不是独立人工总体标注。



## 位置与同措辞锚点补充诊断



POSITION_FOILS_PLAN在部分正式test结果之后、这批GPU评估之前冻结。没有训练、重新选checkpoint或根据test调参。同世界的两种顺序共享gold转换；emotion额外把同主体的非目标对象放在前面，空间固定观察者在前，人称历史引语在前，时间引语和外部表达使用相同事件/相对日期句式。时间历史日期E−3与固定引语一致。原引语只作为原话记录，未假定为事实，原结果仍保留。



情感补充variants2/3显式记录Narrator=Focus，外部第一人称I与参与者C历史引语中的I可以使用相同评价措辞；仅外部目标评价改变。引语分别在末尾/开头。该语法未训练，抽象等级转换已有自然原子训练；2/3单独配对，不与多对象0/1当作相同完整世界状态混合。独立评分适配器只绑定语法合法的未引述I，不修改回灌文本，也不修正I likes等语法错误。新增夹具在该诊断GPU评估之前冻结，7504项情感CPU正负例检查通过；详见POSITION_NARRATOR_AMENDMENT及修订哈希。



|模型|领域|seed|顺序|状态|重构|原子|gold续步|
|---|---|---|---|---|---|---|---|



全部可用角色的test原子预测，即使诊断未准入，仍在position_foils_by_seed与压缩逐例工件中；连续路径仅在同一P的该顺序dev门槛通过时执行。position_order_pairs以同世界/状态/操作配对给顺序差异；两个顺序同时正确才证明这些具体夹具的范围保持。仅靠原目标位于首句的挑战分数不能排除位置捷径。



## 语言学解释限制



见LINGUISTIC_LIMITATIONS.md。core三人循环使用显式姓名，无人称信息丢失；第三代词挑战使用人工姓名/代词约定，没有独立性别属性测试。反身附加事件规定A保留A自己的key；主对象也是key时需要不同实例解释，原文本未命名实例，不能据此声称验证了唯一物体实例所有权。固定launch日期由E−2导出；C是叙述锚点，事件状态独立给定。更复杂图结构、复数/集合、平移、间接引语及随机子空间干预未执行，保留为限制。



## 执行顺序偏差



工程阶段检查了全部八个模型/领域，但最初正式数组把每个组合的600步准入与其补训/行为串在一起，未先完成全组合的最终原子准入。每个组合的早期probe在该组合行为结束后运行，当时其他组合尚未完成；后续命名身份probe统一排在行为阶段之后。这些顺序偏差保留，不冒充最初的全局阶段顺序。剩余未启动孩子16–23改为先运行原预算P600/dev准入的2650，再由零GPU2651释放其原补训任务，复用同一P/dev工件，不新增训练更新。固定科学代码/数据/选择规则与阈值未改。见REMAINING_ATOMIC_PREFLIGHT与submission ledger。
