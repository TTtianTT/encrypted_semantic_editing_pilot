# 跨骨干参考系编辑预实验：实际结果

下表G1/G3依次列出；两步/三步指T_plus²/T_plus³的纯表示全轨迹，原子为六视图按世界内平均。预检不通过的模型没有训练结果，不能填成编辑准确率0。

|模型/层|准入|G1/G3原子|G1/G3两步全轨迹|G1/G3三步全轨迹|时间→人称 G1/G3|人称→时间 G1/G3|已解析非日期错/未决|GPU秒|
|---|---|---|---|---|---|---|---|---:|
|flan-t5-base|reconstruction_failed|—|—|—|—|—|见重构分层，非编辑结果|124|
|t5gemma-2-270m-270m|reconstruction_failed|—|—|—|—|—|见重构分层，非编辑结果|502|
|flan-t5-large|reconstruction_failed|—|—|—|—|—|见重构分层，非编辑结果|209|
|t5gemma-2b-2b-ul2-it/IID|passed|480/480 (100.00%) / 480/480 (100.00%)|0/80 (0.00%) / 80/80 (100.00%)|0/80 (0.00%) / 1/80 (1.25%)|68/80 (85.00%) / 24/80 (30.00%)|63/80 (78.75%) / 27/80 (33.75%)|G1 8错/449未决/1866输出；G3 6错/124未决/1866输出|3531|
|t5gemma-2b-2b-ul2-it/OOD|passed|480/480 (100.00%) / 476/480 (99.17%)|0/80 (0.00%) / 79/80 (98.75%)|0/80 (0.00%) / 3/80 (3.75%)|52/80 (65.00%) / 26/80 (32.50%)|45/80 (56.25%) / 28/80 (35.00%)|G1 10错/448未决/1866输出；G3 7错/136未决/1866输出|3531|
|BART/IID|复用参照，64/64存档复现|480/480 (100.00%) / 479/480 (99.79%)|0/80 (0.00%) / 80/80 (100.00%)|0/80 (0.00%) / 11/80 (13.75%)|79/80 (98.75%) / 80/80 (100.00%)|75/80 (93.75%) / 72/80 (90.00%)|G1 0错/456未决/1866输出；G3 0错/284未决/1866输出|585|
|BART/OOD|复用参照，64/64存档复现|467/480 (97.29%) / 467/480 (97.29%)|0/80 (0.00%) / 61/80 (76.25%)|0/80 (0.00%) / 4/80 (5.00%)|77/80 (96.25%) / 68/80 (85.00%)|79/80 (98.75%) / 66/80 (82.50%)|G1 0错/453未决/1866输出；G3 0错/316未决/1866输出|585|


## 直接回答本批问题

本批直接测量支持：**“原子转换可靠、纯表示连续编辑失败、重编码可恢复”并非只在BART上出现。** T5Gemma IT复现了这一现象；G3也复现了“训练过的两步获益、其他组合受损”的取舍。当前证据支持继续研究可靠连续使用的问题，尚不支持把这套G3当作通用可组合参考系算子。

实际执行了4个候选的API和A/B重构准入、T5Gemma IT的G1/G3各600更新，以及BART旧G1/G3在共同新集上的完整复评。没有重训BART，没有运行新G2或追加seed。以下均为seed42、共同160世界上的结构化自动检查，另有便利模型复核，尚无真人审核。

1. **哪些接口可运行、哪些满足重构前提？** 四个候选均可访问并最终通过API/形状/梯度等检查；只有T5Gemma IT通过冻结重构门槛，B包装原句920/920、目标5880/5880。FLAN-T5-base和预训练T5Gemma2 270M-270M两包装的保守语义通过率均为0；FLAN-T5-large最优B为898/920和5762/5880，精确值低于98%。后者含严格parser格式未决，需与正文遗漏区分。三个未准入模型的编辑能力本批未测量。

2. **哪些模型学稳了原子？** T5Gemma IT G1在IID/OOD均480/480；G3为480/480、476/480，OOD退化都来自T_plus，单独计为156/160（G1为160/160），其余四个原子视图仍全部正确。BART复用参照在新IID为480/480→479/480，OOD均467/480。六视图总体值不能代替T_plus分项。

