# 文本参考系转换 v2 — 预注册执行协议

日期：2026-09-29，Asia/Singapore。研究问题：冻结BART的小算子能否保持事实地连续转换时间/人称？区分第二步文本输入覆盖、编辑后隐藏表示再使用、少量指定链监督的修复与迁移。实际结果另见REPORT.md；本文件在新训练前保存。

## 原证据与执行边界

核对v1提交6883cf0及本地v1子树完全相同；从JSONL重新算出IID原子1、OOD原子.9770833333、IID时间→人称latent .9833333333、时间两次latent 0/reencode .6625，53/27分层吻合。证据见v1_evidence_audit.json，v1文件只读清单见v1_readonly_manifest.json。无在运行相关作业、无既有v2实验。旧HEAD另含未发布的标签实验；本轮只修改v2目录。

复用v1原BART revision/hash、float32、eval、冻结E/D，禁TF32；tokenizer相同。LowRank16四独立算子，参数101376，V~N(0,.01)、U=b=0，有效token编辑，原始mask不被生成长度替换。原输入上限96，max_new_tokens=60，greedy beam1、无forced EOS，不因失败后加长。AdamW lr=.001、weight_decay=0、batch16、无累积、clip1、600更新，每100保存并用目标token加权dev NLL选best。无衰减LR，六路径轮转，时间各200更新、人称各100。至多G0/G1/条件G2三个seed42组，从同一个初始化checkpoint重开，不补seed或搜索。

单GPU、累计不超过7200分配秒；sbatch+srun B300q，不在登录节点训练，不指定GPU编号。按sacct父/step最大ElapsedRaw计费，等待单列。v1完成全批724秒；v2预计约1000秒，阶段提交预留安全边界，不重复默认预算。信号/预算中断保存optimizer/RNG与实际进度。

## 日期合法性与有限范围

继承v1语义schema和12模板（8训练/dev/IID、4仅OOD），解析器原样复用，在v2增加分项指标。作者标题和record_date不变、actor=author且recipient不同；外部条件只有frame/op。plan跨日期仍是记录计划；completed是报告，不是外部验证；取消否定计划不蕴涵正事件。

数学约束：completed满足event_date≤record_date≤每步view_date，因此正offset的completed源不存在；在[-1,+1]起始三次T_minus也不可能合法。已向用户说明，默认保留合法性，显式预定结构性不适用，不造非法日期。生成时completed设record_date=event_date；plan/cancelled设event_date=record_date+5，使有限路径所有帧合法。所有组同样应用。G0因此是匹配对照而非v1重现。每路径合法世界清单在任何模型输出前固定；只有completed/minus3整条路径结构性N=0（每测试层27世界不适用），其余失败不筛除。另保存操作×状态×极性×偏移×人称计数及零单元；不会把结构性零声称已覆盖。

新世界480train、80dev、80IID、80OOD、60calibration，数据seed2026092902。完整事实键（全部schema字段，去掉record_id等生成元数据）与v1和跨split去重；ID独立；全部视图归同split。新日期10–12月，故G0/G1相同绝对日期分布，v1数值不能当作匹配控制。原子dev/test每世界6路径，共同合法源offset∈[-2,2]；两步每世界每合法路径一个预先随机合法offset∈[-2,2]；三步∈[-1,1]。中间时间源落在[-3,3]合法范围，端点[-4,4]。每步frame/offset/组内覆盖布尔值保存。不声称任意长度闭合。

G0/G1同世界同2880对索引同9600实际样本出现；只改时间源覆盖G0[-2,2]、G1[-3,3]（按状态/操作限制合法子集），同随机分位映射配对。P13/P31逐项完全相同。源偏移与状态、极性在合法条件下均有样本。不同覆盖导致监督token长度差异如实报告，不称等FLOPs。

G2预定从G1采样计划T_plus且源offset[-2,2]的出现位置确定性选1600次，占全部时间6400次的25%/T_plus3200次的50%；替换源不变，只把路径/目标换T_plus²。每样本仅终点CE，训练不decode/reencode、不加第一步CE；其余操作原子不变。保存替换位置及唯一记录数，算子调用与token另计。

## 预检与A

calibration穷尽60世界所有合法offset[-4,4]×两人称=920视图。先gold独立解析/规则覆盖100%，全路径长度核验无截断，再自由生成重构joint必须100%；通过后锁定新test文件哈希。若失败先处理calibration，不能打开新测试。检查无BART梯度、编辑梯度、eval重复编码一致和padding。

A只用v1三seed×IID80×Tplus²或Tminus∘Tplus。A1复用原纯链输出、A2复用实际重编码输出，A3以正确中间文本为输入；若actual_mid逐字等于gold_mid，确定性A3与A2输入相同则复用输出并注明，否则补生成。全80及53/27、token长度变/不变分层。纯链保持原mask。保存每token第二步更新范数/输入范数，仅描述，不做未对齐逐位置距离，不把等长当位置语义对齐。A不是独立新测试，A3不是部署方法。

## 门槛、锁定和测试

先G0/G1。共同原子dev 480条按v1 token加权NLL选best，扩展源±3诊断不入选模。完成G1后固定dev gate：时间原子joint≥.95，四条时间两步reencode各≥.95，plus_plus latent<.90，三者均满足才G2；前两项不满足则停止C；前两满足但latent≥.90也不启动C。门槛不能因test改变。

全部实际组checkpoint哈希锁定后统一test。六原子，plus_plus/minus_minus/plus_minus/minus_plus/plus_person/person_plus/person_return两步，plus3/minus3三步；各组合latent_chain和decode_reencode。每步诊断文本/评分保存，但纯链不摄入解码文本；诊断解码时间独立于真实执行路径。无编辑同次数重建按相同源/frame匹配，可跨组复用。Text-rule只读source/frame，Target reconstruction用gold仅为参考可重构性诊断，不当数学性能上界。原子±3扩展诊断另表，不参与选模。

## 评分与统计

沿用v1 joint含义，新增date_ok、perspective_ok、nondate_facts_ok、normal_end；完整消费可解析文本且所有事实与frame正确并正常结束才joint。unresolved不成功但不自动说已确认语义错误；解析子集非日期错误保存分母。v1 collateral不包含date错误，v2不混淆。所有路径按预定合法世界分母，世界是统计单位。

2000次配对world bootstrap，IID/OOD分层、同世界路径/视图一起重采样；seed42区间仅记录抽样。主比较G2−G1（若运行），G1−G0解释覆盖。20个test世界（每层10）已用独立seed预选，方法及路径匿名，映射单存；解释性案例另作便利抽样，不估准确率。没有真人标签时明确结构化自动检查+模型复核，不改旧/v2冻结自动分数。

报告区分测量、辅助诊断、机制猜测；不会由重编码恢复断言离开流形或BART固有缺陷；不会将仅Tplus²修复称任意组合。结束后只在本会话既有Git发布授权内提交/推送v2相关文件，保留optimizer本地，凭据不公开。自然文本/LLM/HE/probe/SAE/层扫描/谱正则化均不运行。
