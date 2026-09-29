# 跨encoder–decoder参考系编辑预实验：冻结协议

日期2026-09-29，Asia/Singapore。仅新增本目录，独立分支experiment/reference-frame-cross-backbone-v1。v1/v2/v3只读。研究有限受控文本的事实保持和逐次参考系转换，不研究开放聊天、decoder-only、自然长文或新损失搜索。

候选固定顺序：google/flan-t5-base、google/t5gemma-2-270m-270m（预训练）、google/flan-t5-large、google/t5gemma-2b-2b-ul2-it。按官方模型卡及当前安装Transformers实际类核实并固定revision/tokenizer/软件/attention/hash；不替换不可访问模型，不代用户接受门控许可。新模型用float32、eager attention、默认microbatch4；OOM只降低microbatch并保持有效batch16，在训练前验证锁定。BART复用G1/G3，无重训，sdpa/float32/96输入/60生成保持原路径，先小样本复现存档。没有L40S/A100分区；当前允许B300q/RTXq，优先现有已获准B300q单GPU，不指定GPU编号。

复用v2 train480/dev80/calibration60及G1源、600步日程（六原子轮转；T±各200更新，P各100），G3固定1600链替换出现。新确认集IID80/OOD80，seed2026092904（若与旧事实冲突按完整事实键拒绝重采，保留本seed及碰撞数）。与全部旧世界及本批跨split去重；同世界视图不跨split。模板、状态、否定及日期合法性沿用v2；模板奇偶与否定相关的旧局限保留。两步源±2、三步±1，时间源±3、人称±2均按实际合法性标注；completed/minus3在模型输出前固定N/A。每层随机预选10世界盲审。全部世界、路径、gold、评分代码、分母先哈希锁定；确认集不决定包装、长度、训练或选模。

每模型只比较A原正文和B固定复制指令：

    Copy the following text exactly. Output only the copied text.

    {text}

官方要求chat格式才使用官方模板，不自创。FLAN没有chat模板不影响支持。包装含原正文，无操作/目标日期/链长/答案。有效非padding token全部编辑，含特殊token和包装token，不豁免标题或指令。标签仅正文。重编码对实际输出正文包装一次，不嵌套指令、不纠错。若实际输出复述指令，保留并重新作为实际正文输入，不自动剥离。不同包装的结论对象是骨干+tokenizer+接口。

calibration原句集使用920个完整合法offset[-4,4]×人称视图；目标集为这些校准世界每条合法原子/两步/三步路径的全部目标阶段（源范围沿用正式路径）。唯一文本可缓存确定性生成但按原角色和出现分母回填，不删重复世界的关联视图。A/B均保留输出与实际输入字符串。先最大化source/target joint较小值，再总体值，平局A。source/target各≥98%、各状态≥95%，且API/shape/mask/生成/梯度/确定性全部通过才训练。未通过记reconstruction_failed继续下模型，不训练重构器/骨干、不追加prompt。生成长度只按train/dev/calibration正文token最大值+8，输入上限按两包装同集合最大长度向上取8倍数；无截断，beam1、不采样、无强制EOS。BART保持原上限。所有输出保留正常EOS/长度/特殊token。

编辑器四独立T(H)=H+(HV)U+b，rank16，d读取encoder实际最终输出；每算子2*d*16+d参数。接口是传给decoder的encoder最后状态，显式审查桥接投影位置；不替换成inputs_embeds或decoder内层。V小随机、U/b零，每骨干同初始化配对G1/G3，骨干eval冻结，只有编辑器优化；encoder可no_grad，decoder允许梯度回H。真实batch核验零编辑/直通一致、labels右移和token对齐、H/editor梯度有限非零、padding不变、骨干梯度为空且权重不变；链终点能回传H1。每次generate新缓存，latent保持原mask，中间解码只诊断。

G1仅原子CE。G3链样本ell_j=.5*(sum CE1/n1)+.5*(sum CE2/n2)，其他样本ell_j=sum CE1/n1。G3外权w_j为旧G2终点有效token数（链n2、普通n1）；batch=sum(w_j ell_j)/sum(w_j)。累积microbatch先求整个有效batch的分母再反传各分子，最后一次clip/step，不对子组mean相加。G1全部token加权。AdamW lr=.001、weight_decay0，无LR衰减，clip1，seed42，600更新，每100按完整固定原子dev token NLL选best，平局早者。另组从初始编辑器重开，不沿G1续训。每检查点保留编辑器及训练/dev曲线，最新optimizer/RNG可恢复。只在同模型组内比较NLL。G1未学稳仍按预算运行预定G3，但不把这种情况称纯组合失败。最多8组，不补G2/seed/rank/LR。

每模型包装/生成/两个best锁定后做共同确认；全批协议不依中途确认成绩改变。矩阵六原子、plus_plus/minus_minus/plus_minus/minus_plus/plus_person/person_plus/person_return/plus3/minus3，纯表示和实际重编码。对照原句还原、每阶段正确目标还原、源文本1/2/3次无编辑重编码、源文本规则（无W）。记录逐步frame/date/person及每个非日期字段、joint、未决、EOS、遗漏/重复诊断。endpoint=末步；trajectory=同记录所有阶段逻辑与。未决不成功，也不自动当确认事实错。全固定合法世界分母。日期错误模式比较相对offset而非各frame下相同的绝对事件日。

统计：每层2000次配对world bootstrap，同世界所有视图/路径/模型共享抽样；原子先世界内平均，报告视图n/N与世界聚合。差值每模型G3−G1、latent−reencode及可复评BART跨骨干差值。只seed42，CI不含训练随机性，探索性多比较不作确认性显著结论。20世界匿名完整轨迹、方法映射独立；至多20便利案例，不估计频率，human_label空，模型复核不是真人审核。

预算累计14400 GPU分配秒，预检/包装筛选≤3600；任意时刻1GPU。下载CPU无GPU，单独计时。分阶段Slurm提交，父/step最大ElapsedRaw、不重复计费；失败/重试也计入，队列单列，账本不可清零。每模型先小批计时，训练前预留至少1.5倍完整评估估时，优先完成该模型G1/G3和评估再下一个。预检上限按已耗减扣；预算前保存并停止，incomplete/budget_skipped区别于模型错误。访问/接口/重构受阻继续其余候选。独立分支提交可审阅结果，已授权远端同步只推新分支，不覆盖main。