3. **哪里复现纯链失败而重编码更好？** T5Gemma IT G1的plus_plus、minus_minus、plus_minus、minus_plus在IID和OOD的纯表示全轨迹均0/80，而实际输出重编码均80/80；全部合法G1重编码链共693/693每层通过。BART G1的plus_plus纯链也均0/80，重编码为IID80/80、OOD73/80。T5Gemma IT原子可靠且无编辑对照可重构，因而这里不是单步尚未学会造成的假组合性问题。

4. **G3两步收益和代价如何跨骨干出现？** T5Gemma IT plus_plus纯链终点两层均80/80，但全轨迹为IID80/80、OOD79/80；OOD那一条中间日期错误仍留在分母。BART对应全轨迹为80/80、61/80。两者均有训练过的两步收益。代价在新骨干更大：T5Gemma IT时间→人称的IID/OOD全轨迹从68/80、52/80降为24/80、26/80；人称→时间从63/80、45/80降为27/80、28/80。BART同两顺序为IID79→80、75→72，OOD77→68、79→66。不同骨干、tokenizer、包装、参数量同时变化，不能唯一归因于规模或架构。

5. **未训练链怎样？** T5Gemma IT G3 plus3纯链仅IID1/80、OOD3/80；minus_minus和两种时间往返仍均0/80，合法minus3均0/53。人称往返保持两层80/80。BART G3 plus3为11/80、4/80，时间往返局部有成功但远未可靠，完整矩阵见下表。T5Gemma IT的T_minus、P_13、P_31在G1/G3之间权重逐项完全相同，未改变的minus链持续失败不能称为遗忘。

6. **下一批最值得复核什么？** 优先给T5Gemma IT补独立seed，复核“原子/重编码可靠、纯时间链失败”和“逐阶段两步监督的局部收益伴随跨操作退化”这两个配对现象；若再研究监督作用，需另立等监督预算及仅终点对照。当前不宜按通用组合方法扩展G3到更长文本或开放任务。FLAN-T5-large可在独立、训练前冻结的评分/人工校准协议中复核格式容忍问题，本批不改分、不补训练。

**事实保持边界：** 不能只看日期终点。T5Gemma IT的已解析反向/往返输出中可见seven→eight books、five→six parcels等数量损坏，另有大量未决。BART本新集的已解析输出没有检测到非日期字段错误，但未决并未消失，不能据此宣称全部事实保持。主表给固定路径终点分母，逐阶段、字段和未决分母另外完整保存。

全部路径和方式逐阶段合计，T5Gemma IT G1/G3各7036个阶段输出中，分别检测到27/22次已解析数量损坏；这些是相关的阶段出现次数，不是27/22个独立世界。其余非日期字段在已解析子集中没有检测到改动，计划→完成已解析计数为0；G1/G3仍有1148/351个阶段未决，无法据已解析子集断言全体事实守恒。终点日期错误则从IID/OOD的33/68增至357/350；未决减少不等于日期控制恢复。

T5Gemma IT G3实际重编码链的IID全部693/693通过，OOD为687/693；其plus3重编码两层均80/80。纯链三步及跨操作退化因此也有直接的实际重编码对照，不能用终点渲染oracle替代这个比较。

**对照支持的解释：** 在源覆盖已满足且无编辑重构通过时，纯链与实际重编码的差异指向“编辑后表示的继续使用”问题；G3的效果主要局限于受监督的操作长度及轨迹。**尚未验证的机制：** 本批没有证明离开流形、固有容量限制或某种架构缺陷，也没有分离中间目标、终点权重改变和额外监督计算的因果贡献。观察限于两个可配对的encoder–decoder冻结接口、受控模板和一个训练seed。


## 固定A/B准入结果

原句分母920合法视图；目标阶段分母5880，保留同世界重复出现的相关性。相同文本只生成一次并按预定角色/出现回填评分，两类分母不视为独立样本。优先最大化两类joint较低值、再总体值、平局A。

