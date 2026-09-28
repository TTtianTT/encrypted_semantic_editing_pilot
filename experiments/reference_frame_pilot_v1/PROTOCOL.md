# 文本参考系转换 v1 — 执行协议

2026-09-29 Asia/Singapore。依据用户本轮完整方案执行；本文是实施细化，不是已运行结果或新颖性声明。状态见 REPORT.md、calibration/gate.json 和 budget.json。

## 语义与输入

W 包含 record_id、author、actor、recipient、action、object、quantity、record_date、event_date、record_status、polarity、attribution；c 包含 view_date、perspective。actor=author，recipient≠author，第一人称仅指 author。姓名及不可变 record_date 在源/目标短标题中。文本是记录重述，不是直接引语；相对日期依外部 view_date 解释。时间单位为同一时区整日。

recorded_plan 表示记录中的计划，不随阅读日越过事件日变为完成；reported_completed 表示作者报告事件结果，positive=报告做了，negative=报告没做，不宣称外部核实；reported_cancelled 表示该 polarity 的计划已被取消，取消“不做”的计划不推导“做了”。attribution 固定 author，并由事件名词的所有格表达。reported_completed 的 event_date≤record_date；所有路径 view_date≥record_date；c0=record_date+1。词表覆盖 ±4 日，实际完整路径需求 −4 至 +3。record_date 显式呈现并评分。输入不包含 W 隐藏槽位，不加入任务前缀或目标提示。

预检前模型复核发现草稿“plan dated …”存在日期作用域歧义，统一明确为“event dated …”；旧草稿原样归档 calibration/pre_generation_draft。这是任何模型输出之前的数据协议校正，不是利用测试结果改模板。最终生成与冻结文件见 frozen_manifest.json。calibration 的30完整记录另存 review/calibration_records.jsonl。只有结构化自动检查和模型复核，没有真人真值。

## 固定数据与算子

先生成独立 W，再按 record_id 固定 split：calibration=60、train=480、dev=80、test_iid=80、test_template_ood=80。全部视图和路径留在所属 split。8个模板家族用于train/dev/IID，4个只用于OOD；calibration覆盖全部。先满足日期合法性，再平衡状态和其他因素。非开放词汇/人物泛化。20%左右为明确否定。每记录6原子对：时间±1各有第一/第三人称，人称1→3/3→1在c0；2880/480/960训练/dev/测试原子对。没有双步训练对或编辑生成文本作训练输入。

operation selector仅对比source/target frame，返回T_plus/T_minus/P_13/P_31，不读取文字或W。Text-rule采用独立parse(source,source_frame)及局部字符串变换，不调用renderer或读取W。评分器不调用renderer，接受数字和词形数量、mentions等非reference替代表达；完整消费文本，未支持的输出记parse_unresolved而非已证实语义错误。额外断言不忽略。frame_ok要求目标人称及由目标view_date解释的event_date正确；content_ok逐槽位比较；joint_ok还要求可理解且未到生成上限。plan_to_completed规则探测不能穷尽任意自然改写；unresolved与冲突必须另作模型/真人审查。

## 冻结底座与工程设置

只读原facebook/bart-base，revision aadd2ab0ae0c8268c7c9693540e9904811f36177，实际逐文件SHA256见source_model_manifest.json。E/D始终eval、requires_grad=False，不导入旧Runner、不进入重构修复、不读旧编辑权重。float32，禁TF32，mask仅编辑有效token，标题无特权。

Shift单算子768参数，四算子3072；LowRank16单算子25344，四算子101376。b=0；LowRank V~N(0,.01)，U=0。E0只做独立临时梯度检查，不执行optimizer更新、不保存为训练权重。

AdamW lr=.001、weight_decay=0、batch=16、梯度累积=1、clip=1、每组最多600更新，每100更新保存/验证。六路径轮转均衡，各自有确定seed的采样流；每组四独立算子，共用固定无衰减学习率调度。每个时间算子得到200批/3200样本，每个人称算子100批/1600样本（满600步时），报告实际量。单步dev target-token NLL选择best。不看组合结果选模型。greedy beam=1，不采样，forced_eos=None；所有金标准及+2视图预先核验长度，共用96或必要时128，禁止截断；max_new_tokens=完整gold最大token数+8。

## 顺序、门槛和停止

E0：60记录×7视图=420真实自由生成，比较D(E(x))与直接generate，核查Copy接口、padding、编辑梯度/BART无梯度。总joint≥98%、各状态≥95%、不得成片计划→完成才进入E1。

若失败，只允许一次calibration格式简化，并用新的独立60记录确认，旧输出保留，不改测试评分口径或底座。再次失败停止；如果不做可选整理，也可保守停止，但须明确未执行确认而不能声称确认失败。

E1最多2个算子组（Shift/LowRank16 seed42）；dev joint≥85%、时间/人称各≥80%、计划误报≤2%，才追加E2的seed43/44两方法共4组。总计最多6组。未达标不扫超参、不延长训练。

单GPU、累计7200分配秒，包括预热、预检、训练、推理、失败作业；Slurm sbatch+srun，B300q，不指定GPU编号，不在登录节点训练。每次重启按sacct父/step最大ElapsedRaw保守计费，不重置预算。训练前测短窗口和固定推理批次估算；无法完成则在预算内保存checkpoint和真实进度。

## 仅当E1/E2通过后执行的锁定测试

全部checkpoint/config锁定后统一测试：六原子路径；P13∘Tplus及Tplus∘P13；Tplus∘Tplus；Tminus∘Tplus及P31∘P13；计划跨日期分层。每条两步路径测latent_chain、decode_reencode及同次数reconstruction_only；重编码中间current_frame更新，失败中间输出仍在分母，不重试择优。Shift交换只作代数性质，不作独立语义证据。

对照：Copy、Identity、Target reconstruction（诊断非上界）、Text-rule、Text-rule+E/D、同次数纯重建链、固定Wrong-operation。所有输出保留文本、允许上下文、路径/op、record_id、seed/hash、长度/截断、encode/edit/decode/total时延、评分/不确定原因。计时同批同长度组，CPU规则和重复编解码包含在总时延中；预热和诊断计入预算。

主表全固定分母，按method/seed/stratum/path/status/时间或人称报告frame/content/joint/collateral/plan→completed/unresolved；组合语义一致与两条都正确分开；逆向同时报前向/回程。record_id内所有视图/路径一起进行2000次配对bootstrap，IID/OOD分层。三seed独立、均值/范围；seed平均record bootstrap只覆盖记录抽样。

正式输出固定抽40 test record_id、方法匿名、保留全部关键路径；另抽unresolved/规则冲突并注明便利抽查不估总体准确率。无真人时明确“结构化自动检查 + 模型复核”。报告开头回答单步、不变量、两步、OOD、继续/停止，附固定抽样10–20成功/失败案例。

自然挑战60条、LoRA、指令模型、rank64、HE、开放条件均不在本批；不自动下载模型、不调用付费API、不发布/推送、不修改旧实验。