|模型|包装|原句joint n/N|目标joint n/N|逐字一致/6800|正常结束/6800|未决/6800|是否选中|
|---|---|---:|---:|---:|---:|---:|---|
|flan-t5-base|A|0/920 (0.00%)|0/5880 (0.00%)|0|6765|6800|True|
|flan-t5-base|B|0/920 (0.00%)|0/5880 (0.00%)|0|5783|6800|False|
|t5gemma-2-270m-270m|A|0/920 (0.00%)|0/5880 (0.00%)|0|16|6800|True|
|t5gemma-2-270m-270m|B|0/920 (0.00%)|0/5880 (0.00%)|0|0|6800|False|
|flan-t5-large|A|0/920 (0.00%)|0/5880 (0.00%)|0|6800|6800|False|
|flan-t5-large|B|898/920 (97.61%)|5762/5880 (97.99%)|6660|6800|140|True|
|t5gemma-2b-2b-ul2-it|A|0/920 (0.00%)|0/5880 (0.00%)|0|77|6800|False|
|t5gemma-2b-2b-ul2-it|B|920/920 (100.00%)|5880/5880 (100.00%)|0|6800|0|True|

FLAN-T5-large的B包装原句898/920、目标5762/5880，均未达到精确的98%门槛，不按四舍五入后的98.0%放行。22条未确认原句中，描述性字符串核对发现9条只缺记录日期后的句点，另13条仅输出作者/记录日期、遗漏正文。前9条说明严格parser存在格式局限，不能都称为事实损坏；主分数与门槛保持冻结，未据此补训练。细节见calibration/flan-t5-large/punctuation_diagnostic.json和review/MODEL_REVIEW.md。

T5Gemma IT B包装原始逐字一致为0/6800，去除首尾空白后为6800/6800；输出保留了额外换行。原始字符串没有被覆盖，语义评分沿用旧解析逻辑，重编码按官方chat模板统一处理正文。


各包装×角色×计划/完成/取消的全部n/N及字段判定见calibration/<模型>/admission.json、A_scored.jsonl、B_scored.jsonl。实际渲染输入、特殊token、EOS及长度见*_unique_outputs.jsonl。不因未决修改parser、删样本或补第三种指令。未决不等于逐条确认语义错误；便利模型复核只能说明所读例子。

## 接口、精度、配置与初始化

模型权重在/dataset1/zailong/models/reference-frame-cross-backbone/，revision、tokenizer revision、文件hash、下载耗时见models/*.json；基础权重不上传。既有环境未升级，软件版本见environment.json，模块源码hash和实际加载类见*_interface.json。

|模型|实际类|d|每算子参数/四算子总数|输入上限/生成上限|dtype/attention|包装|
|---|---|---:|---|---|---|---|
|flan-t5-base|T5ForConditionalGeneration|768|25344/101376|72/61|float32/eager|A|
|t5gemma-2-270m-270m|T5Gemma2ForConditionalGeneration|640|21120/84480|72/65|float32/eager|A|
|flan-t5-large|T5ForConditionalGeneration|1024|33792/135168|72/61|float32/eager|B|
|t5gemma-2b-2b-ul2-it|T5GemmaForConditionalGeneration|2304|76032/304128|80/65|float32/eager|B|
|BART|BartForConditionalGeneration|768|25344/101376|96/60|float32/sdpa|A|


编辑位置为encoder最后表示、decoder cross-attention投影之前；维度实测而非硬编码。全部非padding token编辑，包括包装/特殊token。四个独立rank16参数为33d与132d。G1/G3同骨干初始权重共享，但跨骨干不载BART编辑器。

T5Gemma2首次加载受嵌套dtype影响，encoder曾为bf16，尚未生成A/B结果就因与float32编辑器不兼容而失败。显式model.float()恢复既定float32协议，重试完整预检；失败日志和55 GPU秒保留。未改变旧环境或评分。FLAN checkpoint的shared/lm_head权重不一致警告由Transformers处理为保留两者，没有擅自强制权重绑定。

API预检含右移labels对齐、显式/隐式teacher forcing logits一致、零编辑/直通生成一致、确定性、H与编辑器有限非零梯度、第二步CE能回传H1、骨干无梯度、样本骨干权重未变、padding不变。低秩V初始零梯度可正常，未要求每个因子首步非零。

训练若通过准入：AdamW .001/weight_decay0、float32、clip1、600更新、有效batch16、microbatch4，各完整有效batch权重分母先算再累积；每100原子dev token NLL选best，平局早者。G3链样本阶段均值各0.5，外权为终点有效token数。不同骨干不跨tokenizer比较NLL，不称等FLOPs。未进入训练的模型没有伪造训练曲线或best checkpoint。

## 共同确认集：全部核心路径

新seed2026092904，与v1/v2/v3完整事实键去重。80IID/80模板OOD，词汇共享，模板奇偶与否定相关的旧局限保留。minus3仅53个合法世界，其余每链80；27个completed在模型输出前标N/A。原子每世界六视图，先世界内平均；主率保留未决/重构失败/未结束。

|模型|层|路径|方式|G1终点|G3终点|G1全轨迹|G3全轨迹|
|---|---|---|---|---|---|---|---|
|BART|IID|T_plus_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|T_plus_third|latent_chain|80/80 (100.00%)|79/80 (98.75%)|80/80 (100.00%)|79/80 (98.75%)|
|BART|IID|T_minus_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|T_minus_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|P_13_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|P_31_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|plus_plus|latent_chain|0/80 (0.00%)|80/80 (100.00%)|0/80 (0.00%)|80/80 (100.00%)|
|BART|IID|plus_plus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|minus_minus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|BART|IID|minus_minus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|plus_minus|latent_chain|0/80 (0.00%)|14/80 (17.50%)|0/80 (0.00%)|14/80 (17.50%)|
|BART|IID|plus_minus|decode_reencode|79/80 (98.75%)|80/80 (100.00%)|79/80 (98.75%)|80/80 (100.00%)|
|BART|IID|minus_plus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|BART|IID|minus_plus|decode_reencode|74/80 (92.50%)|80/80 (100.00%)|74/80 (92.50%)|80/80 (100.00%)|
|BART|IID|plus_person|latent_chain|79/80 (98.75%)|80/80 (100.00%)|79/80 (98.75%)|80/80 (100.00%)|
|BART|IID|plus_person|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|person_plus|latent_chain|75/80 (93.75%)|72/80 (90.00%)|75/80 (93.75%)|72/80 (90.00%)|
|BART|IID|person_plus|decode_reencode|79/80 (98.75%)|79/80 (98.75%)|79/80 (98.75%)|79/80 (98.75%)|
|BART|IID|person_return|latent_chain|79/80 (98.75%)|79/80 (98.75%)|79/80 (98.75%)|79/80 (98.75%)|
|BART|IID|person_return|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|plus3|latent_chain|0/80 (0.00%)|11/80 (13.75%)|0/80 (0.00%)|11/80 (13.75%)|
|BART|IID|plus3|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|IID|minus3|latent_chain|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|
|BART|IID|minus3|decode_reencode|53/53 (100.00%)|53/53 (100.00%)|53/53 (100.00%)|53/53 (100.00%)|
|BART|OOD|T_plus_first|latent_chain|75/80 (93.75%)|74/80 (92.50%)|75/80 (93.75%)|74/80 (92.50%)|
|BART|OOD|T_plus_third|latent_chain|73/80 (91.25%)|74/80 (92.50%)|73/80 (91.25%)|74/80 (92.50%)|
|BART|OOD|T_minus_first|latent_chain|79/80 (98.75%)|79/80 (98.75%)|79/80 (98.75%)|79/80 (98.75%)|
|BART|OOD|T_minus_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|OOD|P_13_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|OOD|P_31_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|OOD|plus_plus|latent_chain|0/80 (0.00%)|67/80 (83.75%)|0/80 (0.00%)|61/80 (76.25%)|
|BART|OOD|plus_plus|decode_reencode|73/80 (91.25%)|65/80 (81.25%)|73/80 (91.25%)|64/80 (80.00%)|
|BART|OOD|minus_minus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|BART|OOD|minus_minus|decode_reencode|74/80 (92.50%)|74/80 (92.50%)|74/80 (92.50%)|74/80 (92.50%)|
|BART|OOD|plus_minus|latent_chain|0/80 (0.00%)|4/80 (5.00%)|0/80 (0.00%)|4/80 (5.00%)|
|BART|OOD|plus_minus|decode_reencode|77/80 (96.25%)|75/80 (93.75%)|72/80 (90.00%)|69/80 (86.25%)|
|BART|OOD|minus_plus|latent_chain|0/80 (0.00%)|2/80 (2.50%)|0/80 (0.00%)|2/80 (2.50%)|
|BART|OOD|minus_plus|decode_reencode|68/80 (85.00%)|66/80 (82.50%)|68/80 (85.00%)|66/80 (82.50%)|
|BART|OOD|plus_person|latent_chain|80/80 (100.00%)|68/80 (85.00%)|77/80 (96.25%)|68/80 (85.00%)|
|BART|OOD|plus_person|decode_reencode|77/80 (96.25%)|73/80 (91.25%)|77/80 (96.25%)|73/80 (91.25%)|
|BART|OOD|person_plus|latent_chain|79/80 (98.75%)|66/80 (82.50%)|79/80 (98.75%)|66/80 (82.50%)|
|BART|OOD|person_plus|decode_reencode|70/80 (87.50%)|70/80 (87.50%)|70/80 (87.50%)|70/80 (87.50%)|
|BART|OOD|person_return|latent_chain|73/80 (91.25%)|73/80 (91.25%)|73/80 (91.25%)|73/80 (91.25%)|
|BART|OOD|person_return|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|BART|OOD|plus3|latent_chain|0/80 (0.00%)|5/80 (6.25%)|0/80 (0.00%)|4/80 (5.00%)|
|BART|OOD|plus3|decode_reencode|74/80 (92.50%)|63/80 (78.75%)|73/80 (91.25%)|61/80 (76.25%)|
|BART|OOD|minus3|latent_chain|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|
|BART|OOD|minus3|decode_reencode|46/53 (86.79%)|46/53 (86.79%)|46/53 (86.79%)|46/53 (86.79%)|
|t5gemma-2b-2b-ul2-it|IID|T_plus_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|T_plus_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|T_minus_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|T_minus_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|P_13_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|P_31_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus_plus|latent_chain|0/80 (0.00%)|80/80 (100.00%)|0/80 (0.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus_plus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|minus_minus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|t5gemma-2b-2b-ul2-it|IID|minus_minus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus_minus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus_minus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|minus_plus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|t5gemma-2b-2b-ul2-it|IID|minus_plus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus_person|latent_chain|68/80 (85.00%)|24/80 (30.00%)|68/80 (85.00%)|24/80 (30.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus_person|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|person_plus|latent_chain|63/80 (78.75%)|27/80 (33.75%)|63/80 (78.75%)|27/80 (33.75%)|
|t5gemma-2b-2b-ul2-it|IID|person_plus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|person_return|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|person_return|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|plus3|latent_chain|0/80 (0.00%)|1/80 (1.25%)|0/80 (0.00%)|1/80 (1.25%)|
|t5gemma-2b-2b-ul2-it|IID|plus3|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|IID|minus3|latent_chain|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|
|t5gemma-2b-2b-ul2-it|IID|minus3|decode_reencode|53/53 (100.00%)|53/53 (100.00%)|53/53 (100.00%)|53/53 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|T_plus_first|latent_chain|80/80 (100.00%)|78/80 (97.50%)|80/80 (100.00%)|78/80 (97.50%)|
|t5gemma-2b-2b-ul2-it|OOD|T_plus_third|latent_chain|80/80 (100.00%)|78/80 (97.50%)|80/80 (100.00%)|78/80 (97.50%)|
|t5gemma-2b-2b-ul2-it|OOD|T_minus_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|T_minus_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|P_13_first|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|P_31_third|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|plus_plus|latent_chain|0/80 (0.00%)|80/80 (100.00%)|0/80 (0.00%)|79/80 (98.75%)|
|t5gemma-2b-2b-ul2-it|OOD|plus_plus|decode_reencode|80/80 (100.00%)|79/80 (98.75%)|80/80 (100.00%)|79/80 (98.75%)|
|t5gemma-2b-2b-ul2-it|OOD|minus_minus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|t5gemma-2b-2b-ul2-it|OOD|minus_minus|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|plus_minus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|t5gemma-2b-2b-ul2-it|OOD|plus_minus|decode_reencode|80/80 (100.00%)|79/80 (98.75%)|80/80 (100.00%)|79/80 (98.75%)|
|t5gemma-2b-2b-ul2-it|OOD|minus_plus|latent_chain|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|0/80 (0.00%)|
|t5gemma-2b-2b-ul2-it|OOD|minus_plus|decode_reencode|80/80 (100.00%)|78/80 (97.50%)|80/80 (100.00%)|78/80 (97.50%)|
|t5gemma-2b-2b-ul2-it|OOD|plus_person|latent_chain|52/80 (65.00%)|26/80 (32.50%)|52/80 (65.00%)|26/80 (32.50%)|
|t5gemma-2b-2b-ul2-it|OOD|plus_person|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|person_plus|latent_chain|45/80 (56.25%)|28/80 (35.00%)|45/80 (56.25%)|28/80 (35.00%)|
|t5gemma-2b-2b-ul2-it|OOD|person_plus|decode_reencode|80/80 (100.00%)|78/80 (97.50%)|80/80 (100.00%)|78/80 (97.50%)|
|t5gemma-2b-2b-ul2-it|OOD|person_return|latent_chain|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|person_return|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|plus3|latent_chain|0/80 (0.00%)|3/80 (3.75%)|0/80 (0.00%)|3/80 (3.75%)|
|t5gemma-2b-2b-ul2-it|OOD|plus3|decode_reencode|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|80/80 (100.00%)|
|t5gemma-2b-2b-ul2-it|OOD|minus3|latent_chain|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|0/53 (0.00%)|
|t5gemma-2b-2b-ul2-it|OOD|minus3|decode_reencode|53/53 (100.00%)|53/53 (100.00%)|53/53 (100.00%)|53/53 (100.00%)|


逐步frame/date/person和每个非日期字段、遗漏/重复文本诊断见per_step.csv；按T_plus源offset/person/status/polarity分层见T_plus_strata.csv。解析字段错误见fact_errors.csv，完整固定分母及解析子集分母见fact_summary.csv。未决不能被“已解析子集零错误”掩盖。正确目标重构是oracle诊断而非数学上界；规则只读源文本及框架。无编辑循环1/2/3次、每阶段target和原句重构见各模型controls.jsonl，缓存只复用完全相同实际文本，不用gold替换模型输出。

主表事实错误/未决统计的是1866个路径方式终点输出，每个世界有多条相关路径，不是1866个独立世界；日期错误另列，全部中间阶段字段见per_step.csv。未解析输出不进入“已解析字段错误”计数，不能据零已解析非日期错误宣称全部事实保持。

## 训练与对照实测

|模型|组|更新/选中步|监督token|算子样本调用|decoder前向批次|训练含dev秒|峰值显存字节|
|---|---|---|---:|---:|---:|---:|---:|
|t5gemma-2b-2b-ul2-it|G1|600/600|468798|9600|2400|593.38|24907978752|
|t5gemma-2b-2b-ul2-it|G3|600/600|547718|11200|3150|589.28|26754913792|

这里的前向批次按实际microbatch调用统计；算子调用按样本次数统计。训练秒不含全部GPU加载/调度时间，资源账本则计完整分配秒。两训练作业可能并发，不据这一次运行的耗时差作端到端性能结论。training_counts.csv逐算子列出更新、token与时间；dev_curves.csv保存全部六次完整原子dev检查。

|模型|层|对照|全轨迹 n/N|未决阶段数|
|---|---|---|---:|---:|
|BART|test_iid|source|1173/1173|0|
|BART|test_iid|target_stages|1173/1173|0|
|BART|test_iid|reconstruction_1|1173/1173|0|
|BART|test_iid|reconstruction_2|1173/1173|0|
|BART|test_iid|reconstruction_3|1173/1173|0|
|BART|test_template_ood|source|1173/1173|0|
|BART|test_template_ood|target_stages|1173/1173|0|
|BART|test_template_ood|reconstruction_1|1173/1173|0|
|BART|test_template_ood|reconstruction_2|1173/1173|0|
|BART|test_template_ood|reconstruction_3|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_iid|source|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_iid|target_stages|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_iid|reconstruction_1|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_iid|reconstruction_2|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_iid|reconstruction_3|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_template_ood|source|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_template_ood|target_stages|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_template_ood|reconstruction_1|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_template_ood|reconstruction_2|1173/1173|0|
|t5gemma-2b-2b-ul2-it|test_template_ood|reconstruction_3|1173/1173|0|

Text-rule全轨迹2346/2346。这是固定受控语法内基线，不构成神经方法的性能优势。重构缓存只节省重复诊断生成，不以缓存后的总时间冒充每次部署重构成本。timing_summary.csv分别报告encode、edit、实际decode和纯链诊断decode；BART batch4、新IT正式batch16，不能直接据其计时归因骨干速度。

## 配对差值

|模型|层|路径|指标|G3−G1百分点 [记录bootstrap 95%区间]|
|---|---|---|---|---:|
|BART|test_iid|T_plus|trajectory_joint|-0.62 [-1.88, +0.00]|
|BART|test_iid|person_plus|trajectory_joint|-3.75 [-10.00, +1.25]|
|BART|test_iid|plus3|trajectory_joint|+13.75 [+6.25, +22.50]|
|BART|test_iid|plus_person|trajectory_joint|+1.25 [+0.00, +3.75]|
|BART|test_iid|plus_plus|trajectory_joint|+100.00 [+100.00, +100.00]|
|t5gemma-2b-2b-ul2-it|test_iid|T_plus|trajectory_joint|+0.00 [+0.00, +0.00]|
|t5gemma-2b-2b-ul2-it|test_iid|person_plus|trajectory_joint|-45.00 [-57.50, -32.50]|
|t5gemma-2b-2b-ul2-it|test_iid|plus3|trajectory_joint|+1.25 [+0.00, +3.75]|
|t5gemma-2b-2b-ul2-it|test_iid|plus_person|trajectory_joint|-55.00 [-66.25, -43.75]|
|t5gemma-2b-2b-ul2-it|test_iid|plus_plus|trajectory_joint|+100.00 [+100.00, +100.00]|
|BART|test_template_ood|T_plus|trajectory_joint|+0.00 [-4.38, +4.38]|
|BART|test_template_ood|person_plus|trajectory_joint|-16.25 [-25.00, -8.75]|
|BART|test_template_ood|plus3|trajectory_joint|+5.00 [+1.25, +10.00]|
|BART|test_template_ood|plus_person|trajectory_joint|-11.25 [-18.75, -3.75]|
|BART|test_template_ood|plus_plus|trajectory_joint|+76.25 [+66.25, +85.00]|
|t5gemma-2b-2b-ul2-it|test_template_ood|T_plus|trajectory_joint|-2.50 [-6.25, +0.00]|
|t5gemma-2b-2b-ul2-it|test_template_ood|person_plus|trajectory_joint|-21.25 [-35.00, -6.25]|
|t5gemma-2b-2b-ul2-it|test_template_ood|plus3|trajectory_joint|+3.75 [+0.00, +8.75]|
|t5gemma-2b-2b-ul2-it|test_template_ood|plus_person|trajectory_joint|-32.50 [-42.50, -21.25]|
|t5gemma-2b-2b-ul2-it|test_template_ood|plus_plus|trajectory_joint|+98.75 [+96.25, +100.00]|

## 统计与证据边界

2000次配对world bootstrap，同层所有模型/路径/视图共用重采样索引。paired_statistics.json含每模型G3−G1、latent−reencode；只有存在新骨干完成结果时才有跨骨干−BART差值。单seed区间只涵盖记录抽样，不涵盖训练随机性；探索性多比较不作确认性显著发现。

本轮测量、对照支持的解释、机制猜测分开：重编码优于纯链仅支持继续使用编辑表示存在问题，不能证明离开流形；更大/指令模型的差异同时涉及tokenizer/包装/训练前提，不能唯一归因规模或架构。没有decoder-only实验。

## 资源与完成状态

实际累计4951 GPU分配秒（1.3753小时），预检1662秒，上限分别14400/3600。用户途中将并发上限放宽为2，见PROTOCOL_AMENDMENT_01；每作业单GPU、sbatch+srun，父/step最大ElapsedRaw不重复计费，排队另列。基础下载无GPU，分别记录耗时。

完成/准入不通过/接口失败/预算跳过分别见每模型admission及预算记录，不混入准确率。没有自动扩大模型、prompt、rank、训练步数或seed。已获准的模型下载完成；未训练模型是准入规则限制，不冒称进行了G1/G3。

## 审查与复现

预先20确认世界的匿名完整轨迹见review/blind_trajectories.csv，映射review/private_mapping.json独立保存。最多20配对便利案例见[review/CASES.md](review/CASES.md)，模型复核另存；human_label为空，尚无真人审核。

复现见README.md与commands.log。协议、原世界哈希、评分器锁、模型/初始化/接口配置均保存。v1/v2/v3只读核验；独立分支本地提交，远端只同步独立分支，不覆盖main。原模型权重、环境、凭据和latest优化器恢复状态不上传。
